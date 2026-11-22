"""Offline-only synthetic tests; every Docker/host/file operation is mocked."""

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
from types import SimpleNamespace
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / 'scripts/ccpc_new_a3_g1_backend_process_readonly.py'
spec = importlib.util.spec_from_file_location('g1_backend_inventory', SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def scenario():
    ids = {name: hashlib.sha256(name.encode()).hexdigest() for name in mod.EXPECTED}
    image = 'sha256:' + 'a' * 64
    manifest = {'schema': 1, 'container_ids': ids, 'app_image_id': image,
                'network_name': 'ccpc_prod_erpnext_default'}
    rows = []
    for name in sorted(mod.EXPECTED):
        rows.append({'Name': '/' + name, 'Id': ids[name], 'Image': image,
                     'State': {'Running': name != mod.TEST_FAILED,
                               'ExitCode': 1 if name == mod.TEST_FAILED else 0},
                     'HostConfig': {'RestartPolicy': {'Name': 'no'}},
                     'NetworkSettings': {'Networks': {manifest['network_name']: {}}},
                     'Config': {'Entrypoint': ['/usr/bin/tini', '--'],
                                'Cmd': ['/home/frappe/frappe-bench/env/bin/gunicorn', 'frappe.app:application']},
                     'Path': '/usr/bin/tini', 'Args': ['--', 'gunicorn']})
    tables = {n: 'PID PPID COMMAND COMMAND\n101 1 gunicorn gunicorn frappe.app:application\n'
              for n in mod.CANDIDATES}
    return manifest, rows, tables


class BackendProcessInventoryTests(unittest.TestCase):
    def run_case(self, edit=None, *, host='ccpcerp-prod', sudo='ccpcadmin', root=0,
                 env=None):
        info, rows, tables = scenario()
        names = set(mod.EXPECTED)
        if edit:
            edit(info, rows, tables, names)
        def mock_lstat(path):
            is_file = path == mod.MANIFEST
            return SimpleNamespace(st_mode=(stat.S_IFREG | 0o600) if is_file else
                                   (stat.S_IFDIR | 0o700), st_uid=0,
                                   st_size=100 if is_file else 0)
        calls = []
        def fake_docker(*args):
            calls.append(args)
            if args[0] == 'ps':
                return '\n'.join(sorted(names)) + '\n'
            if args[:2] == ('container', 'inspect'):
                return json.dumps(rows)
            if args[0] == 'top':
                for name, id_ in info['container_ids'].items():
                    if args[1] == id_:
                        return tables[name]
            raise AssertionError('unexpected Docker command')
        with mock.patch.object(mod.os, 'geteuid', return_value=root), \
             mock.patch.object(mod.socket, 'gethostname', return_value=host), \
             mock.patch.dict(mod.os.environ, {'SUDO_USER': sudo, **(env or {})}, clear=True), \
             mock.patch.object(mod.Path, 'lstat', mock_lstat), \
             mock.patch.object(mod.Path, 'read_text', return_value=json.dumps(info)), \
             mock.patch.object(mod, 'docker', side_effect=fake_docker), \
             contextlib.redirect_stdout(io.StringIO()) as buf:
            try:
                mod.audit()
                ok = True
            except Exception:
                ok = False
            outputs = buf.getvalue()
        return ok, outputs, calls

    def test_valid_metadata_only_includes_counts_and_limitations(self):
        ok, out, calls = self.run_case()
        self.assertTrue(ok)
        self.assertIn('CANDIDATE_PROCESS_TABLES_6_PASS', out)
        self.assertIn('BACKEND_PROCESS_COUNT=1', out)
        self.assertIn('QUEUE_CONTENTS_NOT_INSPECTED=YES', out)
        self.assertIn('EXTERNAL_CONSUMERS_NOT_INSPECTED=YES', out)
        self.assertEqual(sum(c[0] == 'top' for c in calls), 6)
        self.assertFalse(any(c[0] == 'exec' for c in calls))
        self.assertNotIn('gunicorn', out)

    def test_detect_worker_in_process_argv_without_exposing_it(self):
        secret = 'SECRET_RECIPIENT_OR_TOKEN'
        def change(i, r, t, n):
            t[mod.CANDIDATES[3]] += f'102 1 python python -m frappe.utils.bench_helper bench worker --queue default --token {secret}\n'
        ok, out, _ = self.run_case(change)
        self.assertTrue(ok)
        self.assertIn('CANDIDATE_WORKER_SIGNATURE_COUNT=1', out)
        self.assertNotIn(secret, out)

    def test_detect_scheduler_in_process_argv(self):
        def change(i, r, t, n):
            t[mod.CANDIDATES[3]] += '102 1 python bench --site ccpcerp.local schedule\n'
        ok, out, _ = self.run_case(change)
        self.assertTrue(ok)
        self.assertIn('CANDIDATE_SCHEDULER_SIGNATURE_COUNT=1', out)

    def test_detect_startup_command_signature(self):
        def change(i, r, t, n):
            backend = next(x for x in r if x['Name'] == '/' + mod.CANDIDATES[3])
            backend['Config']['Cmd'] = ['bench', 'worker', '--queue', 'short']
        ok, out, _ = self.run_case(change)
        self.assertTrue(ok)
        self.assertIn('START_COMMAND_WORKER_SIGNATURE=YES', out)

    def test_identity_drift_prevents_all_top_calls(self):
        def change(i, r, t, n):
            r[0]['Id'] = '0' * 64
        ok, out, calls = self.run_case(change)
        self.assertFalse(ok)
        self.assertFalse(any(c[0] == 'top' for c in calls))

    def test_policy_drift_prevents_all_top_calls(self):
        def change(i, r, t, n):
            r[-1]['HostConfig']['RestartPolicy']['Name'] = 'unless-stopped'
        ok, out, calls = self.run_case(change)
        self.assertFalse(ok)
        self.assertFalse(any(c[0] == 'top' for c in calls))

    def test_external_or_extra_container_is_stop(self):
        def change(i, r, t, n):
            n.add('surprise-worker')
        ok, out, _ = self.run_case(change)
        self.assertFalse(ok)

    def test_unexpected_failed_backend_start_is_stop(self):
        def change(i, r, t, n):
            next(x for x in r if x['Name'] == '/' + mod.TEST_FAILED)['State']['Running'] = True
        ok, out, _ = self.run_case(change)
        self.assertFalse(ok)

    def test_bad_top_format_is_stop_and_never_printed(self):
        def change(i, r, t, n):
            t[mod.CANDIDATES[0]] = 'ID BAD HEAD\nraw secret content\n'
        ok, out, _ = self.run_case(change)
        self.assertFalse(ok)
        self.assertNotIn('raw secret', out)

    def test_top_empty_process_list_is_stop(self):
        def change(i, r, t, n):
            t[mod.CANDIDATES[0]] = 'PID PPID COMMAND COMMAND\n'
        ok, out, _ = self.run_case(change)
        self.assertFalse(ok)

    def test_wrong_host_operator_root_and_docker_env_stop(self):
        for kw in ({'host': 'old-host'}, {'sudo': 'gani'}, {'root': 1000},
                   {'env': {'DOCKER_HOST': 'tcp://example'}}):
            with self.subTest(kw=kw):
                ok, _, calls = self.run_case(**kw)
                self.assertFalse(ok)
                self.assertFalse(calls)

    def test_duplicate_ids_stop(self):
        def change(i, r, t, n):
            keys = list(i['container_ids'])
            i['container_ids'][keys[0]] = i['container_ids'][keys[1]]
        ok, out, calls = self.run_case(change)
        self.assertFalse(ok)
        self.assertFalse(calls)

    def test_manifest_missing_or_non_dict_stops(self):
        def change(i, r, t, n):
            i['schema'] = 2
        ok, out, calls = self.run_case(change)
        self.assertFalse(ok)
        self.assertFalse(calls)

    def test_parser_handles_ps_header_args(self):
        self.assertEqual(mod.process_table('PID PPID COMMAND ARGS\n123 1 nginx nginx -g daemon off;\n'),
                         [('nginx', 'nginx -g daemon off;')])

    def test_empty_or_unexpected_cmd_field_stops(self):
        def change(i, r, t, n):
            next(x for x in r if x['Name'] == '/' + mod.CANDIDATES[0])['Config']['Cmd'] = {'danger': 'dict'}
        ok, _, calls = self.run_case(change)
        self.assertFalse(ok)
        self.assertTrue(any(c[0] == 'top' for c in calls))


if __name__ == '__main__':
    unittest.main()
