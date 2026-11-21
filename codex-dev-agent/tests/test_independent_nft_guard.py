"""Mocked source-only nft isolation layer policy tests; zero host mutations."""
import contextlib
import copy
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SECURITY = ROOT / "scripts/security"
sys.path.insert(0, str(SECURITY))
import ccpc_codex_lab_firewall_guard as guard

spec = importlib.util.spec_from_file_location(
    "ccpc_nft_guard_review", SECURITY / "ccpc_codex_nft_guard_review.py"
)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

BRIDGE = "br-123456789abc"
TABLE = "ccpc_codex_lab_guard"


def match(field, op, value=BRIDGE):
    return {"match": {"op": op, "left": {"meta": {"key": field}},
                      "right": value}}


def rule(chain, *args):
    return {"rule": {"family": "inet", "table": TABLE, "chain": chain,
                     "expr": [*args, {"drop": None}], "handle": 18}}


def snapshot():
    entries = [
        {"metainfo": {"json_schema_version": 1}},
        {"table": {"family": "inet", "name": TABLE, "handle": 1}},
    ]
    for name, hook in (
        ("host_in", "input"), ("host_out", "output"),
        ("cross_bridge", "forward")
    ):
        entries.append({"chain": {
            "family": "inet", "table": TABLE, "name": name,
            "type": "filter", "hook": hook, "prio": -301,
            "policy": "accept", "handle": 5
        }})
    entries += [
        rule("host_in", match("iifname", "==")),
        rule("host_out", match("oifname", "==")),
        rule("cross_bridge", match("iifname", "=="),
             match("oifname", "!=")),
        rule("cross_bridge", match("oifname", "=="),
             match("iifname", "!=")),
    ]
    return {"nftables": entries}


class TestIndependentNftLayer(unittest.TestCase):
    def setUp(self):
        self.data = snapshot()

    def accepted(self):
        return gate.validate_json_snapshot(self.data, BRIDGE)

    def rejected(self):
        with self.assertRaises(gate.LayerFailure):
            self.accepted()

    def test_exact_independent_deny_layer_accepted(self):
        self.assertTrue(self.accepted())

    def test_render_is_scoped_and_without_global_flush(self):
        txt = gate.render_candidate(BRIDGE)
        self.assertEqual(txt.count(" drop\n"), 4)
        self.assertEqual(txt.count("policy accept;"), 3)
        for hook in ("input", "output", "forward"):
            self.assertIn("hook " + hook + " priority -301", txt)
        self.assertNotIn("flush ruleset", txt)
        self.assertNotIn("delete table", txt)

    def test_renderer_rejects_invalid_bridge(self):
        for name in ("docker0", "br-*", 'br-123"drop', "br-abcdefghijkl"):
            with self.assertRaises(gate.LayerFailure):
                gate.render_candidate(name)

    def test_missing_host_input_rule_denied(self):
        self.data["nftables"].pop(5)
        self.rejected()

    def test_missing_host_output_rule_denied(self):
        self.data["nftables"].pop(6)
        self.rejected()

    def test_missing_cross_bridge_direction_denied(self):
        self.data["nftables"].pop()
        self.rejected()

    def test_wrong_chain_priority_denied(self):
        self.data["nftables"][2]["chain"]["prio"] = 0
        self.rejected()

    def test_wrong_table_family_denied(self):
        self.data["nftables"][1]["table"]["family"] = "ip"
        self.rejected()

    def test_wrong_hook_denied(self):
        self.data["nftables"][4]["chain"]["hook"] = "output"
        self.rejected()

    def test_wildcard_bridge_denied(self):
        self.data["nftables"][5]["rule"]["expr"][0]["match"]["right"] = "br-*"
        self.rejected()

    def test_narrowed_host_deny_denied(self):
        self.data["nftables"][5]["rule"]["expr"].insert(
            1, {"match": {"op": "==",
                          "left": {"payload": {"protocol": "ip", "field": "saddr"}},
                          "right": "172.21.0.0/16"}}
        )
        self.rejected()

    def test_wrong_action_accept_denied(self):
        self.data["nftables"][5]["rule"]["expr"][-1] = {"accept": None}
        self.rejected()

    def test_added_rule_denied(self):
        self.data["nftables"].append(rule("host_in", match("iifname", "==")))
        self.rejected()

    def test_wrong_interface_direction_denied(self):
        self.data["nftables"][7]["rule"]["expr"][0]["match"]["op"] = "!="
        self.rejected()

    def test_malformed_nft_json_denied(self):
        with self.assertRaises(gate.LayerFailure):
            gate.validate_json_snapshot("{", BRIDGE)

    def test_absent_nft_table_denied(self):
        self.data["nftables"] = self.data["nftables"][:1]
        self.rejected()

    def test_plan_is_read_only_and_non_authorizing(self):
        out = io.StringIO()
        with mock.patch.object(gate, "candidate_host", return_value=BRIDGE):
            with mock.patch.object(
                guard, "command", side_effect=AssertionError("no kernel writes")
            ):
                with contextlib.redirect_stdout(out):
                    self.assertEqual(gate.main(["plan"]), 0)
        self.assertIn("agent_launch_authorized=False", out.getvalue())

    def test_reject_all_mutation_modes_before_host_access(self):
        with mock.patch.object(gate, "candidate_host", side_effect=AssertionError):
            for mode in ("apply", "install", "restore", "reload", "start", "stop"):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(gate.main([mode]), 2)

    def test_kernel_verification_requires_exact_snapshot(self):
        with mock.patch.object(gate, "candidate_host", return_value=BRIDGE):
            with mock.patch.object(
                guard, "command", return_value=json.dumps(self.data)
            ) as execute:
                self.assertTrue(gate.verify_kernel())
        execute.assert_called_once_with(
            ["nft", "-j", "list", "table", "inet", TABLE]
        )

    def test_kernel_verification_fails_when_table_missing(self):
        with mock.patch.object(gate, "candidate_host", return_value=BRIDGE):
            with mock.patch.object(
                guard, "command", side_effect=guard.GuardFailure
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(gate.main(["verify"]), 1)


if __name__ == "__main__":
    unittest.main()
