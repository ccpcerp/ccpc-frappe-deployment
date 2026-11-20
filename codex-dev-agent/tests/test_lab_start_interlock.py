"""Mock-only Codex offline startup gate validation. No Docker or server calls."""
import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest import mock

SECURITY = Path(__file__).resolve().parents[2] / "scripts/security"
sys.path.insert(0, str(SECURITY))
import ccpc_codex_lab_firewall_guard as guard

spec = importlib.util.spec_from_file_location(
    "ccpc_codex_lab_interlock_test",
    SECURITY / "ccpc_codex_lab_start_interlock.py",
)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def secure():
    agent = {
        "State": {"Running": False},
        "Config": {
            "Image": "frappe/bench@sha256:" + "a" * 64,
            "User": "1000:1000",
            "Labels": {
                "com.docker.compose.project": "ccpc_codex_dev_agent",
                "com.docker.compose.service": "agent",
            },
        },
        "HostConfig": {
            "Privileged": False,
            "ReadonlyRootfs": True,
            "CapDrop": ["ALL"],
            "SecurityOpt": ["no-new-privileges:true"],
            "Memory": 8 * 1024**3,
            "MemorySwap": 8 * 1024**3,
            "PidsLimit": 512,
            "RestartPolicy": {"Name": "no"},
            "NetworkMode": "ccpc_codex_dev_agent_lab",
        },
        "NetworkSettings": {"Networks": {"ccpc_codex_dev_agent_lab": {}}},
        "Mounts": [
            {"Type": "volume", "Destination": "/home/frappe"},
            {"Type": "volume", "Destination": "/home/frappe/.cache"},
        ],
    }
    lab = {
        "Name": "ccpc_codex_dev_agent_lab",
        "Driver": "bridge",
        "Internal": True,
        "Attachable": False,
        "EnableIPv6": False,
    }
    return agent, lab


class TestOfflineCodexStartGate(unittest.TestCase):
    def setUp(self):
        self.agent, self.lab = secure()

    def validated(self):
        return gate.validate_agent_runtime(self.agent, self.lab)

    def rejected(self):
        with self.assertRaises(gate.GateFailure):
            self.validated()

    def test_restricted_pinned_baseline(self):
        self.assertTrue(self.validated())

    def test_mutable_tag_denied(self):
        self.agent["Config"]["Image"] = "frappe/bench:latest"
        self.rejected()

    def test_running_agent_denied(self):
        self.agent["State"]["Running"] = True
        self.rejected()

    def test_auto_restart_denied(self):
        self.agent["HostConfig"]["RestartPolicy"]["Name"] = "always"
        self.rejected()

    def test_root_agent_denied(self):
        self.agent["Config"]["User"] = "root"
        self.rejected()

    def test_privileged_agent_denied(self):
        self.agent["HostConfig"]["Privileged"] = True
        self.rejected()

    def test_writable_root_denied(self):
        self.agent["HostConfig"]["ReadonlyRootfs"] = False
        self.rejected()

    def test_missing_memory_limit_denied(self):
        self.agent["HostConfig"]["Memory"] = 0
        self.rejected()

    def test_excess_swap_denied(self):
        self.agent["HostConfig"]["MemorySwap"] *= 2
        self.rejected()

    def test_pid_limit_drift_denied(self):
        self.agent["HostConfig"]["PidsLimit"] = 0
        self.rejected()

    def test_external_bridge_denied(self):
        self.agent["NetworkSettings"]["Networks"]["public_bridge"] = {}
        self.rejected()

    def test_docker_socket_mount_denied(self):
        self.agent["Mounts"].append({
            "Type": "bind", "Destination": "/var/run/docker.sock"
        })
        self.rejected()

    def test_host_bind_denied(self):
        self.agent["HostConfig"]["Binds"] = ["/host:/home/frappe:rw"]
        self.rejected()

    def test_published_port_denied(self):
        self.agent["HostConfig"]["PortBindings"] = {"22/tcp": [{"HostPort": "22"}]}
        self.rejected()

    def test_wrong_lab_identity_denied(self):
        self.lab["Internal"] = False
        self.rejected()

    def test_missing_cap_drop_denied(self):
        self.agent["HostConfig"]["CapDrop"] = []
        self.rejected()

    def test_no_start_or_apply_mode(self):
        with mock.patch.object(gate, "verify", side_effect=AssertionError):
            for mode in ("start", "up", "monitor", "apply", "restore"):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(gate.main([mode]), 2)

    def test_missing_marker_stops_before_host_inspection(self):
        with mock.patch.object(
            gate, "authorization_required", side_effect=gate.GateFailure()
        ):
            with mock.patch.object(guard, "inspect_host", side_effect=AssertionError):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(gate.main(["verify"]), 1)

    def test_verify_success_does_not_authorize_launch(self):
        out = io.StringIO()
        with mock.patch.object(gate, "verify", return_value=True):
            with contextlib.redirect_stdout(out):
                self.assertEqual(gate.main(["verify"]), 0)
        self.assertIn("agent_launch_authorized=False", out.getvalue())

    def test_source_never_starts_or_stops_containers(self):
        source = (SECURITY / "ccpc_codex_lab_start_interlock.py").read_text()
        self.assertNotIn('["docker", "start"', source)
        self.assertNotIn('["docker", "stop"', source)


if __name__ == "__main__":
    unittest.main()
