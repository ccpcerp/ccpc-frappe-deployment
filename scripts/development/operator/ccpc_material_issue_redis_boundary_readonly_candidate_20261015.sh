#!/usr/bin/env bash
# CCPC ERPNext: NEW review-only DEV Redis CONFIGURATION boundary candidate.
# DO NOT stage or execute without fresh explicit one-operation owner approval.
# READ ONLY: no Redis connections, Frappe init, SQL, writes or production access.
set -euo pipefail
umask 077

if [[ "${CCPC_REDIS_PREFLIGHT_READONLY_APPROVED:-}" != 'ccpc-redis-config-review-one-shot' ]]; then
  printf '%s\n' 'NOT AUTHORIZED: New Redis boundary preflight requires separate approval.' >&2
  exit 1
fi
if [[ "$(id -u)" -eq 0 ]]; then
  printf '%s\n' 'STOP: normal Ubuntu operator required.' >&2
  exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
  printf '%s\n' 'STOP: Docker CLI unavailable.' >&2
  exit 1
fi
DEV_CONTAINER='frappe_docker_devcontainer-frappe-1'
DEV_LABELS="$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}|{{index .Config.Labels "com.docker.compose.service"}}|{{.State.Running}}' "$DEV_CONTAINER" 2>/dev/null)" || {
  printf '%s\n' 'STOP: Documented DEVELOPMENT container unavailable.' >&2
  exit 1
}
if [[ "$DEV_LABELS" != 'frappe_docker_devcontainer|frappe|true' ]]; then
  printf '%s\n' 'STOP: Unexpected DEVELOPMENT Compose identity.' >&2
  exit 1
fi
# The only Docker exec target is the confirmed DEVELOPMENT frappe container.
# No host path or credential is forwarded; stdin carries only source code.
docker exec -i --user frappe "$DEV_CONTAINER" \
  bash -c 'cd /workspace/development/frappe-bench && PYTHONDONTWRITEBYTECODE=1 ./env/bin/python -' <<'PYTHON'
"""Read-only configuration classifier, NOT a Redis connection/isolation test."""
import json
import os
import stat
import sys
from pathlib import Path
from urllib.parse import urlsplit

SITES = Path('/workspace/development/frappe-bench/sites')
TEST = 'ccpc-integration2.localhost'
SHARED = 'development.localhost'
MAX_BYTES = 65536


class Stop(Exception):
    pass


def read_config(path):
    """Read a bounded regular JSON file, refusing symlinks and odd parents."""
    if path.parent.is_symlink() or path.is_symlink():
        raise Stop('Configuration path is a symlink')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    try:
        meta = os.fstat(fd)
        if not stat.S_ISREG(meta.st_mode) or meta.st_size > MAX_BYTES:
            raise Stop('Configuration file is not an expected regular file')
        with os.fdopen(fd, 'rb') as handle:
            fd = -1
            raw = handle.read(MAX_BYTES + 1)
    finally:
        if fd >= 0:
            os.close(fd)
    if len(raw) > MAX_BYTES:
        raise Stop('Configuration file exceeds size limit')
    obj = json.loads(raw)
    if type(obj) is not dict:
        raise Stop('Configuration object is not a JSON mapping')
    return obj


def endpoint(value):
    """Returns only opaque (host,port); never outputs raw URLs or credentials.

    Distinct hostnames do NOT prove distinct physical Redis instances. Redis DB
    numbers, credentials and TLS are ignored for physical-overlap conservatism.
    """
    if type(value) is not str or not 1 <= len(value) <= 2048:
        raise Stop('Redis URL unavailable or malformed')
    try:
        parsed = urlsplit(value)
        port = parsed.port
        host = parsed.hostname
    except ValueError:
        raise Stop('Redis URL could not be parsed') from None
    if (parsed.scheme not in ('redis', 'rediss') or not host or port is None
            or not 1 <= port <= 65535 or any(c.isspace() for c in host)):
        raise Stop('Redis configuration requires an explicit host and port')
    return host.rstrip('.').lower(), port


def effective(common, specific, environment):
    """Model frappe.config _get_common_site_config followed by site override.

    This models the exec child process environment, NOT running worker env.
    Does not handle Sentinel, dynamic DNS, proxies or Redis ACLs: fail closed.
    """
    if any(type(x) is not dict for x in (common, specific, environment)):
        raise Stop('Unexpected configuration shape')
    merged = dict(common)
    for label, env_key, default in (
        ('redis_queue', 'FRAPPE_REDIS_QUEUE', 'redis://127.0.0.1:11311'),
        ('redis_cache', 'FRAPPE_REDIS_CACHE', 'redis://127.0.0.1:13311'),
    ):
        merged[label] = environment.get(env_key) or merged.get(label) or default
    merged.update(specific)
    for label in ('redis_queue', 'redis_cache'):
        if merged.get(label + '_sentinel_enabled'):
            raise Stop('Sentinel mode needs independent source and topology review')
    return {'cache': endpoint(merged.get('redis_cache')),
            'queue': endpoint(merged.get('redis_queue'))}


def classify(test_endpoints, shared_endpoints):
    """Opaque endpoint comparisons only, never return endpoint identifiers."""
    if not (type(test_endpoints) is dict and type(shared_endpoints) is dict
            and set(test_endpoints) == set(shared_endpoints) == {'cache', 'queue'}):
        raise Stop('Invalid endpoint comparison shape')
    within_test_overlap = test_endpoints['cache'] == test_endpoints['queue']
    cross_site_overlap = bool(set(test_endpoints.values()) & set(shared_endpoints.values()))
    return {
        'test_cache_queue_overlap': within_test_overlap,
        'test_shared_site_overlap': cross_site_overlap,
        'configuration_only': True,
        'physical_redis_isolation_proven': False,
        'worker_process_endpoints_proven': False,
        'redis_pubsub_isolation_proven': False,
        'rollback_or_posting_authorized': False,
    }


def main():
    try:
        if SITES.is_symlink() or not SITES.is_dir():
            raise Stop('Sites directory is missing or unsafe')
        common = read_config(SITES / 'common_site_config.json')
        isolated = read_config(SITES / TEST / 'site_config.json')
        shared = read_config(SITES / SHARED / 'site_config.json')
        # Only permitted env names are read. No configuration or env values printed.
        env = {name: os.environ.get(name) for name in ('FRAPPE_REDIS_CACHE', 'FRAPPE_REDIS_QUEUE')}
        result = classify(effective(common, isolated, env), effective(common, shared, env))
        if result['test_cache_queue_overlap'] or result['test_shared_site_overlap']:
            print('REDIS CONFIGURATION ENDPOINT OVERLAP: DETECTED; STOP')
            return 1
        print('REDIS CONFIGURATION ENDPOINT LABELS: NO EXACT OVERLAP')
        print('ACTUAL DNS, SERVICE, WORKERS AND PUBSUB ISOLATION: UNVERIFIED')
        print('CONFIGURATION CHECK COMPLETED; WRITE/ROLLBACK/COMMIT: NO-GO')
        return 0
    except Exception:
        # No exception text: may contain credentials, URLs or site config data.
        print('REDIS READ-ONLY CONFIGURATION PREFLIGHT: STOPPED', file=sys.stderr)
        print('DO NOT RETRY OR CHANGE SERVICE CONFIGURATION', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
PYTHON
