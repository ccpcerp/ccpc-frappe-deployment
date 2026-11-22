"""Synthetic/offline NEW A3 R0 capture tests. NEVER use actual Docker/systemd."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ccpc_new_a3_boot_r0_readonly as guard
import ccpc_new_a3_boot_r0_manifest_once as capture


def synthetic():
    ids = {n: hashlib.sha256(n.encode()).hexdigest() for n in guard.EXPECTED}
    network_name = "ccpc_prod_erpnext_internal"
    image = capture.EXPECTED_APP_IMAGE
    containers = []
    for name in guard.EXPECTED:
        candidate = name in guard.CANDIDATE
        app = name in [f"{guard.PREFIX}-{r}-1" for r in
                       ("backend", "frontend", "websocket")]
        frontend = name == guard.PREFIX + "-frontend-1"
        is_db = name == guard.PREFIX + "-db-1"
        failed = name == guard.TEST_FAILED
        containers.append({
            "Name": "/" + name,
            "Id": ids[name],
            "Image": image if app else "sha256:" + "a" * 64,
            "State": {"Running": not failed, "ExitCode": 1 if failed else 0,
                      "Health": {"Status": "healthy"} if is_db else None},
            "HostConfig": {"RestartPolicy": {"Name": "no"}, "PortBindings": {}},
            "NetworkSettings": {
                "Networks": {network_name: {
                    "IPAddress": capture.EXPECTED_FRONTEND_IP if frontend else "172.20.0.8"
                }} if candidate else {"protected-network": {"IPAddress": "172.22.0.9"}},
                "Ports": {},
            },
        })
    network = {"Name": network_name, "Id": "b" * 64, "Internal": True,
               "Containers": {ids[n]: {} for n in guard.CANDIDATE}}
    return containers, network


class CaptureSyntheticTests(unittest.TestCase):
    def setUp(self):
        self.containers, self.network = synthetic()

    def capture(self, snapshot_valid=True):
        def fake_docker(*args):
            if args[:3] == ("ps", "-a", "--format"):
                return ("\n".join(o["Name"].lstrip("/") for o in self.containers)
                        + "\n").encode()
            if args[:2] == ("container", "inspect"):
                return json.dumps(self.containers).encode()
            if args[:2] == ("network", "inspect"):
                return json.dumps([self.network]).encode()
            raise AssertionError("Unanticipated Docker call")
        with patch.object(guard, "docker", side_effect=fake_docker), \
             patch.object(guard, "snapshot_live", return_value={"synthetic": True}), \
             patch.object(guard, "evaluate", return_value=snapshot_valid):
            return capture.make_manifest()

    def assert_stops(self):
        with self.assertRaises((guard.Stop, ValueError, KeyError, TypeError)):
            self.capture()

    def test_captures_full_pinned_manifest(self):
        m = self.capture()
        self.assertEqual(set(m["container_ids"]), guard.EXPECTED)
        self.assertEqual(len(set(m["container_ids"].values())), 19)
        self.assertEqual(m["app_image_id"], capture.EXPECTED_APP_IMAGE)
        self.assertEqual(m["frontend_ipv4"], capture.EXPECTED_FRONTEND_IP)
        self.assertEqual(m["network_id"], "b" * 64)

    def test_rejects_extra_container(self):
        self.containers.append(dict(self.containers[0], Name="/unexpected"))
        self.assert_stops()

    def test_rejects_missing_container(self):
        self.containers.pop()
        self.assert_stops()

    def test_rejects_duplicate_id(self):
        self.containers[0]["Id"] = self.containers[1]["Id"]
        self.assert_stops()

    def test_rejects_original_stopped(self):
        next(c for c in self.containers if c["Name"] == "/" + guard.ORIGINAL[0])["State"]["Running"] = False
        self.assert_stops()

    def test_rejects_failed_backend_running(self):
        next(c for c in self.containers if c["Name"] == "/" + guard.TEST_FAILED)["State"]["Running"] = True
        self.assert_stops()

    def test_rejects_candidate_db_unhealthy(self):
        next(c for c in self.containers if c["Name"] ==
             f"/{guard.PREFIX}-db-1")["State"]["Health"]["Status"] = "unhealthy"
        self.assert_stops()

    def test_rejects_wrong_image(self):
        next(c for c in self.containers if c["Name"] ==
             f"/{guard.PREFIX}-backend-1")["Image"] = "sha256:" + "d" * 64
        self.assert_stops()

    def test_rejects_published_port(self):
        next(c for c in self.containers if c["Name"] ==
             f"/{guard.PREFIX}-frontend-1")["HostConfig"]["PortBindings"] = {"80/tcp": [{}]}
        self.assert_stops()

    def test_rejects_wrong_frontend_ip(self):
        next(c for c in self.containers if c["Name"] ==
             f"/{guard.PREFIX}-frontend-1")["NetworkSettings"]["Networks"][
                 self.network["Name"]]["IPAddress"] = "172.20.0.9"
        self.assert_stops()

    def test_rejects_external_network(self):
        self.network["Internal"] = False
        self.assert_stops()

    def test_rejects_extra_network_member(self):
        self.network["Containers"]["c" * 64] = {}
        self.assert_stops()

    def test_rejects_bad_full_r0_validation(self):
        self.assert_stops_when_full_guard_invalid()

    def assert_stops_when_full_guard_invalid(self):
        with self.assertRaises(guard.Stop):
            self.capture(snapshot_valid=False)


class ManifestWriteSyntheticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.dest = self.parent / "once"
        # The parent is controlled by the synthetic fixture; root metadata is
        # mocked to exercise the exact helper validation even on nonroot CI.
        real = Path.lstat
        def root_metadata(path):
            info = real(path)
            return SimpleNamespace(st_uid=0, st_mode=info.st_mode)
        p = patch.object(Path, "lstat", root_metadata)
        p.start()
        self.addCleanup(p.stop)
        self.manifest = {"schema": 1, "synthetic": True}

    def test_one_create_only_and_permissions(self):
        capture.write_once(self.manifest, parent=self.parent, destination=self.dest)
        self.assertEqual(stat.S_IMODE(self.dest.stat().st_mode), 0o700)
        f = self.dest / "manifest.json"
        self.assertEqual(stat.S_IMODE(f.stat().st_mode), 0o600)
        self.assertEqual(json.loads(f.read_text()), self.manifest)
        before = f.read_bytes()
        with self.assertRaises(guard.Stop):
            capture.write_once({"changed": True}, parent=self.parent, destination=self.dest)
        self.assertEqual(f.read_bytes(), before)

    def test_destination_symlink_denied(self):
        outside = self.parent / "protected"
        outside.write_text("keep", encoding="utf-8")
        self.dest.symlink_to(outside)
        with self.assertRaises(guard.Stop):
            capture.write_once(self.manifest, parent=self.parent, destination=self.dest)
        self.assertEqual(outside.read_text(), "keep")

    def test_parent_mismatch_denied(self):
        with self.assertRaises(guard.Stop):
            capture.write_once(self.manifest, parent=self.parent, destination=self.parent / "not" / "once")
        self.assertFalse((self.parent / "not").exists())

    def test_group_writable_parent_denied(self):
        self.parent.chmod(0o770)
        with self.assertRaises(guard.Stop):
            capture.write_once(self.manifest, parent=self.parent, destination=self.dest)
        self.assertFalse(self.dest.exists())


if __name__ == "__main__":
    unittest.main()
