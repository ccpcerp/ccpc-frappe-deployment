#!/usr/bin/env python3
"""NEW A3 G1: exact-ID candidate Docker restart-policy transition.

NOT an approved operator command. GitHub review and offline tests only until
separately authorized. No container starts, stops, recreations or site writes.
--apply: only from six 'no' policies; --compensate: only a strict prefix of
known staged 'unless-stopped' policies, plus all 19 original identities.
"""
import argparse
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess

MANIFEST = Path('/var/lib/ccpc-new-a3-r0-manifest-20261113/manifest.json')
PREFIX = 'ccpc_prod_erpnext'
ROLES = ('db', 'redis-cache', 'redis-queue', 'backend', 'websocket', 'frontend')
CANDIDATES = tuple(f'{PREFIX}-{role}-1' for role in ROLES)
OTHER = tuple(f'{p}-{role}-1' for p in
              ('ccpc_full_acceptance_20261107', 'ccpc_restore_rehearsal_20261107')
              for role in ('redis-queue', 'redis-cache', 'db'))
DRILL = 'ccpc_a3_restore_drill_20261112'
DRILL_RUNNING = tuple(f'{DRILL}-{role}-1' for role in
                      ('frontend-completion1', 'websocket-completion1',
                       'backend-recovery1', 'redis-queue', 'redis-cache', 'db'))
DRILL_FAILED = f'{DRILL}-backend-1'
EXPECTED = set(CANDIDATES + OTHER + DRILL_RUNNING + (DRILL_FAILED,))
DOCKER = ('docker', '--host', 'unix:///var/run/docker.sock')
# Fail closed until separate, exact NEW-only mutation approval and source review.
# This is deliberately NOT a CLI flag or environment-variable override.
# Offline tests may patch this constant in memory; live default stays False.
G1_POLICY_MUTATION_REVIEWED = False
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
SITES = '/home/frappe/frappe-bench/sites'
LOGS = '/home/frappe/frappe-bench/logs'


class Stop(Exception):
    """Redacted terminal failure; never print private inspect data."""


def require(value):
    if not value:
        raise Stop()


def call(*args):
    try:
        proc = subprocess.run(DOCKER + args, check=True, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, timeout=25)
        require(len(proc.stdout) <= 1024 * 1024)
        return proc.stdout.decode('utf-8', 'strict')
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise Stop() from None


def operator():
    require(os.geteuid() == 0 and os.environ.get('SUDO_USER') == 'ccpcadmin')
    require(socket.gethostname().split('.')[0] == 'ccpcerp-prod')
    require(not any(k in os.environ for k in
                    ('DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_TLS_VERIFY',
                     'DOCKER_CERT_PATH', 'DOCKER_CONFIG')))


def manifest():
    try:
        parent, file = MANIFEST.parent.lstat(), MANIFEST.lstat()
        require(stat.S_ISDIR(parent.st_mode) and parent.st_uid == 0
                and stat.S_IMODE(parent.st_mode) == 0o700)
        require(stat.S_ISREG(file.st_mode) and file.st_uid == 0
                and stat.S_IMODE(file.st_mode) == 0o600 and file.st_size <= 65536)
        data = json.loads(MANIFEST.read_text(encoding='utf-8'))
        require(isinstance(data, dict) and data.get('schema') == 1)
        ids = data['container_ids']
        require(isinstance(ids, dict) and set(ids) == EXPECTED)
        require(all(isinstance(v, str) and HEX64.fullmatch(v) for v in ids.values()))
        require(len(set(ids.values())) == 19)
        require(isinstance(data.get('app_image_id'), str)
                and data['app_image_id'].startswith('sha256:')
                and HEX64.fullmatch(data['app_image_id'][7:]))
        require(isinstance(data.get('network_id'), str)
                and HEX64.fullmatch(data['network_id']))
        require(data.get('network_name') == 'ccpc_prod_erpnext_default')
        require(isinstance(data.get('frontend_ipv4'), str)
                and re.fullmatch(r'172\.(?:1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3}',
                                 data['frontend_ipv4']))
        return data
    except (OSError, KeyError, TypeError, ValueError, UnicodeError):
        raise Stop() from None


