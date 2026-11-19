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
        "networks": {
            "lab": {"internal": True, "driver": "bridge"},
            "proxy_clients": {
                "internal": True, "driver": "bridge", "attachable": False,
                "enable_ipv6": False,
                "ipam": {"config": [{"subnet": gate.CLIENT_SUBNET}]},
            },
            "outgoing": {"internal": False, "driver": "bridge",
                         "attachable": False, "enable_ipv6": False},
        },
        "secrets": {
            "db-user-password": {"file": "/safe/codex-dev-agent/local-secrets/db-user-password"},
            "db-root-password": {"file": "/safe/codex-dev-agent/local-secrets/db-root-password"},
        },
        "services": {
            "agent": {
                "user": "1000:1000", "read_only": True,
                "command": ["sleep", "infinity"],
                "cap_drop": ["ALL"], "security_opt": ["no-new-privileges:true"],
                "networks": {"lab": None,
                             "proxy_clients": {"ipv4_address": gate.AGENT_CLIENT_IP}},
                "environment": {
                    "HTTP_PROXY": "http://egress-proxy:3128",
                    "HTTPS_PROXY": "http://egress-proxy:3128",
                    "ALL_PROXY": "",
                    "NO_PROXY": "localhost,127.0.0.1,db,redis-cache,redis-queue",
                },
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
                "command": ["squid", "-N", "-f", "/etc/squid/squid.conf"],
                "networks": {
                    "proxy_clients": {"ipv4_address": gate.PROXY_CLIENT_IP},
                    "outgoing": None,
                },
                "volumes": [{
                    "type": "bind",
                    "source": "/safe/codex-dev-agent/proxy/squid.conf",
                    "target": "/etc/squid/squid.conf",
                    "read_only": True,
                }],
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
        self.assertTrue(gate.validate(
            self.config,
            proxy_policy=(ROOT / "proxy" / "squid.conf").read_text(encoding="utf-8"),
        ))

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


class TestProxyNetworkIsolation(unittest.TestCase):
    def setUp(self):
        self.config = safe_config()

    def rejected(self):
        with self.assertRaises(ValueError):
            gate.validate(self.config)

    def test_proxy_must_not_share_lab_bridge(self):
        self.config["services"]["egress-proxy"]["networks"]["lab"] = None
        self.rejected()

    def test_db_must_not_join_proxy_client_bridge(self):
        self.config["services"]["db"]["networks"] = ["lab", "proxy_clients"]
        self.rejected()

    def test_redis_must_not_join_proxy_client_bridge(self):
        self.config["services"]["redis-cache"]["networks"] = ["lab", "proxy_clients"]
        self.rejected()

    def test_agent_must_not_join_outgoing_bridge(self):
        self.config["services"]["agent"]["networks"]["outgoing"] = None
        self.rejected()

    def test_wrong_agent_ip_denied(self):
        self.config["services"]["agent"]["networks"]["proxy_clients"]["ipv4_address"] = "172.30.250.4"
        self.rejected()

    def test_wrong_proxy_ip_denied(self):
        self.config["services"]["egress-proxy"]["networks"]["proxy_clients"]["ipv4_address"] = "172.30.250.4"
        self.rejected()

    def test_client_network_must_be_internal(self):
        self.config["networks"]["proxy_clients"]["internal"] = False
        self.rejected()

    def test_client_network_must_not_be_attachable(self):
        self.config["networks"]["proxy_clients"]["attachable"] = True
        self.rejected()

    def test_client_network_ipv6_disabled(self):
        self.config["networks"]["proxy_clients"]["enable_ipv6"] = True
        self.rejected()

    def test_client_subnet_cannot_drift(self):
        self.config["networks"]["proxy_clients"]["ipam"]["config"][0]["subnet"] = "172.30.251.0/29"
        self.rejected()

    def test_proxy_published_port_denied(self):
        self.config["services"]["egress-proxy"]["ports"] = ["3128:3128"]
        self.rejected()

    def test_proxy_policy_mount_must_be_readonly(self):
        self.config["services"]["egress-proxy"]["volumes"][0]["read_only"] = False
        self.rejected()

    def test_proxy_must_not_have_secrets(self):
        self.config["services"]["egress-proxy"]["secrets"] = ["db-user-password"]
        self.rejected()

    def test_lowercase_proxy_env_override_denied(self):
        self.config["services"]["agent"]["environment"]["http_proxy"] = "http://other:3128"
        self.rejected()


    def test_unreviewed_proxy_entrypoint_denied(self):
        self.config["services"]["egress-proxy"]["entrypoint"] = ["/bin/sh", "-c"]
        self.rejected()

    def test_unreviewed_proxy_command_denied(self):
        self.config["services"]["egress-proxy"]["command"] = ["sleep", "infinity"]
        self.rejected()

    def test_unreviewed_proxy_environment_denied(self):
        self.config["services"]["egress-proxy"]["environment"] = {"HTTP_PROXY": "http://other"}
        self.rejected()

    def test_unreviewed_host_ipc_denied(self):
        self.config["services"]["agent"]["ipc"] = "host"
        self.rejected()

    def test_unreviewed_security_opt_denied(self):
        self.config["services"]["egress-proxy"]["security_opt"].append("seccomp:unconfined")
        self.rejected()

    def test_application_ipam_mutation_denied(self):
        self.config["networks"]["lab"]["ipam"] = {"config": [{"subnet": "172.30.123.0/24"}]}
        self.rejected()


    def test_outgoing_ipv6_must_stay_disabled(self):
        self.config["networks"]["outgoing"]["enable_ipv6"] = True
        self.rejected()

    def test_agent_restart_always_denied(self):
        self.config["services"]["agent"]["restart"] = "always"
        self.rejected()

    def test_proxy_restart_always_denied(self):
        self.config["services"]["egress-proxy"]["restart"] = "always"
        self.rejected()

    def test_unreviewed_agent_gateway_priority_denied(self):
        self.config["services"]["agent"]["networks"]["proxy_clients"]["gw_priority"] = 1
        self.rejected()

    def test_unreviewed_agent_network_alias_denied(self):
        self.config["services"]["agent"]["networks"]["proxy_clients"]["aliases"] = []
        self.rejected()

    def test_unreviewed_proxy_outgoing_priority_denied(self):
        self.config["services"]["egress-proxy"]["networks"]["outgoing"] = {
            "gw_priority": 1
        }
        self.rejected()

    def test_lowercase_no_proxy_denied(self):
        self.config["services"]["agent"]["environment"]["no_proxy"] = "*"
        self.rejected()

    def test_missing_proxy_source_policy_denied(self):
        with self.assertRaises(ValueError):
            gate.validate(self.config, proxy_policy="")

class TestProxyPolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = (ROOT / "proxy" / "squid.conf").read_text(encoding="utf-8")

    def test_approved_policy_accepts(self):
        self.assertTrue(gate.validate_proxy_policy(self.policy))

    def denies(self, policy):
        with self.assertRaises(ValueError):
            gate.validate_proxy_policy(policy)

    def test_wildcard_listener_denied(self):
        self.denies(self.policy.replace(
            "http_port " + gate.PROXY_LISTENER, "http_port 3128"
        ))

    def test_additional_listener_denied(self):
        self.denies(self.policy + "\nhttp_port 0.0.0.0:3129\n")

    def test_broad_client_acl_denied(self):
        self.denies(self.policy.replace(
            "src " + gate.PROXY_SOURCE, "src 172.30.250.0/29"
        ))

    def test_missing_source_deny_denied(self):
        self.denies(self.policy.replace("http_access deny !codex_agent\n", ""))

    def test_extra_allow_denied(self):
        self.denies(self.policy + "\nhttp_access allow all\n")

    def test_destination_deny_removal_denied(self):
        self.denies(self.policy.replace("http_access deny prohibited\n", ""))

    def test_domain_allowlist_expansion_denied(self):
        self.denies(self.policy.replace(
            ".pythonhosted.org", ".pythonhosted.org .example.com"
        ))

    def test_include_file_denied(self):
        self.denies(self.policy + "\ninclude /etc/squid/extra.conf\n")

    def test_upstream_proxy_override_denied(self):
        self.denies(self.policy + "\ncache_peer 192.0.2.9 parent 3128 0\n")


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
