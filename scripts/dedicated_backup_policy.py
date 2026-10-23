"""Inert, offline-only CCPC release and consistency policy. No backup authorization.

Trusted release-manifest digest MUST be supplied by an independent reviewer,
not derived from Docker or the same untrusted manifest.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import posixpath
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

HOST = "ccpcerp-prod"
SITE = "ccpcerp.local"
PROFILE = "dedicated-pre-tls"
FRAPPE_SHA = "988e54f3c4c291e2077a83809663f123731abe76"
ERPNEXT_SHA = "4048fb70e14d1843956fcdabb7c3cca75a1cbcdd"
CCPC_SHA = "cfcc19394a6646548f2b7050db040c8cf5ebafde"
PATCH_SHA256 = "b543d14453d4370c6ddaf53bee8f8b786bf9199d5ce33182eb80aa5080e85ba1"
OVERLAY_SHA256 = "13bfff41433c9ac380b9ed632911674b9b87f7e7cb728388912ed50c79c63d0e"
HEX40 = re.compile(r"[a-f0-9]{40}\Z")
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
IMAGE_ID = re.compile(r"sha256:[a-f0-9]{64}\Z")
PROJECT = re.compile(r"[a-z0-9][a-z0-9_-]{1,63}\Z")
RELEASE_ID = re.compile(r"ccpc-[a-z0-9][a-z0-9-]{5,63}\Z")
FIELDS = frozenset((
    "schema_version", "release_id", "deployment_commit", "frappe_sha",
    "erpnext_sha", "ccpc_sha", "patch_sha256", "overlay_sha256",
    "host", "site", "profile", "compose_project", "backend_image_id",
    "db_image_id", "backend_config_hash", "db_config_hash",
    "sites_volume", "db_volume", "backend_logs_volume",
))
WRITER_CLASSES = frozenset((
    "http", "api", "integrations", "scheduler", "queues", "uploads",
    "custom_jobs", "direct_db",
))


class PolicyRejected(ValueError):
    """Nonsensitive failure reason; never expose original data."""


@dataclass(frozen=True)
class ValidatedRelease:
    """Reviewed digest matches syntax; not runtime trust or backup permission."""
    release_id: str
    manifest_sha256: str
    deployment_commit: str
    project: str
    backend_image_id: str
    db_image_id: str
    backend_config_hash: str
    db_config_hash: str
    sites_volume: str
    db_volume: str
    backend_logs_volume: str
    trusted_runtime: bool = False
    backup_ready: bool = False


def _object_no_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise PolicyRejected("Duplicate release manifest key")
        obj[key] = value
    return obj


def validate_reviewed_release(raw: bytes, *, independently_approved_sha256: str) -> ValidatedRelease:
    """Check a non-secret release against an OUT-OF-BAND approved digest.

    This function does not implement approval/signature verification. The
    caller must NEVER calculate the expected digest from the untrusted raw.
    """
    if type(raw) is not bytes or not raw or len(raw) > 12_000:
        raise PolicyRejected("Invalid manifest encoding or size")
    if type(independently_approved_sha256) is not str or not HEX64.fullmatch(independently_approved_sha256):
        raise PolicyRejected("Missing independent manifest trust anchor")
    digest = hashlib.sha256(raw).hexdigest()
    if not hmac.compare_digest(digest, independently_approved_sha256):
        raise PolicyRejected("Release manifest digest mismatch")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_object_no_duplicates,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid constant")))
    except (UnicodeDecodeError, ValueError, TypeError):
        raise PolicyRejected("Invalid release manifest JSON") from None
    if type(data) is not dict or set(data) != FIELDS or type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise PolicyRejected("Unexpected release manifest schema")
    for key, value in data.items():
        if key != "schema_version" and (type(value) is not str or not value):
            raise PolicyRejected("Invalid non-secret release field")
    if not RELEASE_ID.fullmatch(data["release_id"]) or not HEX40.fullmatch(data["deployment_commit"]):
        raise PolicyRejected("Invalid release identity")
    constants = {
        "host": HOST, "site": SITE, "profile": PROFILE, "frappe_sha": FRAPPE_SHA,
        "erpnext_sha": ERPNEXT_SHA, "ccpc_sha": CCPC_SHA,
        "patch_sha256": PATCH_SHA256, "overlay_sha256": OVERLAY_SHA256,
    }
    if any(data[key] != value for key, value in constants.items()):
        raise PolicyRejected("Unapproved source/profile metadata")
    project = data["compose_project"]
    if not PROJECT.fullmatch(project) or any(not IMAGE_ID.fullmatch(data[k]) for k in ("backend_image_id", "db_image_id")):
        raise PolicyRejected("Invalid project or immutable image identity")
    if any(not HEX64.fullmatch(data[k]) for k in ("backend_config_hash", "db_config_hash")):
        raise PolicyRejected("Invalid configuration identity")
    if (data["sites_volume"], data["db_volume"], data["backend_logs_volume"]) != (
        project + "_sites", project + "_db-data", project + "_logs"):
        raise PolicyRejected("Release manifest mounts are not explicitly named")
    return ValidatedRelease(
        data["release_id"], digest, data["deployment_commit"], project,
        data["backend_image_id"], data["db_image_id"],
        data["backend_config_hash"], data["db_config_hash"],
        data["sites_volume"], data["db_volume"], data["backend_logs_volume"],
    )


@dataclass(frozen=True)
class MountAssessment:
    """Mockable layout result, not a trusted Docker attestation."""
    exact_layout: bool
    backup_ready: bool = False


def verify_exact_mount_layout(release: ValidatedRelease, *, backend_mounts,
                              db_mounts, inspected_volumes: Mapping[str, dict]) -> MountAssessment:
    """Reject anonymous, extra and wrong Docker mounts without host access."""
    if not isinstance(release, ValidatedRelease):
        raise PolicyRejected("Reviewed release manifest required")
    rules = {
        "backend": (
            ("/home/frappe/frappe-bench/sites", release.sites_volume, "sites"),
            ("/home/frappe/frappe-bench/logs", release.backend_logs_volume, "logs"),
        ),
        "db": (("/var/lib/mysql", release.db_volume, "db-data"),),
    }
    expected_names = {release.sites_volume, release.backend_logs_volume, release.db_volume}
    if not isinstance(inspected_volumes, Mapping) or set(inspected_volumes) != expected_names:
        raise PolicyRejected("Unexpected inspected volume inventory")
    for service, mounts in (("backend", backend_mounts), ("db", db_mounts)):
        required = rules[service]
        if type(mounts) is not list or len(mounts) != len(required):
            raise PolicyRejected("Unexpected service mount count")
        index = {}
        for mount in mounts:
            if not isinstance(mount, dict) or not isinstance(mount.get("Destination"), str):
                raise PolicyRejected("Malformed mount metadata")
            dest = mount["Destination"]
            if dest in index:
                raise PolicyRejected("Duplicate mount destination")
            index[dest] = mount
        if set(index) != {dest for dest, _, _ in required}:
            raise PolicyRejected("Unexpected service mount destination")
        for dest, name, logical in required:
            volume = inspected_volumes[name]
            if not isinstance(volume, dict):
                raise PolicyRejected("Missing inspected volume metadata")
            source = volume.get("Mountpoint")
            labels = volume.get("Labels")
            if (volume.get("Name") != name or not isinstance(source, str)
                    or not source.startswith("/") or posixpath.normpath(source) != source
                    or not isinstance(labels, dict)
                    or (labels.get("com.docker.compose.project"),
                        labels.get("com.docker.compose.volume")) != (release.project, logical)):
                raise PolicyRejected("Unapproved named volume metadata")
            mount = index[dest]
            if (mount.get("Type"), mount.get("Name"), mount.get("Source"),
                mount.get("RW")) != ("volume", name, source, True):
                raise PolicyRejected("Unexpected anonymous or bind mount")
    return MountAssessment(True)


@dataclass(frozen=True)
class ConsistencyObservation:
    """Untrusted caller-supplied claim; does not freeze any service."""
    freeze_started_utc: datetime
    capture_started_utc: datetime
    capture_ended_utc: datetime
    freeze_ended_utc: datetime
    writer_activity: Mapping[str, bool]
    in_flight_transactions: int
    changed_files_warning: bool
    backup_side_effects_reviewed: bool
    full_backup_filters_verified: bool
    encryption_state_verified: bool
    recoverable_abort_plan_verified: bool


@dataclass(frozen=True)
class ConsistencyAssessment:
    """Claims checked, but cannot authorize a live backup."""
    evidence_meets_shape_and_claims: bool
    writes_quiesced: bool = False
    backup_ready: bool = False


def evaluate_quiescence_observation(obs: ConsistencyObservation) -> ConsistencyAssessment:
    """Check completeness, not authenticity, of evidence spanning full capture."""
    if not isinstance(obs, ConsistencyObservation):
        raise PolicyRejected("Consistency observation missing")
    times = (obs.freeze_started_utc, obs.capture_started_utc,
             obs.capture_ended_utc, obs.freeze_ended_utc)
    if (any(type(t) is not datetime or t.tzinfo is None or t.utcoffset() is None
            or t.utcoffset().total_seconds() != 0 for t in times)
            or not times[0] < times[1] < times[2] < times[3]):
        raise PolicyRejected("Freeze window does not cover full capture")
    if (not isinstance(obs.writer_activity, Mapping)
            or set(obs.writer_activity) != WRITER_CLASSES
            or any(value is not False for value in obs.writer_activity.values())):
        raise PolicyRejected("Unverified or active writer family")
    if type(obs.in_flight_transactions) is not int or obs.in_flight_transactions != 0:
        raise PolicyRejected("In-flight database transactions not eliminated")
    for flag, expected in ((obs.changed_files_warning, False),
                           (obs.backup_side_effects_reviewed, True),
                           (obs.full_backup_filters_verified, True),
                           (obs.encryption_state_verified, True),
                           (obs.recoverable_abort_plan_verified, True)):
        if flag is not expected:
            raise PolicyRejected("Incomplete or unsafe consistency claim")
    return ConsistencyAssessment(True)


if __name__ == "__main__":
    raise SystemExit("NOT ENABLED: offline policy, no backup entry point")
