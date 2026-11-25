#!/usr/bin/env python3
"""Operator-only fixed-scope audit. See README before connecting."""
import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from getpass import GetPassWarning, getpass
from importlib.metadata import version
from pathlib import Path
import re
import ssl
import subprocess
import sys
import warnings
import hashlib
import json
from zoneinfo import ZoneInfo

SITE = "development.localhost"
COMMIT = "e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5"
@dataclass(frozen=True)
class Pilot:
    """Exact scope privately supplied and independently agreed by both operators."""

    slip: str
    company: str
    requesting: str
    beneficiary: str
    equipment: str
    item: str
    warehouse: str
    expense: str


STOCKROOM = "Stockroom Personnel"
REQUESTOR = "Withdrawal Slip Requestor"


class Stop(Exception):
    """Fixed, safe-to-report audit stop."""


def require(condition, reason):
    if not condition:
        raise Stop(reason)


def single(rows):
    return rows[0] if len(rows) == 1 else None


def digest(*facts):
    return hashlib.sha256(json.dumps(
        facts, ensure_ascii=True, separators=(",", ":"), default=str,
    ).encode()).hexdigest()


def independent(maker, checker):
    return all(isinstance(a, str) and a and a == a.strip()
               and a.casefold() not in ("guest", "administrator") for a in (maker, checker)
               ) and maker.casefold() != checker.casefold()


def local_utc(value, zone):
    if value is None:
        return None
    if not isinstance(value, datetime) or value.tzinfo is not None:
        raise ValueError("unexpected timestamp")
    first, second = (value.replace(tzinfo=zone, fold=fold) for fold in (0, 1))
    if first.utcoffset() != second.utcoffset():
        raise ValueError("ambiguous site timestamp")
    return first.astimezone(timezone.utc)


class Results:
    def __init__(self, output=print):
        self.output = output
        self.states = []

    def emit(self, state, check, message):
        self.states.append(state)
        self.output(f"{state} | {check} | {message}")

    def check(self, ok, label, failure):
        self.emit("PASS" if ok else "FAIL", label, "Confirmed in snapshot." if ok else failure)
        return bool(ok)

    def finish(self):
        state = "FAIL" if "FAIL" in self.states else "UNVERIFIED" if "UNVERIFIED" in self.states else "PASS"
        self.output(f"{state} | OVERALL | Read-only preflight. Separate authorization required for UAT.")
        return {"PASS": 0, "FAIL": 1, "UNVERIFIED": 2}[state]


def decision_matches(d, use, row, *, pilot, kind, source, target, action, checker, approved,
                     reference, maker, instant, zone, request=None, event=None):
    if (not d or not use or not approved or not d["signed_at"] or not use["used_at"]
            or not row["modified"] or not independent(maker, checker)
            or reference == "CIRCLECI-SYNTHETIC-APPROVAL-NOT-FINANCE-AUTHORIZATION"):
        return False
    token = str(row["modified"])
    snap = digest(kind, pilot.company, row["mapping_scope"], source, row["name"], target,
                  row["owner"], token, action, request or "")
    expected = {
        "name": reference, "kind": kind, "action": action, "status": "Signed",
        "company": pilot.company, "mapping_scope": row["mapping_scope"], "revision": row["name"],
        "source_value": source, "financial_value": target, "maker": row["owner"],
        "signed_by": checker, "reviewed_modified": token, "snapshot_hash": snap,
        "decision_key": digest(kind, action, row["name"], checker, snap),
    }
    used = dict(decision=reference, kind=kind, action=action, revision=row["name"],
                used_by=checker, event_ref=event or row["name"])
    return (
        all(d[k] == v for k, v in expected.items())
        and (d["request_name"] or None) == request
        and all(use[k] == v for k, v in used.items())
        and local_utc(row["modified"], zone) <= local_utc(d["signed_at"], zone)
        <= approved <= local_utc(use["used_at"], zone) <= instant
    )


