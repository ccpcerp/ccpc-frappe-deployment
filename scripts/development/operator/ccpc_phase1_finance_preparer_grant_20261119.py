#!/usr/bin/env python3
"""One-shot DEVELOPMENT-MAIN Finance preparer role and two Company grants.

--check: read-only; --apply: audited Frappe document writes and explicit commit.
The authorized account is pinned by its email SHA256, not publicized in source.
Never execute on PROD, Integration2, the broken third site or any other bench.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import sys

B = Path("/workspace/development/frappe-bench")
MAIN = "development.localhost"
ORIGINAL = B / "apps/.ccpcerp-preserved-pr33-20261119-25a7b6be"
PREPARER = "CCPC Mapping Preparer"
APPROVER = "CCPC Accounting Mapping Approver"
COMPANIES = ("Cagayan Corn Products Corporation", "Ricor Mills Corporation")
TARGET_SHA = "c19e755f748badb09cffc4dec74df02c20919516494d3d031d5b8e4c9cbbdb46"
ATTEMPT = B / "logs/ccpc-phase1-finance-preparer-grant-20261119.attempted"


def stop(reason):
    raise RuntimeError(reason)


def git(directory, *args):
    result = subprocess.run(
        ["git", "-C", str(directory), *args],
        capture_output=True, text=True, timeout=20,
    )
    if result.returncode:
        stop("GIT SOURCE INSPECTION FAILED")
    return result.stdout.strip()


def verify_source():
    if git(B / "apps/ccpcerp", "rev-parse", "HEAD") != (
        "55eb10b86a57de55a97e293a78228d9dd17b809a"
    ):
        stop("PINNED RELEASE SOURCE CHANGED")
    if git(ORIGINAL, "rev-parse", "HEAD") != (
        "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
    ):
        stop("ORIGINAL PR33 SOURCE CHANGED")
    if git(ORIGINAL, "status", "--porcelain=v1", "--untracked-files=all") != "?? AGENTS.md":
        stop("ORIGINAL AGENTS / WORKTREE CHANGED")
    if not (ORIGINAL / "AGENTS.md").is_file():
        stop("PROTECTED AGENTS FILE MISSING")
    site_names = {p.parent.name for p in (B / "sites").glob("*/site_config.json")}
    if site_names != {
        "development.localhost",
        "ccpc-integration2.localhost",
        "ccpc-integration.localhost",
    }:
        stop("DEV SITE INVENTORY CHANGED")
    for name in (
        "development.localhost-20261118T233442Z-8db803832468",
        "ccpc-integration2.localhost-20261118T233442Z-8db803832468",
    ):
        if not (B / ".ccpc-pr32-snapshots" / name / "SHA256SUMS").is_file():
            stop("PROTECTED RECOVERY MANIFEST ABSENT")
    print("MAIN DEV RELEASE / ORIGINAL / BACKUP GUARDS: PASS")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("--check", "--apply"):
        stop("EXPECTED --check|--apply AND AUTHORIZED USER")
    mode, target = sys.argv[1:]
    if hashlib.sha256(target.casefold().encode()).hexdigest() != TARGET_SHA:
        stop("USER IS NOT EXACTLY THE OWNER-AUTHORIZED ACCOUNT")
    if os.getuid() == 0 or not (B / "env/bin/python").is_file():
        stop("WRONG EXECUTION USER OR BENCH")
    if not Path("site_config.json").parent.is_dir():
        stop("UNEXPECTED CURRENT DIRECTORY")

    verify_source()
    import frappe
    from frappe.utils import cint

    connected = False
    committed = False
    try:
        frappe.init(site=MAIN, sites_path=".")
        frappe.connect()
        connected = True
        if getattr(frappe.local, "site", None) != MAIN:
            stop("UNEXPECTED DATABASE SITE")

        q = lambda t: chr(96) + t + chr(96)
        lock = " FOR UPDATE" if mode == "--apply" else ""
        users = frappe.db.sql(
            "SELECT name, enabled, user_type FROM " + q("tabUser") +
            " WHERE name=%s" + lock, (target,), as_dict=True,
        )
        if len(users) != 1 or cint(users[0].enabled) != 1:
            stop("TARGET USER MISSING OR DISABLED")
        if users[0].user_type != "System User":
            stop("TARGET NO LONGER A SYSTEM USER")

        before_roles_rows = frappe.db.sql(
            "SELECT name, role FROM " + q("tabHas Role") +
            " WHERE parenttype='User' AND parent=%s ORDER BY name" + lock,
            (target,), as_dict=True,
        )
        roles = {r.role for r in before_roles_rows}
        if len(roles) != len(before_roles_rows):
            stop("DUPLICATE EXISTING USER ROLES")
        if "Purchasing Supervisor" not in roles:
            stop("PURCHASING SUPERVISOR ROLE ABSENT")
        if roles & {PREPARER, APPROVER, "Stockroom Personnel"}:
            stop("FINANCE OR STOCKROOM ROLE STATE CHANGED")
        # The released User.before_save hook automatically adds missing
        # requestor/inquiry roles for a Purchasing Supervisor: do not allow
        # unrelated role changes as a side effect of this one-role grant.
        if not {"MRS Requestor", "Withdrawal Slip Requestor",
                "CCPC Stock Inquiry User"}.issubset(roles):
            stop("CCPC USER HOOK WOULD ADD UNRELATED ROLES")

        before_perms = frappe.db.sql(
            "SELECT name, allow, for_value FROM " + q("tabUser Permission") +
            " WHERE user=%s ORDER BY name" + lock,
            (target,), as_dict=True,
        )
        if any(p.allow == "Company" for p in before_perms):
            stop("COMPANY USER PERMISSIONS CHANGED SINCE OWNER INSPECTION")
        for role in (PREPARER, APPROVER):
            disabled = frappe.db.get_value("Role", role, "disabled")
            if disabled is None or cint(disabled):
                stop("FINANCE ROLE MISSING OR DISABLED")
        for company in COMPANIES:
            if not frappe.db.exists("Company", company):
                stop("AUTHORIZED COMPANY MISSING")

        # Independent established Finance Controller must remain checker only.
        checker_id = "finance_controller@ccpc.com"
        if target.casefold() == checker_id.casefold():
            stop("MAKER AND CHECKER MUST BE DISTINCT")
        if cint(frappe.db.get_value("User", checker_id, "enabled") or 0) != 1:
            stop("CHECKER USER NOT ENABLED")
        checker_roles = set(frappe.get_all(
            "Has Role", filters={"parenttype": "User", "parent": checker_id},
            pluck="role",
        ))
        if APPROVER not in checker_roles or PREPARER in checker_roles or (
            "Stockroom Personnel" in checker_roles
        ):
            stop("CHECKER ROLE STATE CHANGED")
        checker_perms = frappe.db.sql(
            "SELECT for_value FROM " + q("tabUser Permission") +
            " WHERE user=%s AND allow='Company' "
            "AND apply_to_all_doctypes=1 AND IFNULL(applicable_for,'')=''",
            (checker_id,), as_dict=True,
        )
        if not set(COMPANIES).issubset({p.for_value for p in checker_perms}):
            stop("CHECKER EXPLICIT COMPANY PERMISSIONS CHANGED")

        user = frappe.get_doc("User", target)
        if {r.role for r in user.roles} != roles:
            stop("USER DOC AND ROLE TABLE INCONSISTENT")
        protected_fields = ("enabled", "user_type", "module_profile", "default_workspace")
        before_fields = tuple(user.get(x) for x in protected_fields)
        print("NAMED MAKER / SEPARATE CHECKER / EXACT COMPANIES: PASS")
        print("EXISTING ROLE COUNT:", len(roles))
        print("EXISTING TARGET COMPANY GRANTS: ZERO")

        if mode == "--check":
            print("DEV FINANCE PREPARER READ-ONLY PRECHECK: PASS")
            print("USER / COMPANY PERMISSIONS / PROD: NOT MODIFIED")
            return

        # Reserve the one-shot marker before the first possible DB mutation.
        # Interrupted/failed runs require an independent poststate inspection.
        fd = os.open(str(ATTEMPT), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as out:
            out.write("One-shot DEV Finance preparer grant attempted; verify actual DB state before retry.\n")
        print("DEV FINANCE PREPARER GRANT ATTEMPT MARKED: YES")

        frappe.set_user("Administrator")  # Administrative grants only, no Finance signing.
        user.append("roles", {"role": PREPARER})
        user.save(ignore_permissions=True)
        for company in COMPANIES:
            frappe.get_doc({
                "doctype": "User Permission",
                "user": target,
                "allow": "Company",
                "for_value": company,
                "apply_to_all_doctypes": 1,
                "applicable_for": None,
            }).insert(ignore_permissions=True)

        new_user = frappe.get_doc("User", target)
        if {r.role for r in new_user.roles} != roles | {PREPARER}:
            stop("UNEXPECTED USER ROLE CHANGE; ROLLBACK")
        if tuple(new_user.get(x) for x in protected_fields) != before_fields:
            stop("UNEXPECTED OTHER USER FIELD CHANGE; ROLLBACK")
        new_role_rows = frappe.db.sql(
            "SELECT name, role FROM " + q("tabHas Role") +
            " WHERE parenttype='User' AND parent=%s", (target,), as_dict=True,
        )
        if len(new_role_rows) != len(before_roles_rows) + 1 or not {
            r.name for r in before_roles_rows
        }.issubset({r.name for r in new_role_rows}):
            stop("PREEXISTING USER ROLE CHILD ROWS CHANGED; ROLLBACK")

        after_perms = frappe.db.sql(
            "SELECT name, allow, for_value, apply_to_all_doctypes, "
            "IFNULL(applicable_for,'') AS applicable_for FROM " +
            q("tabUser Permission") + " WHERE user=%s", (target,), as_dict=True,
        )
        old_ids = {p.name for p in before_perms}
        if len(after_perms) != len(before_perms) + 2 or not old_ids.issubset(
            {p.name for p in after_perms}
        ):
            stop("UNRELATED EXISTING USER PERMISSIONS CHANGED; ROLLBACK")
        new_perms = [p for p in after_perms if p.name not in old_ids]
        if len(new_perms) != 2 or {p.for_value for p in new_perms} != set(COMPANIES):
            stop("WRONG NUMBER OR COMPANY PERMISSIONS; ROLLBACK")
        if any(p.allow != "Company" or cint(p.apply_to_all_doctypes) != 1
               or p.applicable_for for p in new_perms):
            stop("ADDED PERMISSION SCOPE INCORRECT; ROLLBACK")

        frappe.db.commit()
        committed = True
        print("DEV FINANCE PREPARER ROLE AND TWO COMPANY GRANTS: COMMITTED")
        try:
            frappe.clear_cache(user=target)
            print("TARGET USER CACHE CLEAR: PASS")
        except Exception:
            print("WARNING: CACHE CLEAR FAILED AFTER COMMIT")
        print("PRIOR ROLES AND OTHER USER PERMISSIONS: PRESERVED")
        print("CHECKER / OTHER SITES / SCHEDULER / PROD: NOT MODIFIED")
    finally:
        if connected:
            if not committed:
                frappe.db.rollback()
            frappe.destroy()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Avoid printing DB exception details, credentials, or personal data.
        print("STOP: DEV FINANCE PREPARER OPERATION FAILED:", type(exc).__name__)
        print("IF --apply WAS ATTEMPTED, DO NOT RETRY; VERIFY MAIN DB POSTSTATE")
        raise SystemExit(1)
