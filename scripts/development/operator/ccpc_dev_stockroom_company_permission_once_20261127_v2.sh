#!/usr/bin/env bash
# CCPC ERPNext - ONE approved DEVELOPMENT-only Company User Permission addition.
# Replacement for the CONSUMED 2026-11-27 failed one-shot; never rerun that original.
# Source is intended for checksum-verified, operator-controlled one-shot staging.
# No PRODUCTION, app checkout edits, site migration or accounting postings.
set -euo pipefail
umask 077

HOST='ccpcerpserver'
APP='/home/gani/deployments/frappe_docker/development/frappe-bench/apps/ccpcerp'
CTR='frappe_docker_devcontainer-frappe-1'
WORK='/workspace/development/frappe-bench'
SITE='development.localhost'
EXPECTED='e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5'
NAS='/mnt/erpnext_backups'
BACKUP='ccpc-dev-preupdate-20261125_143912'

stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }
[[ "$(hostname -s)" == "$HOST" ]] || stop 'Unexpected host; no database mutation.'
[[ -d "$APP" ]] || stop 'Pinned DEVELOPMENT app path missing.'
[[ "$(git -C "$APP" rev-parse HEAD)" == "$EXPECTED" ]] || stop 'Host app commit drift.'
[[ "$(git -C "$APP" remote get-url origin)" == 'git@github.com:ccpcerp/ccpcerp.git' ]] || stop 'Host app origin drift.'
[[ -z "$(git -C "$APP" status --porcelain=v1 --untracked-files=all)" ]] || stop 'Host app checkout is dirty.'
[[ "$(findmnt -rn -M "$NAS" -o SOURCE)" == '//192.168.50.132/erpnext_backups' ]] || stop 'Expected off-host backup mount unavailable.'
[[ "$(findmnt -rn -M "$NAS" -o FSTYPE)" == 'cifs' ]] || stop 'Backup mount filesystem mismatch.'
[[ -d "$NAS/$BACKUP" ]] || stop 'Previously verified DEVELOPMENT backup directory missing.'

docker inspect "$CTR" --format '{{.State.Running}}' 2>/dev/null | grep -qx true || stop 'Expected DEVELOPMENT container not running.'
[[ "$(docker exec -u frappe -w "$WORK" "$CTR" git -C apps/ccpcerp rev-parse HEAD)" == "$EXPECTED" ]] || stop 'Container app commit drift.'
[[ -z "$(docker exec -u frappe -w "$WORK" "$CTR" git -C apps/ccpcerp status --porcelain=v1 --untracked-files=all)" ]] || stop 'Container app checkout is dirty.'
docker exec -u frappe -w "$WORK" "$CTR" test -x "$WORK/env/bin/python" || stop 'DEVELOPMENT bench Python is unavailable.'

printf 'PRECHECK PASS: pinned DEVELOPMENT-only host/container/site/app; prior NAS backup directory present.\n'
printf 'ACTION: exactly one CCPC Company User Permission for stockroom@personnel1.com (not a Finance signing grant).\n'

# The only database write occurs through Frappe User Permission.insert and one commit.
# Preconditions are checked within a DB transaction. Before-commit failures roll back.
# Any error DURING commit is UNCERTAIN: STOP and require independent read-only audit.
docker exec -i -u frappe -w "$WORK/sites" "$CTR" "$WORK/env/bin/python" -B - <<'PY'
import sys
from pathlib import Path

import frappe

SITE = "development.localhost"
SITES_PATH = "/workspace/development/frappe-bench/sites"
USER = "stockroom@personnel1.com"
COMPANY = "Cagayan Corn Products Corporation"
EXPECTED_ROLES = {"Stockroom Personnel", "CCPC Mapping Preparer"}
FORBIDDEN_ROLES = {"CCPC Accounting Mapping Approver"}

phase = "startup"
db_connected = False
commit_attempted = False

