#!/usr/bin/env bash
# Copyright (c) 2026, CCPC.
# Read-only gate for a *new* dedicated Codex DEVELOPMENT container.
# This does NOT validate host firewalls, DNS/IP routing or production network reachability.
set -euo pipefail

if [[ $# -ne 1 || -z "${1:-}" ]]; then
  printf 'Usage: %s <dedicated-agent-container-name>\n' "${0##*/}" >&2
  exit 2
fi
if ! command -v docker >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
  echo "STOP: docker and python3 are required for read-only container inspection." >&2
  exit 2
fi

container="$1"
# The inspector reads the JSON from stdin but prints only bounded status labels,
# never mount source paths, credentials or environment variable values.
docker inspect --type container "$container" |
python3 -c '
import json, sys

def stop(label, reason):
    print(f"STOP {label}: {reason}")
    return False

try:
    containers = json.load(sys.stdin)
except Exception:
    print("STOP: could not parse Docker inspect output")
    raise SystemExit(2)

if len(containers) != 1:
    print("STOP: expected exactly one container")
    raise SystemExit(2)

c = containers[0]
h = c.get("HostConfig") or {}
cfg = c.get("Config") or {}
mounts = c.get("Mounts") or []
state = c.get("State") or {}
errors = []

if h.get("Privileged") is True:
    errors.append("privileged container")
if h.get("NetworkMode") == "host":
    errors.append("host network mode")
if h.get("PidMode") == "host" or h.get("IpcMode") == "host":
    errors.append("shared host PID/IPC namespace")
if h.get("CapAdd"):
    errors.append("extra Linux capabilities")
if h.get("Devices") or h.get("DeviceRequests"):
    errors.append("device passthrough")
if not h.get("ReadonlyRootfs"):
    errors.append("writable root filesystem")
if not any("no-new-privileges" in str(x) for x in (h.get("SecurityOpt") or [])):
    errors.append("no-new-privileges is not enforced")
user = str(cfg.get("User") or "").strip()
if user in ("", "root", "0", "0:0"):
    errors.append("container does not declare a non-root user")

for m in mounts:
    if m.get("Type") != "volume":
        errors.append(f"mount type not allowed: {m.get(chr(84)+chr(121)+chr(112)+chr(101), chr(63))}")
    destination = str(m.get("Destination") or "")
    if any(destination == p or destination.startswith(p + "/") for p in (
        "/home/frappe/.ssh", "/root/.ssh", "/var/run", "/run/docker",
        "/mnt/erpnext_backups", "/workspace/development", "/srv/production",
    )):
        errors.append("forbidden mount destination present")
    if destination == "/":
        errors.append("root mount destination forbidden")

if errors:
    for error in sorted(set(errors)):
        print("STOP: " + error)
    print("Local container gate: FAILED. Agent access must remain disabled.")
    raise SystemExit(1)

print("Basic container mount/privilege gate: PASS")
print("Container running:", bool(state.get("Running")))
print("Network policy: NOT VERIFIED by this script")
print("Production/backup reachability: NOT VERIFIED by this script")
print("Dedicated-source isolation and real DEV write permissions: NOT VERIFIED")
print("Do not grant unrestricted Codex execution until separate firewall,")
print("private-network, worktree and backup gates pass.")
';
