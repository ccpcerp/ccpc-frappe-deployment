#!/usr/bin/env bash
# NEW-only A2 candidate empty Docker namespace creation. One-use.
# Authorized by owner 2026-11-09. NEVER touch OLD/DEV or protected clones.
# Preserves partially created resources on STOP; do NOT rerun blindly.
set -euo pipefail
export LC_ALL=C
stop() { printf 'STOP:A2_FOUNDATION_%s\n' "$1" >&2; exit 1; }

[[ "$(hostname -s)" == "ccpcerp-prod" && "$(id -un)" == "ccpcadmin" ]] || stop WRONG_HOST_USER
[[ ! ${DOCKER_HOST+x} && ! ${DOCKER_CONTEXT+x} ]] || stop AMBIENT_DOCKER_TARGET
[[ "$(sudo docker context show)" == "default" ]] || stop DOCKER_CONTEXT
[[ "$(sudo docker context inspect default --format '{{.Endpoints.docker.Host}}')" == "unix:///var/run/docker.sock" ]] || stop DOCKER_SOCKET

# Fail closed when any resource, including stopped containers, differs.
expected_containers=$(printf '%s\n' \
  ccpc_full_acceptance_20261107-db-1 \
  ccpc_full_acceptance_20261107-redis-cache-1 \
  ccpc_full_acceptance_20261107-redis-queue-1 \
  ccpc_restore_rehearsal_20261107-db-1 \
  ccpc_restore_rehearsal_20261107-redis-cache-1 \
  ccpc_restore_rehearsal_20261107-redis-queue-1 | sort)
expected_volumes=$(printf '%s\n' \
  ccpc_full_acceptance_20261107_db-data \
  ccpc_full_acceptance_20261107_logs \
  ccpc_full_acceptance_20261107_redis-queue-data \
  ccpc_full_acceptance_20261107_sites \
  ccpc_restore_rehearsal_20261107_db-data \
  ccpc_restore_rehearsal_20261107_logs \
  ccpc_restore_rehearsal_20261107_redis-queue-data \
  ccpc_restore_rehearsal_20261107_sites | sort)
expected_networks=$(printf '%s\n' \
  bridge host none \
  ccpc_full_acceptance_20261107_default \
  ccpc_restore_rehearsal_20261107_default | sort)

[[ "$(sudo docker ps -a --format '{{.Names}}' | sort)" == "$expected_containers" ]] || stop CONTAINER_INVENTORY_CHANGED
[[ "$(sudo docker volume ls --format '{{.Name}}' | sort)" == "$expected_volumes" ]] || stop VOLUME_INVENTORY_CHANGED
[[ "$(sudo docker network ls --format '{{.Name}}' | sort)" == "$expected_networks" ]] || stop NETWORK_INVENTORY_CHANGED
while IFS= read -r name; do
  [[ "$(sudo docker inspect --format '{{.State.Running}}' "$name")" == true ]] || stop REHEARSAL_SERVICE_NOT_RUNNING
done <<< "$expected_containers"

[[ "$(sudo docker image inspect --format '{{.Id}}' ccpcerp:v16.50.0)" == "sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8" ]] || stop APP_IMAGE_MISMATCH
[[ "$(sudo docker image inspect --format '{{.Id}}' mariadb:11.8)" == "sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4" ]] || stop DB_IMAGE_MISMATCH
[[ "$(sudo docker image inspect --format '{{.Id}}' redis:8.6-alpine)" == "sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763" ]] || stop REDIS_IMAGE_MISMATCH

backup_dir=/home/ccpcadmin/.ccpc-nov05-backup-transfer-20261106
[[ -d "$backup_dir" && ! -L "$backup_dir" ]] || stop BACKUP_DIR
(
  cd "$backup_dir"
  printf '%s\n' \
    '8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87  20261105_020001-ccpcerp_local-database.sql.gz' \
    '200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6  20261105_020001-ccpcerp_local-files.tar' \
    '60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf  20261105_020001-ccpcerp_local-private-files.tar' \
    'b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b  20261105_020001-ccpcerp_local-site_config_backup.json' \
    | sha256sum --check --status
) || stop BACKUP_HASH_MISMATCH

free_bytes=$(df -PB1 /var/lib/docker | awk 'NR==2 {print $4}')
[[ "$free_bytes" =~ ^[0-9]+$ && "$free_bytes" -ge 21474836480 ]] || stop LOW_DISK

project=ccpc_prod_erpnext
network="${project}_default"
volumes=(db-data logs redis-queue-data sites)
printf '%s\n' 'A2_NEW_HOST_AND_SOURCE_PREFLIGHT_PASS'

# First write in explicitly approved A2 scope: *only* new internal Docker
# bridge and four empty named volumes, labeled so Compose can adopt them.
# If any call fails, preserve the partially created resources for inspection.
sudo docker network create --driver bridge --internal \
  --label "com.docker.compose.project=$project" \
  --label "com.docker.compose.network=default" \
  --label "com.ccpc.stage=option-a-a2" \
  "$network" >/dev/null || stop PARTIAL_NETWORK_CREATION
[[ "$(sudo docker network inspect --format '{{.Internal}}|{{.Attachable}}|{{.Driver}}' "$network")" == "true|false|bridge" ]] || stop PARTIAL_NETWORK_NOT_INTERNAL

for volume in "${volumes[@]}"; do
  sudo docker volume create --driver local \
    --label "com.docker.compose.project=$project" \
    --label "com.docker.compose.volume=$volume" \
    --label "com.ccpc.stage=option-a-a2" \
    "${project}_$volume" >/dev/null || stop PARTIAL_VOLUME_CREATION
  [[ "$(sudo docker volume inspect --format '{{index .Labels "com.docker.compose.project"}}' "${project}_$volume")" == "$project" ]] || stop PARTIAL_VOLUME_LABEL
done

[[ "$(sudo docker ps -a --format '{{.Names}}' | sort)" == "$expected_containers" ]] || stop POSTCHECK_CONTAINER_INVENTORY
printf '%s\n' 'A2_SEPARATE_INTERNAL_NETWORK_CREATED_PASS'
printf '%s\n' 'A2_FOUR_EMPTY_CANDIDATE_VOLUMES_CREATED_PASS'
printf '%s\n' 'A2_SIX_EXISTING_REHEARSAL_CONTAINERS_PRESERVED'
printf '%s\n' 'A2_NO_APP_DATABASE_OR_WORKERS_STARTED'
