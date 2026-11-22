"""Only synthetic Python fixtures; no NEW host, systemctl, or key reading."""
import contextlib
import importlib.util
import io
from pathlib import Path
import stat
from types import SimpleNamespace
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / 'scripts/ccpc_new_a3_g1_tls_dropin_readonly.py'
spec = importlib.util.spec_from_file_location('g1_tls_audit', SOURCE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class G1TlsInspectionTests(unittest.TestCase):
    def trial(self, *, dropins=None, text=None, mode=0o640, owner=0,
              reverse=None, credentials=None, environment=None,
              host='ccpcerp-prod', user='ccpcadmin', state='disabled'):
        dropins = [str(audit.CADDY_DROPIN)] if dropins is None else dropins
        text = '\n'.join(audit.EXPECTED_LINES) if text is None else text
        reverse = {"RequiredBy": audit.RELAY} if reverse is None else reverse
        credentials = ('ccpc_tls_key:/etc/ccpc-https/ccpcerp.internal.key'
                       if credentials is None else credentials)
        environment = ('CCPC_TLS_FULLCHAIN_FILE=/private/public.crt '
                       'CCPC_TLS_PRIVATE_KEY_FILE=/private/private.key'
                       if environment is None else environment)

        def get_unit(name):
            p = {'LoadState': 'loaded', 'ActiveState': 'active',
                 'UnitFileState': state, 'DropInPaths': '',
                 'LoadCredential': '', 'Environment': '',
                 'RequiredBy': '', 'WantedBy': '', 'TriggeredBy': ''}
            if name == 'caddy.service':
                p.update(DropInPaths=' '.join(dropins), LoadCredential=credentials,
                         Environment=environment)
            elif name == audit.SOCKET:
                p.update(reverse)
            else:
                raise AssertionError('unexpected systemd read')
            return p
        stdout = io.StringIO()
        with mock.patch.object(audit, 'unit', get_unit), \
             mock.patch.object(audit.os, 'geteuid', return_value=0), \
             mock.patch.object(audit.socket, 'gethostname', return_value=host), \
             mock.patch.dict(audit.os.environ, {'SUDO_USER': user}, clear=True), \
             mock.patch.object(audit.Path, 'lstat',
                               lambda self: SimpleNamespace(st_mode=stat.S_IFREG|mode,
                                                            st_uid=owner)), \
             mock.patch.object(audit.Path, 'read_text',
                               lambda self, **kwargs: text), \
             contextlib.redirect_stdout(stdout):
            try:
                audit.inspect()
                return True, stdout.getvalue()
            except Exception:
                return False, stdout.getvalue()

    def test_expected_reviewed_shape(self):
        ok, output = self.trial()
        self.assertTrue(ok)
        self.assertIn('CADDY_ONLY_REVIEWED_TLS_DROPIN=YES', output)
        self.assertIn('CADDY_TLS_DROPIN_REVIEW_TEMPLATE_MATCH=YES', output)
        self.assertIn('SOCKET_REVERSE_HAS_EXPECTED_RELAY=YES', output)
        self.assertIn('SOCKET_REVERSE_OTHER_UNITS_PRESENT=NO', output)
        self.assertNotIn('/private/', output)

    def test_extra_dropin_is_observed(self):
        _, out = self.trial(dropins=[str(audit.CADDY_DROPIN), '/etc/systemd/system/caddy.service.d/other.conf'])
        self.assertIn('CADDY_ONLY_REVIEWED_TLS_DROPIN=NO', out)

    def test_unknown_dropin_only_is_not_opened(self):
        _, out = self.trial(dropins=['/etc/systemd/system/caddy.service.d/unknown.conf'])
        self.assertIn('CADDY_TLS_DROPIN_REVIEW_TEMPLATE_MATCH=NO', out)

    def test_changed_directives_flagged(self):
        _, out = self.trial(text='[Service]\nExecStart=/bin/false')
        self.assertIn('CADDY_TLS_DROPIN_REVIEW_TEMPLATE_MATCH=NO', out)

    def test_bad_mode_and_owner_flagged(self):
        for kw in ({'mode': 0o666}, {'owner': 123}):
            with self.subTest(**kw):
                _, out = self.trial(**kw)
                self.assertIn('CADDY_TLS_DROPIN_ROOT_PROTECTED=NO', out)
                self.assertIn('CADDY_TLS_DROPIN_REVIEW_TEMPLATE_MATCH=NO', out)

    def test_extra_socket_reverse_flagged(self):
        _, out = self.trial(reverse={'RequiredBy': audit.RELAY, 'WantedBy': 'unexpected.service'})
        self.assertIn('SOCKET_REVERSE_OTHER_UNITS_PRESENT=YES', out)

    def test_missing_expected_socket_relay_flagged(self):
        _, out = self.trial(reverse={'RequiredBy': 'other.service'})
        self.assertIn('SOCKET_REVERSE_HAS_EXPECTED_RELAY=NO', out)

    def test_missing_effective_credentials_flagged(self):
        _, out = self.trial(credentials='')
        self.assertIn('CADDY_EFFECTIVE_TLS_CREDENTIAL_DECLARED=NO', out)

    def test_missing_effective_environment_flagged(self):
        _, out = self.trial(environment='')
        self.assertIn('CADDY_EFFECTIVE_TLS_ENV_NAMES_PRESENT=NO', out)

    def test_wrong_host_or_operator_stop(self):
        self.assertFalse(self.trial(host='some-other-host')[0])
        self.assertFalse(self.trial(user='root')[0])

    def test_unexpected_boot_enablement_stop(self):
        self.assertFalse(self.trial(state='enabled')[0])


if __name__ == '__main__':
    unittest.main()
