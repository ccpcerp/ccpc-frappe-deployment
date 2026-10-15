"""Adversarial offline tests; never connect to Docker, Frappe, Redis, SQL or host sites."""
import ast
import contextlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = (Path(__file__).resolve().parents[2] / 'scripts/development/operator'
          / 'ccpc_material_issue_redis_json_shape_readonly_v2_20261016.sh')


class RedisJsonShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = SCRIPT.read_text()
        assert cls.shell.count("<<'PYTHON'\n") == 1
        cls.py = cls.shell.split("<<'PYTHON'\n", 1)[1].rsplit("\nPYTHON\n", 1)[0]
        cls.tree = ast.parse(cls.py)
        cls.scope = {'__name__': 'ccpc_offline_tests'}
        exec(compile(cls.tree, '<test_embedded_code>', 'exec'), cls.scope)

    def test_01_bash_syntax(self):
        r = subprocess.run(['bash', '-n', str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_02_unapproved_stops_before_any_docker(self):
        r = subprocess.run(['bash', str(SCRIPT)], capture_output=True,
                           text=True, env={'PATH': '/usr/bin:/bin'})
        self.assertEqual(r.returncode, 1)
        self.assertIn('NOT AUTHORIZED', r.stderr)
        self.assertNotIn('docker:', r.stderr)

    def test_03_distinct_new_guard_and_dev_only_container(self):
        self.assertIn('CCPC_REDIS_SHAPE_V2_READONLY_APPROVED', self.shell)
        self.assertNotIn('CCPC_REDIS_PREFLIGHT_READONLY_APPROVED', self.shell)
        self.assertLess(self.shell.index('CCPC_REDIS_SHAPE_V2_READONLY_APPROVED'),
                        self.shell.index('docker inspect'))
        self.assertLess(self.shell.index('frappe_docker_devcontainer|frappe|true'),
                        self.shell.index('docker exec'))
        self.assertIn("DEV_CONTAINER='frappe_docker_devcontainer-frappe-1'", self.shell)
        self.assertIn('docker exec -i --user frappe "$DEV_CONTAINER"', self.shell)

    def test_04_only_allowlisted_standard_lib_imports(self):
        mods = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                mods.update(a.name.split('.')[0] for a in node.names)
            if isinstance(node, ast.ImportFrom):
                mods.add(node.module.split('.')[0])
        self.assertEqual(mods, {'ipaddress', 'json', 'os', 'stat', 'sys', 'pathlib', 'urllib'})
        for bad in ('import frappe', 'import redis', 'import MySQLdb', 'import subprocess',
                    'socket.', 'requests', 'connect(', 'publish(', 'flushall(', '.commit('):
            self.assertNotIn(bad, self.py)

    def test_05_no_redis_endpoint_comparison_or_secret_output(self):
        self.assertNotIn('classify(', self.py)
        self.assertNotIn('getaddrinfo', self.py)
        self.assertNotIn('print(value)', self.py)
        self.assertNotIn('print(conf)', self.py)
        self.assertNotIn('print(path)', self.py)
        self.assertNotIn('print(error)', self.py)
        self.assertIn('ENDPOINTS/ISOLATION: UNVERIFIED', self.py)
        self.assertIn('POSTING: NO-GO', self.py)

    def test_06_python_safe_flags(self):
        self.assertIn('PYTHONDONTWRITEBYTECODE=1 ./env/bin/python -I -B -S -', self.shell)
        self.assertIn('2>/dev/null', self.shell)
        for bad in ('docker restart', 'docker compose up', 'docker compose down',
                    'docker stop', 'docker cp', 'bench --site'):
            self.assertNotIn(bad, self.shell)

    def test_07_effective_override_site_then_environment_final(self):
        common = {'redis_cache': 'redis://common:6379', 'redis_queue': 'redis://queue:6379'}
        site = {'redis_cache': 'not-a-redis-url'}
        env = {'FRAPPE_REDIS_CACHE': 'redis://override:6379'}
        self.assertTrue(self.scope['effective_format'](common, site, env))
        with self.assertRaises(self.scope['Stop']):
            self.scope['effective_format'](common, site, {})

    def test_08_site_only_override_and_defaults(self):
        self.assertTrue(self.scope['effective_format']({}, {}, {}))
        self.assertTrue(self.scope['effective_format']({}, {'redis_cache': 'rediss://site:6380'}, {}))
        with self.assertRaises(self.scope['Stop']):
            self.scope['effective_format']({}, {'redis_queue': 'not-a-url'}, {})

    def test_09_site_sentinel_fail_closed(self):
        for source in ({'redis_cache_sentinel_enabled': True},
                       {'redis_queue_sentinel_enabled': True}):
            with self.assertRaises(self.scope['Stop']):
                self.scope['effective_format']({}, source, {})

    def test_10_sentinel_common_can_be_overridden_by_site_false(self):
        self.assertTrue(self.scope['effective_format'](
            {'redis_cache_sentinel_enabled': True},
            {'redis_cache_sentinel_enabled': False}, {}))

    def test_11_invalid_shapes_fail_closed(self):
        for values in (([], {}, {}), ({}, [], {}), ({}, {}, [])):
            with self.assertRaises(self.scope['Stop']):
                self.scope['effective_format'](*values)

    def test_12_accepts_credentials_tls_without_printing_them(self):
        self.assertTrue(self.scope['redis_url_format']('rediss://user:topsecret@example:6380/1'))

    def test_13_malformed_redis_urls_fail_closed(self):
        bad = (None, 1, '', 'http://example:6379', 'redis://example',
               'redis://example:99999', 'redis://example:0', 'redis://:6379',
               'redis://example:bad', 'redis://[broken:6379',
               'redis://0.0.0.0:6379', 'redis://[::]:6379',
               'redis://224.0.0.1:6379', 'redis://[ff01::1]:6379',
               'redis://example name:6379', 'redis://test:6379' + 'x' * 2050)
        for url in bad:
            with self.subTest(url=str(url)[:28]), self.assertRaises(self.scope['Stop']):
                self.scope['redis_url_format'](url)

    def test_14_normal_url_formats(self):
        for u in ('redis://cache:6379', 'rediss://cache:6380/2',
                  'redis://localhost:6379', 'redis://[::1]:6379'):
            self.assertTrue(self.scope['redis_url_format'](u))

    @contextlib.contextmanager
    def fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_sites = self.scope['SITES']
            old_check = self.scope['checked_directory']
            self.scope['SITES'] = root
            self.scope['checked_directory'] = lambda p: (
                None if str(p).startswith('/workspace') else old_check(p))
            try:
                for name in ('ccpc-integration2.localhost', 'development.localhost'):
                    (root / name).mkdir()
                (root / 'common_site_config.json').write_text('{}')
                (root / 'ccpc-integration2.localhost/site_config.json').write_text('{}')
                (root / 'development.localhost/site_config.json').write_text('{}')
                yield root
            finally:
                self.scope['SITES'] = old_sites
                self.scope['checked_directory'] = old_check

    def run_main(self):
        result = io.StringIO()
        with contextlib.redirect_stdout(result):
            status = self.scope['main']()
        return status, result.getvalue()

    def test_15_fixture_all_good_safe_stages(self):
        with self.fixture():
            code, output = self.run_main()
            self.assertEqual(code, 0)
            self.assertIn('COMMON: JSON_OK', output)
            self.assertIn('ISOLATED: JSON_OK', output)
            self.assertIn('SHARED: JSON_OK', output)
            self.assertIn('ISOLATED_REDIS: FORMAT_OK', output)
            self.assertIn('SHARED_REDIS: FORMAT_OK', output)
            self.assertIn('POSTING: NO-GO', output)

    def test_16_bad_common_json_redacted(self):
        with self.fixture() as root:
            secret = 'redis://user:real_secret@internal:6379'
            (root / 'common_site_config.json').write_text('{"secret":'+secret)
            status, output = self.run_main()
            self.assertEqual(status, 1)
            self.assertEqual(output, 'COMMON: JSON_STOP\nCONFIG SHAPE: STOP; POSTING: NO-GO\n')
            self.assertNotIn(secret, output)

    def test_17_non_dict_isolated_json_stops(self):
        with self.fixture() as root:
            (root / 'ccpc-integration2.localhost/site_config.json').write_text('[]')
            status, out = self.run_main()
            self.assertEqual(status, 1)
            self.assertIn('ISOLATED: JSON_STOP', out)
            self.assertNotIn('SHARED:', out)

    def test_18_invalid_shared_redis_does_not_print_secret(self):
        with self.fixture() as root:
            secret = 'redis://super_private@host:bad_port'
            (root / 'development.localhost/site_config.json').write_text(
                '{"redis_cache":"' + secret + '"}')
            code, out = self.run_main()
            self.assertEqual(code, 1)
            self.assertIn('SHARED_REDIS: FORMAT_STOP', out)
            self.assertNotIn(secret, out)
            self.assertNotIn('super_private', out)

    def test_19_symlink_file_rejected(self):
        with self.fixture() as root:
            link = root / 'common_site_config.json'
            link.unlink()
            link.symlink_to(root / 'development.localhost/site_config.json')
            status, out = self.run_main()
            self.assertEqual(status, 1)
            self.assertIn('COMMON: JSON_STOP', out)

    def test_20_symlink_site_directory_rejected(self):
        with self.fixture() as root:
            p = root / 'ccpc-integration2.localhost'
            p.rename(root / 'renamed')
            p.symlink_to(root / 'renamed', target_is_directory=True)
            code, out = self.run_main()
            self.assertEqual(code, 1)
            self.assertIn('ISOLATED: JSON_STOP', out)

    def test_21_oversize_json_rejected(self):
        with self.fixture() as root:
            (root / 'common_site_config.json').write_bytes(b' ' * 65537)
            code, out = self.run_main()
            self.assertEqual(code, 1)
            self.assertIn('COMMON: JSON_STOP', out)

    def test_22_non_utf8_json_rejected(self):
        with self.fixture() as root:
            (root / 'common_site_config.json').write_bytes(b'\xff\xfe')
            code, out = self.run_main()
            self.assertEqual(code, 1)
            self.assertIn('COMMON: JSON_STOP', out)

    def test_23_unexpected_fifo_rejected_without_blocking(self):
        with self.fixture() as root:
            p = root / 'common_site_config.json'
            p.unlink()
            os.mkfifo(p)
            code, out = self.run_main()
            self.assertEqual(code, 1)
            self.assertIn('COMMON: JSON_STOP', out)

    def test_24_read_config_local_valid_only(self):
        with self.fixture() as root:
            payload = '{"redis_cache":"rediss://name:secret@service:6379"}'
            (root / 'common_site_config.json').write_text(payload)
            result = self.scope['read_config'](root / 'common_site_config.json')
            self.assertEqual(result['redis_cache'], 'rediss://name:secret@service:6379')

    def test_25_no_original_boundary_script_or_endpoint_comparison(self):
        self.assertNotIn('ccpc_material_issue_redis_boundary_readonly_candidate_20261015.sh', self.shell)
        self.assertNotIn('test_shared_site_overlap', self.py)
        self.assertNotIn('physical_redis_isolation_proven', self.py)
        self.assertNotIn('REDIS CONFIGURATION ENDPOINT LABELS: NO EXACT OVERLAP', self.py)


class RedisJsonShapeV2ProcessTests(unittest.TestCase):
    """Execute real embedded entrypoint in isolated Python subprocesses."""

    @classmethod
    def setUpClass(cls):
        shell = SCRIPT.read_text()
        cls.code = shell.split("<<'PYTHON'\n", 1)[1].rsplit("\nPYTHON\n", 1)[0]
        ast.parse(cls.code)

    def process(self, injection, sites=None):
        import sys
        source = self.code
        if sites is not None:
            needle = "SITES = Path('/workspace/development/frappe-bench/sites')"
            assert source.count(needle) == 1
            source = source.replace(needle, 'SITES = Path(' + repr(str(sites)) + ')')
            injection = """
_original_check = checked_directory
def checked_directory(path):
    if str(path) in ('/workspace', '/workspace/development',
                     '/workspace/development/frappe-bench'):
        return None
    return _original_check(path)
""" + injection
        needle = "if __name__ == '__main__':"
        assert source.count(needle) == 1
        source = source.replace(needle, injection + '\n' + needle, 1)
        return subprocess.run([sys.executable, '-I', '-B', '-S', '-'],
                              input=source, capture_output=True, text=True,
                              env={'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1'},
                              timeout=10)

    @staticmethod
    def fixture(root):
        (root / 'ccpc-integration2.localhost').mkdir()
        (root / 'development.localhost').mkdir()
        for p in (root / 'common_site_config.json',
                  root / 'ccpc-integration2.localhost/site_config.json',
                  root / 'development.localhost/site_config.json'):
            p.write_text('{}')

    def test_26_subprocess_main_zero_is_clean_success(self):
        r = self.process('def main():\n    print("SYNTHETIC SUCCESS")\n    return 0\n')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'SYNTHETIC SUCCESS\n')

    def test_27_subprocess_main_one_is_failure(self):
        r = self.process('def main():\n    return 1\n')
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, '')

    def test_28_subprocess_unexpected_exception_is_redacted(self):
        r = self.process('def main():\n    raise ValueError("DONT_PRINT_SECRET")\n')
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, 'CONFIG SHAPE: STOP; POSTING: NO-GO\n')
        self.assertNotIn('DONT_PRINT_SECRET', r.stdout + r.stderr)

    def test_29_subprocess_real_main_good_synthetic_json(self):
        with tempfile.TemporaryDirectory() as path:
            root = pathlib.Path(path)
            self.fixture(root)
            r = self.process('', root)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout.count('JSON_OK'), 3)
            self.assertEqual(r.stdout.count('FORMAT_OK'), 2)
            self.assertIn('ENDPOINTS/ISOLATION: UNVERIFIED', r.stdout)
            self.assertNotIn('CONFIG SHAPE: STOP', r.stdout)

    def test_30_subprocess_real_main_invalid_json_failure(self):
        with tempfile.TemporaryDirectory() as path:
            root = pathlib.Path(path)
            self.fixture(root)
            (root / 'common_site_config.json').write_text('{"secret":"SECRET"')
            r = self.process('', root)
            self.assertEqual(r.returncode, 1)
            self.assertEqual(r.stdout, 'COMMON: JSON_STOP\nCONFIG SHAPE: STOP; POSTING: NO-GO\n')
            self.assertNotIn('SECRET', r.stdout + r.stderr)

    def test_31_subprocess_real_main_bad_redis_format_failure(self):
        with tempfile.TemporaryDirectory() as path:
            root = pathlib.Path(path)
            self.fixture(root)
            (root / 'ccpc-integration2.localhost/site_config.json').write_text(
                '{"redis_queue":"redis://user:PRIVATE@host:bad"}')
            r = self.process('', root)
            self.assertEqual(r.returncode, 1)
            self.assertIn('ISOLATED_REDIS: FORMAT_STOP', r.stdout)
            self.assertNotIn('PRIVATE', r.stdout + r.stderr)

    def test_32_exit_outside_except_exception(self):
        mod = ast.parse(self.code)
        entry = mod.body[-1]
        self.assertIsInstance(entry, ast.If)
        self.assertIsInstance(entry.body[-1], ast.Expr)
        exceptions = [h.type.id for n in ast.walk(entry) if isinstance(n, ast.Try)
                      for h in n.handlers if isinstance(h.type, ast.Name)]
        self.assertEqual(exceptions, ['Exception'])

    def test_33_old_approval_flag_does_not_arm_new_v2(self):
        r = subprocess.run(['bash', str(SCRIPT)], capture_output=True, text=True,
                           env={'PATH':'/usr/bin:/bin',
                                'CCPC_REDIS_SHAPE_READONLY_APPROVED':'ccpc-redis-json-shape-one-shot'},
                           timeout=10)
        self.assertEqual(r.returncode, 1)
        self.assertIn('NOT AUTHORIZED', r.stderr)
        self.assertNotIn('docker:', r.stderr)


if __name__ == '__main__':
    unittest.main()
