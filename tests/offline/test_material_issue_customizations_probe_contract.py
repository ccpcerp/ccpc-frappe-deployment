"""Offline, source-only contract for the CCPC second isolated metadata probe.

Never runs the probe, Docker, Frappe, Redis or a SQL database.
Run: python3 -m unittest discover -s tests/offline -p 'test_material_issue_customizations_probe_contract.py' -v
"""
import ast
from pathlib import Path
import re
import subprocess
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts/development/operator"
    / "ccpc_material_issue_isolated_customizations_readonly_review_20261015.sh"
)


class GuardStopped(Exception):
    pass


def stop(reason):
    raise GuardStopped(reason)


class TestCustomizationMetadataContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = SCRIPT.read_text(encoding="utf-8")
        assert cls.shell.count("<<'PYTHON'\n") == 1
        cls.embedded = cls.shell.split("<<'PYTHON'\n", 1)[1].rsplit("\nPYTHON\n", 1)[0]
        cls.tree = ast.parse(cls.embedded)

    def function(self, function_name, dependencies=None):
        methods = [
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef) and node.name == function_name
        ]
        self.assertEqual(len(methods), 1)
        namespace = {"stop": stop, "re": re, **(dependencies or {})}
        module = ast.fix_missing_locations(ast.Module(body=methods, type_ignores=[]))
        exec(compile(module, "<source-extracted-offline-helper>", "exec"), namespace)
        return namespace[function_name]

    def test_shell_and_embedded_python_are_parseable(self):
        result = subprocess.run(["bash", "-n", str(SCRIPT)], check=False,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        ast.parse(self.embedded)

    def test_staging_token_precedes_dev_only_docker(self):
        self.assertLess(self.shell.index("CCPC_METADATA_DETAILS_APPROVED"),
                        self.shell.index("docker inspect"))
        self.assertLess(self.shell.index("frappe_docker_devcontainer|frappe|true"),
                        self.shell.index("docker exec -i"))
        self.assertNotIn("CCPC_METADATA_READONLY_APPROVED", self.shell)
        self.assertNotIn("frappe_docker-backend", self.shell)

    def test_read_only_sql_and_static_select_calls_only(self):
        calls = [node for node in ast.walk(self.tree) if isinstance(node, ast.Call)]
        executions = [
            n for n in calls if isinstance(n.func, ast.Attribute)
            and isinstance(n.func.value, ast.Name)
            and n.func.value.id == "cur" and n.func.attr == "execute"
        ]
        self.assertEqual(len(executions), 2)
        self.assertEqual(
            sum(isinstance(n.args[0], ast.Constant)
                and n.args[0].value == "START TRANSACTION READ ONLY"
                for n in executions), 1,
        )
        sql_calls = [
            n for n in calls if isinstance(n.func, ast.Name) and n.func.id == "fetch"
        ]
        self.assertGreaterEqual(len(sql_calls), 7)
        for call in sql_calls:
            self.assertIsInstance(call.args[0], ast.Constant)
            self.assertTrue(call.args[0].value.strip().upper().startswith("SELECT "))
        self.assertFalse(any(isinstance(n.func, ast.Attribute)
                             and n.func.attr == "commit" for n in calls))
        self.assertNotIn("frappe.init(", self.shell)
        self.assertNotIn("issue_withdrawal_slip(", self.shell)

    def test_customization_columns_never_request_property_values_in_bulk(self):
        self.assertIn(
            "SELECT doc_type, field_name, property, property_type FROM", self.embedded
        )
        self.assertIn("SELECT dt, fieldname, fieldtype FROM", self.embedded)
        self.assertIn("field_name IS NULL OR field_name=%s", self.embedded)
        self.assertIn("WHERE doc_type=%s", self.embedded)
        self.assertIn("safe_pattern(value)", self.embedded)
        self.assertIn("MAX_RECORDS = 80", self.embedded)

    def test_identifier_rejects_newlines_and_control_chars(self):
        fn = self.function("safe_identifier")
        self.assertEqual(fn("naming_series"), "naming_series")
        self.assertEqual(fn("Section Break", allow_space=True), "Section Break")
        for bad in ("no\ninjection", "bad;UPDATE", "", "..", "a" * 90):
            with self.subTest(bad=bad):
                with self.assertRaises(GuardStopped):
                    fn(bad)

    def test_naming_pattern_redacts_nonstandard_values(self):
        fn = self.function("safe_pattern")
        self.assertEqual(fn("MAT-STE-.YYYY.-"), "MAT-STE-.YYYY.-")
        self.assertEqual(fn("naming_series:"), "naming_series:")
        self.assertEqual(fn(None), "UNAVAILABLE")
        self.assertEqual(fn("MAT-STE-.YYYY.-\nABC-.YYYY.-"),
                         "MAT-STE-.YYYY.-,ABC-.YYYY.-")
        self.assertEqual(fn("sensitive@example.com;DROP"),
                         "NONSTANDARD_PATTERN_REDACTED")
        self.assertEqual(fn("hello\nworld\n" * 7), "TOO_MANY_OPTIONS")

    def test_config_file_search_flag_uses_three_states(self):
        fn = self.function("flag_state")
        self.assertEqual(fn(True), "DISABLED_BY_CONFIG")
        self.assertEqual(fn("1"), "DISABLED_BY_CONFIG")
        self.assertEqual(fn(False), "NOT_DISABLED_BY_CONFIG")
        self.assertEqual(fn(None), "NOT_DISABLED_BY_CONFIG")
        self.assertEqual(fn("unknown"), "UNKNOWN_CONFIG_FORMAT")
        self.assertIn("merged = {**common, **isolated}", self.embedded)
        self.assertIn("NOTE: FILE CONFIG DOES NOT VERIFY LIVE REDIS", self.embedded)

    def test_no_production_or_persistent_dev_sql(self):
        self.assertIn("TEST_SITE = 'ccpc-integration2.localhost'", self.embedded)
        self.assertIn("SHARED_SITE = 'development.localhost'", self.embedded)
        self.assertIn("isolated['db_name'] == shared['db_name']", self.embedded)
        self.assertIn("host='mariadb', port=3306", self.embedded)
        self.assertIn("SELECT DATABASE()", self.embedded)
        self.assertNotIn("ccpcerp.localhost", self.shell)
        self.assertNotIn("docker restart", self.shell)
        self.assertNotIn("docker compose", self.shell)


if __name__ == "__main__":
    unittest.main()
