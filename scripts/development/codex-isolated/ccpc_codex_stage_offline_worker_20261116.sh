#!/usr/bin/env bash
# CCPC DEV: one-use setup of CLEAN, OFFLINE Codex worker image and stopped probe.
# ONLY a new isolated Docker image/container is created. No existing container,
# DEV/PROD database, Git worktree, backup, network/firewall or service is changed.
# No credentials, models, or AGENTS.md mounted; no Codex agent launched.
set -euo pipefail
umask 077
stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }
[[ "$(hostname -s)" == "ccpcerpserver" ]] || stop "wrong host"
[[ "$(id -un)" == "gani" ]] || stop "operator must be gani"
[[ "${CCPC_APPROVE_CODEX_WORKER_SETUP:-}" == "YES" ]] || stop "setup not enabled"
[[ -z "${DOCKER_HOST:-}${DOCKER_CONTEXT:-}${DOCKER_TLS_VERIFY:-}${DOCKER_CERT_PATH:-}${DOCKER_CONFIG:-}" ]] || stop "Docker remote/context override set"
DOCKER=(sudo docker --host unix:///var/run/docker.sock)
[[ -S /var/run/docker.sock ]] || stop "expected Docker socket absent"
[[ "$("${DOCKER[@]}" info --format '{{.Name}}')" == "ccpcerpserver" ]] || stop "Docker daemon differs"
# This setup pulls a base image and installs the pinned npm CLI. Stop if the
# daemon's own Docker storage partition has insufficient free capacity.
DOCKER_ROOT="$("${DOCKER[@]}" info --format '{{.DockerRootDir}}')"
[[ "$DOCKER_ROOT" == /* ]] || stop "unexpected Docker storage root"
AVAILABLE="$(sudo df -PB1 "$DOCKER_ROOT" | awk 'NR==2 {print $4}')"
[[ "$AVAILABLE" =~ ^[0-9]+$ ]] || stop "Docker storage capacity unavailable"
[[ "$AVAILABLE" -ge 4294967296 ]] || stop "less than 4 GiB free on Docker storage filesystem"

# Check known OLD PROD app workers are stopped. Retained OLD MariaDB/Redis
# are allowed. Do not start, stop, remove, inspect data from, or modify them.
OLD_EXPECTED=(
  frappe_docker-frontend-1 frappe_docker-backend-1
  frappe_docker-websocket-1 frappe_docker-queue-short-1
  frappe_docker-queue-long-1 frappe_docker-scheduler-1
  frappe_docker-configurator-1 frappe_docker-db-1
  frappe_docker-redis-cache-1 frappe_docker-redis-queue-1
)
mapfile -t old_status < <("${DOCKER[@]}" ps -a \
  --filter label=com.docker.compose.project=frappe_docker \
  --format '{{.Names}} {{.State}}')
[[ "${#old_status[@]}" -eq "${#OLD_EXPECTED[@]}" ]] || stop "OLD project identities changed"
declare -A found=()
for entry in "${old_status[@]}"; do
  read -r name state extra <<<"$entry"
  [[ -n "${name:-}" && -n "${state:-}" && -z "${extra:-}" ]] || stop "invalid OLD status data"
  allowed=false
  for expected in "${OLD_EXPECTED[@]}"; do
    [[ "$name" == "$expected" ]] && allowed=true
  done
  [[ "$allowed" == true && -z "${found[$name]:-}" ]] || stop "unknown/duplicate OLD container"
  found["$name"]=1
  case "$name" in
    frappe_docker-db-1|frappe_docker-redis-cache-1|frappe_docker-redis-queue-1)
      ;; # PRESERVE old data services
    *)
      [[ "$state" == "exited" || "$state" == "created" || "$state" == "dead" ]] ||
        stop "OLD PRODUCTION application process active"
      ;;
  esac
done
[[ "${#found[@]}" -eq 10 ]] || stop "OLD project membership changed"
[[ "$("${DOCKER[@]}" inspect --format '{{.State.Running}}' \
     frappe_docker_devcontainer-frappe-1)" == "true" ]] || stop "DEV container not running"
[[ "$("${DOCKER[@]}" inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' \
     frappe_docker_devcontainer-frappe-1)" == "frappe_docker_devcontainer" ]] ||
  stop "wrong DEV Compose identity"
echo "SHARED_HOST_SCOPE=PASS"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
[[ -f "$SCRIPT_DIR/Dockerfile" && ! -L "$SCRIPT_DIR/Dockerfile" ]] || stop "reviewed Dockerfile missing"
IMAGE='ccpc-codex-isolated:0.161.0-offline'
PROBE='ccpc-codex-isolated-offline-probe-20261116'
if "${DOCKER[@]}" image inspect "$IMAGE" >/dev/null 2>&1; then
  stop "image tag exists; inspect it, no automatic replacement"
fi
if "${DOCKER[@]}" container inspect "$PROBE" >/dev/null 2>&1; then
  stop "probe exists; no automatic replacement"
fi

# Build pulls a clean published Node base and pinned npm CLI release.
# No host volumes, SSH agents, tokens or password environment supplied.
echo "BUILDING_NEW_CLEAN_CODEX_IMAGE=START"
"${DOCKER[@]}" build --pull --file "$SCRIPT_DIR/Dockerfile" \
  --tag "$IMAGE" \
  --label 'ccpc.scope=isolated-dev-codex-offline-setup' \
  "$SCRIPT_DIR" || stop "image build failed; no automatic retry"
IMAGE_ID="$("${DOCKER[@]}" image inspect --format '{{.Id}}' "$IMAGE")"
[[ "$IMAGE_ID" == sha256:* ]] || stop "built image identity not verified"

# Creates only a new stopped probe with NO mounts, no network, no host PID,
# no socket, no secrets, no privileges and no auto-restart.
"${DOCKER[@]}" container create --name "$PROBE" \
  --network none --read-only --user 14532:14532 \
  --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 64 --memory 768m --cpus 1 --restart no \
  "$IMAGE_ID" --version >/dev/null || stop "probe create failed"
value() { "${DOCKER[@]}" container inspect --format "$1" "$PROBE"; }
[[ "$(value '{{.HostConfig.NetworkMode}}')" == none ]] || stop "network isolation failed"
[[ "$(value '{{.HostConfig.ReadonlyRootfs}}')" == true ]] || stop "writable root"
[[ "$(value '{{.HostConfig.Privileged}}')" == false ]] || stop "privileged probe"
[[ "$(value '{{.Config.User}}')" == '14532:14532' ]] || stop "identity mismatch"
[[ "$(value '{{json .HostConfig.CapDrop}}')" == '["ALL"]' ]] || stop "caps not dropped"
[[ "$(value '{{len .Mounts}}')" == 0 ]] || stop "unexpected mount"
[[ "$(value '{{json .HostConfig.SecurityOpt}}')" == *no-new-privileges* ]] ||
  stop "no-new-privileges absent"
[[ "$(value '{{.HostConfig.RestartPolicy.Name}}')" == no ]] || stop "restart policy enabled"
echo "ISOLATED_PROBE_CONFIG=PASS"

# Starts only 'codex --version', NOT a Codex model or analysis session.
version="$(timeout --foreground 60s "${DOCKER[@]}" container start --attach "$PROBE")" ||
  stop "CLI smoke failed or exceeded bounded probe time; inspect retained probe"
[[ "$version" == "codex-cli 0.161.0" ]] || stop "Codex CLI version mismatch"
[[ "$(value '{{.State.Running}}')" == false ]] || stop "probe still running"
[[ "$(value '{{.State.ExitCode}}')" == 0 ]] || stop "probe exit not zero"
echo "ISOLATED_CODEX_CLI_VERSION=0.161.0"
echo "OFFLINE_WORKER_STAGE=PASS"
echo "PROBE_STOPPED=YES"
echo "NETWORK=NONE"
echo "NO_MODEL_AUTH_OR_AGENT_RUN=PASS"
echo "CURRENT_DEV_AND_PRODUCTION_UNCHANGED_BY_THIS_SETUP=YES"
