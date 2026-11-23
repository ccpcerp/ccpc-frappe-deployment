#!/usr/bin/env bash
# Run ONLY inside isolated offline ccpc-recovery guest, as ccpc-restore.
# Create a NEW, EMPTY MariaDB testing instance; no host Docker or backups.
set -euo pipefail

stop() { printf 'STOP: %s\nPreserve state; do not rerun automatically.\n' "$*" >&2; exit 1; }

test "$(hostname -s)" = ccpc-recovery && test "$(id -un)" = ccpc-restore ||
  stop "wrong machine or user"
test "$(find /sys/class/net -mindepth 1 -maxdepth 1 -printf '%f\n')" = lo ||
  stop "recovery guest must only have loopback interface"
sudo systemctl is-active --quiet ccpc-recovery-docker.service ||
  stop "guest-only Docker engine not active"
test "$(sudo docker info --format '{{.DockerRootDir}}')" = /var/lib/ccpc-recovery-docker ||
  stop "wrong Docker data root"
test -z "$(sudo docker ps -a --format '{{.Names}}')" ||
  stop "guest already has containers; inspect first"
test -z "$(sudo docker volume ls -q)" ||
  stop "guest already has volumes; inspect first"
sudo docker image inspect mariadb:11.8 >/dev/null ||
  stop "offline MariaDB image not loaded"
sudo test ! -e /var/lib/ccpc-recovery-secrets/mariadb-root ||
  stop "guest password file already exists"

# Never put the generated password in a Docker env value, process command line,
# terminal output, guest source script, GitHub, or host filesystem.
sudo install -d -m 0700 /var/lib/ccpc-recovery-secrets
sudo sh -c '
set -eu
umask 077
od -An -N32 -tx1 /dev/urandom | tr -d " \n" > /var/lib/ccpc-recovery-secrets/mariadb-root
test "$(wc -c < /var/lib/ccpc-recovery-secrets/mariadb-root)" -eq 64
'
sudo docker volume create ccpc-recovery-mariadb-data >/dev/null

# Host network here means ONLY the isolated QEMU GUEST namespace; QEMU has
# -nic none and no port forwarding/host share. MariaDB binds guest loopback.
sudo docker run -d \
  --pull=never \
  --name ccpc-recovery-mariadb \
  --network host \
  --restart no \
  --memory 2g \
  --pids-limit 384 \
  -e MARIADB_ROOT_PASSWORD_FILE=/run/secrets/mariadb-root \
  -e MARIADB_ROOT_HOST=127.0.0.1 \
  --mount type=bind,source=/var/lib/ccpc-recovery-secrets,target=/run/secrets,readonly \
  --mount type=volume,source=ccpc-recovery-mariadb-data,target=/var/lib/mysql \
  mariadb:11.8 --bind-address=127.0.0.1

sudo docker ps --filter name=^/ccpc-recovery-mariadb$ \
  --format 'GUEST MARIADB CONTAINER: {{.Names}} {{.Status}}'
printf 'GUEST MARIADB: START REQUESTED, NEW EMPTY DATABASE ONLY\n'
printf 'NO BACKUP RESTORE OR HOST/PRODUCTION OPERATION\n'
