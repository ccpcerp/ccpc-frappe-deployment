#!/usr/bin/env bash
# CCPC ERPNext — reviewed ONE-SHOT, DEVELOPMENT-only PR45 SOURCE CHECKOUT.
# Does NOT run bench migrate, build, restart, install, site SQL, or backup.
# Does NOT change PRODUCTION. Must be SHA256 staged and separately approved.
# Do not rerun on any error. Do not use to undo a migration.
set -euo pipefail
umask 077

HOST='ccpcerpserver'
APP='/home/gani/deployments/frappe_docker/development/frappe-bench/apps/ccpcerp'
CTR='frappe_docker_devcontainer-frappe-1'
WORK='/workspace/development/frappe-bench'
OLD='e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5'
TARGET='afcc7b48ff8c664b0b0c781f89864995b9a59691'
BRANCH='review/stockroom-center-proposer-2026-11-27'
ORIGIN='git@github.com:ccpcerp/ccpcerp.git'
NAS='/mnt/erpnext_backups'
BACKUP='ccpc-dev-preupdate-20261125_143912'

stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }

# Never run from another machine or touch any sibling checkout.
[[ "$(hostname -s)" == "$HOST" ]] || stop 'Wrong host.'
[[ -d "$APP/.git" ]] || stop 'Expected DEVELOPMENT app Git metadata missing.'
[[ "$(git -C "$APP" rev-parse --show-toplevel)" == "$APP" ]] || stop 'App checkout root mismatch.'
[[ "$(git -C "$APP" remote get-url origin)" == "$ORIGIN" ]] || stop 'Unexpected app origin.'
[[ "$(git -C "$APP" rev-parse HEAD)" == "$OLD" ]] || stop 'Unexpected current app commit.'
[[ -z "$(git -C "$APP" status --porcelain=v1 --untracked-files=all)" ]] || stop 'Host app checkout dirty.'
if git -C "$APP" symbolic-ref -q HEAD >/dev/null 2>&1; then
    stop 'Expected a detached DEVELOPMENT checkout, not a branch.'
fi

docker inspect "$CTR" --format '{{.State.Running}}' 2>/dev/null | grep -qx true ||
    stop 'Expected DEVELOPMENT container unavailable.'
[[ "$(docker exec -u frappe -w "$WORK" "$CTR" git -C apps/ccpcerp rev-parse HEAD)" == "$OLD" ]] ||
    stop 'Container app commit drift.'
[[ -z "$(docker exec -u frappe -w "$WORK" "$CTR" git -C apps/ccpcerp status --porcelain=v1 --untracked-files=all)" ]] ||
    stop 'Container app checkout dirty.'
[[ "$(findmnt -rn -M "$NAS" -o SOURCE)" == '//192.168.50.132/erpnext_backups' ]] ||
    stop 'Expected NAS source unavailable.'
[[ "$(findmnt -rn -M "$NAS" -o FSTYPE)" == 'cifs' ]] ||
    stop 'Expected NAS filesystem mismatch.'
[[ -d "$NAS/$BACKUP" ]] || stop 'Existing recovery-point directory missing.'

# Verify the exact reviewed GitHub branch before fetching any object.
export GIT_TERMINAL_PROMPT=0
export GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10'
REMOTE_HEAD="$(git -C "$APP" ls-remote "$ORIGIN" "refs/heads/$BRANCH" |
    awk 'NR==1 {print $1}')"
[[ "$REMOTE_HEAD" == "$TARGET" ]] || stop 'PR45 branch moved from pinned reviewed commit.'

# Fetch changes only Git objects/FETCH_HEAD; it must not modify the working tree.
git -C "$APP" -c core.hooksPath=/dev/null fetch --no-tags "$ORIGIN" "refs/heads/$BRANCH"
[[ "$(git -C "$APP" rev-parse FETCH_HEAD)" == "$TARGET" ]] ||
    stop 'Fetched PR45 commit differs from reviewed SHA.'
git -C "$APP" merge-base --is-ancestor "$OLD" "$TARGET" ||
    stop 'Target is not a descendant of pinned DEVELOPMENT HEAD.'
git -C "$APP" diff --check "$OLD" "$TARGET" ||
    stop 'Reviewed source diff has whitespace errors.'

# Recheck immediately before the only working-tree change.
[[ "$(git -C "$APP" rev-parse HEAD)" == "$OLD" ]] || stop 'Host app HEAD changed during fetch.'
[[ -z "$(git -C "$APP" status --porcelain=v1 --untracked-files=all)" ]] ||
    stop 'Host app became dirty during fetch.'
[[ "$(docker exec -u frappe -w "$WORK" "$CTR" git -C apps/ccpcerp rev-parse HEAD)" == "$OLD" ]] ||
    stop 'Container app changed during fetch.'
[[ -z "$(docker exec -u frappe -w "$WORK" "$CTR" git -C apps/ccpcerp status --porcelain=v1 --untracked-files=all)" ]] ||
    stop 'Container app became dirty during fetch.'

printf 'PRECHECK PASS: exact clean DEVELOPMENT checkout and PR45 GitHub commit; old NAS backup present.\n'
printf 'ACTION: switch only the DEVELOPMENT custom app working tree to pinned PR45 commit.\n'
git -C "$APP" -c core.hooksPath=/dev/null switch --detach "$TARGET"

# Verification after checkout; a failure means STOP and inspect, never retry blindly.
[[ "$(git -C "$APP" rev-parse HEAD)" == "$TARGET" ]] || stop 'Post-switch host commit mismatch.'
[[ -z "$(git -C "$APP" status --porcelain=v1 --untracked-files=all)" ]] ||
    stop 'Post-switch host working tree is dirty.'
[[ "$(docker exec -u frappe -w "$WORK" "$CTR" git -C apps/ccpcerp rev-parse HEAD)" == "$TARGET" ]] ||
    stop 'Post-switch container commit mismatch.'
[[ -z "$(docker exec -u frappe -w "$WORK" "$CTR" git -C apps/ccpcerp status --porcelain=v1 --untracked-files=all)" ]] ||
    stop 'Post-switch container working tree is dirty.'
printf 'PASS: DEVELOPMENT SOURCE-ONLY PR45 checkout at %s\n' "$TARGET"
printf 'NOT RUN: bench migrate, build, restart, database write, Finance approval, stock/GL or PRODUCTION.\n'
printf 'HOLD: app is not claimed functionally deployed until separately approved site integration tests.\n'
