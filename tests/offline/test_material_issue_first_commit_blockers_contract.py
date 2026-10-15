"""Source-only NO-GO contract: records V2 gaps, not transaction readiness.

Never imports Frappe, opens SQL/Redis/Docker, or executes the posting script.
Tests deliberately assert that the current review-only V2 *still blocks* the
normal-series INSERT and child DELETE, and *still has* an unsafe broad-WHERE gap.
"""

import ast
import os
from pathlib import Path
import re
import subprocess
import unittest


SCRIPT = Path(os.environ.get(
    "CCPC_V2_SCRIPT",
    Path(__file__).resolve().parents[2] / "scripts/development/operator"
    / "ccpc_material_issue_first_commit_review_only_v2_20261015.sh",
))


class Blocked(Exception):
    pass


def stop(message):
    raise Blocked(message)


class TestFirstCommitKnownBlockers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = SCRIPT.read_text(encoding="utf-8")
        cls.embedded = cls.shell.split("<<'PY'\n", 1)[1].rsplit("\nPY\n", 1)[0]
        cls.tree = ast.parse(cls.embedded)

    def guard(self):
        targets = {"REVIEW_INSERT_TARGETS", "REVIEW_UPDATE_TARGETS"}
        assignments = [
            n for n in ast.walk(self.tree)
            if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id in targets for t in n.targets
            )
        ]
        helpers = [
            n for n in ast.walk(self.tree)
            if isinstance(n, ast.FunctionDef) and n.name == "review_dml_scope"
        ]
        self.assertEqual(len(assignments), 2)
        self.assertEqual(len(helpers), 1)
        namespace = {"stop": stop, "re": re, "frozenset": frozenset}
        module = ast.fix_missing_locations(ast.Module(
            body=assignments + helpers, type_ignores=[],
        ))
        exec(compile(module, "<review-only-guard>", "exec"), namespace)
        return namespace["review_dml_scope"]

    def test_review_only_shell_hard_stops_before_external_calls(self):
        self.assertEqual(subprocess.run(
            ["bash", "-n", str(SCRIPT)], capture_output=True, text=True,
        ).returncode, 0)
        self.assertLess(self.shell.index("\nexit 1\n"), self.shell.index("docker exec"))
        self.assertLess(self.shell.index("\nexit 1\n"), self.shell.index("docker inspect"))
        self.assertIn("NO-GO: Review-only v2", self.shell.split("\nexit 1\n", 1)[0])

    def test_missing_series_insert_remains_disallowed(self):
        guard = self.guard()
        with self.assertRaises(Blocked):
            guard("INSERT INTO \`tabSeries\` (\`name\`, \`current\`) VALUES (%s, 1)")
        with self.assertRaises(Blocked):
            guard("UPDATE \`tabSeries\` SET \`current\`=\`current\`+1 WHERE \`name\`=%s")

    def test_normal_child_sync_delete_remains_disallowed(self):
        guard = self.guard()
        with self.assertRaises(Blocked):
            guard("DELETE FROM \`tabWithdrawal Slip Item\` WHERE \`parent\`=%s AND \`parenttype\`=%s")
        with self.assertRaises(Blocked):
            guard("DELETE FROM \`tabStock Entry Detail\` WHERE \`parent\`=%s AND \`parentfield\`=%s")

    def test_unknown_auxiliary_writes_still_fail_closed(self):
        guard = self.guard()
        for sql in (
            "INSERT INTO \`tabPayment Ledger Entry\` (\`name\`) VALUES (%s)",
            "INSERT INTO \`__global_search\` (\`doctype\`) VALUES (%s)",
            "UPDATE \`tabSeries\` SET \`current\`=1 WHERE \`name\`=%s",
            "DELETE FROM \`tabVersion\` WHERE \`name\`=%s",
        ):
            with self.subTest(sql=sql), self.assertRaises(Blocked):
                guard(sql)

    def test_record_level_where_gap_documented_not_approved(self):
        # This is an intentionally *passing* characterization of a weakness:
        # WHERE 1 is not a safe record-level constraint but passes this regex.
        guard = self.guard()
        self.assertIsNone(guard("UPDATE \`tabBin\` SET \`actual_qty\`=0 WHERE 1"))
        self.assertIsNone(guard("UPDATE \`tabGL Entry\` SET \`debit\`=0 WHERE 1"))
        # Keep the unavoidable gate explicitly visible in the test output.
        self.assertIn("NOT a full SQL parser", self.shell)

    def test_sql_wrapper_only_not_complete_effect_interceptor(self):
        # Presence of a SQL monkeypatch is NOT proof of full DB interception.
        self.assertIn("original_sql = frappe.db.sql", self.shell)
        self.assertIn("review_dml_scope(query)", self.shell)
        self.assertIn("def limited_realtime(", self.shell)
        # V2's selected realtime interception does not intercept precommit
        # Frappe global-search Redis lpush; no runtime readiness implied.
        self.assertNotIn("global_search_queue", self.embedded)
        self.assertNotIn("cache.lpush(", self.embedded)

    def test_candidate_cannot_be_armed_as_a_side_effect_of_tests(self):
        self.assertLess(
            self.shell.index("\nexit 1\n"),
            self.shell.index("CCPC_FIRST_ISSUE_EXECUTION_APPROVED"),
        )
        self.assertNotIn("subprocess.run([\"bash\", str(SCRIPT)]", __doc__ or "")


if __name__ == "__main__":
    unittest.main()