try:
    if Path.cwd() != Path(SITES_PATH):
        raise RuntimeError("Python working directory must equal pinned sites directory")
    for path in (Path(SITES_PATH).parent / "logs", Path(SITES_PATH) / SITE / "logs"):
        if not path.is_dir():
            raise RuntimeError("Required Frappe logger directory is missing")

    phase = "frappe.init"
    frappe.init(site=SITE, sites_path=SITES_PATH)
    if frappe.local.site != SITE:
        raise RuntimeError("Frappe site mismatch")
    phase = "frappe.connect / logger"
    frappe.connect()
    db_connected = True

    phase = "read-only identity and role checks"
    actual_schema = frappe.db.sql("SELECT DATABASE()", as_list=True)[0][0]
    if not actual_schema or str(actual_schema) != str(frappe.conf.db_name):
        raise RuntimeError("Development site database binding mismatch")

    users = frappe.db.sql(
        "SELECT name, enabled FROM `tabUser` WHERE name=%s FOR UPDATE",
        (USER,), as_dict=True,
    )
    if len(users) != 1 or int(users[0]["enabled"]) != 1:
        raise RuntimeError("Target user missing, duplicated, or disabled")
    if USER in ("Administrator", "Guest"):
        raise RuntimeError("Built-in users are forbidden")

    roles = frappe.db.sql(
        "SELECT role FROM `tabHas Role` "
        "WHERE parenttype='User' AND parent=%s ORDER BY name FOR UPDATE",
        (USER,), as_dict=True,
    )
    assigned = {entry["role"] for entry in roles}
    if (not EXPECTED_ROLES.issubset(assigned) or FORBIDDEN_ROLES.intersection(assigned)
            or "System Manager" in assigned):
        raise RuntimeError("Target Stockroom/Preparer/Approver role precondition failed")

    companies = frappe.db.sql(
        "SELECT name FROM `tabCompany` WHERE name=%s FOR UPDATE",
        (COMPANY,), as_dict=True,
    )
    if len(companies) != 1:
        raise RuntimeError("Target CCPC Company does not exist")

    old_grants = frappe.db.sql(
        "SELECT name, for_value, applicable_for, apply_to_all_doctypes "
        "FROM `tabUser Permission` WHERE user=%s AND allow='Company' "
        "ORDER BY name FOR UPDATE",
        (USER,), as_dict=True,
    )
    if old_grants:
        raise RuntimeError("Existing Company User Permission found: no repeat or overwrite")

    phase = "insert one User Permission"
    frappe.set_user("Administrator")
    doc = frappe.get_doc({
        "doctype": "User Permission",
        "user": USER,
        "allow": "Company",
        "for_value": COMPANY,
        "apply_to_all_doctypes": 1,
        "applicable_for": None,
        "is_default": 0,
        "hide_descendants": 1,
    })
    doc.insert(ignore_permissions=True)

    phase = "post-insert DB invariants"
    resulting = frappe.db.sql(
        "SELECT name, for_value, applicable_for, apply_to_all_doctypes, "
        "is_default, hide_descendants FROM `tabUser Permission` "
        "WHERE user=%s AND allow='Company' ORDER BY name FOR UPDATE",
        (USER,), as_dict=True,
    )
    if (len(resulting) != 1 or resulting[0]["name"] != doc.name
            or resulting[0]["for_value"] != COMPANY
            or (resulting[0]["applicable_for"] or "") != ""
            or int(resulting[0]["apply_to_all_doctypes"]) != 1
            or int(resulting[0]["is_default"]) != 0
            or int(resulting[0]["hide_descendants"]) != 1):
        raise RuntimeError("Post-insert grant invariant failed")

    phase = "commit"
    commit_attempted = True
    frappe.db.commit()
    phase = "after confirmed commit return"
    print("COMMITTED: exactly one CCPC Company User Permission added to the named DEVELOPMENT Stockroom preparer.", flush=True)
    print("NO Finance signature, mapping approval, account, stock, GL, app deployment or production change.")
except Exception as error:
    if commit_attempted:
        # SQL COMMIT may have succeeded before a callback raised. Do not imply rollback.
        print("STOP: COMMIT OUTCOME UNCERTAIN; do NOT retry; independently audit User Permission.", file=sys.stderr)
        print("Failure phase=" + phase + " error_type=" + type(error).__name__, file=sys.stderr)
    else:
        if db_connected:
            try:
                frappe.db.rollback()
            except Exception as rollback_error:
                print("STOP: rollback raised " + type(rollback_error).__name__, file=sys.stderr)
        print("STOP: no commit attempted; phase=" + phase + " error_type=" + type(error).__name__, file=sys.stderr)
    raise SystemExit(1)
finally:
    try:
        frappe.destroy()
    except Exception:
        pass
PY
