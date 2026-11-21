#!/usr/bin/env bash
# One-shot MAIN DEVELOPMENT fresh PRECOMMIT backup copy to verified Synology NAS.
# Copies only a newly approved MAIN-only local backup from Nov 17 onward.
# Never modifies application checkout, databases, earlier backups or PRODUCTION.
set -euo pipefail
umask 077
[[ "$(hostname -s)" == "ccpcerpserver" && "$(id -un)" == "gani" ]] || {
  echo "STOP: original DEV host/operator only" >&2; exit 1;
}
[[ "${CCPC_APPROVE_PR33_MAIN_NAS_COPY:-}" == "YES" ]] || {
  echo "STOP: NAS copy authorization gate missing" >&2; exit 1;
}
SNAPSHOT="${1:-}"
[[ "$SNAPSHOT" =~ ^development\.localhost-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}$ ]] || {
  echo "STOP: specify the exact fresh MAIN snapshot directory name" >&2; exit 1;
}
MARKER="$HOME/.ccpc-pr33-main-precommit-nas-copy-once-20261117"
mkdir "$MARKER" || {
  echo "STOP: NAS copy already attempted; do not auto-retry" >&2; exit 1;
}
python3 - "$SNAPSHOT" <<'PY'
import hashlib
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone, timedelta

NAS = Path('/mnt/erpnext_backups')
SOURCE = Path('/home/gani/deployments/frappe_docker/development/frappe-bench/.ccpc-pr32-snapshots')
SITES = (sys.argv[1],)
OLDER_NAS = 'ccpc-development-pr33-billing-preacceptance-20261104T082044Z-4231b0c38ab77bf0'
EXPECTED_MOUNT = '//192.168.50.132/erpnext_backups cifs'
LINE = re.compile(r'([0-9a-f]{64})  ([A-Za-z0-9._-]+)\Z')
NAME = 'ccpc-development-pr33-main-precommit-'

def must(condition, code):
    if not condition:
        raise RuntimeError(code)

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while data := f.read(1024 * 1024):
            h.update(data)
    return h.hexdigest()

def file_kind(name):
    if name.endswith('-database.sql.gz'):
        return 'database'
    if name.endswith('-site_config_backup.json'):
        return 'config'
    if name.endswith('-private-files.tar'):
        return 'private'
    if name.endswith('-files.tar'):
        return 'public'
    return None

def snapshot_files(folder):
    must(folder.is_dir() and not folder.is_symlink(), 'SOURCE_SNAPSHOT_NOT_DIRECTORY')
    entries = list(folder.iterdir())
    must(len(entries) == 5 and {p.name for p in entries if p.name == 'SHA256SUMS'} == {'SHA256SUMS'}, 'SOURCE_FILE_COUNT')
    must(all(p.is_file() and not p.is_symlink() and p.stat().st_size > 0 for p in entries), 'SOURCE_FILE_INVALID')
    manifest = folder / 'SHA256SUMS'
    lines = manifest.read_text(encoding='utf-8').splitlines()
    must(len(lines) == 4, 'SOURCE_MANIFEST_COUNT')
    expected = {}
    types = set()
    for row in lines:
        match = LINE.fullmatch(row)
        must(match is not None, 'SOURCE_MANIFEST_FORMAT')
        hexsha, filename = match.groups()
        kind = file_kind(filename)
        must(kind is not None and kind not in types and filename not in expected, 'SOURCE_MANIFEST_TYPE')
        types.add(kind)
        expected[filename] = hexsha
    must(types == {'database','config','public','private'}, 'SOURCE_MANIFEST_KINDS')
    must({p.name for p in entries} == set(expected) | {'SHA256SUMS'}, 'SOURCE_MANIFEST_NAMES')
    for filename, hexsha in expected.items():
        must(digest(folder / filename) == hexsha, 'SOURCE_HASH_MISMATCH')
    return expected

def copy_exclusive(src, dst):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(dst, flags, 0o600)
    with os.fdopen(fd, 'wb') as out, src.open('rb') as incoming:
        shutil.copyfileobj(incoming, out, 1024 * 1024)
        out.flush()
        os.fsync(out.fileno())