def approval_snapshot_matches(versions, row, kind, source, target, pilot):
    expected = dict(kind=kind, revision=row["name"], scope=row["mapping_scope"],
                    company=pilot.company, source=source, value=target, prepared_by=row["owner"],
                    approved_by=row["approved_by"], approved_at=str(row["approved_at"]),
                    effective_from=str(row["effective_from"]),
                    effective_until=str(row["effective_until"] or ""),
                    approval_reference=row["approval_reference"])
    evidence = []
    for version in versions:
        body = json.loads(version["data"])
        if isinstance(body, dict) and "ccpc_mapping_decision" in body:
            evidence.append(body["ccpc_mapping_decision"])
    return evidence == [expected]


def cutoff_at(q, row, kind, source, target, start, end, now, zone, pilot):
    event_rows = q(
        "SELECT name,company,mapping_scope,approved_by,approved_at,cutoff_at,decision,"
        "retirement_request,target_key,event_hash FROM `tabCCPC Mapping Retirement Event` "
        "WHERE kind=%s AND revision=%s", (kind, row["name"]),
    )
    if not event_rows:
        return end
    event = single(event_rows)
    if not event:
        raise ValueError("duplicate accepted retirement events")
    cutoff = local_utc(event["cutoff_at"], zone)
    request = single(q(
        "SELECT name,kind,revision,company,mapping_scope,financial_value,maker,request_state,"
        "decided_by,decided_at,target_hash FROM `tabCCPC Mapping Retirement Request` WHERE name=%s",
        (event["retirement_request"],),
    ))
    target_hash = digest(kind, pilot.company, row["mapping_scope"], source, row["name"],
                         target, row["owner"], row["approved_by"], row["approved_at"],
                         row["approval_reference"], row["effective_from"], row["effective_until"])
    if not (request and cutoff and start < cutoff
            and event["cutoff_at"] == event["approved_at"] == request["decided_at"]
            and event["company"] == pilot.company and event["mapping_scope"] == row["mapping_scope"]
            and event["target_key"] == digest(kind, row["name"])
            and event["event_hash"] == digest(kind, row["name"], event["decision"],
                                             event["approved_by"], event["approved_at"])
            and request["name"] == event["retirement_request"]
            and request["kind"] == kind and request["revision"] == row["name"]
            and request["company"] == pilot.company and request["mapping_scope"] == row["mapping_scope"]
            and request["financial_value"] == target and request["request_state"] == "Accepted"
            and request["decided_by"] == event["approved_by"] and request["target_hash"] == target_hash
            and evidence(q, row, kind, source, target, "Retire", event["approved_by"], cutoff,
                         event["decision"], request["maker"], now, zone, pilot, request["name"], event["name"])):
        raise ValueError("retirement evidence mismatch")
    return min(end, cutoff) if end is not None else cutoff


def evidence(q, row, kind, source, target, action, checker, approved, reference, maker,
             now, zone, pilot, request=None, event=None):
    if not reference or reference != reference.strip():
        return False
    d = single(q(
        "SELECT name,kind,action,status,company,mapping_scope,revision,source_value,financial_value,"
        "maker,signed_by,signed_at,request_name,reviewed_modified,snapshot_hash,decision_key "
        "FROM `tabCCPC Accounting Mapping Decision` WHERE name=%s", (reference,),
    ))
    use = single(q(
        "SELECT decision,kind,action,revision,used_by,event_ref,used_at FROM `tabCCPC Mapping Decision Use` "
        "WHERE decision=%s", (reference,),
    ))
    return decision_matches(d, use, row, pilot=pilot, kind=kind, source=source, target=target, action=action,
                            checker=checker, approved=approved, reference=reference, maker=maker,
                            instant=now, zone=zone, request=request, event=event)


