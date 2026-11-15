"""Synthetic tests; never call systemctl or inspect real credentials."""
import contextlib
import importlib.util
import io
from pathlib import Path
import stat
from types import SimpleNamespace
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / 'scripts/ccpc_new_a3_g1_credential_permissions_readonly.py'
spec = importlib.util.spec_from_file_location('g1_credentials_permissions', SOURCE)
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


class PermissionInventoryTests(unittest.TestCase):
    def run_fixture(self, *, file_mode=0o444, root_mode=0o755, service_mode=0o700,
                    wrong_host=False, bad_user=False, symlink=False):
        vals = {script.ROOT_DIR: (stat.S_IFDIR, root_mode, 0, 0),
                script.SERVICE_DIR: (stat.S_IFDIR, service_mode, 0, 0),
                script.RUNTIME_KEY: (stat.S_IFLNK if symlink else stat.S_IFREG, file_mode, 0, 0)}
        def fake_lstat(self):
            file_type, mode, uid, gid = vals[self]
            return SimpleNamespace(st_mode=file_type | mode, st_uid=uid, st_gid=gid)
        raw = 'LoadState=loaded\nActiveState=active\nUnitFileState=disabled\n'
        output = io.StringIO()
        with mock.patch.object(script.os, 'geteuid', return_value=0), \
             mock.patch.object(script.os.environ, 'get', wraps=script.os.environ.get), \
             mock.patch.dict(script.os.environ, {'SUDO_USER': 'wrong' if bad_user else 'ccpcadmin'}, clear=True), \
             mock.patch.object(script.socket, 'gethostname', return_value='wrong' if wrong_host else 'ccpcerp-prod'), \
             mock.patch.object(script.subprocess, 'run', return_value=SimpleNamespace(stdout=raw)), \
             mock.patch.object(script.Path, 'lstat', fake_lstat), \
             contextlib.redirect_stdout(output):
            try:
                script.audit()
                return True, output.getvalue()
            except Exception:
                return False, output.getvalue()

    def test_world_readable_file_inside_private_dir_is_observed_not_misclassified(self):
        okay, output = self.run_fixture()
        self.assertTrue(okay)
        self.assertIn('RUNTIME_CREDENTIAL_FILE_MODE=0444', output)
        self.assertIn('CREDENTIAL_SERVICE_DIR_MODE=0700', output)
        self.assertNotIn('private.key', output)

    def test_mode_permissive_directory_is_observed(self):
        okay, output = self.run_fixture(service_mode=0o755, file_mode=0o644)
        self.assertTrue(okay)
        self.assertIn('CREDENTIAL_SERVICE_DIR_MODE=0755', output)
        self.assertIn('RUNTIME_CREDENTIAL_FILE_MODE=0644', output)

    def test_symlink_fails_closed(self):
        self.assertFalse(self.run_fixture(symlink=True)[0])

    def test_wrong_host_fails_closed(self):
        self.assertFalse(self.run_fixture(wrong_host=True)[0])

    def test_wrong_sudo_user_fails_closed(self):
        self.assertFalse(self.run_fixture(bad_user=True)[0])


if __name__ == '__main__':
    unittest.main()
