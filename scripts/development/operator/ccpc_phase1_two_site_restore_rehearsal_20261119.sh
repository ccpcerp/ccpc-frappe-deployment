#!/usr/bin/env bash
# Two-site CCPC DEVELOPMENT recovery test. Never restores to a live site.
set -euo pipefail
umask 077
[[ "$(hostname -s)" == ccpcerpserver && "$(id -un)" == gani ]] || { echo 'STOP: WRONG_HOST_OR_OPERATOR' >&2; exit 1; }
[[ "${CCPC_APPROVE_PHASE1_ISOLATED_RESTORE:-}" == YES ]] || { echo 'STOP: RESTORE_APPROVAL_FLAG_MISSING' >&2; exit 1; }
sudo -v
python3 -B - <<'PY'
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import pwd
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time

SITES = (
    ('development.localhost', 'development.localhost-20261118T233442Z-8db803832468', 'ccpc_rehearsal_main'),
    ('ccpc-integration2.localhost', 'ccpc-integration2.localhost-20261118T233442Z-8db803832468', 'ccpc_rehearsal_int2'),
)
NAS = Path('/mnt/erpnext_backups')
NAS_SET = NAS / 'ccpc-development-phase1-two-site-preswitch-20261118T233444Z-35c00130d53b457e'
LOCAL = Path('/home/gani/deployments/frappe_docker/development/frappe-bench/.ccpc-pr32-snapshots')
IMAGE = 'docker.io/mariadb:11.8'
CONTAINER_DEV = 'frappe_docker_devcontainer-frappe-1'
COMPOSE = 'frappe_docker_devcontainer'
MAX_EXTRACT = 40 * 1024**3  # STOP rather than filling the server disk


def must(condition, code):
    if not condition:
        raise RuntimeError(code)


def command(args, input_bytes=None, timeout=40):
    p = subprocess.run(args, input=input_bytes, stdout=subprocess.PIPE,
                       stderr=subprocess.DEVNULL, timeout=timeout, check=False)
    must(p.returncode == 0, 'COMMAND_FAILED')
    return p.stdout.decode('utf-8', errors='replace').strip()


def checksum(path):
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1048576), b''):
            digest.update(data)
    return digest.hexdigest()


def kind(filename):
    if filename.endswith('-database.sql.gz'):
        return 'database'
    if filename.endswith('-site_config_backup.json'):
        return 'config'
    if filename.endswith('-private-files.tar'):
        return 'private'
    if filename.endswith('-files.tar'):
        return 'public'
    return None


def verify_set(directory):
    must(directory.is_dir() and not directory.is_symlink(), 'BACKUP_DIRECTORY_INVALID')
    entries = list(directory.iterdir())
    must(len(entries) == 5 and all(x.is_file() and not x.is_symlink() for x in entries),
         'BACKUP_COMPONENT_COUNT')
    manifest = directory / 'SHA256SUMS'
    must(manifest.is_file() and not manifest.is_symlink(), 'MANIFEST_MISSING')
    lines = manifest.read_text(encoding='utf-8').splitlines()
    must(len(lines) == 4, 'MANIFEST_COUNT')
    result = {}
    for line in lines:
        m = re.fullmatch(r'([a-f0-9]{64})  ([A-Za-z0-9._-]+)', line)
        must(bool(m), 'MANIFEST_FORMAT')
        digest, filename = m.groups()
        type_ = kind(filename)
        must(type_ and type_ not in result, 'MANIFEST_DUPLICATE_OR_UNKNOWN')
        f = directory / filename
        must(f.is_file() and not f.is_symlink() and f.stat().st_size > 0,
             'BACKUP_COMPONENT_INVALID')
        must(checksum(f) == digest, 'BACKUP_CHECKSUM_MISMATCH')
        result[type_] = (f, digest)
    must(set(result) == {'database', 'config', 'public', 'private'}, 'BACKUP_TYPES')
    must({x.name for x in entries} == {'SHA256SUMS'} | {v[0].name for v in result.values()},
         'BACKUP_UNEXPECTED_FILE')
    return result


def inspect_tar_members(file):
    total = 0
    count = 0
    with tarfile.open(file, 'r:') as archive:
        for member in archive:
            p = PurePosixPath(member.name)
            must(member.name and not member.name.startswith('/') and '..' not in p.parts,
                 'UNSAFE_TAR_PATH')
            must(member.isfile() or member.isdir(), 'UNSAFE_TAR_ENTRY')
            if member.isfile():
                total += member.size
                count += 1
    must(total <= MAX_EXTRACT, 'TAR_EXTRACT_SIZE_LIMIT')
    return count, total


