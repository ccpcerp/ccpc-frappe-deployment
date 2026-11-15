"""Offline, synthetic fail-closed G1 safety tests. No Docker/systemd/network access."""
import contextlib
import sys
from pathlib import Path
import stat
from types import SimpleNamespace
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ccpc_new_a3_g1_safety as s


class FakeR0:
    def __init__(self):
        self.calls = []
        self.mode = 'cold'
        self.extra_reverse = ''
        self.extra_dropin = ''
        self.caddy_exec = 'argv[]=/usr/bin/caddy run --config /etc/caddy/Caddyfile ;'
        self.env = 'CCPC_TLS_FULLCHAIN_FILE=/private/cert CCPC_TLS_PRIVATE_KEY_FILE=/private/key'
        self.listen = b''
        self.udp = b''

    def invoke(self, command, *, data=None):
        self.calls.append(tuple(command))
        if command[0] == 'ss':
            return self.udp if command[2] == '-lun' else self.listen
        if command[0] != 'systemctl':
            raise AssertionError('unexpected subprocess')
        name = command[2]
        p = {'LoadState': 'loaded', 'ActiveState': 'inactive',
             'UnitFileState': 'disabled', 'DropInPaths': '', 'ExecStart': '',
             'RequiredBy': '', 'WantedBy': '', 'TriggeredBy': '',
             'Requires': '', 'After': '', 'Environment': ''}
        if name == 'caddy.service':
            p.update(DropInPaths=str(s.TLS_DROPIN) + self.extra_dropin,
                     ExecStart=self.caddy_exec, Environment=self.env)
        elif name == 'ccpc-erpnext-upstream.socket':
            p.update(RequiredBy='ccpc-erpnext-upstream.service'+self.extra_reverse)
        elif name == 'ccpc-erpnext-upstream.service':
            p.update(Requires='ccpc-erpnext-upstream.socket',
                     After='ccpc-erpnext-upstream.socket')
        else:
            raise AssertionError(name)
        return ''.join(k + '=' + v + '\n' for k,v in p.items()).encode()


