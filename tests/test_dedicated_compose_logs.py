"""Offline-only dedicated-pre-TLS Compose design guards; NEVER starts Docker.

Requires PyYAML for parsing. This models the Compose-spec volumes merge by
container target; it does not claim `docker compose config` or runtime approval.
"""
import copy
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "compose.yaml"
DEDICATED = ROOT / "overrides" / "compose.dedicated-pre-tls.yaml"
SITE = "/home/frappe/frappe-bench/sites"
LOGS = "/home/frappe/frappe-bench/logs"


class OverrideSequence(list):
    """Represent Compose !override only, without applying/interpolating it."""


class ComposeLoader(yaml.SafeLoader):
    pass


def override_sequence(loader, node):
    return OverrideSequence(loader.construct_sequence(node))


ComposeLoader.add_constructor("!override", override_sequence)


def load_file(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=ComposeLoader)


def short_mount(value):
    if not isinstance(value, str) or value.count(":") != 1:
        raise ValueError("Unexpected mount syntax")
    source, target = value.split(":")
    if not source or not target.startswith("/"):
        raise ValueError("Bad volume source or target")
    return source, target


def checked_design(base, overlay):
    """Fail-closed static design review, not a full Compose CLI evaluator."""
    if set(overlay) != {"services", "volumes"}:
        raise ValueError("Unexpected dedicated overlay root keys")
    services = overlay["services"]
    if not isinstance(services, dict) or set(services) != {"frontend", "db", "backend"}:
        raise ValueError("Unexpected dedicated override services")
    if set(services["backend"]) != {"volumes"}:
        raise ValueError("Backend override may modify only volumes")
    if set(services["db"]) != {"environment"}:
        raise ValueError("Database override may modify only environment")
    if set(services["frontend"]) != {"ports"}:
        raise ValueError("Frontend override may modify only ports")
    if (not isinstance(services["frontend"]["ports"], OverrideSequence)
            or list(services["frontend"]["ports"]) != ["127.0.0.1:8080:8080/tcp"]):
        raise ValueError("Dedicated frontend must remain loopback-only")
    if services["db"]["environment"] != {
        "MYSQL_ROOT_PASSWORD": "${DB_PASSWORD:?Dedicated production requires a nonempty DB_PASSWORD}"
    }:
        raise ValueError("Database password fallback guard changed")
    if overlay["volumes"] != {"logs": None}:
        raise ValueError("Only default-project-scoped named logs volume allowed")
    if base["volumes"] != {"sites": None}:
        raise ValueError("Unexpected base volume inventory")

    base_mounts = base["services"]["backend"]["volumes"]
    overlay_mounts = services["backend"]["volumes"]
    if type(base_mounts) is not list or type(overlay_mounts) is not list:
        raise ValueError("Mounts must use short-form Compose YAML lists")
    if [short_mount(i) for i in base_mounts] != [("sites", SITE)]:
        raise ValueError("Base backend sites mount changed")
    parsed_overlay = [short_mount(i) for i in overlay_mounts]
    if parsed_overlay != [("sites", SITE), ("logs", LOGS)]:
        raise ValueError("Dedicated backend must have exactly sites and logs")
    if len({target for _, target in parsed_overlay}) != len(parsed_overlay):
        raise ValueError("Duplicate target")

    # Docker Compose spec: volumes with same target merge by uniqueness key.
    # We model that one rule only, not a complete `docker compose config` run.
    effective = {target: source for source, target in map(short_mount, base_mounts)}
    effective.update({target: source for source, target in parsed_overlay})
    if effective != {SITE: "sites", LOGS: "logs"}:
        raise ValueError("Unexpected effective volume mapping")
    return effective


class NamedLogsComposeTests(unittest.TestCase):
    def setUp(self):
        self.base = load_file(BASE)
        self.overlay = load_file(DEDICATED)

    def reject(self, modify):
        o = copy.deepcopy(self.overlay)
        modify(o)
        with self.assertRaises(ValueError):
            checked_design(self.base, o)

    def test_dedicated_yaml_and_exact_named_mounts(self):
        self.assertEqual(checked_design(self.base, self.overlay),
                         {SITE: "sites", LOGS: "logs"})

    def test_baseline_compose_unmodified_for_other_profiles(self):
        self.assertEqual(self.base["services"]["backend"]["volumes"], [f"sites:{SITE}"])
        self.assertEqual(self.base["volumes"], {"sites": None})
        self.assertNotIn("logs", self.base["volumes"])

    def test_original_loopback_frontend_and_db_secret_guard(self):
        self.assertIsInstance(self.overlay["services"]["frontend"]["ports"], OverrideSequence)
        self.assertEqual(checked_design(self.base, self.overlay)[LOGS], "logs")

    def test_logs_volume_cannot_be_external_or_custom_named(self):
        for value in ({"external": True}, {"name": "other_logs"}, {"driver_opts": {"type": "none"}}):
            self.reject(lambda o: o["volumes"].update(logs=value))

    def test_unexpected_top_level_keys_rejected(self):
        self.reject(lambda o: o.update(networks={"privileged": None}))

    def test_no_extra_service_change(self):
        self.reject(lambda o: o["services"].update(scheduler={"privileged": True}))

    def test_backend_image_or_privilege_edit_rejected(self):
        self.reject(lambda o: o["services"]["backend"].update(privileged=True))

    def test_anonymous_volume_rejected(self):
        self.reject(lambda o: o["services"]["backend"]["volumes"].__setitem__(1, LOGS))

    def test_bind_mount_rejected(self):
        self.reject(lambda o: o["services"]["backend"]["volumes"].__setitem__(1, f"/tmp/logs:{LOGS}"))

    def test_wrong_target_rejected(self):
        self.reject(lambda o: o["services"]["backend"]["volumes"].__setitem__(1, "logs:/tmp/logs"))

    def test_duplicate_or_additional_mount_rejected(self):
        self.reject(lambda o: o["services"]["backend"]["volumes"].append(f"logs:{LOGS}"))
        self.reject(lambda o: o["services"]["backend"]["volumes"].append("secrets:/run/secrets"))

    def test_missing_logs_rejected(self):
        self.reject(lambda o: o["services"]["backend"]["volumes"].pop())

    def test_missing_explicit_sites_rejected(self):
        self.reject(lambda o: o["services"]["backend"]["volumes"].pop(0))

    def test_frontend_public_port_rejected(self):
        self.reject(lambda o: o["services"]["frontend"].update(ports=["0.0.0.0:8080:8080/tcp"]))

    def test_db_password_guard_downgrade_rejected(self):
        self.reject(lambda o: o["services"]["db"]["environment"].update(MYSQL_ROOT_PASSWORD="${DB_PASSWORD:-admin}"))

    def test_no_backup_authorization_from_compose(self):
        # This file describes volume declarations only, never a backup runner.
        self.assertNotIn("backup", self.overlay["services"])
        self.assertNotIn("docker.sock", DEDICATED.read_text())


if __name__ == "__main__":
    unittest.main()
