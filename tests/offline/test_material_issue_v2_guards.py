"""OFFLINE tests of the source-only v2 Material Issue guard helpers.

Never connects to ERPNext, Docker, SQL, Redis, or PRODUCTION.
Run from the deployment GitHub checkout with:
  python3 -m unittest discover -s tests/offline -p 'test_material_issue_v2_guards.py' -v
"""
import ast
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

SCRIPT = Path(os.environ.get(
    "CCPC_V2_SCRIPT",
    Path(__file__).resolve().parents[2]
    / "scripts/development/operator/ccpc_material_issue_first_commit_review_only_v2_20261015.sh",
))


class GuardBlocked(Exception):
    pass


def stop(reason):
    raise GuardBlocked(reason)


class TestMaterialIssueV2ReviewOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = SCRIPT.read_text(encoding="utf-8")
        cls.python = cls.shell.split("<<'PY'\n", 1)[1].rsplit("\nPY\n", 1)[0]
        cls.tree = ast.parse(cls.python, filename="embedded-v2-guard.py")

    def extract(self, name, globals_dict):
        matches = [node for node in ast.walk(self.tree)
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and node.name == name]
        self.assertEqual(len(matches), 1, f"Expected exactly one {name} definition")
        mod = ast.fix_missing_locations(ast.Module(body=[matches[0]], type_ignores=[]))
        scope = {"stop": stop, "re": re, **globals_dict}
        exec(compile(mod, "<offline-extracted-guard>", "exec"), scope)
        return scope[name], scope

    def test_source_syntax_without_execution(self):
        ast.parse(self.python)
        completed = subprocess.run(["bash", "-n", str(SCRIPT)],
                                   capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_entrypoint_unconditionally_inert(self):
        prefix = self.shell.split("\nexit 1\n", 1)[0]
        self.assertIn("NO-GO: Review-only v2", prefix)
        self.assertNotIn("docker exec", prefix)
        self.assertNotIn("docker inspect", prefix)
        self.assertNotIn("mkdir -m", prefix)
        self.assertIn("\nexit 1\n", self.shell)

    def test_exact_dev_endpoint_fail_closed(self):
        fn, _ = self.extract("ensure_dev_endpoint", {
            "EXPECTED_DEV_DB_HOST": "mariadb", "EXPECTED_DEV_DB_PORT": 3306,
        })
        self.assertEqual(fn({"db_name": "fictional"}, {"db_host": "mariadb", "db_port": "3306"}),
                         ("mariadb", 3306))
        self.assertEqual(fn({"db_host": "mariadb", "db_port": 3306}, {}), ("mariadb", 3306))
        invalid = [
            ({"db_host": "127.0.0.1"}, {}),
            ({"db_host": "production-db"}, {}),
            ({"db_host": "mariadb", "db_port": 3307}, {}),
            ({}, {"db_host": "mariadb", "db_port": "bogus"}),
            ({}, {}),
            ({"db_host": "mariadb"}, {"db_host": "another"}),
            (None, {}),
        ]
        for isolated, common in invalid:
            with self.subTest(isolated=isolated, common=common):
                with self.assertRaises(GuardBlocked):
                    fn(isolated, common)

    def test_sql_command_denials_and_exact_commit_phase(self):
        scope = {
            "sql_commit_phase": "locked",
            "original_sql": lambda q, *a, **k: q,
            # SQL DML targets are exercised by the separate source-extracted
            # test_material_issue_v2_dml_surface.py suite.
            "review_dml_scope": lambda query: None,
        }
        fn, globals_dict = self.extract("limited_sql", scope)
        self.assertEqual(fn("SELECT 1"), "SELECT 1")
        for query in (
            "COMMIT", "ROLLBACK", "START TRANSACTION", "BEGIN",
            "ALTER TABLE test ADD COLUMN x INT", "DROP TABLE test",
            "CREATE TABLE test (x INT)", "TRUNCATE TABLE test",
            "CALL dangerous()", "LOCK TABLES test WRITE",
            "SET autocommit=1", "SAVEPOINT x",
            "SELECT 1; COMMIT", "/* hi */ COMMIT", "-- comment\nCOMMIT",
            "WITH x AS (SELECT 1) DELETE FROM test",
        ):
            with self.subTest(query=query):
                with self.assertRaises(GuardBlocked):
                    fn(query)
        with self.assertRaises(GuardBlocked):
            fn("SELECT 1", auto_commit=True)
        globals_dict["sql_commit_phase"] = "one_commit"
        self.assertEqual(fn("COMMIT"), "COMMIT")
        self.assertEqual(globals_dict["sql_commit_phase"], "committed_sql")
        with self.assertRaises(GuardBlocked):
            fn("COMMIT")
        self.assertEqual(fn("START TRANSACTION"), "START TRANSACTION")
        self.assertEqual(globals_dict["sql_commit_phase"], "postcommit_begin")
        with self.assertRaises(GuardBlocked):
            fn("COMMIT")

    def test_realtime_only_synthetic_notifications_suppressed(self):
        fn, _ = self.extract("limited_realtime", {
            "allowed_realtime_doctypes": {
                "Withdrawal Slip", "Stock Entry", "Stock Ledger Entry", "GL Entry"
            },
        })
        self.assertIsNone(fn(event="doc_update", doctype="Withdrawal Slip", after_commit=True))
        self.assertIsNone(fn(event="list_update", message={"doctype": "Stock Entry"},
                             after_commit=True))
        for kwargs in (
            {"event": "doc_update", "doctype": "Purchase Invoice", "after_commit": True},
            {"event": "doc_update", "doctype": "Stock Entry", "after_commit": False},
            {"event": "progress", "doctype": "Stock Entry", "after_commit": True},
            {"event": "list_update", "message": {"doctype": "User"}, "after_commit": True},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(GuardBlocked):
                    fn(**kwargs)

    def test_recovery_metadata_gate_detects_change(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            snapshots = root / "snapshots"
            baseline = root / "base"
            latest = snapshots / "post-verified-withdrawal-slip-pre-material-issue-20261015"
            baseline.mkdir()
            prefix = "20261015_085718-ccpc-integration2_localhost"
            paths = []
            for folder in [baseline] + [snapshots / f"checkpoint-{i}" for i in range(10)] + [latest]:
                folder.mkdir(parents=True, exist_ok=True)
                for suffix in ("-database.sql.gz", "-files.tar", "-private-files.tar",
                               "-site_config_backup.json"):
                    p = folder / (prefix + suffix)
                    p.write_bytes(b"fixture")
                    paths.append(p)
            self.assertEqual(len(paths), 48)
            fn, _ = self.extract("verify_snapshots", {
                "SNAP_ROOT": snapshots, "BASE_BACKUP": baseline, "LATEST": latest,
                "BACKUP_PREFIX": prefix,
                "sha256": lambda p: hashlib.sha256(p.read_bytes()).hexdigest(),
            })
            before = fn(metadata_only=True)
            self.assertEqual(len(before), 48)
            self.assertEqual(len(fn()), 48)
            paths[0].write_bytes(b"modified fixture")
            self.assertNotEqual(before, fn(metadata_only=True))
            paths[0].unlink()
            with self.assertRaises(GuardBlocked):
                fn(metadata_only=True)

    def test_full_backup_hashing_outside_write_transaction(self):
        self.assertLess(self.shell.index("old_backups = verify_snapshots()"),
                        self.shell.index("frappe.db.begin()"))
        before_commit = self.shell.split("original_commit()", 1)[0]
        locked_window = before_commit.split("frappe.db.begin()", 1)[1]
        self.assertIn("verify_snapshots(metadata_only=True)", locked_window)
        self.assertNotIn("verify_snapshots() != old_backups", locked_window)


if __name__ == "__main__":
    unittest.main()
