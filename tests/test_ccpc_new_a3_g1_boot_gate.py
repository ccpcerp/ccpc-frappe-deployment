"""Synthetic G1 checks: no Docker, NEW host, systemd, or business DB access."""
import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/ccpc_new_a3_g1_boot_gate.py"
UNIT = SCRIPT.with_name("ccpc-new-a3-g1-boot-gate.service")
spec = importlib.util.spec_from_file_location("g1", SCRIPT)
g1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g1)


class MockR0:
    PREFIX = "ccpc_prod_erpnext"
    ROLES = ("db", "redis-cache", "redis-queue", "backend", "websocket", "frontend")
    CANDIDATE = tuple(f"ccpc_prod_erpnext-{role}-1" for role in ("db", "redis-cache", "redis-queue", "backend", "websocket", "frontend"))
    ORIGINAL = tuple(f"{p}-{role}-1" for p in (
        "ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107")
        for role in ("redis-queue", "redis-cache", "db"))
    TEST_PREFIX = "ccpc_a3_restore_drill_20261112"
    TEST_RUNNING = tuple(f"ccpc_a3_restore_drill_20261112-{role}-1" for role in (
        "frontend-completion1", "websocket-completion1", "backend-recovery1",
        "redis-queue", "redis-cache", "db"))
    TEST_FAILED = f"{TEST_PREFIX}-backend-1"
    EXPECTED = set(CANDIDATE + ORIGINAL + TEST_RUNNING + ("ccpc_a3_restore_drill_20261112-backend-1",))
    BENCH_SITES = "/home/frappe/frappe-bench/sites"
    BENCH_LOGS = "/home/frappe/frappe-bench/logs"
    UNITS = {"DOCKER": "docker.service", "CONTAINERD": "containerd.service",
             "CADDY": "caddy.service", "SOCKET": "ccpc-erpnext-upstream.socket",
             "RELAY": "ccpc-erpnext-upstream.service"}

    class Stop(Exception):
        pass

    @staticmethod
    def validate_manifest(m):
        if (set(m["container_ids"]) != MockR0.EXPECTED
                or len(set(m["container_ids"].values())) != len(MockR0.EXPECTED)
                or m.get("schema") != 1):
            raise MockR0.Stop()
        return m


def fixture(profile="postchange"):
    r0 = MockR0
    ids = {k: hashlib.sha256(k.encode()).hexdigest() for k in r0.EXPECTED}
    m = {"schema": 1, "container_ids": ids, "network_name": "ccpc_prod_erpnext_internal",
         "network_id": "b" * 64, "frontend_ipv4": "172.20.0.7",
         "app_image_id": "sha256:" + "a" * 64}
    rows = {}
    for name in r0.EXPECTED:
        candidate = name in r0.CANDIDATE
        app = name in tuple(f"{r0.PREFIX}-{x}-1" for x in ("backend", "websocket", "frontend"))
        vols = {r0.BENCH_SITES: f"{r0.PREFIX}_sites", r0.BENCH_LOGS: f"{r0.PREFIX}_logs"} if app else {}
        if name == f"{r0.PREFIX}-db-1":
            vols = {"/var/lib/mysql": f"{r0.PREFIX}_db-data"}
        if name == f"{r0.PREFIX}-redis-queue-1":
            vols = {"/data": f"{r0.PREFIX}_redis-queue-data"}
        rows[name] = dict(id=ids[name], running=name != r0.TEST_FAILED,
                          health="healthy" if name == f"{r0.PREFIX}-db-1" else None,
                          exit=1 if name == r0.TEST_FAILED else 0,
                          restart=("no" if profile == "prechange" or not candidate else "unless-stopped"),
                          networks=[m["network_name"]] if candidate else ["protected-network"],
                          ipv4="172.20.0.7" if name == f"{r0.PREFIX}-frontend-1" else "172.20.0.8",
                          image=m["app_image_id"] if app else "sha256:" + "c" * 64,
                          volumes=list(vols.values()), dest_volumes=vols, published=False)
    units = {"DOCKER": ["active", "enabled"], "CONTAINERD": ["active", "enabled"],
             "CADDY_API": ["inactive", "masked"],
             "GATE": ["inactive", "disabled"] if profile == "prechange" else ["activating", "enabled"],
             "CADDY": ["active", "disabled"] if profile == "prechange" else ["inactive", "disabled"],
             "SOCKET": ["active", "disabled"] if profile == "prechange" else ["inactive", "disabled"],
             "RELAY": ["active", "static"] if profile == "prechange" else ["inactive", "static"]}
    snap = {"containers": rows, "network": {"name": m["network_name"], "id": m["network_id"],
            "internal": True, "members": list(ids[x] for x in r0.CANDIDATE)},
            "units": units, "socket_bind": "127.0.0.1:8080",
            "relay_exec": "/usr/lib/systemd/systemd-socket-proxyd 172.20.0.7:8080",
            "flags": {"pause_scheduler": True, "mute_emails": True}}
    return m, snap


