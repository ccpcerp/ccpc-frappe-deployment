#!/usr/bin/env bash
# One-time CCPC recovery-only Docker image build on DEVELOPMENT host.
# Never deploys a container, changes a running DEV site, exports data, or
# changes Docker Compose. All inputs are independently pinned in GitHub.
set -euo pipefail
set -C
umask 077

stop() { printf 'STOP: %s\nNo automatic rerun or cleanup.\n' "$*" >&2; exit 1; }
log() { printf 'RECOVERY IMAGE: %s\n' "$*"; }

EXPECTED_HOST=ccpcerpserver
EXPECTED_UID=1000
DEPLOY_REPO=git@github.com:ccpcerp/ccpc-frappe-deployment.git
DEPLOY_BRANCH=review/dev-restore-vm-staging-2026-11-23
# Older fixed commit on reviewed branch contains exact Containerfile, patch,
# and build config, independent of later changes to the review branch.
DEPLOY_COMMIT=23b5f6fbd35bcdfef6d3de8aaa57e4bc5f80d723
APP_REPO=git@github.com:ccpcerp/ccpcerp.git
APP_BRANCH=release/withdrawal-department-phase1-2026-11-17
FRAPPE_SHA=988e54f3c4c291e2077a83809663f123731abe76
ERPNEXT_SHA=4048fb70e14d1843956fcdabb7c3cca75a1cbcdd
CCPC_SHA=b0cbe5c13cb68499a7920de2879f65e72cff000a
PATCH_SHA=b543d14453d4370c6ddaf53bee8f8b786bf9199d5ce33182eb80aa5080e85ba1
OVERLAY_SHA=13bfff41433c9ac380b9ed632911674b9b87f7e7cb728388912ed50c79c63d0e
IMAGE_TAG=ccpc-recovery:dev-nov23-b0cbe5c
IMAGE_MARK=org.ccpc.recovery

test "$(hostname -s)" = "$EXPECTED_HOST" || stop "wrong server"
test "$(id -u)" = "$EXPECTED_UID" || stop "must run as normal gani user"
test "$(id -un)" = gani || stop "unexpected local username"
test -z "${DOCKER_HOST:-}" || stop "DOCKER_HOST override not allowed"
test -z "${DOCKER_CONTEXT:-}" || stop "DOCKER_CONTEXT override not allowed"
test "$(docker context show)" = default || stop "Docker context must be default"
test "$(docker info --format '{{.Name}}')" = "$EXPECTED_HOST" || stop "Docker daemon identity mismatch"
test "$(docker inspect --format '{{.State.Running}}' frappe_docker_devcontainer-frappe-1)" = true || stop "live DEVELOPMENT devcontainer is not running"
docker image inspect "$IMAGE_TAG" >/dev/null 2>&1 && stop "recovery image tag already exists; refuse overwrite"
command -v docker >/dev/null || stop "Docker CLI missing"
command -v git >/dev/null || stop "git missing"
command -v ssh-keygen >/dev/null || stop "ssh-keygen missing"
command -v python3 >/dev/null || stop "python3 missing"
docker buildx version >/dev/null || stop "buildx missing"

# Follow the repository's BuildKit secret-mount convention. SSH key is
# supplied to BuildKit ONLY as a session SSH source; it is not copied to the
# checkout or image. No stored key, site config or database enters build args.
BUILD_SSH_KEY="${CCPC_BUILD_SSH_KEY:-$HOME/.ssh/id_ed25519_ccpc_backup}"
KNOWN_HOSTS="${CCPC_BUILD_KNOWN_HOSTS:-$HOME/.ssh/known_hosts}"
test -f "$BUILD_SSH_KEY" && test -r "$BUILD_SSH_KEY" || stop "approved GitHub build SSH key not readable"
test -f "$KNOWN_HOSTS" && test -r "$KNOWN_HOSTS" || stop "known_hosts file not readable"
test ! -L "$BUILD_SSH_KEY" || stop "build SSH key path must not be symlink"
test "$(stat -c %u "$BUILD_SSH_KEY")" = "$EXPECTED_UID" || stop "build SSH key must be owned by gani"
case "$(stat -c %a "$BUILD_SSH_KEY")" in 400|600) ;; *) stop "build SSH key must be mode 0400 or 0600";; esac
ssh-keygen -F github.com -f "$KNOWN_HOSTS" >/dev/null || stop "github.com not in trusted SSH known_hosts"

LAB="$HOME/ccpc-restore-labs"
test -d "$LAB" && test "$(stat -c '%u:%a' "$LAB")" = 1000:700 || stop "private recovery lab directory missing"
test "$(df -Pk "$LAB" | awk 'NR==2 {print $4}')" -gt 20971520 || stop "less than 20 GiB host free space"
test -z "$(docker ps --format '{{.Names}}' | grep -E '^ccpc-recovery-' || true)" || stop "a recovery container is already running"