def eligible_mapping(q, kind, source, zone, now, pilot):
    key, value, selector = (
        ("item_group", "expense_account", "") if kind == "Expense"
        else ("beneficiary_department", "cost_center", ",selector_kind,selector_key")
    )
    scope = single(q(
        f"SELECT name,company,{key}{selector} FROM `tabCCPC {kind} Mapping Scope` "
        f"WHERE company=%s AND {key}=%s", (pilot.company, source),
    ))
    if (not scope or scope["company"] != pilot.company or scope[key] != source
            or kind == "Center" and (scope["selector_kind"], scope["selector_key"])
            != ("Department Only", "DEPARTMENT_ONLY")):
        raise ValueError("missing, competing or unsupported scope")
    table = f"CCPC {kind} Mapping Revision"
    revisions = q(
        f"SELECT name,mapping_scope,owner,modified,{value},approval_state,approved_by,approved_at,"
        f"approval_reference,effective_from,effective_until FROM `tab{table}` WHERE mapping_scope=%s",
        (scope["name"],),
    )
    active = []
    for row in revisions:
        if row["approval_state"] != "Approved":
            continue
        if row["mapping_scope"] != scope["name"]:
            raise ValueError("revision scope mismatch")
        start, end, approved = (local_utc(row[k], zone) for k in
                                ("effective_from", "effective_until", "approved_at"))
        if not start or not approved or start < approved or (end is not None and end <= start):
            raise ValueError("invalid approved window")
        target = row[value]
        end = cutoff_at(q, row, kind, source, target, start, end, now, zone, pilot)
        if not (start <= now and (end is None or now < end)):
            continue
        versions = q("SELECT data FROM `tabVersion` WHERE ref_doctype=%s AND docname=%s",
                     (table, row["name"]))
        if not (target and evidence(q, row, kind, source, target, "Approve", row["approved_by"],
                                    approved, row["approval_reference"], row["owner"], now, zone, pilot)
                and approval_snapshot_matches(versions, row, kind, source, target, pilot)):
            raise ValueError("approval evidence mismatch")
        active.append(target)
    if len(active) != 1:
        raise ValueError("expected exactly one currently eligible revision")
    return active[0]


def leaf(row, pilot):
    return bool(row and row["company"] == pilot.company and row["is_group"] == 0 and row["disabled"] == 0)


def stock_ready(item, bin_row, ledger, child, pilot):
    return bool(item and bin_row and ledger and child and item["name"] == pilot.item
                and item["disabled"] == 0 and item["is_stock_item"] == 1
                and item["stock_uom"] and child["uom"] == item["stock_uom"]
                and bin_row["actual_qty"] is not None
                and bin_row["actual_qty"] - (bin_row["reserved_stock"] or 0) >= 1
                and (bin_row["stock_value"] or 0) > 0 and (bin_row["valuation_rate"] or 0) > 0
                and ledger["qty_after_transaction"] == bin_row["actual_qty"]
                and ledger["stock_value"] == bin_row["stock_value"]
                and (ledger["valuation_rate"] or 0) > 0)


