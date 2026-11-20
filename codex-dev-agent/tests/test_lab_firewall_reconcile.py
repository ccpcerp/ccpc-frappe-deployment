"""Synthetic-only security tests. No Docker/host access or firewall writes."""
import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SECURITY = ROOT / "scripts" / "security"
sys.path.insert(0, str(SECURITY))
import ccpc_codex_lab_firewall_guard as guard

spec = importlib.util.spec_from_file_location(
    "ccpc_lab_firewall_reconcile_test",
    SECURITY / "ccpc_codex_lab_firewall_reconcile.py"
)
reconcile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reconcile)


class TestOriginalLabReconcile(unittest.TestCase):
    def setUp(self):
        self.specs = guard.rule_specs("br-test", "172.21.0.0/16")
        self.input = []
        self.user = []
        self.forward = [["-A", "FORWARD", "-j", "DOCKER-USER"]]

    def rule(self, name):
        chain, args = self.specs[name]
        return ["-A", chain, *args]

    def plan(self):
        return reconcile.planned_insertions(
            self.specs, self.input, self.user, self.forward
        )

    def test_all_missing_can_be_prepended(self):
        self.assertEqual(self.plan(), ["host", "out", "in"])

    def test_all_existing_no_changes(self):
        self.input = [self.rule("host")]
        self.user = [self.rule("in"), self.rule("out")]
        self.assertEqual(self.plan(), [])

    def test_single_missing_original_rule(self):
        self.input = [self.rule("host")]
        self.user = [self.rule("out")]
        self.assertEqual(self.plan(), ["in"])

    def test_refuse_existing_host_rule_below_accept(self):
        self.input = [["-A", "INPUT", "-j", "ACCEPT"], self.rule("host")]
        self.user = [self.rule("out"), self.rule("in")]
        with self.assertRaises(reconcile.ReconcileFailure):
            self.plan()

    def test_refuse_wrong_tagged_rule(self):
        bad = self.rule("host")
        bad[-1] = "ACCEPT"
        self.input = [bad]
        with self.assertRaises(reconcile.ReconcileFailure):
            self.plan()

    def test_refuse_duplicate_tag(self):
        self.input = [self.rule("host"), self.rule("host")]
        with self.assertRaises(reconcile.ReconcileFailure):
            self.plan()

    def test_refuse_tag_in_wrong_chain(self):
        self.user = [self.rule("host")]
        with self.assertRaises(reconcile.ReconcileFailure):
            self.plan()

    def test_refuse_wrong_forward_hook(self):
        self.forward = [["-A", "FORWARD", "-j", "ACCEPT"]]
        with self.assertRaises(reconcile.ReconcileFailure):
            self.plan()

    def test_refuse_unapproved_proxy_bridge_reference(self):
        self.input = [["-A", "INPUT", "-i", "br-ccpc-cdxpx", "-j", "DROP"]]
        with self.assertRaises(reconcile.ReconcileFailure):
            self.plan()

    def test_refuse_apply_rollback_and_start_modes(self):
        with mock.patch.object(reconcile, "restore", side_effect=AssertionError):
            for mode in ("apply", "rollback", "start", "restart", "up"):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(reconcile.main([mode]), 2)

    def test_plan_is_read_only_and_never_authorizes_launch(self):
        with mock.patch.object(reconcile, "preflight", return_value=(self.specs, [])):
            with mock.patch.object(
                reconcile, "authorization_required", side_effect=AssertionError
            ):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    self.assertEqual(reconcile.main(["plan"]), 0)
                self.assertIn("agent_launch_authorized=False", out.getvalue())

    def test_restore_requires_marker_before_lock_and_host(self):
        with mock.patch.object(
            reconcile, "authorization_required",
            side_effect=reconcile.ReconcileFailure()
        ):
            with mock.patch.object(reconcile, "lock_host", side_effect=AssertionError):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(reconcile.main(["restore"]), 1)

    def test_only_missing_rule_is_inserted(self):
        commands = []
        with mock.patch.object(reconcile, "authorization_required"):
            with mock.patch.object(reconcile, "lock_host", return_value=22):
                with mock.patch.object(reconcile.os, "close"):
                    with mock.patch.object(
                        reconcile, "preflight", return_value=(self.specs, ["host"])
                    ):
                        with mock.patch.object(
                            guard, "command", side_effect=lambda argv: commands.append(argv)
                        ):
                            with mock.patch.object(guard, "inspect_host"):
                                with mock.patch.object(guard, "check_current_rules"):
                                    self.assertEqual(reconcile.restore(), 1)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0][3:6], ["-I", "INPUT", "1"])

    def test_partial_failure_undoes_only_new_rule(self):
        commands = []
        def fake_command(argv):
            commands.append(argv)
            if argv[3] == "-I" and argv[4] == "DOCKER-USER":
                raise guard.GuardFailure()
        with mock.patch.object(reconcile, "authorization_required"):
            with mock.patch.object(reconcile, "lock_host", return_value=22):
                with mock.patch.object(reconcile.os, "close"):
                    with mock.patch.object(
                        reconcile, "preflight",
                        return_value=(self.specs, ["host", "out"])
                    ):
                        with mock.patch.object(guard, "command", side_effect=fake_command):
                            with self.assertRaises(guard.GuardFailure):
                                reconcile.restore()
        self.assertEqual([a[3] for a in commands], ["-I", "-I", "-D"])
        self.assertEqual([a[4] for a in commands], ["INPUT", "DOCKER-USER", "INPUT"])

    def test_verify_refuses_missing_rules(self):
        with mock.patch.object(
            reconcile, "preflight", return_value=(self.specs, ["out"])
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(reconcile.main(["verify"]), 1)

    def test_no_codex_or_docker_start_in_source(self):
        source = (SECURITY / "ccpc_codex_lab_firewall_reconcile.py").read_text()
        self.assertNotIn('["docker", "start"', source)
        self.assertNotIn('["docker", "stop"', source)
        self.assertNotIn('["codex"', source)


if __name__ == "__main__":
    unittest.main()