partial = None
try:
    must(os.geteuid() != 0, 'ROOT_USER_FORBIDDEN')
    actual = subprocess.check_output(
        ['findmnt', '-rn', '-M', str(NAS), '-o', 'SOURCE,FSTYPE'],
        text=True, timeout=15,
    ).strip()
    must(actual == EXPECTED_MOUNT, 'WRONG_NAS_MOUNT')
    must(NAS.is_dir() and not NAS.is_symlink() and os.access(NAS, os.R_OK | os.W_OK), 'NAS_NOT_ACCESSIBLE')
    must((NAS / OLDER_NAS).is_dir() and not (NAS / OLDER_NAS).is_symlink(), 'OLDER_NAS_BACKUP_MISSING')
    must(SOURCE.is_dir() and not SOURCE.is_symlink(), 'SOURCE_ROOT_MISSING')
    must(len(sys.argv) == 2, 'SNAPSHOT_ARGUMENTS_UNEXPECTED')
    stamp = re.fullmatch(
        r'development\.localhost-([0-9]{8}T[0-9]{6}Z)-[0-9a-f]{12}',
        SITES[0],
    )
    must(stamp is not None, 'SNAPSHOT_NAME_UNEXPECTED')
    stamp_time = datetime.strptime(stamp.group(1), '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - stamp_time
    must(timedelta(0) <= age <= timedelta(hours=48)
         and stamp_time >= datetime(2026, 11, 17, tzinfo=timezone.utc),
         'SNAPSHOT_NOT_FRESH')
    print('NEW_MAIN_BACKUP_AGE_WINDOW=PASS', flush=True)

    records = {}
    bytes_total = 0
    for name in SITES:
        checks = snapshot_files(SOURCE / name)
        records[name] = checks
        bytes_total += sum((SOURCE / name / file).stat().st_size for file in checks)
        bytes_total += (SOURCE / name / 'SHA256SUMS').stat().st_size
    must(len(records) == 1 and sum(map(len, records.values())) == 4, 'SOURCE_4_FILES_MISSING')
    statvfs = os.statvfs(NAS)
    available = statvfs.f_bavail * statvfs.f_frsize
    must(available >= max(1024**3, bytes_total * 2), 'INSUFFICIENT_NAS_SPACE')
    print('NAS MOUNT: PASS', flush=True)
    print('FRESH_MAIN_SOURCE_MANIFEST: 4/4 PASS', flush=True)

    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    token = secrets.token_hex(8)
    partial = NAS / ('.partial-' + NAME + timestamp + '-' + token)
    final = NAS / (NAME + timestamp + '-' + token)
    must(not partial.exists() and not partial.is_symlink() and not final.exists() and not final.is_symlink(), 'DESTINATION_EXISTS')
    partial.mkdir(mode=0o700)
    # CIFS may report 0755 regardless of the validated Synology DSM ACL;
    # do not chmod the shared folder or weaken its server-side permissions.
    print('NEW NAS STAGING DIRECTORY: CREATED', flush=True)

    global_lines = []
    for name in SITES:
        src_dir, dst_dir = SOURCE / name, partial / name
        dst_dir.mkdir(mode=0o700)
        for filename, hexsha in records[name].items():
            src_file, dst_file = src_dir / filename, dst_dir / filename
            must(src_file.is_file() and not src_file.is_symlink(), 'SOURCE_CHANGED')
            copy_exclusive(src_file, dst_file)
            must(src_file.stat().st_size == dst_file.stat().st_size, 'COPIED_SIZE_MISMATCH')
            must(digest(src_file) == hexsha and digest(dst_file) == hexsha, 'COPIED_HASH_MISMATCH')
            global_lines.append(f'{hexsha}  {name}/{filename}\n')
        copy_exclusive(src_dir / 'SHA256SUMS', dst_dir / 'SHA256SUMS')
        must(digest(src_dir / 'SHA256SUMS') == digest(dst_dir / 'SHA256SUMS'), 'COPIED_MANIFEST_MISMATCH')
        must(len(tuple(dst_dir.iterdir())) == 5, 'COPIED_DIRECTORY_COUNT')
        print('development.localhost: 4/4 SHA256 PASS', flush=True)

    must(len(global_lines) == 4, 'NAS_GLOBAL_MANIFEST_COUNT')
    overall = partial / 'SHA256SUMS'
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(overall, flags, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.writelines(global_lines)
        f.flush()
        os.fsync(f.fileno())
    for line in global_lines:
        match = re.fullmatch(r'([0-9a-f]{64})  ([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)\n', line)
        must(match is not None, 'NAS_GLOBAL_MANIFEST_FORMAT')
        expected_sha, relative = match.groups()
        must(digest(partial / relative) == expected_sha, 'NAS_GLOBAL_HASH_MISMATCH')
    must({p.name for p in partial.iterdir()} == {*SITES, 'SHA256SUMS'}, 'NAS_FINAL_CONTENTS_INVALID')
    must(not final.exists() and not final.is_symlink(), 'FINAL_COLLISION')
    os.rename(partial, final)
    partial = None
    print('NAS BACKUP CHECKSUMS: 4/4 PASS', flush=True)
    print('FINAL NAS DIRECTORY: ' + str(final), flush=True)
    print('FRESH_PRECOMMIT_MAIN_DEV_OFF_HOST_BACKUP: PASS', flush=True)
except Exception:
    print('STOP: NAS backup transfer not verified; do not retry automatically.', file=sys.stderr)
    if partial is not None and partial.exists():
        print('STOP: New partial directory retained for manual review.', file=sys.stderr)
    raise SystemExit(1)
PY
