#!/usr/bin/env bash
# CCPC ERPNext: one-time reviewed READ-ONLY DEV/PROD database-boundary preflight.
# Preparation only. Run manually after separate pinned GitHub staging and approval.
# It reads site_config db_name inside isolated Docker containers but NEVER prints names.
# No database connection, Frappe init, Docker lifecycle operation or service mutation.
set -euo pipefail
umask 077
if [[ "$(id -u)" == 0 ]]; then
  printf '%s\n' 'STOP: run as the normal Ubuntu operator, not root.' >&2
  exit 1
fi
command -v docker >/dev/null 2>&1 || { printf '%s\n' 'STOP: Docker CLI unavailable.' >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { printf '%s\n' 'STOP: Python 3 unavailable.' >&2; exit 1; }
python3 - <<'PY'
"""Read-only Docker metadata and minimal site db-name identity check."""
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys

# These are the Compose project/service labels and site names documented in GitHub.
DEV_PROJECT, PROD_PROJECT = 'frappe_docker_devcontainer', 'frappe_docker'
DEV_SITES = '/workspace/development/frappe-bench/sites'
PROD_SITES = '/home/frappe/frappe-bench/sites'
DEV_SITE_NAMES = ('ccpc-integration2.localhost', 'development.localhost')
PROD_SITE_NAMES = ('ccpcerp.local',)

class SafeStop(Exception):
    pass

def stop(message):
    raise SafeStop(message)

def docker(*args, timeout=20):
    # No shell, no Docker exec -e secrets, and never show command output on error.
    try:
        run = subprocess.run(['docker', *args], text=True,
                             capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        stop('Docker read-only inspection could not complete')
    if run.returncode:
        stop('Docker read-only inspection was refused or unavailable')
    return run.stdout

def one_container(project, service):
    output = docker('ps', '-q', '--filter', f'label=com.docker.compose.project={project}',
                    '--filter', f'label=com.docker.compose.service={service}')
    rows = [v for v in output.splitlines() if v]
    if len(rows) != 1 or not re.fullmatch('[0-9a-f]{12,64}', rows[0]):
        stop('Expected exactly one running service for each documented Compose role')
    return rows[0]

def mounts(container):
    data = docker('inspect', '--format', '{{json .Mounts}}', container)
    try:
        mounts = json.loads(data)
    except (ValueError, TypeError):
        stop('Docker mount inspection returned invalid JSON')
    if not isinstance(mounts, list):
        stop('Docker mount inspection returned an unexpected result')
    return mounts

def mount_at(container, destination, expected_type=None):
    selected = [m for m in mounts(container) if m.get('Destination') == destination]
    if len(selected) != 1:
        stop('Expected service mount destination absent or ambiguous')
    selected = selected[0]
    if expected_type is not None and selected.get('Type') != expected_type:
        stop('Configured database storage has an unexpected mount type')
    path = selected.get('Source')
    if not isinstance(path, str) or not path.startswith('/'):
        stop('Unverifiable database storage mount source')
    return path.rstrip('/')

# Executed *inside* the relevant container; deliberately sends only a one-time
# keyed digest of each database name to the parent process (never db_name or password).
# No module imports from Frappe, no SQL, no cache operations, no file writes.
CHILD = r'''
import hashlib, hmac, json, os, stat, sys
root, nonce_hex, *sites = sys.argv[1:]
key = bytes.fromhex(nonce_hex)
if len(key) != 32 or len(sites) not in (1, 2):
    raise SystemExit(1)
result = []
for site in sites:
    if '/' in site or site in ('.', '..'):
        raise SystemExit(1)
    p = os.path.join(root, site, 'site_config.json')
    fd = os.open(p, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode) or os.fstat(fd).st_size > 65536:
            raise SystemExit(1)
        with os.fdopen(fd, 'rb') as stream:
            fd = None
            raw = stream.read(65537)
    finally:
        if fd is not None:
            os.close(fd)
    if len(raw) > 65536:
        raise SystemExit(1)
    v = json.loads(raw)
    name = v.get('db_name')
    if not isinstance(name, str) or not (1 <= len(name) <= 128):
        raise SystemExit(1)
    result.append(hmac.new(key, name.encode('utf-8'), hashlib.sha256).hexdigest())
print(json.dumps(result, separators=(',', ':')))
'''

def hashed_site_db_names(container, root, site_names, nonce):
    result = docker('exec', '--user', 'frappe', container, 'python3', '-c',
                    CHILD, root, nonce, *site_names, timeout=20)
    try:
        values = json.loads(result)
    except (ValueError, TypeError):
        stop('Read-only site database identity check returned invalid JSON')
    if not isinstance(values, list) or len(values) != len(site_names):
        stop('Read-only site database identity check returned unexpected shape')
    if any(not isinstance(v, str) or not re.fullmatch('[0-9a-f]{64}', v) for v in values):
        stop('Read-only site database identity check returned invalid digest')
    return values

try:
    dev_app = one_container(DEV_PROJECT, 'frappe')
    dev_db = one_container(DEV_PROJECT, 'mariadb')
    prod_app = one_container(PROD_PROJECT, 'backend')
    prod_db = one_container(PROD_PROJECT, 'db')
    if len(set((dev_app, dev_db, prod_app, prod_db))) != 4:
        stop('Database or application container boundaries overlap')
    print('FOUR DISTINCT RUNNING DEV/PROD COMPOSE SERVICE ROLES: VERIFIED', flush=True)

    # Site and database filesystem layout match the documented Compose design.
    dev_workspace = mount_at(dev_app, '/workspace', expected_type='bind')
    prod_sites = mount_at(prod_app, PROD_SITES, expected_type='volume')
    dev_db_source = mount_at(dev_db, '/var/lib/mysql', expected_type='volume')
    prod_db_source = mount_at(prod_db, '/var/lib/mysql', expected_type='volume')
    def sources_overlap(a, b):
        try:
            return os.path.commonpath((a, b)) in (a, b)
        except ValueError:
            return True
    if sources_overlap(dev_db_source, prod_db_source) or sources_overlap(dev_workspace, prod_sites):
        stop('Development and production persistent mount sources overlap')
    print('SEPARATE DEV/PROD MARIADB STORAGE MOUNTS: VERIFIED', flush=True)
    print('PRODUCTION SITES MOUNT DISTINCT FROM DEV WORKSPACE: VERIFIED', flush=True)

    nonce = secrets.token_hex(32)
    dev = hashed_site_db_names(dev_app, DEV_SITES, DEV_SITE_NAMES, nonce)
    prod = hashed_site_db_names(prod_app, PROD_SITES, PROD_SITE_NAMES, nonce)
    if len(set(dev + prod)) != 3:
        stop('At least two test/shared/production database names overlap')
    print('ISOLATED TEST, SHARED DEVELOPMENT AND PRODUCTION DB NAMES: DISTINCT', flush=True)
    print('ONLY SITE CONFIG DATABASE NAMES WERE READ; NO VALUES OR SECRETS PRINTED', flush=True)
    print('NO SQL, FRAPPE, STOCK, GL, BACKUP, DOCKER LIFECYCLE OR PRODUCTION DATA WRITE', flush=True)
    print('DATABASE CONFIGURATION ISOLATION READ-ONLY PREFLIGHT: PASSED', flush=True)
except SafeStop as exc:
    print('DATABASE CONFIGURATION ISOLATION PREFLIGHT: STOPPED', file=sys.stderr)
    print('CHECK:', str(exc), file=sys.stderr)
    print('NO AUTOMATIC RETRY OR FIX; INVESTIGATE SEPARATELY', file=sys.stderr)
    sys.exit(1)
PY
