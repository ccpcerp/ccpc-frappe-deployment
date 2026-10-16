"""Stage A synthetic offline tests. Never contact Docker, Redis, Frappe or PROD."""
import ast
import json
from pathlib import Path
import re
import os
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPT = (Path(__file__).resolve().parents[2] / 'scripts/development/operator' /
          'ccpc_material_issue_redis_dev_topology_stage_a_candidate_20261016.sh')
SOURCE = SCRIPT.read_text(encoding='utf-8')
PYTHON = SOURCE.split("<<'PYTHON'\n", 1)[1].rsplit('\nPYTHON\n', 1)[0]
TREE = ast.parse(PYTHON)
PROJECT = 'frappe_docker_devcontainer'
NETWORK = PROJECT + '_default'
ROLES = ('frappe', 'redis-cache', 'redis-queue')
IDS = dict(zip(ROLES, ('a' * 64, 'b' * 64, 'c' * 64)))
NET_ID = 'd' * 64


def jsonlines(role, **override):
    fields = [IDS[role], '/' + PROJECT + '-' + role + '-1', True, PROJECT,
              role, NETWORK, (NETWORK, NET_ID)]
    for index, value in override.items():
        fields[int(index)] = value
    return ('\n'.join(json.dumps(v) for v in fields[:6]) + '\n' +
            json.dumps(fields[6][0]) + ' ' + json.dumps(fields[6][1]) + '\n')


