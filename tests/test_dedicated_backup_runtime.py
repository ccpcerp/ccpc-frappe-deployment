"""No Docker daemon, NAS, secrets or production host: synthetic inspection only."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts import dedicated_backup_runtime as runtime


class RuntimeVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sites = self.root / "sites"
        self.database = self.root / "database"
        self.sites.mkdir()
        self.database.mkdir()
        (self.sites / runtime.EXPECTED_SITE).mkdir()
        (self.sites / runtime.EXPECTED_SITE / "site_config.json").write_text('{"a":"synthetic"}')
        self.name = "ccpc-dedicated"
        self.ids = ["a" * 64, "b" * 64, "c" * 64]
        self.img_backend = "sha256:" + "d" * 64
        self.img_db = "sha256:" + "e" * 64
        self.hash_backend = "1" * 64
        self.hash_db = "2" * 64
        self.expected = runtime.ApprovedRuntime(
            self.name, self.img_backend, self.img_db, self.hash_backend,
            self.hash_db, self.name + "_sites", self.name + "_db-data"
        )
        self.containers = {}
        for ident, svc, img, h in (
            (self.ids[0], "backend", self.img_backend, self.hash_backend),
            (self.ids[1], "db", self.img_db, self.hash_db),
            (self.ids[2], "scheduler", self.img_backend, "3" * 64),
        ):
            mounts = [{"Type": "volume", "Name": self.name + ("_db-data" if svc == "db" else "_sites"),
                       "Destination": runtime.DB_DESTINATION if svc == "db" else runtime.SITE_DESTINATION,
                       "Source": str(self.database if svc == "db" else self.sites), "RW": True}]
            self.containers[ident] = {
                "Id": ident, "Image": img, "Config": {"Labels": {
                    "com.docker.compose.project": self.name, "com.docker.compose.service": svc,
                    "com.docker.compose.config-hash": h}, "Env": ["PASSWORD=TEST_SECRET_DO_NOT_LOG"]},
                "State": {"Running": True, "Paused": False, "Restarting": False,
                          "Health": {"Status": "healthy"} if svc == "db" else None},
                "HostConfig": {"Privileged": False, "NetworkMode": self.name + "_default", "PidMode": ""},
                "Mounts": mounts,
            }
        self.images = {
            self.img_backend: {"Id": self.img_backend, "Config": {"Labels": {
                "org.ccpc.frappe.sha": runtime.EXPECTED_FRAPPE_SHA}}},
            self.img_db: {"Id": self.img_db, "Config": {"Labels": {}}},
        }
        self.volumes = {
            self.expected.sites_volume: {"Name": self.expected.sites_volume, "Mountpoint": str(self.sites),
                                         "Labels": {"com.docker.compose.project": self.name, "com.docker.compose.volume": "sites"}},
            self.expected.db_volume: {"Name": self.expected.db_volume, "Mountpoint": str(self.database),
                                      "Labels": {"com.docker.compose.project": self.name, "com.docker.compose.volume": "db-data"}},
        }
        self.calls = []

    def query(self, argv):
        self.calls.append(tuple(argv))
        if argv[:3] == ["docker", "container", "ls"]:
            return "\n".join(self.ids) + "\n"
        if argv[:3] == ["docker", "container", "inspect"]:
            return json.dumps([self.containers[argv[3]]])
        if argv[:3] == ["docker", "image", "inspect"]:
            return json.dumps([self.images[argv[3]]])
        if argv[:3] == ["docker", "volume", "inspect"]:
            return json.dumps([self.volumes[argv[3]]])
        raise AssertionError("Unexpected Docker operation")

    def verify(self):
        return runtime.verify_runtime(self.expected, self.query, hostname=lambda: runtime.EXPECTED_HOST)

    def reject(self):
        with self.assertRaises(runtime.RuntimeRejected):
            self.verify()

    def test_success_checks_read_only_inventory_and_keeps_backup_gates_closed(self):
        e = self.verify()
        self.assertEqual(e.host, runtime.EXPECTED_HOST)
        self.assertEqual(e.frappe_sha, runtime.EXPECTED_FRAPPE_SHA)
        self.assertTrue(e.site_volume_verified)
        self.assertTrue(e.database_volume_verified)
        self.assertFalse(e.backup_ready)
        self.assertFalse(e.writes_quiesced or e.no_partial_backup_filters or e.encryption_disabled)
        self.assertEqual(len(self.calls), 8)
        self.assertTrue(all(c[:3] in (("docker", "container", "ls"),
                                           ("docker", "container", "inspect"),
                                           ("docker", "image", "inspect"),
                                           ("docker", "volume", "inspect")) for c in self.calls))

    def test_host_mismatch_rejected_before_docker(self):
        with self.assertRaises(runtime.RuntimeRejected):
            runtime.verify_runtime(self.expected, self.query, hostname=lambda: "ccpcerpserver")
        self.assertEqual(self.calls, [])

    def test_unapproved_expected_release_ids_rejected(self):
        for bad in ("mariadb:11.8", "sha256:zz", "sha256:" + "F" * 64):
            bad_exp = runtime.ApprovedRuntime(self.name, bad, self.img_db,
                                              self.hash_backend, self.hash_db,
                                              self.expected.sites_volume, self.expected.db_volume)
            with self.assertRaises(runtime.RuntimeRejected):
                runtime.verify_runtime(bad_exp, self.query, hostname=lambda: runtime.EXPECTED_HOST)
        self.assertEqual(self.calls, [])

    def test_reject_unsafe_project_and_volume_names(self):
        for project in ("prod/unsafe", "", "CCPC", "x" * 65):
            bad = runtime.ApprovedRuntime(project, self.img_backend, self.img_db,
                                           self.hash_backend, self.hash_db,
                                           self.expected.sites_volume, self.expected.db_volume)
            with self.assertRaises(runtime.RuntimeRejected):
                runtime.verify_runtime(bad, self.query, hostname=lambda: runtime.EXPECTED_HOST)
        self.expected = runtime.ApprovedRuntime(self.name, self.img_backend, self.img_db,
                                                 self.hash_backend, self.hash_db, "oldprod_sites",
                                                 self.expected.db_volume)
        self.reject()

    def test_missing_docker_containers_rejected(self):
        self.ids = [self.ids[0]]
        self.reject()

    def test_truncated_docker_ps_ids_resolve_to_full_inspect_ids(self):
        self.ids = [i[:12] for i in self.ids]
        original = self.query
        def abbreviated_query(argv):
            if argv[:3] == ["docker", "container", "inspect"]:
                return json.dumps([self.containers[argv[3].ljust(64, argv[3][0])]])
            return original(argv)
        observed = runtime.verify_runtime(self.expected, abbreviated_query,
                                          hostname=lambda: runtime.EXPECTED_HOST)
        self.assertFalse(observed.backup_ready)

    def test_duplicate_container_id_rejected(self):
        self.ids.append(self.ids[0])
        self.reject()

    def test_duplicate_backend_service_rejected(self):
        self.containers[self.ids[2]]["Config"]["Labels"]["com.docker.compose.service"] = "backend"
        self.reject()

    def test_critical_service_missing_rejected(self):
        self.containers[self.ids[1]]["Config"]["Labels"]["com.docker.compose.service"] = "queue-long"
        self.reject()

    def test_changed_compose_project_label_rejected(self):
        self.containers[self.ids[0]]["Config"]["Labels"]["com.docker.compose.project"] = "legacy-prod"
        self.reject()

    def test_changed_compose_hash_rejected(self):
        self.containers[self.ids[1]]["Config"]["Labels"]["com.docker.compose.config-hash"] = "9" * 64
        self.reject()

    def test_different_image_id_rejected(self):
        self.containers[self.ids[0]]["Image"] = self.img_db
        self.reject()

    def test_backend_provenance_label_missing_rejected(self):
        self.images[self.img_backend]["Config"]["Labels"].pop("org.ccpc.frappe.sha")
        self.reject()

    def test_db_health_must_be_healthy(self):
        self.containers[self.ids[1]]["State"]["Health"]["Status"] = "starting"
        self.reject()

    def test_backend_stopped_rejected(self):
        self.containers[self.ids[0]]["State"]["Running"] = False
        self.reject()

    def test_privileged_container_rejected(self):
        self.containers[self.ids[0]]["HostConfig"]["Privileged"] = True
        self.reject()

    def test_wrong_named_volume_rejected(self):
        self.containers[self.ids[1]]["Mounts"][0]["Name"] = "oldprod_db-data"
        self.reject()

    def test_bind_mount_or_extra_mount_rejected(self):
        self.containers[self.ids[0]]["Mounts"][0]["Type"] = "bind"
        self.reject()
        self.containers[self.ids[0]]["Mounts"][0]["Type"] = "volume"
        self.containers[self.ids[0]]["Mounts"].append({"Type": "bind", "Destination": "/var/run/docker.sock"})
        self.reject()

    def test_volume_provenance_rejected(self):
        self.volumes[self.expected.sites_volume]["Labels"]["com.docker.compose.project"] = "legacy"
        self.reject()

    def test_missing_site_config_rejected(self):
        (self.sites / runtime.EXPECTED_SITE / "site_config.json").unlink()
        self.reject()

    def test_symlinked_site_rejected(self):
        site = self.sites / runtime.EXPECTED_SITE
        moved = self.root / "moved-site"
        site.rename(moved)
        site.symlink_to(moved, target_is_directory=True)
        self.reject()

    def test_symlinked_config_rejected(self):
        f = self.sites / runtime.EXPECTED_SITE / "site_config.json"
        f.unlink()
        f.symlink_to("/etc/hosts")
        self.reject()

    def test_symlinked_volume_parent_rejected(self):
        real = self.root.with_name(self.root.name + "-real")
        self.root.rename(real)
        self.root.symlink_to(real, target_is_directory=True)
        try:
            self.reject()
        finally:
            self.root.unlink()
            real.rename(self.root)

    def test_json_injection_or_oversized_response_rejected(self):
        orig = self.query
        def bad(argv):
            if argv[:3] == ["docker", "volume", "inspect"]:
                return json.dumps([self.volumes[argv[3]], self.volumes[argv[3]]])
            return orig(argv)
        with self.assertRaises(runtime.RuntimeRejected):
            runtime.verify_runtime(self.expected, bad, hostname=lambda: runtime.EXPECTED_HOST)
        def oversized(argv):
            return "x" * 1_000_001
        with self.assertRaises(runtime.RuntimeRejected):
            runtime.verify_runtime(self.expected, oversized, hostname=lambda: runtime.EXPECTED_HOST)

    def test_never_echo_password_from_docker_inspect(self):
        self.containers[self.ids[0]]["State"]["Running"] = False
        with self.assertRaises(runtime.RuntimeRejected) as ctx:
            self.verify()
        self.assertNotIn("TEST_SECRET_DO_NOT_LOG", str(ctx.exception))

    def test_docker_transport_blocks_every_mutation(self):
        for argv in (["docker", "container", "exec", "abc"], ["docker", "compose", "up", "-d"],
                     ["docker", "volume", "rm", "fake"], ["docker", "container", "inspect", "abc", "--format", "x"]):
            with self.assertRaises(runtime.RuntimeRejected):
                runtime.docker_readonly_query(argv)

    def test_readonly_transport_mock_accepts_only_expected_query_shapes(self):
        proc = Mock(returncode=0, stdout='[{"Id":"synthetic"}]', stderr='')
        with patch.object(runtime.subprocess, "run", return_value=proc) as call:
            result = runtime.docker_readonly_query(["docker", "image", "inspect", self.img_backend])
            self.assertEqual(result, proc.stdout)
            self.assertEqual(call.call_args.kwargs["timeout"], 8)
            self.assertEqual(call.call_args.args[0][1:3],
                             ["--host", "unix:///var/run/docker.sock"])
            self.assertNotIn("DOCKER_HOST", call.call_args.kwargs["env"])
            self.assertEqual(call.call_args.kwargs["check"], False)
        with patch.object(runtime.subprocess, "run", return_value=proc):
            runtime.docker_readonly_query(["docker", "container", "ls", "--all", "--quiet", "--filter",
                                            "label=com.docker.compose.project=" + self.name])


if __name__ == "__main__":
    unittest.main()
