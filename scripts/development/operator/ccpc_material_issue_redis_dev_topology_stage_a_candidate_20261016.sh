#!/usr/bin/env bash
# CCPC DEVELOPMENT-only Stage A Redis topology METADATA candidate.
# REVIEW ONLY: neither staging nor execution on Ubuntu is authorized.
# Never infer PRODUCTION/Redis/Node/worker isolation or permission to post.
set -euo pipefail
umask 077

if [[ "${CCPC_DEV_REDIS_TOPOLOGY_A_APPROVED:-}" != 'ccpc-dev-redis-topology-a-one-shot' ]]; then
  printf '%s\n' 'STAGE_A_AUTHORIZATION_STOP' 'DEV_PROD_SEPARATION_UNVERIFIED' 'POSTING_NO_GO'
  exit 1
fi
if [[ "$(id -un 2>/dev/null || :)" != 'gani' || ! "$(id -u 2>/dev/null || :)" =~ ^[1-9][0-9]*$ ]]; then
  # This is intentionally restrictive; do not broaden the user boundary on host.
  printf '%s\n' 'STAGE_A_OPERATOR_STOP' 'DEV_PROD_SEPARATION_UNVERIFIED' 'POSTING_NO_GO'
  exit 1
fi
if ! command -v docker >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'STAGE_A_PREREQUISITE_STOP' 'DEV_PROD_SEPARATION_UNVERIFIED' 'POSTING_NO_GO'
  exit 1
fi

# The Python portion prints fixed result vocabulary only. Docker stdout/stderr,
# identifiers, networks, names and errors never reach user-visible output.
PYTHONDONTWRITEBYTECODE=1 python3 -I -B -S - <<'PYTHON'
"""Stage A only: exact-field DEV Docker metadata, no connection or config read."""
import json
import re
import subprocess
import sys

PROJECT = 'frappe_docker_devcontainer'
ROLES = ('frappe', 'redis-cache', 'redis-queue')
NETWORK = 'frappe_docker_devcontainer_default'
DOCKER = ('docker', '--host', 'unix:///var/run/docker.sock')
# This Go template intentionally extracts only six exact container fields and
# DEV network attachment name/id pairs, never environment, mounts or peer lists.
FORMAT = ("{{json .Id}}\n{{json .Name}}\n{{json .State.Running}}\n"
          "{{json (index .Config.Labels \"com.docker.compose.project\")}}\n"
          "{{json (index .Config.Labels \"com.docker.compose.service\")}}\n"
          "{{json .HostConfig.NetworkMode}}\n"
          "{{range $name, $net := .NetworkSettings.Networks}}"
          "{{json $name}} {{json $net.NetworkID}}\n{{end}}")
HEX64 = re.compile(r'[0-9a-f]{64}\Z')


class Stop(Exception):
    def __init__(self, category):
        self.category = category


def docker_read(args):
    # EXACT allowlisted command shapes; no shell, no Docker exec, no raw dump.
    result = subprocess.run(DOCKER + tuple(args), stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, timeout=10,
                            check=False, encoding='utf-8', errors='strict')
    if result.returncode != 0 or len(result.stdout) > 4096:
        raise Stop('DEV_NETWORK_UNKNOWN_STOP')
    return result.stdout


def inventory(role):
    args = ('container', 'ls', '-a', '--no-trunc',
            '--filter', 'label=com.docker.compose.project=' + PROJECT,
            '--filter', 'label=com.docker.compose.service=' + role,
            '--format', '{{.ID}}')
    lines = docker_read(args).splitlines()
    if not lines:
        raise Stop('DEV_ROLE_MISSING_STOP')
    if len(lines) != 1 or not HEX64.fullmatch(lines[0]):
        raise Stop('DEV_ROLE_AMBIGUOUS_STOP')
    return lines[0]


def inspect(cid, role):
    raw = docker_read(('inspect', '--type', 'container', '--format', FORMAT, cid))
    lines = raw.splitlines()
    if len(lines) != 7:
        raise Stop('DEV_NETWORK_UNKNOWN_STOP')
    try:
        ident, name, running, project, service, mode = [json.loads(x) for x in lines[:6]]
        net_name, net_id = (json.loads(x) for x in lines[6].split(' ', 1))
    except (ValueError, TypeError):
        raise Stop('DEV_NETWORK_UNKNOWN_STOP') from None
    if (type(ident) is not str or not HEX64.fullmatch(ident) or ident != cid or
            project != PROJECT or service != role or type(name) is not str or
            name != '/' + PROJECT + '-' + role + '-1'):
        raise Stop('DEV_IDENTITY_STOP')
    if type(running) is not bool or not running:
        raise Stop('DEV_ROLE_STOPPED_STOP')
    if (type(mode) is not str or mode != NETWORK or
            type(net_name) is not str or net_name != NETWORK or
            type(net_id) is not str or not HEX64.fullmatch(net_id)):
        raise Stop('DEV_NETWORK_RISK_STOP')
    return (cid, name, running, project, service, mode, net_name, net_id)


def verify():
    found = {role: inventory(role) for role in ROLES}
    if len(set(found.values())) != len(ROLES):
        raise Stop('DEV_ROLE_AMBIGUOUS_STOP')
    first = {role: inspect(found[role], role) for role in ROLES}
    if len({row[-1] for row in first.values()}) != 1:
        raise Stop('DEV_NETWORK_RISK_STOP')
    # Catch changed state/attachments across the bounded snapshot; still not
    # a durable/live process isolation claim, and not an atomic Docker view.
    second = {role: inspect(found[role], role) for role in ROLES}
    if first != second:
        raise Stop('DEV_RUNTIME_CHANGED_STOP')
    return ('DEV_IDENTITY_OK', 'DEV_REDIS_ROLES_PRESENT',
            'DEV_NETWORK_METADATA_CHECKED')


def main():
    try:
        statuses = verify()
        code = 0
    except Stop as exc:
        statuses = (exc.category,)
        code = 1
    except (Exception, KeyboardInterrupt):
        statuses = ('DEV_NETWORK_UNKNOWN_STOP',)
        code = 1
    for status in statuses:
        print(status)
    print('NODE_ROUTE_UNVERIFIED')
    print('WORKER_ROUTE_UNVERIFIED')
    print('DEV_PROD_SEPARATION_UNVERIFIED')
    print('POSTING_NO_GO')
    return code


if __name__ == '__main__':
    sys.exit(main())
PYTHON
