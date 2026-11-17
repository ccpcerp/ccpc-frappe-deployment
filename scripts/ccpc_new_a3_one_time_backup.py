#!/usr/bin/env python3
"""CCPC NEW A3 one-use four-artifact backup and verified NAS publication.

Manual execution only. NEVER uses generic bench backup or cleanup/retention.
Must be root-owned when run on the exact NEW host after hash verification.
No OLD PROD / DEVELOPMENT / protected rehearsal writes or service changes.
"""
from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import stat
import subprocess
import sys
import tarfile

HOST = "ccpcerp-prod"
OPERATOR = "ccpcadmin"
PROJECT = "ccpc_prod_erpnext"
SITE = "ccpcerp.local"
IMAGE = "sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8"
NAS = "//192.168.50.132/ccpcerp-prod_backups"
NAS_MOUNT = Path("/mnt/ccpcerp-prod_backups")
NAS_CREDENTIALS = Path("/etc/ccpc-prod-nas/credentials")
RUN_BASE = Path("/var/lib/ccpc-a3-one-time-backup")
LOCK = Path("/run/lock/ccpc-a3-one-time-backup.lock")
RUN_ID = re.compile(r"\A\d{8}T\d{6}Z-[a-f0-9]{16}\Z")
ARTIFACT = re.compile(r"\A(\d{8}_\d{6})-ccpcerp_local-(database\.sql\.gz|site_config_backup\.json|files\.tar|private-files\.tar)\Z")
ROLES = {"database.sql.gz": "database", "site_config_backup.json": "site_config", "files.tar": "public_files", "private-files.tar": "private_files"}
EXPECTED = {f"{PROJECT}-{service}-1" for service in ("frontend", "websocket", "backend", "redis-queue", "redis-cache", "db")}
REHEARSALS = {f"{prefix}-{service}-1" for prefix in ("ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107") for service in ("redis-queue", "redis-cache", "db")}

CHILD = r'''import inspect, json, os, re, sys
from pathlib import Path
import frappe
from frappe.utils.backups import BackupGenerator
try:
    run_id = sys.argv[1]
    if not re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{16}", run_id):
        raise RuntimeError("invalid run identifier")
    if frappe.__version__ != "16.33.1":
        raise RuntimeError("unexpected Frappe version")
    if not {"backup_path", "ignore_conf"}.issubset(inspect.signature(BackupGenerator).parameters):
        raise RuntimeError("unexpected backup API")
    if "delete_temp_backups" in inspect.getsource(BackupGenerator.get_backup):
        raise RuntimeError("unsafe generator cleanup")
    frappe.init(site="ccpcerp.local", sites_path=".")
    frappe.connect()
    def yes(v):
        return str(v or "").strip().lower() in ("1", "true", "yes", "on")
    if not yes(frappe.conf.get("pause_scheduler")) or not yes(frappe.conf.get("mute_emails")):
        raise RuntimeError("scheduler or email active")
    if yes(frappe.get_system_settings("encrypt_backup")):
        raise RuntimeError("encrypted backup unsupported by this run")
    if frappe.conf.db_type != "mariadb":
        raise RuntimeError("unexpected DB type")
    # Unique, private output OUTSIDE the conventional private/backups folder.
    private = Path("ccpcerp.local/private")
    if private.is_symlink() or not private.is_dir():
        raise RuntimeError("private site root invalid")
    output = private / (".ccpc-a3-backup-" + run_id)
    if os.path.lexists(output):
        raise RuntimeError("run output exists")
    old_umask = os.umask(0o077)
    try:
        output.mkdir(mode=0o700)
    finally:
        os.umask(old_umask)
    gen = BackupGenerator(
        frappe.conf.db_name, frappe.conf.db_user, frappe.conf.db_password,
        backup_path=str(output), db_socket=frappe.conf.db_socket,
        db_host=frappe.conf.db_host, db_port=frappe.conf.db_port,
        db_type=frappe.conf.db_type, ignore_conf=True, compress_files=False,
        include_doctypes="", exclude_doctypes="", verbose=False,
    )
    if gen.partial or gen.backup_includes or gen.backup_excludes:
        raise RuntimeError("partial backup rejected")
    gen.get_backup(force=True, ignore_files=False)
    names = [x.name for x in output.iterdir()]
    if len(names) != 4:
        raise RuntimeError("incomplete backup")
    if not all((output / name).is_file() and (output / name).stat().st_size > 0 for name in names):
        raise RuntimeError("empty/nonfile backup artifact")
    frappe.destroy()
    print("CCPC_A3_GENERATOR_CAPTURE_PASS")
except Exception:
    # Suppress error/traceback: may contain DB credentials, file names or business data.
    print("CCPC_A3_GENERATOR_CAPTURE_STOP")
    raise SystemExit(1)
'''


