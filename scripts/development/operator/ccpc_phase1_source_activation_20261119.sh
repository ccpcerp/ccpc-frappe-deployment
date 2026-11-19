#!/usr/bin/env bash
# One-shot DEVELOPMENT-only, source-only Phase1 activation.
# No database migration, Frappe site write, service restart, or PRODUCTION access.
set -euo pipefail

if [[ "$(hostname -s)" != "ccpcerpserver" || "$(id -un)" != "gani" ]]; then
  echo "STOP: WRONG HOST OR OPERATOR"; exit 1
fi

dev=frappe_docker_devcontainer-frappe-1
if [[ "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" != true ]] ||
   [[ "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" != frappe_docker_devcontainer ]]; then
  echo "STOP: WRONG OR STOPPED DEVELOPMENT CONTAINER"; exit 1
fi

# Exact app directory must not be its own external Docker mount.
sudo docker inspect --format '{{json .Mounts}}' "$dev" | python3 -c '
import json,sys
items=json.load(sys.stdin)
target="/workspace/development/frappe-bench/apps/ccpcerp"
if any(str(m.get("Destination","")).rstrip("/") == target for m in items):
    sys.exit("STOP: APPLICATION DIRECTORY IS A SEPARATE BIND MOUNT")
print("DEV APPLICATION SEPARATE DOCKER MOUNT: NO")
'

# The original application checkout, its untracked AGENTS.md, both sites,
# and both backup manifests must be protected. The old directory is renamed,
# NEVER deleted/overwritten or reset.
sudo docker exec -i --user frappe \
  --workdir /workspace/development/frappe-bench/sites \
  --env FRAPPE_STREAM_LOGGING=1 \
  "$dev" /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
from pathlib import Path
import importlib.util
import os
import pwd
import re
import subprocess
import sys

B = Path("/workspace/development/frappe-bench")
APP = B / "apps/ccpcerp"
STAGE = B / ".ccpc-phase1-release-stage-20261119-55eb10b86a57"
PRESERVE = B / "apps/.ccpcerp-preserved-pr33-20261119-25a7b6be"
OLD = "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
NEW = "55eb10b86a57de55a97e293a78228d9dd17b809a"
FRAPPE_UID = pwd.getpwnam("frappe").pw_uid

def stop(reason):
    raise SystemExit("STOP: " + reason)

def git(path, *args):
    p = subprocess.run(
        ["git", "-C", str(path), *args],
        capture_output=True, text=True, timeout=25,
    )
    if p.returncode:
        stop("GIT REPOSITORY VALIDATION FAILED")
    return p.stdout.strip()

def proc(pid):
    root = Path("/proc") / str(pid)
    try:
        stat = (root / "stat").read_text().rsplit(")", 1)[1].split()
        argv = [t.decode("utf-8", "replace") for t in (root / "cmdline").read_bytes().split(b"\0") if t]
        return {
            "pid": pid, "uid": root.stat().st_uid,
            "state": stat[0], "pgid": int(stat[2]),
            "sid": int(stat[3]), "argv": argv,
        }
    except (OSError, ValueError, IndexError):
        return None

def ensure_services_stopped():
    # Most importantly, original Honcho sessions and their descendants must be gone.
    # Also detect other Frappe-owned dev service processes not in the known sessions.
    active = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdecimal():
            continue
        p = proc(int(entry.name))
        if not p or p["state"] in ("Z", "X"):
            continue
        if p["pgid"] in (543180, 546647) or p["sid"] in (543180, 546647):
            active.append("OLD SESSION")
            continue
        if p["uid"] != FRAPPE_UID:
            continue
        argv = " ".join(p["argv"])
        if re.search(
            r"(?:\bhoncho\s+start\b|\bbench\s+(?:start|worker|schedule)\b|"
            r"frappe\.utils\.(?:background_jobs|scheduler)|"
            r"rq\.worker|socketio\.js|gunicorn|werkzeug|redis_queue)",
            argv, re.I,
        ):
            active.append("SERVICE CANDIDATE")
    if active:
        stop(f"DEVELOPMENT SERVICE PROCESS STILL RUNNING ({len(active)} CANDIDATES)")
    print("DEV ORIGINAL HONCHO SESSIONS AND SERVICE CANDIDATES: CLEAR")

def ensure_import_points_to_app():
    spec = importlib.util.find_spec("ccpcerp")
    expected = APP / "ccpcerp" / "__init__.py"
    if spec is None or not spec.origin or Path(spec.origin).resolve() != expected.resolve():
        stop("APP PYTHON IMPORT ORIGIN DOES NOT MATCH LIVE DIRECTORY")

ensure_services_stopped()

if not (
    APP.is_dir() and STAGE.is_dir()
    and not APP.is_symlink() and not STAGE.is_symlink()
    and not PRESERVE.exists() and not PRESERVE.is_symlink()
):
    stop("SOURCE DIRECTORIES OR UNIQUE PRESERVATION TARGET CHANGED")
