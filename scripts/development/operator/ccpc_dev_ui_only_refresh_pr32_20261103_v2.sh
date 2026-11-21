#!/usr/bin/env bash
# One-shot, owner-approved CCPC DEVELOPMENT UI-only refresh (v2: tokenized Procfile check).
# Exact DEV container only. No bench migrate, Docker restart, DB writes,
# scheduler/worker/watch start, PRODUCTION operations, or automatic retry.
set -euo pipefail

CONT='frappe_docker_devcontainer-frappe-1'
BENCH='/workspace/development/frappe-bench'
PYTHON="$BENCH/env/bin/python"

if [ "$(id -un)" != 'gani' ]; then
  echo 'STOP: run as the normal Ubuntu operator gani'; exit 1
fi

echo '=== ONE-TIME DEVELOPMENT UI REFRESH PREFLIGHT ==='
docker exec -i --user frappe "$CONT" "$PYTHON" - <<'PRECHECK'
import json, os, pwd, re, shlex, signal, socket, subprocess, time, urllib.request
from pathlib import Path

BENCH = Path('/workspace/development/frappe-bench')
APP = BENCH / 'apps/ccpcerp'
SITES = BENCH / 'sites'
OLD_ROOT = 537388
TARGET = 'e1d67f2716d15e8ffdf42f0547c44d8324516d7e'
MARKER = Path('/home/frappe/.ccpc-dev-ui-refresh-pr32-20261103.started')
EXPECTED_PROC = {
    'web': 'bench serve --port 8000',
    'socketio': 'bench socketio',
}
SITES_TO_TEST = ('development.localhost', 'ccpc-integration2.localhost')


def stop(message):
    raise SystemExit('STOP BEFORE/AT UI REFRESH: ' + message)


def run_git(*args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    return subprocess.check_output(['git', '-C', str(APP), *args], env=env, text=True).strip()


def ps_rows():
    raw = subprocess.check_output(['ps', '-eo', 'pid=,ppid=,args='], text=True)
    rows = {}
    for line in raw.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) != 3:
            continue
        try:
            rows[int(parts[0])] = (int(parts[1]), parts[2].lower())
        except ValueError:
            continue
    return rows


def descendants(rows, root):
    group = {root}
    while True:
        more = {pid for pid, (ppid, _) in rows.items() if ppid in group}
        if more <= group:
            return group
        group |= more


def port_up(port):
    with socket.socket() as s:
        s.settimeout(1)
        return s.connect_ex(('127.0.0.1', port)) == 0


def ping(site):
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/method/ping',
        headers={'Host': site, 'X-Frappe-Site-Name': site},
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=8) as resp:
        return resp.status == 200 and json.loads(resp.read(1024)).get('message') == 'pong'

if os.getuid() != pwd.getpwnam('frappe').pw_uid:
    stop('wrong container identity')
if MARKER.exists() or MARKER.is_symlink():
    stop('one-shot marker already exists; do not replay')
if run_git('rev-parse', '--show-toplevel') != str(APP):
    stop('wrong DEVELOPMENT app checkout')
if run_git('rev-parse', 'HEAD') != TARGET:
    stop('unapproved app source SHA')
if subprocess.run(['git', '-C', str(APP), 'symbolic-ref', '-q', 'HEAD'], stdout=subprocess.DEVNULL).returncode == 0:
    stop('checkout no longer detached')
if run_git('status', '--porcelain=v1', '--untracked-files=all') != '?? AGENTS.md':
    stop('tracked changes or unexpected untracked files')
if not (APP / 'AGENTS.md').is_file() or (APP / 'AGENTS.md').is_symlink():
    stop('protected AGENTS.md missing or unsafe')
proc_lines = (BENCH / 'Procfile').read_text().splitlines()
proc = {}
for line in proc_lines:
    if ':' in line and not line.lstrip().startswith('#'):
        label, command = line.split(':', 1)
        proc[label.strip()] = command.strip()
if set(proc) != {'web', 'socketio', 'watch', 'schedule', 'worker'}:
    stop('Procfile set changed')
