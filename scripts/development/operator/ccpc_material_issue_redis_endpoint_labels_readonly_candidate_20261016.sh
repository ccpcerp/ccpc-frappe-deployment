#!/usr/bin/env bash
# CCPC ERPNext: DISTINCT review-only Redis ENDPOINT LABEL comparison candidate.
# NO staging or execution on Ubuntu without separate per-operation approval.
# No Redis/SQL/Frappe access, DNS, service modification, or PRODUCTION inspection.
set -euo pipefail
umask 077

if [[ "${CCPC_REDIS_LABELS_V1_APPROVED:-}" != 'ccpc-redis-labels-v1-one-shot' ]]; then
  printf '%s\n' 'NOT AUTHORIZED: new Redis label diagnostic requires separate approval.' >&2
  exit 1
fi
if [[ "$(id -u)" -eq 0 ]]; then
  printf '%s\n' 'STOP: normal nonroot Ubuntu operator required.' >&2
  exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
  printf '%s\n' 'STOP: Docker CLI unavailable.' >&2
  exit 1
fi
DEV_CONTAINER='frappe_docker_devcontainer-frappe-1'
if ! DEV_ID="$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}|{{index .Config.Labels "com.docker.compose.service"}}|{{.State.Running}}' "$DEV_CONTAINER" 2>/dev/null)"; then
  printf '%s\n' 'STOP: DEVELOPMENT container identity not available.' >&2
  exit 1
fi
if [[ "$DEV_ID" != 'frappe_docker_devcontainer|frappe|true' ]]; then
  printf '%s\n' 'STOP: unexpected DEVELOPMENT container identity.' >&2
  exit 1
fi

# Python stderr is suppressed; Python prints only fixed diagnostic strings.
# This is configuration-label comparison ONLY, not a Redis connection/isolation test.
if docker exec -i --user frappe "$DEV_CONTAINER" \
    bash -c 'cd /workspace/development/frappe-bench && PYTHONDONTWRITEBYTECODE=1 ./env/bin/python -I -B -S -' 2>/dev/null <<'PYTHON'
"""Redacted read-only Redis configured-label comparator. Never contact Redis."""
import ipaddress
import json
import os
import stat
import sys
from pathlib import Path
from urllib.parse import urlsplit

SITES = Path('/workspace/development/frappe-bench/sites')
ISOLATED = 'ccpc-integration2.localhost'
SHARED = 'development.localhost'
MAX_BYTES = 65536
ENV_KEYS = ('FRAPPE_REDIS_CACHE', 'FRAPPE_REDIS_QUEUE')
DEFAULTS = {'redis_cache': 'redis://127.0.0.1:13311',
            'redis_queue': 'redis://127.0.0.1:11311'}


class Stop(Exception):
    """Expected conservative STOP; no exception text is ever printed."""


def checked_directory(path):
    if path.is_symlink() or not path.is_dir():
        raise Stop()


def read_config(path):
    # No directory listings. No app, database, backups or PRODUCTION paths.
    for parent in (Path('/workspace'), Path('/workspace/development'),
                   Path('/workspace/development/frappe-bench'), SITES,
                   path.parent):
        checked_directory(parent)
    if path.is_symlink():
        raise Stop()
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    fd = os.open(path, flags)
    try:
        meta = os.fstat(fd)
        if not stat.S_ISREG(meta.st_mode) or meta.st_size > MAX_BYTES:
            raise Stop()
        with os.fdopen(fd, 'rb') as handle:
            fd = -1
            data = handle.read(MAX_BYTES + 1)
    finally:
        if fd >= 0:
            os.close(fd)
    if len(data) > MAX_BYTES:
        raise Stop()
    conf = json.loads(data.decode('utf-8'))
    if type(conf) is not dict:
        raise Stop()
    return conf


def opaque_endpoint(value):
    """Return local-only host/port identity; never print/log it."""
    if type(value) is not str or not 1 <= len(value) <= 2048:
        raise Stop()
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        raise Stop() from None
    if (parsed.scheme not in ('redis', 'rediss') or not host or port is None
            or not 1 <= port <= 65535 or any(c.isspace() for c in host)):
        raise Stop()
    # TLS, Redis database numbers and credentials do not partition Redis servers.
    host = host.lower().rstrip('.')
    if host in ('localhost', 'localhost.localdomain'):
        return ('loopback', port)
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        # Nonliteral DNS labels may alias another configured label. Fail closed
        # on apparently distinct DNS spellings rather than asserting isolation.
        if (not 1 <= len(host) <= 253 or host.startswith('.')
                or any(not part or len(part) > 63 or part[0] == '-'
                       or part[-1] == '-' or not all(c.isascii() and
                       (c.isalnum() or c == '-') for c in part)
                       for part in host.split('.'))):
            raise Stop()
        return ('dns:' + host, port)
    if ip.is_unspecified or ip.is_multicast:
        raise Stop()
    mapped = getattr(ip, 'ipv4_mapped', None)
    if ip.is_loopback or (mapped is not None and mapped.is_loopback):
        return ('loopback', port)
    if mapped is not None:
        ip = mapped
    return ('ip:' + ip.compressed, port)


