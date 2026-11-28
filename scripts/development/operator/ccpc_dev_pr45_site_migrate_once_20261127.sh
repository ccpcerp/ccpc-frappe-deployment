#!/usr/bin/env bash
# CCPC ERPNext PR45 — OWNER-APPROVED, ONE-SHOT DEVELOPMENT SITE MIGRATION.
# Site: development.localhost; no PRODUCTION, build/restart, Finance signing,
# stock/GL posting, restore, role grant or broad CLI site selection.
# The existing ccpcerp.setup.after_migrate CAN change DEV operational masters,
# workflow/role/DocPerm configuration. Owner approved this specific DEV migration.
# Do not run more than once or blindly retry if any command fails.
set -euo pipefail
umask 077

HOST='ccpcerpserver'
CTR='frappe_docker_devcontainer-frappe-1'
WORK='/workspace/development/frappe-bench'
APP='/home/gani/deployments/frappe_docker/development/frappe-bench/apps/ccpcerp'
SITE='development.localhost'
TARGET='afcc7b48ff8c664b0b0c781f89864995b9a59691'
ORIGIN='git@github.com:ccpcerp/ccpcerp.git'
NAS='/mnt/erpnext_backups'
DEST="$NAS/ccpc-dev-pre-pr45-20261127_175637"
SRC="$WORK/sites/$SITE/private/backups"
BASE='20261127_175637-development_localhost'
FILES=(
  "$BASE-database.sql.gz"
  "$BASE-files.tar"
  "$BASE-private-files.tar"
  "$BASE-site_config_backup.json"
)

stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }
trap 'printf "STOP: command failed at script line %s; NO AUTOMATIC RETRY OR RESTORE. Inspect DEVELOPMENT state first.\n" "$LINENO" >&2' ERR

# Exact host and clean, reviewed DEVELOPMENT checkout; no other container/site.
[[ "$(hostname -s)" == "$HOST" ]] || stop 'Wrong host.'
[[ "$(git -C "$APP" rev-parse --show-toplevel)" == "$APP" ]] || stop 'Unexpected app checkout root.'
[[ "$(git -C "$APP" remote get-url origin)" == "$ORIGIN" ]] || stop 'Unexpected app origin.'
[[ "$(git -C "$APP" rev-parse HEAD)" == "$TARGET" ]] || stop 'Unexpected host app commit.'
[[ -z "$(git -C "$APP" status --porcelain=v1 --untracked-files=all)" ]] ||
  stop 'Host app checkout is not clean.'
if git -C "$APP" symbolic-ref -q HEAD >/dev/null 2>&1; then
  stop 'Expected detached application checkout.'
fi
[[ "$(docker inspect "$CTR" --format '{{.State.Running}}' 2>/dev/null)" == 'true' ]] ||
  stop 'Expected DEVELOPMENT container is not running.'
[[ "$(docker exec -u frappe -w "$WORK" "$CTR" git -C apps/ccpcerp rev-parse HEAD)" == "$TARGET" ]] ||
  stop 'Container app HEAD does not match reviewed PR45.'
[[ -z "$(docker exec -u frappe -w "$WORK" "$CTR" git -C apps/ccpcerp status --porcelain=v1 --untracked-files=all)" ]] ||
  stop 'Container app checkout is not clean.'
docker exec -u frappe -w "$WORK" "$CTR" test -f "sites/$SITE/site_config.json" ||
  stop 'DEVELOPMENT site config missing.'

# Fresh prior backup must be present at expected Synology mount, complete and
# byte-for-byte equal to the four site backup source artifacts. Nothing written.
[[ "$(findmnt -rn -M "$NAS" -o SOURCE)" == '//192.168.50.132/erpnext_backups' ]] ||
  stop 'Expected NAS mount source unavailable.'
[[ "$(findmnt -rn -M "$NAS" -o FSTYPE)" == 'cifs' ]] ||
  stop 'Unexpected NAS mount filesystem.'
[[ -d "$DEST" && ! -L "$DEST" ]] || stop 'Verified NAS backup folder missing.'
for name in "${FILES[@]}"; do
  [[ -f "$DEST/$name" && ! -L "$DEST/$name" && -s "$DEST/$name" ]] ||
    stop 'Missing, empty or symlinked NAS backup component.'
  docker exec -u frappe -w "$WORK" "$CTR" bash -c     'test -f "$1" && test ! -L "$1" && test -s "$1"'     _ "$SRC/$name" || stop 'Missing DEVELOPMENT backup source component.'
  source_hash="$(docker exec -u frappe -w "$WORK" "$CTR" sha256sum "$SRC/$name")"
  source_hash="${source_hash%% *}"
  dest_hash="$(sha256sum "$DEST/$name")"
  dest_hash="${dest_hash%% *}"
  [[ "$source_hash" == "$dest_hash" ]] || stop 'Backup SHA256 drift detected.'
done
printf 'PRECHECK PASS: Fresh DEVELOPMENT with-files backup and NAS 4/4 SHA256 verified.\n'