def extract_tar(file, dest):
    dest.mkdir(mode=0o700)
    total_count = 0
    with tarfile.open(file, 'r:') as archive:
        for member in archive:
            p = PurePosixPath(member.name)
            must(member.name and not member.name.startswith('/') and '..' not in p.parts,
                 'UNSAFE_TAR_PATH')
            must(member.isfile() or member.isdir(), 'UNSAFE_TAR_ENTRY')
            target = dest.joinpath(*p.parts)
            if member.isdir():
                target.mkdir(mode=0o700, parents=True, exist_ok=True)
                must(target.is_dir() and not target.is_symlink(), 'TAR_DIRECTORY_COLLISION')
                continue
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
            fd = os.open(target, flags, 0o600)
            source = archive.extractfile(member)
            must(source is not None, 'TAR_SOURCE_FILE_MISSING')
            with os.fdopen(fd, 'wb') as output, source:
                shutil.copyfileobj(source, output, 1048576)
            must(target.stat().st_size == member.size, 'TAR_FILE_SIZE_MISMATCH')
            total_count += 1
    return total_count


def docker(*args, input_bytes=None, timeout=40):
    return command(['sudo', '-n', 'docker', *args], input_bytes, timeout)


def docker_sql(container, secret, sql):
    return docker('exec', '-e', 'MYSQL_PWD=' + secret, container,
                  'mariadb', '--protocol=socket', '-uroot', '-N', '-B', '-e', sql,
                  timeout=60)