def permissions(q, slip, issuer, result, pilot):
    owner = slip["owner"]

    def roles(user):
        return {r["role"] for r in q("SELECT role FROM `tabHas Role` WHERE parenttype='User' AND parent=%s",
                                     (user,))}

    people = [single(q("SELECT enabled FROM `tabUser` WHERE name=%s", (user,))) for user in (owner, issuer)]
    owner_roles, issuer_roles = roles(owner), roles(issuer)
    result.check(
        owner == slip["approving_supervisor"] and independent(owner, issuer)
        and all(p and p["enabled"] == 1 for p in people)
        and REQUESTOR in owner_roles and STOCKROOM in issuer_roles,
        "Named requester and issuer", "Enabled distinct actors or explicit workflow roles missing.",
    )
    for index, user in enumerate((owner, issuer)):
        companies = q("SELECT for_value,apply_to_all_doctypes,applicable_for FROM `tabUser Permission` "
                      "WHERE user=%s AND allow='Company'", (user,))
        relevant = [g for g in companies if g["apply_to_all_doctypes"] == 1
                    or g["applicable_for"] == "Withdrawal Slip"]
        result.check(not relevant or any(g["for_value"] == pilot.company for g in relevant),
                     ("Requester", "Issuer")[index] + " Company grant review",
                     "Applicable explicit Company restrictions exclude CCPC.")
    workflow = single(q("SELECT name,workflow_state_field FROM `tabWorkflow` "
                        "WHERE document_type='Withdrawal Slip' AND is_active=1"))
    transitions = q("SELECT state,next_state,allowed FROM `tabWorkflow Transition` WHERE parent=%s",
                    (workflow["name"],)) if workflow else []
    required = {("Draft", "Approved", REQUESTOR), ("Approved", "Stockroom Review", STOCKROOM)}
    result.check(workflow and workflow["workflow_state_field"] == "status"
                 and required <= {(r["state"], r["next_state"], r["allowed"]) for r in transitions},
                 "Workflow metadata", "Expected active request and Stockroom transitions are absent.")
    params = ("Withdrawal Slip",)
    fields = "role,permlevel,if_owner,`read`,`write`,`create`"
    custom = q(f"SELECT {fields} FROM `tabCustom DocPerm` WHERE parent=%s", params)
    rows = custom or q(f"SELECT {fields} FROM `tabDocPerm` WHERE parent=%s", params)
    for name, actor_roles, own, flags in (
        ("Requester", owner_roles, True, ("read", "write")),
        ("Issuer", issuer_roles, False, ("read", "write")),
    ):
        usable = [r for r in rows if r["role"] in actor_roles and r["permlevel"] == 0
                  and (own or not r["if_owner"])]
        if all(any(r[f] for r in usable) for f in flags):
            result.emit("PASS", name + " static permission rows", "Slip read/write grant present.")
        else:
            result.emit("UNVERIFIED", name + " static permission rows", "No direct grant demonstrated. Review runtime permission.")
    result.emit("UNVERIFIED", "Effective named-user permissions",
                "Confirm saved-record access, Workflow actions, issuer write, and reviewer report access in read-only named sessions.")


