"""Offline mock-only regression tests for proposed original-lab firewall guard.

No Docker daemon, iptables, UFW, network access, credentials or root required.
"""
import contextlib
import importlib.util
import io
import sys
from pathlib import Path
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SECURITY_DIR = REPO / "scripts/security"
if str(SECURITY_DIR) not in sys.path:
    sys.path.insert(0, str(SECURITY_DIR))
GUARD_FILE = REPO / "scripts/security/ccpc_codex_lab_firewall_guard.py"
UNIT_FILE = (REPO / "scripts/security/systemd" /
             "ccpc-codex-lab-firewall-restore.service.example")

spec = importlib.util.spec_from_file_location(
    "ccpc_codex_lab_firewall_guard_test", GUARD_FILE
)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def appended(specs, name):
    chain, tokens = specs[name]
    return ["-A", chain, *tokens]


class TestOriginalLabFirewallGuard(unittest.TestCase):
    def setUp(self):
        self.specs = guard.rule_specs("br-test", "172.21.0.0/16")
        self.host = appended(self.specs, "host")
        self.out = appended(self.specs, "out")
        self.inbound = appended(self.specs, "in")
        self.forward = ["-A", "FORWARD", "-j", "DOCKER-USER"]

    def test_all_specs_are_drop_rules_scoped_to_original_bridge(self):
        self.assertEqual(set(self.specs), {"host", "out", "in"})
        for chain, tokens in self.specs.values():
            self.assertIn(chain, ("INPUT", "DOCKER-USER"))
            self.assertEqual(tokens[-2:], ["-j", "DROP"])
            self.assertIn("br-test", tokens)

    def test_reordered_iptables_modules_are_treated_equivalently(self):
        reordered = [
            "-A", "INPUT",
            "-m", "comment", "-j", "DROP", "-i", "br-test",
            "--comment", "ccpc-codex-deny-host",
            "-s", "172.21.0.0/16",
        ]
        self.assertEqual(
            guard.canonical_rule(reordered, "INPUT"),
            guard.canonical_rule(self.host, "INPUT"),
        )

    def test_extra_allow_or_unknown_match_fails_closed(self):
        candidate = self.host + ["-m", "state"]
        self.assertIsNone(guard.canonical_rule(candidate, "INPUT"))
        self.assertNotEqual(
            guard.canonical_rule(["-A", "INPUT", "-j", "ACCEPT"], "INPUT"),
            guard.canonical_rule(self.host, "INPUT"),
        )

    def test_normalized_first_rule_order_is_required(self):
        self.assertTrue(guard.precedence_valid(
            self.specs, [self.host], [self.out, self.inbound], [self.forward]
        ))
        self.assertTrue(guard.precedence_valid(
            self.specs, [self.host], [self.inbound, self.out], [self.forward]
        ))
        self.assertFalse(guard.precedence_valid(
            self.specs, [["-A", "INPUT", "-j", "ACCEPT"], self.host],
            [self.out, self.inbound], [self.forward],
        ))
        self.assertFalse(guard.precedence_valid(
            self.specs, [self.host],
            [["-A", "DOCKER-USER", "-j", "ACCEPT"], self.out, self.inbound],
            [self.forward],
        ))

    def test_both_bridges_can_coexist_in_restrictive_prefixes(self):
        proxy = guard.proxy_rule_specs()
        p_host = appended(proxy, "host")
        p_out = appended(proxy, "outbound")
        p_in = appended(proxy, "inbound")
        self.assertTrue(guard.precedence_valid(
            self.specs,
            [p_host, self.host],
            [p_out, self.out, p_in, self.inbound],
            [self.forward],
        ))
        self.assertTrue(guard.precedence_valid(
            self.specs,
            [self.host, p_host],
            [self.out, self.inbound, p_in, p_out],
            [self.forward],
        ))

    def test_partial_second_bridge_firewall_fails_closed(self):
        proxy = guard.proxy_rule_specs()
        self.assertFalse(guard.precedence_valid(
            self.specs,
            [appended(proxy, "host"), self.host],
            [self.out, self.inbound],
            [self.forward],
        ))

    def test_second_bridge_rules_after_accept_fail_closed(self):
        proxy = guard.proxy_rule_specs()
        self.assertFalse(guard.precedence_valid(
            self.specs,
            [self.host, ["-A", "INPUT", "-j", "ACCEPT"],
             appended(proxy, "host")],
            [self.out, self.inbound,
             appended(proxy, "outbound"), appended(proxy, "inbound")],
            [self.forward],
        ))

    def test_missing_original_bridge_rule_in_joint_mode_fails_closed(self):
        proxy = guard.proxy_rule_specs()
        self.assertFalse(guard.precedence_valid(
            self.specs,
            [appended(proxy, "host")],
            [appended(proxy, "outbound"), appended(proxy, "inbound")],
            [self.forward],
        ))

    def test_alternate_inverted_interface_syntax_is_normalized(self):
        legacy = ["-A", "DOCKER-USER",
                  "-i", "br-test", "-o", "!", "br-test",
                  "-m", "comment", "--comment",
                  "ccpc-codex-deny-outbound", "-j", "DROP"]
        self.assertEqual(
            guard.canonical_rule(legacy, "DOCKER-USER"),
            guard.canonical_rule(self.out, "DOCKER-USER"),
        )

    def test_wrong_forward_jump_fails_closed(self):
        self.assertFalse(guard.precedence_valid(
            self.specs, [self.host], [self.out, self.inbound],
            [["-A", "FORWARD", "-j", "ACCEPT"], self.forward],
        ))

    def test_no_apply_rollback_or_start_mode(self):
        for unsafe in ("apply", "rollback", "start", "restart", "up"):
            with mock.patch.object(
                guard, "inspect_host",
                side_effect=AssertionError("must not inspect host"),
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(guard.main([unsafe]), 2)

    def test_preflight_does_not_claim_rules_or_authorize_launch(self):
        output = io.StringIO()
        with mock.patch.object(guard, "inspect_host", return_value=self.specs):
            with mock.patch.object(
                guard, "check_current_rules",
                side_effect=AssertionError("preflight must not call verifier"),
            ):
                with contextlib.redirect_stdout(output):
                    result = guard.main(["preflight"])
        self.assertEqual(result, 0)
        self.assertIn("original_three_rules_and_precedence_verified=False",
                      output.getvalue())
        self.assertIn("agent_launch_authorized=False", output.getvalue())

    def test_missing_rule_fails_closed(self):
        with mock.patch.object(guard, "inspect_host", return_value=self.specs):
            with mock.patch.object(
                guard, "check_current_rules", side_effect=guard.GuardFailure()
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(guard.main(["verify"]), 1)

    def test_verify_success_still_does_not_authorize_launch(self):
        output = io.StringIO()
        with mock.patch.object(guard, "inspect_host", return_value=self.specs):
            with mock.patch.object(guard, "check_current_rules", return_value=True):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(guard.main(["verify"]), 0)
        self.assertIn("original_three_rules_and_precedence_verified=True",
                      output.getvalue())
        self.assertIn("agent_launch_authorized=False", output.getvalue())
        self.assertIn("firewall_reboot_persistence_verified=False",
                      output.getvalue())

    def test_systemd_sample_is_inert_firewall_only(self):
        text = UNIT_FILE.read_text(encoding="utf-8")
        self.assertIn("AssertPathExists=/etc/ccpc/", text)
        self.assertIn("Requires=docker.service", text)
        self.assertIn("After=docker.service ufw.service", text)
        self.assertIn("ccpc_codex_lab_firewall_guard.py preflight", text)
        self.assertIn("ccpc_codex_dev_lab_firewall.sh apply", text)
        self.assertIn("ccpc_codex_lab_firewall_guard.py verify", text)
        self.assertNotIn("\nExecStop=", text)
        self.assertNotIn("\nExecStart=/usr/bin/docker", text)
        self.assertNotIn("\nExecStart=/usr/bin/codex", text)


if __name__ == "__main__":
    unittest.main()