# Compare shell tokens, not raw spacing/quotation. The exact approved argv
# remains ["bench","serve","--port","8000"] and ["bench","socketio"].
# All other flags/commands fail closed.
try:
    live_argv = {label: shlex.split(proc.get(label, '')) for label in EXPECTED_PROC}
except ValueError:
    stop('cannot parse web/socketio Procfile command')
expected_argv = {label: shlex.split(command) for label, command in EXPECTED_PROC.items()}
if live_argv != expected_argv:
    stop('approved web/socketio Procfile command tokens changed')
configs = [json.loads((SITES / site / 'site_config.json').read_text()) for site in SITES_TO_TEST]
if not configs[0].get('db_name') or not configs[1].get('db_name') or configs[0]['db_name'] == configs[1]['db_name']:
    stop('two intended DEVELOPMENT site identities not isolated')
if not (SITES / 'ccpc-integration.localhost').is_dir():
    stop('legacy site inventory unexpectedly changed; review required')

rows = ps_rows()
if OLD_ROOT not in rows:
    stop('original UI-only Honcho manager PID changed')
ppid, old_cmd = rows[OLD_ROOT]
if ppid != 0 or 'honcho' not in old_cmd or 'start web socketio' not in old_cmd:
    stop('original Honcho manager identity is ambiguous')
if Path(f'/proc/{OLD_ROOT}').stat().st_uid != os.getuid():
    stop('original Honcho manager is owned by another user')
start_ticks = Path(f'/proc/{OLD_ROOT}/stat').read_text().rsplit(') ', 1)[-1].split()[19]
family = descendants(rows, OLD_ROOT)
if not {537435, 537438, 537440} <= family:
    stop('known web/socketio processes no longer belong to approved Honcho tree')
for pid in family:
    if Path(f'/proc/{pid}').exists() and Path(f'/proc/{pid}').stat().st_uid != os.getuid():
        stop('Honcho descendant owned by unexpected user')
for pid, (_, cmd) in rows.items():
    if re.search(r'\bbench\s+(schedule|worker|watch)\b|\brq\s+worker\b|frappe\.utils\.scheduler|\byarn\s+watch\b', cmd):
        stop('active background scheduler/worker/watch candidate detected')
    if pid not in family and ('honcho start' in cmd or 'bench serve' in cmd or 'bench socketio' in cmd):
        stop('another live Honcho/web/socketio process may be present')
if not port_up(8000) or not port_up(9000):
    stop('expected two UI listener ports not both active')
try:
    for site in SITES_TO_TEST:
        if not ping(site):
            stop('pre-refresh HTTP ping failed for ' + site)
except Exception:
    stop('pre-refresh two-site HTTP ping failed')

# Recheck the exact PID and start time immediately before the single graceful signal.
if OLD_ROOT not in ps_rows() or Path(f'/proc/{OLD_ROOT}/stat').read_text().rsplit(') ', 1)[-1].split()[19] != start_ticks:
    stop('Honcho PID was reused or changed during preflight')