def run_snapshot(q, result, issuer, timezone_name, pilot, now=None):
    versions = q("SELECT app_name,app_version FROM `tabInstalled Application` "
                 "WHERE app_name IN ('frappe','erpnext','ccpcerp')")
    result.check(len(versions) == 3 and {r["app_name"]: r["app_version"] for r in versions} ==
                 {"frappe": "16.33.1", "erpnext": "16.34.2", "ccpcerp": "0.0.1"},
                 "Installed app registry", "Installed versions differ from the approved checkpoint.")
    slip = single(q(
        "SELECT name,docstatus,status,owner,approving_supervisor,company,requesting_company,"
        "department,work_for_department,work_for_section,source_warehouse,equipment,ccpc_material_use,"
        "COALESCE(received_by,'')<>'' AS received_by_present FROM `tabWithdrawal Slip` WHERE name=%s", (pilot.slip,),
    ))
    if not result.check(slip and slip["name"] == pilot.slip, "Persisted slip", "Exact slip missing."):
        return
    result.check(slip["docstatus"] == 0 and slip["status"] == "Draft",
                 "Draft state", "Slip is outside the approved Draft preflight.")
    result.check(slip["company"] == slip["requesting_company"] == pilot.company
                 and slip["department"] == pilot.requesting and slip["work_for_department"] == pilot.beneficiary
                 and slip["equipment"] == pilot.equipment and slip["source_warehouse"] == pilot.warehouse
                 and slip["ccpc_material_use"] == "Routine Maintenance",
                 "Slip intent", "Company, beneficiary, equipment, warehouse or use differs from the approved scope.")
    if not slip["received_by_present"]:
        result.emit("UNVERIFIED", "Received By", "Must be supplied in the authorized future workflow before issue.")
    child = single(q("SELECT item_code,requested_qty,uom,issued_qty FROM `tabWithdrawal Slip Item` "
                     "WHERE parent=%s AND parenttype='Withdrawal Slip' AND parentfield='items'", (pilot.slip,)))
    result.check(child and child["item_code"] == pilot.item and child["requested_qty"] == 1
                 and not child["issued_qty"], "Persisted item row", "Expected one unissued unit of the attested item on a sole saved row.")
    entry_counts = {r["docstatus"]:r["n"] for r in q(
        "SELECT docstatus,COUNT(*) AS n FROM `tabStock Entry` WHERE withdrawal_slip=%s GROUP BY docstatus", (pilot.slip,),
    )}
    result.check(not (set(entry_counts) - {2}), "Linked Stock Entries",
                 "A draft, submitted or unexpected linked Stock Entry blocks this issue.")
    if entry_counts.get(2):
        result.emit("UNVERIFIED", "Prior cancelled issue", "Review prior cancellation and issue history before UAT.")
    dept = single(q("SELECT company,is_group,disabled FROM `tabDepartment` WHERE name=%s", (pilot.beneficiary,)))
    equipment = single(q("SELECT name,company,department,section,status FROM `tabEquipment Registry` WHERE name=%s",
                         (pilot.equipment,)))
    result.check(leaf(dept, pilot) and equipment and equipment["name"] == pilot.equipment
                 and equipment["company"] == pilot.company and equipment["department"] == pilot.beneficiary
                 and equipment["status"] == "Active"
                 and (not equipment["section"] or equipment["section"] == slip["work_for_section"]),
                 "Equipment and actual beneficiary", "Missing, inactive, foreign or conflicting equipment affiliation.")
    enabled_sections = q("SELECT name FROM `tabCCPC Section` WHERE department=%s AND company=%s AND disabled=0",
                         (pilot.beneficiary, pilot.company))
    if enabled_sections or slip["work_for_section"]:
        result.check(any(s["name"] == slip["work_for_section"] for s in enabled_sections),
                     "Beneficiary section", "The persisted section is required or is outside the beneficiary Department.")

    item = single(q("SELECT name,item_group,disabled,is_stock_item,stock_uom,has_serial_no,has_batch_no,"
                    "valuation_method FROM `tabItem` WHERE name=%s", (pilot.item,)))
    group = single(q("SELECT name,is_group FROM `tabItem Group` WHERE name=%s",
                     (item["item_group"],))) if item else None
    bearings = result.check(group and group["name"] == item["item_group"] == "Bearings" and group["is_group"] == 0,
                            "Exact Bearings group", "Actual Item Group differs from the reviewed Bearings pilot.")
    wh = single(q("SELECT company,is_group,disabled,lft,rgt FROM `tabWarehouse` WHERE name=%s", (pilot.warehouse,)))
    result.check(leaf(wh, pilot), "Warehouse ownership", "Warehouse missing, disabled, group, or foreign Company.")
    bin_row = single(q("SELECT actual_qty,reserved_stock,valuation_rate,stock_value FROM `tabBin` "
                       "WHERE item_code=%s AND warehouse=%s", (pilot.item, pilot.warehouse)))
    ledger = single(q(
        "SELECT qty_after_transaction,stock_value,valuation_rate FROM `tabStock Ledger Entry` "
        "WHERE company=%s AND item_code=%s AND warehouse=%s AND docstatus=1 AND is_cancelled=0 "
        "ORDER BY posting_date DESC,posting_time DESC,creation DESC,name DESC LIMIT 1",
        (pilot.company, pilot.item, pilot.warehouse),
    ))
    result.check(stock_ready(item, bin_row, ledger, child, pilot), "Stock and valuation",
                 "No one valued unreserved stock-UOM unit, invalid stock item, or Bin/SLE mismatch.")
    if not item or item["has_serial_no"] or item["has_batch_no"]:
        result.emit("UNVERIFIED", "Serial/batch eligibility",
                    "Confirm specific available, eligible serial or batch in the authorized read-only ERPNext UI.")
    else:
        result.emit("PASS", "Serial/batch eligibility", "Item flags require neither.")
    result.emit("UNVERIFIED", "Other stock commitments",
                "Confirm effective availability and any non-Bin commitments immediately before authorized issue.")

    site_zone = single(q("SELECT value FROM `tabSingles` WHERE doctype='System Settings' AND field='time_zone'"))
    if not site_zone or site_zone["value"] != timezone_name:
        result.emit("UNVERIFIED", "Signed Finance", "Persisted and independently verified site timezone differ or are missing.")
    else:
        zone = ZoneInfo(timezone_name)
        now = now or datetime.now(timezone.utc)
        for kind, source, master in (
            ("Expense", item["item_group"] if bearings else None, "Account"),
            ("Center", pilot.beneficiary, "Cost Center"),
        ):
            if not source:
                result.emit("UNVERIFIED", "Signed Expense", "Exact Bearings scope was not established.")
                continue
            try:
                target = eligible_mapping(q, kind, source, zone, now, pilot)
                extra = ",root_type" if kind == "Expense" else ""
                row = single(q(f"SELECT name,company,is_group,disabled{extra} FROM `tab{master}` WHERE name=%s",
                               (target,)))
                result.check(leaf(row, pilot) and row["name"] == target and (
                    kind == "Center" or target == pilot.expense and row["root_type"] == "Expense"
                ), "Signed " + kind, "Approved target differs from the expected eligible master.")
            except ValueError:
                result.emit("FAIL", "Signed " + kind,
                            "Missing or conflicting eligible revision, or approval/retirement evidence did not reconcile.")

    flags = single(q("SELECT enable_perpetual_inventory,default_inventory_account,valuation_method "
                     "FROM `tabCompany` WHERE name=%s", (pilot.company,)))
    dim = q("SELECT document_type FROM `tabAccounting Dimension` WHERE fieldname='department' AND disabled=0")
    result.check(flags and flags["enable_perpetual_inventory"] == 1
                 and len(dim) == 1 and dim[0]["document_type"] == "Department",
                 "Perpetual inventory and Department dimension", "Required accounting settings not active.")
    account = None
    if leaf(wh, pilot) and flags:
        nearest = single(q("SELECT account FROM `tabWarehouse` WHERE company=%s AND lft<=%s AND rgt>=%s "
                           "AND COALESCE(account,'')<>'' ORDER BY lft DESC LIMIT 1", (pilot.company, wh["lft"], wh["rgt"])))
        account = (nearest or {}).get("account") or flags["default_inventory_account"]
        if not account:
            fallback = single(q("SELECT name FROM `tabAccount` WHERE company=%s AND account_type='Stock' AND is_group=0",
                                (pilot.company,)))
            account = (fallback or {}).get("name")
    inventory = single(q("SELECT name,company,is_group,disabled,root_type FROM `tabAccount` WHERE name=%s",
                         (account,))) if account else None
    result.check(leaf(inventory, pilot) and inventory["name"] == account and inventory["root_type"] == "Asset",
                 "Warehouse inventory account", "No valid resolved same-Company inventory asset account.")
    columns = q("SELECT TABLE_NAME,COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() "
                "AND TABLE_NAME IN ('tabWithdrawal Slip','tabStock Entry','tabStock Entry Detail','tabGL Entry')")
    required = {
        ("tabWithdrawal Slip", "ccpc_material_use"), ("tabStock Entry", "withdrawal_slip"),
        ("tabStock Entry", "department"), ("tabGL Entry", "department"),
        *(("tabStock Entry Detail", name) for name in (
            "department", "withdrawal_slip_item", "ccpc_expense_mapping_revision",
            "ccpc_center_mapping_revision", "ccpc_item_group_at_issue",
            "ccpc_equipment_at_issue", "ccpc_equipment_code_at_issue",
        )),
    }
    result.check(required <= {(c["TABLE_NAME"], c["COLUMN_NAME"]) for c in columns},
                 "Issue provenance columns", "Expected migrated posting fields missing.")
    permissions(q, slip, issuer, result, pilot)
    result.emit("UNVERIFIED", "Loaded worker code and effective metadata",
                "Confirm the active worker source, effective Frappe fields and accounting period controls without restarting.")
    result.emit("UNVERIFIED", "UAT action gate",
                "Keep Draft. Separate authorization and normal workflow required before any approval or issue.")


