"""Credential-free tests: examine source and run pure functions, NEVER Docker."""
import ast
import pathlib
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve()
SCRIPT = (HERE.parents[2] / 'scripts/development/operator'
          / 'ccpc_material_issue_redis_boundary_readonly_candidate_20261015.sh')


class RedisBoundaryCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = SCRIPT.read_text()
        assert cls.shell.count("<<'PYTHON'\n") == 1
        cls.embedded = cls.shell.split("<<'PYTHON'\n", 1)[1].rsplit("\nPYTHON\n", 1)[0]
        cls.ast = ast.parse(cls.embedded)
        scope = {'__name__': 'ccpc_offline_test'}  # Does NOT enter main().
        exec(compile(cls.ast, 'reviewed_embedded_script', 'exec'), scope)
        cls.fn = scope

    def test_01_shell_syntax(self):
        result = subprocess.run(['bash', '-n', str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_02_unapproved_shell_stops_before_docker(self):
        result = subprocess.run(['bash', str(SCRIPT)], capture_output=True, text=True,
                                env={'PATH': '/usr/bin:/bin'})
        self.assertEqual(result.returncode, 1)
        self.assertIn('NOT AUTHORIZED', result.stderr)
        self.assertNotIn('docker:', result.stderr)

    def test_03_approval_check_precedes_all_docker_calls(self):
        self.assertLess(self.shell.index('CCPC_REDIS_PREFLIGHT_READONLY_APPROVED'),
                        self.shell.index('docker inspect'))
        self.assertLess(self.shell.index('frappe_docker_devcontainer|frappe|true'),
                        self.shell.index('docker exec'))

    def test_04_only_one_documented_dev_container_target(self):
        self.assertIn("DEV_CONTAINER='frappe_docker_devcontainer-frappe-1'", self.shell)
        self.assertNotIn('frappe_docker-backend', self.shell)
        self.assertNotIn('ccpcerp.local', self.shell)
        self.assertNotIn('docker compose', self.shell)
        self.assertNotIn('docker restart', self.shell)

    def test_05_no_redis_frappe_mysql_or_network_library_imports(self):
        nodes = [node for node in ast.walk(self.ast)
                 if isinstance(node, (ast.Import, ast.ImportFrom))]
        imports = {(n.module.split('.')[0] if isinstance(n, ast.ImportFrom) else a.name.split('.')[0]) for n in nodes for a in n.names}
        self.assertEqual(imports, {'ipaddress', 'json', 'os', 'stat', 'sys', 'pathlib', 'urllib'})
        self.assertNotIn('import frappe', self.embedded)
        self.assertNotIn('import redis', self.embedded)
        self.assertNotIn('import MySQLdb', self.embedded)
        self.assertNotIn('subprocess', self.embedded)

    def test_06_effective_config_common_site_override(self):
        common = {'redis_cache': 'redis://common-cache:6379',
                  'redis_queue': 'redis://common-queue:6379'}
        site = {'redis_cache': 'rediss://site-cache:6380/1'}
        result = self.fn['effective'](common, site, {})
        self.assertEqual(result, {'cache': ('site-cache', 6380), 'queue': ('common-queue', 6379)})

    def test_07_common_environment_overrides_then_site_override(self):
        common = {'redis_cache': 'redis://common-cache:6379',
                  'redis_queue': 'redis://common-queue:6379'}
        env = {'FRAPPE_REDIS_CACHE': 'redis://env-cache:6379',
               'FRAPPE_REDIS_QUEUE': 'redis://env-queue:6380'}
        site = {'redis_queue': 'redis://site-queue:6381'}
        self.assertEqual(self.fn['effective'](common, site, env),
                         {'cache': ('env-cache', 6379), 'queue': ('site-queue', 6381)})

    def test_08_same_endpoint_with_different_db_tls_or_auth_is_overlap(self):
        value_a = self.fn['endpoint']('redis://u:p@service:6379/0')
        value_b = self.fn['endpoint']('rediss://SERVICE.:6379/9')
        self.assertEqual(value_a, value_b)

    def test_09_test_cache_queue_same_endpoint_is_no_go(self):
        test = {'cache': ('cache', 6379), 'queue': ('cache', 6379)}
        shared = {'cache': ('shared1', 6379), 'queue': ('shared2', 6379)}
        result = self.fn['classify'](test, shared)
        self.assertTrue(result['test_cache_queue_overlap'])
        self.assertFalse(result['rollback_or_posting_authorized'])

    def test_10_cross_site_cache_overlap_is_no_go(self):
        test = {'cache': ('cache', 6379), 'queue': ('queue', 6379)}
        shared = {'cache': ('cache', 6379), 'queue': ('other', 6379)}
        self.assertTrue(self.fn['classify'](test, shared)['test_shared_site_overlap'])

    def test_11_cross_site_cross_role_overlap_is_no_go(self):
        test = {'cache': ('cache', 6379), 'queue': ('queue', 6379)}
        shared = {'cache': ('queue', 6379), 'queue': ('other', 6379)}
        self.assertTrue(self.fn['classify'](test, shared)['test_shared_site_overlap'])

    def test_12_all_four_distinct_still_not_a_proof(self):
        test = {'cache': ('test-cache', 6379), 'queue': ('test-queue', 6379)}
        shared = {'cache': ('shared-cache', 6379), 'queue': ('shared-queue', 6379)}
        x = self.fn['classify'](test, shared)
        self.assertFalse(x['test_shared_site_overlap'])
        self.assertFalse(x['test_cache_queue_overlap'])
        for key in ('physical_redis_isolation_proven', 'redis_pubsub_isolation_proven',
                    'worker_process_endpoints_proven', 'rollback_or_posting_authorized'):
            self.assertFalse(x[key])

    def test_13_sentinal_configuration_fails_closed(self):
        with self.assertRaises(self.fn['Stop']):
            self.fn['effective']({'redis_cache_sentinel_enabled': True}, {}, {})

    def test_14_missing_or_bad_url_fails_closed(self):
        for value in ('', 'localhost:6379', 'redis://host', 'redis://host:99999',
                      'http://host:6379', 3, None):
            with self.subTest(value=value), self.assertRaises(self.fn['Stop']):
                self.fn['endpoint'](value)

    def test_15_config_input_types_fail_closed(self):
        with self.assertRaises(self.fn['Stop']):
            self.fn['effective']([], {}, {})
        with self.assertRaises(self.fn['Stop']):
            self.fn['classify']({'cache': ('x',1)}, {'cache': ('y',1)})

    def test_16_read_json_file_only_from_local_temporary_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'config.json'
            p.write_text('{"redis_cache":"redis://test:6379"}')
            self.assertEqual(self.fn['read_config'](p)['redis_cache'], 'redis://test:6379')

    def test_17_refuses_symlink_config(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'config.json'
            p.write_text('{}')
            link = pathlib.Path(d) / 'link.json'
            link.symlink_to(p)
            with self.assertRaises(self.fn['Stop']):
                self.fn['read_config'](link)

    def test_18_rejects_oversized_config(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'config.json'
            p.write_bytes(b'x' * 65537)
            with self.assertRaises(self.fn['Stop']):
                self.fn['read_config'](p)

    def test_20_localhost_aliases_share_conservative_endpoint_identity(self):
        urls = (
            'redis://localhost:6379/0', 'redis://LOCALHOST.:6379/2',
            'redis://localhost.localdomain:6379/4',
            'redis://127.0.0.1:6379', 'redis://127.5.0.1:6379',
            'redis://[::1]:6379', 'redis://[::ffff:127.0.0.1]:6379',
        )
        identifiers = {self.fn['endpoint'](url) for url in urls}
        self.assertEqual(len(identifiers), 1)

    def test_21_localhost_cross_site_different_alias_must_stop(self):
        test = {'cache': self.fn['endpoint']('redis://localhost:6379'),
                'queue': self.fn['endpoint']('redis://queue:6379')}
        shared = {'cache': self.fn['endpoint']('redis://127.0.0.1:6379'),
                  'queue': self.fn['endpoint']('redis://shared:6379')}
        report = self.fn['classify'](test, shared)
        self.assertTrue(report['test_shared_site_overlap'])
        self.assertFalse(report['rollback_or_posting_authorized'])

    def test_22_unspecified_and_multicast_ip_fail_closed(self):
        for url in ('redis://0.0.0.0:6379', 'redis://[::]:6379',
                    'redis://224.0.0.1:6379', 'redis://[ff01::1]:6379'):
            with self.subTest(url=url), self.assertRaises(self.fn['Stop']):
                self.fn['endpoint'](url)

    def test_23_nonloopback_names_still_not_physical_isolation(self):
        test = {'cache': self.fn['endpoint']('redis://cache1:6379'),
                'queue': self.fn['endpoint']('redis://queue1:6379')}
        shared = {'cache': self.fn['endpoint']('redis://cache2:6379'),
                  'queue': self.fn['endpoint']('redis://queue2:6379')}
        report = self.fn['classify'](test, shared)
        self.assertFalse(report['physical_redis_isolation_proven'])
        self.assertFalse(report['worker_process_endpoints_proven'])
        self.assertFalse(report['rollback_or_posting_authorized'])

    def test_19_no_external_connection_ever_claimed(self):
        for forbidden in ('connect(', 'ping(', 'publish(', 'getaddrinfo(',
                          'socket.', '.commit(', 'flushall(', 'frappe.init('):
            self.assertNotIn(forbidden, self.embedded)
        self.assertIn('CONFIGURATION CHECK COMPLETED; WRITE/ROLLBACK/COMMIT: NO-GO', self.embedded)


if __name__ == '__main__':
    unittest.main()
