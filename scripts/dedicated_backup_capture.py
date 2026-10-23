"""Inert, injectable Frappe v16 backup-capture adapter for offline review.

This module NEVER invokes a bench/container executable by itself.  A future,
separately approved environment adapter must attest real host/image/site
identity, quiescence, filesystem isolation and encryption before it supplies
an execution callback.  Do not install or run on a live ERPNext host.
"""

from __future__ import annotations

import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from scripts import dedicated_backup_core as core

# Pinned Frappe v16 source: frappe/commands/site.py & utils/backups.py, tag
# v16.33.1, reviewed 2026-10-23.  These flags are NOT guessed from log text.
FRAPPE_SHA = "988e54f3c4c291e2077a83809663f123731abe76"
HOST = "ccpcerp-prod"
PROFILE = "dedicated-pre-tls"
SITE = core.SITE
CAPTURE_DIR_PREFIX = ".ccpc-capture-"
OUTPUT_RE = re.compile(
    r"\A([0-9]{8}_[0-9]{6})-ccpcerp_local-"
    r"(database\.sql\.gz|site_config_backup\.json|files\.tar|private-files\.tar)\Z"
)
SUFFIX_TO_ROLE = {
    "database.sql.gz": "database",
    "site_config_backup.json": "site_config",
    "files.tar": "public_files",
    "private-files.tar": "private_files",
}
IMAGE_DIGEST_RE = re.compile(r"\Asha256:[0-9a-f]{64}\Z")
PROJECT_RE = re.compile(r"\A[a-z0-9][a-z0-9_-]{1,63}\Z")


@dataclass(frozen=True)
class CaptureAttestation:
    """Evidence interface only. A verified source is NOT implemented here."""

    host: str
    site: str
    compose_profile: str
    compose_project: str
    frappe_sha: str
    image_digest: str
    service: str
    database_service: str
    site_volume_verified: bool
    database_volume_verified: bool
    writes_quiesced: bool
    no_partial_backup_filters: bool
    encryption_disabled: bool


@dataclass(frozen=True)
class CapturedSet:
    source_dir: Path
    filenames: dict[str, str]
    run_id: str
    image_digest: str
    argv: tuple[str, ...]


def verify_attestation(a: CaptureAttestation) -> None:
    """Reject obviously wrong declarations; independent runtime checks pending."""
    if not isinstance(a, CaptureAttestation):
        raise core.BackupSafetyError("Runtime attestation is missing")
    if (a.host, a.site, a.compose_profile, a.frappe_sha) != (
        HOST,
        SITE,
        PROFILE,
        FRAPPE_SHA,
    ):
        raise core.BackupSafetyError("Wrong Frappe host, site, profile or release")
    if not PROJECT_RE.fullmatch(a.compose_project):
        raise core.BackupSafetyError("Unverified Compose project")
    if a.service != "backend" or a.database_service != "db":
        raise core.BackupSafetyError("Wrong Frappe or MariaDB service")
    if not IMAGE_DIGEST_RE.fullmatch(a.image_digest):
        raise core.BackupSafetyError("Unpinned container image")
    if not all(flag is True for flag in (
        a.site_volume_verified,
        a.database_volume_verified,
        a.writes_quiesced,
        a.no_partial_backup_filters,
        a.encryption_disabled,
    )):
        raise core.BackupSafetyError("Capture consistency or format not attested")


def _safe_capture_root(root: Path) -> Path:
    """Require a pre-provisioned, private directory owned by the executor."""
    root = Path(root)
    if not root.is_absolute() or root.is_symlink():
        raise core.BackupSafetyError("Capture root must be absolute and not a symlink")
    try:
        info = root.lstat()
        if ".." in root.parts or root.resolve(strict=True) != root:
            raise core.BackupSafetyError("Noncanonical capture root")
    except (OSError, RuntimeError) as exc:
        raise core.BackupSafetyError("Capture root unavailable") from exc
    if (
        not stat.S_ISDIR(info.st_mode)
        or stat.S_IMODE(info.st_mode) != 0o700
        or info.st_uid != os.geteuid()
    ):
        raise core.BackupSafetyError("Capture root ownership or mode invalid")
    # A future verified container adapter must pin the root to the site's
    # real private backups volume.  This local exclusion is defense-in-depth.
    if root == core.NAS_MOUNT or core.NAS_MOUNT in root.parents:
        raise core.BackupSafetyError("Cannot capture directly onto NAS")
    return root