IDENTITY = ("SELECT DATABASE() AS db,CURRENT_USER() AS principal,@@hostname AS hostname,"
            "@@server_id AS server_id,CURRENT_ROLE() AS role")
ISOLATION = "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"
SNAPSHOT = "START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY"


def verified_target(a, b):
    require(a["reviewer_role"] == "site-operator" and b["reviewer_role"] == "database-operator"
            and independent(a["reviewer"], b["reviewer"]), "Independent operator attestations required.")
    target = a["target"]
    require(target == b["target"] and target["site"] == SITE and target["environment"] == "DEVELOPMENT"
            and target["commit"] == COMMIT, "DEVELOPMENT site, source or database binding mismatch.")
    require(a["development_endpoint_exclusive"] is True and b["development_endpoint_exclusive"] is True
            and b["direct_select_only_no_inherited_access"] is True,
            "DEVELOPMENT route isolation and grant review are required.")
    require(bool(re.fullmatch(r"[A-Za-z0-9_.-]+", target["host"]))
            and bool(re.fullmatch(r"[A-Za-z0-9_]+", target["database"]))
            and bool(re.fullmatch(r"[A-Za-z0-9_]+@[A-Za-z0-9.:%_-]+", target["principal"]))
            and target["principal"].split("@", 1)[0] == target["username"]
            and type(target["port"]) is int and 0 < target["port"] <= 65535
            and type(target["server_id"]) is int and target["hostname"]
            and all(re.fullmatch(r"[0-9a-f]{64}", target[key])
                    for key in ("ca_sha256", "leaf_sha256")),
            "Invalid endpoint, account or fingerprint inputs.")
    ZoneInfo(target["timezone"])
    pilot = Pilot(**target["pilot"])
    require(all(isinstance(value, str) and value and value == value.strip()
                and len(value) <= 140 and not any(ord(char) < 32 for char in value)
                for value in vars(pilot).values()),
            "Both attestations must agree on all exact pilot identifiers.")
    return target, pilot


