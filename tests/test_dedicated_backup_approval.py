"""Synthetic Ed25519 tests. Test-only keys generated in memory; no live authority."""
from __future__ import annotations
import copy
import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone
from dataclasses import replace

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from scripts import dedicated_backup_approval as a
from scripts import dedicated_backup_policy as p


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')


class OfflineApprovalTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 23, 12, 0, tzinfo=timezone.utc)
        self.key = Ed25519PrivateKey.generate()  # disposable synthetic test key only
        pk = self.key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
        self.trust = a.TrustedApprovalAnchor(pk, 'security-reviewer-v1', 12, frozenset())
        self.manifest = {
            'schema_version': 1, 'release_id': 'ccpc-offline-synthetic-0001',
            'deployment_commit': '1'*40, 'frappe_sha':p.FRAPPE_SHA,
            'erpnext_sha':p.ERPNEXT_SHA, 'ccpc_sha':p.CCPC_SHA,
            'patch_sha256':p.PATCH_SHA256,'overlay_sha256':p.OVERLAY_SHA256,
            'host':p.HOST,'site':p.SITE,'profile':p.PROFILE,
            'compose_project':'ccpc-dedicated', 'backend_image_id':'sha256:'+'2'*64,
            'db_image_id':'sha256:'+'3'*64, 'backend_config_hash':'4'*64,
            'db_config_hash':'5'*64, 'sites_volume':'ccpc-dedicated_sites',
            'db_volume':'ccpc-dedicated_db-data',
            'backend_logs_volume':'ccpc-dedicated_logs',
        }
        self.approval = {
            'schema_version':1,'authority_id':a.AUTHORITY_ID,
            'key_id':'security-reviewer-v1','sequence':12,
            'issued_utc':'2026-10-23T11:59:00Z','expires_utc':'2026-10-23T12:05:00Z',
            'approval':{'release_id':self.manifest['release_id'],
                        'manifest_sha256':hashlib.sha256(encode(self.manifest)).hexdigest(),
                        'prepared_by':'builder-operator','approved_by':'release-reviewer',
                        'approved_utc':'2026-10-23T11:58:00Z','decision':'approved'},
            'revoked_release_ids':[],
        }

    def runverify(self, approval=None, *, manifest=None, trust=None, now=None, sign=True, sig=None):
        raw = encode(self.approval if approval is None else approval)
        signature = self.key.sign(a.DOMAIN + raw) if sign else sig
        return a.verify_signed_approval(
            encode(self.manifest if manifest is None else manifest), raw, signature,
            trust=self.trust if trust is None else trust,
            now_utc=self.now if now is None else now)

    def reject(self, **kwargs):
        with self.assertRaises(a.ApprovalRejected) as cm:
            self.runverify(**kwargs)
        self.assertNotIn(self.manifest['release_id'],str(cm.exception))

    def change(self, section=None, **changes):
        state=copy.deepcopy(self.approval)
        target=state if section is None else state[section]
        target.update(changes)
        return state

    def test_valid_signature_never_backup_authorizes(self):
        got=self.runverify()
        self.assertEqual(got.release.release_id, self.manifest['release_id'])
        self.assertEqual(got.approval_sequence,12)
        self.assertFalse(got.trust_source_authenticated)
        self.assertFalse(got.backup_ready)
        self.assertFalse(got.release.backup_ready)

    def test_changed_manifest(self):
        self.reject(manifest={**self.manifest,'db_image_id':'sha256:'+'6'*64})

    def test_changed_manifest_release_identity(self):
        self.reject(manifest={**self.manifest,'release_id':'ccpc-different-synthetic'})

    def test_missing_signature_and_invalid_signature_length(self):
        self.reject(sign=False,sig=None)
        self.reject(sign=False,sig=b'0'*63)

    def test_forged_signature_fails(self):
        self.reject(sign=False,sig=b'x'*64)

    def test_changed_signed_snapshot_fails(self):
        good_raw=encode(self.approval)
        signature=self.key.sign(a.DOMAIN + good_raw)
        with self.assertRaises(a.ApprovalRejected):
            a.verify_signed_approval(encode(self.manifest),good_raw.replace(b'"sequence":12',b'"sequence":13'),signature,
                                     trust=self.trust,now_utc=self.now)

    def test_wrong_signer_key_fails(self):
        other=Ed25519PrivateKey.generate()
        pk=other.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        self.reject(trust=replace(self.trust,public_key=pk))

    def test_revoked_key_rejected(self):
        self.reject(trust=replace(self.trust,revoked_key_ids=frozenset((self.trust.key_id,))))

    def test_revoked_release_rejected(self):
        self.reject(approval=self.change(revoked_release_ids=[self.manifest['release_id']]))

    def test_absent_revocation_list_rejected(self):
        state=copy.deepcopy(self.approval);state.pop('revoked_release_ids')
        self.reject(approval=state)

    def test_duplicate_revocations_rejected(self):
        self.reject(approval=self.change(revoked_release_ids=['ccpc-another-0001','ccpc-another-0001']))

    def test_old_sequence_rejected(self):
        self.reject(approval=self.change(sequence=11))

    def test_future_snapshot_rejected(self):
        self.reject(approval=self.change(issued_utc='2026-10-23T12:01:00Z'))

    def test_expired_snapshot_rejected(self):
        self.reject(now=self.now+timedelta(minutes=6))

    def test_snapshot_exceeding_fifteen_minutes_rejected(self):
        self.reject(approval=self.change(expires_utc='2026-10-23T12:20:00Z'))

    def test_snapshot_bad_timezone_rejected(self):
        self.reject(approval=self.change(issued_utc='2026-10-23T11:59:00+00:00'))

    def test_wrong_authority_rejected(self):
        self.reject(approval=self.change(authority_id='other-issuer'))

    def test_wrong_key_id_rejected(self):
        self.reject(approval=self.change(key_id='other-reviewer'))

    def test_unapproved_decision_rejected(self):
        self.reject(approval=self.change('approval',decision='pending'))

    def test_same_preparer_and_approver_rejected(self):
        self.reject(approval=self.change('approval',approved_by='builder-operator'))

    def test_bad_approval_digest_with_valid_signature_rejected(self):
        self.reject(approval=self.change('approval',manifest_sha256='f'*64))

    def test_mismatched_release_id_rejected(self):
        self.reject(approval=self.change('approval',release_id='ccpc-other-0001'))

    def test_unknown_fields_rejected(self):
        self.reject(approval=self.change(private_key='not-real-test-secret'))

    def test_malformed_clock_rejected(self):
        self.reject(now=self.now.replace(tzinfo=None))

    def test_disabled_or_untrusted_anchor_rejected(self):
        for changed in ({'public_key':b''},{'minimum_sequence':0},{'key_id':'*'}):
            self.reject(trust=replace(self.trust,**changed))

    def test_explicit_signed_duplicate_fields_rejected(self):
        raw=encode(self.approval)
        modified=raw[:-1]+b',"sequence":12}'
        sig=self.key.sign(a.DOMAIN+modified)
        with self.assertRaises(a.ApprovalRejected):
            a.verify_signed_approval(encode(self.manifest),modified,sig,
                                     trust=self.trust,now_utc=self.now)

    def test_released_still_not_trusted_runtime(self):
        result=self.runverify()
        self.assertFalse(result.release.trusted_runtime)


if __name__=='__main__':
    unittest.main()
