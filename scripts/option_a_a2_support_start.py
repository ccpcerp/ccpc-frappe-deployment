#!/usr/bin/env python3
"""One-use, owner-approved NEW-only A2 isolated MariaDB/Redis foundation.

Consumes already existing empty ccpc_prod_erpnext network/volumes, protected Nov5
backup as preflight only, NEW existing images. No app, SQL restore or cutover.
Never blindly rerun; retain partial resources for inspection on failure.
"""
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time

PROJECT = 'ccpc_prod_erpnext'
NETWORK = PROJECT + '_default'
ROOT = Path('/home/ccpcadmin')
SECRETS = ROOT / '.ccpc-option-a-secrets-20261109'
BACKUP = ROOT / '.ccpc-nov05-backup-transfer-20261106'
APP_ID = 'sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8'
DB_ID = 'sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4'
REDIS_ID = 'sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763'
BACKUPS = {
    '20261105_020001-ccpcerp_local-database.sql.gz': '8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87',
    '20261105_020001-ccpcerp_local-files.tar': '200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6',
    '20261105_020001-ccpcerp_local-private-files.tar': '60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf',
    '20261105_020001-ccpcerp_local-site_config_backup.json': 'b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b',
}
REHEARSAL = {
    f'{project}-{service}-1'
    for project in ('ccpc_restore_rehearsal_20261107', 'ccpc_full_acceptance_20261107')
    for service in ('db', 'redis-cache', 'redis-queue')
}
CANDIDATE = {f'{PROJECT}-{service}-1' for service in ('db', 'redis-cache', 'redis-queue')}
VOL_OLD = {f'{project}_{name}' for project in ('ccpc_restore_rehearsal_20261107', 'ccpc_full_acceptance_20261107')
           for name in ('db-data', 'logs', 'redis-queue-data', 'sites')}
VOL_NEW = {f'{PROJECT}_{name}' for name in ('db-data', 'logs', 'redis-queue-data', 'sites')}
NETS = {'bridge', 'host', 'none', 'ccpc_restore_rehearsal_20261107_default',
        'ccpc_full_acceptance_20261107_default', NETWORK}
started = False


def stop(reason):
    print('STOP:A2_SUPPORT_' + reason, flush=True)
    raise SystemExit(1)


def process(args, *, timeout=25, expected=True):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        stop('COMMAND_TIMEOUT_OR_UNAVAILABLE')
    if expected and p.returncode:
        stop('DOCKER_COMMAND_FAILED')
    return p


def docker(*args, timeout=25):
    return process(['sudo', 'docker', *args], timeout=timeout).stdout.strip()


def docker_json(*args):
    try:
        return json.loads(docker(*args))
    except (ValueError, TypeError):
        stop('INVALID_DOCKER_METADATA')


def inventory(kind):
    return set(docker(*kind).splitlines())


def sha256_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while data := f.read(1024 * 1024):
            h.update(data)
    return h.hexdigest()


def write_private(path, body):
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(body)
        f.flush()
        os.fsync(f.fileno())


if os.uname().nodename.split('.')[0] != 'ccpcerp-prod' or os.getuid() == 0 or os.environ.get('USER') != 'ccpcadmin':
    stop('WRONG_HOST_OR_OPERATOR')
if any(k in os.environ for k in ('DOCKER_HOST', 'DOCKER_CONTEXT', 'COMPOSE_FILE', 'COMPOSE_PROJECT_NAME')):
    stop('AMBIENT_DOCKER_OVERRIDE')
if SECRETS.exists() or SECRETS.is_symlink():
    stop('EXISTING_SECRETS_DO_NOT_OVERWRITE')
if docker('context', 'show') != 'default':
    stop('DOCKER_CONTEXT')
if docker('context', 'inspect', 'default', '--format', '{{.Endpoints.docker.Host}}') != 'unix:///var/run/docker.sock':
    stop('DOCKER_SOCKET')
if inventory(('ps', '-a', '--format', '{{.Names}}')) != REHEARSAL:
    stop('EXISTING_CONTAINER_INVENTORY')
