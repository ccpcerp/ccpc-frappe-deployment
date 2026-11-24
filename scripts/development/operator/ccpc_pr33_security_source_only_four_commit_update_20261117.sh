#!/usr/bin/env bash
# CCPC ERPNext: owner-approved source-only PR #33 gateway security update.
# Update only DEV detached app Git checkout; preserve all non-Git work.
# Owner explicitly approved source-only DEV update after exact-source 15-test Frappe PASS.
# No database access/migration, service start/restart, branch merge, PROD action.
set -euo pipefail
umask 077

stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }

[[ "$(hostname -s)" == 'ccpcerpserver' ]] || stop 'not original CCPC DEV host'
[[ "$(id -un)" == 'gani' ]] || stop 'normal operator gani required'
[[ "${CCPC_APPROVE_PR33_SOURCE_ONLY:-}" == 'YES' ]] || stop 'source-only execution not expressly enabled'
NAS='/mnt/erpnext_backups'
[[ "$(findmnt -rn -M "$NAS" -o SOURCE,FSTYPE)" == '//192.168.50.132/erpnext_backups cifs' ]] || stop 'protected NAS mount changed'
for pair in \
  'ccpc-development-pr33-20261104T010408Z-82316b860fe951ad:8' \
  'ccpc-development-pr33-billing-preacceptance-20261104T082044Z-4231b0c38ab77bf0:4'
do
  dir="$NAS/${pair%:*}"
  lines="${pair##*:}"
  [[ -d "$dir" && ! -L "$dir" && -f "$dir/SHA256SUMS" && ! -L "$dir/SHA256SUMS" ]] || stop 'protected backup manifest unavailable'
  [[ "$(wc -l < "$dir/SHA256SUMS")" == "$lines" ]] || stop 'protected backup manifest count changed'
done
printf 'PROTECTED_BACKUP_LOCATIONS=PASS (SHA256 independently operator-verified)\n'

DEV='frappe_docker_devcontainer-frappe-1'
# Host operator's existing Docker access is via sudo; retain nonroot operator identity.
# sudo is confined to read-only Docker metadata and exact named-container exec.
[[ "$(sudo docker inspect --format '{{.State.Running}}' "$DEV")" == 'true' ]] || stop 'DEV container not running'
[[ "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$DEV")" == 'frappe_docker_devcontainer' ]] || stop 'unexpected Compose project'

# The existing DEV container has a historical SSH bind mount. This bounded
# supervised operator command uses the GitHub origin only, no unrestricted agent.
sudo docker exec -i --user frappe "$DEV" bash -s <<'CCPC_DEV_SOURCE_ONLY'
set -euo pipefail
umask 077
export GIT_TERMINAL_PROMPT=0
export GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10'

APP='/workspace/development/frappe-bench/apps/ccpcerp'
OLD='1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc'
TARGET='25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87'
BRANCH='refs/heads/review/billing-authorization-correction-2026-11-03'
stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }
guard() {
  [[ "$(git -C "$APP" rev-parse HEAD)" == "$OLD" ]] || stop 'DEV HEAD changed'
  [[ "$(git -C "$APP" status --porcelain=v1 --untracked-files=all)" == '?? AGENTS.md' ]] || stop 'DEV worktree changed'
  [[ -f "$APP/AGENTS.md" && ! -L "$APP/AGENTS.md" ]] || stop 'protected AGENTS.md unavailable or symlink'
  ! git -C "$APP" symbolic-ref -q HEAD >/dev/null 2>&1 || stop 'DEV HEAD no longer detached'
}
[[ "$(id -un)" == 'frappe' ]] || stop 'not DEV frappe user'
[[ -d "$APP/.git" ]] || stop 'not normal DEV Git checkout'
[[ "$(git -C "$APP" rev-parse --show-toplevel)" == "$APP" ]] || stop 'unexpected Git root'
guard
[[ -z "$(git -C "$APP" ls-tree -r --name-only HEAD -- AGENTS.md)" ]] || stop 'protected AGENTS tracked in OLD'
PROTECTED_AGENTS_HASH="$(sha256sum "$APP/AGENTS.md" | awk '{print $1}')"
[[ "$PROTECTED_AGENTS_HASH" =~ ^[a-f0-9]{64}$ ]] || stop 'protected AGENTS checksum unavailable'

