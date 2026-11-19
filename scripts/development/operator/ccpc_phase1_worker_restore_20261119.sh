#!/usr/bin/env bash
# One-shot DEVELOPMENT-only Phase1 worker restoration after live two-site
# website indexing jobs were identified. No scheduler/watch/PROD action.
# A worker will WRITE website search indexes when processing queued jobs.
# Never retry an interrupted/failed launch without examining actual state.
set -euo pipefail

if [[ "$(hostname -s)" != "ccpcerpserver" || "$(id -un)" != "gani" ]]; then
  echo "STOP: WRONG HOST OR OPERATOR"; exit 1
fi
umask 077
dev=frappe_docker_devcontainer-frappe-1
bench=/workspace/development/frappe-bench

if [[ "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" != true ]] ||
   [[ "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" != frappe_docker_devcontainer ]]; then
  echo "STOP: WRONG OR STOPPED DEVELOPMENT CONTAINER"; exit 1
fi

sudo docker exec -i --user frappe --workdir "$bench/sites" \
  --env FRAPPE_STREAM_LOGGING=1 \
  "$dev" "$bench/env/bin/python" -B - <<'PY'
from pathlib import Path
import hashlib
import importlib.util
import pwd
import re
import shlex
import subprocess

B = Path("/workspace/development/frappe-bench")
APP = B / "apps/ccpcerp"
OLD = B / "apps/.ccpcerp-preserved-pr33-20261119-25a7b6be"
UID = pwd.getpwnam("frappe").pw_uid

def stop(why):
    raise SystemExit("STOP: " + why)

def git(path, *args):
    p = subprocess.run(["git", "-C", str(path), *args],
                       capture_output=True, text=True, timeout=20)
    return p.stdout.strip() if p.returncode == 0 else None

if git(APP, "rev-parse", "HEAD") != "55eb10b86a57de55a97e293a78228d9dd17b809a":
    stop("ACTIVE RELEASE SHA CHANGED")
if git(OLD, "rev-parse", "HEAD") != "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87":
    stop("PROTECTED ORIGINAL SHA CHANGED")
if git(OLD, "status", "--porcelain=v1", "--untracked-files=all") != "?? AGENTS.md":
    stop("PROTECTED ORIGINAL AGENTS/WORKTREE CHANGED")
if not (OLD / "AGENTS.md").is_file():
    stop("PROTECTED AGENTS.MD NOT FOUND")
spec = importlib.util.find_spec("ccpcerp")
if not spec or not spec.origin or Path(spec.origin).resolve() != (APP / "ccpcerp/__init__.py").resolve():
    stop("CCPC PYTHON IMPORT SOURCE CHANGED")

for site, snapshot in (
    ("development.localhost", "development.localhost-20261118T233442Z-8db803832468"),
    ("ccpc-integration2.localhost", "ccpc-integration2.localhost-20261118T233442Z-8db803832468"),
):
    if not (B / "sites" / site / "site_config.json").is_file():
        stop("VALID DEV SITE CONFIG MISSING")
    if not (B / ".ccpc-pr32-snapshots" / snapshot / "SHA256SUMS").is_file():
        stop("PROTECTED TWO-SITE BACKUP MANIFEST MISSING")
sites = {p.parent.name for p in (B / "sites").glob("*/site_config.json")}
if sites != {"development.localhost", "ccpc-integration2.localhost", "ccpc-integration.localhost"}:
    stop("BENCH SITE INVENTORY CHANGED")

commands = {}
for line in (B / "Procfile").read_text().splitlines():
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    if ":" not in line:
        stop("PROCFILE INVALID")
    label, cmd = line.split(":", 1)
    if label.strip() in commands:
        stop("DUPLICATE PROCFILE LABEL")
    commands[label.strip()] = cmd.strip()
if set(commands) != {"web", "socketio", "watch", "schedule", "worker"}:
    stop("PROCFILE SERVICE LABELS CHANGED")
if shlex.split(commands["web"]) != ["bench", "serve", "--port", "8000"]:
    stop("PROCFILE WEB COMMAND CHANGED")
if shlex.split(commands["socketio"]) != ["bench", "socketio"]:
    stop("PROCFILE SOCKETIO COMMAND CHANGED")
if commands["worker"] != "bench worker 1>> logs/worker.log 2>> logs/worker.error.log":
    stop("PROCFILE WORKER COMMAND CHANGED")
if not Path("/home/frappe/.local/bin/honcho").is_file() or not (B / "logs").is_dir():
    stop("HONCHO BINARY OR BENCH LOG DIRECTORY MISSING")

honchos = []
worker_candidates = 0
scheduler_candidates = 0
for p in Path("/proc").iterdir():
    if not p.name.isdecimal():
        continue
    try:
        if p.stat().st_uid != UID:
            continue
        state = (p / "stat").read_text().rsplit(")", 1)[1].split()[0]
        if state in ("Z", "X"):
            continue
        args = [x.decode("utf-8", "replace")
                for x in (p / "cmdline").read_bytes().split(b"\0") if x]
    except (OSError, ValueError, IndexError):
        continue
    for i, token in enumerate(args):
        if Path(token).name == "honcho" and args[i + 1:i + 2] == ["start"]:
            honchos.append(args[i + 2:])
            break
    joined = " ".join(args)
    if re.search(r"\bbench\s+worker\b|\brq\s+worker\b|rq\.worker|frappe\.utils\.background_jobs", joined):
        worker_candidates += 1
    if re.search(r"\bbench\s+schedule\b|frappe\.utils\.scheduler", joined):
        scheduler_candidates += 1