if inventory(('volume', 'ls', '--format', '{{.Name}}')) != VOL_OLD | VOL_NEW:
    stop('EXISTING_VOLUME_INVENTORY')
if inventory(('network', 'ls', '--format', '{{.Name}}')) != NETS:
    stop('EXISTING_NETWORK_INVENTORY')
for name in REHEARSAL:
    if docker('inspect', '--format', '{{.State.Running}}', name) != 'true':
        stop('REHEARSAL_NOT_RUNNING')
for ref, expected in (('ccpcerp:v16.50.0', APP_ID), ('mariadb:11.8', DB_ID), ('redis:8.6-alpine', REDIS_ID)):
    if docker('image', 'inspect', '--format', '{{.Id}}', ref) != expected:
        stop('IMAGE_ID')
network = docker_json('network', 'inspect', NETWORK)[0]
if network.get('Internal') is not True or network.get('Driver') != 'bridge' or network.get('Attachable') is not False:
    stop('INTERNAL_NETWORK')
if network.get('Containers'):
    stop('CANDIDATE_NETWORK_NOT_EMPTY')
if network.get('Labels', {}).get('com.docker.compose.project') != PROJECT:
    stop('NETWORK_OWNERSHIP')
for name in VOL_NEW:
    obj = docker_json('volume', 'inspect', name)[0]
    if obj.get('Driver') != 'local' or obj.get('Labels', {}).get('com.docker.compose.project') != PROJECT:
        stop('VOLUME_OWNERSHIP')
    if obj.get('Labels', {}).get('com.ccpc.stage') != 'option-a-a2':
        stop('VOLUME_STAGE')
    mp = obj.get('Mountpoint', '')
    if not mp or not mp.startswith('/var/lib/docker/volumes/') or not mp.endswith('/_data'):
        stop('VOLUME_MOUNTPOINT')
    # A2 foundation must have left these four volumes genuinely empty.
    if process(['sudo', 'find', mp, '-mindepth', '1', '-maxdepth', '1', '-print', '-quit']).stdout.strip():
        stop('CANDIDATE_VOLUME_NOT_EMPTY')
if not BACKUP.is_dir() or BACKUP.is_symlink():
    stop('BACKUP_PATH')
for name, digest in BACKUPS.items():
    p = BACKUP / name
    if not p.is_file() or p.is_symlink() or sha256_file(p) != digest:
        stop('NOV05_BACKUP_HASH')
print('A2_SUPPORT_PREFLIGHT_ALL_PROTECTED_RESOURCES_AND_NOV05_VERIFIED', flush=True)

# The first write in this one-use operation. Keep all partially created
# secrets/containers if any step fails so the operator can inspect safely.
try:
    SECRETS.mkdir(mode=0o700)
    root_password = secrets.token_hex(32)
    write_private(SECRETS / 'mariadb-root-password', root_password.encode('ascii'))
    write_private(SECRETS / 'db-client.cnf', ('[client]\nuser=root\npassword=' + root_password + '\nprotocol=socket\n').encode('ascii'))
    del root_password
except (OSError, ValueError):
    stop('SECRET_CREATION_PARTIAL')
print('A2_SUPPORT_NEW_PRIVATE_DB_SECRET_CREATED', flush=True)

db_name = f'{PROJECT}-db-1'
cache_name = f'{PROJECT}-redis-cache-1'
queue_name = f'{PROJECT}-redis-queue-1'

# No host -p, no automatic restarts/pulls, no remote networks or Compose up.
# Root host restricted to localhost: only socket auth inside DB container.
base = ['run', '-d', '--pull=never', '--restart=no', '--network', NETWORK,
        '--security-opt=no-new-privileges', '--pids-limit=512',
        '--label', 'com.ccpc.stage=option-a-a2']

