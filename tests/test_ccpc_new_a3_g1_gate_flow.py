"""All mocked complete G1 gate flow tests; never use Docker or systemd.

Uses a fake R0 and fake safety module to exercise G1.main ordering/STOP.
The live activation lock is patched only within the isolated test process.
"""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import ccpc_new_a3_g1_boot_gate as g1


class FakeR0:
    class Stop(Exception):
        pass

    def __init__(self):
        self.reads = []

    def validate_manifest(self, value):
        return value

    def load_json_file(self, path, root_only=False):
        self.reads.append((str(path), root_only))
        return {'schema': 1}


class FakeSafety:
    class SafetyStop(Exception):
        pass

    def __init__(self):
        self.calls = []

    def deadline_guard(self, r0, deadline):
        self.calls.append(('deadline', deadline))
        return contextlib.nullcontext()

    def validate_gateway_config(self, r0):
        self.calls.append(('config', None))
        return True

    def validate_tcp_bindings(self, r0, *, gateway_state):
        self.calls.append(('bind', gateway_state))
        return True


class GateFlowTests(unittest.TestCase):
    def execute(self, *, mutating=False, fail_at=None, remaining=150):
        r0, safety = FakeR0(), FakeSafety()
        events = []
        def collector(*args):
            events.append('collect')
            if fail_at == 'collect':
                raise g1.Stop()
            return {'snapshot': True}
        def evaluator(*args, **kwargs):
            events.append('evaluate')
            if fail_at == 'evaluate':
                raise g1.Stop()
            return True
        def probe(*args):
            events.append('probe')
            if fail_at == 'probe':
                raise g1.Stop()
        def configuration(*args):
            safety.calls.append(('config', None))
            if fail_at == 'config':
                raise FakeSafety.SafetyStop()
            return True
        def bindings(*args, **kwargs):
            safety.calls.append(('bind', kwargs['gateway_state']))
            if fail_at == 'bind':
                raise FakeSafety.SafetyStop()
            return True
        def gateway(*args):
            events.append('gateway')
            if fail_at == 'gateway':
                raise g1.Stop()
        t = 100 if remaining >= 70 else 100 + 180 - remaining
        stdout = io.StringIO()
        with mock.patch.object(g1, 'get_r0', return_value=r0), \
             mock.patch.object(g1, 'get_safety', return_value=safety), \
             mock.patch.object(g1, 'check_host'), \
             mock.patch.object(g1, 'collect', side_effect=collector), \
             mock.patch.object(g1, 'evaluate', side_effect=evaluator), \
             mock.patch.object(g1, 'probe', side_effect=probe), \
             mock.patch.object(g1, 'start_gateway', side_effect=gateway), \
             mock.patch.object(safety, 'validate_gateway_config', side_effect=configuration), \
             mock.patch.object(safety, 'validate_tcp_bindings', side_effect=bindings), \
             mock.patch.object(g1.time, 'monotonic', side_effect=[100] + [t] * 50), \
             mock.patch.object(g1, 'G1_ACTIVATION_REVIEWED', True if mutating else False), \
             contextlib.redirect_stdout(stdout):
            mode = '--gate-once' if mutating else '--live-readonly'
            rc = g1.main(['--manifest', str(g1.MANIFEST_PATH), mode,
                          '--profile', 'postchange', '--gateway-state', 'cold'])
        return rc, stdout.getvalue(), events, safety.calls, r0.reads

    def test_live_readonly_checks_config_and_bind_without_start(self):
        rc, out, events, guards, reads = self.execute()
        self.assertEqual(rc, 0)
        self.assertEqual(events, ['collect', 'evaluate', 'probe', 'evaluate'])
        self.assertEqual([x[0] for x in guards], ['deadline', 'config', 'bind'])
        self.assertEqual(guards[-1], ('bind', 'cold'))
        self.assertIn('READONLY_PREFLIGHT_PASS', out)
        self.assertTrue(reads[0][1])

    def test_mutating_mode_still_locked_by_default(self):
        out = io.StringIO()
        with mock.patch.object(g1, 'get_r0') as imported, \
             contextlib.redirect_stdout(out):
            rc = g1.main(['--manifest', str(g1.MANIFEST_PATH),
                          '--gate-once', '--profile', 'postchange'])
        self.assertEqual(rc, 1)
        imported.assert_not_called()
        self.assertEqual(out.getvalue().strip(), 'CCPC_NEW_A3_G1_STOP_REVIEW_REQUIRED')
        self.assertFalse(g1.G1_ACTIVATION_REVIEWED)

    def test_config_failure_no_gateway_start(self):
        rc, out, events, guards, _ = self.execute(fail_at='config')
        self.assertEqual(rc, 1)
        self.assertNotIn('gateway', events)
        self.assertEqual(out.strip(), 'CCPC_NEW_A3_G1_STOP_REVIEW_REQUIRED')

    def test_listener_failure_no_gateway_start(self):
        rc, out, events, guards, _ = self.execute(fail_at='bind')
        self.assertEqual(rc, 1)
        self.assertNotIn('gateway', events)
        self.assertIn(('bind', 'cold'), guards)

    def test_mutating_gate_rechecks_just_before_start(self):
        rc, out, events, guards, _ = self.execute(mutating=True)
        self.assertEqual(rc, 0)
        self.assertEqual(events.count('collect'), 2)
        self.assertEqual(events.count('probe'), 2)
        self.assertEqual([x[0] for x in guards], [
            'deadline', 'config', 'bind', 'config', 'bind', 'bind'])
        self.assertEqual(guards[-1], ('bind', 'pilot'))
        self.assertEqual(events[-1], 'gateway')
        self.assertIn('GATEWAY_STARTED_PASS', out)

    def test_pre_start_deadline_reservation_blocks_start(self):
        rc, out, events, _, _ = self.execute(mutating=True, remaining=69)
        self.assertEqual(rc, 1)
        self.assertNotIn('gateway', events)
        self.assertEqual(out.strip(), 'CCPC_NEW_A3_G1_STOP_REVIEW_REQUIRED')

    def test_gateway_start_failure_no_false_pass(self):
        rc, out, events, _, _ = self.execute(mutating=True, fail_at='gateway')
        self.assertEqual(rc, 1)
        self.assertIn('gateway', events)
        self.assertNotIn('GATEWAY_STARTED_PASS', out)
        self.assertEqual(out.strip(), 'CCPC_NEW_A3_G1_STOP_REVIEW_REQUIRED')


if __name__ == '__main__':
    unittest.main()
