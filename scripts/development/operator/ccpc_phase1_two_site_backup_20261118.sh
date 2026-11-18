#!/usr/bin/env bash
# CCPC Phase 1: independently verified two-site DEVELOPMENT backup, local + Synology.
# This script creates NEW backup files only. Never pulls code, migrates, restarts or restores.
set -euo pipefail
umask 077

if [[ "$(hostname -s)" != ccpcerpserver || "$(id -un)" != gani ]]; then
  echo 'STOP: Wrong host/operator; no backup attempted' >&2
  exit 1
fi
if [[ "${CCPC_APPROVE_PHASE1_TWO_SITE_BACKUP:-}" != YES ]]; then
  echo 'STOP: Backup authorization flag missing; no backup attempted' >&2
  exit 1
fi
sudo -v
python3 -B - <<'PY'
import fcntl
import pwd
import hashlib
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
from datetime import datetime, timezone

SITES = ('development.localhost', 'ccpc-integration2.localhost')
CONTAINER = 'frappe_docker_devcontainer-frappe-1'
PROJECT = 'frappe_docker_devcontainer'
EXPECTED_HEAD = '25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87'
NAS = Path('/mnt/erpnext_backups')
EXPECTED_MOUNT = '//192.168.50.132/erpnext_backups cifs'
HOST_SNAPSHOTS = Path('/home/gani/deployments/frappe_docker/development/frappe-bench/.ccpc-pr32-snapshots')


def must(cond, code):
    if not cond:
        raise RuntimeError(code)


def run(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kwargs).stdout.strip()


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def kind(name):
    if name.endswith('-database.sql.gz'):
        return 'database'
    if name.endswith('-site_config_backup.json'):
        return 'config'
    if name.endswith('-private-files.tar'):
        return 'private'
    if name.endswith('-files.tar'):
        return 'public'
    return None


def verify_snapshot(directory):
    must(directory.is_dir() and not directory.is_symlink(), 'SNAPSHOT_DIR_INVALID')
    entries = tuple(directory.iterdir())
    must(len(entries) == 5 and all(p.is_file() and not p.is_symlink() for p in entries),
         'SNAPSHOT_FILE_COUNT_OR_LINK')
    manifest = directory / 'SHA256SUMS'
    must(manifest.is_file() and not manifest.is_symlink(), 'MANIFEST_MISSING')
    lines = manifest.read_text(encoding='utf-8').splitlines()
    must(len(lines) == 4, 'MANIFEST_ENTRY_COUNT')
    found, types = {}, set()
    for row in lines:
        match = re.fullmatch(r'([0-9a-f]{64})  ([A-Za-z0-9._-]+)', row)
        must(match is not None, 'MANIFEST_FORMAT')
        expected, name = match.groups()
        group = kind(name)
        must(group is not None and group not in types and name not in found,
             'DUPLICATE_OR_UNKNOWN_BACKUP_TYPE')
        types.add(group)
        found[name] = expected
    must(types == {'database', 'config', 'public', 'private'}, 'BACKUP_KINDS_MISSING')
    must({p.name for p in entries} == set(found) | {'SHA256SUMS'},
         'SNAPSHOT_CONTENTS_UNEXPECTED')
    for name, expected in found.items():
        file = directory / name
        must(file.stat().st_size > 0 and digest(file) == expected, 'SNAPSHOT_SHA256_MISMATCH')
    return found


