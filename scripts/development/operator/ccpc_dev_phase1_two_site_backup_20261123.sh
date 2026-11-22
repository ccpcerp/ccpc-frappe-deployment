#!/usr/bin/env bash
# One-shot, owner-approved DEVELOPMENT-only Frappe backup + segregated NAS copy.
# Do not rerun after any completed or partial execution; retain all partials for review.
set -euo pipefail
umask 077
exec python3 - <<'PY'
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import stat
import subprocess
import sys

EXPECTED_SHA = "b0cbe5c13cb68499a7920de2879f65e72cff000a"
DEV_CONTAINER = "frappe_docker_devcontainer-frappe-1"
BENCH_HOST = Path("/home/gani/deployments/frappe_docker/development/frappe-bench")
BENCH_CONTAINER = "/workspace/development/frappe-bench"
DEV_BIND_HOST = "/home/gani/deployments/frappe_docker/development"
DEV_BIND_CONTAINER = "/workspace/development"
APP_CONTAINER = BENCH_CONTAINER + "/apps/ccpcerp"
LOCAL_ROOT = BENCH_HOST / ".ccpc-pr32-snapshots"
NAS_ROOT = Path("/mnt/erpnext_backups")
EXPECTED_NAS = "//192.168.50.132/erpnext_backups cifs"
HISTORICAL_NAS = "ccpc-development-pr32-20261029T234223Z-f38259861f97ed80"
SITES = ("ccpc-integration2.localhost", "development.localhost")
SUFFIXES = ("-database.sql.gz", "-site_config_backup.json", "-files.tar", "-private-files.tar")


def stop(why: str) -> None:
    raise RuntimeError(why)


def run(argv: list[str], *, input_text: str | None = None) -> str:
    # Intentionally capture diagnostics; they may contain private system information.
    p = subprocess.run(argv, input=input_text, text=True, capture_output=True, check=False)
    if p.returncode != 0:
        stop("guarded command failed: " + argv[0] + " (private stderr withheld)")
    return p.stdout.strip()


def guard_regular_dir(p: Path, *, owner: int | None = None) -> None:
    st = p.lstat()
    if not stat.S_ISDIR(st.st_mode) or (owner is not None and st.st_uid != owner):
        stop("unexpected local directory ownership or type")


def guard_nas() -> None:
    guard_regular_dir(NAS_ROOT)
    actual = run(["findmnt", "-rn", "-M", str(NAS_ROOT), "-o", "SOURCE,FSTYPE"])
    if actual != EXPECTED_NAS:
        stop("NAS is not the verified exact CIFS mount")
    guard_regular_dir(NAS_ROOT / HISTORICAL_NAS)


def guard_checkout() -> None:
    sha = run(["docker", "exec", "--user", "frappe", DEV_CONTAINER,
               "git", "-C", APP_CONTAINER, "rev-parse", "HEAD"])
    if sha != EXPECTED_SHA:
        stop("DEVELOPMENT app source commit differs from approved SHA")
    status = run(["docker", "exec", "--user", "frappe", DEV_CONTAINER,
                  "git", "-C", APP_CONTAINER, "status", "--porcelain=v1", "--untracked-files=all"])
    if status:
        stop("DEVELOPMENT app checkout is no longer clean")


def sha256(p: Path) -> str:
    digest = hashlib.sha256()
    with p.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def components(folder: Path) -> list[Path]:
    guard_regular_dir(folder, owner=1000)
    files = list(folder.iterdir())
    if len(files) != 4:
        stop("backup component count is not exactly four")
    matched: list[Path] = []
    for suffix in SUFFIXES:
        candidates = [p for p in files if p.name.endswith(suffix)
                      and not (suffix == "-files.tar" and p.name.endswith("-private-files.tar"))]
        if len(candidates) != 1 or candidates[0] in matched:
            stop("missing/duplicate backup artifact type")
        f = candidates[0]
        st = f.lstat()
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size <= 0 or st.st_uid != 1000:
            stop("backup artifact is empty, linked, nonregular or unexpected owner")
        matched.append(f)
    return matched


