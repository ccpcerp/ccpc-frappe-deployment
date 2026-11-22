"""Six synthetic G1 systemd/listener tests; no live host, Docker or systemd use."""
import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "scripts/ccpc_new_a3_g1_unit_listener_readonly.py"
spec = importlib.util.spec_from_file_location("g1_unit_listener", SOURCE)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

BASELINE = {
    "docker.service": ("loaded", "active", "enabled"),
    "containerd.service": ("loaded", "active", "enabled"),
    "caddy.service": ("loaded", "active", "disabled"),
    "ccpc-erpnext-upstream.socket": ("loaded", "active", "disabled"),
    "ccpc-erpnext-upstream.service": ("loaded", "active", "static"),
    "caddy-api.service": ("masked", "inactive", "masked"),
    "ccpc-new-a3-g1-boot-gate.service": ("not-found", "inactive", ""),
}
LISTENERS = ("LISTEN 0 4096 192.168.50.186:443 0.0.0.0:*\n"
             "LISTEN 0 4096 127.0.0.1:8080 0.0.0.0:*\n")


class SyntheticTest(unittest.TestCase):
    def trial(self, extra="", override=None):
        states = dict(BASELINE)
        if override:
            states.update(override)
        def fake_read(*command):
            if command[0] == "systemctl":
                state = states[command[2]]
                return "".join(f"{key}={value}\n" for key, value in
                               zip(("LoadState", "ActiveState", "UnitFileState"), state))
            if command[:3] == ("ss", "-H", "-ltn"):
                return LISTENERS + extra
            raise AssertionError("unexpected command")
        with mock.patch.object(a, "read", fake_read), \
             mock.patch.object(a.os, "geteuid", return_value=0), \
             mock.patch.object(a.socket, "gethostname", return_value="ccpcerp-prod"), \
             mock.patch.dict(a.os.environ, {"SUDO_USER": "ccpcadmin"}, clear=True), \
             contextlib.redirect_stdout(io.StringIO()):
            try:
                a.check()
                return True
            except AssertionError:
                return False

    def test_baseline(self):
        self.assertTrue(self.trial())

    def test_public_https_listener_fails(self):
        self.assertFalse(self.trial(extra="LISTEN 0 4096 0.0.0.0:443 0.0.0.0:*\n"))

    def test_public_relay_listener_fails(self):
        self.assertFalse(self.trial(extra="LISTEN 0 4096 0.0.0.0:8080 0.0.0.0:*\n"))

    def test_independently_enabled_gateway_fails(self):
        self.assertFalse(self.trial(override={"caddy.service": ("loaded", "active", "enabled")}))

    def test_g1_unit_already_installed_fails(self):
        self.assertFalse(self.trial(override={"ccpc-new-a3-g1-boot-gate.service":
                                              ("loaded", "inactive", "disabled")}))

    def test_caddy_api_unmasked_fails(self):
        self.assertFalse(self.trial(override={"caddy-api.service": ("loaded", "inactive", "disabled")}))


if __name__ == "__main__":
    unittest.main()
