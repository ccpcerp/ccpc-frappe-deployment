#!/usr/bin/env bash
# Dedicated NEW host metadata-only review. NO writes, Docker compose up,
# config rendering, inspect of secret-bearing objects, or sudo.
# Review-only: requires owner approval and a verified local execution session.
set -euo pipefail

stop() {
  printf 'STOP: %s\n' "$1" >&2
  exit 1
}

[[ "$(id -un)" == "ccpcadmin" ]] ||
  stop "Expected dedicated host operator ccpcadmin (do not use sudo)"

host=$(hostnamectl --static 2>/dev/null) ||
  stop "Cannot verify local host identity"
[[ "$host" == "ccpcerp-prod" ]] ||
  stop "Wrong host identity (expected ccpcerp-prod)"

[[ ! ${DOCKER_HOST+x} && ! ${DOCKER_CONTEXT+x} &&
   ! ${DOCKER_CONFIG+x} ]] ||
  stop "Docker context/host/config overrides are present"

command -v docker >/dev/null ||
  stop "Docker CLI missing; no installation authorized"

context=$(docker context show 2>/dev/null) ||
  stop "Cannot read current Docker context"
[[ "$context" == "default" ]] ||
  stop "Docker context is not default"

endpoint=$(docker context inspect default --format '{{.Endpoints.docker.Host}}' 2>/dev/null) ||
  stop "Cannot read default Docker endpoint"
[[ "$endpoint" == "unix:///var/run/docker.sock" ]] ||
  stop "Docker endpoint is not the expected local Unix socket"

printf '%s\n' 'CHECK: dedicated host, operator, Docker default local context verified'
printf '%s\n' 'DOCKER_COMPOSE_VERSION (informational):'
docker compose version --short 2>/dev/null ||
  printf '%s\n' 'NOT_AVAILABLE (this does not prove a Compose render)'
printf '%s\n' 'CONTAINERS: name | compose project label | compose service label'
docker ps -a --format '{{.Names}} | {{.Label "com.docker.compose.project"}} | {{.Label "com.docker.compose.service"}}' 2>/dev/null ||
  stop "Container metadata query failed (do not use sudo)"
printf '%s\n' 'VOLUMES: name only'
docker volume ls --format '{{.Name}}' 2>/dev/null ||
  stop "Volume-name query failed (do not use sudo)"
printf '%s\n' 'NETWORKS: name only'
docker network ls --format '{{.Name}}' 2>/dev/null ||
  stop "Network-name query failed (do not use sudo)"
printf '%s\n' 'END: read-only metadata inventory (NOT project approval or deployment)'
