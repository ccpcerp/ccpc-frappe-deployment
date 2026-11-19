#!/usr/bin/env bash
# One-time MAIN-only Phase1 DEVELOPMENT migration. No other site.
# No PRODUCTION actions, service restart, or automatic migration retry.
set -euo pipefail

if [[ "$(hostname -s)" != "ccpcerpserver" || "$(id -un)" != "gani" ]]; then
  echo "STOP: WRONG HOST OR OPERATOR"; exit 1
fi
dev=frappe_docker_devcontainer-frappe-1
if [[ "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" != true ]] ||
   [[ "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" != frappe_docker_devcontainer ]]; then
  echo "STOP: WRONG OR STOPPED DEVELOPMENT CONTAINER"; exit 1
fi

sudo docker exec -i --user frappe \
  --workdir /workspace/development/frappe-bench/sites \
  --env FRAPPE_STREAM_LOGGING=1 \
  "$dev" /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
from pathlib import Path
import importlib.util
import pwd
import re
import subprocess

B = Path("/workspace/development/frappe-bench")
APP = B / "apps/ccpcerp"
PRESERVE = B / "apps/.ccpcerp-preserved-pr33-20261119-25a7b6be"
SITE = "development.localhost"
FRAPPE_UID = pwd.getpwnam("frappe").pw_uid

def stop(reason):
    raise SystemExit("STOP: " + reason)

def git(repo, *args):
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, timeout=25,
    )
    if p.returncode:
        stop("GIT VALIDATION FAILED")
    return p.stdout.strip()

if git(APP, "rev-parse", "HEAD") != "55eb10b86a57de55a97e293a78228d9dd17b809a":
    stop("ACTIVE RELEASE SHA CHANGED")
if git(PRESERVE, "rev-parse", "HEAD") != "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87":
    stop("PROTECTED ORIGINAL SHA CHANGED")
if git(PRESERVE, "status", "--porcelain=v1", "--untracked-files=all") != "?? AGENTS.md":
    stop("PROTECTED ORIGINAL SOURCE/AGENTS STATUS CHANGED")
if not (PRESERVE / "AGENTS.md").is_file():
    stop("OWNER AGENTS.MD NOT PRESERVED")
spec = importlib.util.find_spec("ccpcerp")
if not spec or not spec.origin or Path(spec.origin).resolve() != (APP / "ccpcerp/__init__.py").resolve():
    stop("PYTHON IMPORT NOT AT RELEASE PATH")
for site, snap in (
    ("ccpc-integration2.localhost", "ccpc-integration2.localhost-20261118T233442Z-8db803832468"),
    ("development.localhost", "development.localhost-20261118T233442Z-8db803832468"),
):
    if not (B / "sites" / site / "site_config.json").is_file():
        stop("PROTECTED DEV SITE CONFIG MISSING")
    if not (B / ".ccpc-pr32-snapshots" / snap / "SHA256SUMS").is_file():
        stop("PROTECTED NOV19 BACKUP MANIFEST MISSING")

# Reject lingering Honcho sessions, background jobs and concurrent migrations.
# Never print other processes' command lines.
active = 0
for entry in Path("/proc").iterdir():
    if not entry.name.isdecimal():
        continue
    try:
        stat = (entry / "stat").read_text().rsplit(")", 1)[1].split()
        if stat[0] in ("Z", "X"):
            continue
        pgrp, sid = int(stat[2]), int(stat[3])
        if pgrp in (543180, 546647) or sid in (543180, 546647):
            active += 1
            continue
        if entry.stat().st_uid != FRAPPE_UID:
            continue
        argv = " ".join(
            a.decode("utf-8", "replace")
            for a in (entry / "cmdline").read_bytes().split(b"\0")
            if a
        )
        if re.search(
            r"(?:\bhoncho\s+start\b|\bbench\s+(?:start|worker|schedule)\b|"
            r"\bbench\s+--site\s+\S+\s+migrate\b|rq\.worker|"
            r"frappe\.utils\.(?:scheduler|background_jobs)|socketio\.js|gunicorn|werkzeug)",
            argv, re.I,
        ):
            active += 1
    except (OSError, ValueError, IndexError):
        continue
if active:
    stop(f"DEVELOPMENT PROCESS GUARD FAILED ({active} CANDIDATES)")
print("MAIN MIGRATION SERVICE PROCESS GUARD: PASS")