REMOTE="$(git -C "$APP" remote get-url origin)" || stop 'GitHub origin missing'
case "$REMOTE" in
  git@github.com:ccpcerp/ccpcerp.git|ssh://git@github.com/ccpcerp/ccpcerp.git|https://github.com/ccpcerp/ccpcerp.git|https://github.com/ccpcerp/ccpcerp) ;;
  *) stop 'unreviewed Git remote; remote URL not printed' ;;
esac
REMOTE_SHA="$(git ls-remote "$REMOTE" "$BRANCH" 2>/dev/null | awk 'NR==1 {print $1}')" || stop 'GitHub branch could not be verified'
[[ "$REMOTE_SHA" == "$TARGET" ]] || stop 'review branch moved; must re-review GitHub'

printf 'REMOTE_EXACT_PR33_HEAD=PASS\n'
if ! git -C "$APP" -c gc.auto=0 fetch --no-tags --no-recurse-submodules --no-auto-gc --no-write-fetch-head "$REMOTE" "$BRANCH" >/dev/null 2>&1; then
  stop 'source fetch failed; checkout NOT attempted'
fi
[[ "$(git -C "$APP" rev-parse --verify "$TARGET^{commit}")" == "$TARGET" ]] || stop 'target commit unavailable'
git -C "$APP" merge-base --is-ancestor "$OLD" "$TARGET" || stop 'target not descendant of installed HEAD'
[[ "$(git -C "$APP" rev-list --count "$OLD..$TARGET")" == '4' ]] || stop 'unexpected commit count'
[[ -z "$(git -C "$APP" ls-tree -r --name-only "$TARGET" -- AGENTS.md)" ]] || stop 'protected AGENTS tracked in TARGET'

EXPECTED_FILES="$(printf '%s\n' \
  'ccpcerp/ccpc_erp/executive_reporting.py' \
  'ccpcerp/ccpc_erp/test_executive_reporting.py')"
[[ "$(git -C "$APP" diff --name-only "$OLD" "$TARGET")" == "$EXPECTED_FILES" ]] || stop 'unexpected file changes in PR33 delta'
git -C "$APP" diff --check "$OLD" "$TARGET" >/dev/null || stop 'approved diff has whitespace errors'
guard

# No reset/clean/stash/pull, no tags/submodule recursion and no Git hooks.
if ! git -C "$APP" -c core.hooksPath=/dev/null -c submodule.recurse=false switch --detach "$TARGET" >/dev/null 2>&1; then
  stop 'checkout error; inspect state without automatic retries'
fi
[[ "$(git -C "$APP" rev-parse HEAD)" == "$TARGET" ]] || stop 'post-switch SHA mismatch'
[[ "$(git -C "$APP" status --porcelain=v1 --untracked-files=all)" == '?? AGENTS.md' ]] || stop 'post-switch worktree discrepancy'
[[ -f "$APP/AGENTS.md" && ! -L "$APP/AGENTS.md" ]] || stop 'protected AGENTS.md changed'
[[ "$(sha256sum "$APP/AGENTS.md" | awk '{print $1}')" == "$PROTECTED_AGENTS_HASH" ]] || stop 'protected AGENTS content changed'
! git -C "$APP" symbolic-ref -q HEAD >/dev/null 2>&1 || stop 'DEV no longer detached after update'
printf 'DEV_SOURCE_UPDATE=PASS\nDEV_SOURCE_HEAD=%s\nPROTECTED_AGENTS_ONLY=PASS\n' "$TARGET"
printf 'SOURCE_DELTA=4_COMMITS_2_PYTHON_FILES\n'
printf 'NOT_RUN=bench_migrate,benches,services,schedulers,user_grants,PRODUCTION\n'
CCPC_DEV_SOURCE_ONLY
