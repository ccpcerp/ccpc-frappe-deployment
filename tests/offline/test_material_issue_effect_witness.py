"""Credential-free offline tests; does not invoke any ERPNext service."""
import ast
from pathlib import Path
import unittest

from material_issue_effect_witness import (
    EXISTING_SERIES_INCREMENT,
    FIRST_SERIES_INSERT,
    IsolatedSeriesBaseline,
    OfflineEffectWitness,
    UnreviewedEffect,
)


KEY = "MAT-STE-2026-"  # Synthetic review key; NOT a verified runtime key.


class OfflineWitnessTests(unittest.TestCase):
    def baseline(self, current=None):
        return IsolatedSeriesBaseline("ccpc-integration2.localhost", KEY, current)

    def test_first_series_insert_matches_only_its_key(self):
        witness = OfflineEffectWitness(self.baseline())
        self.assertEqual(witness.observe_sql(FIRST_SERIES_INSERT, (KEY,)),
                         "MATCHED_EXPECTED_SERIES_SQL_ONLY")
        self.assertFalse(witness.outcome()["safe_to_commit"])
        self.assertFalse(witness.outcome()["safe_to_execute"])

    def test_existing_series_increment_matches_only_its_key(self):
        witness = OfflineEffectWitness(self.baseline(4))
        self.assertEqual(witness.observe_sql(EXISTING_SERIES_INCREMENT, (KEY,)),
                         "MATCHED_EXPECTED_SERIES_SQL_ONLY")
        self.assertFalse(witness.outcome()["safe_to_execute"])

    def test_wrong_key_rejected(self):
        for key in ("MAT-STE-2025-", "MAT-STE-2026-x", ""):
            with self.subTest(key=key):
                with self.assertRaises(UnreviewedEffect):
                    OfflineEffectWitness(self.baseline()).observe_sql(
                        FIRST_SERIES_INSERT, (key,))

    def test_wrong_site_or_series_format_rejected(self):
        for site, key in (
            ("development.localhost", KEY),
            ("ccpc-integration2.localhost", "MAT-STE-x-"),
            ("ccpc-integration2.localhost", "MAT-STE-2026-;DROP"),
        ):
            with self.subTest(site=site, key=key), self.assertRaises(UnreviewedEffect):
                IsolatedSeriesBaseline(site, key, None)

    def test_unknown_or_negative_counter_rejected(self):
        for current in (True, -1, 1.5, "1"):
            with self.subTest(current=current), self.assertRaises(UnreviewedEffect):
                self.baseline(current)

    def test_broad_update_where_true_rejected(self):
        for sql in (
            "UPDATE `tabBin` SET `actual_qty`=0 WHERE 1",
            "UPDATE `tabGL Entry` SET `debit`=0 WHERE 1",
            "UPDATE `tabWithdrawal Slip Item` SET `issued_qty`=1 WHERE 1",
        ):
            with self.subTest(sql=sql), self.assertRaises(UnreviewedEffect):
                OfflineEffectWitness(self.baseline()).observe_sql(sql, ())

    def test_child_delete_remains_blocked(self):
        sql = "DELETE FROM `tabWithdrawal Slip Item` WHERE `parent`=%s"
        with self.assertRaises(UnreviewedEffect):
            OfflineEffectWitness(self.baseline()).observe_sql(sql, ("WS-2026-00001",))

    def test_new_series_write_rejects_update_variant(self):
        with self.assertRaises(UnreviewedEffect):
            OfflineEffectWitness(self.baseline()).observe_sql(
                EXISTING_SERIES_INCREMENT, (KEY,))

    def test_existing_series_write_rejects_insert_variant(self):
        with self.assertRaises(UnreviewedEffect):
            OfflineEffectWitness(self.baseline(1)).observe_sql(
                FIRST_SERIES_INSERT, (KEY,))

    def test_duplicated_series_mutation_rejected(self):
        witness = OfflineEffectWitness(self.baseline())
        witness.observe_sql(FIRST_SERIES_INSERT, (KEY,))
        with self.assertRaises(UnreviewedEffect):
            witness.observe_sql(FIRST_SERIES_INSERT, (KEY,))

    def test_sql_comment_or_non_tuple_args_rejected(self):
        for sql, params in (
            (FIRST_SERIES_INSERT + "; UPDATE `tabBin` SET `actual_qty`=0", (KEY,)),
            (FIRST_SERIES_INSERT + " -- extra", (KEY,)),
            (FIRST_SERIES_INSERT, [KEY]),
            (FIRST_SERIES_INSERT, (KEY, 1)),
        ):
            with self.subTest(sql=sql), self.assertRaises(UnreviewedEffect):
                OfflineEffectWitness(self.baseline()).observe_sql(sql, params)

    def test_external_redis_cache_enqueue_always_rejected(self):
        witness = OfflineEffectWitness(self.baseline())
        for kind in ("global_search_queue", "cache.clear", "realtime", "enqueue", "unknown"):
            with self.subTest(kind=kind), self.assertRaises(UnreviewedEffect):
                witness.observe_external_effect(kind)
        self.assertFalse(witness.outcome()["global_search_redis_contained"])

    def test_outcome_never_signals_ready_even_if_expected_sql_seen(self):
        witness = OfflineEffectWitness(self.baseline())
        witness.observe_sql(FIRST_SERIES_INSERT, (KEY,))
        state = witness.outcome()
        self.assertTrue(state["series_statement_matched"])
        for key in ("safe_to_execute", "safe_to_commit", "database_rollback_verified",
                    "child_delete_reviewed", "global_search_redis_contained"):
            self.assertFalse(state[key])

    def test_source_has_no_runtime_import_or_entrypoint(self):
        source = (Path(__file__).parent / "material_issue_effect_witness.py").read_text()
        tree = ast.parse(source)
        imported = [
            node.module if isinstance(node, ast.ImportFrom) else alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in (node.names if isinstance(node, ast.Import) else [None])
        ]
        self.assertTrue(set(imported).issubset({"dataclasses", "re"}))
        for forbidden in ("import frappe", "import MySQLdb", "import redis", "docker exec",
                          "def main(", "def execute(", "subprocess", "conn.commit("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