def select_only_grants(rows, target):
    user, host = target["principal"].split("@", 1)
    accounts = (f"`{user}`@`{host}`", f"'{user}'@'{host}'")
    schema = target["database"].replace("_", r"\_")
    permitted = {f"GRANT SELECT ON `{schema}`.* TO {a}" for a in accounts}
    usage = {f"GRANT USAGE ON *.* TO {a}" for a in accounts}
    found = False
    for row in rows:
        if len(row) != 1:
            return False
        grant = next(iter(row.values()))
        if not isinstance(grant, str):
            return False
        if grant in permitted:
            found = True
        elif re.sub(r" IDENTIFIED BY PASSWORD '\*[0-9A-Fa-f]{40}'$", "", grant) not in usage:
            return False
    return found


def require_source():
    require((Path("sites") / SITE).is_dir() and Path("apps/ccpcerp").is_dir(),
            "Run from the verified DEVELOPMENT container bench root.")

    def git(*args):
        return subprocess.check_output(
            ["git", "--no-optional-locks", "-C", "apps/ccpcerp", *args],
            stderr=subprocess.DEVNULL, text=True,
        ).strip()

    require(git("rev-parse", "HEAD") == COMMIT
            and not git("status", "--porcelain=v1", "--untracked-files=all"),
            "CCPC source must be clean at the exact approved commit.")


