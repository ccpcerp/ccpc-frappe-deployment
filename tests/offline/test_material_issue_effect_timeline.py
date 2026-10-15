"""Credential-free negative tests for synthetic nontransactional effect timelines."""
import ast
from pathlib import Path
import unittest

from material_issue_effect_timeline import (
    HypotheticalEffect, InvalidSyntheticTimeline, SITE, inspect_synthetic_timeline,
)


def event(n, kind, phase="precommit", label=None, site=SITE):
    return HypotheticalEffect(n, site, kind, phase, label or kind)


class SyntheticTimelineTests(unittest.TestCase):
    def test_no_events_are_not_proof_of_complete_capture(self):
        output = inspect_synthetic_timeline(())
        self.assertFalse(output["actual_effect_capture_verified"])
        self.assertFalse(output["safe_to_rehearse"])

    def test_sql_dml_and_full_rollback_still_not_certified(self):
        output = inspect_synthetic_timeline((event(1, "sql_dml"), event(2, "sql_rollback", "full_rollback")))
        self.assertEqual(output["sql_rollback_markers"], 1)
        self.assertFalse(output["rollback_delta_verified"])
        self.assertFalse(output["safe_to_commit"])

    def test_document_cache_eviction_precedes_full_rollback(self):
        output = inspect_synthetic_timeline((
            event(1, "redis_unlink", label="document_cache_immediate"),
            event(2, "callback_registration", label="after_rollback_redelete"),
            event(3, "sql_rollback", "full_rollback"),
        ))
        self.assertIn("document_cache_immediate", output["external_effects_before_first_rollback"])
        self.assertFalse(output["process_and_shared_cache_contained"])

    def test_slip_doctype_cache_cross_worker_publish_precommit(self):
        output = inspect_synthetic_timeline((
            event(1, "sql_dml", label="slip_status"),
            event(2, "redis_pubsub", label="clear_persistent_cache"),
            event(3, "redis_unlink", label="doctype_keys"),
            event(4, "sql_rollback", "full_rollback"),
        ))
        self.assertEqual(output["external_effects_before_first_rollback"],
                         ("clear_persistent_cache", "doctype_keys"))

    def test_realtime_immediate_pubsub_not_reversed(self):
        output = inspect_synthetic_timeline((
            event(1, "redis_pubsub", label="events_channel"),
            event(2, "sql_rollback", "full_rollback"),
        ))
        self.assertTrue(output["sql_rollback_cannot_reverse_external_effects"])

    def test_realtime_after_commit_registration_not_proof_of_flush(self):
        output = inspect_synthetic_timeline((event(1, "callback_registration", label="realtime_after_commit"),))
        self.assertEqual(output["registered_callbacks_not_proof_of_invocation"],
                         ("realtime_after_commit",))
        self.assertFalse(output["safe_to_rehearse"])

    def test_global_search_lpush_synthetic_prefix_not_isolation(self):
        output = inspect_synthetic_timeline((event(1, "redis_queue_push", label="site_prefixed_global_search"),))
        self.assertIn("site_prefixed_global_search", output["all_external_effects"])
        self.assertFalse(output["isolated_redis_endpoint_verified"])

    def test_search_sql_fallback_does_not_make_rollback_verified(self):
        output = inspect_synthetic_timeline((
            event(1, "sql_dml", label="__global_search_fallback"),
            event(2, "sql_rollback", "full_rollback"),
        ))
        self.assertFalse(output["rollback_delta_verified"])

    def test_savepoint_cannot_be_treated_as_full_cleanup(self):
        output = inspect_synthetic_timeline((
            event(1, "redis_unlink", label="pre_savepoint_eviction"),
            event(2, "sql_rollback", "savepoint"),
        ))
        self.assertIn("pre_savepoint_eviction", output["external_effects_before_first_rollback"])
        self.assertFalse(output["safe_to_rehearse"])

    def test_callback_invocation_after_rollback_is_external_effect(self):
        output = inspect_synthetic_timeline((
            event(1, "sql_rollback", "full_rollback"),
            event(2, "callback_invocation", "full_rollback", "repeat_cache_eviction"),
        ))
        self.assertEqual(output["all_external_effects"], ("repeat_cache_eviction",))

    def test_process_local_cache_is_effect_too(self):
        output = inspect_synthetic_timeline((event(1, "process_cache_invalidation"),))
        self.assertTrue(output["sql_rollback_cannot_reverse_external_effects"])

    def test_unknown_kind_and_unknown_phase_rejected(self):
        for kind, phase in (("network", "precommit"), ("redis_pubsub", "outside_time")):
            with self.subTest(kind=kind, phase=phase), self.assertRaises(InvalidSyntheticTimeline):
                event(1, kind, phase)

    def test_unknown_event_in_review_never_silent(self):
        output = inspect_synthetic_timeline((event(1, "unknown_effect", "unknown"),))
        self.assertEqual(output["unresolved_unknown_events"], ("unknown_effect",))
        self.assertFalse(output["safe_to_commit"])

    def test_cross_site_event_rejected(self):
        with self.assertRaises(InvalidSyntheticTimeline):
            event(1, "redis_unlink", site="development.localhost")

    def test_duplicate_or_out_of_order_event_rejected(self):
        for effects in ((event(1, "sql_dml"), event(1, "redis_unlink")),
                        (event(3, "sql_dml"), event(2, "sql_rollback", "full_rollback"))):
            with self.subTest(effects=effects), self.assertRaises(InvalidSyntheticTimeline):
                inspect_synthetic_timeline(effects)

    def test_list_and_dict_events_rejected(self):
        for effects in ([event(1, "sql_dml")], ({"kind": "sql_dml"},)):
            with self.subTest(effects=effects), self.assertRaises(InvalidSyntheticTimeline):
                inspect_synthetic_timeline(effects)

    def test_incorrect_rollback_phase_rejected(self):
        with self.assertRaises(InvalidSyntheticTimeline):
            event(1, "sql_rollback", "precommit")

    def test_untrusted_callback_phase_rejected(self):
        with self.assertRaises(InvalidSyntheticTimeline):
            event(1, "callback_registration", "after_commit")

    def test_source_has_no_runtime_import_or_execution_paths(self):
        source = (Path(__file__).parent / "material_issue_effect_timeline.py").read_text()
        tree = ast.parse(source)
        imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(imports, {"dataclasses"})
        for bad in ("import frappe", "import redis", "import MySQLdb", "subprocess", "docker",
                    "def main(", "conn.commit(", "frappe.db.sql("):
            self.assertNotIn(bad, source)


if __name__ == "__main__":
    unittest.main()
