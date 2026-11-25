"""Offline tests. No connector, credentials, Docker or SQL server."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from unittest import TestCase
from unittest.mock import patch

import ws_readiness_audit as audit

PILOT = audit.Pilot("SYNTH-SLIP", "_Test Company", "Synthetic Requester Department",
                    "Synthetic Beneficiary Department", "SYNTH-EQUIPMENT",
                    "SYNTH-ITEM", "Synthetic Warehouse", "Synthetic Expense")


@dataclass
class Cursor:
    identity: dict
    grants: list
    statements: list

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql, params=None):
        self.statements.append((sql, params))

    def fetchone(self):
        return {"Value": "synthetic TLS"}

    def fetchall(self):
        if self.statements[-1][0] == audit.IDENTITY:
            return [self.identity]
        if self.statements[-1][0] == "SHOW GRANTS":
            return self.grants
        return []


class Connection:
    def __init__(self, cursor):
        self.db_cursor = cursor
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return self.db_cursor

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class SecurityTests(TestCase):
    target = dict(site=audit.SITE, environment="DEVELOPMENT", commit=audit.COMMIT,
                  host="dev-db.invalid", port=3306, database="synthetic_dev", username="reader",
                  principal="reader@localhost", hostname="sandbox", server_id=3,
                  timezone="UTC", ca_sha256="a" * 64, leaf_sha256="b" * 64, pilot=vars(PILOT))
    identity = dict(db="synthetic_dev", principal="reader@localhost", hostname="sandbox",
                    server_id=3, role=None)
    grants = [
        {"grant": f"GRANT SELECT ON `synthetic_dev`.`{table}` TO `reader`@`localhost`"}
        for table in sorted(audit.AUDIT_TABLES)
    ]

    def test_target_requires_independent_site_binding(self):
        a = dict(reviewer_role="site-operator", reviewer="operator", target=self.target,
                 development_endpoint_exclusive=True)
        b = dict(reviewer_role="database-operator", reviewer="dba", target=self.target,
                 development_endpoint_exclusive=True, direct_select_only_no_inherited_access=True)
        self.assertEqual(audit.verified_target(a, b), (self.target, PILOT))
        for changed in (dict(b, reviewer="operator"), dict(b, development_endpoint_exclusive=False),
                        dict(b, target=dict(self.target, site="other.localhost")),
                        dict(b, direct_select_only_no_inherited_access=False)):
            with self.assertRaises(audit.Stop):
                audit.verified_target(a, changed)

    def test_broad_grants_rejected(self):
        self.assertTrue(audit.select_only_grants(self.grants, self.target))
        self.assertTrue(audit.select_only_grants(self.grants + [{
            "grant": "GRANT USAGE ON *.* TO `reader`@`localhost` REQUIRE SSL",
        }], self.target))
        self.assertFalse(audit.select_only_grants(self.grants[:-1], self.target))
        for grant in (
            "GRANT SELECT ON *.* TO `reader`@`localhost`",
            "GRANT SELECT ON `synthetic_dev`.* TO `reader`@`localhost`",
            self.grants[0]["grant"] + " WITH GRANT OPTION",
            self.grants[0]["grant"].replace("SELECT", "SELECT,UPDATE"),
            "GRANT some_role TO `reader`@`localhost`",
            "GRANT SELECT ON `synthetic_dev`.`tabUnrelated` TO `reader`@`localhost`",
            "GRANT SELECT ON `other_schema`.`tabAccount` TO `reader`@`localhost`",
        ):
            self.assertFalse(audit.select_only_grants(self.grants + [{"grant": grant}], self.target))

    def test_grant_manifest_matches_query_tables(self):
        from pathlib import Path
        import re

        source = Path(audit.__file__).read_text()
        tables = set(re.findall(r"FROM `(tab[^`{}]+)`", source))
        tables |= {f"tabCCPC {kind} Mapping {doctype}"
                   for kind in ("Expense", "Center") for doctype in ("Scope", "Revision")}
        tables.add("tabCost Center")
        self.assertEqual(audit.AUDIT_TABLES, tables)

    def test_identity_and_grants_fail_before_snapshot(self):
        for identity, grants in ((dict(self.identity, db="other"), self.grants),
                                 (dict(self.identity, role="writer"), self.grants),
                                 (self.identity, [])):
            conn = Connection(Cursor(identity, grants, []))
            with patch.object(audit, "run_snapshot") as run, self.assertRaises(audit.Stop):
                audit.inspect_connection(conn, self.target, "fake", audit.Results(lambda line: None), PILOT)
            run.assert_not_called()
            self.assertTrue(conn.closed)
            self.assertNotIn((audit.SNAPSHOT, None), conn.db_cursor.statements)

    def test_snapshot_guard_and_cleanup(self):
        conn = Connection(Cursor(self.identity, self.grants, []))

        def fake_snapshot(q, *_):
            for bad in ("UPDATE t SET a=1", "SELECT x FROM t FOR UPDATE",
                        "SELECT x FROM t; DELETE FROM t", "SELECT x INTO OUTFILE '/tmp/a'"):
                with self.assertRaises(audit.Stop):
                    q(bad)
            q("SELECT field FROM test WHERE name=%s", ("a'; DELETE FROM t",))
            raise audit.Stop("synthetic failure")

        with patch.object(audit, "run_snapshot", side_effect=fake_snapshot), self.assertRaises(audit.Stop):
            audit.inspect_connection(conn, self.target, "fake", audit.Results(lambda line: None), PILOT)
        self.assertEqual(conn.db_cursor.statements[-3:], [
            (audit.ISOLATION, None), (audit.SNAPSHOT, None),
            ("SELECT field FROM test WHERE name=%s", ("a'; DELETE FROM t",)),
        ])
        self.assertTrue(conn.rolled_back and conn.closed)


class FinanceTests(TestCase):
    def setUp(self):
        self.zone = timezone.utc
        self.modified = datetime(2026, 11, 25, 10)
        self.approval = self.modified + timedelta(minutes=1)
        self.when = self.approval.replace(tzinfo=self.zone) + timedelta(minutes=2)
        self.row = dict(name="rev", mapping_scope="wet", owner="maker", modified=self.modified,
                        approved_by="checker", approved_at=self.approval, approval_reference="approval",
                        effective_from=self.approval, effective_until=None,
                        approval_state="Approved", cost_center="leaf")
        self.args = dict(pilot=PILOT, kind="Center", source=PILOT.beneficiary, target="leaf", action="Approve",
                         checker="checker", approved=self.approval.replace(tzinfo=self.zone),
                         reference="approval", maker="maker", instant=self.when, zone=self.zone)
        snap = audit.digest("Center", PILOT.company, "wet", PILOT.beneficiary, "rev", "leaf",
                            "maker", str(self.modified), "Approve", "")
        self.decision = dict(name="approval", kind="Center", action="Approve", status="Signed",
                             company=PILOT.company, mapping_scope="wet", revision="rev",
                             source_value=PILOT.beneficiary, financial_value="leaf", maker="maker",
                             signed_by="checker", signed_at=self.modified, request_name=None,
                             reviewed_modified=str(self.modified), snapshot_hash=snap,
                             decision_key=audit.digest("Center", "Approve", "rev", "checker", snap))
        self.use = dict(decision="approval", kind="Center", action="Approve", revision="rev",
                        used_by="checker", event_ref="rev", used_at=self.approval)
        snapshot = dict(kind="Center", revision="rev", scope="wet", company=PILOT.company,
                        source=PILOT.beneficiary, value="leaf", prepared_by="maker", approved_by="checker",
                        approved_at=str(self.approval), effective_from=str(self.approval),
                        effective_until="", approval_reference="approval")
        self.version = {"data": json.dumps({"ccpc_mapping_decision": snapshot})}
        self.scopes = [dict(name="wet", company=PILOT.company, beneficiary_department=PILOT.beneficiary,
                            selector_kind="Department Only", selector_key="DEPARTMENT_ONLY")]
        self.revisions = [self.row]
        self.events = []

    def q(self, sql, args):
        if "Mapping Scope" in sql:
            self.assertEqual(args, (PILOT.company, PILOT.beneficiary))
            return self.scopes
        if "Mapping Revision" in sql:
            return self.revisions
        if "Retirement Event" in sql:
            return self.events
        if "`tabVersion`" in sql:
            return [self.version]
        if "Accounting Mapping Decision" in sql:
            return [self.decision]
        if "Mapping Decision Use" in sql:
            return [self.use]
        self.fail("Unexpected fixture SQL")

    def test_signature_and_revision_token(self):
        match = audit.decision_matches
        self.assertTrue(match(self.decision, self.use, self.row, **self.args))
        for decision, use, row in (
            (None, self.use, self.row),
            (dict(self.decision, source_value="Maintenance"), self.use, self.row),
            (self.decision, dict(self.use, event_ref="another"), self.row),
            (self.decision, self.use, dict(self.row, modified=self.modified + timedelta(seconds=1))),
        ):
            self.assertFalse(match(decision, use, row, **self.args))

    def test_wet_mill_eligibility_and_competing_scope_fail_closed(self):
        check = lambda: audit.eligible_mapping(self.q, "Center", PILOT.beneficiary, self.zone, self.when, PILOT)
        self.assertEqual(check(), "leaf")
        self.scopes.append(dict(self.scopes[0], name="second"))
        with self.assertRaises(ValueError):
            check()

    def test_future_expired_draft_and_duplicate_retirement_fail(self):
        for row, events in (
            (dict(self.row, effective_from=self.approval + timedelta(days=1)), []),
            (dict(self.row, effective_until=self.approval + timedelta(seconds=1)), []),
            (dict(self.row, approval_state="Draft"), []),
            (self.row, [{}, {}]),
        ):
            self.revisions, self.events = [row], events
            with self.assertRaises(ValueError):
                audit.eligible_mapping(self.q, "Center", PILOT.beneficiary, self.zone, self.when, PILOT)

    def test_accepted_retirement_cutoff_is_exclusive(self):
        from copy import deepcopy

        cutoff = self.approval + timedelta(minutes=1)
        request = dict(name="request", kind="Center", revision="rev", company=PILOT.company,
                       mapping_scope="wet", financial_value="leaf", maker="retirement-maker",
                       request_state="Accepted", decided_by="retirement-checker", decided_at=cutoff,
                       target_hash=audit.digest("Center", PILOT.company, "wet", PILOT.beneficiary, "rev",
                                                "leaf", "maker", "checker", self.approval, "approval",
                                                self.approval, None))
        self.events = [dict(name="event", company=PILOT.company, mapping_scope="wet",
                            approved_by="retirement-checker", approved_at=cutoff, cutoff_at=cutoff,
                            decision="retire", retirement_request="request",
                            target_key=audit.digest("Center", "rev"),
                            event_hash=audit.digest("Center", "rev", "retire", "retirement-checker", cutoff))]
        base = self.q

        def q(sql, args):
            if "Retirement Request" in sql:
                return [request]
            return base(sql, args)

        with patch.object(audit, "evidence", return_value=True):
            self.assertEqual(audit.cutoff_at(q, self.row, "Center", PILOT.beneficiary, "leaf",
                                            self.args["approved"], None, self.when, self.zone, PILOT),
                             cutoff.replace(tzinfo=self.zone))
            with self.assertRaises(ValueError):
                audit.eligible_mapping(q, "Center", PILOT.beneficiary, self.zone, self.when, PILOT)
            self.events = deepcopy(self.events)
            self.events[0]["cutoff_at"] += timedelta(seconds=1)
            with self.assertRaises(ValueError):
                audit.eligible_mapping(q, "Center", PILOT.beneficiary, self.zone, self.when, PILOT)


class SnapshotTests(TestCase):
    def test_available_unreserved_stock_uom_and_valuation(self):
        item = dict(name=PILOT.item, disabled=0, is_stock_item=1, stock_uom="Nos")
        bin_row = dict(actual_qty=2, reserved_stock=1, stock_value=20, valuation_rate=10)
        ledger = dict(qty_after_transaction=2, stock_value=20, valuation_rate=10)
        child = dict(uom="Nos")
        self.assertTrue(audit.stock_ready(item, bin_row, ledger, child, PILOT))
        self.assertFalse(audit.stock_ready(item, dict(bin_row, reserved_stock=2), ledger, child, PILOT))
        self.assertFalse(audit.stock_ready(item, bin_row, dict(ledger, stock_value=19), child, PILOT))
        self.assertFalse(audit.stock_ready(item, bin_row, ledger, dict(uom="Box"), PILOT))

    def test_missing_slip_stops_scoped_queries(self):
        output, calls = [], []

        def q(sql, args=()):
            calls.append((sql, args))
            return []

        result = audit.Results(output.append)
        audit.run_snapshot(q, result, "hidden", "UTC", PILOT)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[-1][1], (PILOT.slip,))
        self.assertEqual(result.finish(), 1)
        self.assertNotIn("hidden", " ".join(output))

    def test_snapshot_flags_wrong_equipment_and_duplicate_issue_without_leaking_identity(self):
        output = []
        sensitive = "synthetic-identity-do-not-output"
        leaf = dict(company=PILOT.company, is_group=0, disabled=0)
        tables = {
            "Installed Application": [{"app_name": a, "app_version": v} for a, v in (
                ("frappe", "16.33.1"), ("erpnext", "16.34.2"), ("ccpcerp", "0.0.1"))],
            "Withdrawal Slip": [dict(name=PILOT.slip, docstatus=0, status="Draft", owner=sensitive,
                                     approving_supervisor=sensitive, company=PILOT.company,
                                     requesting_company=PILOT.company, department=PILOT.requesting,
                                     work_for_department=PILOT.beneficiary, work_for_section=None,
                                     source_warehouse=PILOT.warehouse, equipment=PILOT.equipment,
                                     ccpc_material_use="Routine Maintenance", received_by_present=0)],
            "Withdrawal Slip Item": [dict(item_code=PILOT.item, requested_qty=1, uom="Nos", issued_qty=0)],
            "Stock Entry": [dict(docstatus=1, n=1)],
            "Department": [leaf],
            "Equipment Registry": [dict(name=PILOT.equipment, company=PILOT.company,
                                        department=PILOT.requesting, section=None, status="Active")],
            "Item": [dict(name=PILOT.item, item_group="Bearings", disabled=0, is_stock_item=1,
                          stock_uom="Nos", has_serial_no=0, has_batch_no=1)],
            "Item Group": [dict(name="Bearings", is_group=0)],
            "Warehouse": [dict(leaf, lft=2, rgt=3)],
            "Bin": [dict(actual_qty=2, reserved_stock=0, valuation_rate=10, stock_value=20)],
            "Stock Ledger Entry": [dict(qty_after_transaction=2, stock_value=20, valuation_rate=10)],
            "Company": [dict(enable_perpetual_inventory=1, default_inventory_account=None,
                             valuation_method="FIFO")],
            "Accounting Dimension": [dict(document_type="Department")],
            "User": [dict(enabled=1)],
        }

        def q(sql, args=()):
            import re

            table = re.search(r"FROM `tab([^`]+)`", sql)
            if not table:
                return []
            if table[1] == "Warehouse" and sql.startswith("SELECT account"):
                return []
            if table[1] == "Department":
                return [dict(leaf, name=args[0], disabled=int(args[0] == PILOT.requesting))]
            if table[1] == "Has Role":
                return [{"role": audit.REQUESTOR if args == (sensitive,) else audit.STOCKROOM}]
            return tables.get(table[1], [])

        result = audit.Results(output.append)
        audit.run_snapshot(q, result, "synthetic-issuer", "UTC", PILOT)
        self.assertEqual(result.finish(), 1)
        output = "\n".join(output)
        self.assertIn("PASS | Persisted item row", output)
        self.assertIn("FAIL | Linked Stock Entries", output)
        self.assertIn("FAIL | Equipment and actual beneficiary", output)
        self.assertIn("FAIL | Requesting Department master", output)
        self.assertIn("PASS | Stock and valuation", output)
        self.assertIn("UNVERIFIED | Serial/batch eligibility", output)
        self.assertIn("UNVERIFIED | Signed Finance", output)
        self.assertNotIn(sensitive, output)
