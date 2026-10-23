"""Offline-only, fail-closed signed release approval verification.

TrustConfig MUST come from an independent protected source, NOT Docker, the
manifest, the approval blob, or an operator-controlled environment variable.
This module has no signing interface, private keys, network or backup executor.
A valid approval is never permission to operate a backup or production service.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from scripts import dedicated_backup_policy as policy

AUTHORITY_ID = "ccpc-release-approvals"
DOMAIN = b"CCPC-RELEASE-APPROVAL-SNAPSHOT-v1\x00"
MAX_SNAPSHOT_BYTES = 16_384
MAX_AGE = timedelta(minutes=15)
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
IDENTITY = re.compile(r"[a-z][a-z0-9_-]{2,63}\Z")
TIMESTAMP = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ\Z")
FIELDS = frozenset((
    "schema_version", "authority_id", "key_id", "sequence",
    "issued_utc", "expires_utc", "approval", "revoked_release_ids",
))
APPROVAL_FIELDS = frozenset((
    "release_id", "manifest_sha256", "prepared_by", "approved_by",
    "approved_utc", "decision",
))


class ApprovalRejected(ValueError):
    """Sanitized failure. Never attach input data or crypto exceptions."""


@dataclass(frozen=True)
class TrustedApprovalAnchor:
    """Supplied externally; independent approval-channel provenance NOT proven here."""
    public_key: bytes
    key_id: str
    minimum_sequence: int
    revoked_key_ids: frozenset[str]


@dataclass(frozen=True)
class VerifiedApproval:
    """Signed digest/revocation check, not runtime or backup authorization."""
    release: policy.ValidatedRelease
    approval_sequence: int
    approval_sha256: str
    approved_by: str
    trust_source_authenticated: bool = False
    backup_ready: bool = False


def _no_duplicates(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ApprovalRejected("Duplicate approval field")
        d[k] = v
    return d


def _utc_timestamp(value):
    if type(value) is not str or not TIMESTAMP.fullmatch(value):
        raise ApprovalRejected("Invalid UTC approval timestamp")
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ApprovalRejected("Invalid UTC approval timestamp") from None
    return t


def verify_signed_approval(manifest_raw: bytes, snapshot_raw: bytes, signature: bytes,
                           *, trust: TrustedApprovalAnchor, now_utc: datetime) -> VerifiedApproval:
    """Verify an independently signed, bounded-life revocation snapshot.

    The caller MUST obtain trust.public_key, trust.minimum_sequence,
    trust.revoked_key_ids and now_utc from independently authenticated,
    high-integrity channels. No such provider is implemented here.
    """
    if (type(trust) is not TrustedApprovalAnchor or type(trust.public_key) is not bytes
            or len(trust.public_key) != 32 or type(trust.key_id) is not str
            or not IDENTITY.fullmatch(trust.key_id)
            or type(trust.minimum_sequence) is not int or trust.minimum_sequence < 1
            or type(trust.revoked_key_ids) is not frozenset
            or any(type(k) is not str or not IDENTITY.fullmatch(k) for k in trust.revoked_key_ids)
            or trust.key_id in trust.revoked_key_ids):
        raise ApprovalRejected("Trusted approval anchor missing or revoked")
    if (type(now_utc) is not datetime or now_utc.tzinfo is None
            or now_utc.utcoffset() != timedelta(0)):
        raise ApprovalRejected("Trusted UTC clock required")
    if (type(snapshot_raw) is not bytes or not snapshot_raw
            or len(snapshot_raw) > MAX_SNAPSHOT_BYTES
            or type(signature) is not bytes or len(signature) != 64):
        raise ApprovalRejected("Signed approval snapshot missing or malformed")

    # A signature must be checked before trusting ANY field of the snapshot.
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        Ed25519PublicKey.from_public_bytes(trust.public_key).verify(
            signature, DOMAIN + snapshot_raw
        )
    except (ImportError, InvalidSignature, ValueError, TypeError):
        raise ApprovalRejected("Approval signature unavailable or invalid") from None

    try:
        doc = json.loads(snapshot_raw.decode("utf-8"), object_pairs_hook=_no_duplicates,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("constant")))
    except (ValueError, TypeError, UnicodeDecodeError):
        raise ApprovalRejected("Invalid signed approval schema") from None
    if (type(doc) is not dict or set(doc) != FIELDS
            or type(doc["schema_version"]) is not int or doc["schema_version"] != 1
            or doc["authority_id"] != AUTHORITY_ID or doc["key_id"] != trust.key_id
            or type(doc["sequence"]) is not int
            or doc["sequence"] < trust.minimum_sequence):
        raise ApprovalRejected("Approval authority or generation not accepted")
    issued = _utc_timestamp(doc["issued_utc"])
    expires = _utc_timestamp(doc["expires_utc"])
    if not issued <= now_utc < expires or not timedelta(0) < expires - issued <= MAX_AGE:
        raise ApprovalRejected("Approval revocation snapshot stale or invalid")
    a = doc["approval"]
    if type(a) is not dict or set(a) != APPROVAL_FIELDS:
        raise ApprovalRejected("Missing release review record")
    if (type(a["release_id"]) is not str or not policy.RELEASE_ID.fullmatch(a["release_id"])
            or type(a["manifest_sha256"]) is not str
            or not SHA256.fullmatch(a["manifest_sha256"])
            or a["decision"] != "approved"
            or any(type(a[k]) is not str or not IDENTITY.fullmatch(a[k])
                   for k in ("prepared_by", "approved_by"))
            or a["prepared_by"] == a["approved_by"]):
        raise ApprovalRejected("Release was not independently approved")
    approved = _utc_timestamp(a["approved_utc"])
    if not approved <= issued:
        raise ApprovalRejected("Approval timestamp does not precede snapshot")
    revoked = doc["revoked_release_ids"]
    if (type(revoked) is not list or len(revoked) > 256
            or any(type(v) is not str or not policy.RELEASE_ID.fullmatch(v) for v in revoked)
            or len(set(revoked)) != len(revoked)
            or a["release_id"] in revoked):
        raise ApprovalRejected("Release revocation state invalid or revoked")

    # Reuse existing pinned-source and strict exact-manifest validation.
    try:
        release = policy.validate_reviewed_release(
            manifest_raw, independently_approved_sha256=a["manifest_sha256"]
        )
    except policy.PolicyRejected:
        raise ApprovalRejected("Manifest rejected by signed release policy") from None
    if release.release_id != a["release_id"]:
        raise ApprovalRejected("Approval does not match release identity")
    return VerifiedApproval(release, doc["sequence"], hashlib.sha256(snapshot_raw).hexdigest(),
                            a["approved_by"])


if __name__ == "__main__":
    raise SystemExit("NOT ENABLED: offline approval verifier, no signing or backup entry point")
