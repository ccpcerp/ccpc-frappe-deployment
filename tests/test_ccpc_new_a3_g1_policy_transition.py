"""Synthetic-only NEW A3 policy transition tests. No Docker/host access."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest import mock

SOURCE = (Path(__file__).resolve().parents[1] / 'scripts' /
          'ccpc_new_a3_g1_policy_transition.py')
spec = importlib.util.spec_from_file_location('ccpc_policy_transition', SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture():
    ids = {name: f'{i:064x}' for i, name in enumerate(sorted(mod.EXPECTED), 1)}
    data = dict(schema=1, container_ids=ids, network_name='ccpc_prod_erpnext_default',
                network_id='b' * 64, app_image_id='sha256:' + 'a' * 64,
                frontend_ipv4='172.20.0.7')
    rows = {}
    for name in sorted(mod.EXPECTED):
        role = name.removeprefix(mod.PREFIX + '-')
        is_candidate = name in mod.CANDIDATES
        mounts = []
        if role in ('backend-1', 'frontend-1', 'websocket-1') and is_candidate:
            mounts = [dict(Type='volume', Destination=mod.SITES, Name=mod.PREFIX + '_sites'),
                      dict(Type='volume', Destination=mod.LOGS, Name=mod.PREFIX + '_logs')]
        elif role == 'db-1' and is_candidate:
            mounts = [dict(Type='volume', Destination='/var/lib/mysql', Name=mod.PREFIX + '_db-data')]
        elif role == 'redis-queue-1' and is_candidate:
            mounts = [dict(Type='volume', Destination='/data', Name=mod.PREFIX + '_redis-queue-data')]
        rows[name] = dict(Name='/' + name, Id=ids[name], Image=data['app_image_id'],
                          State=dict(Running=name != mod.DRILL_FAILED,
                                     ExitCode=1 if name == mod.DRILL_FAILED else 0,
                                     Health=dict(Status='healthy')),
                          HostConfig=dict(RestartPolicy=dict(Name='no'), PortBindings={}),
                          NetworkSettings=dict(Networks={data['network_name']: {
                              'NetworkID': data['network_id'],
                              'IPAddress': data['frontend_ipv4'] if role == 'frontend-1' else '172.20.0.3'}}
                              if is_candidate else {}, Ports={}),
                          Mounts=mounts)
    return data, rows


class FakeDocker:
    def __init__(self, data, rows):
        self.data, self.rows = data, rows
        self.calls = []
        self.fail_update_number = None
        self.updates = []
        self.after_update = None

    def __call__(self, *args):
        self.calls.append(args)
        if args[0] == 'ps':
            return '\n'.join(sorted(self.rows)) + '\n'
        if args[:2] == ('container', 'inspect'):
            return json.dumps(list(self.rows.values()))
        if args[:2] == ('network', 'inspect'):
            return json.dumps([{'Name': self.data['network_name'],
                                'Id': self.data['network_id'], 'Internal': True,
                                'Containers': {self.data['container_ids'][k]: {} for k in mod.CANDIDATES}}])
        if args[0] == 'update':
            self.updates.append(args)
            if self.fail_update_number == len(self.updates):
                raise mod.Stop()
            assert args[1] in ('--restart=unless-stopped', '--restart=no')
            assert len(args) == 3 and args[2] in self.data['container_ids'].values()
            name = next(n for n, v in self.data['container_ids'].items() if v == args[2])
            self.rows[name]['HostConfig']['RestartPolicy']['Name'] = args[1].split('=', 1)[1]
            if self.after_update:
                self.after_update(self, name)
            return ''
        raise AssertionError('Unexpected Docker command: ' + repr(args))


class PolicyTransitionTests(unittest.TestCase):
    def setUp(self):
        self.data, self.rows = fixture()
        self.fake = FakeDocker(self.data, self.rows)

    def run_main(self, mode):
        # Exercise transition logic only inside the mock: production source
        # retains the False interlock, and --check works with it locked.
        with mock.patch.object(mod, 'G1_POLICY_MUTATION_REVIEWED', mode != '--check'), \
             mock.patch.object(mod, 'operator'), mock.patch.object(mod, 'manifest', return_value=self.data), \
             mock.patch.object(mod, 'call', side_effect=self.fake), \
             contextlib.redirect_stdout(io.StringIO()) as buf:
            code = mod.main([mode])
        return code, buf.getvalue()


    def test_mutating_modes_locked_before_any_host_or_docker_access(self):
        self.assertFalse(mod.G1_POLICY_MUTATION_REVIEWED)
        for mode in ('--apply', '--compensate'):
            with self.subTest(mode=mode):
                with mock.patch.object(mod, 'operator') as operator, \
                     mock.patch.object(mod, 'manifest') as manifest, \
                     mock.patch.object(mod, 'call') as docker, \
                     contextlib.redirect_stdout(io.StringIO()) as buf:
                    rc = mod.main([mode])
                self.assertEqual(rc, 1)
                self.assertEqual(buf.getvalue().strip(),
                                 'CCPC_NEW_A3_G1_POLICY_STOP_REVIEW_REQUIRED')
                operator.assert_not_called()
                manifest.assert_not_called()
                docker.assert_not_called()
        self.assertFalse(mod.G1_POLICY_MUTATION_REVIEWED)

    def test_readonly_stays_allowed_without_policy_activation(self):
        self.assertFalse(mod.G1_POLICY_MUTATION_REVIEWED)
        rc, out = self.run_main('--check')
        self.assertEqual(rc, 0)
        self.assertIn('POLICY_READONLY_CHECK_PASS', out)
        self.assertFalse(self.fake.updates)

    def set_prefix(self, n):
        for name in mod.CANDIDATES[:n]:
            self.rows[name]['HostConfig']['RestartPolicy']['Name'] = 'unless-stopped'

    def test_readonly_clean_initial(self):
        rc, out = self.run_main('--check')
        self.assertEqual(rc, 0)
        self.assertIn('POLICY_READONLY_CHECK_PASS', out)
        self.assertEqual(self.fake.updates, [])

    def test_readonly_all_complete(self):
        self.set_prefix(6)
        rc, _ = self.run_main('--check')
        self.assertEqual(rc, 0)
        self.assertFalse(self.fake.updates)

    def test_apply_all_six_pinned_full_ids_ordered(self):
        rc, out = self.run_main('--apply')
        self.assertEqual(rc, 0)
        self.assertIn('POLICY_APPLY_COMPLETE', out)
        self.assertEqual([x[2] for x in self.fake.updates],
                         [self.data['container_ids'][k] for k in mod.CANDIDATES])
        self.assertTrue(all(x[1] == '--restart=unless-stopped' for x in self.fake.updates))
        self.assertEqual(out.count('POLICY_VERIFIED_CANDIDATE_COUNT='), 6)
        self.assertEqual(len(self.fake.updates), 6)

    def test_explicit_partial_compensation_only_applied(self):
        self.set_prefix(3)
        rc, out = self.run_main('--compensate')
        self.assertEqual(rc, 0)
        self.assertIn('POLICY_COMPENSATION_COMPLETE', out)
        self.assertEqual([x[2] for x in self.fake.updates],
                         [self.data['container_ids'][k] for k in reversed(mod.CANDIDATES[:3])])
        self.assertTrue(all(x[1] == '--restart=no' for x in self.fake.updates))

    def test_explicit_full_compensation(self):
        self.set_prefix(6)
        rc, _ = self.run_main('--compensate')
        self.assertEqual(rc, 0)
        self.assertEqual(len(self.fake.updates), 6)

    def test_compensation_fails_if_nothing_applied(self):
        rc, _ = self.run_main('--compensate')
        self.assertEqual(rc, 1)
        self.assertFalse(self.fake.updates)

    def test_apply_fails_on_existing_partial(self):
        self.set_prefix(2)
        rc, _ = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertFalse(self.fake.updates)

    def test_nonprefix_drift_blocks_compensation(self):
        name = mod.CANDIDATES[3]
        self.rows[name]['HostConfig']['RestartPolicy']['Name'] = 'unless-stopped'
        rc, _ = self.run_main('--compensate')
        self.assertEqual(rc, 1)
        self.assertFalse(self.fake.updates)

    def test_mid_update_error_stops_without_retry(self):
        self.fake.fail_update_number = 3
        rc, out = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertIn('POSSIBLE_PARTIAL_STOP_REVIEW_REQUIRED', out)
        self.assertEqual(len(self.fake.updates), 3)
        self.assertNotIn('APPLY_COMPLETE', out)

    def test_post_change_identity_drift_stops_no_further_updates(self):
        def inject(f, name):
            f.rows[name]['Id'] = '0' * 64
        self.fake.after_update = inject
        rc, out = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertEqual(len(self.fake.updates), 1)
        self.assertIn('POSSIBLE_PARTIAL_STOP_REVIEW_REQUIRED', out)

    def test_unexpected_container_blocks(self):
        self.rows['unexpected'] = {'Name': '/unexpected'}
        rc, _ = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertFalse(self.fake.updates)

    def test_non_candidate_policy_drift_blocks(self):
        self.rows[mod.OTHER[0]]['HostConfig']['RestartPolicy']['Name'] = 'always'
        rc, _ = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertFalse(self.fake.updates)

    def test_unexpected_stopped_rehearsal_blocks(self):
        self.rows[mod.DRILL_RUNNING[0]]['State']['Running'] = False
        rc, _ = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertFalse(self.fake.updates)

    def test_backend_image_drift_blocks(self):
        self.rows[mod.CANDIDATES[3]]['Image'] = 'sha256:' + '9' * 64
        rc, _ = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertFalse(self.fake.updates)

    def test_network_id_drift_blocks(self):
        self.rows[mod.CANDIDATES[0]]['NetworkSettings']['Networks'][self.data['network_name']]['NetworkID'] = 'e' * 64
        rc, _ = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertFalse(self.fake.updates)

    def test_wrong_db_health_blocks(self):
        self.rows[mod.CANDIDATES[0]]['State']['Health']['Status'] = 'unhealthy'
        rc, _ = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertFalse(self.fake.updates)

    def test_host_port_publish_blocks(self):
        self.rows[mod.CANDIDATES[5]]['HostConfig']['PortBindings'] = {'8080/tcp': [{'HostPort':'8080'}]}
        rc, _ = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertFalse(self.fake.updates)

    def test_noncandidate_exit_code_change_blocks(self):
        self.rows[mod.DRILL_FAILED]['State']['ExitCode'] = 0
        rc, _ = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertFalse(self.fake.updates)

    def test_no_raw_stdout_leak(self):
        self.rows[mod.CANDIDATES[0]]['HostConfig']['RestartPolicy']['Name'] = 'secret-value'
        rc, out = self.run_main('--apply')
        self.assertEqual(rc, 1)
        self.assertNotIn('secret-value', out)
        self.assertNotIn(self.data['container_ids'][mod.CANDIDATES[0]], out)

    def test_startup_mode_requires_explicit_choice(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                mod.main([])

    def test_source_no_exec_start_stop_recreation(self):
        content = SOURCE.read_text()
        for bad in ("call('start'", "call('stop'", "call('restart'", "call('run'", "call('create'", "call('rm'", "docker compose", "frappe.db"):
            self.assertNotIn(bad, content)

    def test_operator_checks_sudo_and_host(self):
        with mock.patch.object(mod.os, 'geteuid', return_value=0), \
             mock.patch.object(mod.socket, 'gethostname', return_value='ccpcerp-prod'), \
             mock.patch.dict(mod.os.environ, {'SUDO_USER':'ccpcadmin'}, clear=True):
            mod.operator()
        with mock.patch.object(mod.os, 'geteuid', return_value=0), \
             mock.patch.object(mod.socket, 'gethostname', return_value='ccpcerp-prod'), \
             mock.patch.dict(mod.os.environ, {'SUDO_USER':'anyone'}, clear=True):
            with self.assertRaises(mod.Stop):
                mod.operator()
        with mock.patch.object(mod.os, 'geteuid', return_value=0), \
             mock.patch.object(mod.socket, 'gethostname', return_value='ccpcerp-prod'), \
             mock.patch.dict(mod.os.environ, {'SUDO_USER':'ccpcadmin', 'DOCKER_HOST':'tcp://localhost'}, clear=True):
            with self.assertRaises(mod.Stop):
                mod.operator()


if __name__ == '__main__':
    unittest.main()