class GatewaySafetyTests(unittest.TestCase):
    def verify(self, *, caddy=None, dropin=None, modes=None, manipulate=None):
        caddy = '\n'.join(s.CADDY_CONFIG) if caddy is None else caddy
        dropin = '\n'.join(s.TLS_DROPIN_LINES) if dropin is None else dropin
        modes = {} if modes is None else modes
        fake = FakeR0()
        if manipulate:
            manipulate(fake)
        def file_stat(self):
            mode = modes.get(self, 0o600)
            return SimpleNamespace(st_mode=stat.S_IFREG | mode, st_uid=0)
        def file_read(self, *args, **kwargs):
            return caddy if self == s.CADDYFILE else dropin
        with mock.patch.object(s.Path, 'lstat', file_stat), \
             mock.patch.object(s.Path, 'read_text', file_read):
            return s.validate_gateway_config(fake)

    def test_approved_config_and_edges(self):
        self.assertTrue(self.verify())

    def test_unknown_reverse_unit_denied(self):
        with self.assertRaises(s.SafetyStop):
            self.verify(manipulate=lambda r: setattr(r,'extra_reverse',' other.service'))

    def test_unreviewed_dropin_denied(self):
        with self.assertRaises(s.SafetyStop):
            self.verify(manipulate=lambda r: setattr(r,'extra_dropin',' /other.conf'))

    def test_missing_env_denied(self):
        with self.assertRaises(s.SafetyStop):
            self.verify(manipulate=lambda r: setattr(r,'env','CCPC_TLS_FULLCHAIN_FILE=/private/cert'))

    def test_unknown_caddy_exec_denied(self):
        with self.assertRaises(s.SafetyStop):
            self.verify(manipulate=lambda r: setattr(r,'caddy_exec','/usr/bin/caddy run --config /tmp/mismatch'))

    def test_wrong_bind_denied(self):
        txt='\n'.join(s.CADDY_CONFIG).replace('bind 192.168.50.186', 'bind 0.0.0.0')
        with self.assertRaises(s.SafetyStop):
            self.verify(caddy=txt)

    def test_tls_line_mismatch_denied(self):
        txt='\n'.join(s.CADDY_CONFIG).replace('tls {$CCPC_TLS_FULLCHAIN_FILE} {$CCPC_TLS_PRIVATE_KEY_FILE}', 'tls internal')
        with self.assertRaises(s.SafetyStop):
            self.verify(caddy=txt)

    def test_private_source_key_world_read_denied(self):
        with self.assertRaises(s.SafetyStop):
            self.verify(modes={s.SOURCE_KEY:0o644})

    def test_symlink_caddyfile_denied(self):
        fake=FakeR0()
        def link_stat(self):
            return SimpleNamespace(st_mode=(stat.S_IFLNK if self==s.CADDYFILE else stat.S_IFREG)|0o600, st_uid=0)
        with mock.patch.object(s.Path, 'lstat', link_stat):
            with self.assertRaises(s.SafetyStop):
                s.validate_gateway_config(fake)

    def test_cold_requires_empty_listeners(self):
        f=FakeR0()
        self.assertTrue(s.validate_tcp_bindings(f,gateway_state='cold'))
        f.listen=b'LISTEN 0 4096 127.0.0.1:8080 0.0.0.0:*\n'
        with self.assertRaises(s.SafetyStop):
            s.validate_tcp_bindings(f,gateway_state='cold')

    def test_pilot_requires_exact_bindings(self):
        f=FakeR0()
        f.listen=b'LISTEN 0 4096 192.168.50.186:443 0.0.0.0:*\nLISTEN 0 4096 127.0.0.1:8080 0.0.0.0:*\n'
        self.assertTrue(s.validate_tcp_bindings(f,gateway_state='pilot'))
        f.listen+=b'LISTEN 0 4096 0.0.0.0:443 0.0.0.0:*\n'
        with self.assertRaises(s.SafetyStop):
            s.validate_tcp_bindings(f,gateway_state='pilot')

    def test_udp_quic_443_denied(self):
        f = FakeR0()
        f.udp = b'UNCONN 0 0 192.168.50.186:443 0.0.0.0:*\n'
        with self.assertRaises(s.SafetyStop):
            s.validate_tcp_bindings(f,gateway_state='cold')

    def test_deadline_wrapper_restores_original_and_caps_subprocess(self):
        class R0:
            def invoke(self, command, *, data=None):
                return b'original'
        r=R0()
        prior=r.invoke
        with mock.patch.object(s.time,'monotonic',side_effect=[10,11]), \
             mock.patch.object(s.subprocess,'run',return_value=SimpleNamespace(stdout=b'ok')) as run:
            with s.deadline_guard(r, deadline=15):
                self.assertEqual(r.invoke(('docker','ps')),b'ok')
        self.assertEqual(r.invoke(('whatever',)), b'original')
        self.assertEqual(run.call_args.kwargs['timeout'],5)

    def test_deadline_expired_stops_without_invocation(self):
        class R0: invoke=lambda self,*a,**kw:b'original'
        r=R0()
        with mock.patch.object(s.time,'monotonic',return_value=20), \
             mock.patch.object(s.subprocess,'run') as run:
            with s.deadline_guard(r,deadline=20):
                with self.assertRaises(s.SafetyStop):
                    r.invoke(('docker','ps'))
            run.assert_not_called()

    def test_timeout_sanitized_and_restored(self):
        class R0: invoke=lambda self,*a,**kw:b'original'
        r=R0()
        with mock.patch.object(s.time,'monotonic',return_value=12), \
             mock.patch.object(s.subprocess,'run',side_effect=s.subprocess.TimeoutExpired(('docker','ps'),3)):
            with self.assertRaises(s.SafetyStop):
                with s.deadline_guard(r,deadline=15):
                    r.invoke(('docker','ps'))
        self.assertEqual(r.invoke(('whatever',)),b'original')

if __name__ == '__main__':
    unittest.main()
