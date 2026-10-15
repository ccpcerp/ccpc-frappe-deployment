"""Adversarial, credential-free tests for a NON-RUNNABLE coverage model."""
import ast
from pathlib import Path
import unittest

from material_issue_capture_coverage import (
    ISOLATED_SITE,
    FrozenNamedBinds,
    REVIEW_SURFACES,
    SyntheticCaptureEvent,
    UnreviewedCapture,
    review_synthetic_coverage,
)


def sql_event(text="DELETE FROM `tabWithdrawal Slip Item` WHERE `parent`=%s", binds=("WS-SYNTHETIC",),
              surface="frappe.qb.run"):
    return SyntheticCaptureEvent(ISOLATED_SITE, surface, "before_commit", text, binds)


class CoverageContractTests(unittest.TestCase):
    def test_zero_events_does_not_prove_zero_side_effects(self):
        outcome = review_synthetic_coverage((), ())
        self.assertEqual(outcome["hypothetical_sql_event_count"], 0)
        self.assertTrue(outcome["missing_capture_claims"])
        self.assertFalse(outcome["real_capture_coverage_verified"])
        self.assertFalse(outcome["safe_to_rehearse"])

    def test_all_claims_even_without_events_are_not_runtime_proof(self):
        outcome = review_synthetic_coverage(tuple(sorted(REVIEW_SURFACES)), ())
        self.assertEqual(outcome["missing_capture_claims"], ())
        self.assertFalse(outcome["real_capture_coverage_verified"])
        self.assertFalse(outcome["safe_to_commit"])

    def test_query_builder_child_delete_cannot_be_auto_approved(self):
        event = sql_event(binds=("WS-SYNTHETIC", "Withdrawal Slip", "items"))
        outcome = review_synthetic_coverage(("frappe.qb.run",), (event,))
        self.assertEqual(outcome["hypothetical_sql_event_count"], 1)
        self.assertFalse(outcome["child_sql_predicates_verified"])
        self.assertFalse(outcome["safe_to_rehearse"])

    def test_broad_update_where_one_is_not_accepted(self):
        event = sql_event("UPDATE `tabBin` SET `actual_qty`=0 WHERE 1", (), "frappe.db.sql")
        outcome = review_synthetic_coverage(("frappe.db.sql",), (event,))
        self.assertFalse(outcome["safe_to_commit"])
        self.assertFalse(outcome["child_sql_predicates_verified"])

    def test_redis_lpush_is_uncontained_even_if_declared(self):
        event = SyntheticCaptureEvent(ISOLATED_SITE, "frappe.cache.lpush", "before_commit")
        outcome = review_synthetic_coverage(("frappe.cache.lpush",), (event,))
        self.assertEqual(outcome["hypothetical_non_sql_event_count"], 1)
        self.assertFalse(outcome["redis_cache_containment_verified"])

    def test_unclaimed_raw_redis_sink_is_visible_as_gap(self):
        event = SyntheticCaptureEvent(ISOLATED_SITE, "redis.raw_client", "before_commit")
        outcome = review_synthetic_coverage(("frappe.cache.lpush",), (event,))
        self.assertIn("redis.raw_client", outcome["events_on_unclaimed_surfaces"])

    def test_direct_driver_sink_not_laundered_as_query_builder(self):
        event = sql_event("UPDATE `tabGL Entry` SET `debit`=0 WHERE 1", (), "db.cursor.execute")
        outcome = review_synthetic_coverage(("frappe.qb.run",), (event,))
        self.assertEqual(outcome["events_on_unclaimed_surfaces"], ("db.cursor.execute",))

    def test_callbacks_are_not_equivalent_to_transaction_rollback(self):
        events = (
            SyntheticCaptureEvent(ISOLATED_SITE, "frappe.db.before_commit", "before_commit"),
            SyntheticCaptureEvent(ISOLATED_SITE, "frappe.db.after_rollback", "after_rollback"),
        )
        outcome = review_synthetic_coverage(("frappe.db.before_commit", "frappe.db.after_rollback"), events)
        self.assertEqual(outcome["hypothetical_non_sql_event_count"], 2)
        self.assertFalse(outcome["before_after_rollback_delta_verified"])

    def test_wrong_site_rejected(self):
        with self.assertRaises(UnreviewedCapture):
            SyntheticCaptureEvent("development.localhost", "frappe.db.sql", "before_commit", "SELECT 1", ())

    def test_sql_without_exact_tuple_binds_rejected(self):
        for sql, binds in (("DELETE FROM x", None), ("SELECT 1", []), ("", ())):
            with self.subTest(sql=sql, binds=binds), self.assertRaises(UnreviewedCapture):
                SyntheticCaptureEvent(ISOLATED_SITE, "frappe.db.sql", "before_commit", sql, binds)

    def test_query_builder_named_dictionary_binding_shape_supported_without_certification(self):
        sql = "DELETE FROM `tabStock Entry Detail` WHERE `parent`=%(param1)s"
        event = sql_event(sql, FrozenNamedBinds((("param1", "'MAT-STE-SYNTHETIC'"),)))
        report = review_synthetic_coverage(("frappe.qb.run",), (event,))
        self.assertEqual(report["hypothetical_sql_event_count"], 1)
        self.assertFalse(report["child_sql_predicates_verified"])
        self.assertFalse(report["safe_to_rehearse"])

    def test_named_multisql_fallback_fields_supported(self):
        sql = "INSERT INTO `__global_search` (`doctype`, `name`) VALUES (%(doctype)s, %(name)s)"
        event = sql_event(sql, FrozenNamedBinds((("doctype", "Stock Entry"), ("name", "STE-SYNTHETIC"))), "frappe.db.multisql")
        self.assertFalse(review_synthetic_coverage(("frappe.db.multisql",), (event,))["safe_to_commit"])

    def test_mismatched_named_placeholders_rejected(self):
        sql = "DELETE FROM `tabStock Entry Detail` WHERE `parent`=%(param1)s"
        for binds in (FrozenNamedBinds(()), FrozenNamedBinds((("param2", "x"),)),
                      FrozenNamedBinds((("param1", "x"), ("param2", "y")))):
            with self.subTest(binds=binds), self.assertRaises(UnreviewedCapture):
                sql_event(sql, binds)

    def test_direct_dict_is_not_immutable_evidence(self):
        with self.assertRaises(UnreviewedCapture):
            sql_event("DELETE FROM x WHERE parent=%(param1)s", {"param1": "foo"})

    def test_duplicate_named_key_rejected(self):
        with self.assertRaises(UnreviewedCapture):
            FrozenNamedBinds((("param1", "a"), ("param1", "b")))

    def test_malformed_named_keys_rejected(self):
        for key in ("", "1param", "param-1", "param name", 42):
            with self.subTest(key=key), self.assertRaises(UnreviewedCapture):
                FrozenNamedBinds(((key, "x"),))

    def test_mutable_named_value_and_outer_entries_rejected(self):
        for entries in ([("param1", "x")], (("param1", [1]),), (("param1", {"x": 1}),)):
            with self.subTest(entries=entries), self.assertRaises(UnreviewedCapture):
                FrozenNamedBinds(entries)

    def test_mutable_positional_value_rejected(self):
        with self.assertRaises(UnreviewedCapture):
            sql_event("SELECT %s", (["x"],))

    def test_named_binding_is_immutable_after_creation(self):
        from dataclasses import FrozenInstanceError
        pairs = FrozenNamedBinds((("param1", "a"),))
        with self.assertRaises(FrozenInstanceError):
            pairs.entries = (("param1", "b"),)
        self.assertEqual(pairs.entries, (("param1", "a"),))

    def test_unknown_surface_and_phase_rejected(self):
        for surface, phase in (("redis.unrecognized", "before_commit"),
                               ("frappe.cache.lpush", "unknown_phase")):
            with self.subTest(surface=surface, phase=phase), self.assertRaises(UnreviewedCapture):
                SyntheticCaptureEvent(ISOLATED_SITE, surface, phase)

    def test_duplicate_unknown_and_untyped_declarations_fail(self):
        for claims in (("frappe.db.sql", "frappe.db.sql"), ("sql.any",), ["frappe.db.sql"]):
            with self.subTest(claims=claims), self.assertRaises(UnreviewedCapture):
                review_synthetic_coverage(claims, ())

    def test_unknown_or_untyped_events_fail(self):
        for events in (({"surface": "frappe.db.sql"},), [sql_event()]):
            with self.subTest(events=events), self.assertRaises(UnreviewedCapture):
                review_synthetic_coverage((), events)

    def test_non_sql_event_cannot_disguise_sql(self):
        with self.assertRaises(UnreviewedCapture):
            SyntheticCaptureEvent(ISOLATED_SITE, "frappe.cache.lpush", "before_commit", "DELETE FROM x", ())

    def test_unknown_phase_does_not_silently_default_to_safe(self):
        event = SyntheticCaptureEvent(ISOLATED_SITE, "frappe.document_hooks", "unknown")
        outcome = review_synthetic_coverage(("frappe.document_hooks",), (event,))
        self.assertFalse(outcome["safe_to_rehearse"])

    def test_source_remains_pure_and_has_no_runtime_adapter(self):
        source = (Path(__file__).parent / "material_issue_capture_coverage.py").read_text()
        tree = ast.parse(source)
        roots = {
            a.name.split(".")[0]
            for node in ast.walk(tree) if isinstance(node, ast.Import)
            for a in node.names
        } | {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(roots, {"dataclasses", "re"})
        for forbidden in ("import frappe", "import redis", "import MySQLdb", "subprocess",
                          "docker exec", "def main(", "conn.commit(", "frappe.db.sql("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
