"""Offline negative preflight tests; creates only throwaway synthetic Git repos.

No Frappe import, Docker, network, running checkout, databases, or ERP data.
"""

import importlib.util
from pathlib import Path
import subprocess
import tempfile
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


if __name__ == "__main__":
    unittest.main()