if not STAGE.joinpath(".git").is_dir():
    stop("STAGE IS NOT A SEPARATE GIT CHECKOUT")
if not (APP / "AGENTS.md").is_file() or (APP / "AGENTS.md").is_symlink():
    stop("OWNER PROTECTED UNTRACKED AGENTS.MD MISSING")
if not (STAGE / "AGENTS.md").is_file():
    stop("RELEASE TRACKED AGENTS.MD MISSING")
if git(APP, "rev-parse", "HEAD") != OLD:
    stop("ORIGINAL PR33 SHA CHANGED")
if git(APP, "status", "--porcelain=v1", "--untracked-files=all") != "?? AGENTS.md":
    stop("ORIGINAL PR33 WORKTREE CHANGED")
if git(STAGE, "rev-parse", "HEAD") != NEW:
    stop("RELEASE SOURCE SHA CHANGED")
if git(STAGE, "status", "--porcelain=v1", "--untracked-files=all"):
    stop("RELEASE SOURCE WORKTREE CHANGED")
if not git(STAGE, "ls-tree", "-r", "--name-only", "HEAD", "--", "AGENTS.md") == "AGENTS.md":
    stop("RELEASE AGENTS.MD IS NOT TRACKED")
if len({B.stat().st_dev, APP.stat().st_dev, STAGE.stat().st_dev, (B/"apps").stat().st_dev}) != 1:
    stop("APP AND STAGE ARE NOT ON SAME FILESYSTEM")
for site, snap in (
    ("development.localhost", "development.localhost-20261118T233442Z-8db803832468"),
    ("ccpc-integration2.localhost", "ccpc-integration2.localhost-20261118T233442Z-8db803832468"),
):
    if not (B/"sites"/site/"site_config.json").is_file():
        stop("INTENDED SITE CONFIG MISSING")
    if not (B/".ccpc-pr32-snapshots"/snap/"SHA256SUMS").is_file():
        stop("PROTECTED BACKUP MANIFEST MISSING")

ensure_import_points_to_app()
print("PHASE1 SOURCE SWITCH PRECHECK: PASS")

# No migrations have run: a failed filesystem activation may be reversed safely
# only while precise directory identities and target absence remain verifiable.
phase = 0
try:
    os.rename(APP, PRESERVE)
    phase = 1
    os.rename(STAGE, APP)
    phase = 2

    if git(APP, "rev-parse", "HEAD") != NEW:
        raise RuntimeError("POST-SWAP RELEASE SHA MISMATCH")
    if git(PRESERVE, "rev-parse", "HEAD") != OLD:
        raise RuntimeError("POST-SWAP PRESERVED SHA MISMATCH")
    if git(PRESERVE, "status", "--porcelain=v1", "--untracked-files=all") != "?? AGENTS.md":
        raise RuntimeError("PRESERVED PR33 / AGENTS STATUS CHANGED")
    if git(APP, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("POST-SWAP RELEASE WORKTREE NOT CLEAN")
    ensure_import_points_to_app()
except BaseException as exc:
    # Catch preflight helper SystemExit/KeyboardInterrupt too, so post-rename
    # verification cannot leave the original checkout moved without a rollback.
    # Do not operate on unknown paths. Exact git identity is checked before reversal.
    print("STOP: SOURCE ACTIVATION FAILED; ATTEMPTING GUARDED PRE-MIGRATION ROLLBACK")
    try:
        if phase == 1:
            if APP.exists() or git(PRESERVE, "rev-parse", "HEAD") != OLD:
                raise RuntimeError("UNSAFE TO RESTORE ORIGINAL APP")
            os.rename(PRESERVE, APP)
        elif phase == 2:
            if STAGE.exists() or git(APP, "rev-parse", "HEAD") != NEW or git(PRESERVE, "rev-parse", "HEAD") != OLD:
                raise RuntimeError("UNSAFE TO REVERSE TWO DIRECTORY RENAMES")
            os.rename(APP, STAGE)
            os.rename(PRESERVE, APP)
        print("PRE-MIGRATION ORIGINAL SOURCE RESTORED; NO MIGRATION PERFORMED")
    except Exception:
        print("STOP: AUTOMATIC SOURCE RESTORATION NOT VERIFIED; DO NOT START SERVICES OR MIGRATE")
    raise SystemExit("STOP: PHASE1 SOURCE ACTIVATION NOT ACCEPTED") from exc

print("PHASE1 ACTIVE APP RELEASE SHA:", NEW)
print("ORIGINAL PR33 CHECKOUT AND LOCAL AGENTS.MD: PRESERVED IN PROTECTED SIBLING")
print("PHASE1 SOURCE ACTIVATION: PASS")
print("SITE MIGRATION / SERVICES / PROD: NOT PERFORMED")
PY
