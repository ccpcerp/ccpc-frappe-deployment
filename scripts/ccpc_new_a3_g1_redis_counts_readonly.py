#!/usr/bin/env python3
"""NEW A3 G1 Redis DB0 fixed-key metadata audit; NOT queue or restart safety proof.

Uses pinned container identity and a bounded direct TCP connection to its Docker
bridge IPv4. Redis commands are TYPE, LLEN, ZCARD, SCARD, DBSIZE, INFO clients
only. Never fetches job IDs, payloads, arbitrary key names or secret configuration.
The approved operator must separately authorize any one-time NEW-host execution.
"""

import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess

MANIFEST = Path('/var/lib/ccpc-new-a3-r0-manifest-20261113/manifest.json')
PREFIX = 'ccpc_prod_erpnext'
CANDIDATES = tuple(f'{PREFIX}-{role}-1' for role in
                   ('db', 'redis-cache', 'redis-queue', 'backend', 'websocket', 'frontend'))
ORIGINALS = tuple(f'{p}-{role}-1'
                  for p in ('ccpc_full_acceptance_20261107', 'ccpc_restore_rehearsal_20261107')
                  for role in ('redis-queue', 'redis-cache', 'db'))
DRILL = 'ccpc_a3_restore_drill_20261112'
DRILL_RUNNING = tuple(f'{DRILL}-{role}-1' for role in
                      ('frontend-completion1', 'websocket-completion1',
                       'backend-recovery1', 'redis-queue', 'redis-cache', 'db'))
DRILL_FAILED = f'{DRILL}-backend-1'
EXPECTED = set(CANDIDATES + ORIGINALS + DRILL_RUNNING + (DRILL_FAILED,))
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
DOCKER = ('docker', '--host', 'unix:///var/run/docker.sock')
QUEUES = ('default', 'short', 'long')
# Names are fixed RQ conventions; other queues/registry versions may exist.
REGISTRIES = (('failed', 'failed'), ('deferred', 'deferred'),
              ('scheduled', 'scheduled'), ('started_wip', 'wip'),
              ('started_alt', 'started'))


class Stop(Exception):
    """Redacts internal errors and Redis responses."""


def need(ok):
    if not ok:
        raise Stop()


def docker(*parts):
    try:
        r = subprocess.run(DOCKER + parts, check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, timeout=20)
        need(len(r.stdout) <= 256 * 1024)
        return r.stdout.decode('utf-8', 'strict')
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise Stop() from None


def operator():
    need(os.geteuid() == 0)
    need(os.environ.get('SUDO_USER') == 'ccpcadmin')
    need(socket.gethostname().split('.')[0] == 'ccpcerp-prod')
    need(not any(k in os.environ for k in
                 ('DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH')))


def pinned_manifest():
    try:
        parent, file = MANIFEST.parent.lstat(), MANIFEST.lstat()
        need(stat.S_ISDIR(parent.st_mode) and parent.st_uid == 0
             and stat.S_IMODE(parent.st_mode) == 0o700)
        need(stat.S_ISREG(file.st_mode) and file.st_uid == 0
             and stat.S_IMODE(file.st_mode) == 0o600 and file.st_size <= 65536)
        data = json.loads(MANIFEST.read_text(encoding='utf-8'))
        need(isinstance(data, dict) and data.get('schema') == 1)
        ids = data['container_ids']
        need(isinstance(ids, dict) and set(ids) == EXPECTED)
        need(all(isinstance(i, str) and HEX64.fullmatch(i) for i in ids.values()))
        need(len(set(ids.values())) == 19)
        need(isinstance(data.get('network_name'), str)
             and data['network_name'] == 'ccpc_prod_erpnext_default')
        need(isinstance(data.get('app_image_id'), str)
             and data['app_image_id'].startswith('sha256:')
             and HEX64.fullmatch(data['app_image_id'][7:]))
        return data
    except (OSError, KeyError, TypeError, ValueError, UnicodeError):
        raise Stop() from None


def snapshot(data):
    names = docker('ps', '-a', '--format', '{{.Names}}').splitlines()
    need(len(names) == 19 and set(names) == EXPECTED)
    try:
        records = json.loads(docker('container', 'inspect', *sorted(EXPECTED)))
        need(isinstance(records, list) and len(records) == 19)
        rows = {}
        for row in records:
            name = row['Name'].lstrip('/')
            need(name in EXPECTED and name not in rows)
            rows[name] = row
        need(set(rows) == EXPECTED)
        for name, row in rows.items():
            need(row['Id'] == data['container_ids'][name])
            need(row['HostConfig']['RestartPolicy']['Name'] == 'no')
            need(row['State']['Running'] is (name != DRILL_FAILED))
        need(rows[DRILL_FAILED]['State']['ExitCode'] == 1)
        need(rows[f'{PREFIX}-backend-1']['Image'] == data['app_image_id'])
        network_name = data['network_name']
        backend_nets = rows[f'{PREFIX}-backend-1']['NetworkSettings']['Networks']
        need(len(backend_nets) == 1 and network_name in backend_nets)
        redis_nets = rows[f'{PREFIX}-redis-queue-1']['NetworkSettings']['Networks']
        need(len(redis_nets) == 1 and network_name in redis_nets)
        ip = redis_nets[network_name]['IPAddress']
        address = ipaddress.ip_address(ip)
        need(address.version == 4 and address.is_private and not address.is_loopback
             and not address.is_link_local and not address.is_multicast)
        need(redis_nets[network_name]['NetworkID'] == backend_nets[network_name]['NetworkID'])
        return ip
    except (KeyError, TypeError, ValueError, AttributeError):
        raise Stop() from None


