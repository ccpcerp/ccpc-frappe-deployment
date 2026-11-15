"""Mock-only DEVELOPMENT boundary audit tests: no Docker or host access."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest import mock

SOURCE = (Path(__file__).resolve().parents[1] / "scripts" / "development" /
          "operator" / "ccpc_dev_execution_boundary_readonly.py")
spec = importlib.util.spec_from_file_location("dev_boundary", SOURCE)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class FakeDocker:
    def __init__(self):
        self.old_states = {name: ("running" if name in a.OLD_RETAINED_DATA else "exited")
                           for name in a.OLD_EXPECTED}
        self.running = "true"
        self.privileged = "false"
        self.project = a.DEV_PROJECT
        self.mounts = []
        self.calls = []

    def __call__(self, *args):
        self.calls.append(args)
        if args[0] == "ps":
            return "\n".join(f"{name} {state}" for name, state in sorted(self.old_states.items()))
        if args[:2] == ("container", "inspect"):
            key = args[3]
            if key == '{{index .Config.Labels "com.docker.compose.project"}}':
                return self.project
            if key == "{{.State.Running}}":
                return self.running
            if key == "{{.HostConfig.Privileged}}":
                return self.privileged
            if key == "{{json .Mounts}}":
                return json.dumps(self.mounts)
        raise AssertionError("unexpected Docker operation")

    def add_mount(self, source, dest):
        self.mounts.append({"Source": source, "Destination": dest,
                            "Type": "bind", "RW": True})


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeDocker()

    def run_preflight(self):
        with mock.patch.object(a, "operator_guard"), \
             mock.patch.object(a, "docker", side_effect=self.fake), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            result = a.main()
        return result, out.getvalue()

    def test_clean_boundary(self):
        result, out = self.run_preflight()
        self.assertEqual(result, 0)
        self.assertIn("CCPC_DEV_EXECUTION_BOUNDARY_PREFLIGHT_PASS", out)
        self.assertIn("OLD_PRODUCTION_APP_ACTIVE=0", out)
        self.assertIn("OLD_PRODUCTION_RETAINED_DATA_ACTIVE=3", out)
        self.assertEqual(len(self.fake.calls), 5)
        self.assertTrue(all(cmd[0] in ("ps", "container") for cmd in self.fake.calls))

    def test_active_old_production_blocks(self):
        self.fake.old_states["frappe_docker-backend-1"] = "running"
        result, out = self.run_preflight()
        self.assertEqual(result, 1)
        self.assertIn("OLD_PRODUCTION_APP_ACTIVE=1", out)
        self.assertIn("STOP_REVIEW_REQUIRED", out)

    def test_retained_old_data_does_not_block_if_app_services_exited(self):
        result, out = self.run_preflight()
        self.assertEqual(result, 0)
        self.assertIn("OLD_PRODUCTION_RETAINED_DATA_ACTIVE=3", out)

    def test_old_scheduler_restart_blocks(self):
        self.fake.old_states["frappe_docker-scheduler-1"] = "restarting"
        result, out = self.run_preflight()
        self.assertEqual(result, 1)
        self.assertIn("OLD_PRODUCTION_APP_ACTIVE=1", out)

    def test_unknown_old_service_blocks_before_printing_names(self):
        self.fake.old_states["frappe_docker-unexpected-1"] = "running"
        result, out = self.run_preflight()
        self.assertEqual(result, 1)
        self.assertEqual(out.strip(), "CCPC_DEV_EXECUTION_BOUNDARY_STOP_REVIEW_REQUIRED")
        self.assertNotIn("unexpected", out)

    def test_missing_old_service_blocks(self):
        self.fake.old_states.pop("frappe_docker-backend-1")
        result, out = self.run_preflight()
        self.assertEqual(result, 1)
        self.assertEqual(out.strip(), "CCPC_DEV_EXECUTION_BOUNDARY_STOP_REVIEW_REQUIRED")

    def test_ssh_mount_blocks_without_printing_source(self):
        self.fake.add_mount("/home/gani/.ssh", "/home/frappe/.ssh")
        result, out = self.run_preflight()
        self.assertEqual(result, 1)
        self.assertIn("DEV_CREDENTIAL_MOUNT_DETECTED=YES", out)
        self.assertNotIn("/home/gani/.ssh", out)

    def test_docker_socket_blocks(self):
        self.fake.add_mount("/var/run/docker.sock", "/var/run/docker.sock")
        result, out = self.run_preflight()
        self.assertEqual(result, 1)
        self.assertIn("DEV_DOCKER_SOCKET_MOUNT_DETECTED=YES", out)

    def test_privileged_dev_blocks(self):
        self.fake.privileged = "true"
        result, out = self.run_preflight()
        self.assertEqual(result, 1)
        self.assertIn("DEV_PRIVILEGED=YES", out)

    def test_stopped_dev_blocks(self):
        self.fake.running = "false"
        result, out = self.run_preflight()
        self.assertEqual(result, 1)
        self.assertIn("DEV_CONTAINER_RUNNING=NO", out)

    def test_wrong_project_blocks(self):
        self.fake.project = "frappe_docker"
        result, out = self.run_preflight()
        self.assertEqual(result, 1)
        self.assertEqual(out.strip(), "CCPC_DEV_EXECUTION_BOUNDARY_STOP_REVIEW_REQUIRED")

    def test_failed_docker_call_redacts(self):
        def bad(*args):
            raise a.Stop()
        with mock.patch.object(a, "operator_guard"), \
             mock.patch.object(a, "docker", side_effect=bad), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(a.main(), 1)
        self.assertEqual(out.getvalue().strip(),
                         "CCPC_DEV_EXECUTION_BOUNDARY_STOP_REVIEW_REQUIRED")

    def test_operator_rejects_wrong_host(self):
        with mock.patch.object(a.os, "geteuid", return_value=0), \
             mock.patch.dict(a.os.environ, {"SUDO_USER": "gani"}, clear=True), \
             mock.patch.object(a.socket, "gethostname", return_value="ccpcerp-prod"):
            with self.assertRaises(a.Stop):
                a.operator_guard()

    def test_unsafe_env_rejected(self):
        with mock.patch.object(a.os, "geteuid", return_value=0), \
             mock.patch.dict(a.os.environ, {
                 "SUDO_USER": "gani", "DOCKER_HOST": "tcp://remote:2375"}, clear=True), \
             mock.patch.object(a.socket, "gethostname", return_value=a.HOST):
            with self.assertRaises(a.Stop):
                a.operator_guard()

    def test_no_mutation_operations_in_source(self):
        code = SOURCE.read_text()
        for forbidden in ('docker("update"', 'docker("start"', 'docker("stop"',
                          'docker("run"', 'docker("exec"', 'subprocess.Popen',
                          'shell=True'):
            self.assertNotIn(forbidden, code)


if __name__ == "__main__":
    unittest.main()