import frappe
connected = False
try:
    frappe.init(site=SITE, sites_path=".")
    frappe.connect()
    connected = True
    if "ccpcerp" not in frappe.get_installed_apps():
        stop("CCPC APP NOT INSTALLED")
    patches = {
        line.strip()
        for line in (APP / "ccpcerp/patches.txt").read_text().splitlines()
        if line.strip().startswith("ccpcerp.patches.")
    }
    recorded = {row[0] for row in frappe.db.sql("SELECT patch FROM " + chr(96) + "tabPatch Log" + chr(96), as_list=True)}
    if len(patches) != 8 or not patches.issubset(recorded):
        stop("CCPC PATCH INVENTORY DEVIATED FROM 8/8")
    counts = {
        name: int(frappe.db.sql("SELECT COUNT(*) FROM " + chr(96) + "tab" + name + chr(96))[0][0])
        for name in ("Company", "MRS", "Purchase Order", "Withdrawal Slip", "CCPC Personnel")
    }
    expected = {"Company": 25, "MRS": 3, "Purchase Order": 5, "Withdrawal Slip": 7, "CCPC Personnel": 10}
    if counts != expected:
        stop("MAIN MASTER/VOUCHER COUNTS CHANGED SINCE PREFLIGHT")
    # Recheck whether previously ineligible legacy rows became eligible.
    # Stop before after_migrate can alter these rows unexpectedly.
    personnel = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabCCPC Personnel` p
        LEFT JOIN `tabDepartment` d ON d.name=p.department
        WHERE COALESCE(p.company,'')=''
          AND COALESCE(p.department,'')!=''
          AND COALESCE(d.company,'')!=''
    """)[0][0]
    issue = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabWithdrawal Slip Item` i
        LEFT JOIN `tabWithdrawal Slip` w ON w.name=i.parent
        WHERE i.issue_qty<=0
          AND ((w.status='Stockroom Review' AND i.requested_qty>0)
            OR (w.status IN ('Fully Issued','Issued with Shortage')
                AND COALESCE(NULLIF(i.issued_qty,0),i.requested_qty)>0))
    """)[0][0]
    if int(personnel) != 0 or int(issue) != 0:
        stop("MAIN LEGACY BACKFILL ELIGIBILITY CHANGED; REVIEW BEFORE MIGRATION")
    print("MAIN LEGACY AUTOMATIC BACKFILL ELIGIBLE: ZERO")
    print("PHASE1 MAIN DATABASE PRECONDITIONS: PASS")
finally:
    if connected:
        frappe.destroy()
print("PHASE1 MAIN MIGRATION PRECHECK: PASS")
PY

# The marker and logfile live on the host, not in either application worktree.
# A failure or disconnect means investigate; never silently retry.
umask 077
dir="$HOME/ccpc-reviewed-scripts/migration-logs"
mkdir -p -m 700 "$dir"
marker="$dir/phase1-main-migrate-20261119.attempted"
log="$dir/phase1-main-migrate-20261119.log"
if [[ -e "$marker" || -e "$log" ]]; then
  echo "STOP: MAIN MIGRATION ALREADY ATTEMPTED OR LOG EXISTS; NO RETRY"
  exit 1
fi
( set -o noclobber; printf 'One-shot MAIN-only migration attempted; inspect private log before retry.\n' > "$marker" ) || {
  echo "STOP: MAIN ATTEMPT MARKER EXISTS"; exit 1;
}
( set -o noclobber; : > "$log" ) || {
  echo "STOP: CANNOT CREATE PRIVATE MIGRATION LOG"; exit 1;
}
chmod 600 "$marker" "$log"
echo "MAIN MIGRATION ATTEMPT MARKED: YES"
echo "MAIN MIGRATION STARTING: SITE-SCOPED DEVELOPMENT ONLY"
set +e
sudo docker exec --user frappe \
  --workdir /workspace/development/frappe-bench \
  --env FRAPPE_STREAM_LOGGING=1 \
  "$dev" bash -lc 'exec bench --site development.localhost migrate' \
  > "$log" 2>&1
result=$?
set -e
if [[ "$result" -ne 0 ]]; then
  echo "STOP: MAIN MIGRATION FAILED (EXIT CODE $result)"
  echo "PRIVATE MIGRATION LOG: $log"
  echo "NO RETRY / NO SOURCE-ONLY ROLLBACK / DO NOT START SERVICES"
  exit 1
fi
echo "MAIN MIGRATION COMMAND EXIT: 0"
echo "PRIVATE MIGRATION LOG: $log"
echo "MAIN MIGRATION COMMAND: PASS"
echo "POST-MIGRATION DATABASE VALIDATION: NOT YET PERFORMED"
echo "INTEGRATION2 RE-MIGRATION / SERVICES / PROD: NOT PERFORMED"
