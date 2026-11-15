#!/usr/bin/env python3
"""NEW A3 G1 metadata-only backend process inventory; NOT a restart-safety pass.

No docker exec, Redis commands, database access, process signal, service start,
container update, or file write. Docker inspect and top are read-only daemon
queries. Raw argv/entrypoints are held in memory and NEVER printed or logged.
Run on NEW only after a separate reviewed owner/operator approval and source pin.
"""

import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess

MANIFEST = Path('/var/lib/ccpc-new-a3-r0-manifest-20261113/manifest.json')
PREFIX = 'ccpc_prod_erpnext'
CANDIDATE_ROLES = ('db', 'redis-cache', 'redis-queue', 'backend', 'websocket', 'frontend')
CANDIDATES = tuple(f'{PREFIX}-{role}-1' for role in CANDIDATE_ROLES)
ORIGINALS = tuple(f'{prefix}-{role}-1'
                  for prefix in ('ccpc_full_acceptance_20261107',
                                 'ccpc_restore_rehearsal_20261107')
                  for role in ('redis-queue', 'redis-cache', 'db'))
TEST_PREFIX = 'ccpc_a3_restore_drill_20261112'
TEST_RUNNING = tuple(f'{TEST_PREFIX}-{role}-1'
                     for role in ('frontend-completion1', 'websocket-completion1',
                                  'backend-recovery1', 'redis-queue', 'redis-cache', 'db'))
TEST_FAILED = f'{TEST_PREFIX}-backend-1'
EXPECTED = set(CANDIDATES + ORIGINALS + TEST_RUNNING + (TEST_FAILED,))
HEX64 = re.compile(r'[a-f0-9]{64}\Z')
DOCKER = ('docker', '--host', 'unix:///var/run/docker.sock')
# Signature matching is a diagnostic, NOT a proof that no arbitrary Python
# module or external consumer can execute business jobs.
WORKER = re.compile(r'\b(?:bench\s+(?:--site\s+[^\s]+\s+)?worker|rq\s+worker|'
                    r'rqworker|celery\s+(?:-A\s+[^\s]+\s+)?worker)\b', re.I)
SCHEDULER = re.compile(r'\b(?:bench\s+(?:--site\s+[^\s]+\s+)?schedule|'
                       r'frappe\.utils\.scheduler|scheduler\.py)\b', re.I)


class Stop(Exception):
    """Deliberately hides underlying private values."""


def require(condition):
    if not condition:
        raise Stop()


def read(*args):
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                check=True, timeout=20)
        require(len(result.stdout) <= 256 * 1024)
        return result.stdout.decode('utf-8', 'strict')
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise Stop() from None


def docker(*args):
    return read(*(DOCKER + tuple(args)))


def parse_json(value):
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        raise Stop() from None


def check_operator():
    require(os.geteuid() == 0)
    require(os.environ.get('SUDO_USER') == 'ccpcadmin')
    require(socket.gethostname().split('.')[0] == 'ccpcerp-prod')
    require(not any(k in os.environ for k in
                    ('DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH')))


def manifest():
    try:
        parent = MANIFEST.parent.lstat()
        doc = MANIFEST.lstat()
        require(stat.S_ISDIR(parent.st_mode) and parent.st_uid == 0
                and stat.S_IMODE(parent.st_mode) == 0o700)
        require(stat.S_ISREG(doc.st_mode) and doc.st_uid == 0
                and stat.S_IMODE(doc.st_mode) == 0o600)
        require(doc.st_size <= 64 * 1024)
        info = parse_json(MANIFEST.read_text(encoding='utf-8'))
        require(isinstance(info, dict) and info.get('schema') == 1)
        ids = info['container_ids']
        require(isinstance(ids, dict) and set(ids) == EXPECTED)
        require(all(isinstance(x, str) and HEX64.fullmatch(x) for x in ids.values()))
        require(len(set(ids.values())) == 19)
        require(isinstance(info.get('app_image_id'), str)
                and info['app_image_id'].startswith('sha256:')
                and HEX64.fullmatch(info['app_image_id'][7:]))
        return info
    except (OSError, UnicodeError, KeyError, ValueError, TypeError):
        raise Stop() from None


def snapshot(info):
    names = docker('ps', '-a', '--format', '{{.Names}}').splitlines()
    require(len(names) == 19 and set(names) == EXPECTED)
    rows = parse_json(docker('container', 'inspect', *sorted(EXPECTED)))
    require(isinstance(rows, list) and len(rows) == 19)
    by_name = {}
    for row in rows:
        require(isinstance(row, dict))
        name = row['Name'].lstrip('/')
        require(name in EXPECTED and name not in by_name)
        by_name[name] = row
    require(set(by_name) == EXPECTED)
    ids = info['container_ids']
    for name, row in by_name.items():
        require(row['Id'] == ids[name])
        require(row['HostConfig']['RestartPolicy']['Name'] == 'no')
        require(row['State']['Running'] is (name != TEST_FAILED))
    require(by_name[TEST_FAILED]['State']['ExitCode'] == 1)
    backend = by_name[f'{PREFIX}-backend-1']
    require(backend['Image'] == info['app_image_id'])
    require(info.get('network_name') in backend['NetworkSettings']['Networks'])
    require(len(backend['NetworkSettings']['Networks']) == 1)
    return by_name