def inventory(data):
    try:
        names = call('ps', '-a', '--format', '{{.Names}}').splitlines()
        require(len(names) == 19 and set(names) == EXPECTED)
        raw = json.loads(call('container', 'inspect', *sorted(EXPECTED)))
        require(isinstance(raw, list) and len(raw) == 19)
        rows = {}
        for row in raw:
            name = row['Name'].lstrip('/')
            require(name in EXPECTED and name not in rows)
            require(row['Id'] == data['container_ids'][name])
            require(row['HostConfig']['RestartPolicy']['Name'] in ('no', 'unless-stopped'))
            require(row['State']['Running'] is (name != DRILL_FAILED))
            if name == DRILL_FAILED:
                require(row['State']['ExitCode'] == 1)
            if name not in CANDIDATES:
                require(row['HostConfig']['RestartPolicy']['Name'] == 'no')
            rows[name] = row
        require(set(rows) == EXPECTED)
        network_name = data['network_name']
        for name in CANDIDATES:
            row = rows[name]
            networks = row['NetworkSettings']['Networks']
            require(len(networks) == 1 and network_name in networks)
            require(networks[network_name]['NetworkID'] == data['network_id'])
            require(not row['HostConfig'].get('PortBindings'))
            require(not any(bool(v) for v in
                            (row['NetworkSettings'].get('Ports') or {}).values()))
        for role in ('backend', 'frontend', 'websocket'):
            row = rows[f'{PREFIX}-{role}-1']
            require(row['Image'] == data['app_image_id'])
            vols = {m['Destination']: m['Name'] for m in row['Mounts']
                    if m.get('Type') == 'volume'}
            require(vols.get(SITES) == f'{PREFIX}_sites')
            require(vols.get(LOGS) == f'{PREFIX}_logs')
        require(rows[f'{PREFIX}-backend-1']['Image'] == data['app_image_id'])
        db = rows[f'{PREFIX}-db-1']
        require(db['State']['Health']['Status'] == 'healthy')
        require(f'{PREFIX}_db-data' in {m.get('Name') for m in db['Mounts']})
        rq = rows[f'{PREFIX}-redis-queue-1']
        require(f'{PREFIX}_redis-queue-data' in {m.get('Name') for m in rq['Mounts']})
        frontend = rows[f'{PREFIX}-frontend-1']
        require(frontend['NetworkSettings']['Networks'][network_name]['IPAddress']
                == data['frontend_ipv4'])
        networks = json.loads(call('network', 'inspect', network_name))
        require(isinstance(networks, list) and len(networks) == 1)
        net = networks[0]
        require(net['Name'] == network_name and net['Id'] == data['network_id'])
        require(net['Internal'] is True)
        require(set((net.get('Containers') or {}).keys()) ==
                {data['container_ids'][k] for k in CANDIDATES})
        return tuple(rows[name]['HostConfig']['RestartPolicy']['Name']
                     for name in CANDIDATES)
    except (KeyError, TypeError, ValueError, IndexError, UnicodeError):
        raise Stop() from None


def verify_prefix(data, applied):
    require(0 <= applied <= len(CANDIDATES))
    expected = ('unless-stopped',) * applied + ('no',) * (6 - applied)
    require(inventory(data) == expected)


def transition(data, *, apply):
    # One candidate at a time. A failed/ambiguous Docker update leads to a STOP,
    # never blind retry or automatic rollback. Explicit --compensate is separate.
    before = inventory(data)
    if apply:
        require(before == ('no',) * 6)
        sequence = list(enumerate(CANDIDATES))
    else:
        prefixes = [i for i in range(7)
                    if before == ('unless-stopped',) * i + ('no',) * (6 - i)]
        require(len(prefixes) == 1 and prefixes[0] > 0)
        sequence = [(i, CANDIDATES[i]) for i in range(prefixes[0] - 1, -1, -1)]
    for i, name in sequence:
        current = i if apply else i + 1
        verify_prefix(data, current)
        desired = 'unless-stopped' if apply else 'no'
        call('update', f'--restart={desired}', data['container_ids'][name])
        verify_prefix(data, current + 1 if apply else current - 1)
        print(f'CCPC_NEW_A3_G1_POLICY_VERIFIED_CANDIDATE_COUNT='
              f'{current + 1 if apply else current - 1}')
    verify_prefix(data, 6 if apply else 0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check', action='store_true')
    modes.add_argument('--apply', action='store_true')
    modes.add_argument('--compensate', action='store_true')
    args = parser.parse_args(argv)
    touched = False
    try:
        # Reject --apply/--compensate before touching host state or even
        # invoking Docker. --check remains a metadata-only inspection.
        require(args.check or G1_POLICY_MUTATION_REVIEWED)
        operator()
        data = manifest()
        if args.check:
            policies = inventory(data)
            require(policies == ('no',) * 6 or policies == ('unless-stopped',) * 6)
            print('CCPC_NEW_A3_G1_POLICY_READONLY_CHECK_PASS')
        else:
            touched = True
            transition(data, apply=args.apply)
            print('CCPC_NEW_A3_G1_POLICY_APPLY_COMPLETE' if args.apply
                  else 'CCPC_NEW_A3_G1_POLICY_COMPENSATION_COMPLETE')
        return 0
    except Exception:
        print('CCPC_NEW_A3_G1_POLICY_POSSIBLE_PARTIAL_STOP_REVIEW_REQUIRED' if touched
              else 'CCPC_NEW_A3_G1_POLICY_STOP_REVIEW_REQUIRED')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
