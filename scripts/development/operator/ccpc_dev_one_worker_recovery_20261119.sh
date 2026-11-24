#!/usr/bin/env bash
set -euo pipefail

if [[ "$(hostname -s)" != "ccpcerpserver" || "$(id -un)" != "gani" ]]; then
  echo "STOP: WRONG HOST OR OPERATOR"
  exit 1
fi

dev=frappe_docker_devcontainer-frappe-1
if [[ "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" != true ]] ||
   [[ "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" != frappe_docker_devcontainer ]]; then
  echo "STOP: WRONG OR STOPPED DEVELOPMENT CONTAINER"
  exit 1
fi

sudo docker exec --user frappe --workdir /workspace/development/frappe-bench "$dev" bash -s <<'PRECHECK'
set -euo pipefail
if [[ "$(git -C apps/ccpcerp rev-parse HEAD)" != 25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87 ]] ||
   [[ "$(git -C apps/ccpcerp status --porcelain=v1 --untracked-files=all)" != "?? AGENTS.md" ]] ||
   [[ "$(git -C .ccpc-phase1-release-stage-20261119-55eb10b86a57 rev-parse HEAD)" != 55eb10b86a57de55a97e293a78228d9dd17b809a ]]; then
  echo "STOP: PROTECTED DEVELOPMENT CODE STATE CHANGED"
  exit 1
fi
if [[ "$(grep -Ec '^worker:' Procfile)" != 1 ]] || [[ ! -w logs ]]; then
  echo "STOP: EXPECTED PROCFILE WORKER OR LOG DIRECTORY NOT AVAILABLE"
  exit 1
fi

for site in development.localhost ccpc-integration2.localhost; do
  result=$(FRAPPE_STREAM_LOGGING=1 bench --site "$site" doctor 2>&1) || { echo "STOP: BENCH DOCTOR FAILED FOR $site"; exit 1; }
  count=$(printf '%s\n' "$result" | awk '/^[[:space:]]*Workers online:/ {print $3}' | tail -n 1)
  if [[ ! "$count" =~ ^[0-9]+$ ]]; then
    echo "STOP: WORKER REGISTRY COULD NOT BE READ FOR $site"
    exit 1
  fi
  echo "REGISTERED WORKERS $site: $count"
  if (( count != 0 )); then
    echo "STOP: ALREADY REGISTERED WORKER; NO EXTRA WORKER CREATED"
    exit 1
  fi
done

python - <<'PY'
import os, re
hits=[]
pattern = re.compile(r'(?:\bbench\s+worker\b|\bfrappe\s+worker\b|frappe\.utils\.background_jobs|\brq\s+worker\b|\bhoncho\s+start\s+worker\b)')
for entry in os.scandir('/proc'):
    if not entry.name.isdigit():
        continue
    try:
        with open(f'/proc/{entry.name}/cmdline', 'rb') as fh:
            command=fh.read().replace(b'\0',b' ').decode('utf-8','replace')
        if pattern.search(command):
            hits.append(int(entry.name))
    except (OSError, PermissionError):
        continue
print(f'EXISTING WORKER-LIKE PROCESSES IN DEV: {len(hits)}')
if hits:
    raise SystemExit('STOP: WORKER PROCESS EXISTS BUT IS NOT REGISTERED; DIAGNOSE IT, DO NOT DUPLICATE')
print('ONE-WORKER DEVELOPMENT PRECHECK: PASS')
PY
PRECHECK

# Only execute this after every read-only guard above passed.
# Run the existing worker service from the bench Procfile, without restarting Honcho's other services.
sudo docker exec -d --user frappe --workdir /workspace/development/frappe-bench "$dev" \
  bash -lc 'exec honcho start worker >> logs/ccpc-dev-one-worker-recovery.log 2>&1'
echo "ONE DEVELOPMENT WORKER LAUNCH REQUESTED"
sleep 7

sudo docker exec --user frappe --workdir /workspace/development/frappe-bench "$dev" bash -s <<'VERIFY'
set -euo pipefail
for site in development.localhost ccpc-integration2.localhost; do
  result=$(FRAPPE_STREAM_LOGGING=1 bench --site "$site" doctor 2>&1) || { echo "VERIFY: DOCTOR FAILED $site; NO AUTOMATIC RETRY"; exit 1; }
  count=$(printf '%s\n' "$result" | awk '/^[[:space:]]*Workers online:/ {print $3}' | tail -n 1)
  echo "AFTER LAUNCH WORKERS $site: ${count:-UNKNOWN}"
done
echo "VERIFY: NO APP SWITCH, SITE MIGRATION, REDIS PURGE OR PRODUCTION CHANGE"
VERIFY