CONTAINER_CODE = r'''
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import sys
import tarfile
from datetime import datetime, timezone

SITES = ('development.localhost', 'ccpc-integration2.localhost')
BENCH = Path('/workspace/development/frappe-bench')
ROOT = BENCH / '.ccpc-pr32-snapshots'
APP = BENCH / 'apps/ccpcerp'
EXPECTED_HEAD = '25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87'


def must(value, label):
    if not value:
        raise RuntimeError(label)


def git(*args):
    return subprocess.run(['git', '-C', str(APP), *args], check=True,
                          capture_output=True, text=True, timeout=30).stdout.strip()


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for data in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def validate_artifact(kind, path, stage):
    must(path.parent == stage and path.is_file() and not path.is_symlink(),
         'BACKUP_FILE_PATH')
    must(path.stat().st_size > 0, 'EMPTY_BACKUP_FILE')
    os.chmod(path, 0o600)
    if kind == 'database':
        must(path.name.endswith('-database.sql.gz'), 'DB_BACKUP_TYPE')
        with gzip.open(path, 'rb') as fh:
            must(bool(fh.read(1)), 'EMPTY_SQL')
            while fh.read(1024 * 1024):
                pass
    elif kind == 'config':
        must(path.name.endswith('-site_config_backup.json'), 'CONFIG_BACKUP_TYPE')
        with path.open(encoding='utf-8') as fh:
            must(isinstance(json.load(fh), dict), 'BAD_CONFIG_JSON')
    else:
        suffix = '-private-files.tar' if kind == 'private' else '-files.tar'
        must(path.name.endswith(suffix), 'TAR_BACKUP_TYPE')
        with tarfile.open(path, 'r:') as fh:
            for member in fh:
                must(not member.issym() and not member.islnk(), 'ARCHIVE_LINK_UNEXPECTED')
                if member.isfile():
                    source = fh.extractfile(member)
                    must(source is not None, 'ARCHIVE_ENTRY_INVALID')
                    with source:
                        while source.read(1024 * 1024):
                            pass
    return sha256(path)


def main():
    os.umask(0o077)
    must(os.geteuid() != 0 and Path.cwd() == BENCH / 'sites', 'CONTAINER_IDENTITY')
    must(APP.is_dir() and not APP.is_symlink(), 'APP_ROOT')
    must(git('rev-parse', 'HEAD') == EXPECTED_HEAD, 'SOURCE_SHA_CHANGED')
    must(subprocess.run(['git', '-C', str(APP), 'symbolic-ref', '-q', '--short', 'HEAD'],
                        capture_output=True, text=True, timeout=30).returncode == 1,
         'SOURCE_NOT_DETACHED')
    must(git('status', '--porcelain=v1', '--untracked-files=all') == '?? AGENTS.md',
         'SOURCE_WORKTREE_CHANGED')
    protected = APP / 'AGENTS.md'
    must(protected.is_file() and not protected.is_symlink(), 'PROTECTED_AGENTS_CHANGED')
    must(not git('ls-tree', '-r', '--name-only', 'HEAD', '--', 'AGENTS.md'),
         'AGENTS_TRACKED_UNEXPECTEDLY')
    spec = importlib.util.find_spec('ccpcerp')
    must(spec is not None and spec.origin and Path(spec.origin).resolve()
         == (APP / 'ccpcerp/__init__.py').resolve(), 'APP_IMPORT_PATH_CHANGED')
    must(ROOT.is_dir() and not ROOT.is_symlink(), 'SNAPSHOT_ROOT_UNAVAILABLE')
    must(ROOT.stat().st_uid == os.geteuid(), 'SNAPSHOT_OWNER_CHANGED')
    must(stat.S_IMODE(ROOT.stat().st_mode) & 0o077 == 0,
         'SNAPSHOT_ROOT_NOT_PRIVATE')
    must(os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize >= 2 * 1024**3,
         'LOCAL_SPACE_LOW')
    for site in SITES:
        p = BENCH / 'sites' / site
        must(p.is_dir() and not p.is_symlink()
             and (p / 'site_config.json').is_file(), 'SITE_NOT_AVAILABLE')
    import frappe
    from frappe.utils.backups import BackupGenerator
    from frappe.utils import cint

    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    token = secrets.token_hex(6)
    names = []
    for site in SITES:
        stage = ROOT / ('.partial-' + site + '-' + timestamp + '-' + token)
        dest = ROOT / (site + '-' + timestamp + '-' + token)
        must(not stage.exists() and not dest.exists(), 'BACKUP_NAME_COLLISION')
        stage.mkdir(mode=0o700)
        try:
            frappe.init(site=site, sites_path=str(BENCH / 'sites'))
            frappe.connect()
            must(frappe.local.site == site, 'FRAPPE_SITE_MISMATCH')
            must(not cint(frappe.get_system_settings('encrypt_backup')),
                 'ENCRYPTED_BACKUP_NOT_SUPPORTED')
            bg = BackupGenerator(
                frappe.conf.db_name, frappe.conf.db_user, frappe.conf.db_password,
                db_socket=frappe.conf.db_socket, db_host=frappe.conf.db_host,
                db_port=frappe.conf.db_port, db_type=frappe.conf.db_type,
                backup_path=str(stage), ignore_conf=True, compress_files=False,
                verbose=False,
            )
            bg.get_backup(force=True, ignore_files=False)
            files = {
                'database': Path(bg.backup_path_db),
                'config': Path(bg.backup_path_conf),
                'public': Path(bg.backup_path_files),
                'private': Path(bg.backup_path_private_files),
            }
            must(len(set(files.values())) == 4, 'BACKUP_PATH_COLLISION')
            must({p.name for p in stage.iterdir()} == {p.name for p in files.values()},
                 'UNEXPECTED_BACKUP_FILES')
            hashes = {name: validate_artifact(name, path, stage)
                      for name, path in files.items()}
            with (stage / 'SHA256SUMS').open('x', encoding='utf-8') as out:
                for kind in ('database', 'config', 'public', 'private'):
                    out.write(hashes[kind] + '  ' + files[kind].name + '\n')
            os.chmod(stage / 'SHA256SUMS', 0o600)
            must(len(tuple(stage.iterdir())) == 5, 'BACKUP_FINAL_FILE_COUNT')
            stage.rename(dest)
            names.append(dest.name)
        finally:
            frappe.destroy()
    for name in names:
        print('CCPC_NEW_SNAPSHOT=' + name, flush=True)
    print('CCPC_NEW_LOCAL_TWO_SITE_BACKUPS=PASS', flush=True)


try:
    main()
except Exception:
    # Do not dump Frappe tracebacks, database credentials or private data.
    print('STOP: DEVELOPMENT backup creation failed; partial files (if any) retained.',
          file=sys.stderr)
    sys.exit(1)
'''


