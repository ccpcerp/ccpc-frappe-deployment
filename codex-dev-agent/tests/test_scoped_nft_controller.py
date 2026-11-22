"""Review-only mocked tests: no nftables, host daemon or network writes."""
import contextlib
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
import ccpc_codex_nft_guard_review as nft

spec = importlib.util.spec_from_file_location(
    "ccpc_scoped_nft_controller_test",
    SECURITY / "ccpc_codex_nft_scoped_controller.py",
)
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)
BRIDGE = "br-123456789abc"


def tables(*pairs):
    return json.dumps({"nftables": [
        {"metainfo": {"json_schema_version": 1}},
        *({"table": {"family": family, "name": name}}
          for family, name in pairs),
    ]})


class TestScopedNftController(unittest.TestCase):
    def test_absent_project_table(self):
        with mock.patch.object(control, "command", return_value=tables(("inet", "ufw"))):
            self.assertEqual(control.table_state(), "absent")

    def test_existing_project_table(self):
        with mock.patch.object(
            control, "command",
            return_value=tables(("inet", nft.TABLE))
        ):
            self.assertEqual(control.table_state(), "present")

    def test_foreign_family_collision_refused(self):
        with mock.patch.object(
            control, "command",
            return_value=tables(("ip", nft.TABLE))
        ):
            with self.assertRaises(control.ControllerFailure):
                control.table_state()

    def test_multiple_project_table_names_refused(self):
        with mock.patch.object(
            control, "command",
            return_value=tables(("inet", nft.TABLE), ("ip", nft.TABLE))
        ):
            with self.assertRaises(control.ControllerFailure):
                control.table_state()

    def test_malformed_table_listing_refused(self):
        with mock.patch.object(control, "command", return_value="{"):
            with self.assertRaises(ValueError):
                control.table_state()

    def test_unexpected_non_table_object_refused(self):
        with mock.patch.object(
            control, "command",
            return_value=json.dumps({"nftables": [{"rule": {}}]})
        ):
            with self.assertRaises(control.ControllerFailure):
                control.table_state()

    def test_stock_unit_must_be_inactive_and_disabled(self):
        value = "ActiveState=inactive\nUnitFileState=disabled\n"
        with mock.patch.object(control, "command", return_value=value):
            self.assertTrue(control.stock_service_disabled())

    def test_active_nft_service_refused(self):
        value = "ActiveState=active\nUnitFileState=disabled\n"
        with mock.patch.object(control, "command", return_value=value):
            with self.assertRaises(control.ControllerFailure):
                control.stock_service_disabled()

    def test_enabled_nft_service_refused(self):
        value = "ActiveState=inactive\nUnitFileState=enabled\n"
        with mock.patch.object(control, "command", return_value=value):
            with self.assertRaises(control.ControllerFailure):
                control.stock_service_disabled()

    def test_any_unexpected_stock_service_property_refused(self):
        with mock.patch.object(
            control, "command",
            return_value="ActiveState=inactive\nUnitFileState=disabled\nExtra=1\n"
        ):
            with self.assertRaises(control.ControllerFailure):
                control.stock_service_disabled()

    def test_plan_no_marker_or_mutation(self):
        with mock.patch.object(control, "ready_bridge", return_value=BRIDGE):
            with mock.patch.object(control, "table_state", return_value="absent"):
                with mock.patch.object(
                    control, "authorization_required",
                    side_effect=AssertionError("plan must not authorize")
                ):
                    with mock.patch.object(control, "command",
                                           side_effect=AssertionError("no nft write")):
                        self.assertEqual(control.plan(), "absent")

    def test_plan_rejects_modified_existing_table(self):
        with mock.patch.object(control, "ready_bridge", return_value=BRIDGE):
            with mock.patch.object(control, "table_state", return_value="present"):
                with mock.patch.object(
                    control, "verify_exact",
                    side_effect=control.ControllerFailure()
                ):
                    with self.assertRaises(control.ControllerFailure):
                        control.plan()

    def test_install_missing_authorization_fails_before_host(self):
        with mock.patch.object(
            control, "authorization_required", side_effect=control.ControllerFailure()
        ):
            with mock.patch.object(
                control, "ready_bridge", side_effect=AssertionError("no host")
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(control.main(["install"]), 1)

    def test_install_existing_exact_does_not_modify(self):
        with mock.patch.object(control, "authorization_required"):
            with mock.patch.object(control, "lock_host", return_value=42):
                with mock.patch.object(control.os, "close"):
                    with mock.patch.object(control, "ready_bridge", return_value=BRIDGE):
                        with mock.patch.object(
                            control, "table_state", return_value="present"
                        ):
                            with mock.patch.object(control, "verify_exact") as verify:
                                with mock.patch.object(
                                    control, "command",
                                    side_effect=AssertionError("should not mutate")
                                ):
                                    self.assertEqual(
                                        control.install(), "already-exact"
                                    )
        verify.assert_called_once_with(BRIDGE)

    def test_install_new_table_uses_check_then_single_scoped_transaction(self):
        operations = []
        def call(argv, source=None):
            operations.append((argv, source))
            return ""
        with mock.patch.object(control, "authorization_required"):
            with mock.patch.object(control, "lock_host", return_value=42):
                with mock.patch.object(control.os, "close"):
                    with mock.patch.object(control, "ready_bridge", return_value=BRIDGE):
                        with mock.patch.object(
                            control, "table_state", return_value="absent"
                        ):
                            with mock.patch.object(control, "verify_exact"):
                                with mock.patch.object(
                                    control, "command", side_effect=call
                                ):
                                    self.assertEqual(control.install(), "installed")
        self.assertEqual(
            [x[0] for x in operations],
            [["nft", "--check", "--file", "-"], ["nft", "--file", "-"]]
        )
        self.assertEqual(operations[0][1], operations[1][1])
        self.assertTrue(operations[1][1].startswith("table inet " + nft.TABLE))

    def test_post_install_verification_failure_does_not_flush_or_delete(self):
        operations = []
        def call(argv, source=None):
            operations.append(argv)
            return ""
        with mock.patch.object(control, "authorization_required"):
            with mock.patch.object(control, "lock_host", return_value=42):
                with mock.patch.object(control.os, "close"):
                    with mock.patch.object(control, "ready_bridge", return_value=BRIDGE):
                        with mock.patch.object(control, "table_state", return_value="absent"):
                            with mock.patch.object(control, "verify_exact",
                                                   side_effect=control.ControllerFailure):
                                with mock.patch.object(control, "command",
                                                       side_effect=call):
                                    with self.assertRaises(control.ControllerFailure):
                                        control.install()
        self.assertEqual(len(operations), 2)
        self.assertFalse(any("flush" in " ".join(op) or
                             "delete" in " ".join(op) for op in operations))

    def test_bridge_recreated_before_install_refused(self):
        with mock.patch.object(control, "authorization_required"):
            with mock.patch.object(control, "lock_host", return_value=42):
                with mock.patch.object(control.os, "close"):
                    with mock.patch.object(
                        control, "ready_bridge",
                        side_effect=[BRIDGE, "br-abcdefabcdef"]
                    ):
                        with mock.patch.object(
                            control, "table_state", return_value="absent"
                        ):
                            with mock.patch.object(control, "command") as cmd:
                                with self.assertRaises(control.ControllerFailure):
                                    control.install()
        cmd.assert_called_once_with(
            ["nft", "--check", "--file", "-"], nft.render_candidate(BRIDGE)
        )

    def test_verify_missing_table_fails_closed(self):
        with mock.patch.object(control, "ready_bridge", return_value=BRIDGE):
            with mock.patch.object(control, "table_state", return_value="absent"):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(control.main(["verify"]), 1)

    def test_unsafe_modes_refused_before_host(self):
        with mock.patch.object(
            control, "ready_bridge", side_effect=AssertionError("must not call")
        ):
            for mode in ("start", "stop", "reset", "reload", "flush", "delete"):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(control.main([mode]), 2)

    def test_controller_has_no_stock_service_or_global_flush_commands(self):
        source = (SECURITY / "ccpc_codex_nft_scoped_controller.py").read_text()
        self.assertNotIn('"nft", "flush"', source)
        self.assertNotIn('"nft", "delete"', source)
        self.assertNotIn('"systemctl", "start"', source)
        self.assertNotIn('"systemctl", "reload"', source)
        self.assertNotIn('"docker", "start"', source)

    def test_success_cannot_authorize_codex(self):
        with mock.patch.object(control, "plan", return_value="absent"):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(control.main(["plan"]), 0)
        self.assertIn("agent_launch_authorized=False", out.getvalue())

    def test_unit_template_is_inert_and_scoped(self):
        file = SECURITY / "systemd" / "ccpc-codex-nft-guard.service.example"
        txt = file.read_text()
        self.assertIn("ccpc_codex_nft_scoped_controller.py install", txt)
        self.assertIn("ccpc_codex_nft_scoped_controller.py verify", txt)
        self.assertIn("AssertPathExists=/etc/ccpc/codex-lab-nft-guard-authorized", txt)
        self.assertNotIn("\nExecStop=", txt)
        self.assertNotIn("\n[Install]", txt)
        self.assertNotIn("\nExecStart=/usr/sbin/nft", txt)


if __name__ == "__main__":
    unittest.main()
