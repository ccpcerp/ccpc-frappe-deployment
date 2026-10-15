"""Credential-free negative tests of the inert pinned-source path model."""
import ast
from pathlib import Path
import unittest

from material_issue_effect_routes import (
    CANDIDATE_HOOKS, ROUTES, EffectRoute, RouteReviewError, analyze_route_claims,
)


class RouteModelTests(unittest.TestCase):
    def test_empty_hook_claims_leave_all_routes_uncovered(self):
        report = analyze_route_claims(())
        self.assertEqual(report["route_count"], len(ROUTES))
        self.assertEqual(len(report["theoretically_uncovered_routes"]), len(ROUTES))
        self.assertFalse(report["safe_to_rehearse"])

    def test_only_qb_hook_misses_sql_execution_and_series_paths(self):
        report = analyze_route_claims(("qb.run",))
        self.assertIn("series_counter", report["theoretically_uncovered_routes"])
        self.assertIn("search_sql_fallback", report["theoretically_uncovered_routes"])

    def test_db_sql_hook_misses_non_sql_side_effect(self):
        report = analyze_route_claims(("db.sql",))
        self.assertNotIn("child_qb_delete", report["theoretically_uncovered_routes"])
        self.assertIn("search_redis_push", report["theoretically_uncovered_routes"])
        self.assertIn("possible_cursor_bypass", report["theoretically_uncovered_routes"])

    def test_high_level_redis_hook_does_not_cover_raw_client(self):
        report = analyze_route_claims(("cache.lpush",))
        self.assertNotIn("search_redis_push", report["theoretically_uncovered_routes"])
        self.assertIn("possible_redis_bypass", report["theoretically_uncovered_routes"])

    def test_raw_sql_and_redis_claims_still_do_not_prove_runtime_binding(self):
        report = analyze_route_claims(("cursor.execute", "redis.lpush"))
        self.assertFalse(report["runtime_hook_binding_verified"])
        self.assertFalse(report["sql_driver_coverage_verified"])
        self.assertFalse(report["redis_endpoint_isolation_verified"])

    def test_fallback_sql_is_distinct_from_redis_push(self):
        report = analyze_route_claims(("cache.lpush",))
        self.assertIn("search_sql_fallback", report["theoretically_uncovered_routes"])

    def test_savepoint_requires_separate_sql_capture(self):
        report = analyze_route_claims(("callback.before_rollback",))
        self.assertIn("savepoint_sql", report["theoretically_uncovered_routes"])

    def test_callback_claims_do_not_cover_custom_hooks(self):
        report = analyze_route_claims(("callback.before_commit", "callback.before_rollback"))
        self.assertIn("document_custom_hooks", report["theoretically_uncovered_routes"])

    def test_every_candidate_hook_claimed_still_no_go(self):
        report = analyze_route_claims(tuple(sorted(CANDIDATE_HOOKS)))
        self.assertFalse(report["theoretically_uncovered_routes"])
        self.assertTrue(report["all_declared_routes_intersect_claimed_hooks"])
        for name in ("safe_to_commit", "safe_to_rehearse", "source_graph_exhaustive",
                     "runtime_hook_binding_verified", "rollback_external_effects_verified"):
            self.assertFalse(report[name])

    def test_unverified_routes_are_marked_explicitly(self):
        report = analyze_route_claims(())
        self.assertIn("possible_redis_bypass", report["routes_needing_source_review"])
        self.assertIn("document_cache", report["routes_needing_source_review"])
        self.assertNotIn("child_qb_delete", report["routes_needing_source_review"])

    def test_sql_and_external_sinks_are_not_conflated(self):
        report = analyze_route_claims(())
        self.assertIn("search_redis_push", report["external_effect_routes"])
        self.assertNotIn("search_sql_fallback", report["external_effect_routes"])

    def test_unknown_hook_and_duplicate_hook_rejected(self):
        for claims in (("cache.lpush", "cache.lpush"), ("unsafe.magic",)):
            with self.subTest(claims=claims), self.assertRaises(RouteReviewError):
                analyze_route_claims(claims)

    def test_non_tuple_or_untyped_claim_rejected(self):
        for claims in (["db.sql"], (7,), None):
            with self.subTest(claims=claims), self.assertRaises(RouteReviewError):
                analyze_route_claims(claims)

    def test_invalid_or_empty_routes_rejected(self):
        for routes in ((), [ROUTES[0]], ("fake",)):
            with self.subTest(routes=routes), self.assertRaises(RouteReviewError):
                analyze_route_claims((), routes)

    def test_duplicate_route_names_rejected(self):
        with self.assertRaises(RouteReviewError):
            analyze_route_claims((), (ROUTES[0], ROUTES[0]))

    def test_invalid_route_sink_or_evidence_rejected(self):
        for route in (EffectRoute("a", ("x", "y"), "committed", "pinned_source"),
                      EffectRoute("a", ("x", "y"), "sql", "asserted")):
            with self.subTest(route=route), self.assertRaises(RouteReviewError):
                analyze_route_claims((), (route,))

    def test_model_has_no_runtime_import_or_entrypoint(self):
        source = (Path(__file__).parent / "material_issue_effect_routes.py").read_text()
        tree = ast.parse(source)
        imports = {(node.module or "").split(".")[0]
                   for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(imports, {"dataclasses"})
        for prohibited in ("import frappe", "import redis", "import MySQLdb", "import docker",
                           "import subprocess", "def main(", "db.sql(", "conn.commit("):
            self.assertNotIn(prohibited, source)


if __name__ == "__main__":
    unittest.main()