RUN="$LAB/ccpc-recovery-image-build-20261123"
test ! -e "$RUN" && test ! -L "$RUN" || stop "one-shot build directory already exists"
mkdir -m 0700 "$RUN" || stop "cannot create private one-shot directory"
test "$(stat -c '%u:%a' "$RUN")" = 1000:700 || stop "private build directory permissions"
GIT_DB="$RUN/git"
WORKTREE="$RUN/context"
mkdir -m 0700 "$GIT_DB" "$WORKTREE"
git -C "$GIT_DB" init -q
export GIT_TERMINAL_PROMPT=0
export GIT_SSH_COMMAND="ssh -o BatchMode=yes -o StrictHostKeyChecking=yes"
log "fetching reviewed deployment source privately"
git -C "$GIT_DB" fetch -q --depth=20 --no-tags "$DEPLOY_REPO" "refs/heads/$DEPLOY_BRANCH"
git -C "$GIT_DB" cat-file -e "$DEPLOY_COMMIT^{commit}" || stop "pinned reviewed source commit unavailable"
git -C "$GIT_DB" archive "$DEPLOY_COMMIT" | tar -x -C "$WORKTREE"
test -f "$WORKTREE/images/custom/Containerfile" || stop "reviewed Dockerfile not found"
test -f "$WORKTREE/resources/patches/erpnext-v16.34.2-ccpc.patch" || stop "ERPNext patch not found"
printf '%s  %s\n' "$PATCH_SHA" "$WORKTREE/resources/patches/erpnext-v16.34.2-ccpc.patch" |
  sha256sum -c - >/dev/null || stop "ERPNext patch checksum mismatch"

# Never use the deployment repository's older apps.json / CCPC_REF.
# Temporary build-only apps list points to the exact November release branch;
# the Dockerfile independently enforces the full immutable commit SHA.
python3 - "$RUN/apps.json" <<'PY'
import json, os, sys
dest=sys.argv[1]
apps=[
    {"url":"https://github.com/frappe/erpnext.git","branch":"v16.34.2"},
    {"url":"git@github.com:ccpcerp/ccpcerp.git",
     "branch":"release/withdrawal-department-phase1-2026-11-17"}
]
fd=os.open(dest, os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW, 0o600)
with os.fdopen(fd, "w") as f:
    json.dump(apps, f, indent=2)
    f.write("\n")
PY

log "building ONLY new local image tag $IMAGE_TAG (no container deployment)"
log "existing DEVELOPMENT image/DB and guest VM are not modified"
log "build log is private: $RUN/build.log"
# The original reviewed Dockerfile uses the SSH and secret mounts and validates
# each exact source SHA + approved ERPNext patch + overlay state.
if ! docker buildx build \
    --load \
    --progress=plain \
    --target backend \
    --pull=false \
    --tag "$IMAGE_TAG" \
    --label "$IMAGE_MARK.frappe-sha=$FRAPPE_SHA" \
    --label "$IMAGE_MARK.erpnext-sha=$ERPNEXT_SHA" \
    --label "$IMAGE_MARK.ccpcerp-sha=$CCPC_SHA" \
    --label "$IMAGE_MARK.deploy-commit=$DEPLOY_COMMIT" \
    --build-arg FRAPPE_BRANCH=v16.33.1 \
    --build-arg EXPECTED_FRAPPE_SHA="$FRAPPE_SHA" \
    --build-arg EXPECTED_ERPNEXT_SHA="$ERPNEXT_SHA" \
    --build-arg EXPECTED_CCPC_SHA="$CCPC_SHA" \
    --build-arg EXPECTED_ERPNEXT_PATCH_SHA="$PATCH_SHA" \
    --build-arg EXPECTED_ERPNEXT_OVERLAY_STATE_SHA="$OVERLAY_SHA" \
    --ssh "default=$BUILD_SSH_KEY" \
    --secret "id=github_known_hosts,src=$KNOWN_HOSTS" \
    --secret "id=apps_json,src=$RUN/apps.json" \
    --file "$WORKTREE/images/custom/Containerfile" \
    "$WORKTREE" >"$RUN/build.log" 2>&1; then
    stop "Docker image build failed; preserve private $RUN/build.log for review"
fi

log "verifying image without networking, host folders, DB or secrets"
IMAGE_ID="$(docker image inspect --format '{{.Id}}' "$IMAGE_TAG")" || stop "built image not found"
test "$(docker image inspect --format '{{index .Config.Labels "org.ccpc.recovery.ccpcerp-sha"}}' "$IMAGE_TAG")" = "$CCPC_SHA" ||
   stop "built image CCPC SHA metadata mismatch"
docker run --rm --network none --read-only --user 1000:1000 \
  --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 \
  --memory 768m --entrypoint /bin/sh "$IMAGE_TAG" -c '
    set -e
    cd /home/frappe/frappe-bench
    for a in frappe erpnext ccpcerp; do test -d "apps/$a"; done
    bench version
  ' > "$RUN/bench-version.txt" 2>&1 || stop "read-only application smoke test failed"
grep -Eq 'frappe 16[.]33[.]1' "$RUN/bench-version.txt" || stop "Frappe version mismatch"
grep -Eq 'erpnext 16[.]34[.]2' "$RUN/bench-version.txt" || stop "ERPNext version mismatch"
grep -Eq 'ccpcerp 0[.]0[.]1' "$RUN/bench-version.txt" || stop "CCPC version mismatch"

printf 'RECOVERY IMAGE BUILD: PASS\n'
printf 'IMAGE TAG: %s\n' "$IMAGE_TAG"
printf 'IMAGE ID: %s\n' "$IMAGE_ID"
printf 'FRAPPE GIT SHA: %s\n' "$FRAPPE_SHA"
printf 'ERPNEXT GIT SHA: %s\n' "$ERPNEXT_SHA"
printf 'CCPC GIT SHA: %s\n' "$CCPC_SHA"
printf 'IMAGE APP VERSIONS:\n'
cat "$RUN/bench-version.txt"
printf 'PRIVATE AUDIT DIRECTORY: %s\n' "$RUN"
printf 'NO DEPLOYMENT, IMAGE EXPORT, VM NETWORKING OR BACKUP RESTORE\n'