def ensure_space(path: Path, minimum: int) -> None:
    if shutil.disk_usage(path).free < minimum:
        stop("insufficient free space for new DEVELOPMENT backup / NAS copy")


BACKUP_CODE = r'''
from pathlib import Path
import gzip, json, os, sys, tarfile
import frappe
from frappe.utils.backups import BackupGenerator

site, label = sys.argv[1], sys.argv[2]
allowed = ("ccpc-integration2.localhost", "development.localhost")
if site not in allowed or not label.startswith("ccpc-development-phase1-"):
    raise RuntimeError("unexpected site or destination label")

os.umask(0o077)
bench = Path("/workspace/development/frappe-bench")
root = bench / ".ccpc-pr32-snapshots"
if not root.is_dir() or root.is_symlink():
    raise RuntimeError("missing or unexpected backup root")
if not (bench / "sites" / site / "site_config.json").is_file():
    raise RuntimeError("expected development site config is absent")

frappe.init(site=site, sites_path=".")
try:
    frappe.connect()
    if frappe.conf.db_type != "mariadb":
        raise RuntimeError("unexpected database engine")
    if frappe.get_system_settings("encrypt_backup"):
        raise RuntimeError("site requests encryption; stop rather than produce unencrypted files")
    dest = root / (site + "-" + label)
    if dest.exists() or dest.is_symlink():
        raise RuntimeError("snapshot destination already exists")
    dest.mkdir(mode=0o700)
    gen = BackupGenerator(
        frappe.conf.db_name,
        frappe.conf.db_user,
        frappe.conf.db_password,
        db_socket=frappe.conf.db_socket,
        db_host=frappe.conf.db_host,
        db_port=frappe.conf.db_port,
        db_type=frappe.conf.db_type,
        backup_path=str(dest),
        ignore_conf=True,
        compress_files=False,
        verbose=False,
    )
    gen.get_backup(force=True, ignore_files=False)
    expected = [Path(p) for p in (
        gen.backup_path_db,
        gen.backup_path_conf,
        gen.backup_path_files,
        gen.backup_path_private_files,
    )]
    if len(list(dest.iterdir())) != 4 or len(set(expected)) != 4:
        raise RuntimeError("not exactly four generated artifacts")
    for p in expected:
        if p.parent != dest or not p.is_file() or p.is_symlink() or p.stat().st_size <= 0:
            raise RuntimeError("incomplete backup component")
    with gzip.open(gen.backup_path_db, "rb") as f:
        while f.read(1024 * 1024):
            pass
    with open(gen.backup_path_conf, "r", encoding="utf-8") as f:
        if not isinstance(json.load(f), dict):
            raise RuntimeError("invalid site config format")
    for p in (gen.backup_path_files, gen.backup_path_private_files):
        with tarfile.open(p, mode="r:") as tf:
            for member in tf:
                if member.isfile():
                    entry = tf.extractfile(member)
                    if entry is None:
                        raise RuntimeError("unreadable TAR member")
                    while entry.read(1024 * 1024):
                        pass
    print("BACKUP_AND_STREAM_VALIDATION_PASS")
finally:
    frappe.destroy()
'''


def make_backup(site: str, label: str) -> Path:
    guard_checkout()
    cmd = ["docker", "exec", "-i", "--user", "frappe", DEV_CONTAINER,
           "/bin/bash", "-c",
           'cd /workspace/development/frappe-bench/sites && exec /workspace/development/frappe-bench/env/bin/python - "$@"',
           "backup-runner", site, label]
    result = run(cmd, input_text=BACKUP_CODE)
    if "BACKUP_AND_STREAM_VALIDATION_PASS" not in result:
        stop("no verified success marker from Frappe backup")
    folder = LOCAL_ROOT / (site + "-" + label)
    components(folder)
    print(site + ": LOCAL FOUR-COMPONENT BACKUP PASS", flush=True)
    return folder


