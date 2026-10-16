"""Offline negative preflight tests; creates only throwaway synthetic Git repos.

No Frappe import, Docker, network, running checkout, databases, or ERP data.
"""

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest.mock import patch

RUNNER = (
    Path(__file__).resolve().parents[2]
    / "scripts/development/operator/ccpc_withdrawal_sitefree_67_runner_20261016.py"
)
spec = importlib.util.spec_from_file_location("ccpc_sitefree_runner", RUNNER)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class TestSourceBoundary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ccpc-safe-offline-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.run_git("init", "-q")
        self.run_git("config", "user.name", "Synthetic Reviewer")
        self.run_git("config", "user.email", "review@example.invalid")
        self.source = self.root / "ccpcerp/ccpc_erp/withdrawal_slip_stock.py"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("# synthetic fixture; not real CCPC source\n")
        self.run_git("add", ".")
        self.run_git("commit", "-qm", "synthetic fixture")
        self.pin = self.run_git("rev-parse", "HEAD")
        self.pin_patch = patch.object(runner, "FEATURE_SHA", self.pin)
        self.pin_patch.start()
        self.addCleanup(self.pin_patch.stop)
        self.run_git("checkout", "--detach", "-q")

    def run_git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.root), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def test_verified_clean_detached_checkout_passes_preflight(self):
        runner.verify_source(self.root)

    def test_wrong_commit_stops(self):
        with patch.object(runner, "FEATURE_SHA", "0" * 40):
            with self.assertRaises(runner.Stop):
                runner.verify_source(self.root)

    def test_attached_branch_stops(self):
        self.run_git("checkout", "-q", "master" if self.run_git("branch", "--list", "master") else "main")
        with self.assertRaises(runner.Stop):
            runner.verify_source(self.root)

    def test_modified_tracked_file_stops(self):
        self.source.write_text("# changed fixture\n")
        with self.assertRaises(runner.Stop):
            runner.verify_source(self.root)

    def test_untracked_file_stops(self):
        (self.root / "do-not-touch.txt").write_text("synthetic")
        with self.assertRaises(runner.Stop):
            runner.verify_source(self.root)

    def test_symlink_checkout_stops(self):
        alias = Path(self.temp.name) / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(runner.Stop):
            runner.verify_source(alias)

    def test_missing_feature_module_stops_without_import(self):
        self.source.unlink()
        self.run_git("add", "-A")
        self.run_git("commit", "-qm", "drop synthetic feature")
        self.run_git("checkout", "--detach", "-q")
        with patch.object(runner, "FEATURE_SHA", self.run_git("rev-parse", "HEAD")):
            with self.assertRaises(runner.Stop):
                runner.verify_source(self.root)

    def test_failed_source_preflight_cannot_import_frappe(self):
        with patch.object(runner, "FEATURE_SHA", "0" * 40):
            with patch.object(runner, "install_non_site_context") as init:
                with self.assertRaises(runner.Stop):
                    runner.run_tests(self.root)
                init.assert_not_called()


    def test_expected_stock_module_origin_passes(self):
        module = types.ModuleType("ccpcerp.ccpc_erp.withdrawal_slip_stock")
        module.__file__ = str(self.source)
        with patch.dict(runner.sys.modules, {module.__name__: module}):
            runner.verify_loaded_ccpc_modules(self.root)

    def test_module_from_other_checkout_stops(self):
        module = types.ModuleType("ccpcerp.ccpc_erp.withdrawal_slip_stock")
        module.__file__ = str(Path(self.temp.name) / "other/withdrawal_slip_stock.py")
        with patch.dict(runner.sys.modules, {module.__name__: module}):
            with self.assertRaises(runner.Stop):
                runner.verify_loaded_ccpc_modules(self.root)

    def test_wrong_dotted_path_inside_checkout_stops(self):
        module = types.ModuleType("ccpcerp.ccpc_erp.withdrawal_slip_stock")
        module.__file__ = str(self.root / "ccpcerp/wrong_name.py")
        with patch.dict(runner.sys.modules, {module.__name__: module}):
            with self.assertRaises(runner.Stop):
                runner.verify_loaded_ccpc_modules(self.root)

    def test_external_test_module_stops(self):
        module = types.ModuleType(
            "ccpcerp.ccpc_erp.doctype.withdrawal_slip.test_withdrawal_slip"
        )
        module.__file__ = str(Path(self.temp.name) / "external/test_withdrawal_slip.py")
        with patch.dict(runner.sys.modules, {module.__name__: module}):
            with self.assertRaises(runner.Stop):
                runner.verify_loaded_ccpc_modules(self.root)

    def test_namespace_spanning_another_checkout_stops(self):
        module = types.ModuleType("ccpcerp")
        module.__path__ = [
            str(self.root / "ccpcerp"),
            str(Path(self.temp.name) / "external/ccpcerp"),
        ]
        with patch.dict(runner.sys.modules, {module.__name__: module}):
            with self.assertRaises(runner.Stop):
                runner.verify_loaded_ccpc_modules(self.root)

    def test_single_namespace_path_inside_checkout_passes(self):
        module = types.ModuleType("ccpcerp")
        module.__path__ = [str(self.root / "ccpcerp")]
        with patch.dict(runner.sys.modules, {module.__name__: module}):
            runner.verify_loaded_ccpc_modules(self.root)

    def test_unknown_origin_stops(self):
        module = types.ModuleType("ccpcerp.ccpc_erp.synthetic")
        with patch.dict(runner.sys.modules, {module.__name__: module}):
            with self.assertRaises(runner.Stop):
                runner.verify_loaded_ccpc_modules(self.root)

    def test_post_test_source_recheck_on_discovery_failure(self):
        with (
            patch.object(runner, "verify_source") as source,
            patch.object(runner, "verify_loaded_ccpc_modules") as origins,
            patch.object(runner, "install_non_site_context"),
            patch("importlib.import_module"),
            patch.object(
                runner.unittest.defaultTestLoader,
                "loadTestsFromNames",
                side_effect=RuntimeError("synthetic discovery failure"),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "synthetic discovery failure"):
                runner.run_tests(self.root)
            self.assertEqual(source.call_count, 2)
            origins.assert_called_once()



if __name__ == "__main__":
    unittest.main()