if honchos != [["web", "socketio"]]:
    stop("EXACT WEB/SOCKETIO HONCHO MANAGER NO LONGER PRESENT")
if worker_candidates or scheduler_candidates:
    stop("WORKER OR SCHEDULER ALREADY HAS LIVE PROCESS CANDIDATES")
print("EXISTING DEV WEB/SOCKETIO AND NO WORKER/SCHEDULER GUARD: PASS")

# Pure queue metadata inspection. DO NOT connect to SQL or run a job.
import frappe
from frappe.utils.background_jobs import get_queue, get_queue_list, get_workers

expected = {
    "7c7b578365dd": "development.localhost",
    "2460aabaac65": "ccpc-integration2.localhost",
}
frappe_started = False
try:
    frappe.init(site="development.localhost", sites_path=".")
    frappe_started = True
    if len(get_workers()) != 0:
        stop("RQ WORKER REGISTRY NO LONGER EMPTY")

    found = {}
    for queue_name in get_queue_list():
        queue = get_queue(queue_name)
        count = queue.count
        if count > 25:
            stop("UNEXPECTED QUEUE BACKLOG")
        jobs = queue.jobs
        if len(jobs) != count or queue.count != count:
            stop("QUEUE CHANGED DURING INSPECTION")
        for job in jobs:
            fingerprint = hashlib.sha256(str(job.id).encode()).hexdigest()[:12]
            if fingerprint not in expected or fingerprint in found:
                stop("QUEUED JOB SET CHANGED")
            if str(queue_name) != "long":
                stop("UNEXPECTED NON-LONG QUEUE JOB")
            kwargs = job.kwargs
            if not isinstance(kwargs, dict) or kwargs.get("site") != expected[fingerprint]:
                stop("JOB SITE NOT APPROVED OR CHANGED")
            method = kwargs.get("method")
            if not callable(method):
                stop("JOB METHOD NO LONGER CALLABLE")
            module = getattr(method, "__module__", None)
            qualname = getattr(method, "__qualname__", None)
            if (module, qualname) != ("frappe.search.website_search", "build_index_for_all_routes"):
                stop("JOB METHOD NO LONGER APPROVED WEBSITE INDEX BUILDER")
            if job.func_name != "frappe.utils.background_jobs.execute_job":
                stop("JOB EXECUTOR CHANGED")
            found[fingerprint] = expected[fingerprint]
    if found != expected:
        stop("QUEUED WEBSITE INDEX JOBS CHANGED")
    print("EXACT TWO APPROVED DEV LONG WEBSITE INDEX JOBS: PASS")
    print("RQ REGISTERED WORKERS: ZERO")
finally:
    if frappe_started:
        frappe.destroy()

print("PHASE1 ONE-WORKER RESTORATION PRECHECK: PASS")
PY

# Do not interpret a site migration attempt marker as evidence of later success.
# Both site post-migration checks and web HTTP were independently owner-reported PASS.
for required in \
  "$HOME/ccpc-reviewed-scripts/migration-logs/phase1-main-migrate-20261119.attempted" \
  "$HOME/ccpc-reviewed-scripts/migration-logs/phase1-integration2-migrate-20261119.attempted" \
  "$HOME/ccpc-reviewed-scripts/phase1-web-socketio-start-20261119.attempted"; do
  if [[ ! -f "$required" ]]; then
    echo "STOP: REQUIRED PREVIOUS DEV OPERATION MARKER NOT FOUND"; exit 1
  fi
done

marker="$HOME/ccpc-reviewed-scripts/phase1-worker-restore-20261119.attempted"
if [[ -e "$marker" ]]; then
  echo "STOP: WORKER RESTORATION ALREADY ATTEMPTED; NO RETRY"; exit 1
fi
# Reserve bench log and host attempt marker without clobbering previous run.
sudo docker exec --user frappe --workdir "$bench" "$dev" bash -lc \
  '( set -C; umask 077; : > logs/ccpc-phase1-worker-20261119.log )' || {
    echo "STOP: PRIVATE DEV WORKER LOG ALREADY EXISTS OR CANNOT BE RESERVED"; exit 1;
  }
( set -C; printf 'DEV worker launch attempted; inspect processes, queue and log before retry.\n' > "$marker" ) || {
  echo "STOP: DEV WORKER ATTEMPT MARKER ALREADY EXISTS"; exit 1;
}

echo "PHASE1 WORKER RESTORATION ATTEMPT MARKED: YES"
echo "STARTING ONE DEV WORKER HONCHO: NO SCHEDULER"
sudo docker exec -d --user frappe --workdir "$bench" "$dev" bash -lc \
  'umask 077; exec /home/frappe/.local/bin/honcho start worker >> logs/ccpc-phase1-worker-20261119.log 2>&1'

echo "ONE DEVELOPMENT WORKER LAUNCH REQUESTED"
echo "QUEUED JOBS MAY NOW EXECUTE: TWO DEV WEBSITE SEARCH INDEX BUILDS"
echo "SCHEDULER / WATCH / PROD: NOT STARTED BY THIS SCRIPT"
echo "POST-START RQ/QUEUE/HTTP VALIDATION: NOT YET PERFORMED"
