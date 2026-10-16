"""Stage A v2 fake-only offline review, NEVER invoke Docker or Frappe."""
import ast
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPT = (Path(__file__).resolve().parents[2] / 'scripts/development/operator' /
          'ccpc_material_issue_redis_dev_topology_stage_a_v2_reviewonly_20261016.sh')
SOURCE = SCRIPT.read_text(encoding='utf-8')
PYTHON = SOURCE.split("<<'PYTHON'\n", 1)[1].rsplit('\nPYTHON\n', 1)[0]
TREE = ast.parse(PYTHON)
PROJECT = 'frappe_docker_devcontainer'
NETWORK = PROJECT + '_default'
ROLES = ('frappe', 'redis-cache', 'redis-queue')
IDS = dict(zip(ROLES, ('a' * 64, 'b' * 64, 'c' * 64)))


def formatted(role, values=None):
    row = [IDS[role], PROJECT + '-' + role + '-1', 'running',
           NETWORK, PROJECT, role]
    if values:
        for index, value in values.items():
            row[index] = value
    return '\t'.join(json.dumps(v) for v in row) + '\n'


def proc(code, timeout=8):
    return subprocess.run([sys.executable, '-I', '-B', '-S', '-c', code],
                          capture_output=True, text=True, timeout=timeout)


