#!/usr/bin/env bash
# Read-only runtime gate for the NEW Codex-only synthetic DEVELOPMENT agent.
# Never print environment variables, passwords or host mount source locations.
# Does NOT prove network egress isolation or authorize Codex access.
set -euo pipefail

if [[ $# -ne 1 || -z "${1:-}" ]]; then
  printf 'Usage: %s <dedicated-agent-container-name>\n' "${0##*/}" >&2
  exit 2
fi
if ! command -v docker >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
  echo "STOP: docker and python3 required." >&2
  exit 2
fi

docker inspect --type container "$1" | python3 -c '
import json
import sys

PROJECT = "ccpc_codex_dev_agent"
try:
    container, = json.load(sys.stdin)
except (ValueError, TypeError):
    print("STOP: container inspect did not return exactly one container")
    raise SystemExit(2)

config = container.get("Config") or {}
host = container.get("HostConfig") or {}
network = container.get("NetworkSettings") or {}
labels = config.get("Labels") or {}
errors = []

if labels.get("com.docker.compose.project") != PROJECT or labels.get("com.docker.compose.service") != "agent":
    errors.append("not the dedicated Codex agent Compose service")
if host.get("Privileged") or host.get("NetworkMode") == "host":
    errors.append("host/privileged Docker mode")
if host.get("PidMode") == "host" or host.get("IpcMode") == "host":
    errors.append("shared host namespaces")
if host.get("CapAdd") or host.get("Devices") or host.get("DeviceRequests"):
    errors.append("extra capabilities/devices")
if not host.get("ReadonlyRootfs"):
    errors.append("writable container root filesystem")
if not any("no-new-privileges" in str(x) for x in (host.get("SecurityOpt") or [])):
    errors.append("no-new-privileges missing")
if str(config.get("User") or "").strip() not in ("1000:1000", "1000"):
    errors.append("non-root image UID not pinned")
if host.get("PortBindings"):
    errors.append("host port publishing present")
if host.get("ExtraHosts"):
    errors.append("custom host mappings present")

networks = set((network.get("Networks") or {}).keys())
if networks != {PROJECT + "_lab"}:
    errors.append("network membership outside dedicated internal lab")

allowed_volumes = {
    PROJECT + "_agent-home": "/home/frappe",
    PROJECT + "_agent-cache": "/home/frappe/.cache",
}
seen_volumes = {}
secrets = 0
for mount in container.get("Mounts") or []:
    kind = str(mount.get("Type") or "")
    destination = str(mount.get("Destination") or "")
    source = str(mount.get("Source") or "")
    if kind == "volume":
        volume_name = str(mount.get("Name") or "")
        if allowed_volumes.get(volume_name) != destination or not mount.get("RW"):
            errors.append("unknown or read-only agent volume")
        seen_volumes[volume_name] = destination
    elif kind == "bind":
        # Compose implements Docker secrets as read-only bind mounts on local Engine.
        if (destination != "/run/secrets/db-user-password" or mount.get("RW")
                or not source.endswith("/codex-dev-agent/local-secrets/db-user-password")):
            errors.append("forbidden host bind mount")
        secrets += 1
    elif kind == "tmpfs":
        if destination not in ("/tmp", "/run"):
            errors.append("unexpected tmpfs mount")
    else:
        errors.append("unexpected mount type")
if seen_volumes != allowed_volumes:
    errors.append("expected private named volumes missing")
if secrets != 1:
    errors.append("synthetic user secret count is not one")

if errors:
    for reason in sorted(set(errors)):
        print("STOP: " + reason)
    print("Agent shell access: NOT AUTHORIZED")
    raise SystemExit(1)

print("PASS: expected isolated agent container mounts, user and basic privileges")
print("NOT VERIFIED: host firewall/proxy policy and production route exclusion")
print("NOT VERIFIED: source consistency, actual sandbox readiness or DEV backups")
print("Agent shell access: HOLD until separate network verification")
'
