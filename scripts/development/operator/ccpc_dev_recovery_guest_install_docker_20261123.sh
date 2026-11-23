#!/usr/bin/env bash
# RUN ONLY as ccpc-restore INSIDE the isolated Ubuntu 24.04.5 recovery VM.
# This is the one-time guest Docker TEST runtime setup from a verified local ISO.
# No guest networking, no package download, no image import, no backup restore.
set -euo pipefail
MEDIA=/mnt/ccpc-recovery-media

test "$(hostname)" = ccpc-recovery || { echo "STOP: not recovery guest" >&2; exit 1; }
test "$(id -un)" = ccpc-restore || { echo "STOP: wrong user" >&2; exit 1; }
test "$(findmnt -no FSTYPE "$MEDIA")" = iso9660
test "$(lsblk -n -o RO /dev/vdc | tr -d '[:space:]')" = 1
test ! -e /usr/local/bin/dockerd
test ! -e /etc/docker/daemon.json
test ! -e /etc/systemd/system/ccpc-recovery-docker.service
test ! -S /run/docker.sock
for tool in git ps xz; do command -v "$tool" >/dev/null; done
(cd "$MEDIA" && sha256sum -c SHA256SUMS)

sudo modprobe overlay
grep -w overlay /proc/filesystems
sudo install -d -m 0700 /opt/ccpc-recovery-docker-static
sudo tar -xzf "$MEDIA/docker-29.7.2.tgz" \
  -C /opt/ccpc-recovery-docker-static --no-same-owner
# The parent directory is root-owned 0700; expand the glob INSIDE sudo, not in the guest shell.
sudo sh -c 'set -eu; test -x /opt/ccpc-recovery-docker-static/docker/dockerd; test -x /opt/ccpc-recovery-docker-static/docker/docker; install -m 0755 /opt/ccpc-recovery-docker-static/docker/* /usr/local/bin/'
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
sudo tee /etc/systemd/system/ccpc-recovery-docker.service >/dev/null <<'UNIT'
[Unit]
Description=CCPC isolated recovery guest Docker testing engine
After=local-fs.target

[Service]
Type=notify
ExecStart=/usr/local/bin/dockerd --host=unix:///run/docker.sock --group=root --config-file=/etc/docker/daemon.json
Restart=no
TimeoutStartSec=120
UMask=0077

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl start ccpc-recovery-docker.service
sudo docker info --format 'Storage={{.Driver}} Cgroup={{.CgroupVersion}} Root={{.DockerRootDir}}'
echo 'GUEST DOCKER ENGINE: STARTED'
