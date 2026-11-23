#!/usr/bin/env bash
# Prepare strictly image-only, read-only offline ISO media for the isolated
# Nov 23 DEVELOPMENT recovery VM. Host Docker reads only, VM untouched.
# Does NOT copy running containers, host mounts, site files, secrets, DB or backups.
set -euo pipefail
set -C
umask 077

stop() { printf 'STOP: %s\nPreserve one-shot private output and inspect before rerunning.\n' "$*" >&2; exit 1; }
say() { printf 'RECOVERY OFFLINE MEDIA: %s\n' "$*"; }
require() { command -v "$1" >/dev/null 2>&1 || stop "missing tool $1"; }

test "$(hostname -s)" = ccpcerpserver || stop "wrong host"
test "$(id -u)" = 1000 && test "$(id -un)" = gani || stop "must run as normal gani"
test -z "${DOCKER_HOST:-}" && test -z "${DOCKER_CONTEXT:-}" || stop "Docker override prohibited"
test "$(docker context show)" = default || stop "Docker context is not default"
test "$(docker info --format '{{.Name}}')" = ccpcerpserver || stop "Docker daemon identity mismatch"
test "$(docker inspect --format '{{.State.Running}}' frappe_docker_devcontainer-frappe-1)" = true ||
  stop "live DEVELOPMENT app container not running"
for prog in curl tar sha256sum split gzip docker df awk stat; do require "$prog"; done

ISO_TOOL=""
for candidate in genisoimage mkisofs; do
    if command -v "$candidate" >/dev/null 2>&1; then ISO_TOOL="$candidate"; break; fi
done
test -n "$ISO_TOOL" || stop "genisoimage or mkisofs missing; no output written"

# This image was built using the SHA-gated Nov23 reviewed Dockerfile and
# independently checked in a disposable, network-disabled inspection container.
APP=ccpc-recovery:dev-nov23-b0cbe5c
APP_ID=sha256:f53cc9ee316f758be669e4844655698b50776cd4cc3ccfb834bc433c1dec9bfb
DB=mariadb:11.8
REDIS=redis:alpine
test "$(docker image inspect --format '{{.Id}}' "$APP")" = "$APP_ID" || stop "app image identity mismatch"
test "$(docker image inspect --format '{{.Id}}' "$DB" | cut -c1-19)" = "sha256:efb4959ef2c8" ||
  stop "MariaDB image changed since owner inventory"
test "$(docker image inspect --format '{{.Id}}' "$REDIS" | cut -c1-19)" = "sha256:9d317178ecea" ||
  stop "Redis image changed since owner inventory"
test "$(docker image inspect --format '{{index .Config.Labels "org.ccpc.recovery.ccpcerp-sha"}}' "$APP")" =
  "b0cbe5c13cb68499a7920de2879f65e72cff000a" ||
  stop "app commit image label mismatch"

LAB="$HOME/ccpc-restore-labs"
test -d "$LAB" && test "$(stat -c '%u:%a' "$LAB")" = 1000:700 ||
  stop "private recovery lab directory not secure"
test "$(df -Pk "$LAB" | awk 'NR==2 {print $4}')" -gt 20971520 ||
  stop "need 20GiB free host workspace for image export and ISO"
ROOT="$LAB/ccpc-recovery-offline-media-20261123"
test ! -e "$ROOT" && test ! -L "$ROOT" || stop "one-shot media directory already exists"
mkdir -m 0700 "$ROOT"
PAYLOAD="$ROOT/iso-files"
mkdir -m 0700 "$PAYLOAD"

# Official Docker's self-contained Linux testing binaries; no host Docker
# daemon/socket is exported or mounted into the guest. Download is on host ONLY.
DOCKER_VERSION=29.7.2
DOCKER_NAME="docker-$DOCKER_VERSION.tgz"
DOCKER_URL="https://download.docker.com/linux/static/stable/x86_64/$DOCKER_NAME"
say "downloading official Docker static testing runtime $DOCKER_VERSION on host"
curl --fail --location --silent --show-error --proto '=https' --tlsv1.2 \
  --retry 2 --connect-timeout 15 --max-time 1200 \
  --output "$PAYLOAD/$DOCKER_NAME" "$DOCKER_URL"
