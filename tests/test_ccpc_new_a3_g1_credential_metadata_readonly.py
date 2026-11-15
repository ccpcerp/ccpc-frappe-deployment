"""Synthetic only: no host systemctl or secret files touched."""
import contextlib
import io
import os
from pathlib import Path
import stat
from types import SimpleNamespace
import unittest
from unittest import mock

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import ccpc_new_a3_g1_credential_metadata_readonly as gate


class TestCredentialMetadata(unittest.TestCase):
    def run_fixture(self, *, properties=None, host='ccpcerp-prod', user='ccpcadmin',
                    source=True, runtime=True, source_mode=0o600, runtime_mode=0o400,
                    caddy_active=True):
        values = dict(properties or {})
        values.update(LoadState='loaded', ActiveState='active' if caddy_active else 'inactive',
                      UnitFileState='disabled')
        def stat_file(self):
            if self == gate.SOURCE_KEY and source:
                return SimpleNamespace(st_mode=stat.S_IFREG | source_mode, st_size=1024)
            if self == gate.RUNTIME_KEY and runtime:
                return SimpleNamespace(st_mode=stat.S_IFREG | runtime_mode, st_size=1024)
            raise FileNotFoundError()
        out = io.StringIO()
        with mock.patch.object(gate, 'unit', return_value=values), \
             mock.patch.object(gate.os, 'geteuid', return_value=0), \
             mock.patch.object(gate.socket, 'gethostname', return_value=host), \
             mock.patch.dict(gate.os.environ, {'SUDO_USER': user}, clear=True), \
             mock.patch.object(gate.Path, 'lstat', stat_file), \
             contextlib.redirect_stdout(out):
            try:
                gate.audit()
                return True, out.getvalue()
            except Exception:
                return False, out.getvalue()

    def test_both_systemctl_property_shapes(self):
        ok, out = self.run_fixture(properties={'LoadCredential': '(name=ccpc_tls_key path=hidden)',
                                                'LoadCredentialEx': 'other'} )
        self.assertTrue(ok)
        self.assertIn('SYSTEMD_LOADCREDENTIAL_NAME_PRESENT=YES', out)
        self.assertIn('SYSTEMD_LOADCREDENTIALEX_NAME_PRESENT=NO', out)
        self.assertNotIn('hidden', out)

    def test_properties_missing_inconclusive_runtime_visible(self):
        ok, out = self.run_fixture()
        self.assertTrue(ok)
        self.assertIn('SYSTEMD_LOADCREDENTIAL_PROPERTY_PRESENT=NO', out)
        self.assertIn('TLS_RUNTIME_CREDENTIAL_HOST_VISIBLE=YES', out)

    def test_runtime_not_visible_still_inventory_completes(self):
        ok, out = self.run_fixture(runtime=False)
        self.assertTrue(ok)
        self.assertIn('TLS_RUNTIME_CREDENTIAL_HOST_VISIBLE=NO', out)
        self.assertIn('INVENTORY_COMPLETE', out)

    def test_source_missing_flagged_without_stop(self):
        ok, out = self.run_fixture(source=False)
        self.assertTrue(ok)
        self.assertIn('TLS_SOURCE_KEY_METADATA_PRESENT=NO', out)

    def test_key_unsafe_permissions_flagged(self):
        ok, out = self.run_fixture(source_mode=0o644, runtime_mode=0o444)
        self.assertTrue(ok)
        self.assertIn('TLS_SOURCE_KEY_PRIVATE_MODE=NO', out)
        self.assertIn('TLS_RUNTIME_CREDENTIAL_PRIVATE_MODE=NO', out)

    def test_wrong_host_stops(self):
        self.assertFalse(self.run_fixture(host='wrong')[0])

    def test_wrong_operator_stops(self):
        self.assertFalse(self.run_fixture(user='other')[0])

    def test_inactive_caddy_stops(self):
        self.assertFalse(self.run_fixture(caddy_active=False)[0])


if __name__ == '__main__':
    unittest.main()