class OfflineStageATests(unittest.TestCase):
    def setUp(self):
        self.scope = {'__name__': 'offline_test_import'}
        exec(compile(TREE, '<reviewed_stage_a_embedded>', 'exec'), self.scope)
        self.inventory = dict(IDS)
        self.snapshots = {role: jsonlines(role) for role in ROLES}
        self.inspected = []
        self.calls = []

        def fake_read(args):
            self.calls.append(tuple(args))
            if args[0:2] == ('container', 'ls'):
                role = args[-3].rsplit('=', 1)[-1]
                value = self.inventory.get(role)
                if isinstance(value, Exception):
                    raise value
                return value if value is not None else ''
            if args[0:2] == ('inspect', '--type'):
                cid = args[-1]
                self.inspected.append(cid)
                role = next((r for r, i in IDS.items() if i == cid), None)
                result = self.snapshots.get(role, '')
                if isinstance(result, list):
                    return result.pop(0)
                if isinstance(result, Exception):
                    raise result
                return result
            raise AssertionError('unapproved Docker command')

        self.scope['docker_read'] = fake_read
        self.inventory = {k: v + '\n' for k, v in IDS.items()}

    def result(self):
        return self.scope['verify']()

    def check_stop(self, code):
        with self.assertRaises(self.scope['Stop']) as ctx:
            self.result()
        self.assertEqual(ctx.exception.category, code)

    def test_01_shell_and_python_parse(self):
        self.assertEqual(subprocess.run(['bash', '-n', str(SCRIPT)], capture_output=True).returncode, 0)
        self.assertIsInstance(TREE, ast.Module)

    def test_02_default_authorization_gate_blocks_before_docker(self):
        p = subprocess.run(['bash', str(SCRIPT)], capture_output=True, text=True,
                           env={'PATH': '/usr/bin:/bin'}, timeout=6)
        self.assertEqual(p.returncode, 1)
        self.assertEqual(p.stdout, 'STAGE_A_AUTHORIZATION_STOP\nDEV_PROD_SEPARATION_UNVERIFIED\nPOSTING_NO_GO\n')
        self.assertEqual(p.stderr, '')

    def test_03_consumed_approval_tokens_refused(self):
        for key, val in (
            ('CCPC_REDIS_LABELS_V1_APPROVED', 'ccpc-redis-labels-v1-one-shot'),
            ('CCPC_REDIS_SHAPE_V2_READONLY_APPROVED', 'ccpc-redis-json-shape-v2-one-shot'),
            ('CCPC_DEV_REDIS_TOPOLOGY_A_APPROVED', 'ccpc-redis-labels-v1-one-shot')):
            with self.subTest(key=key):
                p = subprocess.run(['bash', str(SCRIPT)], capture_output=True, text=True,
                                   env={'PATH': '/usr/bin:/bin', key: val}, timeout=6)
                self.assertEqual(p.returncode, 1)
                self.assertIn('STAGE_A_AUTHORIZATION_STOP', p.stdout)

    def test_04_fixed_operator_and_approval_precede_python_and_docker(self):
        self.assertLess(SOURCE.index('CCPC_DEV_REDIS_TOPOLOGY_A_APPROVED'),
                        SOURCE.index('command -v docker'))
        self.assertIn('id -un', SOURCE)
        self.assertIn("!= 'gani'", SOURCE)
        self.assertIn('python3 -I -B -S -', SOURCE)
        self.assertNotIn('set +e', SOURCE)

    def test_05_exact_docker_project_and_service_filter(self):
        self.assertEqual(self.result(), ('DEV_IDENTITY_OK', 'DEV_REDIS_ROLES_PRESENT',
                                         'DEV_NETWORK_METADATA_CHECKED'))
        self.assertEqual(len(self.calls), 9)
        for role, call in zip(ROLES, self.calls[:3]):
            self.assertEqual(call, ('container', 'ls', '-a', '--no-trunc',
                             '--filter', 'label=com.docker.compose.project=' + PROJECT,
                             '--filter', 'label=com.docker.compose.service=' + role,
                             '--format', '{{.ID}}'))
        self.assertEqual(len(self.inspected), 6)
        self.assertEqual(set(self.inspected), set(IDS.values()))
        self.assertTrue(all(x[:3] == ('inspect', '--type', 'container')
                            for x in self.calls[3:]))

    def test_06_no_broad_docker_network_or_prod_inspection(self):
        self.result()
        self.assertTrue(all(x[0] in ('container', 'inspect') for x in self.calls))
        self.assertNotIn('docker exec', SOURCE)
        self.assertNotIn('docker compose', SOURCE)
        for forbidden in ('network inspect', 'docker ps', 'docker cp', 'docker restart',
                          '.Config.Env', '.Mounts', '.Cmd', '.Ports', '.Containers',
                          '/proc/', 'frappe.db', 'redis-cli', 'socket.connect',
                          'getaddrinfo', 'publish(', 'redis.ping', 'bench --site',
                          'import frappe', 'import redis', 'subprocess.Popen',
                          'shell=True'):
            self.assertNotIn(forbidden, PYTHON)

    def test_07_stdlib_module_allowlist(self):
        modules = set()
        for node in ast.walk(TREE):
            if isinstance(node, ast.Import):
                modules.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                modules.add(node.module.split('.')[0])
        self.assertEqual(modules, {'json', 're', 'subprocess', 'sys'})

    def test_08_read_docker_captures_and_suppresses_raw_stderr(self):
        expected = self.scope['DOCKER'] + ('inspect', '--type', 'container', '--format',
                                          self.scope['FORMAT'], IDS['frappe'])
        completed = subprocess.CompletedProcess(expected, 0, stdout='HELLO_PRIVATE', stderr=None)
        with patch.object(subprocess, 'run', return_value=completed) as mock:
            self.assertEqual(self.scope['docker_read'].__class__.__name__, 'function')
            # Call original exact-source function, bypassing fixture replacement.
            inner = {'__name__': 'offline'}
            exec(compile(TREE, '<original>', 'exec'), inner)
            self.assertEqual(inner['docker_read'](expected[3:]), 'HELLO_PRIVATE')
            self.assertEqual(mock.call_args.args[0], expected)
            self.assertIs(mock.call_args.kwargs['stderr'], subprocess.DEVNULL)
            self.assertFalse(mock.call_args.kwargs['check'])
            self.assertEqual(mock.call_args.kwargs['timeout'], 10)

    def test_09_docker_errors_do_not_print_details(self):
        inner = {'__name__': 'offline'}
        exec(compile(TREE, '<original>', 'exec'), inner)
        for result in (subprocess.CompletedProcess((), 1, 'SECRET', None),
                       subprocess.CompletedProcess((), 0, 'X' * 4097, None)):
            with self.subTest(result=result.returncode, size=len(result.stdout)):
                with patch.object(subprocess, 'run', return_value=result):
                    with self.assertRaises(inner['Stop']) as ctx:
                        inner['docker_read'](('container', 'ls'))
                    self.assertEqual(ctx.exception.category, 'DEV_NETWORK_UNKNOWN_STOP')

    def test_10_missing_role(self):
        self.inventory['redis-cache'] = ''
        self.check_stop('DEV_ROLE_MISSING_STOP')

    def test_11_duplicate_role(self):
        self.inventory['redis-queue'] = IDS['redis-queue'] + '\n' + 'e' * 64 + '\n'
        self.check_stop('DEV_ROLE_AMBIGUOUS_STOP')

    def test_12_short_or_injected_id(self):
        for bad in ('abc\n', 'abc\nSECRET_PASSWORD\n', 'a' * 63 + '\n',
                    'A' * 64 + '\n', 'a' * 64 + '\r\n' + 'b' * 64 + '\n'):
            with self.subTest(bad=repr(bad[:8])):
                self.inventory['frappe'] = bad
                self.check_stop('DEV_ROLE_AMBIGUOUS_STOP')

    def test_13_same_id_for_multiple_roles(self):
        self.inventory['redis-cache'] = IDS['frappe'] + '\n'
        self.check_stop('DEV_ROLE_AMBIGUOUS_STOP')

    def test_14_wrong_inspected_id(self):
        self.snapshots['frappe'] = jsonlines('frappe', **{'0': 'f' * 64})
        self.check_stop('DEV_IDENTITY_STOP')

    def test_15_wrong_compose_project(self):
        self.snapshots['frappe'] = jsonlines('frappe', **{'3': 'production'})
        self.check_stop('DEV_IDENTITY_STOP')

    def test_16_wrong_service_label(self):
        self.snapshots['redis-cache'] = jsonlines('redis-cache', **{'4': 'redis-queue'})
        self.check_stop('DEV_IDENTITY_STOP')

    def test_17_wrong_name(self):
        self.snapshots['frappe'] = jsonlines('frappe', **{'1': '/prod-backend'})
        self.check_stop('DEV_IDENTITY_STOP')

    def test_18_stopped_and_nonboolean_state(self):
        for state, code in ((False, 'DEV_ROLE_STOPPED_STOP'),
                            ('true', 'DEV_ROLE_STOPPED_STOP'),
                            (None, 'DEV_ROLE_STOPPED_STOP')):
            with self.subTest(state=state):
                self.snapshots['frappe'] = jsonlines('frappe', **{'2': state})
                self.check_stop(code)

    def test_19_host_none_and_foreign_network_modes(self):
        for mode in ('host', 'none', 'container:peer', 'bridge', 'prod_default',
                     '', None, {'mode': 'host'}):
            with self.subTest(mode=mode):
                self.snapshots['frappe'] = jsonlines('frappe', **{'5': mode})
                self.check_stop('DEV_NETWORK_RISK_STOP')

    def test_20_wrong_network_name(self):
        self.snapshots['redis-cache'] = jsonlines('redis-cache', **{'6': ('foreign_default', NET_ID)})
        self.check_stop('DEV_NETWORK_RISK_STOP')

    def test_21_network_id_mismatch(self):
        self.snapshots['redis-queue'] = jsonlines('redis-queue', **{'6': (NETWORK, 'e' * 64)})
        self.check_stop('DEV_NETWORK_RISK_STOP')

    def test_22_invalid_network_id(self):
        self.snapshots['frappe'] = jsonlines('frappe', **{'6': (NETWORK, 'notanid')})
        self.check_stop('DEV_NETWORK_RISK_STOP')

    def test_23_empty_network_attachment(self):
        self.snapshots['frappe'] = jsonlines('frappe').rsplit('\n', 2)[0] + '\n'
        self.check_stop('DEV_NETWORK_UNKNOWN_STOP')

    def test_24_multiple_network_attachments(self):
        self.snapshots['frappe'] = jsonlines('frappe') + json.dumps('other_network') + ' ' + json.dumps('e' * 64) + '\n'
        self.check_stop('DEV_NETWORK_UNKNOWN_STOP')

    def test_25_malformed_docker_response(self):
        for raw in ('', '{"oops":"SECRET"}\n', 'not json\n' * 7,
                    jsonlines('frappe').replace('true', 'True')):
            with self.subTest(raw=raw[:20]):
                self.snapshots['frappe'] = raw
                self.check_stop('DEV_NETWORK_UNKNOWN_STOP')

    def test_25b_bad_utf8_escape_network_value_fails_closed(self):
        self.snapshots['frappe'] = jsonlines('frappe').replace(NET_ID, '\\ud800')
        self.check_stop('DEV_NETWORK_RISK_STOP')

    def test_25c_oversized_or_type_corrupt_network_value(self):
        for value in (None, [], 42, {'name': 'SECRET'}, 'e' * 6000):
            with self.subTest(value=str(value)[:12]):
                self.snapshots['frappe'] = jsonlines('frappe', **{'6': (NETWORK, value)})
                self.check_stop('DEV_NETWORK_RISK_STOP')

    def test_26_raw_extra_fields_refused(self):
        self.snapshots['redis-queue'] = jsonlines('redis-queue') + 'SECRET\n'
        self.check_stop('DEV_NETWORK_UNKNOWN_STOP')

    def test_27_unicode_and_terminal_escape_strings_refused(self):
        for name in ('/frappe\x1b[0m', '/\u202e', '/redis://pass@secret',
                     '/frappe\nPRODUCTION_OK', '/frappe\rOK'):
            with self.subTest(name=repr(name)):
                self.snapshots['frappe'] = jsonlines('frappe', **{'1': name})
                self.check_stop('DEV_IDENTITY_STOP')

    def test_28_first_second_snapshot_drift(self):
        first = jsonlines('frappe')
        second = jsonlines('frappe', **{'6': (NETWORK, 'e' * 64)})
        self.snapshots['frappe'] = [first, second]
        self.check_stop('DEV_RUNTIME_CHANGED_STOP')

    def test_29_partial_read_failure_cannot_pass(self):
        self.snapshots['redis-queue'] = RuntimeError('PASSWORD=NEVER_EXPOSE')
        with self.assertRaisesRegex(RuntimeError, 'NEVER_EXPOSE'):
            self.result()
        # Main wraps all accidental external errors as fixed UNKNOWN result.

    def test_30_fixed_safe_failure_and_exit_subprocess(self):
        injection = '''\ndef verify():\n    raise RuntimeError("PASSWORD=PRIVATE-NOT-PRINTABLE")\n'''
        src = PYTHON.replace("if __name__ == '__main__':", injection + "\nif __name__ == '__main__':")
        p = subprocess.run([sys.executable, '-I', '-B', '-S', '-'], input=src,
                           capture_output=True, text=True, timeout=6)
        self.assertEqual(p.returncode, 1)
        self.assertEqual(p.stderr, '')
        self.assertEqual(p.stdout, 'DEV_NETWORK_UNKNOWN_STOP\nNODE_ROUTE_UNVERIFIED\n'
                         'WORKER_ROUTE_UNVERIFIED\nDEV_PROD_SEPARATION_UNVERIFIED\nPOSTING_NO_GO\n')

    def test_31_fixed_safe_interruption_exit_subprocess(self):
        injection = '''\ndef verify():\n    raise KeyboardInterrupt()\n'''
        src = PYTHON.replace("if __name__ == '__main__':", injection + "\nif __name__ == '__main__':")
        p = subprocess.run([sys.executable, '-I', '-B', '-S', '-'], input=src,
                           capture_output=True, text=True, timeout=6)
        self.assertEqual(p.returncode, 1)
        self.assertEqual(p.stderr, '')
        self.assertEqual(p.stdout.count('POSTING_NO_GO'), 1)

    def test_32_successful_synthetic_process_only_has_safe_labels(self):
        fixture = {role: jsonlines(role) for role in ROLES}
        injection = '''\ndef docker_read(args):\n    import json as _json\n    ids = ''' + repr(IDS) + '''\n    data = ''' + repr(fixture) + '''\n    if args[0] == 'container':\n        role = args[-3].rsplit('=', 1)[-1]\n        return ids[role] + '\\n'\n    role = next(r for r, i in ids.items() if i == args[-1])\n    return data[role]\n'''
        src = PYTHON.replace("if __name__ == '__main__':", injection + "\nif __name__ == '__main__':")
        p = subprocess.run([sys.executable, '-I', '-B', '-S', '-'], input=src,
                           capture_output=True, text=True, timeout=6)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, 'DEV_IDENTITY_OK\nDEV_REDIS_ROLES_PRESENT\n'
                         'DEV_NETWORK_METADATA_CHECKED\nNODE_ROUTE_UNVERIFIED\n'
                         'WORKER_ROUTE_UNVERIFIED\nDEV_PROD_SEPARATION_UNVERIFIED\nPOSTING_NO_GO\n')

    def test_33_real_subprocess_never_invoked_in_mocked_verify(self):
        with patch.object(subprocess, 'run', side_effect=AssertionError('unmocked call')):
            self.assertEqual(self.result()[-1], 'DEV_NETWORK_METADATA_CHECKED')

    def test_34_release_and_process_gates_never_positive(self):
        self.assertNotIn('PRODUCTION_NOT_REACHABLE', PYTHON)
        self.assertNotIn('SAFE_TO_POST', PYTHON)
        self.assertNotIn('ISOLATED', PYTHON)
        self.assertIn("print('NODE_ROUTE_UNVERIFIED')", PYTHON)
        self.assertIn("print('WORKER_ROUTE_UNVERIFIED')", PYTHON)
        self.assertIn("print('DEV_PROD_SEPARATION_UNVERIFIED')", PYTHON)
        self.assertIn("print('POSTING_NO_GO')", PYTHON)

    def test_35_authorized_shell_with_fake_docker_end_to_end(self):
        # Own mock executables on PATH: real script, no Docker daemon accessed.
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            id_cmd = p / 'id'
            id_cmd.write_text('#!/bin/sh\ncase "$1" in -un) echo gani;; -u) echo 1234;; *) exit 1;; esac\n')
            id_cmd.chmod(0o700)
            docker_cmd = p / 'docker'
            fixture = {role: jsonlines(role) for role in ROLES}
            mock_code = ("#!/usr/bin/env python3\nimport sys\n" +
                         "ids = " + repr(IDS) + "\n" +
                         "data = " + repr(fixture) + "\n" +
                         "argv = sys.argv[1:]\n" +
                         "assert argv[:2] == ['--host', 'unix:///var/run/docker.sock']\n" +
                         "a = argv[2:]\n" +
                         "if a[:2] == ['container', 'ls']:\n" +
                         "    role = a[-3].rsplit('=', 1)[-1]\n" +
                         "    sys.stdout.write(ids[role] + '\\n')\n" +
                         "elif a[:3] == ['inspect', '--type', 'container']:\n" +
                         "    role = next(r for r,i in ids.items() if i == a[-1])\n" +
                         "    sys.stdout.write(data[role])\n" +
                         "else: sys.exit(19)\n")
            # Unescape only the intended mock code's newline string literal.
            mock_code = mock_code.replace("'\\n'", "'\\n'")
            docker_cmd.write_text(mock_code)
            docker_cmd.chmod(0o700)
            env = {'PATH': str(p) + ':/usr/bin:/bin',
                   'CCPC_DEV_REDIS_TOPOLOGY_A_APPROVED': 'ccpc-dev-redis-topology-a-one-shot'}
            run = subprocess.run(['bash', str(SCRIPT)], env=env,
                                 capture_output=True, text=True, timeout=20)
            self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
            self.assertEqual(run.stdout, 'DEV_IDENTITY_OK\nDEV_REDIS_ROLES_PRESENT\n'
                             'DEV_NETWORK_METADATA_CHECKED\nNODE_ROUTE_UNVERIFIED\n'
                             'WORKER_ROUTE_UNVERIFIED\nDEV_PROD_SEPARATION_UNVERIFIED\nPOSTING_NO_GO\n')
            self.assertEqual(run.stderr, '')

    def test_36_authorized_shell_rejects_wrong_operator_without_docker(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            i = p / 'id'
            i.write_text('#!/bin/sh\ncase "$1" in -un) echo other;; -u) echo 1234;; esac\n')
            i.chmod(0o700)
            # Must never attempt Docker if operator is wrong.
            env = {'PATH': str(p) + ':/usr/bin:/bin',
                   'CCPC_DEV_REDIS_TOPOLOGY_A_APPROVED': 'ccpc-dev-redis-topology-a-one-shot'}
            run = subprocess.run(['bash', str(SCRIPT)], env=env,
                                 capture_output=True, text=True, timeout=6)
            self.assertEqual(run.returncode, 1)
            self.assertEqual(run.stdout, 'STAGE_A_OPERATOR_STOP\nDEV_PROD_SEPARATION_UNVERIFIED\nPOSTING_NO_GO\n')
            self.assertEqual(run.stderr, '')

    def test_35_exit_is_outside_exception_catch(self):
        node = TREE.body[-1]
        self.assertIsInstance(node, ast.If)
        self.assertIsInstance(node.body[-1], ast.Expr)
        self.assertEqual(node.body[-1].value.func.attr, 'exit')


if __name__ == '__main__':
    unittest.main()