tar -tzf "$PAYLOAD/$DOCKER_NAME" >"$ROOT/docker-archive-list.txt" ||
  stop "invalid Docker runtime tarball"
for required in docker/dockerd docker/docker docker/containerd docker/runc; do
  grep -Fxq "$required" "$ROOT/docker-archive-list.txt" ||
    stop "Docker runtime missing archive member $required"
done
if grep -Eq '(^/|(^|/)\.\.(/|$))' "$ROOT/docker-archive-list.txt"; then
  stop "Docker runtime archive contains an unsafe path"
fi
test "$(stat -c %s "$PAYLOAD/$DOCKER_NAME")" -gt 50000000 ||
  stop "Docker runtime tarball unexpectedly small"

say "exporting exactly 3 pre-validated immutable images (no live container or volume)"
say "app=$APP; db=$DB; redis=$REDIS"
# Split into <=1600MiB pieces because ISO9660 individual files have size
# limitations. Guest will stream these pieces directly into 'docker load'.
# Gzip minimizes host/guest media footprint; does not alter Docker images.
docker image save "$APP" "$DB" "$REDIS" |
  gzip -1 |
  split -b 1600m -d -a 3 - "$PAYLOAD/images.tgz.part-"
test -s "$PAYLOAD/images.tgz.part-000" || stop "no Docker image archive parts created"
cat "$PAYLOAD"/images.tgz.part-* | gzip -t ||
  stop "compressed Docker image archive fails integrity test"

cat >"$PAYLOAD/README.txt" <<'README'
CCPC November 23 DEVELOPMENT recovery guest OFFLINE RUNTIME/IMAGE MEDIA.
NO SQL, site_config, site files, SSH credentials or host Docker socket are included.
Never attach these image media to PRODUCTION.
Required guest: Ubuntu 24.04.5 LTS amd64. QEMU guest must remain -nic none.
Docker static runtime is from official Docker testing binaries, version 29.7.2.
Docker says binaries are suitable for testing, not production package management.
  https://docs.docker.com/engine/install/binaries
  https://download.docker.com/linux/static/stable/x86_64/
Docker image archive parts contain exactly these host Docker image tags:
  ccpc-recovery:dev-nov23-b0cbe5c
  mariadb:11.8
  redis:alpine
Application source is SHA-gated by build helper and remains unvalidated
against a restored DEVELOPMENT backup until the isolated restore test.
Verify SHA256SUMS inside the GUEST before unpacking, installing or loading.
No guest network is required and no host Docker daemon may be shared.
README
(
 cd "$PAYLOAD"
 sha256sum "$DOCKER_NAME" images.tgz.part-* > SHA256SUMS
)
say "constructing read-only ISO from non-secret Docker images and testing runtime"
"$ISO_TOOL" -quiet -r -J -iso-level 3 -V CCPCRECOVERY2026 -o "$ROOT/ccpc-recovery-offline.iso" "$PAYLOAD" ||
  stop "ISO generation failed"
test -s "$ROOT/ccpc-recovery-offline.iso" || stop "ISO missing"
sha256sum "$ROOT/ccpc-recovery-offline.iso" > "$ROOT/iso.sha256"
test "$(stat -c %a "$ROOT/ccpc-recovery-offline.iso")" = 600 ||
  stop "private ISO permissions mismatch"
echo "RECOVERY OFFLINE MEDIA: PASS"
printf 'ISO PATH: %s\n' "$ROOT/ccpc-recovery-offline.iso"
printf 'ISO SHA256: '
cut -d' ' -f1 "$ROOT/iso.sha256"
printf 'ISO SIZE BYTES: %s\n' "$(stat -c %s "$ROOT/ccpc-recovery-offline.iso")"
printf 'DOCKER RUNTIME VERSION: %s\n' "$DOCKER_VERSION"
printf 'APP IMAGE: %s\n' "$APP"
printf 'NO BACKUP DATA OR HOST FILES EXPORTED\n'
printf 'GUEST VM: NOT TOUCHED; NO GUEST NETWORK OR IMAGE IMPORT\n'
