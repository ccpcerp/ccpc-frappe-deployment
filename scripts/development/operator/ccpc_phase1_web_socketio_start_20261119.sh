#!/usr/bin/env bash
# One-shot Phase1 DEVELOPMENT-only web and Socket.IO startup.
# Excludes scheduler, worker, watch, Docker/Compose restart and all PROD.
# On any failure, inspect actual process state; never rerun blindly.
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
import importlib.util
import pwd
import re
import shlex
import socket
import subprocess

b = Path("/workspace/development/frappe-bench")
app = b / "apps/ccpcerp"
old = b / "apps/.ccpcerp-preserved-pr33-20261119-25a7b6be"
uid = pwd.getpwnam("frappe").pw_uid

def stop(msg):
    raise SystemExit("STOP: " + msg)

def git(p, *args):
    r = subprocess.run(["git", "-C", str(p), *args], capture_output=True, text=True, timeout=20)
    return r.stdout.strip() if r.returncode == 0 else None

if git(app, "rev-parse", "HEAD") != "55eb10b86a57de55a97e293a78228d9dd17b809a":
    stop("ACTIVE PHASE1 SOURCE HAS CHANGED")
if git(old, "rev-parse", "HEAD") != "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87":
    stop("PRESERVED PR33 SOURCE HAS CHANGED")
if git(old, "status", "--porcelain=v1", "--untracked-files=all") != "?? AGENTS.md":
    stop("OWNER-LOCAL AGENTS.MD NOT EXACTLY PRESERVED")
spec = importlib.util.find_spec("ccpcerp")
if spec is None or not spec.origin or Path(spec.origin).resolve() != (app / "ccpcerp/__init__.py").resolve():
    stop("PYTHON IMPORT SOURCE NOT PHASE1")

for site, name in (
    ("development.localhost", "development.localhost-20261118T233442Z-8db803832468"),
    ("ccpc-integration2.localhost", "ccpc-integration2.localhost-20261118T233442Z-8db803832468"),
):
    if not (b / "sites" / site / "site_config.json").is_file():
        stop("VALID DEV SITE CONFIG MISSING")
    if not (b / ".ccpc-pr32-snapshots" / name / "SHA256SUMS").is_file():
        stop("PROTECTED DEV BACKUP MANIFEST MISSING")

site_names = {p.parent.name for p in (b/"sites").glob("*/site_config.json")}
if site_names != {"development.localhost", "ccpc-integration2.localhost", "ccpc-integration.localhost"}:
    stop("UNEXPECTED DEV SITE CONFIG INVENTORY")

commands = {}
for line in (b / "Procfile").read_text().splitlines():
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    if ":" not in line:
        stop("INVALID DEV PROCFILE")
    label, command = line.split(":", 1)
    if label.strip() in commands:
        stop("DUPLICATED PROCFILE SERVICE")
    commands[label.strip()] = command.strip()
if set(commands) != {"web", "socketio", "watch", "schedule", "worker"}:
    stop("PROCFILE SERVICE LABELS CHANGED")
if shlex.split(commands["web"]) != ["bench", "serve", "--port", "8000"]:
    stop("WEB PROCFILE COMMAND CHANGED")
if shlex.split(commands["socketio"]) != ["bench", "socketio"]:
    stop("SOCKETIO PROCFILE COMMAND CHANGED")

active = 0
for p in Path("/proc").iterdir():
    if not p.name.isdecimal():
        continue
    try:
        stat = (p / "stat").read_text().rsplit(")", 1)[1].split()
        if stat[0] in ("Z", "X"):
            continue
        if int(stat[2]) in (543180, 546647) or int(stat[3]) in (543180, 546647):
            active += 1
            continue
        if p.stat().st_uid != uid:
            continue
        argv = " ".join(x.decode("utf-8", "replace") for x in (p/"cmdline").read_bytes().split(b"\0") if x)
        if re.search(
            r"(?:\bhoncho\s+start\b|\bbench\s+(?:serve|socketio|worker|schedule|start)\b|"
            r"frappe\.utils\.(?:scheduler|background_jobs)|rq\.worker|gunicorn|werkzeug)",
            argv, re.I
        ):
            active += 1
    except (OSError, ValueError, IndexError):
        pass
if active:
    stop("EXISTING DEV SERVICE PROCESS CANDIDATES: " + str(active))

for port in (8000, 9000):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            stop("EXISTING DEV PORT LISTENER")
    except (ConnectionRefusedError, TimeoutError, OSError):
        pass

if not Path("/home/frappe/.local/bin/honcho").is_file():
    stop("HONCHO BINARY MISSING")
if not (b / "logs").is_dir():
    stop("PRIVATE BENCH LOG DIRECTORY MISSING")
print("DEV WEB/SOCKETIO SOURCE, BACKUPS, PROCFILE AND STOPPED-SERVICE GUARDS: PASS")
print("DEV BROKEN THIRD SITE: EXCLUDED FROM SELECTED HONCHO SERVICES")
PY

for prior in \
  "$HOME/ccpc-reviewed-scripts/migration-logs/phase1-main-migrate-20261119.attempted" \
  "$HOME/ccpc-reviewed-scripts/migration-logs/phase1-integration2-migrate-20261119.attempted"; do
    if [[ ! -f "$prior" ]]; then
        echo "STOP: REQUIRED DEV SITE MIGRATION ATTEMPT MARKER ABSENT"; exit 1
    fi
done
echo "BOTH DEV SITE MIGRATION ATTEMPT MARKERS: PRESENT"

marker="$HOME/ccpc-reviewed-scripts/phase1-web-socketio-start-20261119.attempted"
log="$bench/logs/ccpc-phase1-web-socketio-20261119.log"
if [[ -e "$marker" ]]; then
    echo "STOP: WEB/SOCKETIO START PREVIOUSLY ATTEMPTED; NO RETRY"; exit 1
fi
# Reserve a private log without clobbering any previous attempt.
sudo docker exec --user frappe --workdir "$bench" "$dev" bash -lc \
  '( set -C; umask 077; : > logs/ccpc-phase1-web-socketio-20261119.log )' || {
      echo "STOP: CANNOT RESERVE UNIQUE BENCH LOG"; exit 1;
  }
( set -C; printf 'DEV Phase1 web/socketio launch attempted; inspect actual state before retry.\n' > "$marker" ) || {
    echo "STOP: CANNOT RESERVE UNIQUE HOST ATTEMPT MARKER"; exit 1;
}

# Launch only the two named services; NEVER 'honcho start' without arguments.
sudo docker exec -d --user frappe --workdir "$bench" "$dev" bash -lc \
  'umask 077; exec /home/frappe/.local/bin/honcho start web socketio >> logs/ccpc-phase1-web-socketio-20261119.log 2>&1'
echo "DEV WEB/SOCKETIO LAUNCH REQUESTED: EXACT TWO-SERVICE HONCHO"
echo "DEV SCHEDULER / WORKER / WATCH: NOT STARTED BY THIS SCRIPT"
echo "POST-START PROCESS/HTTP CHECK: STILL REQUIRED"
echo "PRODUCTION: NOT TOUCHED"
