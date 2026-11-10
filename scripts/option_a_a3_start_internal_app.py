#!/usr/bin/env python3
"""One-use Option A A3: start only NEW internal backend/websocket/frontend.

Source-reviewed NEW-host candidate acceptance, not an employee deployment. This
script preserves any partial state on STOP; never blindly rerun. No Compose up,
worker, scheduler, configurator, SQL restore/migration, host port or OLD write.
"""
import json
import os
from pathlib import Path
import pwd
import subprocess
import sys
import time

PROJECT = 'ccpc_prod_erpnext'
NETWORK = PROJECT + '_default'
SITE_VOLUME = PROJECT + '_sites'
LOGS_VOLUME = PROJECT + '_logs'
SITE_PATH = '/var/lib/docker/volumes/' + SITE_VOLUME + '/_data'
LOGS_PATH = '/var/lib/docker/volumes/' + LOGS_VOLUME + '/_data'
APP_ID = 'sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8'
DB_ID = 'sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4'
REDIS_ID = 'sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763'
REHEARSAL_PROJECTS = ('ccpc_restore_rehearsal_20261107', 'ccpc_full_acceptance_20261107')
SUPPORT = {f'{p}-{s}-1' for p in (*REHEARSAL_PROJECTS, PROJECT)
           for s in ('db', 'redis-cache', 'redis-queue')}
APP = {role: f'{PROJECT}-{role}-1' for role in ('backend', 'websocket', 'frontend')}
VOLUMES = {f'{p}_{v}' for p in (*REHEARSAL_PROJECTS, PROJECT)
           for v in ('db-data', 'logs', 'redis-queue-data', 'sites')}
NETWORKS = {'bridge', 'host', 'none', NETWORK,
            'ccpc_restore_rehearsal_20261107_default',
            'ccpc_full_acceptance_20261107_default'}


def stop(reason):
    print('STOP:A3_APP_' + reason, flush=True)
    raise SystemExit(1)