# READ ONLY: confirm Finance protection, exact stockroom grant, Cost Center
# and untouched Withdrawal Slip Draft immediately before a write-capable migrate.
audit="$(docker exec -i -u frappe -w "$WORK" "$CTR"   bench --site "$SITE" mariadb --batch --raw <<'SQL'
START TRANSACTION READ ONLY;
SELECT CASE WHEN
  (SELECT COUNT(*) FROM `tabDocType` WHERE name IN (
    'CCPC Expense Mapping Scope',
    'CCPC Expense Mapping Revision',
    'CCPC Center Mapping Scope',
    'CCPC Center Mapping Revision',
    'CCPC Accounting Mapping Decision',
    'CCPC Mapping Decision Use',
    'CCPC Mapping Rejection Event',
    'CCPC Mapping Retirement Request',
    'CCPC Mapping Retirement Event')) = 9
AND (SELECT COUNT(*) FROM `tabDocPerm` WHERE parent IN (
    'CCPC Expense Mapping Scope',
    'CCPC Expense Mapping Revision',
    'CCPC Center Mapping Scope',
    'CCPC Center Mapping Revision',
    'CCPC Accounting Mapping Decision',
    'CCPC Mapping Decision Use',
    'CCPC Mapping Rejection Event',
    'CCPC Mapping Retirement Request',
    'CCPC Mapping Retirement Event')) = 0
AND (SELECT COUNT(*) FROM `tabCustom DocPerm` WHERE parent IN (
    'CCPC Expense Mapping Scope',
    'CCPC Expense Mapping Revision',
    'CCPC Center Mapping Scope',
    'CCPC Center Mapping Revision',
    'CCPC Accounting Mapping Decision',
    'CCPC Mapping Decision Use',
    'CCPC Mapping Rejection Event',
    'CCPC Mapping Retirement Request',
    'CCPC Mapping Retirement Event')) = 0
AND (SELECT COUNT(*) FROM `tabUser Permission`
     WHERE user='stockroom@personnel1.com' AND allow='Company') = 1
AND (SELECT COUNT(*) FROM `tabUser Permission`
     WHERE user='stockroom@personnel1.com'
       AND allow='Company'
       AND for_value='Cagayan Corn Products Corporation'
       AND apply_to_all_doctypes=1 AND IFNULL(applicable_for,'')=''
       AND is_default=0 AND hide_descendants=1) = 1
AND (SELECT COUNT(*) FROM `tabHas Role`
     WHERE parenttype='User' AND parent='stockroom@personnel1.com'
       AND role='Stockroom Personnel') = 1
AND (SELECT COUNT(*) FROM `tabHas Role`
     WHERE parenttype='User' AND parent='stockroom@personnel1.com'
       AND role='CCPC Mapping Preparer') = 1
AND (SELECT COUNT(*) FROM `tabHas Role`
     WHERE parenttype='User' AND parent='stockroom@personnel1.com'
       AND role IN ('CCPC Accounting Mapping Approver','System Manager')) = 0
AND (SELECT COUNT(*) FROM `tabUser`
     WHERE name='stockroom@personnel1.com' AND enabled=1) = 1
AND (SELECT COUNT(*) FROM `tabCost Center`
     WHERE name='Main - CCPC'
       AND company='Cagayan Corn Products Corporation'
       AND is_group=0) = 1
AND (SELECT COUNT(*) FROM `tabWithdrawal Slip`
     WHERE name='WS-2026-00008' AND status='Draft') = 1
THEN 'PASS' ELSE 'STOP' END AS pre_migration_baseline;
ROLLBACK;
SQL
)"
[[ "$(printf '%s\n' "$audit" | tail -n 1)" == 'PASS' ]] ||
  stop 'Pre-migration site read-only business/security baseline drift.'
printf 'PRECHECK PASS: Finance DocTypes, Stockroom authority, CCPC Center and saved Draft.\n'

# Recheck the app before any site write, then perform ONE site-scoped migration.
[[ "$(git -C "$APP" rev-parse HEAD)" == "$TARGET" ]] || stop 'App changed after preflight.'
[[ -z "$(git -C "$APP" status --porcelain=v1 --untracked-files=all)" ]] ||
  stop 'App became dirty after preflight.'
[[ "$(docker exec -u frappe -w "$WORK" "$CTR" git -C apps/ccpcerp rev-parse HEAD)" == "$TARGET" ]] ||
  stop 'Container app changed after preflight.'
printf 'ACTION: ONE write-capable bench migrate for DEVELOPMENT site %s only.\n' "$SITE"
printf 'NOTICE: full existing app after_migrate hooks run; no auto-rollback or retry.\n'
docker exec -u frappe -w "$WORK" "$CTR" bench --site "$SITE" migrate

printf 'MIGRATE COMMAND RETURNED SUCCESS for %s; post-migration audits PENDING.\n' "$SITE"
printf 'NOT RUN: build, service restart, restore, real Finance signing, stock/GL, PRODUCTION.\n'
printf 'SCRIPT CONSUMED: DO NOT RERUN; perform independent read-only DB/role/workflow acceptance.\n'