def main():
    must(os.geteuid() != 0 and pwd.getpwuid(os.getuid()).pw_name == 'gani', 'HOST_OPERATOR')
    must(os.uname().nodename.split('.')[0] == 'ccpcerpserver', 'WRONG_HOST')
    running = run(['sudo', '-n', 'docker', 'inspect', '--format', '{{.State.Running}}', CONTAINER])
    project = run(['sudo', '-n', 'docker', 'inspect', '--format',
                   '{{index .Config.Labels "com.docker.compose.project"}}', CONTAINER])
    must(running == 'true' and project == PROJECT, 'WRONG_DEV_CONTAINER')
    mount = run(['findmnt', '-rn', '-M', str(NAS), '-o', 'SOURCE,FSTYPE'])
    must(mount == EXPECTED_MOUNT, 'WRONG_NAS_MOUNT')
    must(NAS.is_dir() and not NAS.is_symlink(), 'NAS_UNAVAILABLE')
    must(HOST_SNAPSHOTS.is_dir() and not HOST_SNAPSHOTS.is_symlink(),
         'HOST_SNAPSHOT_ROOT_UNAVAILABLE')
    # Guard against concurrent runs; the lock persists but is not a backup file.
    lockpath = Path.home() / '.ccpc-phase1-two-site-backup.lock'
    fd = os.open(lockpath, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'rb') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('ANOTHER_BACKUP_RUNNING')
        print('DEV CONTAINER/NAS PRECHECK: PASS', flush=True)
        print('CREATING TWO LOCAL DEV BACKUPS (NO SITE MIGRATION)', flush=True)
        cp = subprocess.run(
            ['sudo', '-n', 'docker', 'exec', '-i', '--user', 'frappe',
             '--workdir', '/workspace/development/frappe-bench/sites',
             CONTAINER, '/workspace/development/frappe-bench/env/bin/python', '-B', '-'],
            input=CONTAINER_CODE, capture_output=True, text=True,
            timeout=7200,
        )
        must(cp.returncode == 0, 'LOCAL_BACKUP_FAILED_PRESERVE_PARTIALS')
        names = [line.split('=', 1)[1] for line in cp.stdout.splitlines()
                 if line.startswith('CCPC_NEW_SNAPSHOT=')]
        must('CCPC_NEW_LOCAL_TWO_SITE_BACKUPS=PASS' in cp.stdout.splitlines(),
             'LOCAL_SUCCESS_MARKER_MISSING')
        must(len(names) == 2 and all(re.fullmatch(
            re.escape(site) + r'-\d{8}T\d{6}Z-[0-9a-f]{12}', name)
            for site, name in zip(SITES, names)), 'SNAPSHOT_NAMES_INVALID')
        records = {}
        for name in names:
            records[name] = verify_snapshot(HOST_SNAPSHOTS / name)
        print('LOCAL DEV SNAPSHOTS: 2/2, FOUR FILES EACH, SHA256 PASS', flush=True)

        total = sum((HOST_SNAPSHOTS / name / filename).stat().st_size
                    for name, files in records.items() for filename in files)
        free = os.statvfs(NAS)
        must(free.f_bavail * free.f_frsize >= max(1024**3, 2 * total),
             'NAS_SPACE_LOW')
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        token = secrets.token_hex(8)
        basename = 'ccpc-development-phase1-two-site-preswitch-' + stamp + '-' + token
        partial = NAS / ('.partial-' + basename)
        dest = NAS / basename
        must(not partial.exists() and not dest.exists(), 'NAS_DESTINATION_EXISTS')
        partial.mkdir(mode=0o700)
        print('COPYING BOTH SNAPSHOTS TO VERIFIED NAS', flush=True)
        lines = []
        for name in names:
            srcdir = HOST_SNAPSHOTS / name
            dstdir = partial / name
            dstdir.mkdir(mode=0o700)
            for filename, sha in records[name].items():
                src = srcdir / filename
                dst = dstdir / filename
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
                fd = os.open(dst, flags, 0o600)
                with os.fdopen(fd, 'wb') as out, src.open('rb') as incoming:
                    shutil.copyfileobj(incoming, out, 1024 * 1024)
                    out.flush()
                    os.fsync(out.fileno())
                must(src.stat().st_size == dst.stat().st_size
                     and digest(src) == sha and digest(dst) == sha,
                     'NAS_COPIED_HASH_MISMATCH')
                lines.append(sha + '  ' + name + '/' + filename + '\n')
            manifest_src = srcdir / 'SHA256SUMS'
            manifest_dst = dstdir / 'SHA256SUMS'
            fd = os.open(manifest_dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'wb') as out, manifest_src.open('rb') as incoming:
                shutil.copyfileobj(incoming, out)
                out.flush()
                os.fsync(out.fileno())
            must(digest(manifest_src) == digest(manifest_dst), 'NAS_MANIFEST_COPY_MISMATCH')
            must(verify_snapshot(dstdir) == records[name], 'NAS_MANIFEST_CONTENT_MISMATCH')
        must(len(lines) == 8, 'NAS_GLOBAL_ENTRY_COUNT')
        global_manifest = partial / 'SHA256SUMS'
        with global_manifest.open('x', encoding='utf-8') as out:
            out.writelines(lines)
            out.flush()
            os.fsync(out.fileno())
        must(set(p.name for p in partial.iterdir()) == {*names, 'SHA256SUMS'},
             'NAS_DESTINATION_CONTENTS')
        for line in lines:
            sha, relative = line.rstrip('\n').split('  ', 1)
            must(digest(partial / relative) == sha, 'NAS_FINAL_SHA256_MISMATCH')
        partial.rename(dest)
        print('NAS DEV SNAPSHOTS: 2/2, FOUR FILES EACH, SHA256 PASS', flush=True)
        print('LOCAL/NAS BACKUPS: MATCH', flush=True)
        print('MAIN DEV SNAPSHOT: ' + names[0], flush=True)
        print('INTEGRATION2 DEV SNAPSHOT: ' + names[1], flush=True)
        print('FINAL NAS BACKUP DIRECTORY: ' + str(dest), flush=True)
        print('PHASE1_TWO_SITE_OFFHOST_BACKUP: PASS', flush=True)
        print('RESTORE TEST: NOT PERFORMED', flush=True)
        print('SOURCE SWITCH / MIGRATION / RESTART: NOT PERFORMED', flush=True)


try:
    main()
except Exception as err:
    # Print only our own error codes; never dump Frappe's captured stdout or secrets.
    code = err.args[0] if isinstance(err, RuntimeError) and err.args else 'BACKUP_EXECUTION_FAILED'
    if not re.fullmatch(r'[A-Z0-9_]+', str(code)):
        code = 'BACKUP_EXECUTION_FAILED'
    print('STOP: ' + str(code) + ' (inspect privately; do not retry blindly)', file=sys.stderr)
    sys.exit(1)
PY