def process_table(raw):
    """Parse Docker-top ps output without emitting argv, PIDs or raw lines."""
    lines = raw.splitlines()
    require(1 <= len(lines) <= 256)
    heading = lines[0].split(None, 3)
    require(len(heading) == 4)
    require([h.upper() for h in heading[:3]] == ['PID', 'PPID', 'COMMAND'])
    require(heading[3].upper() in ('COMMAND', 'ARGS'))
    rows = []
    for line in lines[1:]:
        parts = line.split(None, 3)
        require(len(parts) == 4)
        require(parts[0].isdigit() and parts[1].isdigit())
        require(parts[2] and len(parts[2]) <= 128 and len(parts[3]) <= 16384)
        rows.append((parts[2], parts[3]))
    require(len(rows) > 0)
    return rows


def start_vector(row):
    # Config and runtime launch data are *only* classified in memory; shell
    # wrappers, interpreter -c, and unknown entrypoints are not cleared.
    config = row['Config']
    fields = [config.get('Entrypoint'), config.get('Cmd'), row.get('Path'), row.get('Args')]
    values = []
    for field in fields:
        if field is None:
            continue
        if isinstance(field, str):
            values.append(field)
        elif isinstance(field, list) and all(isinstance(x, str) for x in field):
            values.extend(field)
        else:
            raise Stop()
    require(values and sum(map(len, values)) <= 32768)
    return ' '.join(values)


def classify(row, processes):
    start = start_vector(row)
    command_worker = bool(WORKER.search(start))
    command_scheduler = bool(SCHEDULER.search(start))
    worker_count = sum(bool(WORKER.search(f'{comm} {args}')) for comm, args in processes)
    scheduler_count = sum(bool(SCHEDULER.search(f'{comm} {args}')) for comm, args in processes)
    return command_worker, command_scheduler, worker_count, scheduler_count


def audit():
    check_operator()
    info = manifest()
    first = snapshot(info)  # All 19 IDs/policies verified BEFORE any docker top.
    total_worker = total_scheduler = 0
    command_worker = command_scheduler = False
    counts = {}
    for name in CANDIDATES:
        # Use immutable full container ID, never a name which could race.
        container_id = info['container_ids'][name]
        rows = process_table(docker('top', container_id, '-eo', 'pid,ppid,comm,args'))
        counts[name] = len(rows)
        wc, sc, wp, sp = classify(first[name], rows)
        command_worker |= wc
        command_scheduler |= sc
        total_worker += wp
        total_scheduler += sp
    # Recheck identities and policies after all queries to reject simple drift.
    snapshot(info)
    print('CCPC_NEW_A3_G1_BACKEND_PROCESS_IDENTITIES_19_PASS')
    print('CCPC_NEW_A3_G1_CANDIDATE_PROCESS_TABLES_6_PASS')
    print('CCPC_NEW_A3_G1_BACKEND_PROCESS_COUNT=' + str(counts[f'{PREFIX}-backend-1']))
    print('CCPC_NEW_A3_G1_CANDIDATE_WORKER_SIGNATURE_COUNT=' + str(total_worker))
    print('CCPC_NEW_A3_G1_CANDIDATE_SCHEDULER_SIGNATURE_COUNT=' + str(total_scheduler))
    print('CCPC_NEW_A3_G1_START_COMMAND_WORKER_SIGNATURE=' + ('YES' if command_worker else 'NO'))
    print('CCPC_NEW_A3_G1_START_COMMAND_SCHEDULER_SIGNATURE=' + ('YES' if command_scheduler else 'NO'))
    # Deliberately no SAFE/NO-WRITES verdict: ps signatures miss arbitrary jobs.
    print('CCPC_NEW_A3_G1_QUEUE_CONTENTS_NOT_INSPECTED=YES')
    print('CCPC_NEW_A3_G1_EXTERNAL_CONSUMERS_NOT_INSPECTED=YES')
    print('CCPC_NEW_A3_G1_PROCESS_READONLY_INVENTORY_COMPLETE')


if __name__ == '__main__':
    try:
        audit()
    except Exception:
        print('CCPC_NEW_A3_G1_PROCESS_STOP_REVIEW_REQUIRED')
        raise SystemExit(1) from None
