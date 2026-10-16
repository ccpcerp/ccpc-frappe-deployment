#!/usr/bin/env bash
# CCPC Stage A v2 -- GITHUB REVIEW ONLY. Do not stage or run on Ubuntu.
# DEV-labelled Docker list metadata only; no individual docker inspect, Redis,
# SQL, site config, service changes, network peer lists or PRODUCTION access.
set -euo pipefail
umask 077

if [[ "${CCPC_DEV_TOPOLOGY_A_V2_APPROVED:-}" != 'ccpc-dev-topology-a-v2-separate-one-shot' ]]; then
  printf '%s\n' 'STAGE_A_V2_AUTHORIZATION_STOP' 'DEV_PROD_SEPARATION_UNVERIFIED' 'POSTING_NO_GO'
  exit 1
fi
# Pinned absolute executable paths; fail closed if the host differs.
if [[ ! -x /usr/bin/id || ! -x /usr/bin/docker || ! -x /usr/bin/python3 ]]; then
  printf '%s\n' 'STAGE_A_V2_PREREQUISITE_STOP' 'DEV_PROD_SEPARATION_UNVERIFIED' 'POSTING_NO_GO'
  exit 1
fi
if [[ "$(/usr/bin/id -un 2>/dev/null || :)" != 'gani' || "$(/usr/bin/id -u 2>/dev/null || :)" == '0' ]]; then
  printf '%s\n' 'STAGE_A_V2_OPERATOR_STOP' 'DEV_PROD_SEPARATION_UNVERIFIED' 'POSTING_NO_GO'
  exit 1
fi

# Python emits only fixed-category status labels; Docker bytes never printed.
/usr/bin/python3 -I -B -S - <<'PYTHON'
"""Stage A v2: bounded, narrow Docker listing. Does NOT prove real DEV identity."""
import json
import os
import re
import selectors
import subprocess
import sys
import time

PROJECT = 'frappe_docker_devcontainer'
NETWORK = 'frappe_docker_devcontainer_default'
ROLES = ('frappe', 'redis-cache', 'redis-queue')
DOCKER = '/usr/bin/docker'
MAX_STDOUT_BYTES = 4096  # Per invocation: project choice, not a Docker default.
MAX_SECONDS = 6
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
# Docker CLI documented container-ls placeholders, limited to these six values.
FMT = ('{{json .ID}}\t{{json .Names}}\t{{json .State}}\t'
       '{{json .Networks}}\t{{json (.Label "com.docker.compose.project")}}\t'
       '{{json (.Label "com.docker.compose.service")}}')
CLEAN_ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'HOME': '/nonexistent',
             'DOCKER_CONFIG': '/nonexistent'}


class Stop(Exception):
    def __init__(self, category):
        self.category = category


def bounded_docker_read(argv, deadline_seconds=MAX_SECONDS):
    """Read at most MAX+1 stdout bytes, killing timed-out/oversized child.

    No communicate(), read-all(), text mode or shell; read readiness uses an
    absolute deadline even when the child produces no output. stderr discarded.
    """
    child = None
    selector = None
    try:
        child = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                 env=CLEAN_ENV, close_fds=True, start_new_session=True)
        selector = selectors.DefaultSelector()
        selector.register(child.stdout, selectors.EVENT_READ)
        stop_at = time.monotonic() + deadline_seconds
        pieces = []
        count = 0
        while True:
            remaining = stop_at - time.monotonic()
            if remaining <= 0:
                raise Stop('DEV_METADATA_UNKNOWN_STOP')
            if not selector.select(remaining):
                raise Stop('DEV_METADATA_UNKNOWN_STOP')
            # Never ask kernel/Python for more than 4097 bytes total.
            piece = os.read(child.stdout.fileno(), min(1024, MAX_STDOUT_BYTES + 1 - count))
            if not piece:
                break
            count += len(piece)
            if count > MAX_STDOUT_BYTES:
                raise Stop('DEV_METADATA_OVERSIZE_STOP')
            pieces.append(piece)
        remaining = stop_at - time.monotonic()
        if remaining <= 0 or child.wait(timeout=remaining) != 0:
            raise Stop('DEV_METADATA_UNKNOWN_STOP')
        return b''.join(pieces).decode('utf-8', errors='strict')
    except Stop:
        raise
    except (Exception, KeyboardInterrupt):
        raise Stop('DEV_METADATA_UNKNOWN_STOP') from None
    finally:
        if selector is not None:
            selector.close()
        if child is not None:
            if child.poll() is None:
                child.kill()
            try:
                child.wait(timeout=2)
            except (Exception, KeyboardInterrupt):
                pass
            if child.stdout is not None:
                child.stdout.close()


def observe(role):
    name = PROJECT + '-' + role + '-1'
    argv = (DOCKER, '--host', 'unix:///var/run/docker.sock',
            'container', 'ls', '-a', '--no-trunc',
            '--filter', 'label=com.docker.compose.project=' + PROJECT,
            '--filter', 'label=com.docker.compose.service=' + role,
            '--filter', 'name=^/' + name + '$', '--format', FMT)
    raw = bounded_docker_read(argv)
    if raw == '':
        raise Stop('DEV_ROLE_MISSING_STOP')
    if not raw.endswith('\n') or raw.count('\n') != 1:
        raise Stop('DEV_ROLE_AMBIGUOUS_STOP')
    fields = raw[:-1].split('\t')
    if len(fields) != 6:
        raise Stop('DEV_METADATA_UNKNOWN_STOP')
    try:
        cid, found_name, state, networks, project, service = [json.loads(v) for v in fields]
    except (TypeError, ValueError):
        raise Stop('DEV_METADATA_UNKNOWN_STOP') from None
    if (any(type(v) is not str for v in (cid, found_name, state, networks, project, service))
            or not HEX64.fullmatch(cid) or found_name != name
            or project != PROJECT or service != role):
        raise Stop('DEV_LABEL_IDENTITY_STOP')
    if state != 'running':
        raise Stop('DEV_ROLE_STOPPED_STOP')
    if networks != NETWORK:
        raise Stop('DEV_NETWORK_RISK_STOP')
    return (cid, found_name, state, networks, project, service)


def verify():
    first = {role: observe(role) for role in ROLES}
    if len({row[0] for row in first.values()}) != len(ROLES):
        raise Stop('DEV_ROLE_AMBIGUOUS_STOP')
    second = {role: observe(role) for role in ROLES}
    if first != second:
        raise Stop('DEV_RUNTIME_CHANGED_STOP')
    # Only limited DEV-LABELLED list metadata; NOT independently attested DEV.
    return ('DEV_LABELLED_ROLES_OBSERVED', 'DEV_NETWORK_NAMES_OBSERVED')


def main():
    try:
        values = verify()
        rc = 0
    except Stop as exc:
        values = (exc.category,)
        rc = 1
    except (Exception, KeyboardInterrupt):
        values = ('DEV_METADATA_UNKNOWN_STOP',)
        rc = 1
    for value in values:
        print(value)
    print('DEV_OBJECT_PROVENANCE_UNVERIFIED')
    print('NODE_ROUTE_UNVERIFIED')
    print('WORKER_ROUTE_UNVERIFIED')
    print('DEV_PROD_SEPARATION_UNVERIFIED')
    print('POSTING_NO_GO')
    return rc


if __name__ == '__main__':
    sys.exit(main())
PYTHON
