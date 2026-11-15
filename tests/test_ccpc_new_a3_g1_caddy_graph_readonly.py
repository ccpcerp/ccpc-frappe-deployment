"""Synthetic-only tests for sanitized G1 Caddy/loaded-systemd inventory."""
import contextlib
import importlib.util
import io
from pathlib import Path
import stat
from types import SimpleNamespace
import unittest
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "scripts/ccpc_new_a3_g1_caddy_graph_readonly.py"
spec = importlib.util.spec_from_file_location("caddy_graph", SRC)
aud = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aud)

CADDY = """# Private settings must not be printed.
{
 admin off
 auto_https off
 servers 192.168.50.186:443 {
  protocols h1 h2
  strict_sni_host on
 }
}
https://ccpcerp.internal:443 {
 bind 192.168.50.186
 tls /secret/cert.pem /secret/key.pem
 reverse_proxy 127.0.0.1:8080
}
"""
NAMES = ("docker.service", "containerd.service", "caddy.service",
         "ccpc-erpnext-upstream.socket", "ccpc-erpnext-upstream.service",
         "caddy-api.service")


class G1InventoryTests(unittest.TestCase):
    def exercise(self, *, config=CADDY, udp443=False, dropin=False, bad_owner=False,
                 host="ccpcerp-prod", operator="ccpcadmin", caddy_enabled=False,
                 include_exec=True):
        def fake_read(*args):
            if args[0] == "ss":
                return ("UNCONN 0 0 127.0.0.1:5353 0.0.0.0:*\n" +
                        ("UNCONN 0 0 192.168.50.186:443 0.0.0.0:*\n" if udp443 else ""))
            if args[0] != "systemctl" or args[2] not in NAMES:
                raise AssertionError("unanticipated command")
            unit = args[2]
            fields = {"LoadState": "loaded", "ActiveState": "active",
                      "UnitFileState": "disabled",
                      "DropInPaths": "/etc/systemd/system/x.conf" if dropin and unit == "caddy.service" else "",
                      "ExecStart": "argv[]=/usr/bin/caddy run --config /etc/caddy/Caddyfile ;" if include_exec else "",
                      "Requires": "", "After": "", "Wants": "",
                      "RequiredBy": "", "WantedBy": "", "TriggeredBy": "", "Triggers": ""}
            if unit == "ccpc-erpnext-upstream.service":
                fields["Requires"] = "ccpc-erpnext-upstream.socket"
                fields["After"] = "ccpc-erpnext-upstream.socket"
            return "".join(f"{k}={v}\n" for k, v in fields.items())
        def fake_lstat(_):
            return SimpleNamespace(st_mode=stat.S_IFREG | 0o640,
                                   st_uid=123 if bad_owner else 0)
        output = io.StringIO()
        with mock.patch.object(aud, "read", fake_read), \
             mock.patch.object(aud.os, "geteuid", return_value=0), \
             mock.patch.object(aud.socket, "gethostname", return_value=host), \
             mock.patch.dict(aud.os.environ, {"SUDO_USER": operator}, clear=True), \
             mock.patch.object(aud.Path, "lstat", fake_lstat), \
             mock.patch.object(aud.Path, "read_text", lambda *_a, **_kw: config), \
             contextlib.redirect_stdout(output):
            try:
                aud.inspect()
                return True, output.getvalue()
            except Exception:
                return False, output.getvalue()

    def test_expected_template_is_observation_not_security_pass(self):
        ok, out = self.exercise()
        self.assertTrue(ok)
        self.assertIn("CCPC_NEW_A3_G1_CADDYFILE_REVIEW_TEMPLATE_SHAPE=YES", out)
        self.assertIn("CCPC_NEW_A3_G1_UDP443_LISTENER_PRESENT=NO", out)
        self.assertIn("CCPC_NEW_A3_G1_CADDY_GRAPH_READONLY_INVENTORY_COMPLETE", out)
        self.assertNotIn("/secret/", out)

    def test_unknown_config_is_review_not_silent_pass(self):
        ok, out = self.exercise(config=CADDY.replace("reverse_proxy 127.0.0.1:8080",
                                                       "reverse_proxy 0.0.0.0:8080"))
        self.assertTrue(ok)
        self.assertIn("CADDYFILE_REVIEW_TEMPLATE_SHAPE=NO", out)

    def test_udp_443_is_observed(self):
        ok, out = self.exercise(udp443=True)
        self.assertTrue(ok)
        self.assertIn("UDP443_LISTENER_PRESENT=YES", out)

    def test_dropin_is_observed(self):
        ok, out = self.exercise(dropin=True)
        self.assertTrue(ok)
        self.assertIn("CADDY_DROPINS_PRESENT=YES", out)

    def test_unexpected_caddy_command_is_observed(self):
        ok, out = self.exercise(include_exec=False)
        self.assertTrue(ok)
        self.assertIn("CADDY_UNIT_CONFIG_PATH_MATCH=NO", out)

    def test_wrong_host_or_user_stops(self):
        self.assertFalse(self.exercise(host="other")[0])
        self.assertFalse(self.exercise(operator="root")[0])

    def test_wrong_file_owner_stops(self):
        self.assertFalse(self.exercise(bad_owner=True)[0])


if __name__ == "__main__":
    unittest.main()