def python_effective(common, site, env):
    """Pinned Frappe config.py: common, site, Redis environment LAST."""
    if any(type(x) is not dict for x in (common, site, env)):
        raise Stop()
    merged = dict(common)
    merged.update(site)
    if 'extra_config' in merged:
        raise Stop()  # Dynamic Frappe hooks are out of scope.
    out = {}
    for key, var in (('redis_cache', ENV_KEYS[0]), ('redis_queue', ENV_KEYS[1])):
        if merged.get(key + '_sentinel_enabled'):
            raise Stop()
        value = env.get(var) or merged.get(key) or DEFAULTS[key]
        out[key] = opaque_endpoint(value)
    return out


def node_queue_effective(common, env):
    """Bench-level Node: common Redis queue then process-env override.

    The unexamined Node config.json and live Node process env are NOT proved.
    Require an explicit value in the common/env subset or STOP.
    """
    if type(common) is not dict or type(env) is not dict:
        raise Stop()
    if 'extra_config' in common or common.get('redis_queue_sentinel_enabled'):
        raise Stop()
    value = env.get(ENV_KEYS[1]) or common.get('redis_queue')
    if not value:
        raise Stop()
    return opaque_endpoint(value)


def compare_labels(isolated, shared, node_queue):
    if any(set(x) != {'redis_cache', 'redis_queue'} for x in (isolated, shared)):
        raise Stop()
    isolated_values = tuple(isolated.values())
    shared_values = tuple(shared.values())
    if (isolated['redis_cache'] == isolated['redis_queue']
            or bool(set(isolated_values) & set(shared_values))
            or node_queue in (isolated['redis_cache'], shared['redis_cache'])):
        return 'OVERLAP_STOP'
    # The bench-level Node subscriber can consume from a site-specific queue;
    # that is NOT evidence of isolated WebSocket service or subscriber identity.
    all_values = isolated_values + shared_values + (node_queue,)
    if any(value[0].startswith('dns:') for value in all_values):
        return 'AMBIGUOUS_STOP'  # No DNS resolution or alias guesses.
    return 'NO_EXACT_LABEL_OVERLAP'


def main():
    try:
        common = read_config(SITES / 'common_site_config.json')
        isolated = read_config(SITES / ISOLATED / 'site_config.json')
        shared = read_config(SITES / SHARED / 'site_config.json')
        env = {name: os.environ.get(name) for name in ENV_KEYS}
        status = compare_labels(python_effective(common, isolated, env),
                                python_effective(common, shared, env),
                                node_queue_effective(common, env))
    except Exception:
        print('CONFIGURED ENDPOINT LABELS: AMBIGUOUS_STOP; POSTING: NO-GO')
        return 1
    if status == 'OVERLAP_STOP':
        print('CONFIGURED ENDPOINT LABELS: OVERLAP_STOP; POSTING: NO-GO')
        return 1
    if status == 'AMBIGUOUS_STOP':
        print('CONFIGURED ENDPOINT LABELS: AMBIGUOUS_STOP; POSTING: NO-GO')
        return 1
    print('CONFIGURED ENDPOINT LABELS: NO_EXACT_LABEL_OVERLAP; ISOLATION: UNVERIFIED')
    print('NODE/WORKER/PUBSUB/PHYSICAL: UNVERIFIED; POSTING: NO-GO')
    return 0


if __name__ == '__main__':
    try:
        result = main()
    except Exception:
        print('CONFIGURED ENDPOINT LABELS: AMBIGUOUS_STOP; POSTING: NO-GO')
        result = 1
    sys.exit(result)
PYTHON
then
  printf '%s\n' 'REDIS LABEL REVIEW V1: COMPLETED; POSTING: NO-GO'
else
  printf '%s\n' 'REDIS LABEL REVIEW V1: STOPPED; POSTING: NO-GO'
  exit 1
fi
