#!/usr/bin/env bash
# CCPC ERPNext: separate GitHub-review-only JSON/Redis FORMAT diagnostic.
# NOT the consumed Redis boundary preflight. DO NOT stage/run without new approval.
# Only DEVELOPMENT; no Frappe init, Redis/SQL/network connection or writes.
set -euo pipefail
umask 077

if [[ "${CCPC_REDIS_SHAPE_READONLY_APPROVED:-}" != 'ccpc-redis-json-shape-one-shot' ]]; then
  printf '%s\n' 'NOT AUTHORIZED: separate Redis JSON shape check needs explicit one-shot approval.' >&2
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
  printf '%s\n' 'STOP: DEVELOPMENT identity inspection failed.' >&2
  exit 1
fi
if [[ "$DEV_ID" != 'frappe_docker_devcontainer|frappe|true' ]]; then
  printf '%s\n' 'STOP: Unexpected DEVELOPMENT Compose identity.' >&2
  exit 1
fi

# Expected safe output is fixed labels only. Suppress docker/container stderr,
# which could otherwise disclose host/configuration/exception details.
if docker exec -i --user frappe "$DEV_CONTAINER" \
    bash -c 'cd /workspace/development/frappe-bench && PYTHONDONTWRITEBYTECODE=1 ./env/bin/python -I -B -S -' 2>/dev/null <<'PYTHON'
"""Read-only, redacted FORMAT check. Does not compare or connect endpoints."""
import ipaddress
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


def checked_directory(path):
    """Reject any unexpected/symlinked directory component."""
    if path.is_symlink() or not path.is_dir():
        raise Stop()


def read_config(path):
    # Only fixed, allowlisted paths are passed. No configuration values logged.
    for parent in (Path('/workspace'), Path('/workspace/development'),
                   Path('/workspace/development/frappe-bench'), SITES, path.parent):
        checked_directory(parent)
    if path.is_symlink():
        raise Stop()
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
            raise Stop()
        with os.fdopen(fd, 'rb') as handle:
            fd = -1
            raw = handle.read(MAX_BYTES + 1)
    finally:
        if fd >= 0:
            os.close(fd)
    if len(raw) > MAX_BYTES:
        raise Stop()
    obj = json.loads(raw.decode('utf-8'))
    if type(obj) is not dict:
        raise Stop()
    return obj


def redis_url_format(value):
    """Same URL shape guards as the original candidate; never return the URL."""
    if type(value) is not str or not 1 <= len(value) <= 2048:
        raise Stop()
    try:
        parsed = urlsplit(value)
        port = parsed.port
        host = parsed.hostname
    except ValueError:
        raise Stop() from None
    if (parsed.scheme not in ('redis', 'rediss') or not host or port is None
            or not 1 <= port <= 65535 or any(c.isspace() for c in host)):
        raise Stop()
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if ip.is_unspecified or ip.is_multicast:
            raise Stop()
    return True


def effective_format(common, site, env):
    """Follow pinned Frappe config.py: common -> site -> environment LAST."""
    if any(type(d) is not dict for d in (common, site, env)):
        raise Stop()
    conf = dict(common)
    conf.update(site)
    for key, env_key, default in (
        ('redis_queue', 'FRAPPE_REDIS_QUEUE', 'redis://127.0.0.1:11311'),
        ('redis_cache', 'FRAPPE_REDIS_CACHE', 'redis://127.0.0.1:13311'),
    ):
        conf[key] = env.get(env_key) or conf.get(key) or default
    for key in ('redis_queue', 'redis_cache'):
        if conf.get(key + '_sentinel_enabled'):
            raise Stop()
        redis_url_format(conf.get(key))
    return True


def main():
    configs = {}
    for label, path in (
        ('COMMON', SITES / 'common_site_config.json'),
        ('ISOLATED', SITES / TEST / 'site_config.json'),
        ('SHARED', SITES / SHARED / 'site_config.json'),
    ):
        try:
            configs[label] = read_config(path)
        except Exception:
            print(label + ': JSON_STOP')
            print('CONFIG SHAPE: STOP; POSTING: NO-GO')
            return 1
        print(label + ': JSON_OK')
    environment = {key: os.environ.get(key) for key in (
        'FRAPPE_REDIS_QUEUE', 'FRAPPE_REDIS_CACHE')}
    for label in ('ISOLATED', 'SHARED'):
        try:
            effective_format(configs['COMMON'], configs[label], environment)
        except Exception:
            print(label + '_REDIS: FORMAT_STOP')
            print('CONFIG SHAPE: STOP; POSTING: NO-GO')
            return 1
        print(label + '_REDIS: FORMAT_OK')
    print('CONFIG SHAPE: COMPLETE; ENDPOINTS/ISOLATION: UNVERIFIED; POSTING: NO-GO')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BaseException:
        print('CONFIG SHAPE: STOP; POSTING: NO-GO')
        sys.exit(1)
PYTHON
then
  printf '%s\n' 'ONE-SHOT REDACTED FORMAT CHECK: COMPLETED; POSTING: NO-GO'
else
  printf '%s\n' 'ONE-SHOT REDACTED FORMAT CHECK: STOPPED; POSTING: NO-GO'
  exit 1
fi
