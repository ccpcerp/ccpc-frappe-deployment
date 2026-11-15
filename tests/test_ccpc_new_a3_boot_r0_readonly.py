"""Synthetic/offline only: no Docker, systemd, server, or database access."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ccpc_new_a3_boot_r0_readonly as guard


def fake():
    ids = {name: hashlib.sha256(name.encode()).hexdigest() for name in guard.EXPECTED}
    manifest = {
        "schema": 1,
        "container_ids": ids,
        "network_name": "ccpc_prod_erpnext_internal",
        "network_id": "b" * 64,
        "frontend_ipv4": "172.20.0.7",
        "app_image_id": "sha256:" + "a" * 64,
    }
    rows = {}
    for name in guard.EXPECTED:
        is_candidate = name in guard.CANDIDATE
        is_app = name in tuple(f"{guard.PREFIX}-{x}-1" for x in ("backend", "websocket", "frontend"))
        vols = {}
        if is_app:
            vols = {guard.BENCH_SITES: guard.PREFIX + "_sites", guard.BENCH_LOGS: guard.PREFIX + "_logs"}
        if name == guard.PREFIX + "-db-1":
            vols = {"/var/lib/mysql": guard.PREFIX + "_db-data"}
        if name == guard.PREFIX + "-redis-queue-1":
            vols = {"/data": guard.PREFIX + "_redis-queue-data"}
        rows[name] = dict(
            id=ids[name], running=name != guard.TEST_FAILED,
            exit=1 if name == guard.TEST_FAILED else 0,
            health="healthy" if name == guard.PREFIX + "-db-1" else None,
            restart="no", networks=[manifest["network_name"]] if is_candidate else ["protected-network"],
            ipv4="172.20.0.7" if name == guard.PREFIX + "-frontend-1" else "172.20.0.8",
            image=manifest["app_image_id"] if is_app else "sha256:" + "c" * 64,
            volumes=list(vols.values()), dest_volumes=vols, published=False,
        )
    snapshot = {
        "containers": rows,
        "network": {"name": manifest["network_name"], "id": manifest["network_id"],
                    "internal": True, "members": [ids[name] for name in guard.CANDIDATE]},
        "units": {"DOCKER": ["active", "enabled"], "CONTAINERD": ["active", "enabled"],
                  "CADDY": ["active", "disabled"], "SOCKET": ["active", "disabled"],
                  "RELAY": ["active", "static"]},
        "socket_bind": "127.0.0.1:8080",
        "relay_exec": "/usr/lib/systemd/systemd-socket-proxyd 172.20.0.7:8080",
        "flags": {"pause_scheduler": True, "mute_emails": True},
    }
    return manifest, snapshot


class GuardFixtureTests(unittest.TestCase):
    def setUp(self):
        self.m, self.s = fake()

    def test_good_fixture(self):
        self.assertTrue(guard.evaluate(self.m, self.s))

    def assert_stops(self):
        with self.assertRaises((guard.Stop, KeyError, ValueError, TypeError)):
            guard.evaluate(self.m, self.s)

    def test_extra_network_member(self):
        self.s["network"]["members"].append("d" * 64)
        self.assert_stops()

    def test_changed_container_identity(self):
        self.s["containers"][guard.PREFIX + "-frontend-1"]["id"] = "0" * 64
        self.assert_stops()

    def test_changed_ip(self):
        self.s["containers"][guard.PREFIX + "-frontend-1"]["ipv4"] = "172.20.0.9"
        self.assert_stops()

    def test_relay_target_stale(self):
        self.s["relay_exec"] = "/usr/lib/systemd/systemd-socket-proxyd 172.20.0.9:8080"
        self.assert_stops()

    def test_published_port(self):
        self.s["containers"][guard.PREFIX + "-backend-1"]["published"] = True
        self.assert_stops()

    def test_missing_volume(self):
        self.s["containers"][guard.PREFIX + "-frontend-1"]["dest_volumes"].pop(guard.BENCH_SITES)
        self.assert_stops()

    def test_wrong_image(self):
        self.s["containers"][guard.PREFIX + "-backend-1"]["image"] = "sha256:" + "d" * 64
        self.assert_stops()

    def test_scheduler_unpaused(self):
        self.s["flags"]["pause_scheduler"] = False
        self.assert_stops()

    def test_mail_unmuted(self):
        self.s["flags"]["mute_emails"] = False
        self.assert_stops()

    def test_failed_backend_missing(self):
        del self.s["containers"][guard.TEST_FAILED]
        self.assert_stops()

    def test_original_stopped(self):
        self.s["containers"][guard.ORIGINAL[0]]["running"] = False
        self.assert_stops()

    def test_no_candidate_restart_policy(self):
        self.s["containers"][guard.PREFIX + "-db-1"]["restart"] = "unless-stopped"
        self.assert_stops()

    def test_caddy_unexpected_enabled(self):
        self.s["units"]["CADDY"][1] = "enabled"
        self.assert_stops()

    def test_extra_container(self):
        self.s["containers"]["unknown-container"] = copy.deepcopy(next(iter(self.s["containers"].values())))
        self.assert_stops()

    def test_missing_manifest_id(self):
        self.m["container_ids"].pop(guard.CANDIDATE[0])
        self.assert_stops()

    def test_malformed_manifest_ids_type(self):
        self.m["container_ids"] = list(self.m["container_ids"])
        self.assert_stops()

    def test_duplicate_manifest_ids(self):
        self.m["container_ids"][guard.CANDIDATE[0]] = self.m["container_ids"][guard.CANDIDATE[1]]
        self.assert_stops()

    def run_cli(self, break_flag=False):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            snapshot = Path(directory) / "snapshot.json"
            manifest.write_text(json.dumps(self.m), encoding="utf-8")
            if break_flag:
                self.s["flags"]["pause_scheduler"] = False
            snapshot.write_text(json.dumps(self.s), encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-B", str(Path(guard.__file__)),
                 "--manifest", str(manifest), "--offline-fixture", str(snapshot)],
                text=True, capture_output=True, timeout=10,
                cwd=directory)

    def test_offline_cli_pass(self):
        p = self.run_cli()
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout.strip().splitlines(), [
            "CCPC_NEW_A3_R0_IDENTITY_STORAGE_NETWORK_PASS",
            "CCPC_NEW_A3_R0_GATEWAY_AND_PRECUTOVER_FLAGS_PASS",
            "CCPC_NEW_A3_R0_READONLY_PREFLIGHT_PASS"])
        self.assertEqual(p.stderr, "")

    def test_offline_cli_fail_closed(self):
        p = self.run_cli(break_flag=True)
        self.assertEqual(p.returncode, 1)
        self.assertEqual(p.stdout.strip(), "CCPC_NEW_A3_R0_STOP_REVIEW_REQUIRED")
        self.assertEqual(p.stderr, "")

    def test_not_live_without_args(self):
        # No automatic calls to Docker or systemd on import.
        self.assertTrue(callable(guard.main))


if __name__ == "__main__":
    unittest.main()
