"""Pure synthetic tests: no Docker, Redis or host connection."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import unittest
from types import SimpleNamespace
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / 'scripts' / 'ccpc_new_a3_g1_redis_counts_readonly.py'
spec = importlib.util.spec_from_file_location('ccpc_redis_review', SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FakeConn:
    def __init__(self, values=None):
        self.values = values or {}
        self.received = []
        self.pending = b''
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def settimeout(self, n):
        assert n == 5

    def sendall(self, payload):
        chunks = payload.split(b'\r\n')
        count = int(chunks[0][1:])
        parts = tuple(chunks[i].decode('ascii') for i in range(2, 2 + 2 * count, 2))
        self.received.append(parts)
        command = parts[0]
        if parts in self.values:
            value = self.values[parts]
        elif command == 'TYPE':
            if parts[1] == 'rq:queues':
                value = 'set'
            elif parts[1].startswith('rq:queue:'):
                value = 'list'
            else:
                value = 'zset'
        elif command == 'DBSIZE':
            value = 24
        elif command == 'INFO':
            value = b'# Clients\r\nconnected_clients:2\r\n'
        elif command == 'SCARD':
            value = 3
        elif command in ('LLEN', 'ZCARD'):
            value = 0
        else:
            raise AssertionError(f'unexpected Redis operation {command}')
        if isinstance(value, int):
            self.pending += b':' + str(value).encode() + b'\r\n'
        elif isinstance(value, str):
            self.pending += b'+' + value.encode() + b'\r\n'
        else:
            self.pending += value if value.startswith(b'-') else (
                b'$' + str(len(value)).encode() + b'\r\n' + value + b'\r\n')

    def recv(self, n):
        out, self.pending = self.pending[:n], self.pending[n:]
        return out


def scenario():
    ids = {name: f'{i:064x}' for i, name in enumerate(sorted(mod.EXPECTED), 1)}
    network_name = 'ccpc_prod_erpnext_default'
    network_id = 'n' * 64
    image_id = 'sha256:' + 'a' * 64
    data = {'schema': 1, 'container_ids': ids, 'app_image_id': image_id,
            'network_name': network_name}
    rows = []
    for name in sorted(mod.EXPECTED):
        rows.append({'Name': '/' + name, 'Id': ids[name], 'Image': image_id,
                     'State': {'Running': name != mod.DRILL_FAILED,
                               'ExitCode': 1 if name == mod.DRILL_FAILED else 0},
                     'HostConfig': {'RestartPolicy': {'Name': 'no'}},
                     'NetworkSettings': {'Networks': {network_name: {
                         'IPAddress': '172.25.0.4' if name.endswith('-redis-queue-1') else '172.25.0.5',
                         'NetworkID': network_id}}}})
    return data, rows, set(mod.EXPECTED)


class RedisMetadataTests(unittest.TestCase):
    def run_case(self, edit=None, *, values=None, host='ccpcerp-prod', sudo='ccpcadmin',
                 uid=0, docker_env=None, socket_error=None):
        data, rows, names = scenario()
        if edit:
            edit(data, rows, names)
        conn = FakeConn(values)
        docker_calls = []
        network_calls = []

        def fake_docker(*args):
            docker_calls.append(args)
            if args[0] == 'ps':
                return '\n'.join(sorted(names)) + '\n'
            if args[:2] == ('container', 'inspect'):
                return json.dumps(rows)
            raise AssertionError('unsafe Docker command')

        def connect(where, timeout):
            network_calls.append((where, timeout))
            if socket_error:
                raise socket_error
            return conn

        def fake_lstat(path):
            file = path == mod.MANIFEST
            return SimpleNamespace(st_mode=((stat.S_IFREG | 0o600) if file else
                                             (stat.S_IFDIR | 0o700)),
                                   st_uid=0, st_size=1024 if file else 0)

        with mock.patch.object(mod.os, 'geteuid', return_value=uid), \
             mock.patch.object(mod.socket, 'gethostname', return_value=host), \
             mock.patch.dict(mod.os.environ, {'SUDO_USER': sudo, **(docker_env or {})}, clear=True), \
             mock.patch.object(mod.Path, 'lstat', fake_lstat), \
             mock.patch.object(mod.Path, 'read_text', return_value=json.dumps(data)), \
             mock.patch.object(mod, 'docker', side_effect=fake_docker), \
             mock.patch.object(mod.socket, 'create_connection', side_effect=connect), \
             contextlib.redirect_stdout(io.StringIO()) as captured:
            try:
                mod.audit()
                ok = True
            except Exception:
                ok = False
        return ok, captured.getvalue(), docker_calls, network_calls, conn

    def test_valid_counts_restrict_commands_and_no_raw_data(self):
        ok, out, docker, network, conn = self.run_case()
        self.assertTrue(ok)
        self.assertIn('REDIS_DB0_TOTAL_KEYS=24', out)
        self.assertIn('REDIS_CONNECTED_CLIENTS_INCLUDING_AUDIT=2', out)
        self.assertIn('QUEUE_DEFAULT_PENDING_LIST=0', out)
        self.assertIn('UNKNOWN_QUEUES_NOT_INSPECTED=YES', out)
        self.assertIn('SNAPSHOT_ATOMIC=NO', out)
        self.assertEqual(network, [(('172.25.0.4', 6379), 5)])
        self.assertEqual(len(docker), 4)
        self.assertFalse(any(c[0] == 'exec' for c in docker))
        self.assertEqual(set(c[0] for c in conn.received),
                         {'TYPE', 'LLEN', 'ZCARD', 'SCARD', 'DBSIZE', 'INFO'})
        self.assertTrue(conn.closed)
        self.assertNotIn('172.25', out)
        self.assertNotIn('rq:queue:', out)

    def test_positive_counts_not_assumed_empty(self):
        ok, out, _, _, _ = self.run_case(values={
            ('LLEN', 'rq:queue:short'): 12,
            ('ZCARD', 'rq:failed:long'): 5,
            ('SCARD', 'rq:queues'): 7})
        self.assertTrue(ok)
        self.assertIn('QUEUE_SHORT_PENDING_LIST=12', out)
        self.assertIn('QUEUE_LONG_FAILED_REGISTRY=5', out)
        self.assertIn('RQ_REGISTERED_QUEUE_NAMES_COUNT=7', out)
        self.assertIn('UNKNOWN_QUEUES_NOT_INSPECTED=YES', out)

    def test_missing_key_explicit_absent_not_zero(self):
        ok, out, _, _, conn = self.run_case(values={('TYPE', 'rq:queue:short'): 'none'})
        self.assertTrue(ok)
        self.assertIn('QUEUE_SHORT_PENDING_LIST=ABSENT', out)
        self.assertNotIn(('LLEN', 'rq:queue:short'), conn.received)

    def test_unexpected_redis_type_rejected(self):
        ok, _, _, _, _ = self.run_case(values={('TYPE', 'rq:queue:default'): 'string'})
        self.assertFalse(ok)

    def test_auth_or_redis_errors_not_printed(self):
        secret = b'-NOAUTH do-not-print-secret\r\n'
        ok, out, _, _, _ = self.run_case(values={('DBSIZE',): secret})
        self.assertFalse(ok)
        self.assertNotIn('secret', out)

    def test_info_clients_does_not_leak_raw_data(self):
        payload = b'connected_clients:4\r\nSECRET_PAYLOAD=must-never-echo\r\n'
        ok, out, _, _, _ = self.run_case(values={('INFO', 'clients'): payload})
        self.assertTrue(ok)
        self.assertIn('CONNECTED_CLIENTS_INCLUDING_AUDIT=4', out)
        self.assertNotIn('SECRET', out)

    def test_info_clients_malformed_fails(self):
        ok, _, _, _, _ = self.run_case(values={('INFO', 'clients'): b'connected_clients:err\r\n'})
        self.assertFalse(ok)

    def test_socket_failure_fails_closed(self):
        ok, _, _, network, _ = self.run_case(socket_error=ConnectionRefusedError('private endpoint'))
        self.assertFalse(ok)
        self.assertEqual(len(network), 1)

    def test_wrong_host_user_euid_and_docker_override(self):
        for kw in ({'host': 'ccpcerp-old'}, {'sudo': 'gani'}, {'uid': 1000},
                   {'docker_env': {'DOCKER_HOST': 'tcp://127.0.0.1:2375'}}):
            with self.subTest(kw=kw):
                ok, _, calls, network, _ = self.run_case(**kw)
                self.assertFalse(ok)
                self.assertFalse(calls)
                self.assertFalse(network)

    def test_id_drift_prevents_network(self):
        def change(data, rows, names):
            rows[0]['Id'] = '0' * 64
        ok, _, _, network, _ = self.run_case(change)
        self.assertFalse(ok)
        self.assertFalse(network)

    def test_restart_policy_drift_prevents_network(self):
        def change(data, rows, names):
            rows[-1]['HostConfig']['RestartPolicy']['Name'] = 'unless-stopped'
        ok, _, _, network, _ = self.run_case(change)
        self.assertFalse(ok)
        self.assertFalse(network)

    def test_unexpected_container_prevents_network(self):
        def change(data, rows, names):
            names.add('rogue-redis')
        ok, _, _, network, _ = self.run_case(change)
        self.assertFalse(ok)
        self.assertFalse(network)

    def test_private_bridge_ip_required(self):
        def change(data, rows, names):
            redis = next(r for r in rows if r['Name'] == f'/{mod.PREFIX}-redis-queue-1')
            redis['NetworkSettings']['Networks'][data['network_name']]['IPAddress'] = '8.8.8.8'
        ok, _, _, network, _ = self.run_case(change)
        self.assertFalse(ok)
        self.assertFalse(network)

    def test_redis_network_id_mismatch_prevents_network(self):
        def change(data, rows, names):
            redis = next(r for r in rows if r['Name'] == f'/{mod.PREFIX}-redis-queue-1')
            redis['NetworkSettings']['Networks'][data['network_name']]['NetworkID'] = 'bad'
        ok, _, _, network, _ = self.run_case(change)
        self.assertFalse(ok)
        self.assertFalse(network)

    def test_unexpected_stopped_drill_backend(self):
        def change(data, rows, names):
            dr = next(r for r in rows if r['Name'] == '/' + mod.DRILL_FAILED)
            dr['State']['Running'] = True
        ok, _, _, network, _ = self.run_case(change)
        self.assertFalse(ok)
        self.assertFalse(network)

    def test_duplicate_manifest_ids_prevent_network(self):
        def change(data, rows, names):
            keys = list(data['container_ids'])
            data['container_ids'][keys[0]] = data['container_ids'][keys[1]]
        ok, _, _, network, _ = self.run_case(change)
        self.assertFalse(ok)
        self.assertFalse(network)

    def test_readonly_protocol_parses_resp3_unexpected_as_stop(self):
        # RESP3 map or error replies must never be silently accepted.
        conn = FakeConn()
        conn.pending = b'%0\r\n'
        with mock.patch.object(conn, 'sendall', return_value=None):
            with self.assertRaises(mod.Stop):
                mod.redis(conn, 'DBSIZE')

    def test_large_integer_rejected(self):
        with self.assertRaises(mod.Stop):
            mod._uint(b'9223372036854775808')

    def test_no_report_is_safe_recovery_verdict(self):
        ok, out, _, _, _ = self.run_case()
        self.assertTrue(ok)
        self.assertNotIn('NO_WRITES', out)
        self.assertNotIn('G1_ACTIVATION', out)
        self.assertNotIn('BACKEND_SAFE', out)


if __name__ == '__main__':
    unittest.main()
