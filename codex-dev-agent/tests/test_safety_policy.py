"""Source-only tests: no Docker, ERPNext, network or real credentials required."""
import copy
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    instance = importlib.util.module_from_spec(spec)
    sys.modules[name] = instance
    spec.loader.exec_module(instance)
    return instance


gate = module("codex_dev_compose_gate", "check_compose.py")
secrets = module("codex_dev_local_secrets", "init_local_secrets.py")


def safe_config():
    images = {"agent": "frappe/bench:latest", "db": "mariadb:11.8",
              "redis-cache": "redis:7-alpine", "redis-queue": "redis:7-alpine",
              "egress-proxy": "ubuntu/squid:latest"}
    result = {
        "name": "ccpc_codex_dev_agent",
        "networks": {"lab": {"internal": True}, "outgoing": {"internal": False}},
        "secrets": {
            "db-user-password": {"file": "/safe/codex-dev-agent/local-secrets/db-user-password"},
            "db-root-password": {"file": "/safe/codex-dev-agent/local-secrets/db-root-password"},
        },
        "services": {
            "agent": {
                "user": "1000:1000", "read_only": True,
                "cap_drop": ["ALL"], "security_opt": ["no-new-privileges:true"],
                "networks": ["lab"],
                "volumes": [
                    {"type": "volume", "source": "agent-home", "target": "/home/frappe"},
                    {"type": "volume", "source": "agent-cache", "target": "/home/frappe/.cache"},
                ],
                "secrets": [{"source": "db-user-password"}],
            },
            "db": {"cap_drop": ["ALL"], "security_opt": ["no-new-privileges:true"],
                   "networks": ["lab"], "volumes": [
                       {"type": "volume", "source": "db-data", "target": "/var/lib/mysql"}]},
            "redis-cache": {"cap_drop": ["ALL"], "security_opt": ["no-new-privileges:true"], "networks": ["lab"]},
            "redis-queue": {"cap_drop": ["ALL"], "security_opt": ["no-new-privileges:true"], "networks": ["lab"]},
            "egress-proxy": {
                "cap_drop": ["ALL"], "security_opt": ["no-new-privileges:true"],
                "read_only": True, "profiles": ["online"],
                "networks": ["lab", "outgoing"],
            },
        },
    }
    for name, service in result["services"].items():
        service["image"] = images[name]
        service["pull_policy"] = "never"
        if name == "db":
            service["cap_add"] = ["CHOWN", "SETUID", "SETGID", "DAC_OVERRIDE", "FOWNER"]
        if name in ("redis-cache", "redis-queue"):
            service["user"] = "redis"
    return result


class TestStaticComposeGate(unittest.TestCase):
    def setUp(self):
        self.config = safe_config()

    def test_secure_baseline_accepts(self):
        self.assertTrue(gate.validate(self.config))

    def test_host_network_denied(self):
        self.config["services"]["agent"]["network_mode"] = "host"
        with self.assertRaises(ValueError):
            gate.validate(self.config)

    def test_public_port_denied(self):
        self.config["services"]["agent"]["ports"] = ["9999:9999"]
        with self.assertRaises(ValueError):
            gate.validate(self.config)

    def test_bind_mount_denied(self):
        self.config["services"]["agent"]["volumes"][0] = {
            "type": "bind", "source": "/home/user/.ssh", "target": "/work"
        }
        with self.assertRaises(ValueError):
            gate.validate(self.config)

    def test_external_network_denied(self):
        self.config["services"]["agent"]["networks"] = ["lab", "outgoing"]
        with self.assertRaises(ValueError):
            gate.validate(self.config)

    def test_egress_proxy_always_on_denied(self):
        self.config["services"]["egress-proxy"]["profiles"] = []
        with self.assertRaises(ValueError):
            gate.validate(self.config)


    def test_unreviewed_image_denied(self):
        self.config["services"]["agent"]["image"] = "another/agent:latest"
        with self.assertRaises(ValueError):
            gate.validate(self.config)

    def test_implicit_image_pull_denied(self):
        self.config["services"]["agent"]["pull_policy"] = "always"
        with self.assertRaises(ValueError):
            gate.validate(self.config)

    def test_extra_mariadb_capability_denied(self):
        self.config["services"]["db"]["cap_add"].append("NET_ADMIN")
        with self.assertRaises(ValueError):
            gate.validate(self.config)

    def test_missing_mariadb_initialization_cap_denied(self):
        self.config["services"]["db"]["cap_add"].remove("SETUID")
        with self.assertRaises(ValueError):
            gate.validate(self.config)

    def test_redis_root_default_denied(self):
        self.config["services"]["redis-queue"].pop("user")
        with self.assertRaises(ValueError):
            gate.validate(self.config)

    def test_legacy_db_secret_in_agent_denied(self):
        self.config["services"]["agent"]["secrets"] = ["db-root-password"]
        with self.assertRaises(ValueError):
            gate.validate(self.config)


class TestSecretSafety(unittest.TestCase):
    def test_creation_and_reuse_without_disclosure(self):
        original = secrets.DIRECTORY
        with tempfile.TemporaryDirectory() as tmp:
            try:
                secrets.DIRECTORY = Path(tmp) / "local-secrets"
                secrets.main()
                first = {name: (secrets.DIRECTORY / name).read_bytes() for name in secrets.FILES}
                self.assertEqual({name: (secrets.DIRECTORY / name).stat().st_mode & 0o777 for name in secrets.FILES},
                                 {name: 0o600 for name in secrets.FILES})
                self.assertEqual(secrets.DIRECTORY.stat().st_mode & 0o777, 0o700)
                secrets.main()
                second = {name: (secrets.DIRECTORY / name).read_bytes() for name in secrets.FILES}
                self.assertEqual(first, second)
                self.assertNotEqual(first[secrets.FILES[0]], first[secrets.FILES[1]])
            finally:
                secrets.DIRECTORY = original


if __name__ == "__main__":
    unittest.main()
