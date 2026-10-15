"""Offline adversarial tests for a manifest that cannot authorize a live test."""
import ast
from pathlib import Path
import unittest

from material_issue_containment_manifest import (
    BoundaryClaim, EVIDENCE, ISOLATED_SITE, MODES, REDIS_SURFACES,
    SURFACES, InvalidManifest, review_containment_manifest,
)


def claim(surface, mode="proposed_isolation", evidence="asserted_runtime", alias=None, site=ISOLATED_SITE):
    return BoundaryClaim(site, surface, mode, evidence, alias)


class ManifestTests(unittest.TestCase):
    def test_zero_declarations_are_no_go(self):
        result = review_containment_manifest(())
        self.assertEqual(len(result["missing_surfaces"]), len(SURFACES))
        self.assertFalse(result["safe_to_stage"])

    def test_complete_asserted_runtime_declarations_not_independent_proof(self):
        result = review_containment_manifest(tuple(claim(s) for s in sorted(SURFACES)))
        self.assertTrue(result["all_named_surfaces_declared"])
        for k in ("safe_to_stage", "safe_to_rehearse", "safe_to_commit",
                  "actual_runtime_sinks_exhaustively_known", "owner_authorized_live_stage"):
            self.assertFalse(result[k])

    def test_literal_redis_key_prefix_does_not_isolate_pubsub(self):
        result = review_containment_manifest((claim("redis.cache_keys", "site_prefix_only"),))
        self.assertIn("redis.cache_keys", result["shared_or_unknown_surfaces"])
        self.assertIn("redis.cache_pubsub", result["missing_surfaces"])
        self.assertIn("redis.queue_pubsub", result["missing_surfaces"])

    def test_cache_and_queue_redis_are_distinct_sinks(self):
        result = review_containment_manifest((claim("redis.cache_keys"),))
        self.assertIn("redis.background_jobs", result["missing_surfaces"])
        self.assertIn("redis.queue_pubsub", result["missing_surfaces"])
        self.assertIn("redis.search_queue", result["missing_surfaces"])

    def test_same_declared_endpoint_alias_is_visible_risk(self):
        result = review_containment_manifest((
            claim("redis.cache_pubsub", alias="shared-redis"),
            claim("redis.queue_pubsub", alias="shared-redis"),
        ))
        self.assertEqual(result["declared_redis_endpoint_overlap"],
                         (("shared-redis", ("redis.cache_pubsub", "redis.queue_pubsub")),))

    def test_distinct_endpoint_names_not_physical_isolation_proof(self):
        result = review_containment_manifest((
            claim("redis.cache_pubsub", alias="claimed-cache"),
            claim("redis.queue_pubsub", alias="claimed-queue"),
        ))
        self.assertFalse(result["declared_redis_endpoint_overlap"])
        self.assertFalse(result["physical_redis_and_worker_isolation_verified"])

    def test_high_level_capture_claim_does_not_cover_driver(self):
        result = review_containment_manifest((claim("document.hooks", "proposed_capture"),))
        self.assertIn("sql.driver", result["missing_surfaces"])
        self.assertIn("sql.transaction", result["missing_surfaces"])

    def test_sql_rollback_does_not_cover_local_cache(self):
        result = review_containment_manifest((claim("sql.transaction"),))
        self.assertIn("process.cache", result["missing_surfaces"])
        self.assertIn("redis.cache_keys", result["missing_surfaces"])

    def test_callback_claim_does_not_cover_pubsub(self):
        result = review_containment_manifest((claim("transaction.callbacks", "proposed_capture"),))
        self.assertIn("redis.queue_pubsub", result["missing_surfaces"])
        self.assertIn("redis.cache_pubsub", result["missing_surfaces"])

    def test_series_and_delete_are_separate(self):
        result = review_containment_manifest((claim("sql.child_delete"),))
        self.assertIn("sql.series", result["missing_surfaces"])
        self.assertFalse(result["child_delete_and_series_concurrency_verified"])

    def test_backup_claim_never_proves_recovery(self):
        result = review_containment_manifest((claim("backup.recovery"),))
        self.assertFalse(result["backups_and_rollback_recovery_verified"])

    def test_all_sources_are_untrusted_even_runtime_label(self):
        self.assertEqual(EVIDENCE, frozenset({"source_only", "synthetic", "asserted_runtime"}))
        result = review_containment_manifest((claim("sql.driver", evidence="asserted_runtime"),))
        self.assertFalse(result["safe_to_commit"])

    def test_reject_wrong_site(self):
        with self.assertRaises(InvalidManifest):
            claim("sql.driver", site="development.localhost")

    def test_reject_duplicate_surface_even_if_modes_differ(self):
        with self.assertRaises(InvalidManifest):
            review_containment_manifest((claim("sql.driver"), claim("sql.driver", "shared")))

    def test_reject_unknown_surface(self):
        with self.assertRaises(InvalidManifest):
            claim("redis.magic")

    def test_reject_unknown_mode(self):
        with self.assertRaises(InvalidManifest):
            claim("sql.driver", "fully_safe")

    def test_reject_unknown_evidence(self):
        with self.assertRaises(InvalidManifest):
            claim("sql.driver", evidence="cryptographically_proven")

    def test_reject_alias_for_non_redis(self):
        with self.assertRaises(InvalidManifest):
            claim("sql.driver", alias="wrong")

    def test_reject_untyped_and_blank_alias(self):
        for alias in ("", 7, "A" * 101):
            with self.subTest(alias=alias), self.assertRaises(InvalidManifest):
                claim("redis.cache_keys", alias=alias)

    def test_reject_untyped_manifest(self):
        for manifest in ([claim("sql.driver")], ({"sql.driver": "isolate"},), None):
            with self.subTest(manifest=manifest), self.assertRaises(InvalidManifest):
                review_containment_manifest(manifest)

    def test_reject_wrong_dataclass_type(self):
        with self.assertRaises(InvalidManifest):
            review_containment_manifest(("sql.driver",))

    def test_required_surfaces_include_specific_pubsub_and_jobs(self):
        for surface in ("redis.cache_pubsub", "redis.queue_pubsub", "redis.background_jobs",
                        "redis.search_queue", "sql.child_delete", "sql.series", "process.cache"):
            self.assertIn(surface, SURFACES)
            if surface.startswith("redis."):
                self.assertIn(surface, REDIS_SURFACES)

    def test_shared_mode_always_unresolved(self):
        result = review_containment_manifest((claim("redis.cache_pubsub", "shared"),))
        self.assertIn("redis.cache_pubsub", result["shared_or_unknown_surfaces"])

    def test_unknown_mode_always_unresolved(self):
        result = review_containment_manifest((claim("filesystem.external", "unknown"),))
        self.assertIn("filesystem.external", result["shared_or_unknown_surfaces"])

    def test_no_runtime_import_or_entrypoint(self):
        p = Path(__file__).with_name("material_issue_containment_manifest.py")
        source = p.read_text()
        tree = ast.parse(source)
        imports = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertEqual(imports, {"dataclasses"})
        for blocked in ("import frappe", "import redis", "import pymysql", "import subprocess",
                        "import docker", "def main(", "frappe.db.sql(", "conn.commit("):
            self.assertNotIn(blocked, source)


if __name__ == "__main__":
    unittest.main()