def process(args, timeout=30, *, expected=True):
    try:
        result = subprocess.run(args, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        stop('COMMAND_TIMEOUT_OR_UNAVAILABLE')
    if expected and result.returncode:
        stop('COMMAND_FAILED_RETAIN_STATE')
    return result


def docker(*args, timeout=30):
    return process(['sudo', 'docker', *args], timeout).stdout.decode('utf-8', 'replace').strip()


def inspect(kind, name):
    try:
        return json.loads(docker(kind, 'inspect', name))[0]
    except (ValueError, KeyError, IndexError, TypeError):
        stop('INVALID_DOCKER_INSPECT')


def names(*args):
    return set(docker(*args).splitlines())


def container_guard(name, image, expected_network):
    state = inspect('container', name)
    if state.get('Image') != image or not state.get('State', {}).get('Running'):
        stop('CONTAINER_NOT_RUNNING_OR_IMAGE')
    if (state.get('HostConfig', {}).get('PortBindings') or
            state.get('NetworkSettings', {}).get('Ports') and any(
                v for v in state['NetworkSettings']['Ports'].values())):
        stop('UNEXPECTED_PUBLISHED_PORT')
    if set(state.get('NetworkSettings', {}).get('Networks', {})) != {expected_network}:
        stop('UNEXPECTED_CONTAINER_NETWORK')
    return state


if (os.uname().nodename.split('.')[0] != 'ccpcerp-prod'
        or os.geteuid() == 0 or pwd.getpwuid(os.getuid()).pw_name != 'ccpcadmin'
        or os.environ.get('USER') != 'ccpcadmin'):
    stop('HOST_OR_OPERATOR')
if any(k in os.environ for k in
       ('DOCKER_HOST', 'DOCKER_CONTEXT', 'COMPOSE_FILE', 'COMPOSE_PROJECT_NAME', 'DB_PASSWORD')):
    stop('AMBIENT_OVERRIDE')
if docker('context', 'show') != 'default' or docker(
        'context', 'inspect', 'default', '--format', '{{.Endpoints.docker.Host}}'
) != 'unix:///var/run/docker.sock':
    stop('DOCKER_TARGET')
if (names('ps', '-a', '--format', '{{.Names}}') != SUPPORT or
        names('ps', '--format', '{{.Names}}') != SUPPORT or
        names('volume', 'ls', '--format', '{{.Name}}') != VOLUMES or
        names('network', 'ls', '--format', '{{.Name}}') != NETWORKS):
    stop('EXISTING_RESOURCE_INVENTORY_CHANGED')
for name in SUPPORT:
    network = NETWORK if name.startswith(PROJECT + '-') else name.rsplit('-', 2)[0] + '_default'
    image = DB_ID if name.endswith('-db-1') else REDIS_ID
    container_guard(name, image, network)
if inspect('container', PROJECT + '-db-1').get('State', {}).get('Health', {}).get('Status') != 'healthy':
    stop('CANDIDATE_DB_HEALTH')
for tag, immutable in (('ccpcerp:v16.50.0', APP_ID),
                       ('mariadb:11.8', DB_ID), ('redis:8.6-alpine', REDIS_ID)):
    if docker('image', 'inspect', '--format', '{{.Id}}', tag) != immutable:
        stop('PINNED_IMAGE_CHANGED')
net = inspect('network', NETWORK)
if (net.get('Internal') is not True or net.get('Attachable') is not False or
        net.get('Driver') != 'bridge' or
        (net.get('Labels') or {}).get('com.docker.compose.project') != PROJECT or
        set((obj.get('Name') for obj in (net.get('Containers') or {}).values())) !=
        {f'{PROJECT}-{s}-1' for s in ('db', 'redis-cache', 'redis-queue')}):
    stop('NETWORK_ISOLATION_CHANGED')
for vol in ('sites', 'logs', 'db-data', 'redis-queue-data'):
    item = inspect('volume', f'{PROJECT}_{vol}')
    path = f'/var/lib/docker/volumes/{PROJECT}_{vol}/_data'
    labels = item.get('Labels') or {}
    if (item.get('Name') != f'{PROJECT}_{vol}' or item.get('Driver') != 'local'
            or item.get('Mountpoint') != path
            or labels.get('com.docker.compose.project') != PROJECT
            or labels.get('com.ccpc.stage') != 'option-a-a2'):
        stop('CANDIDATE_VOLUME_IDENTITY')

# Privileged read-only inspection: contents of site_config.json and private
# attachment file NAMES are never echoed. Reports only an exact PASS marker.
read_only_check = r'''
import json,os,pathlib,stat,sys
sites=pathlib.Path(sys.argv[1]); logs=pathlib.Path(sys.argv[2])
def node(p,kind,uid,gid,mode):
 s=p.lstat(); is_type=stat.S_ISDIR if kind=='dir' else stat.S_ISREG
 assert is_type(s.st_mode) and s.st_uid==uid and s.st_gid==gid and stat.S_IMODE(s.st_mode)==mode
node(sites,'dir',1000,1000,0o755)
node(logs,'dir',1000,1000,0o755)
assert not list(logs.iterdir())
assert {p.name for p in sites.iterdir()}=={'common_site_config.json','apps.txt','ccpcerp.local'}
node(sites/'common_site_config.json','file',1000,1000,0o600)
node(sites/'apps.txt','file',1000,1000,0o644)
assert (sites/'apps.txt').read_bytes()==b'frappe\nerpnext\nccpcerp\n'
site=sites/'ccpcerp.local'
node(site,'dir',1000,1000,0o755)
assert {p.name for p in site.iterdir()}=={'site_config.json','public','private'}
node(site/'site_config.json','file',1000,1000,0o600)
for name in ('public','private'):
 node(site/name,'dir',1000,1000,0o755)
 node(site/name/'files','dir',1000,1000,0o755)
assert not list((site/'public'/'files').iterdir())
private=list((site/'private'/'files').iterdir())
assert len(private)==1
node(private[0],'file',1000,1000,0o600)
common=json.loads((sites/'common_site_config.json').read_bytes())
config=json.loads((site/'site_config.json').read_bytes())
for c in (common,config):
 assert c.get('db_host')=='db' and c.get('db_port')==3306
 assert c.get('disable_scheduler')==1 and c.get('pause_scheduler')==1
 assert c.get('mute_emails')==1 and c.get('maintenance_mode')==0
 assert c.get('developer_mode')==0
assert common.get('redis_cache')=='redis://redis-cache:6379'
assert common.get('redis_queue')=='redis://redis-queue:6379'
assert common.get('redis_socketio')=='redis://redis-queue:6379'
assert isinstance(config.get('db_name'),str) and len(config['db_name'])>=4
assert isinstance(config.get('db_password'),str) and len(config['db_password'])==64
assert isinstance(config.get('encryption_key'),str) and len(config['encryption_key'])>=16
print('A3_CANDIDATE_SITE_LOGS_AND_SIDE_EFFECT_FLAGS_PASS')
'''
r = process(['sudo', 'python3', '-c', read_only_check, SITE_PATH, LOGS_PATH], timeout=20,
            expected=False)
if (r.returncode or r.stdout.decode('utf-8', 'replace').strip() !=
        'A3_CANDIDATE_SITE_LOGS_AND_SIDE_EFFECT_FLAGS_PASS'):
    stop('SITE_FILES_OR_PERMISSIONS_CHANGED')
print('A3_APP_PREFLIGHT_NINE_SUPPORT_CONTAINERS_AND_PRIVATE_NETWORK_PASS', flush=True)
print('A3_CANDIDATE_SITE_LOGS_AND_SIDE_EFFECT_FLAGS_PASS', flush=True)

# First mutation after all guards: three explicit names, no host ports, no
# Compose, no worker/scheduler. Each shares only the two candidate volumes.
base = [
    'run', '-d', '--pull=never', '--restart=no',
    '--network', NETWORK, '--security-opt', 'no-new-privileges',
    '--cap-drop=ALL', '--pids-limit=512', '--user', '1000:1000',
    '--label', 'com.ccpc.stage=option-a-a3',
    '--mount', f'type=volume,source={SITE_VOLUME},target=/home/frappe/frappe-bench/sites,volume-nocopy',
    '--mount', f'type=volume,source={LOGS_VOLUME},target=/home/frappe/frappe-bench/logs,volume-nocopy',
]


def start(role, extra, command):
    name = APP[role]
    docker(*base, '--name', name, '--network-alias', role, *extra,
           APP_ID, *command, timeout=90)
    # Preserve the partially started candidate on failures; never replay.
    state = container_guard(name, APP_ID, NETWORK)
    if (state.get('HostConfig', {}).get('RestartPolicy') or {}).get('Name') != 'no':
        stop('UNEXPECTED_APP_RESTART_POLICY')
    if (state.get('Config', {}).get('User') != '1000:1000' or
            (state.get('Config', {}).get('Labels') or {}).get('com.ccpc.stage') != 'option-a-a3'):
        stop('APP_IDENTITY')
    mounts = {(m.get('Name'), m.get('Destination')) for m in state.get('Mounts', [])}
    if mounts != {(SITE_VOLUME, '/home/frappe/frappe-bench/sites'),
                  (LOGS_VOLUME, '/home/frappe/frappe-bench/logs')}:
        stop('UNEXPECTED_APP_MOUNT')
    print('A3_' + role.upper() + '_STARTED_INTERNAL_ONLY_PASS', flush=True)


start('backend', ['--env', 'GUNICORN_WORKERS=2', '--env', 'GUNICORN_THREADS=4'], ['start.sh'])
start('websocket', [], ['node', '/home/frappe/frappe-bench/apps/frappe/socketio.js'])
start('frontend', ['--env', 'BACKEND=backend:8000', '--env', 'SOCKETIO=websocket:9000',
                   '--env', 'FRAPPE_SITE_NAME_HEADER=ccpcerp.local'], ['nginx-entrypoint.sh'])

if names('ps', '-a', '--format', '{{.Names}}') != SUPPORT | set(APP.values()):
    stop('POST_START_CONTAINER_INVENTORY')
if (names('volume', 'ls', '--format', '{{.Name}}') != VOLUMES or
        names('network', 'ls', '--format', '{{.Name}}') != NETWORKS):
    stop('POST_START_VOLUME_OR_NETWORK_INVENTORY')
for role, name in APP.items():
    container_guard(name, APP_ID, NETWORK)
for name in SUPPORT:
    network = NETWORK if name.startswith(PROJECT + '-') else name.rsplit('-', 2)[0] + '_default'
    container_guard(name, DB_ID if name.endswith('-db-1') else REDIS_ID, network)
print('A3_ALL_SIX_REHEARSAL_SERVICES_PRESERVED_PASS', flush=True)
print('A3_NO_PUBLISHED_PORTS_WORKERS_SCHEDULER_MIGRATION_PASS', flush=True)

# Use an *inside-frontend* HTTP GET. Never expose the service to office/LAN,
# print HTML, session tokens, private records, or container logs.
for attempt in range(25):
    curl = process([
        'sudo', 'docker', 'exec', APP['frontend'],
        'curl', '-sS', '--max-time', '6', '-o', '/dev/null',
        '-w', '%{http_code}', '-H', 'Host: ccpcerp.local',
        'http://127.0.0.1:8080/login'
    ], timeout=12, expected=False)
    status = curl.stdout.decode('ascii', 'ignore').strip()
    if curl.returncode == 0 and status == '200':
        print('A3_INTERNAL_ERPNext_LOGIN_HTTP_200_PASS', flush=True)
        print('A3_NEW_CANDIDATE_READY_FOR_AUTHENTICATED_ACCEPTANCE', flush=True)
        break
    if attempt < 24:
        time.sleep(2)
else:
    print('A3_INTERNAL_LOGIN_LAST_HTTP_STATUS=' + (status if status in ('000','301','302','400','401','403','404','500','502','503','504') else 'OTHER'), flush=True)
    stop('INTERNAL_LOGIN_HTTP_NOT_200_RETAIN_STATE')