def stop(reason: str) -> None:
    raise RuntimeError(reason)


def run(argv: list[str], *, input_text: str | None = None, timeout: int = 60) -> str:
    try:
        p = subprocess.run(argv, input=input_text, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        stop("A system command could not complete; preserve state; do not retry")
    if p.returncode != 0:
        # Never expose stderr, which can hold application or SMB information.
        stop("A guarded system operation failed; preserve state; do not retry")
    return p.stdout.strip()


def root_stat(path: Path, *, regular=False, directory=False, mode: int | None = None) -> None:
    s = path.lstat()
    if s.st_uid != 0 or s.st_gid != 0:
        stop("Protected root-owned path mismatch")
    if regular and not stat.S_ISREG(s.st_mode) or directory and not stat.S_ISDIR(s.st_mode):
        stop("Protected path type mismatch")
    if mode is not None and stat.S_IMODE(s.st_mode) != mode:
        stop("Protected path mode mismatch")


def docker_json(argv: list[str]) -> list[dict]:
    data = json.loads(run(["docker", *argv], timeout=45))
    if not isinstance(data, list):
        stop("Docker inspection shape mismatch")
    return data


def inspect_runtime() -> Path:
    if socket.gethostname().split(".")[0] != HOST or os.geteuid() != 0 or os.environ.get("SUDO_USER") != OPERATOR:
        stop("Wrong host/operator/root execution identity")
    if RUN_BASE.is_symlink() or NAS_MOUNT.is_symlink():
        stop("Unexpected protected path link")
    root_stat(NAS_MOUNT, directory=True, mode=0o700)
    root_stat(NAS_CREDENTIALS, regular=True, mode=0o600)
    mount_status = subprocess.run(["findmnt", "--mountpoint", str(NAS_MOUNT), "--noheadings", "--output", "SOURCE"], capture_output=True, text=True, check=False)
    if mount_status.returncode == 0 or mount_status.returncode not in (0, 1):
        stop("NAS already mounted or findmnt unavailable; no mount reuse")
    entries = run(["docker", "ps", "-a", "--format", "{{.Names}}"], timeout=30).splitlines()
    if len(entries) != 12 or set(entries) != EXPECTED | REHEARSALS:
        stop("Docker container inventory differs from the protected 12-container baseline")
    objs = docker_json(["inspect", *sorted(EXPECTED | REHEARSALS)])
    by_name = {r.get("Name", "").lstrip("/"): r for r in objs}
    if set(by_name) != EXPECTED | REHEARSALS:
        stop("Docker identity mismatch")
    for name, info in by_name.items():
        if not info.get("State", {}).get("Running"):
            stop("A protected container is not running")
        if name in EXPECTED:
            if info.get("HostConfig", {}).get("RestartPolicy", {}).get("Name") != "no":
                stop("Candidate restart policy changed")
            if info.get("HostConfig", {}).get("PortBindings"):
                stop("Candidate has a published port")
            nets = info.get("NetworkSettings", {}).get("Networks") or {}
            if set(nets) != {PROJECT + "_default"}:
                stop("Candidate unexpected network identity")
            if name in {f"{PROJECT}-{x}-1" for x in ("frontend", "websocket", "backend")} and info.get("Image") != IMAGE:
                stop("Candidate app image mismatch")
    front = by_name[f"{PROJECT}-frontend-1"]
    if front["NetworkSettings"]["Networks"][PROJECT + "_default"].get("IPAddress") != "172.20.0.7":
        stop("Frontend private proxy target changed")
    if by_name[f"{PROJECT}-db-1"].get("State", {}).get("Health", {}).get("Status") != "healthy":
        stop("NEW database health is not healthy")
    needed = {
        f"{PROJECT}-backend-1": {(f"{PROJECT}_sites", "/home/frappe/frappe-bench/sites"), (f"{PROJECT}_logs", "/home/frappe/frappe-bench/logs")},
        f"{PROJECT}-db-1": {(f"{PROJECT}_db-data", "/var/lib/mysql")},
    }
    for name, pairs in needed.items():
        mounts = {(m.get("Name"), m.get("Destination")) for m in by_name[name].get("Mounts", []) if m.get("Type") == "volume"}
        if not pairs.issubset(mounts):
            stop("Candidate persistent volumes differ")
    volumes = docker_json(["volume", "inspect", f"{PROJECT}_sites", f"{PROJECT}_db-data"])
    vmap = {v.get("Name"): v for v in volumes}
    if set(vmap) != {f"{PROJECT}_sites", f"{PROJECT}_db-data"}:
        stop("Candidate volume identity mismatch")
    if any(v.get("Driver") != "local" for v in volumes):
        stop("Unexpected volume storage driver")
    sites = Path(vmap[f"{PROJECT}_sites"].get("Mountpoint", ""))
    if not sites.is_absolute() or sites.is_symlink() or not sites.is_dir() or sites.name != "_data" or sites.parent.name != f"{PROJECT}_sites":
        stop("Candidate sites volume mountpoint mismatch")
    site = sites / SITE
    if site.is_symlink() or not site.is_dir() or not (site / "private").is_dir():
        stop("Candidate site volume not recognized")
    free = shutil.disk_usage(RUN_BASE.parent).free
    if free < 5 * 1024**3:
        stop("Insufficient host local space (<5 GiB)")
    return sites


def artifacts_at(directory: Path) -> dict[str, Path]:
    if directory.is_symlink() or not directory.is_dir():
        stop("Backup output directory replaced")
    entries = list(directory.iterdir())
    if len(entries) != 4:
        stop("Expected exactly four source backup artifacts")
    dates: set[str] = set()
    result: dict[str, Path] = {}
    for path in entries:
        m = ARTIFACT.fullmatch(path.name)
        if not m:
            stop("Unexpected generated backup artifact name")
        s = path.lstat()
        if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1 or s.st_size <= 0:
            stop("Unsafe or empty generated backup artifact")
        dates.add(m.group(1))
        role = ROLES[m.group(2)]
        if role in result:
            stop("Duplicate backup artifact role")
        result[role] = path
    if set(result) != set(ROLES.values()) or len(dates) != 1:
        stop("Incomplete or mixed backup artifact set")
    return result


def digest(path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as source:
        before = os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            stop("Backup source replaced")
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
        after = os.fstat(source.fileno())
        if (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_size) != (after.st_dev, after.st_ino, after.st_mtime_ns, after.st_size):
            stop("Backup file changed during checksum")
    return before.st_size, h.hexdigest()


def check_format(role: str, path: Path) -> None:
    try:
        if role == "database":
            with gzip.open(path, "rb") as f:
                if b"frappe" not in f.read(2000).lower():
                    stop("Database gzip header does not look like Frappe")
                for _ in iter(lambda: f.read(1024 * 1024), b""):
                    pass  # CRC/decompression verified through EOF
        elif role == "site_config":
            with open(path, "rb") as f:
                data = json.load(f)
            if not isinstance(data, dict) or not {"db_name", "db_password"}.issubset(data):
                stop("Site config recovery metadata incomplete")
        else:
            with tarfile.open(path, "r:") as archive:
                count = 0
                for member in archive:
                    count += 1
                    if member.name.startswith("/") or ".." in Path(member.name).parts or member.issym() or member.islnk():
                        stop("Unsafe attachment archive entry")
                if not count:
                    stop("Empty attachment archive structure")
    except (OSError, gzip.BadGzipFile, tarfile.TarError, ValueError, EOFError, json.JSONDecodeError):
        stop("Backup artifact format verification failed")


def copy_new(src: Path, dest: Path) -> None:
    before = digest(src)
    source_fd = os.open(src, os.O_RDONLY | os.O_NOFOLLOW)
    dest_fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(source_fd, "rb") as inp, os.fdopen(dest_fd, "wb") as out:
        shutil.copyfileobj(inp, out, 1024 * 1024)
        out.flush()
        os.fsync(out.fileno())
    if digest(src) != before or digest(dest) != before:
        stop("Backup copy checksum mismatch")


def verify_mount() -> None:
    output = run(["findmnt", "--mountpoint", str(NAS_MOUNT), "--noheadings", "--output", "SOURCE,FSTYPE,OPTIONS"])
    parts = output.split(maxsplit=2)
    if len(parts) != 3 or parts[0] != NAS or parts[1] != "cifs" or "rw" not in parts[2].split(","):
        stop("NAS CIFS source/type/write-state mismatch; no fallback writes")


def publish_noreplace(src: Path, dst: Path) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    func = getattr(libc, "renameat2", None)
    if func is None:
        stop("Atomic no-replace NAS publish unavailable")
    func.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    func.restype = ctypes.c_int
    result = func(-100, os.fsencode(src), -100, os.fsencode(dst), 1)
    if result != 0:
        stop("Atomic no-replace NAS publish failed; preserve partial")


def write_new(path: Path, content: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())


def backup_once(sites: Path) -> None:
    # A persistent run-once marker intentionally blocks accidental repeated runs.
    RUN_BASE.mkdir(mode=0o700, exist_ok=True)
    root_stat(RUN_BASE, directory=True, mode=0o700)
    write_new(RUN_BASE / "DO_NOT_REPEAT", b"NEW A3 manual backup started; preserve any partial state.\n")
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(8)
    if not RUN_ID.fullmatch(run_id):
        stop("Run identifier invalid")
    local = RUN_BASE / run_id
    local.mkdir(mode=0o700)
    print("RUN_ID=" + run_id, flush=True)
    print("=== CAPTURE NEW A3 SITE ONLY ===", flush=True)
    out = subprocess.run(["docker", "exec", "-i", "--user", "1000:1000", "--workdir", "/home/frappe/frappe-bench/sites", f"{PROJECT}-backend-1", "/home/frappe/frappe-bench/env/bin/python", "-", run_id], input=CHILD, text=True, capture_output=True, timeout=1800, check=False)
    if out.returncode != 0 or "CCPC_A3_GENERATOR_CAPTURE_PASS" not in out.stdout:
        stop("NEW A3 Frappe capture failed; see preserved partial; do not repeat")
    print("CCPC_A3_GENERATOR_CAPTURE_PASS", flush=True)
    source_dir = sites / SITE / "private" / (".ccpc-a3-backup-" + run_id)
    names = artifacts_at(source_dir)
    total_source_bytes = sum(p.stat().st_size for p in names.values())
    if shutil.disk_usage(local).free < total_source_bytes + 2 * 1024**3:
        stop("Insufficient local scratch capacity for the new backup set")
    manifest = {"schema": 1, "site": SITE, "project": PROJECT, "image": IMAGE, "run_id": run_id, "artifacts": []}
    for role in sorted(names):
        source = names[role]
        check_format(role, source)
        target = local / source.name
        copy_new(source, target)
        size, sha = digest(target)
        manifest["artifacts"].append({"role": role, "filename": source.name, "size": size, "sha256": sha})
        print("LOCAL_" + role.upper() + "_SHA256_VERIFIED", flush=True)
    manifest_bytes = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode()
    write_new(local / "manifest.json", manifest_bytes)
    print("CCPC_A3_FOUR_LOCAL_ARTIFACTS_PASS", flush=True)

    print("=== MOUNT DEDICATED NAS SHARE ===", flush=True)
    # Block all local fallback writing; NAS mount identity must be confirmed after mount.
    run(["mount", "-t", "cifs", NAS, str(NAS_MOUNT), "-o", "credentials=" + str(NAS_CREDENTIALS) + ",vers=3.1.1,sec=ntlmssp,rw,nosuid,nodev,noexec,uid=0,gid=0,file_mode=0600,dir_mode=0700"], timeout=90)
    mounted = True
    completed = False
    try:
        verify_mount()
        if shutil.disk_usage(NAS_MOUNT).free < total_source_bytes + 1024**3:
            stop("Insufficient dedicated NAS free capacity")
        stage = NAS_MOUNT / (".partial-ccpc-new-a3-" + run_id)
        final = NAS_MOUNT / ("ccpc-new-a3-" + run_id)
        if os.path.lexists(stage) or os.path.lexists(final):
            stop("NAS backup run path already exists")
        stage.mkdir(mode=0o700)
        for entry in manifest["artifacts"]:
            verify_mount()
            copy_new(local / entry["filename"], stage / entry["filename"])
            if digest(stage / entry["filename"]) != (entry["size"], entry["sha256"]):
                stop("NAS read-back mismatch")
            print("NAS_" + entry["role"].upper() + "_SHA256_VERIFIED", flush=True)
        verify_mount()
        write_new(stage / "manifest.json", manifest_bytes)
        if digest(stage / "manifest.json") != digest(local / "manifest.json"):
            stop("NAS manifest mismatch")
        verify_mount()
        if os.path.lexists(final):
            stop("Final run path exists; would overwrite")
        publish_noreplace(stage, final)
        verify_mount()
        write_new(final / "COMPLETED", (run_id + "\n").encode())
        for entry in manifest["artifacts"]:
            if digest(final / entry["filename"]) != (entry["size"], entry["sha256"]):
                stop("Published NAS readback mismatch")
        if (final / "COMPLETED").read_text().strip() != run_id:
            stop("NAS completed marker mismatch")
        completed = True
        print("CCPC_A3_NAS_FOUR_ARTIFACT_PUBLICATION_PASS", flush=True)
    finally:
        if mounted:
            try:
                verify_mount()
                run(["umount", str(NAS_MOUNT)], timeout=75)
                print("CCPC_A3_NAS_CLEAN_UNMOUNT_PASS", flush=True)
            except Exception:
                # Never unmount any unexpected share and never silently report success.
                stop("NAS unmount/identity unsafe; manual review required")
    if not completed:
        stop("NAS publication did not complete")
    print("CCPC_NEW_A3_ONE_TIME_BACKUP_COMPLETE_RESTORE_TEST_PENDING", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="NEW CCPC A3 guarded one-time backup")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--preflight", action="store_true")
    g.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        sites = inspect_runtime()
        if args.preflight:
            if RUN_BASE.exists() and (RUN_BASE / "DO_NOT_REPEAT").exists():
                stop("One-time backup already attempted")
            print("CCPC_A3_BACKUP_HOST_DOCKER_NAS_LOCAL_PREFLIGHT_PASS")
            return 0
        if RUN_BASE.exists() and (RUN_BASE / "DO_NOT_REPEAT").exists():
            stop("One-time backup already attempted; no rerun")
        fd = os.open(LOCK, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w"):
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            backup_once(sites)
        return 0
    except Exception as exc:
        # Explicit sanitized status; never print underlying exception/command stderr.
        print("CCPC_A3_BACKUP_STOP_REVIEW_REQUIRED")
        print("REASON=" + str(exc) if isinstance(exc, RuntimeError) else "REASON=Unexpected local error; preserve state")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
