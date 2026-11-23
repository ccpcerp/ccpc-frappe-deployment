#!/usr/bin/env bash
# One-time Redis cache + queue service staging inside the NO-NIC recovery VM.
# A local guest-only setup step, never for the physical DEVELOPMENT/PRODUCTION host.
# Nothing is restored, imported from backups, or exposed outside guest loopback.
set -euo pipefail

stop() { printf 'STOP: %s\nDo not rerun automatically; preserve guest state for review.\n' "$*" >&2; exit 1; }

test "$(hostname -s)" = ccpc-recovery && test "$(id -un)" = ccpc-restore ||
  stop "wrong host/user; must run in isolated recovery guest"
test "$(find /sys/class/net -mindepth 1 -maxdepth 1 -printf '%f\n')" = lo ||
  stop "unexpected guest network interface; only lo is allowed"
sudo systemctl is-active --quiet ccpc-recovery-docker.service ||
  stop "guest-only Docker engine is not running"
test "$(sudo docker info --format '{{.DockerRootDir}}')" = /var/lib/ccpc-recovery-docker ||
  stop "unexpected Docker data root"
test "$(sudo docker ps -a --format '{{.Names}}')" = ccpc-recovery-mariadb ||
  stop "expected exactly one existing MariaDB container"
test "$(sudo docker volume ls --format '{{.Name}}')" = ccpc-recovery-mariadb-data ||
  stop "unexpected preexisting Docker volume(s)"
sudo docker exec ccpc-recovery-mariadb healthcheck.sh --connect --innodb_initialized ||
  stop "MariaDB is not ready"
test "$(sudo ss -lntH '( sport = :3306 )' | awk '{print $4}')" = 127.0.0.1:3306 ||
  stop "MariaDB is not listening exclusively on guest IPv4 loopback"
test -z "$(sudo ss -lntH '( sport = :13000 )')" ||
  stop "Redis cache port 13000 already in use"
test -z "$(sudo ss -lntH '( sport = :11000 )')" ||
  stop "Redis queue port 11000 already in use"
sudo docker image inspect redis:alpine >/dev/null ||
  stop "offline Redis image missing"

# Docker host network is the QEMU GUEST network namespace with -nic none.
# Cache contains no confidential backup and uses no persistent disk.
sudo docker run -d --pull=never \
  --name ccpc-recovery-redis-cache --network host --restart no \
  --user redis --read-only \
  --tmpfs /tmp:rw,nosuid,noexec,size=16m \
  --memory 384m --pids-limit 96 \
  redis:alpine redis-server \
  --bind 127.0.0.1 --port 13000 --protected-mode yes \
  --appendonly no --save '' \
  --maxmemory 256mb --maxmemory-policy allkeys-lru

# Queue keeps background job state in a NEW guest-only named Docker volume.
# Official Redis image entrypoint manages /data volume file ownership.
sudo docker volume create ccpc-recovery-redis-queue-data >/dev/null
sudo docker run -d --pull=never \
  --name ccpc-recovery-redis-queue --network host --restart no \
  --read-only --memory 384m --pids-limit 96 \
  --mount type=volume,source=ccpc-recovery-redis-queue-data,target=/data \
  redis:alpine redis-server \
  --bind 127.0.0.1 --port 11000 --protected-mode yes \
  --appendonly yes --appendfsync everysec \
  --maxmemory 256mb --maxmemory-policy noeviction

printf 'REDIS CONTAINERS: START REQUESTED (guest-only)\n'
sudo docker ps --format '{{.Names}}  {{.Status}}'
printf 'NO GUEST NETWORK ADAPTERS / NO BACKUP RESTORE / NO HOST OR PRODUCTION OPERATION\n'
