#!/usr/bin/env bash
# CCPC ERPNext: explicitly approved, source-only DEVELOPMENT update.
# Run manually on the Ubuntu host as the normal operator; never on PRODUCTION.
# No bench, database, Docker lifecycle, service, scheduler or worker commands.
# The only checkout change is a guarded detached switch to a pinned commit.
set -euo pipefail

DEV_CONTAINER='frappe_docker_devcontainer-frappe-1'

docker exec -i --user frappe "$DEV_CONTAINER" bash -s <<'CCPC_DEV_SOURCE_ONLY'
set -euo pipefail
umask 077
export GIT_TERMINAL_PROMPT=0
export GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10'
APP='/workspace/development/frappe-bench/apps/ccpcerp'
OLD='532a28d99bd0548241854495156a61f94eb1ac6b'
TARGET='e1d67f2716d15e8ffdf42f0547c44d8324516d7e'
REF='refs/heads/feature/finance-mapping-lifecycle-2026-10-28'

stop() { printf 'STOP: %s\n' "$1"; exit 1; }
[ "$(id -un)" = 'frappe' ] || stop 'not running as frappe'
[ -d "$APP/.git" ] || stop 'DEVELOPMENT app directory is not a normal Git checkout'
[ "$(git -C "$APP" rev-parse --show-toplevel)" = "$APP" ] || stop 'wrong Git root'
[ "$(git -C "$APP" rev-parse HEAD)" = "$OLD" ] || stop 'DEVELOPMENT HEAD changed since approved preflight'
if git -C "$APP" symbolic-ref -q HEAD >/dev/null 2>&1; then
  stop 'DEVELOPMENT is not in detached-HEAD state'
fi
[ -e "$APP/AGENTS.md" ] && [ ! -L "$APP/AGENTS.md" ] || stop 'protected AGENTS.md missing or symlinked'
[ "$(git -C "$APP" status --porcelain=v1 --untracked-files=all)" = '?? AGENTS.md' ] || stop 'tracked or untracked working tree differs from approved preflight'

REMOTE_URL="$(git -C "$APP" remote get-url origin)" || stop 'origin is not configured'
case "$REMOTE_URL" in
  git@github.com:ccpcerp/ccpcerp.git|ssh://git@github.com/ccpcerp/ccpcerp.git|https://github.com/ccpcerp/ccpcerp.git|https://github.com/ccpcerp/ccpcerp)
    ;;
  *) stop 'origin URL is not the reviewed CCPC GitHub repository (URL not printed)' ;;
esac

REMOTE_HEAD="$(git ls-remote "$REMOTE_URL" "$REF" 2>/dev/null | awk 'NR==1 {print $1}')" || stop 'cannot read verified GitHub branch without prompting'
[ "$REMOTE_HEAD" = "$TARGET" ] || stop 'GitHub Finance branch moved or is inaccessible'
printf 'PRECHECK PASS: pinned DEV source, protected AGENTS.md, and GitHub target\n'

# Fetch only the approved GitHub branch; no merge/pull, tags, submodules, refs, or pruning.
if ! git -C "$APP" -c gc.auto=0 fetch --no-tags --no-recurse-submodules --no-auto-gc --no-write-fetch-head "$REMOTE_URL" "$REF" >/dev/null 2>&1; then
  stop 'Git object fetch failed; source switch NOT attempted'
fi
[ "$(git -C "$APP" rev-parse --verify "$TARGET^{commit}")" = "$TARGET" ] || stop 'pinned target commit not present'
git -C "$APP" merge-base --is-ancestor "$OLD" "$TARGET" || stop 'target is not a descendant of pinned DEVELOPMENT HEAD'
[ "$(git -C "$APP" rev-list --count "$OLD..$TARGET")" = '6' ] || stop 'unexpected commit distance'
[ -z "$(git -C "$APP" ls-tree -r --name-only "$TARGET" -- AGENTS.md)" ] || stop 'target would track protected AGENTS.md'
EXPECTED_FILES="$(printf '%s\n' \
  '.circleci/test_four_reports_ci_config_static.py' \
  'ccpcerp/ccpc_erp/executive_reporting.py' \
  'ccpcerp/ccpc_erp/test_executive_reporting.py' \
  'ccpcerp/ccpc_erp/test_four_reports_28_disposable_integration.py')"
[ "$(git -C "$APP" diff --name-only "$OLD" "$TARGET")" = "$EXPECTED_FILES" ] || stop 'pinned source changes do not match four reviewed files'
[ "$(git -C "$APP" rev-parse HEAD)" = "$OLD" ] || stop 'HEAD changed during fetch'
[ "$(git -C "$APP" status --porcelain=v1 --untracked-files=all)" = '?? AGENTS.md' ] || stop 'working tree changed during fetch'

# Reviewed, non-destructive checkout. No reset/clean/stash/branch changes or hooks.
if ! git -C "$APP" -c core.hooksPath=/dev/null -c submodule.recurse=false switch --detach "$TARGET" >/dev/null 2>&1; then
  stop 'source switch failed; inspect current HEAD and status before any further action'
fi
if [ "$(git -C "$APP" rev-parse HEAD)" != "$TARGET" ] || \
   [ "$(git -C "$APP" status --porcelain=v1 --untracked-files=all)" != '?? AGENTS.md' ] || \
   [ ! -e "$APP/AGENTS.md" ]; then
  stop 'post-switch verification failed; DO NOT restart, migrate or attempt another update'
fi
printf 'SOURCE UPDATE PASS: DEVELOPMENT now at %s\n' "$TARGET"
printf 'PRESERVED: detached HEAD; only untracked AGENTS.md; no tracked changes\n'
printf 'NOT RUN: bench migrate, restarts, workers, schedulers, database writes, PRODUCTION\n'
CCPC_DEV_SOURCE_ONLY
