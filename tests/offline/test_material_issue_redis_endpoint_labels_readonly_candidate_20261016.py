"""Credential-free, synthetic offline review; never invoke Docker or ERPNext."""
import ast
import contextlib
import io
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

SCRIPT = (Path(__file__).resolve().parents[2] / 'scripts/development/operator' /
          'ccpc_material_issue_redis_endpoint_labels_readonly_candidate_20261016.sh')


class LabelsV1OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sh = SCRIPT.read_text()
        cls.assertions = ('<<\'PYTHON\'\n', '\nPYTHON\n')
        assert cls.sh.count("<<'PYTHON'\n") == 1
        cls.py = cls.sh.split("<<'PYTHON'\n", 1)[1].rsplit('\nPYTHON\n', 1)[0]
        cls.tree = ast.parse(cls.py)
        cls.scope = {'__name__': 'test_import_without_main'}
        exec(compile(cls.tree, 'ccpc_labels_v1_embedded', 'exec'), cls.scope)

    @staticmethod
    def fixture(root, common=None, isolated=None, shared=None):
        (root / 'ccpc-integration2.localhost').mkdir()
        (root / 'development.localhost').mkdir()
        import json
        if common is None:
            common = {'redis_queue': 'redis://192.0.2.77:6379'}
        if isolated is None:
            isolated = {'redis_cache': 'redis://192.0.2.1:6379',
                        'redis_queue': 'redis://192.0.2.2:6379'}
        if shared is None:
            shared = {'redis_cache': 'redis://192.0.2.3:6379',
                      'redis_queue': 'redis://192.0.2.4:6379'}
        for path, value in ((root / 'common_site_config.json', common),
                            (root / 'ccpc-integration2.localhost/site_config.json', isolated),
                            (root / 'development.localhost/site_config.json', shared)):
            path.write_text(json.dumps(value), encoding='utf-8')

    def process(self, *, injection='', root=None):
        source = self.py
        if root is not None:
            needle = "SITES = Path('/workspace/development/frappe-bench/sites')"
            self.assertEqual(source.count(needle), 1)
            source = source.replace(needle, 'SITES = Path(' + repr(str(root)) + ')')
            injection = """
_saved_directory_check = checked_directory
def checked_directory(path):
    if str(path) in ('/workspace', '/workspace/development',
                     '/workspace/development/frappe-bench'):
        return None
    return _saved_directory_check(path)
""" + injection
        needle = "if __name__ == '__main__':"
        self.assertEqual(source.count(needle), 1)
        source = source.replace(needle, injection + '\n' + needle, 1)
        return subprocess.run([sys.executable, '-I', '-B', '-S', '-'], input=source,
                              capture_output=True, text=True, timeout=10,
                              env={'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1'})

    def function(self, name, *args):
        return self.scope[name](*args)

    def test_01_shell_syntax(self):
        p = subprocess.run(['bash', '-n', str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_02_default_shell_gate_blocks_before_docker(self):
        p = subprocess.run(['bash', str(SCRIPT)], capture_output=True, text=True,
                           env={'PATH': '/usr/bin:/bin'}, timeout=10)
        self.assertEqual(p.returncode, 1)
        self.assertIn('NOT AUTHORIZED', p.stderr)
        self.assertNotIn('docker:', p.stderr)

    def test_03_old_v2_approval_cannot_arm_new_candidate(self):
        p = subprocess.run(['bash', str(SCRIPT)], capture_output=True, text=True,
                           env={'PATH': '/usr/bin:/bin',
                                'CCPC_REDIS_SHAPE_V2_READONLY_APPROVED':
                                    'ccpc-redis-json-shape-v2-one-shot'}, timeout=10)
        self.assertEqual(p.returncode, 1)
        self.assertIn('NOT AUTHORIZED', p.stderr)

    def test_04_distinct_gate_and_fixed_development_identity(self):
        self.assertIn('CCPC_REDIS_LABELS_V1_APPROVED', self.sh)
        self.assertIn('ccpc-redis-labels-v1-one-shot', self.sh)
        self.assertLess(self.sh.index('CCPC_REDIS_LABELS_V1_APPROVED'),
                        self.sh.index('docker inspect'))
        self.assertLess(self.sh.index('frappe_docker_devcontainer|frappe|true'),
                        self.sh.index('docker exec'))
        self.assertIn("DEV_CONTAINER='frappe_docker_devcontainer-frappe-1'", self.sh)

    def test_05_no_network_frappe_redis_sql_or_docker_mutation(self):
        for absent in ('import frappe', 'import redis\n', 'import socket',
                       'import MySQLdb', '.connect(', 'getaddrinfo(',
                       '.commit(', '.publish(', '.ping(', 'set_value(',
                       'frappe.db.', 'docker compose', 'docker restart',
                       'docker cp', 'docker exec -u 0'):
            self.assertNotIn(absent, self.py if 'docker' not in absent else self.sh)

    def test_06_stdlib_allowlist(self):
        found = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                found.update(name.name.split('.')[0] for name in node.names)
            if isinstance(node, ast.ImportFrom):
                found.add(node.module.split('.')[0])
        self.assertEqual(found, {'ipaddress', 'json', 'os', 'stat', 'sys', 'pathlib', 'urllib'})

    def test_07_python_isolated_and_stderr_hidden(self):
        self.assertIn('PYTHONDONTWRITEBYTECODE=1 ./env/bin/python -I -B -S -', self.sh)
        self.assertIn('2>/dev/null', self.sh)
        self.assertIn('docker exec -i --user frappe', self.sh)
        self.assertNotIn('print(value)', self.py)

    def test_08_main_zero_exits_success(self):
        p = self.process(injection='def main():\n    print("SYNTHETIC_SUCCESS")\n    return 0\n')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, 'SYNTHETIC_SUCCESS\n')

    def test_09_main_one_exits_failure(self):
        p = self.process(injection='def main():\n    return 1\n')
        self.assertEqual(p.returncode, 1)
        self.assertEqual(p.stdout, '')

    def test_10_unexpected_exception_redacted(self):
        p = self.process(injection='def main():\n    raise RuntimeError("SECRET_NEVER_PRINT")\n')
        self.assertEqual(p.returncode, 1)
        self.assertEqual(p.stdout,
                         'CONFIGURED ENDPOINT LABELS: AMBIGUOUS_STOP; POSTING: NO-GO\n')
        self.assertNotIn('SECRET_NEVER_PRINT', p.stdout + p.stderr)

    def test_11_main_exit_outside_try_no_baseexception(self):
        node = self.tree.body[-1]
        self.assertIsInstance(node, ast.If)
        handlers = [h.type.id for stmt in ast.walk(node) if isinstance(stmt, ast.Try)
                    for h in stmt.handlers if isinstance(h.type, ast.Name)]
        self.assertEqual(handlers, ['Exception'])
        self.assertEqual(node.body[-1].value.func.attr, 'exit')

    def test_12_configured_distinct_ips_no_exact_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            p = self.process(root=root)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(p.stdout,
                'CONFIGURED ENDPOINT LABELS: NO_EXACT_LABEL_OVERLAP; ISOLATION: UNVERIFIED\n'
                'NODE/WORKER/PUBSUB/PHYSICAL: UNVERIFIED; POSTING: NO-GO\n')

    def test_13_isolated_cache_queue_collision_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.fixture(root, isolated={'redis_cache': 'redis://192.0.2.5:1234',
                                         'redis_queue': 'rediss://192.0.2.5:1234/9'})
            p=self.process(root=root)
            self.assertEqual(p.returncode,1)
            self.assertIn('OVERLAP_STOP',p.stdout)
            self.assertNotIn('192.0.2.5',p.stdout)

    def test_14_cross_site_role_mismatch_collides(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.fixture(root, shared={'redis_cache':'redis://192.0.2.4:6379',
                                       'redis_queue':'redis://192.0.2.1:6379'})
            p=self.process(root=root)
            self.assertEqual(p.returncode,1)
            self.assertIn('OVERLAP_STOP',p.stdout)

    def test_15_loopback_alias_equality(self):
        f=self.scope['opaque_endpoint']
        self.assertEqual(f('redis://localhost:6379'), f('redis://127.0.0.1:6379'))
        self.assertEqual(f('redis://[::1]:6379'), f('redis://localhost.localdomain:6379'))
        self.assertEqual(f('redis://[::ffff:127.0.0.1]:6379'),f('redis://localhost:6379'))

    def test_16_ip_normalization(self):
        f=self.scope['opaque_endpoint']
        self.assertEqual(f('rediss://[::ffff:192.0.2.42]:6380/5'),
                         f('redis://192.0.2.42:6380/0'))
        self.assertEqual(f('redis://[2001:0db8::0001]:6379'),
                         f('redis://[2001:db8::1]:6379'))

    def test_17_dns_case_trailing_dot_collapse(self):
        f=self.scope['opaque_endpoint']
        self.assertEqual(f('redis://Redis.Example.:6379'),
                         f('redis://redis.example:6379'))

    def test_18_distinct_dns_remains_ambiguous(self):
        self.assertEqual(self.function('compare_labels',
            {'redis_cache': ('dns:a',6379), 'redis_queue': ('dns:b',6379)},
            {'redis_cache': ('dns:c',6379), 'redis_queue': ('dns:d',6379)},
            ('dns:e',6379)), 'AMBIGUOUS_STOP')

    def test_19_node_dns_alone_is_ambiguous(self):
        self.assertEqual(self.function('compare_labels',
            {'redis_cache': ('ip:a', 1), 'redis_queue': ('ip:b', 1)},
            {'redis_cache': ('ip:c', 1), 'redis_queue': ('ip:d', 1)},
            ('dns:queue', 6379)), 'AMBIGUOUS_STOP')

    def test_20_normalized_dns_collision_stops(self):
        f=self.scope['opaque_endpoint']
        self.assertEqual(self.function('compare_labels',
            {'redis_cache': f('redis://redis-a:6379'), 'redis_queue': f('redis://redis-b:6379')},
            {'redis_cache': f('redis://redis-A.:6379'), 'redis_queue': f('redis://redis-c:6379')},
            f('redis://redis-b:6379')), 'OVERLAP_STOP')

    def test_21_python_env_override_last(self):
        eff=self.scope['python_effective']
        common={'redis_cache':'redis://192.0.2.1:1111', 'redis_queue':'redis://192.0.2.2:1111'}
        site={'redis_cache':'redis://192.0.2.3:1111'}
        env={'FRAPPE_REDIS_CACHE':'redis://192.0.2.9:1111'}
        self.assertEqual(eff(common,site,env)['redis_cache'], ('ip:192.0.2.9',1111))
        self.assertEqual(eff(common,site,{})['redis_cache'], ('ip:192.0.2.3',1111))
        self.assertEqual(eff(common,{}, {})['redis_cache'], ('ip:192.0.2.1',1111))

    def test_22_node_common_env_not_site(self):
        f=self.scope['node_queue_effective']
        common={'redis_queue':'redis://192.0.2.2:6379'}
        self.assertEqual(f(common,{}),('ip:192.0.2.2',6379))
        self.assertEqual(f(common,{'FRAPPE_REDIS_QUEUE':'redis://192.0.2.6:6380'}),
                         ('ip:192.0.2.6',6380))

    def test_23_node_without_common_env_is_unverifiable(self):
        with self.assertRaises(self.scope['Stop']):
            self.function('node_queue_effective', {},{})

    def test_24_reject_extra_config_from_any_site(self):
        f=self.scope['python_effective']
        for config in ({'extra_config': []}, {'extra_config':'some.hook'}):
            with self.assertRaises(self.scope['Stop']):
                f({},config,{})
            with self.assertRaises(self.scope['Stop']):
                f(config,{}, {})

    def test_25_reject_sentinel(self):
        f=self.scope['python_effective']
        with self.assertRaises(self.scope['Stop']):
            f({'redis_queue_sentinel_enabled': True}, {}, {})
        with self.assertRaises(self.scope['Stop']):
            self.function('node_queue_effective',{'redis_queue_sentinel_enabled':True}, {})

    def test_26_reject_malformed_URLs(self):
        f=self.scope['opaque_endpoint']
        bad=['', None, 0,'mysql://192.0.2.1:6379', 'redis://192.0.2.1',
             'redis://[invalid:6379', 'redis://192.0.2.1:99999',
             'redis://0.0.0.0:6379', 'redis://224.0.0.1:6379',
             'redis://[::]:6379', 'redis://[ff01::1]:6379',
             'redis://bad_host!:6379', 'redis://bad host:6379']
        for value in bad:
            with self.subTest(value=repr(value)), self.assertRaises(self.scope['Stop']):
                f(value)

    def test_27_username_password_db_tls_not_isolation(self):
        f=self.scope['opaque_endpoint']
        self.assertEqual(f('rediss://user:SECRET@192.0.2.9:6379/13'),
                         f('redis://192.0.2.9:6379/0'))

    def test_28_common_malformed_json_redacts_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.fixture(root)
            (root/'common_site_config.json').write_text('{"CREDENTIAL":"HUSH"')
            p=self.process(root=root)
            self.assertEqual(p.returncode,1)
            self.assertEqual(p.stdout,
                'CONFIGURED ENDPOINT LABELS: AMBIGUOUS_STOP; POSTING: NO-GO\n')
            self.assertNotIn('HUSH',p.stdout+p.stderr)

    def test_29_site_non_object_json_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.fixture(root)
            (root/'ccpc-integration2.localhost/site_config.json').write_text('[]')
            p=self.process(root=root)
            self.assertEqual(p.returncode,1)
            self.assertIn('AMBIGUOUS_STOP',p.stdout)

    def test_30_missing_file_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.fixture(root)
            (root/'development.localhost/site_config.json').unlink()
            p=self.process(root=root)
            self.assertEqual(p.returncode,1)
            self.assertIn('AMBIGUOUS_STOP',p.stdout)

    def test_31_symlink_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.fixture(root)
            target=root/'common_site_config.json'
            target.unlink()
            target.symlink_to(root/'development.localhost/site_config.json')
            p=self.process(root=root)
            self.assertEqual(p.returncode,1)
            self.assertIn('AMBIGUOUS_STOP',p.stdout)

    def test_32_oversized_file_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.fixture(root)
            (root/'common_site_config.json').write_bytes(b' ' * 65537)
            p=self.process(root=root)
            self.assertEqual(p.returncode,1)
            self.assertIn('AMBIGUOUS_STOP',p.stdout)

    def test_33_fifo_refused_without_hang(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.fixture(root)
            pth=root/'common_site_config.json'
            pth.unlink()
            os.mkfifo(pth)
            p=self.process(root=root)
            self.assertEqual(p.returncode,1)
            self.assertIn('AMBIGUOUS_STOP',p.stdout)

    def test_34_empty_node_common_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.fixture(root,common={})
            p=self.process(root=root)
            self.assertEqual(p.returncode,1)
            self.assertIn('AMBIGUOUS_STOP',p.stdout)

    def test_35_distinct_dns_full_process_ambiguous(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.fixture(root, isolated={'redis_cache': 'redis://cache-a:6379',
                                         'redis_queue':'redis://queue-a:6379'})
            p=self.process(root=root)
            self.assertEqual(p.returncode,1)
            self.assertIn('AMBIGUOUS_STOP',p.stdout)

    def test_36_restrict_file_paths_allowlist(self):
        for v in ('common_site_config.json','ccpc-integration2.localhost',
                  'development.localhost'):
            self.assertIn(v,self.py)
        for forbidden in ('/home/frappe/.ssh','/mnt/erpnext_backups',
                          'ccpcerp.local','production.localhost'):
            self.assertNotIn(forbidden,self.sh)

    def test_37_no_long_lived_worker_claim(self):
        self.assertIn('NODE/WORKER/PUBSUB/PHYSICAL: UNVERIFIED',self.sh)
        self.assertIn('ISOLATION: UNVERIFIED',self.sh)
        self.assertIn('POSTING: NO-GO',self.sh)

    def test_38_reject_unexpected_mapping_shape(self):
        with self.assertRaises(self.scope['Stop']):
            self.function('compare_labels', {},{},('ip:x',1))

    def test_39_unsafe_comparison_disjoint_ip_literals_still_no_isolation(self):
        f=self.scope['opaque_endpoint']
        iso={'redis_cache': f('redis://192.0.2.1:6379'), 'redis_queue': f('redis://192.0.2.2:6379')}
        shared={'redis_cache': f('redis://192.0.2.3:6379'),'redis_queue':f('redis://192.0.2.4:6379')}
        result=self.function('compare_labels',iso,shared,f('redis://192.0.2.5:6379'))
        self.assertEqual(result,'NO_EXACT_LABEL_OVERLAP')

    def test_40_readonly_paths_guard_against_stored_secrets(self):
        self.assertNotIn('print(common)',self.py)
        self.assertNotIn('print(env)',self.py)
        self.assertNotIn('print(isolated)',self.py)
        self.assertNotIn('print(shared)',self.py)
        self.assertNotIn('traceback.print',self.py)
        self.assertNotIn('logging.',self.py)


if __name__ == '__main__':
    unittest.main()