def copy_to_nas(folders: dict[str, Path], label: str) -> None:
    guard_nas()
    size_needed = sum(p.stat().st_size for folder in folders.values() for p in components(folder))
    ensure_space(NAS_ROOT, max(1024 * 1024 * 1024, size_needed * 2))
    stage = NAS_ROOT / (".partial-" + label)
    final = NAS_ROOT / label
    if stage.exists() or final.exists() or stage.is_symlink() or final.is_symlink():
        stop("NAS destination name already exists")
    stage.mkdir(mode=0o700)
    manifest = []
    for site in SITES:
        guard_nas()
        target_dir = stage / site
        target_dir.mkdir(mode=0o700)
        for source in components(folders[site]):
            guard_nas()
            dest = target_dir / source.name
            before = source.stat()
            orig_hash = sha256(source)
            with source.open("rb") as inp, dest.open("xb") as out:
                shutil.copyfileobj(inp, out, length=1024 * 1024)
                out.flush()
                os.fsync(out.fileno())
            after = source.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                stop("source backup changed during off-host transfer")
            if dest.stat().st_size != before.st_size or sha256(dest) != orig_hash:
                stop("NAS copy SHA256/size mismatch")
            manifest.append(orig_hash + "  " + site + "/" + source.name + "\n")
        print(site + ": NAS 4/4 SHA256 PASS", flush=True)
    if len(manifest) != 8:
        stop("NAS transfer did not include eight components")
    text = "".join(manifest)
    with (stage / "SHA256SUMS").open("x", encoding="ascii") as out:
        out.write(text)
        out.flush()
        os.fsync(out.fileno())
    if (stage / "SHA256SUMS").read_text(encoding="ascii") != text:
        stop("manifest verification failed")
    guard_nas()
    if final.exists():
        stop("NAS final destination collision")
    stage.rename(final)
    print("NAS 8/8 CHECKSUM PASS", flush=True)
    print("NEW NAS FOLDER: " + final.name, flush=True)


def main() -> None:
    os.umask(0o077)
    if os.geteuid() != 1000 or socket.gethostname().split(".")[0] != "ccpcerpserver":
        stop("must run as non-root UID 1000 on the approved DEVELOPMENT host")
    guard_regular_dir(BENCH_HOST)
    guard_regular_dir(LOCAL_ROOT, owner=1000)
    guard_nas()
    ensure_space(LOCAL_ROOT, 2 * 1024 * 1024 * 1024)
    mounts = json.loads(run(["docker", "inspect", "--format", "{{json .Mounts}}", DEV_CONTAINER]))
    if not any(m.get("Type") == "bind" and m.get("Source") == DEV_BIND_HOST
               and m.get("Destination") == DEV_BIND_CONTAINER and m.get("RW") is True
               for m in mounts):
        stop("DEVELOPMENT container bind mount does not match protected host path")
    if run(["docker", "inspect", "--format", "{{.State.Running}}", DEV_CONTAINER]) != "true":
        stop("DEVELOPMENT Frappe container not running")
    guard_checkout()
    print("DEVELOPMENT-ONLY TARGET AND NAS GUARDS: PASS", flush=True)
    label = "ccpc-development-phase1-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(8)
    folders = {site: make_backup(site, label) for site in SITES}
    guard_checkout()
    copy_to_nas(folders, label)
    print("TWO-SITE DEVELOPMENT BACKUP AND NAS COPY: PASS", flush=True)
    print("RESTORE REHEARSAL: UNVERIFIED", flush=True)
    print("NO MIGRATION, SERVICE RESTART, OR PRODUCTION OPERATION PERFORMED", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        # Deliberately omit traceback and exception parameters (could expose credentials).
        print("STOP: " + type(err).__name__ + ": " + (str(err) if type(err) is RuntimeError else "backup operation did not complete"), file=sys.stderr)
        print("Preserve any created local/NAS partials. Do not retry automatically.", file=sys.stderr)
        sys.exit(1)
PY