def build_bench_argv(output_dir: Path) -> tuple[str, ...]:
    """Build fixed v16 arguments, never via a shell or user-provided flags."""
    return (
        "bench",
        "--site",
        SITE,
        "backup",
        "--with-files",
        "--ignore-backup-conf",
        "--backup-path",
        str(output_dir),
    )


def _discover_exact_set(output_dir: Path) -> dict[str, str]:
    """Fail closed on any untracked/stale/ambiguous output."""
    result: dict[str, str] = {}
    timestamps: set[str] = set()
    entries = list(output_dir.iterdir())
    if len(entries) != 4:
        raise core.BackupSafetyError("Expected four and only four generated files")
    for entry in entries:
        match = OUTPUT_RE.fullmatch(entry.name)
        if match is None:
            raise core.BackupSafetyError("Unexpected Frappe artifact filename")
        file_info = entry.lstat()
        if not stat.S_ISREG(file_info.st_mode) or file_info.st_nlink != 1:
            raise core.BackupSafetyError("Unsafe generated artifact")
        timestamp, suffix = match.groups()
        role = SUFFIX_TO_ROLE[suffix]
        if role in result:
            raise core.BackupSafetyError("Duplicate Frappe artifact role")
        result[role] = entry.name
        timestamps.add(timestamp)
    if set(result) != set(core.ROLES) or len(timestamps) != 1:
        raise core.BackupSafetyError("Missing/mixed Frappe backup set")
    core.inspect_artifacts(output_dir, result)
    return result


def capture_with_verified_runner(
    *,
    capture_root: Path,
    run_id: str,
    attest: Callable[[], CaptureAttestation],
    runner: Callable[[tuple[str, ...]], int],
) -> CapturedSet:
    """Run ONLY an injected executor, and validate exactly this one set.

    The runtime attestor, runner and container identity are intentionally NOT
    supplied.  Current code is only suitable for mocked offline tests.
    An interrupted/failed capture is preserved, not deleted automatically.
    """
    if not core.RUN_ID.fullmatch(run_id):
        raise core.BackupSafetyError("Unsafe run identifier")
    if not callable(attest) or not callable(runner):
        raise core.BackupSafetyError("Trusted attestor and runner required")
    runtime = attest()
    verify_attestation(runtime)
    root = _safe_capture_root(capture_root)
    output_dir = root / (CAPTURE_DIR_PREFIX + run_id)
    if os.path.lexists(output_dir):
        raise core.BackupSafetyError("Backup capture run already exists")
    # Frappe will create files in this new private location.  No globbing in
    # the site's old backup directory or cleanup of Frappe-managed backups.
    try:
        output_dir.mkdir(mode=0o700)
    except OSError as exc:
        raise core.BackupSafetyError("Cannot reserve unique capture directory") from exc
    argv = build_bench_argv(output_dir)
    try:
        rc = runner(argv)
    except Exception as exc:
        raise core.BackupSafetyError("Frappe capture executor failed") from exc
    if type(rc) is not int or rc != 0:
        raise core.BackupSafetyError("Frappe backup failed")
    # A hostile or faulty runner must not replace the reserved directory.
    if output_dir.is_symlink() or not output_dir.is_dir():
        raise core.BackupSafetyError("Capture directory was replaced")
    names = _discover_exact_set(output_dir)
    return CapturedSet(output_dir, names, run_id, runtime.image_digest, argv)


if __name__ == "__main__":
    raise SystemExit("NOT ENABLED: offline capture adapter; no production execution entry point")