class StageAV2Offline(unittest.TestCase):
    def setUp(self):
        self.scope = {'__name__': 'offline_not_main'}
        exec(compile(TREE, '<stage_a_v2_reviewonly>', 'exec'), self.scope)
        self.results = {r: formatted(r) for r in ROLES}
        self.calls = []

        def stub(argv):
            self.calls.append(argv)
            self.assertEqual(argv[0:4], ('/usr/bin/docker', '--host',
                                        'unix:///var/run/docker.sock', 'container'))
            self.assertEqual(argv[4:7], ('ls', '-a', '--no-trunc'))
            role = next(r for r in ROLES if 'label=com.docker.compose.service=' + r in argv)
            value = self.results[role]
            if isinstance(value, list):
                return value.pop(0)
            if isinstance(value, Exception):
                raise value
            return value
        self.scope['bounded_docker_read'] = stub

    def verify(self):
        return self.scope['verify']()

    def real_bounded_reader(self):
        # Independent unmodified function: fixture stub stays on mock verify path.
        scope = {'__name__': 'offline_reader_only'}
        exec(compile(TREE, '<stage_a_v2_bounded_reader>', 'exec'), scope)
        return scope['bounded_docker_read'], scope['Stop']

    def stop(self, category):
        with self.assertRaises(self.scope['Stop']) as got:
            self.verify()
        self.assertEqual(got.exception.category, category)

    def test_01_shell_and_python_parse(self):
        p = subprocess.run(['bash', '-n', str(SCRIPT)], capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIsInstance(TREE, ast.Module)

    def test_02_unapproved_script_exits_before_any_docker(self):
        p = subprocess.run(['bash', str(SCRIPT)], capture_output=True, text=True,
                           env={'PATH': '/usr/bin:/bin'}, timeout=5)
        self.assertEqual(p.returncode, 1)
        self.assertEqual(p.stderr, '')
        self.assertEqual(p.stdout, 'STAGE_A_V2_AUTHORIZATION_STOP\n'
                                      'DEV_PROD_SEPARATION_UNVERIFIED\nPOSTING_NO_GO\n')

    def test_03_old_tokens_cannot_authorize_new_script(self):
        for key, value in (('CCPC_DEV_REDIS_TOPOLOGY_A_APPROVED', 'ccpc-dev-redis-topology-a-one-shot'),
                           ('CCPC_REDIS_LABELS_V1_APPROVED', 'ccpc-redis-labels-v1-one-shot'),
                           ('CCPC_REDIS_SHAPE_V2_READONLY_APPROVED', 'ccpc-redis-json-shape-v2-one-shot'),
                           ('CCPC_DEV_TOPOLOGY_A_V2_APPROVED', 'ccpc-dev-topology-a-one-shot')):
            with self.subTest(key=key):
                p = subprocess.run(['bash', str(SCRIPT)], capture_output=True, text=True,
                                   env={key: value, 'PATH': '/usr/bin:/bin'}, timeout=5)
                self.assertEqual(p.returncode, 1)
                self.assertTrue(p.stdout.startswith('STAGE_A_V2_AUTHORIZATION_STOP\n'))

    def test_04_operator_and_executables_gated(self):
        self.assertLess(SOURCE.index('CCPC_DEV_TOPOLOGY_A_V2_APPROVED'),
                        SOURCE.index('/usr/bin/docker'))
        self.assertIn('"$(/usr/bin/id -un 2>/dev/null || :)" != \'gani\'', SOURCE)
        self.assertIn('/usr/bin/python3 -I -B -S -', SOURCE)
        self.assertNotIn('PATH=', SOURCE.split("<<'PYTHON'\n")[0])

    def test_05_only_docker_container_ls_no_inspect(self):
        self.assertNotIn('docker inspect', PYTHON)
        self.assertNotIn("'inspect'", PYTHON)
        for forbidden in ("'exec'", "'network'", "'compose'", ".Config.Env", ".Mounts",
                          ".Command", ".Ports", ".Containers", '/proc/', 'site_config',
                          'getaddrinfo', 'import frappe', 'import redis', 'redis-cli',
                          'docker restart', 'docker rm', 'shell=True'):
            self.assertNotIn(forbidden, PYTHON)
        self.assertIn("'container', 'ls', '-a', '--no-trunc'", PYTHON)

    def test_06_docker_documented_list_fields(self):
        self.assertEqual(self.scope['FMT'].count('{{json '), 6)
        for field in ('.ID', '.Names', '.State', '.Networks'):
            self.assertIn(field, self.scope['FMT'])
        self.assertEqual(self.scope['FMT'].count('.Label'), 2)
        self.assertNotIn('.HostConfig', self.scope['FMT'])

    def test_07_full_success_is_limited_claim(self):
        self.assertEqual(self.verify(), ('DEV_LABELLED_ROLES_OBSERVED', 'DEV_NETWORK_NAMES_OBSERVED'))
        self.assertEqual(len(self.calls), 6)
        self.assertEqual([t[-1] for t in self.calls], [self.scope['FMT']] * 6)
        for role, argv in zip(ROLES * 2, self.calls):
            self.assertEqual(argv[-2:], ('--format', self.scope['FMT']))
            self.assertIn('name=^/' + PROJECT + '-' + role + '-1$', argv)
            self.assertIn('label=com.docker.compose.project=' + PROJECT, argv)
            self.assertIn('label=com.docker.compose.service=' + role, argv)
            self.assertTrue(all(v in ('--host', 'unix:///var/run/docker.sock', '/usr/bin/docker',
                                      'container', 'ls', '-a', '--no-trunc', '--filter',
                                      'label=com.docker.compose.project=' + PROJECT,
                                      'label=com.docker.compose.service=' + role,
                                      'name=^/' + PROJECT + '-' + role + '-1$',
                                      '--format', self.scope['FMT']) for v in argv))

    def test_08_no_id_duplicate_across_roles(self):
        self.results['redis-cache'] = formatted('redis-cache', {0: IDS['frappe']})
        self.stop('DEV_ROLE_AMBIGUOUS_STOP')

    def test_09_missing(self):
        self.results['redis-queue'] = ''
        self.stop('DEV_ROLE_MISSING_STOP')

    def test_10_duplicate(self):
        self.results['frappe'] = formatted('frappe') * 2
        self.stop('DEV_ROLE_AMBIGUOUS_STOP')

    def test_11_mismatched_project(self):
        self.results['redis-queue'] = formatted('redis-queue', {4: 'production'})
        self.stop('DEV_LABEL_IDENTITY_STOP')

    def test_12_mismatched_service(self):
        self.results['redis-queue'] = formatted('redis-queue', {5: 'frappe'})
        self.stop('DEV_LABEL_IDENTITY_STOP')

    def test_13_bad_container_name(self):
        self.results['frappe'] = formatted('frappe', {1: 'prod-backend'})
        self.stop('DEV_LABEL_IDENTITY_STOP')

    def test_14_bad_ids(self):
        for bad in ('not-sha', 'a'*63, 'A'*64, 'g'*64, None, [], 123):
            with self.subTest(bad=str(bad)[:8]):
                self.results['frappe'] = formatted('frappe', {0: bad})
                self.stop('DEV_LABEL_IDENTITY_STOP')

    def test_15_stopped_or_unknown_state(self):
        for state in ('exited', 'paused', 'created', 'restarting', 'up', None, True):
            with self.subTest(state=state):
                self.results['frappe'] = formatted('frappe', {2: state})
                self.stop('DEV_ROLE_STOPPED_STOP' if isinstance(state, str) else 'DEV_LABEL_IDENTITY_STOP')

    def test_16_foreign_network(self):
        self.results['redis-cache'] = formatted('redis-cache', {3: 'production_default'})
        self.stop('DEV_NETWORK_RISK_STOP')

    def test_17_host_none_and_multi_network(self):
        for name in ('host', 'none', 'bridge', NETWORK + ',production_default', '', None, []):
            with self.subTest(name=str(name)):
                self.results['redis-cache'] = formatted('redis-cache', {3: name})
                self.stop('DEV_NETWORK_RISK_STOP' if isinstance(name, str) else 'DEV_LABEL_IDENTITY_STOP')

    def test_18_malformed_json_and_tabs(self):
        for raw in ('{\n', 'not-json\n', '"x"\n', formatted('frappe').replace('\t', ' ', 1),
                    formatted('frappe') + 'PRIVATE=NEVER\n', '\t'.join(('"x"',)*6)+'\n'):
            with self.subTest(raw=raw[:10]):
                self.results['frappe'] = raw
                with self.assertRaises(self.scope['Stop']):
                    self.verify()

    def test_19_control_chars_and_injection_never_pass(self):
        for attack in ('\x1b[0m', 'DEV_OK\nSECRET', '\rsecret', '\u202e',
                       'redis://:private@127.0.0.1', 'PRODUCTION_OK'):
            with self.subTest(attack=repr(attack)):
                self.results['frappe'] = formatted('frappe', {1: attack})
                self.stop('DEV_LABEL_IDENTITY_STOP')

    def test_20_snapshot_container_id_drift(self):
        self.results['frappe'] = [formatted('frappe'), formatted('frappe', {0: 'e'*64})]
        self.stop('DEV_RUNTIME_CHANGED_STOP')

    def test_21_snapshot_network_drift(self):
        self.results['redis-queue'] = [formatted('redis-queue'),
                                       formatted('redis-queue', {3: 'production_default'})]
        self.stop('DEV_NETWORK_RISK_STOP')

    def test_22_snapshot_roles_unchanged(self):
        self.assertEqual(self.verify()[0], 'DEV_LABELLED_ROLES_OBSERVED')

    def test_23_exact_status_vocab_and_safety(self):
        src = PYTHON.replace("if __name__ == '__main__':", "\ndef verify():\n    return ('DEV_LABELLED_ROLES_OBSERVED','DEV_NETWORK_NAMES_OBSERVED')\n\nif __name__ == '__main__':")
        p = proc(src)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout,
                         'DEV_LABELLED_ROLES_OBSERVED\nDEV_NETWORK_NAMES_OBSERVED\n'
                         'DEV_OBJECT_PROVENANCE_UNVERIFIED\nNODE_ROUTE_UNVERIFIED\n'
                         'WORKER_ROUTE_UNVERIFIED\nDEV_PROD_SEPARATION_UNVERIFIED\nPOSTING_NO_GO\n')
        self.assertEqual(p.stderr, '')

    def test_24_unexpected_secret_exception_redacted(self):
        src = PYTHON.replace("if __name__ == '__main__':",
                             "\ndef verify():\n    raise RuntimeError('PASSWORD=EXAMPLE_NEVER_PRINT')\n\nif __name__ == '__main__':")
        p = proc(src)
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertEqual(p.stderr, '')
        self.assertNotIn('PASSWORD', p.stdout)
        self.assertTrue(p.stdout.startswith('DEV_METADATA_UNKNOWN_STOP\n'))
        self.assertTrue(p.stdout.endswith('POSTING_NO_GO\n'))

    def test_25_keyboard_interrupt_redacted(self):
        src = PYTHON.replace("if __name__ == '__main__':",
                             "\ndef verify():\n    raise KeyboardInterrupt()\n\nif __name__ == '__main__':")
        p = proc(src)
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertEqual(p.stderr, '')
        self.assertTrue(p.stdout.startswith('DEV_METADATA_UNKNOWN_STOP\n'))

    def test_26_no_positive_isolation_or_release(self):
        for status in ('DEV_PROD_SEPARATION_VERIFIED', 'SAFE_TO_POST',
                       'PRODUCTION_NOT_REACHABLE', 'NODE_ROUTE_OK', 'WORKER_ROUTE_OK'):
            self.assertNotIn(status, PYTHON)
        self.assertIn("print('DEV_OBJECT_PROVENANCE_UNVERIFIED')", PYTHON)
        self.assertIn("print('POSTING_NO_GO')", PYTHON)

    def test_27_stdout_bytes_bounded_for_flooding_child(self):
        fn, Stop = self.real_bounded_reader()
        args = (sys.executable, '-u', '-c',
                'import sys; sys.stdout.buffer.write(b"SECRET"*400000); sys.stdout.flush()')
        with self.assertRaises(Stop) as caught:
            fn(args, deadline_seconds=3)
        self.assertEqual(caught.exception.category, 'DEV_METADATA_OVERSIZE_STOP')

    def test_28_hanging_child_bounded_by_deadline(self):
        fn, Stop = self.real_bounded_reader()
        args = (sys.executable, '-u', '-c', 'import time; time.sleep(3)')
        with self.assertRaises(Stop) as caught:
            fn(args, deadline_seconds=0.15)
        self.assertEqual(caught.exception.category, 'DEV_METADATA_UNKNOWN_STOP')

    def test_29_nonzero_child_output_is_not_pass(self):
        fn, Stop = self.real_bounded_reader()
        args = (sys.executable, '-u', '-c',
                'import sys; sys.stdout.write("PRIVATE");sys.exit(3)')
        with self.assertRaises(Stop) as caught:
            fn(args, deadline_seconds=2)
        self.assertEqual(caught.exception.category, 'DEV_METADATA_UNKNOWN_STOP')

    def test_30_bounded_exact_4096_and_4097(self):
        fn, Stop = self.real_bounded_reader()
        for size in (0, 4095, 4096, 4097):
            with self.subTest(size=size):
                args = (sys.executable, '-u', '-c',
                        f'import sys;sys.stdout.buffer.write(b"x"*{size})')
                if size <= 4096:
                    self.assertEqual(len(fn(args, deadline_seconds=2)), size)
                else:
                    with self.assertRaises(Stop) as caught:
                        fn(args, deadline_seconds=2)
                    self.assertEqual(caught.exception.category, 'DEV_METADATA_OVERSIZE_STOP')

    def test_31_valid_utf8_within_limit(self):
        fn, Stop = self.real_bounded_reader()
        args = (sys.executable, '-u', '-c', 'import sys;sys.stdout.buffer.write("é".encode())')
        self.assertEqual(fn(args, deadline_seconds=2), 'é')

    def test_32_invalid_utf8_refused_without_echo(self):
        fn, Stop = self.real_bounded_reader()
        args = (sys.executable, '-u', '-c', 'import sys;sys.stdout.buffer.write(b"\xff")')
        with self.assertRaises(Stop) as caught:
            fn(args, deadline_seconds=2)
        self.assertEqual(caught.exception.category, 'DEV_METADATA_UNKNOWN_STOP')

    def test_33_pipe_read_is_bounded_not_communicate(self):
        self.assertNotIn('.communicate(', PYTHON)
        self.assertNotIn('stdout=subprocess.PIPE, stderr=subprocess.PIPE', PYTHON)
        self.assertIn('os.read(child.stdout.fileno(), min(1024, MAX_STDOUT_BYTES + 1 - count))', PYTHON)
        self.assertIn('if count > MAX_STDOUT_BYTES:', PYTHON)
        self.assertIn('child.kill()', PYTHON)
        self.assertIn('child.wait(timeout=2)', PYTHON)
        self.assertEqual(self.scope['MAX_STDOUT_BYTES'], 4096)

    def test_34_exact_runtime_subprocess_restrictions(self):
        real = {'__name__': 'fake_import'}
        exec(compile(TREE, '<no_docker>', 'exec'), real)
        argv = (sys.executable, '-c', 'print(1)')
        with patch.object(subprocess, 'Popen', wraps=subprocess.Popen) as mock:
            result = real['bounded_docker_read'](argv, deadline_seconds=2)
        self.assertEqual(result, '1\n')
        kwargs = mock.call_args.kwargs
        self.assertIs(kwargs['stdin'], subprocess.DEVNULL)
        self.assertIs(kwargs['stderr'], subprocess.DEVNULL)
        self.assertTrue(kwargs['start_new_session'])
        self.assertTrue(kwargs['close_fds'])
        self.assertEqual(kwargs['env'], real['CLEAN_ENV'])

    def test_35_interpreter_and_docker_provenance_explicit(self):
        self.assertEqual(self.scope['DOCKER'], '/usr/bin/docker')
        self.assertNotIn('subprocess.run(', PYTHON)
        self.assertNotIn('os.environ.copy()', PYTHON)
        self.assertNotIn('shell=True', PYTHON)
        self.assertEqual(self.scope['CLEAN_ENV']['PATH'], '/usr/bin:/bin')

    def test_36_generated_raw_stdout_never_in_fixed_labels(self):
        self.results['frappe'] = formatted('frappe').replace(IDS['frappe'], 'private=ACCESS_TOKEN')
        with self.assertRaises(self.scope['Stop']) as caught:
            self.verify()
        self.assertEqual(caught.exception.category, 'DEV_LABEL_IDENTITY_STOP')

    def test_37_absent_label_rejected(self):
        self.results['frappe'] = formatted('frappe', {4: ''})
        self.stop('DEV_LABEL_IDENTITY_STOP')

    def test_38_network_foreign_does_not_trigger_other_docker_calls(self):
        self.results['redis-queue'] = formatted('redis-queue', {3: 'shared-proxy'})
        self.stop('DEV_NETWORK_RISK_STOP')
        self.assertLessEqual(len(self.calls), 3)

    def test_39_main_exit_outside_catches(self):
        statement = TREE.body[-1]
        self.assertIsInstance(statement, ast.If)
        self.assertIsInstance(statement.body[-1], ast.Expr)
        self.assertEqual(statement.body[-1].value.func.attr, 'exit')


if __name__ == '__main__':
    unittest.main()