def _line(conn):
    buf = bytearray()
    while len(buf) <= 127:
        c = conn.recv(1)
        need(len(c) == 1)
        if c == b'\n':
            need(buf.endswith(b'\r'))
            return bytes(buf[:-1])
        buf.extend(c)
    raise Stop()


def _exact(conn, length):
    need(0 <= length <= 32768)
    result = bytearray()
    while len(result) < length:
        chunk = conn.recv(length - len(result))
        need(bool(chunk))
        result.extend(chunk)
    return bytes(result)


def _uint(value):
    need(bool(re.fullmatch(rb'(?:0|[1-9][0-9]{0,18})', value)))
    n = int(value)
    need(n <= 2**63 - 1)
    return n


def redis(conn, *parts):
    # Only compile-time specified, ASCII, metadata-only command and operands.
    need(parts[0] in ('TYPE', 'LLEN', 'ZCARD', 'SCARD', 'DBSIZE', 'INFO'))
    encoded = [p.encode('ascii') for p in parts]
    payload = b'*' + str(len(parts)).encode() + b'\r\n'
    for p in encoded:
        need(len(p) <= 100)
        payload += b'$' + str(len(p)).encode() + b'\r\n' + p + b'\r\n'
    conn.sendall(payload)
    result = _line(conn)
    need(bool(result))
    if result[:1] == b':':
        return _uint(result[1:])
    if result[:1] == b'+':
        need(len(result) <= 100)
        return result[1:].decode('ascii', 'strict')
    if result[:1] == b'$':
        n = _uint(result[1:])
        need(n <= 32768)
        content = _exact(conn, n)
        need(_exact(conn, 2) == b'\r\n')
        return content
    raise Stop()


def sized(conn, key, expected_type, count_command):
    kind = redis(conn, 'TYPE', key)
    need(isinstance(kind, str))
    if kind == 'none':
        return 'ABSENT'  # Missing is NOT claimed to be zero or empty.
    need(kind == expected_type)
    size = redis(conn, count_command, key)
    need(type(size) is int)
    return str(size)


def metadata(conn):
    dbsize = redis(conn, 'DBSIZE')  # Default Redis DB 0 only; never SELECT.
    need(type(dbsize) is int)
    info = redis(conn, 'INFO', 'clients')
    need(isinstance(info, bytes))
    found = re.findall(rb'(?:^|\r\n)connected_clients:([0-9]+)(?:\r\n|$)', info)
    need(len(found) == 1)
    clients = _uint(found[0])
    results = [('DB0_TOTAL_KEYS', str(dbsize)), ('CONNECTED_CLIENTS_INCLUDING_AUDIT', str(clients)),
               ('RQ_REGISTERED_QUEUE_NAMES_COUNT', sized(conn, 'rq:queues', 'set', 'SCARD'))]
    for queue in QUEUES:
        results.append((f'QUEUE_{queue.upper()}_PENDING_LIST',
                        sized(conn, f'rq:queue:{queue}', 'list', 'LLEN')))
        for label, prefix in REGISTRIES:
            results.append((f'QUEUE_{queue.upper()}_{label.upper()}_REGISTRY',
                            sized(conn, f'rq:{prefix}:{queue}', 'zset', 'ZCARD')))
    return results


def audit():
    operator()
    data = pinned_manifest()
    ip = snapshot(data)
    try:
        # Only direct TCP to verified pinned redis-queue container bridge IPv4.
        # No docker exec, no auth/key reads; if auth is required, fail closed.
        with socket.create_connection((ip, 6379), timeout=5) as conn:
            conn.settimeout(5)
            results = metadata(conn)
    except (OSError, UnicodeError, ValueError, TypeError):
        raise Stop() from None
    need(snapshot(data) == ip)  # Preserve identity and policy checks after query.
    print('CCPC_NEW_A3_G1_REDIS_IDENTITIES_19_PASS')
    print('CCPC_NEW_A3_G1_REDIS_PINNED_DB0_METADATA_PASS')
    for label, value in results:
        print(f'CCPC_NEW_A3_G1_REDIS_{label}={value}')
    print('CCPC_NEW_A3_G1_REDIS_UNKNOWN_QUEUES_NOT_INSPECTED=YES')
    print('CCPC_NEW_A3_G1_REDIS_OTHER_DATABASES_NOT_INSPECTED=YES')
    print('CCPC_NEW_A3_G1_REDIS_EXTERNAL_CONSUMERS_NOT_IDENTIFIED=YES')
    print('CCPC_NEW_A3_G1_REDIS_SNAPSHOT_ATOMIC=NO')
    print('CCPC_NEW_A3_G1_REDIS_READONLY_COUNTS_COMPLETE')


if __name__ == '__main__':
    try:
        audit()
    except Exception:
        print('CCPC_NEW_A3_G1_REDIS_STOP_REVIEW_REQUIRED')
        raise SystemExit(1) from None