def connect(target, ca, password):
    import pymysql
    from pymysql.constants import CLIENT

    require(version("PyMySQL") == "1.1.2", "Reviewed PyMySQL version unavailable.")

    class PinnedContext(ssl.SSLContext):
        def wrap_socket(self, *args, **kwargs):
            sock = super().wrap_socket(*args, **kwargs)
            leaf = sock.getpeercert(binary_form=True)
            if not leaf or hashlib.sha256(leaf).hexdigest() != target["leaf_sha256"]:
                sock.close()
                raise Stop("TLS leaf certificate mismatch before authentication.")
            return sock

    class TLSRequired(pymysql.connections.Connection):
        def _request_authentication(self):
            require(self.ssl and self.server_capabilities & CLIENT.SSL,
                    "Server greeting did not offer TLS.")
            return super()._request_authentication()

    ctx = PinnedContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_verify_locations(cadata=ca.decode("ascii"))
    return TLSRequired(
        host=target["host"], port=target["port"], user=target["username"], password=password,
        database=target["database"], ssl=ctx, local_infile=False, autocommit=True,
        cursorclass=pymysql.cursors.DictCursor, connect_timeout=5, read_timeout=15, write_timeout=5,
    )


def inspect_connection(connection, target, issuer, result, pilot):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW SESSION STATUS LIKE 'Ssl_cipher'")
            require((cursor.fetchone() or {}).get("Value"), "Negotiated TLS could not be confirmed.")
            cursor.execute(IDENTITY)
            require(single(cursor.fetchall()) == dict(db=target["database"], principal=target["principal"],
                     hostname=target["hostname"], server_id=target["server_id"], role=None),
                    "Unexpected DEVELOPMENT schema, principal, server identity or active role.")
            cursor.execute("SHOW GRANTS")
            require(select_only_grants(cursor.fetchall(), target), "Unsupported or broader direct grants.")
            result.emit("PASS", "DEVELOPMENT connection", "Pinned TLS, server, schema and direct grants matched.")
            cursor.execute(ISOLATION)
            cursor.execute(SNAPSHOT)

            def q(sql, args=()):
                require(sql.startswith("SELECT ") and not any(
                    token in sql.upper() for token in (";", "FOR UPDATE", "OUTFILE", "DUMPFILE", "/*", "--")
                ), "Application query escaped the fixed SELECT boundary.")
                cursor.execute(sql, args or None)
                return cursor.fetchall()

            try:
                run_snapshot(q, result, issuer, target["timezone"], pilot)
            finally:
                connection.rollback()
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_attestation", type=Path)
    parser.add_argument("database_attestation", type=Path)
    parser.add_argument("approved_ca_pem", type=Path)
    args = parser.parse_args()
    result = Results()
    try:
        require_source()
        target, pilot = verified_target(json.loads(args.site_attestation.read_text()),
                                 json.loads(args.database_attestation.read_text()))
        ca = args.approved_ca_pem.read_bytes()
        require(hashlib.sha256(ca).hexdigest() == target["ca_sha256"], "CA file digest mismatch.")
        require(sys.stdin.isatty(), "An interactive trusted terminal is required.")
        with warnings.catch_warnings():
            warnings.simplefilter("error", GetPassWarning)
            issuer = getpass("Proposed Stockroom issuer login (hidden): ").strip()
            password = getpass("Existing SELECT-only database password (hidden): ")
        require(issuer and password, "Proposed issuer and credential are required.")
        inspect_connection(connect(target, ca, password), target, issuer, result, pilot)
    except Stop as exc:
        result.emit("UNVERIFIED", "Audit stopped", str(exc))
    except (Exception, KeyboardInterrupt):
        result.emit("UNVERIFIED", "Audit stopped",
                    "Target inputs, driver, database access or schema could not be verified. Raw error omitted.")
    return result.finish()


if __name__ == "__main__":
    raise SystemExit(main())