fd = os.open(MARKER, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as fp:
    fp.write('One-shot UI-only refresh attempt\n')
    fp.write('OLD_ROOT=' + str(OLD_ROOT) + '\nTARGET=' + TARGET + '\n')
print('PREFLIGHT PASS: DEV source, Procfile, two sites, original UI-only Honcho and ports')
print('SENDING ONE GRACEFUL SIGTERM TO VERIFIED DEVELOPMENT HONCHO MANAGER ONLY')
os.kill(OLD_ROOT, signal.SIGTERM)

def live(pid):
    st = Path(f'/proc/{pid}/stat')
    if not st.exists():
        return False
    try:
        return st.read_text().rsplit(') ', 1)[-1].split()[0] != 'Z'
    except FileNotFoundError:
        return False

for _ in range(20):
    if not any(live(pid) for pid in family) and not port_up(8000) and not port_up(9000):
        print('OLD UI-ONLY HONCHO FAMILY STOPPED GRACEFULLY; BOTH UI PORTS QUIESCENT')
        break
    time.sleep(1)
else:
    stop('graceful shutdown incomplete; no forced kill or automatic retry; inspect before launch')
PRECHECK

echo '=== STARTING ONLY DEVELOPMENT WEB AND SOCKETIO ==='
# docker exec -d is the exact Ubuntu->DEV-container launch pattern previously used.
# The private log filename is exclusive; stdout/stderr never enter chat or GitHub.
docker exec -d --user frappe "$CONT" bash -lc '
set -euo pipefail
umask 077
cd /workspace/development/frappe-bench
LOG="$HOME/ccpc-dev-ui-refresh-pr32-20261103.log"
if [ -e "$LOG" ] || [ -L "$LOG" ]; then exit 45; fi
set -C
exec /home/frappe/.local/bin/honcho start web socketio >"$LOG" 2>&1
'

echo '=== POST-REFRESH DEVELOPMENT TWO-SITE HTTP CHECK ==='
docker exec -i --user frappe "$CONT" "$PYTHON" - <<'VERIFY'
import json, os, re, socket, subprocess, time, urllib.request
from pathlib import Path
TARGET='e1d67f2716d15e8ffdf42f0547c44d8324516d7e'
APP=Path('/workspace/development/frappe-bench/apps/ccpcerp')
SITES=('development.localhost','ccpc-integration2.localhost')

def rows():
    raw=subprocess.check_output(['ps','-eo','pid=,ppid=,args='],text=True)
    out=[]
    for line in raw.splitlines():
        fields=line.strip().split(None,2)
        if len(fields)==3:
            try: out.append((int(fields[0]),int(fields[1]),fields[2].lower()))
            except ValueError: pass
    return out

def port_up(n):
    with socket.socket() as s:
        s.settimeout(1)
        return s.connect_ex(('127.0.0.1',n))==0

def ping(site):
    req=urllib.request.Request('http://127.0.0.1:8000/api/method/ping',headers={'Host':site,'X-Frappe-Site-Name':site})
    client=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with client.open(req,timeout=8) as reply:
        return reply.status==200 and json.loads(reply.read(1024)).get('message')=='pong'

if subprocess.check_output(['git','-C',str(APP),'rev-parse','HEAD'],text=True).strip()!=TARGET:
    raise SystemExit('STOP: DEVELOPMENT source SHA changed after UI start')
if subprocess.check_output(['git','-C',str(APP),'status','--porcelain=v1','--untracked-files=all'],text=True).strip()!='?? AGENTS.md':
    raise SystemExit('STOP: DEVELOPMENT working tree unexpected after UI start')
if not Path('/home/frappe/.ccpc-dev-ui-refresh-pr32-20261103.started').is_file():
    raise SystemExit('STOP: one-shot audit marker absent')
for _ in range(30):
    processes=rows()
    managers=[pid for pid,ppid,cmd in processes if 'honcho' in cmd and 'start web socketio' in cmd and pid!=537388]
    forbidden=[pid for pid,ppid,cmd in processes if re.search(r'\bbench\s+(schedule|worker|watch)\b|\brq\s+worker\b|frappe\.utils\.scheduler|\byarn\s+watch\b',cmd)]
    if forbidden:
        raise SystemExit('STOP: unexpected background worker/scheduler/watch process detected')
    if len(managers)==1 and port_up(8000) and port_up(9000):
        try:
            if all(ping(site) for site in SITES):
                print('DEVELOPMENT UI REFRESH: PASS')
                print('NEW UI-ONLY HONCHO MANAGER: VERIFIED')
                for site in SITES:
                    print('HTTP PING PASS: '+site+' (200, pong)')
                print('DEVELOPMENT SOURCE: '+TARGET)
                print('PRESERVED: detached Git source; only untracked AGENTS.md')
                print('NOT RUN: migrate, scheduler, worker, watch, database writes, PRODUCTION')
                raise SystemExit(0)
        except Exception:
            pass
    time.sleep(1)
raise SystemExit('STOP: new DEV UI runtime not verified; do not auto-retry. Inspect private log safely.')
VERIFY
