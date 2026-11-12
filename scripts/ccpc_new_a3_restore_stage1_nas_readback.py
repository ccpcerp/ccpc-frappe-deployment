#!/usr/bin/env python3
"""CCPC isolated restore Stage 1: a single read-only NAS reread into NEW test scratch.

No database access, Docker mutations, Frappe actions, existing backup edits,
NAS writes, retention or service operations. Run manually on NEW only.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess

HOST = "ccpcerp-prod"
OPERATOR = "ccpcadmin"
RUN_ID = "20261112T090214Z-0148d36b2cb678b3"
SOURCE = "//192.168.50.132/ccpcerp-prod_backups"
CREDENTIALS = Path("/etc/ccpc-prod-nas/credentials")
LIVE_NAS_MOUNT = Path("/mnt/ccpcerp-prod_backups")
MOUNT = Path("/mnt/ccpc-a3-restore-readonly-20261112")
LOCAL = Path("/var/lib/ccpc-a3-one-time-backup") / RUN_ID
SCRATCH = Path("/var/lib/ccpc-a3-isolated-restore-20261112")
NAS_DIR = "ccpc-new-a3-" + RUN_ID
IMAGE = "sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8"
FILENAME = re.compile(r"\A\d{8}_\d{6}-ccpcerp_local-(database\.sql\.gz|site_config_backup\.json|files\.tar|private-files\.tar)\Z")
SUFFIX_ROLE = {
    "database.sql.gz": "database",
    "site_config_backup.json": "site_config",
    "files.tar": "public_files",
    "private-files.tar": "private_files",
}
CONTAINERS = {
    *(f"ccpc_prod_erpnext-{s}-1" for s in ("frontend", "websocket", "backend", "redis-cache", "redis-queue", "db")),
    *(f"{p}-{s}-1" for p in ("ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107")
      for s in ("db", "redis-cache", "redis-queue")),
}
PREFIX = "ccpc_a3_restore_drill_20261112"

class Stop(Exception):
    pass

def guard(ok: bool, reason: str) -> None:
    if not ok:
        raise Stop(reason)

def execute(argv: list[str], *, timeout: int = 90) -> str:
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise Stop("Guarded system command unavailable or timed out") from None
    if p.returncode != 0:
        raise Stop("Guarded system command failed")  # Never surface stderr.
    return p.stdout.strip()

def mount_info(path: Path) -> tuple[str, str, set[str]] | None:
    p = subprocess.run(
        ["findmnt", "--mountpoint", str(path), "--noheadings", "--raw",
         "--output", "SOURCE,FSTYPE,OPTIONS"],
        capture_output=True, text=True, timeout=15, check=False,
    )
    if p.returncode == 1:
        return None
    guard(p.returncode == 0, "Mount inspection unavailable")
    parts = p.stdout.strip().split(maxsplit=2)
    guard(len(parts) == 3, "Unexpected mount inspection result")
    return parts[0], parts[1], set(parts[2].split(","))

def verify_mount() -> None:
    current = mount_info(MOUNT)
    guard(current is not None, "Drill NAS mount missing")
    source, typ, opts = current
    guard(source == SOURCE and typ == "cifs" and "ro" in opts and "rw" not in opts,
          "Drill NAS not exactly expected read-only CIFS share")

def stat_root(path: Path, *, directory: bool = False, file: bool = False, mode: int | None = None) -> None:
    try:
        s = path.lstat()
    except OSError:
        raise Stop("Expected protected path absent") from None
    guard(s.st_uid == 0 and s.st_gid == 0, "Protected path ownership invalid")
    guard(not directory or stat.S_ISDIR(s.st_mode), "Protected directory invalid")
    guard(not file or stat.S_ISREG(s.st_mode), "Protected regular file invalid")
    guard(mode is None or stat.S_IMODE(s.st_mode) == mode, "Protected path mode invalid")

def sha(path: Path) -> tuple[int, str]:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    h = hashlib.sha256()
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        guard(stat.S_ISREG(before.st_mode) and before.st_size > 0, "Backup artifact invalid")
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
        after = os.fstat(stream.fileno())
        guard((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
              (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
              "Backup artifact changed while reading")
    return before.st_size, h.hexdigest()

def manifest_from(source: Path) -> tuple[bytes, list[dict]]:
    guard(not source.is_symlink() and source.is_file(), "Local manifest unavailable")
    raw = source.read_bytes()
    guard(0 < len(raw) < 16384, "Local manifest invalid")
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeError):
        raise Stop("Local manifest unreadable") from None
    guard(isinstance(data, dict) and data.get("schema") == 1 and
          data.get("run_id") == RUN_ID and data.get("site") == "ccpcerp.local" and
          data.get("project") == "ccpc_prod_erpnext" and data.get("image") == IMAGE,
          "Manifest backup identity mismatch")
    arts = data.get("artifacts")
    guard(isinstance(arts, list) and len(arts) == 4, "Manifest incomplete")
    names, roles, timestamps = set(), set(), set()
    for item in arts:
        guard(isinstance(item, dict), "Unexpected manifest item")
        name, role = item.get("filename"), item.get("role")
        guard(type(name) is str and type(role) is str, "Invalid artifact metadata")
        match = FILENAME.fullmatch(name)
        guard(match is not None and SUFFIX_ROLE.get(match.group(1)) == role and
              role not in roles and name not in names, "Wrong artifact role/name")
        guard(type(item.get("size")) is int and item["size"] > 0 and
              type(item.get("sha256")) is str and
              re.fullmatch(r"[a-f0-9]{64}", item["sha256"]) is not None,
              "Invalid artifact checksum metadata")
        timestamps.add(name[:15]); names.add(name); roles.add(role)
    guard(roles == set(SUFFIX_ROLE.values()) and len(timestamps) == 1,
          "Mixed or missing backup artifacts")
    return raw, arts

def check_baseline() -> tuple[bytes, list[dict]]:
    guard(os.geteuid() == 0 and os.environ.get("SUDO_USER") == OPERATOR and
          socket.gethostname().split(".")[0] == HOST, "Wrong host or operator")
    stat_root(CREDENTIALS, file=True, mode=0o600)
    stat_root(LIVE_NAS_MOUNT, directory=True, mode=0o700)
    guard(mount_info(LIVE_NAS_MOUNT) is None, "Active backup NAS mount found; STOP")
    guard(not MOUNT.exists() and not MOUNT.is_symlink(), "Drill mountpoint already exists; STOP")
    guard(not SCRATCH.exists() and not SCRATCH.is_symlink(), "Restore scratch already exists; STOP")
    guard(LOCAL.is_dir() and not LOCAL.is_symlink(), "Original backup directory missing")
    containers = set(execute(["docker", "ps", "-a", "--format", "{{.Names}}"], timeout=30).splitlines())
    guard(containers == CONTAINERS, "Protected Docker container inventory changed")
    running = set(execute(["docker", "ps", "--format", "{{.Names}}"], timeout=30).splitlines())
    guard(running == CONTAINERS, "A protected container stopped")
    for typ in ("volume", "network"):
        names = execute(["docker", typ, "ls", "--format", "{{.Name}}"], timeout=30).splitlines()
        guard(not any(n.startswith(PREFIX) for n in names), "Restore test namespace occupied")
    raw, arts = manifest_from(LOCAL / "manifest.json")
    guard(set(f.name for f in LOCAL.iterdir()) ==
          {"manifest.json"} | {a["filename"] for a in arts},
          "Local backup directory contains unexpected entries")
    total = 0
    for a in arts:
        guard(sha(LOCAL / a["filename"]) == (a["size"], a["sha256"]),
              "Local backup artifact SHA256 mismatch")
        total += a["size"]
    guard(shutil.disk_usage(SCRATCH.parent).free >= 2 * total + 10 * 1024 ** 3,
          "Insufficient isolated restore scratch free space")
    return raw, arts

def copy_verified(src: Path, dst: Path, expected_size: int, expected_hash: str) -> None:
    source_fd = os.open(src, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        output_fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except Exception:
        os.close(source_fd)
        raise
    digest = hashlib.sha256()
    with os.fdopen(source_fd, "rb") as source, os.fdopen(output_fd, "wb") as output:
        before = os.fstat(source.fileno())
        guard(stat.S_ISREG(before.st_mode) and before.st_size == expected_size,
              "NAS source changed before copying")
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
            output.write(chunk)
        output.flush()
        os.fsync(output.fileno())
        after = os.fstat(source.fileno())
        guard((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
              (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
              "NAS source changed during copying")
    guard(digest.hexdigest() == expected_hash, "Independent NAS SHA256 mismatch")
    guard(sha(dst) == (expected_size, expected_hash), "Scratch copy SHA256 mismatch")

def readback(raw: bytes, arts: list[dict]) -> None:
    verify_mount()
    remote = MOUNT / NAS_DIR
    guard(remote.is_dir() and not remote.is_symlink(), "Published NAS backup not found")
    expected_entries = {"manifest.json", "COMPLETED"} | {a["filename"] for a in arts}
    guard(set(x.name for x in remote.iterdir()) == expected_entries,
          "Published NAS directory contains unexpected entries")
    marker = remote / "COMPLETED"
    guard(marker.is_file() and not marker.is_symlink() and
          marker.read_bytes() == (RUN_ID + "\n").encode(),
          "Published NAS completion marker mismatch")
    nas_manifest = remote / "manifest.json"
    guard(nas_manifest.is_file() and not nas_manifest.is_symlink() and
          nas_manifest.read_bytes() == raw,
          "Independent NAS manifest readback mismatch")
    print("CCPC_RESTORE_NAS_COMPLETED_MANIFEST_PASS", flush=True)
    # Root-only destination: a new disposable scratch, NEVER a live Docker site.
    SCRATCH.mkdir(mode=0o700)
    stat_root(SCRATCH, directory=True, mode=0o700)
    for a in arts:
        verify_mount()
        src = remote / a["filename"]
        guard(src.is_file() and not src.is_symlink(), "Published NAS artifact type mismatch")
        copy_verified(src, SCRATCH / a["filename"], a["size"], a["sha256"])
        print("CCPC_RESTORE_NAS_" + a["role"].upper() + "_SHA256_PASS", flush=True)
    (SCRATCH / "manifest.json").write_bytes(raw)
    (SCRATCH / "manifest.json").chmod(0o600)
    guard((SCRATCH / "manifest.json").read_bytes() == raw,
          "Scratch manifest mismatch")
    (SCRATCH / "NAS_COMPLETED_VERIFIED").write_text(RUN_ID + "\n")
    (SCRATCH / "NAS_COMPLETED_VERIFIED").chmod(0o600)
    print("CCPC_RESTORE_INDEPENDENT_SCRATCH_FOUR_ARTIFACTS_PASS", flush=True)

def single_readback() -> None:
    raw, arts = check_baseline()
    # No network/backup writes before the protected mountpoint is exclusively reserved.
    MOUNT.mkdir(mode=0o700)
    stat_root(MOUNT, directory=True, mode=0o700)
    mounted = False
    failed = False
    try:
        print("CCPC_RESTORE_NAS_READONLY_MOUNT_ATTEMPT", flush=True)
        execute(
            ["mount", "-t", "cifs", SOURCE, str(MOUNT), "-o",
             "credentials=" + str(CREDENTIALS) +
             ",vers=3.1.1,sec=ntlmssp,ro,nosuid,nodev,noexec,uid=0,gid=0,file_mode=0600,dir_mode=0700"],
            timeout=90,
        )
        mounted = True
        verify_mount()
        print("CCPC_RESTORE_EXACT_NAS_READONLY_MOUNT_PASS", flush=True)
        readback(raw, arts)
    except Exception:
        failed = True
        raise
    finally:
        # Unmount only when *this run* successfully mounted the exact approved NAS share.
        if mounted:
            verify_mount()
            execute(["umount", str(MOUNT)], timeout=75)
            print("CCPC_RESTORE_NAS_READONLY_CLEAN_UNMOUNT_PASS", flush=True)
        elif mount_info(MOUNT) is not None:
            raise Stop("Mount outcome ambiguous; manual review, DO NOT unmount unknown share")
        if failed:
            print("CCPC_RESTORE_PARTIAL_SCRATCH_RETAINED", flush=True)
    print("CCPC_NEW_A3_RESTORE_STAGE1_NAS_READBACK_PASS", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEW A3 independent NAS reread only")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--preflight", action="store_true")
    selection.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        if args.preflight:
            check_baseline()
            print("CCPC_NEW_A3_RESTORE_STAGE1_PREFLIGHT_PASS")
        else:
            single_readback()
    except Exception:
        print("CCPC_NEW_A3_RESTORE_STAGE1_STOP_REVIEW_REQUIRED")
        raise SystemExit(1)
