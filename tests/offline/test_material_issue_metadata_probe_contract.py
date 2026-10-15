"""Offline source-only tests. No ERPNext, Docker, database or PRODUCTION calls."""
import ast
from pathlib import Path
import subprocess
import unittest

SCRIPT = (Path(__file__).resolve().parents[2]
          / "scripts/development/operator"
          / "ccpc_material_issue_isolated_metadata_readonly_review_20261015.sh")


class TestMetadataSourceOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = SCRIPT.read_text(encoding="utf-8")
        assert cls.shell.count("<<'PYTHON'\n") == 1
        cls.python = cls.shell.split("<<'PYTHON'\n", 1)[1].rsplit("\nPYTHON\n", 1)[0]
        cls.tree = ast.parse(cls.python)

    def test_bash_and_python_syntax_without_execution(self):
        p = subprocess.run(["bash", "-n", str(SCRIPT)], text=True,
                           capture_output=True, check=False)
        self.assertEqual(p.returncode, 0, p.stderr)
        ast.parse(self.python)

    def test_dev_label_and_approval_gate_precede_docker(self):
        self.assertLess(self.shell.index("CCPC_METADATA_READONLY_APPROVED"),
                        self.shell.index("docker inspect"))
        self.assertLess(self.shell.index("frappe_docker_devcontainer|frappe|true"),
                        self.shell.index("docker exec -i"))
        self.assertNotIn("ccpcerp.local", self.shell)
        self.assertNotIn("frappe_docker-backend", self.shell)

    def test_no_commit_and_read_only_transaction(self):
        calls = [node for node in ast.walk(self.tree)
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute)]
        executes = [n for n in calls if n.func.attr == "execute"
                    and isinstance(n.func.value, ast.Name)
                    and n.func.value.id == "cur"]
        self.assertEqual(len(executes), 2)
        self.assertEqual(sum(isinstance(n.args[0], ast.Constant)
                             and n.args[0].value == "START TRANSACTION READ ONLY"
                             for n in executes), 1)
        self.assertFalse(any(n.func.attr == "commit" for n in calls))

    def test_all_metadata_calls_use_static_select(self):
        queries = [node for node in ast.walk(self.tree)
                   if isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Name)
                   and node.func.id == "query"]
        self.assertGreaterEqual(len(queries), 6)
        for n in queries:
            self.assertIsInstance(n.args[0], ast.Constant)
            self.assertTrue(n.args[0].value.strip().upper().startswith("SELECT "))

    def test_no_frappe_or_stock_posting_calls(self):
        imports = [n for n in ast.walk(self.tree)
                   if isinstance(n, (ast.Import, ast.ImportFrom))]
        imported = [a.name for n in imports for a in n.names]
        self.assertFalse(any(x == "frappe" or x.startswith("frappe.") for x in imported))
        self.assertNotIn("issue_withdrawal_slip(", self.shell)
        self.assertNotIn("docker compose ", self.shell)
        self.assertNotIn("docker restart", self.shell)


if __name__ == "__main__":
    unittest.main()