def import_sql(container, secret, db_name, source):
    proc = subprocess.Popen(
        ['sudo', '-n', 'docker', 'exec', '-i', '-e', 'MYSQL_PWD=' + secret,
         container, 'mariadb', '--protocol=socket', '-uroot', db_name],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        with gzip.open(source, 'rb') as dump:
            while True:
                chunk = dump.read(1048576)
                if not chunk:
                    break
                proc.stdin.write(chunk)
        proc.stdin.close()
        must(proc.wait(timeout=3600) == 0, 'SQL_IMPORT_FAILED')
    except Exception:
        if proc.poll() is None:
            proc.kill()
        proc.wait()
        raise


def main():
    must(os.geteuid() != 0 and pwd.getpwuid(os.getuid()).pw_name == 'gani',
         'UNAUTHORIZED_OPERATOR')
    must(os.uname().nodename.split('.')[0] == 'ccpcerpserver', 'HOST_MISMATCH')
    running = docker('inspect', '--format', '{{.State.Running}}', CONTAINER_DEV)
    project = docker('inspect', '--format', '{{index .Config.Labels "com.docker.compose.project"}}',
                     CONTAINER_DEV)
    must(running == 'true' and project == COMPOSE, 'DEV_CONTAINER_MISMATCH')
    must(command(['findmnt', '-rn', '-M', str(NAS), '-o', 'SOURCE,FSTYPE'])
         == '//192.168.50.132/erpnext_backups cifs', 'NAS_MOUNT_MISMATCH')
    must(NAS_SET.is_dir() and not NAS_SET.is_symlink(), 'NAMED_NAS_SET_MISSING')
    must(LOCAL.is_dir() and not LOCAL.is_symlink(), 'LOCAL_SNAPSHOT_ROOT_MISSING')
    must(docker('image', 'inspect', '--format', '{{.Id}}', IMAGE).startswith('sha256:'),
         'OFFLINE_MARIADB_IMAGE_NOT_INSTALLED')
    must(shutil.disk_usage('/').free >= 8 * 1024**3, 'HOST_FREE_SPACE_TOO_LOW')
    mem = Path('/proc/meminfo').read_text().splitlines()
    available = next((int(line.split()[1]) * 1024 for line in mem
                      if line.startswith('MemAvailable:')), 0)
    must(available >= 5 * 1024**3, 'HOST_AVAILABLE_MEMORY_TOO_LOW')

    # A nonblocking lock prevents simultaneous rehearsal invocations.
    lock = Path('/home/gani/.ccpc-phase1-isolated-restore.lock')
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'rb') as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('ANOTHER_RESTORE_REHEARSAL_RUNNING')
        restored = []
        extracted_bytes = 0
        for site, folder, dbname in SITES:
            local = verify_set(LOCAL / folder)
            nas = verify_set(NAS_SET / folder)
            must({t: local[t][1] for t in local} == {t: nas[t][1] for t in nas},
                 'LOCAL_NAS_HASH_MISMATCH')
            for category in ('public', 'private'):
                _, bytes_ = inspect_tar_members(nas[category][0])
                extracted_bytes += bytes_
            with nas['config'][0].open(encoding='utf-8') as cfg:
                must(isinstance(json.load(cfg), dict), 'CONFIG_NOT_JSON_OBJECT')
            restored.append((site, dbname, nas))
        must(shutil.disk_usage('/home/gani').free >= extracted_bytes + 4 * 1024**3,
             'INSUFFICIENT_ISOLATED_EXTRACT_SPACE')
        print('TWO LOCAL/NAS BACKUP SETS: 8/8 SHA256 PASS', flush=True)
        print('OFFLINE MARIA DB IMAGE / DEV IDENTITY: VERIFIED', flush=True)

        # This directory is exclusively private rehearsal scratch, never bench/sites.
        scratch = Path(tempfile.mkdtemp(prefix='.ccpc-phase1-restore-', dir='/home/gani'))
        os.chmod(scratch, 0o700)
        container = 'ccpc-restore-' + secrets.token_hex(7)
        password = secrets.token_urlsafe(32)
        started = False
        try:
            for site, db_name, nas in restored:
                folder = scratch / db_name
                folder.mkdir(mode=0o700)
                cfg = folder / 'site_config_backup.json'
                with cfg.open('xb') as out, nas['config'][0].open('rb') as source:
                    shutil.copyfileobj(source, out, 1048576)
                os.chmod(cfg, 0o600)
                for kind_ in ('public', 'private'):
                    restored_count = extract_tar(nas[kind_][0], folder / kind_)
                    must(restored_count == inspect_tar_members(nas[kind_][0])[0],
                         'TAR_RESTORED_FILE_COUNT_MISMATCH')
                print('ISOLATED FILES/CONFIG RESTORE: ' + db_name + ' PASS', flush=True)

            # The container has NO network, published ports, host folders, SSH keys,
            # bench mounts, NAS mounts or Docker socket mounts. --rm destroys its
            # anonymous database volume on stop. Docker resource limits bound impact.
            docker('run', '-d', '--rm', '--name', container,
                   '--network', 'none', '--pids-limit', '256', '--memory', '3g',
                   '--memory-swap', '3g', '--cpus', '2',
                   '--security-opt', 'no-new-privileges',
                   '--label', 'ccpc.purpose=isolated-two-site-restore',
                   '-e', 'MARIADB_ROOT_PASSWORD=' + password,
                   '-e', 'MARIADB_INITDB_SKIP_TZINFO=1', IMAGE, timeout=120)
            started = True
            network = docker('inspect', '--format', '{{.HostConfig.NetworkMode}}', container)
            privileged = docker('inspect', '--format', '{{.HostConfig.Privileged}}', container)
            exposed = docker('inspect', '--format', '{{json .HostConfig.PortBindings}}', container)
            must(network == 'none' and privileged == 'false' and exposed in ('null', '{}'),
                 'ISOLATED_CONTAINER_CONFIGURATION_MISMATCH')
            print('DISPOSABLE MARIADB: NETWORK NONE, NO PORTS, RESOURCE LIMITED', flush=True)
            ready = False
            for _ in range(90):
                try:
                    result = docker('exec', '-e', 'MYSQL_PWD=' + password, container,
                                    'mariadb-admin', '--protocol=socket', '-uroot', 'ping',
                                    timeout=5)
                    if 'alive' in result:
                        ready = True
                        break
                except (RuntimeError, subprocess.TimeoutExpired):
                    time.sleep(2)
            must(ready, 'ISOLATED_DATABASE_STARTUP_FAILED')
            for site, db_name, nas in restored:
                must(bool(re.fullmatch(r'[A-Za-z0-9_]+', db_name)), 'UNSAFE_DB_NAME')
                docker_sql(container, password,
                           'CREATE DATABASE `' + db_name + '` CHARACTER SET utf8mb4;')
                import_sql(container, password, db_name, nas['database'][0])
                count_text = docker_sql(container, password,
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='" + db_name + "';")
                must(int(count_text) >= 20, 'RESTORED_DATABASE_TABLE_COUNT_TOO_LOW')
                # Standard Frappe metadata table proves real SQL, not just empty DDL.
                doc_count = docker_sql(container, password,
                    'SELECT COUNT(*) FROM `' + db_name + '`.`tabDocType`;')
                must(int(doc_count) > 0, 'RESTORED_FRAPPE_DOCTYPE_EMPTY')
                print('ISOLATED SQL RESTORE: ' + db_name + ' PASS', flush=True)
            print('TWO-SITE ISOLATED SQL + FILE RECOVERY: PASS', flush=True)
            print('FULL FRAPPE SITE BOOT / APP UAT: NOT TESTED', flush=True)
            print('LIVE DEV / PROD SOURCE, DB, SERVICES: NOT MODIFIED', flush=True)
        finally:
            if started:
                # Stop only the unique container created by THIS run.
                stop = subprocess.run(['sudo', '-n', 'docker', 'stop', '-t', '12', container],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                      timeout=50, check=False)
                must(stop.returncode == 0, 'RESTORE_CONTAINER_CLEANUP_FAILED')
            # Refuse to delete scratch if owned by unexpected path.
            must(scratch.parent == Path('/home/gani') and scratch.name.startswith('.ccpc-phase1-restore-')
                 and scratch.is_dir() and not scratch.is_symlink(), 'SCRATCH_CLEANUP_GUARD')
            shutil.rmtree(scratch)
            print('ISOLATED SCRATCH CLEANUP: PASS', flush=True)
        print('PHASE1_TWO_SITE_ISOLATED_RESTORE_REHEARSAL: PASS', flush=True)

try:
    main()
except Exception as e:
    code = str(e) if isinstance(e, RuntimeError) and re.fullmatch(r'[A-Z0-9_]+', str(e)) else 'RESTORE_REHEARSAL_FAILED'
    print('STOP: ' + code + '. Do not retry automatically; review only operator-safe outputs.',
          file=sys.stderr)
    raise SystemExit(1)
PY
