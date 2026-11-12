#!/usr/bin/env python3
"""NEW A3 restore drill Stage 0: strictly read-only local source/namespace audit.

Run with sudo from ccpcadmin on ccpcerp-prod. No backup import, mounts, writes,
container starts, volume/network creation or secret output.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess

RUN = "20261112T090214Z-0148d36b2cb678b3"
DIR = Path("/var/lib/ccpc-a3-one-time-backup") / RUN
PREFIX = "ccpc_a3_restore_drill_20261112"
IMAGE = "sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8"
ROLES = {"database", "site_config", "public_files", "private_files"}
EXPECTED = {
    *(f"ccpc_prod_erpnext-{s}-1" for s in
      ("frontend", "websocket", "backend", "redis-cache", "redis-queue", "db")),
    *(f"{p}-{s}-1" for p in
      ("ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107")
      for s in ("db", "redis-cache", "redis-queue")),
}
PATTERN = re.compile(
    r"\d{8}_\d{6}-ccpcerp_local-(database\.sql\.gz|site_config_backup\.json|files\.tar|private-files\.tar)"
)

def stop(reason: str) -> None:
    raise RuntimeError(reason)

def docker(*args: str) -> set[str]:
    try:
        result = subprocess.run(
            ["docker", "--host", "unix:///var/run/docker.sock", *args],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        stop("Docker read-only inventory failed")
    if result.returncode != 0:
        stop("Docker read-only inventory unavailable")
    return set(result.stdout.splitlines())

def check() -> None:
    if (socket.gethostname().split(".")[0] != "ccpcerp-prod"
        or os.geteuid() != 0 or os.environ.get("SUDO_USER") != "ccpcadmin"):
        stop("Unexpected host/operator")
    if DIR.is_symlink() or not DIR.is_dir():
        stop("Backup local run directory missing")
    manifest = DIR / "manifest.json"
    if manifest.is_symlink() or not manifest.is_file():
        stop("Backup manifest missing")
    ms = manifest.lstat()
    if ms.st_uid != 0 or not stat.S_ISREG(ms.st_mode):
        stop("Backup manifest ownership/type changed")
    try:
        metadata = json.loads(manifest.read_bytes())
    except (OSError, ValueError):
        stop("Backup manifest unreadable")
    if (not isinstance(metadata, dict)
        or metadata.get("schema") != 1 or metadata.get("run_id") != RUN
        or metadata.get("site") != "ccpcerp.local"
        or metadata.get("project") != "ccpc_prod_erpnext"
        or metadata.get("image") != IMAGE):
        stop("Backup manifest source mismatch")
    entries = metadata.get("artifacts")
    if not isinstance(entries, list) or len(entries) != 4:
        stop("Backup manifest must contain exactly four artifacts")
    seen_roles: set[str] = set()
    seen_names: set[str] = set()
    total = 0
    for item in entries:
        if not isinstance(item, dict):
            stop("Malformed artifact metadata")
        role, filename, size, expected = (
            item.get("role"), item.get("filename"),
            item.get("size"), item.get("sha256"),
        )
        if (role not in ROLES or role in seen_roles
            or not isinstance(filename, str) or PATTERN.fullmatch(filename) is None
            or filename in seen_names or type(size) is not int or size <= 0
            or not isinstance(expected, str) or re.fullmatch(r"[a-f0-9]{64}", expected) is None):
            stop("Unexpected backup artifact role/name/digest")
        path = DIR / filename
        if path.is_symlink() or not path.is_file():
            stop("Local backup artifact missing/unsafe")
        info = path.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0
            or info.st_nlink != 1 or info.st_size != size):
            stop("Backup artifact size or ownership mismatch")
        hash_obj = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                hash_obj.update(chunk)
        if hash_obj.hexdigest() != expected:
            stop("Backup artifact digest mismatch")
        seen_roles.add(role)
        seen_names.add(filename)
        total += size
    if seen_roles != ROLES or set(x.name for x in DIR.iterdir()) != seen_names | {"manifest.json"}:
        stop("Unexpected local backup run entries")
    print("CCPC_RESTORE_LOCAL_FOUR_ARTIFACT_SHA256_PASS", flush=True)
    if docker("ps", "-a", "--format", "{{.Names}}") != EXPECTED:
        stop("Protected twelve-container baseline changed")
    if docker("ps", "--format", "{{.Names}}") != EXPECTED:
        stop("Protected twelve containers not all running")
    print("CCPC_RESTORE_PROTECTED_12_CONTAINER_NAMES_PASS", flush=True)
    for kind, template in (("volume", "{{.Name}}"), ("network", "{{.Name}}")):
        names = docker(kind, "ls", "--format", template)
        if any(name.startswith(PREFIX) for name in names):
            stop("Restore test resource name collision")
    print("CCPC_RESTORE_NEW_NAMESPACE_UNUSED_PASS", flush=True)
    free = shutil.disk_usage("/var/lib/docker").free
    if free < 3 * total + 10 * 1024 ** 3:
        stop("Insufficient scratch/restore disk headroom")
    print("CCPC_RESTORE_LOCAL_CAPACITY_PASS", flush=True)
    print("CCPC_NEW_A3_RESTORE_STAGE0_READONLY_PASS", flush=True)

if __name__ == "__main__":
    try:
        check()
    except Exception:
        # Do not print Python traceback/source content on production.
        print("CCPC_NEW_A3_RESTORE_STAGE0_STOP_REVIEW_REQUIRED")
        raise SystemExit(1)
