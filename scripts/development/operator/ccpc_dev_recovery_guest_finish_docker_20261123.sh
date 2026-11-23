#!/usr/bin/env bash
# Resume ONLY after successful manual guest-only Docker 29.7.2 binary copy.
# Configures an isolated, root-only Docker test engine inside ccpc-recovery.
# Does not access host Docker, deploy ERPNext, import images, or restore backups.
set -euo pipefail

stop() { printf 'STOP: %s\nDo not rerun automatically; preserve guest state for inspection.\n' "$*" >&2; exit 1; }

test "$(hostname -s)" = ccpc-recovery || stop "wrong hostname; use inside recovery guest ONLY"
test "$(id -un)" = ccpc-restore && test "$(id -u)" = 1000 ||
  stop "not normal ccpc-restore guest user"
test "$(findmnt -no FSTYPE /mnt/ccpc-recovery-media)" = iso9660 ||
  stop "verified offline ISO is not mounted"
test "$(lsblk -n -o RO /dev/vdc | tr -d '[:space:]')" = 1 ||
  stop "source ISO not read-only"
test "$(/usr/local/bin/docker --version)" = "Docker version 29.7.2, build a7dcaa6" ||
  stop "unexpected Docker CLI version"
test "$(/usr/local/bin/dockerd --version)" = "Docker version 29.7.2, build 6a43e3d" ||
  stop "unexpected dockerd version"
test ! -e /etc/docker/daemon.json || stop "guest daemon.json already exists"
test ! -e /etc/systemd/system/ccpc-recovery-docker.service ||
  stop "guest recovery Docker service already defined"
test ! -S /run/docker.sock || stop "Docker socket already exists; inspect guest first"
test -f /proc/filesystems && grep -qw overlay /proc/filesystems ||
  stop "guest overlay filesystem driver not available"
test "$(find /sys/class/net -mindepth 1 -maxdepth 1 | wc -l)" -eq 1 ||
  stop "guest has unexpected network interface(s); require no-NIC environment"
test -d /sys/class/net/lo || stop "guest loopback interface missing"

sudo install -d -m 0755 /etc/docker
sudo tee /etc/docker/daemon.json >/dev/null <<'JSON'
{
  "data-root": "/var/lib/ccpc-recovery-docker",
  "storage-driver": "overlay2",
  "features": {"containerd-snapshotter": false},
  "bridge": "none",
  "iptables": false,
  "ip6tables": false,
  "ip-forward": false,
  "ip-masq": false,
  "userland-proxy": false,
  "log-driver": "json-file",
  "log-opts": {"max-size": "10m", "max-file": "2"}
}
JSON

# Validate all daemon settings before creating or starting a system service.
sudo /usr/local/bin/dockerd --validate --config-file=/etc/docker/daemon.json ||
  stop "daemon configuration validation failed; no service installed"

sudo tee /etc/systemd/system/ccpc-recovery-docker.service >/dev/null <<'UNIT'
[Unit]
Description=CCPC isolated recovery guest Docker testing engine
After=local-fs.target

[Service]
Type=notify
ExecStart=/usr/local/bin/dockerd --host=unix:///run/docker.sock --group=root --config-file=/etc/docker/daemon.json
Restart=no
TimeoutStartSec=120
Delegate=yes
UMask=0077

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl start ccpc-recovery-docker.service ||
  stop "Docker service failed to start; check 'sudo systemctl status ccpc-recovery-docker.service --no-pager'"
sudo systemctl is-active --quiet ccpc-recovery-docker.service ||
  stop "guest Docker service not active"

sudo /usr/local/bin/docker info \
  --format 'Storage={{.Driver}} Cgroup={{.CgroupVersion}} Root={{.DockerRootDir}}' ||
  stop "guest Docker info failed"
if test -e /sys/class/net/docker0; then
  stop "unexpected Docker bridge created; inspect network configuration"
fi
printf 'GUEST DOCKER ENGINE: STARTED\n'
printf 'NO GUEST NETWORK INTERFACE OR DOCKER BRIDGE\n'
printf 'NO IMAGE IMPORT, CONFIDENTIAL BACKUP RESTORE, LIVE DEVELOPMENT OR PRODUCTION OPERATION\n'