class G1FixtureTests(unittest.TestCase):
    def setUp(self):
        self.m, self.s = fixture()

    def assert_stop(self):
        with self.assertRaises((g1.Stop, KeyError, ValueError, TypeError, MockR0.Stop)):
            g1.evaluate(MockR0, self.m, self.s, profile="postchange")

    def test_prechange_and_postchange(self):
        self.assertTrue(g1.evaluate(MockR0, self.m, self.s, profile="postchange"))
        m, s = fixture("prechange")
        self.assertTrue(g1.evaluate(MockR0, m, s, profile="prechange", gateway_state="pilot"))
        self.assertTrue(g1.evaluate(MockR0, self.m, self.s, profile="postchange"))

    def test_reject_all_dangerous_drift(self):
        corruptions = {
            "missing identity": lambda s: s["containers"].pop(MockR0.ORIGINAL[0]),
            "extra identity": lambda s: s["containers"].update({"rogue": {}}),
            "candidate replaced": lambda s: s["containers"][MockR0.CANDIDATE[0]].update(id="0" * 64),
            "candidate stopped": lambda s: s["containers"][MockR0.CANDIDATE[0]].update(running=False),
            "drill started": lambda s: s["containers"][MockR0.TEST_FAILED].update(running=True),
            "drill exit changed": lambda s: s["containers"][MockR0.TEST_FAILED].update(exit=0),
            "db unhealthy": lambda s: s["containers"][f"{MockR0.PREFIX}-db-1"].update(health="starting"),
            "noncandidate auto-start": lambda s: s["containers"][MockR0.ORIGINAL[0]].update(restart="always"),
            "partial policy": lambda s: s["containers"][MockR0.CANDIDATE[0]].update(restart="no"),
            "candidate wrong image": lambda s: s["containers"][f"{MockR0.PREFIX}-frontend-1"].update(image="sha256:" + "9" * 64),
            "volume missing": lambda s: s["containers"][f"{MockR0.PREFIX}-backend-1"]["dest_volumes"].pop(MockR0.BENCH_SITES),
            "candidate published": lambda s: s["containers"][MockR0.CANDIDATE[0]].update(published=True),
            "extra net member": lambda s: s["network"]["members"].append("x" * 64),
            "network changed": lambda s: s["network"].update(id="f" * 64),
            "network no longer internal": lambda s: s["network"].update(internal=False),
            "wrong candidate net": lambda s: s["containers"][MockR0.CANDIDATE[0]].update(networks=["other"]),
            "frontend ip changed": lambda s: s["containers"][f"{MockR0.PREFIX}-frontend-1"].update(ipv4="172.20.0.9"),
            "relay drift": lambda s: s.update(relay_exec="/usr/lib/systemd/systemd-socket-proxyd 172.20.0.9:8080"),
            "socket wildcard": lambda s: s.update(socket_bind="0.0.0.0:8080"),
            "scheduler enabled": lambda s: s["flags"].update(pause_scheduler=False),
            "emails enabled": lambda s: s["flags"].update(mute_emails=False),
            "caddy already active": lambda s: s["units"]["CADDY"].__setitem__(0, "active"),
            "socket already active": lambda s: s["units"]["SOCKET"].__setitem__(0, "active"),
            "caddy independently enabled": lambda s: s["units"]["CADDY"].__setitem__(1, "enabled"),
            "socket independently enabled": lambda s: s["units"]["SOCKET"].__setitem__(1, "enabled"),
            "gate disabled": lambda s: s["units"]["GATE"].__setitem__(1, "disabled"),
            "caddy api unmasked": lambda s: s["units"]["CADDY_API"].__setitem__(1, "disabled"),
            "docker off": lambda s: s["units"]["DOCKER"].__setitem__(0, "inactive"),
        }
        for label, corrupt in corruptions.items():
            with self.subTest(case=label):
                _, s = fixture()
                corrupt(s)
                with self.assertRaises((g1.Stop, KeyError, ValueError, TypeError, MockR0.Stop)):
                    g1.evaluate(MockR0, self.m, s, profile="postchange")

    def test_noncandidate_publication_not_promoted_or_changed_by_g1(self):
        # Preserved rehearsal/restore containers are not candidates for G1
        # gateway exposure. Candidate service host publication is still fatal.
        m, s = fixture()
        s["containers"][MockR0.ORIGINAL[0]]["published"] = True
        self.assertTrue(g1.evaluate(MockR0, m, s, profile="postchange"))
        s["containers"][MockR0.CANDIDATE[0]]["published"] = True
        with self.assertRaises(g1.Stop):
            g1.evaluate(MockR0, m, s, profile="postchange")

    def test_pinned_safety_module_verified_and_interlock_locked(self):
        helper = SCRIPT.with_name(g1.SAFETY_NAME)
        self.assertEqual(hashlib.sha256(helper.read_bytes()).hexdigest(), g1.SAFETY_SHA256)
        self.assertFalse(g1.G1_ACTIVATION_REVIEWED)

    def test_postchange_pilot_readonly_profile(self):
        m, s = fixture("postchange")
        s["units"]["CADDY"] = ["active", "disabled"]
        s["units"]["SOCKET"] = ["active", "disabled"]
        s["units"]["RELAY"] = ["active", "static"]
        self.assertTrue(g1.evaluate(MockR0, m, s, profile="postchange", gateway_state="pilot"))
        with self.assertRaises(g1.Stop):
            g1.evaluate(MockR0, m, s, profile="postchange", gateway_state="cold")

    def test_g1_unit_is_content_pinned_and_not_implicitly_gateway_enabled(self):
        self.assertEqual(hashlib.sha256(UNIT.read_bytes()).hexdigest(), g1.UNIT_SHA256)
        unit = UNIT.read_text()
        self.assertIn("Type=oneshot", unit)
        self.assertIn("TimeoutStartSec=260", unit)
        self.assertNotIn("--now", unit)
        self.assertNotIn("Wants=caddy.service", unit)
        self.assertNotIn("Requires=caddy.service", unit)
        self.assertNotIn("ExecStop=", unit)
        self.assertFalse(g1.G1_ACTIVATION_REVIEWED)
        self.assertNotIn("docker update", SCRIPT.read_text())
        self.assertNotIn("docker start", SCRIPT.read_text())

    def test_gateway_start_order_and_no_other_units(self):
        class Runner:
            def __init__(self):
                self.calls = []

            def invoke(self, cmd):
                self.calls.append(tuple(cmd))
                if cmd[1] == "show":
                    return b"ActiveState=active\nUnitFileState=disabled\n"
                return b""
        runner = Runner()
        g1.start_gateway(runner)
        self.assertEqual([x[:3] for x in runner.calls[:2]],
                         [("systemctl", "start", "ccpc-erpnext-upstream.socket"),
                          ("systemctl", "start", "caddy.service")])

    def test_failed_socket_start_does_not_start_caddy(self):
        class Runner:
            calls = []

            def invoke(self, cmd):
                self.calls.append(cmd)
                raise g1.Stop()
        runner = Runner()
        with self.assertRaises(g1.Stop):
            g1.start_gateway(runner)
        self.assertEqual(len(runner.calls), 1)

    def test_wrong_host_stops_before_unit_or_container(self):
        with mock.patch.object(g1.os, "geteuid", return_value=0), \
             mock.patch.object(g1.socket, "gethostname", return_value="wrong-host"):
            with self.assertRaises(g1.Stop):
                g1.check_host()

    def test_unit_hash_enforced(self):
        with mock.patch.object(g1.os, "geteuid", return_value=0), \
             mock.patch.object(g1.socket, "gethostname", return_value="ccpcerp-prod"), \
             mock.patch.object(g1, "private_file"), \
             mock.patch.object(g1, "sha256_file", return_value="0" * 64), \
             mock.patch.dict(g1.os.environ, {}, clear=True):
            with self.assertRaises(g1.Stop):
                g1.check_host()

    def test_offline_cli_no_service_start(self):
        fake_r0 = MockR0()
        fake_r0.load_json_file = lambda p, root_only=False: self.m if str(p).endswith('manifest') else self.s
        with mock.patch.object(g1, "get_r0", return_value=fake_r0), \
             mock.patch.object(g1, "start_gateway") as start:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = g1.main(["--manifest", "/tmp/manifest", "--offline-fixture", "/tmp/snapshot"])
            self.assertEqual(rc, 0)
            self.assertIn("READONLY_PREFLIGHT_PASS", out.getvalue())
            start.assert_not_called()

    def test_mutating_mode_rejects_prechange_profile(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = g1.main(["--manifest", "/tmp/x", "--gate-once", "--profile", "prechange"])
        self.assertEqual(rc, 1)
        self.assertEqual(out.getvalue().strip(), "CCPC_NEW_A3_G1_STOP_REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