docker(*base, '--name', db_name, '--network-alias', 'db',
       '--mount', f'type=volume,source={PROJECT}_db-data,target=/var/lib/mysql',
       '--mount', f'type=bind,source={SECRETS / "mariadb-root-password"},target=/run/secrets/mariadb-root-password,readonly',
       '--mount', f'type=bind,source={SECRETS / "db-client.cnf"},target=/run/secrets/db-client.cnf,readonly',
       '--env', 'MARIADB_ROOT_PASSWORD_FILE=/run/secrets/mariadb-root-password',
       '--env', 'MARIADB_ROOT_HOST=localhost',
       '--health-cmd', 'healthcheck.sh --connect --innodb_initialized',
       '--health-interval', '5s', '--health-timeout', '5s', '--health-retries', '15',
       DB_ID, '--character-set-server=utf8mb4',
       '--collation-server=utf8mb4_unicode_ci', '--skip-character-set-client-handshake', timeout=90)

for i in range(45):
    state = docker_json('inspect', db_name)[0]
    if not state['State']['Running']:
        stop('DB_STOPPED_RETAIN_FOR_INSPECTION')
    status = state['State'].get('Health', {}).get('Status', 'missing')
    if status == 'healthy':
        break
    if status == 'unhealthy':
        stop('DB_UNHEALTHY_RETAIN_FOR_INSPECTION')
    time.sleep(2)
else:
    stop('DB_HEALTH_TIMEOUT_RETAIN_FOR_INSPECTION')

# Password is supplied via a mounted on-container 0600 defaults file,
# never through argv, environment variables or terminal output.
if docker('exec', db_name, 'mariadb', '--defaults-extra-file=/run/secrets/db-client.cnf',
          '--batch', '--skip-column-names', '--execute=SELECT 1') != '1':
    stop('DB_ROOT_SOCKET_AUTH_FAILED')
print('A2_SUPPORT_DB_RUNNING_HEALTHY_ROOT_SOCKET_AUTH_PASS', flush=True)

docker(*base, '--name', cache_name, '--network-alias', 'redis-cache',
       '--tmpfs', '/data:rw,nosuid,nodev,size=64m',
       REDIS_ID, 'redis-server', '--protected-mode', 'no', '--save', '', '--appendonly', 'no', timeout=90)
docker(*base, '--name', queue_name, '--network-alias', 'redis-queue',
       '--mount', f'type=volume,source={PROJECT}_redis-queue-data,target=/data',
       REDIS_ID, 'redis-server', '--protected-mode', 'no', '--appendonly', 'yes', timeout=90)
for name in (cache_name, queue_name):
    for i in range(15):
        if docker('inspect', '--format', '{{.State.Running}}', name) != 'true':
            stop('REDIS_NOT_RUNNING_RETAIN_FOR_INSPECTION')
        if docker('exec', name, 'redis-cli', 'ping') == 'PONG':
            break
        time.sleep(1)
    else:
        stop('REDIS_PING_RETAIN_FOR_INSPECTION')
print('A2_SUPPORT_BOTH_REDIS_PING_PASS', flush=True)

if inventory(('ps', '-a', '--format', '{{.Names}}')) != REHEARSAL | CANDIDATE:
    stop('AFTER_CONTAINER_INVENTORY')
if inventory(('volume', 'ls', '--format', '{{.Name}}')) != VOL_OLD | VOL_NEW:
    stop('AFTER_VOLUME_INVENTORY')
if inventory(('network', 'ls', '--format', '{{.Name}}')) != NETS:
    stop('AFTER_NETWORK_INVENTORY')
for name in REHEARSAL:
    if docker('inspect', '--format', '{{.State.Running}}', name) != 'true':
        stop('AFTER_REHEARSAL_RUNNING')
for name in CANDIDATE:
    obj = docker_json('inspect', name)[0]
    if not obj['State']['Running'] or obj.get('HostConfig', {}).get('PortBindings'):
        stop('AFTER_SERVICE_OR_PORTS')
    nets = obj['NetworkSettings']['Networks']
    if set(nets) != {NETWORK}:
        stop('AFTER_NETWORK_ATTACHMENT')
print('A2_SUPPORT_THREE_CANDIDATE_SERVICES_ISOLATED_PASS', flush=True)
print('A2_SUPPORT_SIX_REHEARSAL_SERVICES_PRESERVED', flush=True)
print('A2_SUPPORT_NO_APP_SQL_IMPORT_WORKERS_OR_CUTOVER', flush=True)
