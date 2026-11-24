#!/usr/bin/env python3
"""One-time PRIVATE backup ISO preparation on normal DEVELOPMENT host.

Copies exactly the checksum-verified 2026-11-23 DEVELOPMENT-only eight-part
NAS backup set into a new owner-private offline ISO. Does NOT open guest QEMU,
run Docker, mount a host share, restore a database or change any live site.
ISO and staging files contain CONFIDENTIAL site configuration and business data.
Never upload them or their contents to GitHub, ChatGPT, CI or external services.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess
import sys

HOST = "ccpcerpserver"
UID = 1000
NAS = Path("/mnt/erpnext_backups")
NAS_MOUNT = "//192.168.50.132/erpnext_backups cifs"
SOURCE = NAS / "ccpc-development-phase1-20261123T014828Z-ee8c493c7b6bbfc9"
BASE = Path("/home/gani/ccpc-restore-labs")
OUT = BASE / "ccpc-dev-backup-media-20261124"
STAGE = OUT / "iso-root"
ISO = OUT / "ccpc-development-backup-20261123.iso"
RECEIPT = OUT / "ccpc-development-backup-20261123.iso.sha256"
MAX_COMPONENT_BYTES = 32 * 1024 * 1024
EXPECTED = {
    "development.localhost/20261123_094829-development_localhost-database.sql.gz": 1721569,
    "development.localhost/20261123_094829-development_localhost-files.tar": 10240,
    "development.localhost/20261123_094829-development_localhost-private-files.tar": 20480,
    "development.localhost/20261123_094829-development_localhost-site_config_backup.json": 234,
    "ccpc-integration2.localhost/20261123_094828-ccpc-integration2_localhost-database.sql.gz": 1113028,
    "ccpc-integration2.localhost/20261123_094828-ccpc-integration2_localhost-files.tar": 10240,
    "ccpc-integration2.localhost/20261123_094828-ccpc-integration2_localhost-private-files.tar": 10240,
    "ccpc-integration2.localhost/20261123_094828-ccpc-integration2_localhost-site_config_backup.json": 212,
}


def stop(reason: str) -> None:
    raise RuntimeError(reason)


def require_regular(path: Path, *, max_bytes: int = MAX_COMPONENT_BYTES) -> os.stat_result:
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode) or not (0 < metadata.st_size <= max_bytes):
        stop("unexpected source file type or size: " + path.name)
    return metadata


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest() -> dict[str, str]:
    manifest = SOURCE / "SHA256SUMS"
    require_regular(manifest, max_bytes=4096)
    raw = manifest.read_bytes()
    try:
        lines = raw.decode("ascii").splitlines()
    except UnicodeDecodeError:
        stop("manifest must be ASCII")
    if len(lines) != 8:
        stop("manifest must contain exactly eight entries")
    parsed: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9._/-]+)", line)
        if match is None:
            stop("unexpected manifest structure")
        digest, rel = match.groups()
        if rel not in EXPECTED or rel in parsed:
            stop("unknown or duplicated manifest component")
        parsed[rel] = digest
    if set(parsed) != set(EXPECTED):
        stop("backup file manifest not exact")
    return parsed


def check_host() -> None:
    if (socket.gethostname().split(".")[0] != HOST or
            os.getuid() != UID or os.geteuid() != UID):
        stop("must execute only as normal gani on ccpcerpserver, never sudo")
    if not BASE.is_dir() or BASE.is_symlink():
        stop("private recovery base missing or linked")
    base_st = BASE.stat()
    if base_st.st_uid != UID or stat.S_IMODE(base_st.st_mode) != 0o700:
        stop("private recovery base ownership/mode differs")
    if OUT.exists() or OUT.is_symlink():
        stop("private one-shot media directory already exists; never overwrite/retry")
    if not shutil.which("findmnt") or not shutil.which("genisoimage"):
        stop("host findmnt/genisoimage is unavailable")
    result = subprocess.run(
        ["findmnt", "-rn", "-M", str(NAS), "-o", "SOURCE,FSTYPE"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 or result.stdout.strip() != NAS_MOUNT:
        stop("NAS CIFS mount identity mismatch; no copy permitted")
    if not SOURCE.is_dir() or SOURCE.is_symlink():
        stop("source backup folder missing or linked")
    expected_top = {"SHA256SUMS", "development.localhost", "ccpc-integration2.localhost"}
    if {p.name for p in SOURCE.iterdir()} != expected_top:
        stop("unexpected NAS backup top-level inventory")
    for site in ("development.localhost", "ccpc-integration2.localhost"):
        folder = SOURCE / site
        if not folder.is_dir() or folder.is_symlink():
            stop("source site directory linked or missing")
        expected_files = {Path(p).name for p in EXPECTED if p.startswith(site + "/")}
        if {p.name for p in folder.iterdir()} != expected_files:
            stop("unexpected NAS site backup component")
    if shutil.disk_usage(BASE).free < 1024**3:
        stop("less than 1GiB free on private host recovery storage")


def main() -> None:
    os.umask(0o077)
    check_host()
    manifest = read_manifest()
    # Validate all eight NAS files before creating even the first output folder.
    for rel, size in EXPECTED.items():
        src = SOURCE / rel
        if require_regular(src).st_size != size or sha256(src) != manifest[rel]:
            stop("NAS component size/checksum mismatch: " + Path(rel).name)
    OUT.mkdir(mode=0o700)
    STAGE.mkdir(mode=0o700)
    for site in ("development.localhost", "ccpc-integration2.localhost"):
        (STAGE / site).mkdir(mode=0o700)
    # Recheck each source checksum while copying; staged contents must match.
    for rel, size in EXPECTED.items():
        src, dest = SOURCE / rel, STAGE / rel
        before = require_regular(src)
        if before.st_size != size:
            stop("NAS source changed during copy")
        src_fd = os.open(src, os.O_RDONLY | os.O_NOFOLLOW)
        dest_fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(src_fd, "rb") as inp, os.fdopen(dest_fd, "wb") as out:
            shutil.copyfileobj(inp, out, 1024 * 1024)
            out.flush()
            os.fsync(out.fileno())
        after = require_regular(src)
        if ((before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns)
                or require_regular(dest).st_size != size
                or sha256(src) != manifest[rel] or sha256(dest) != manifest[rel]):
            stop("backup changed or copy verification failed: " + Path(rel).name)
    shutil.copyfile(SOURCE / "SHA256SUMS", STAGE / "SHA256SUMS")
    os.chmod(STAGE / "SHA256SUMS", 0o600)
    if read_manifest() != manifest or sha256(STAGE / "SHA256SUMS") != sha256(SOURCE / "SHA256SUMS"):
        stop("backup manifest changed while staging")
    # Private ISO containing ONLY staged backup files and the manifest.
    proc = subprocess.run(
        ["genisoimage", "-quiet", "-R", "-J", "-iso-level", "3",
         "-V", "CCPCDEV23", "-o", str(ISO), str(STAGE)],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=False,
    )
    if proc.returncode:
        stop("genisoimage failed; preserve partial private folder for review")
    image_stat = require_regular(ISO, max_bytes=128 * 1024 * 1024)
    os.chmod(ISO, 0o600)
    digest = sha256(ISO)
    with RECEIPT.open("x", encoding="ascii") as out:
        out.write(digest + "  " + ISO.name + "\n")
    os.chmod(RECEIPT, 0o600)
    print("PRIVATE DEVELOPMENT BACKUP ISO: PREPARED")
    print("SOURCE NAS MANIFEST: 8/8 VERIFIED BEFORE AND AFTER COPY")
    print("ISOLATED ISO BYTES:", image_stat.st_size)
    print("ISO SHA256:", digest)
    print("PRIVATE ISO:", ISO)
    print("PRIVATE SHA256 RECEIPT:", RECEIPT)
    print("NO QEMU/DOCKER OPERATION; NO BACKUP RESTORE; NO DEV/PROD MODIFICATION")
    print("CONFIDENTIAL FILES: KEEP HOST-PRIVATE; NO PUBLIC UPLOAD OR AUTO CLEANUP")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, UnicodeError) as exc:
        print("STOP: " + str(exc), file=sys.stderr)
        print("Do not rerun if private output directory exists; preserve state.", file=sys.stderr)
        sys.exit(1)
