"""Offline only: exact-ID rollback planning negative paths, no Docker calls."""
from copy import deepcopy
from pathlib import Path
import hashlib
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import ccpc_new_a3_g1_policy_plan as p


def fixture():
    ids = {n: hashlib.sha256(n.encode()).hexdigest() for n in p.EXPECTED}
    rows = {n: {'id': ids[n], 'restart': 'no', 'running': n != p.TEST_FAILED,
                'exit': 1 if n == p.TEST_FAILED else 0} for n in p.EXPECTED}
    return {'container_ids': ids}, rows


class PlanTests(unittest.TestCase):
    def test_exact_six_update_intents(self):
        m, s = fixture()
        updates = p.plan_candidate_updates(m, s)
        self.assertEqual(len(updates), 6)
        self.assertEqual(tuple(ch.name for ch in updates), p.CANDIDATE)
        self.assertTrue(all(ch.pinned_id == m['container_ids'][ch.name]
                            and ch.before == 'no' and ch.after == 'unless-stopped'
                            for ch in updates))
        self.assertTrue(all(s[n]['restart'] == 'no' for n in p.EXPECTED))

    def test_applied_partial_compensation_reverses_exact_ids(self):
        m, s = fixture()
        applied = p.CANDIDATE[:3]
        for n in applied:
            s[n]['restart'] = 'unless-stopped'
        compensation = p.plan_partial_compensation(m, s, applied)
        self.assertEqual(tuple(ch.name for ch in compensation), tuple(reversed(applied)))
        self.assertTrue(all(ch.pinned_id == m['container_ids'][ch.name]
                            and ch.before == 'unless-stopped' and ch.after == 'no'
                            for ch in compensation))

    def test_no_op_compensation(self):
        m, s = fixture()
        self.assertEqual(p.plan_partial_compensation(m, s, ()), ())

    def test_missing_or_extra_protected_identity_rejected(self):
        m, s = fixture()
        s.pop(p.ORIGINAL[0])
        with self.assertRaises(p.PlanStop): p.plan_candidate_updates(m, s)
        m, s = fixture()
        s['rogue'] = {'id':'0'*64,'restart':'no','running':True}
        with self.assertRaises(p.PlanStop): p.plan_candidate_updates(m, s)

    def test_id_drift_rejected_even_non_candidate(self):
        m, s = fixture()
        s[p.ORIGINAL[0]]['id'] = '0'*64
        with self.assertRaises(p.PlanStop): p.plan_candidate_updates(m, s)

    def test_failed_drill_resumed_rejected(self):
        m, s = fixture()
        s[p.TEST_FAILED]['running'] = True
        with self.assertRaises(p.PlanStop): p.plan_candidate_updates(m, s)

    def test_noncandidate_policy_drift_rejected(self):
        m, s = fixture()
        s[p.ORIGINAL[0]]['restart'] = 'unless-stopped'
        with self.assertRaises(p.PlanStop): p.plan_candidate_updates(m, s)

    def test_candidate_already_enabled_prechange_rejected(self):
        m, s = fixture()
        s[p.CANDIDATE[0]]['restart'] = 'unless-stopped'
        with self.assertRaises(p.PlanStop): p.plan_candidate_updates(m, s)

    def test_unlisted_applied_container_rejected(self):
        m, s = fixture()
        with self.assertRaises(p.PlanStop): p.plan_partial_compensation(m, s, [p.ORIGINAL[0]])

    def test_duplicate_applied_container_rejected(self):
        m, s = fixture()
        with self.assertRaises(p.PlanStop): p.plan_partial_compensation(m, s, [p.CANDIDATE[0],p.CANDIDATE[0]])

    def test_unreported_policy_change_rejected_on_compensation(self):
        m, s = fixture()
        s[p.CANDIDATE[1]]['restart'] = 'unless-stopped'
        with self.assertRaises(p.PlanStop): p.plan_partial_compensation(m, s, [p.CANDIDATE[0]])

    def test_partial_applied_name_mismatch_rejected(self):
        m, s = fixture()
        with self.assertRaises(p.PlanStop): p.plan_partial_compensation(m, s, [p.CANDIDATE[0]])

    def test_malformed_manifest_and_ledger_rejected_cleanly(self):
        m, snap = fixture()
        m['container_ids'][p.CANDIDATE[0]] = []
        with self.assertRaises(p.PlanStop): p.plan_candidate_updates(m, snap)
        m, snap = fixture()
        with self.assertRaises(p.PlanStop): p.plan_partial_compensation(m, snap, [[p.CANDIDATE[0]]])

    def test_bad_manifest_duplicate_ids_rejected(self):
        m, s = fixture()
        m['container_ids'][p.CANDIDATE[1]]=m['container_ids'][p.CANDIDATE[0]]
        with self.assertRaises(p.PlanStop): p.plan_candidate_updates(m, s)


if __name__ == '__main__':
    unittest.main()
