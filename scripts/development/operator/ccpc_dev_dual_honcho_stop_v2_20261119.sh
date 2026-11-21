#!/usr/bin/env bash
# One-shot, fail-closed, DEVELOPMENT-only graceful Honcho shutdown.
# Corrected original Honcho identity: honcho start web socketio.
# The original v1 script must not be rerun.
# Existing site backups and protected code are never changed.
set -euo pipefail
if [[ "$(hostname -s)" != "ccpcerpserver" || "$(id -un)" != "gani" ]]; then
  echo 'STOP: WRONG HOST / OPERATOR'
  exit 1
fi

dev=frappe_docker_devcontainer-frappe-1
[[ "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" == true ]] || {
  echo 'STOP: NAMED DEV CONTAINER NOT RUNNING'; exit 1;
}
[[ "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" == frappe_docker_devcontainer ]] || {
  echo 'STOP: WRONG DOCKER COMPOSE PROJECT'; exit 1;
}

# The container already has the Frappe bench venv. No installer, external download,
# Docker restart, git pull, site migration or Redis cleanup is performed.
sudo docker exec -i --user frappe \
  --workdir /workspace/development/frappe-bench/sites \
  --env FRAPPE_STREAM_LOGGING=1 \
  "$dev" /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
from pathlib import Path
import os
import pwd
import re
import signal
import subprocess
import sys
import time

BENCH = Path('/workspace/development/frappe-bench')
LIVE = BENCH / 'apps/ccpcerp'
STAGE = BENCH / '.ccpc-phase1-release-stage-20261119-55eb10b86a57'
MAIN_PID, WORKER_PID = 543180, 546647
FRAPPE_UID = pwd.getpwnam('frappe').pw_uid
SITES = ('development.localhost', 'ccpc-integration2.localhost')


def stop(msg):
    raise SystemExit('STOP: ' + msg)


def git(path, *args):
    p = subprocess.run(['git', '-C', str(path), *args], capture_output=True, text=True, timeout=20)
    if p.returncode:
        stop('GIT VALIDATION FAILED')
    return p.stdout.strip()


def proc(pid):
    root = Path('/proc') / str(pid)
    try:
        argv = [v.decode('utf-8', 'replace') for v in (root / 'cmdline').read_bytes().split(b'\0') if v]
        stat = (root / 'stat').read_text().rsplit(')', 1)[1].split()
        state, ppid, pgid, sid = stat[0], int(stat[1]), int(stat[2]), int(stat[3])
        starttime = int(stat[19])
        uid = root.stat().st_uid
        cwd = os.readlink(root / 'cwd')
        return dict(argv=argv, state=state, ppid=ppid, pgid=pgid, sid=sid, starttime=starttime, uid=uid, cwd=cwd)
    except (OSError, ValueError, IndexError):
        return None


def honchos():
    result = []
    for entry in Path('/proc').iterdir():
        if entry.name.isdecimal():
            p = proc(int(entry.name))
            if p and len(p['argv']) >= 3 and Path(p['argv'][1]).name == 'honcho' and p['argv'][2] == 'start':
                result.append((int(entry.name), p))
    return sorted(result)


def assert_honcho(pid, role):
    p = proc(pid)
    if not p:
        stop(f'{role} PID MISSING / CHANGED')
    argv = p['argv']
    expected_tail = ['start', 'web', 'socketio'] if role == 'BENCH' else ['start', 'worker']
    if (len(argv) != len(expected_tail) + 2
        or Path(argv[1]).as_posix() != '/home/frappe/.local/bin/honcho'
        or argv[2:] != expected_tail
        or p['uid'] != FRAPPE_UID
        or p['ppid'] != 0 or p['pgid'] != pid or p['sid'] != pid
        or p['state'] == 'Z'
        or p['cwd'] != str(BENCH)):
        stop(f'{role} HONCHO IDENTITY/SESSION/CWD CHANGED')
    return p


def assert_only_expected_honchos(expected):
    actual = [pid for pid, _ in honchos()]
    if actual != sorted(expected):
        stop('UNEXPECTED HONCHO PROCESS COUNT OR IDENTITY')


def assert_rq_idle():
    # Only Redis worker metadata is read; no Frappe DB connection is created.
    import frappe
    from frappe.utils.background_jobs import get_workers
    frappe.init(site=SITES[0], sites_path='.')
    try:
        workers = get_workers()
        if len(workers) != 1:
            stop(f'REGISTERED WORKERS NOT EXACTLY ONE ({len(workers)})')
        worker = workers[0]
        status = worker.get_state()
        status = getattr(status, 'value', status)
        job = worker.get_current_job()
        if status != 'idle' or job is not None:
            stop('WORKER IS BUSY OR PROCESSING A JOB')
        print('RQ REGISTERED WORKER: ONE, IDLE, NO CURRENT JOB')
    finally:
        frappe.destroy()


def snapshot_descendants(pid):
    # Snapshot exact process births so a reused numeric PID is not mistaken for a lingerer.
    seen = {}
    while True:
        before = len(seen)
        for entry in Path('/proc').iterdir():
            if not entry.name.isdecimal():
                continue
            child_pid = int(entry.name)
            p = proc(child_pid)
            if p and (p['ppid'] == pid or p['ppid'] in seen):
                seen[child_pid] = p['starttime']
        if len(seen) == before:
            return seen


def alive_same_birth(pid, starttime=None):
    p = proc(pid)
    return bool(p and p['state'] not in ('Z', 'X') and (starttime is None or p['starttime'] == starttime))


def wait_for_full_exit(pid, children, max_seconds=45):
    for _ in range(max_seconds):
        if not alive_same_birth(pid) and all(not alive_same_birth(child, birth) for child, birth in children.items()):
            return True
        time.sleep(1)
    return False


# Fail-closed preconditions, before any signals.
if not (LIVE.is_dir() and STAGE.is_dir() and not LIVE.is_symlink() and not STAGE.is_symlink()):
    stop('SOURCE CHECKOUT DIRECTORY INVALID')
if git(LIVE, 'rev-parse', 'HEAD') != '25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87':
    stop('LIVE PR33 SHA CHANGED')
if git(LIVE, 'status', '--porcelain=v1', '--untracked-files=all') != '?? AGENTS.md':
    stop('LIVE PR33 WORKTREE CHANGED')
if git(STAGE, 'rev-parse', 'HEAD') != '55eb10b86a57de55a97e293a78228d9dd17b809a':
    stop('STAGED PHASE1 SHA CHANGED')
if git(STAGE, 'status', '--porcelain=v1', '--untracked-files=all'):
    stop('STAGED PHASE1 WORKTREE NOT CLEAN')
if not (LIVE / 'AGENTS.md').is_file():
    stop('PROTECTED LOCAL AGENTS.MD MISSING')
if len(re.findall(r'^worker:', (BENCH / 'Procfile').read_text(), re.M)) != 1:
    stop('EXPECTED PROCFILE WORKER SERVICE NOT FOUND')
for site, folder in (
    ('development.localhost', 'development.localhost-20261118T233442Z-8db803832468'),
    ('ccpc-integration2.localhost', 'ccpc-integration2.localhost-20261118T233442Z-8db803832468'),
):
    if not (BENCH / 'sites' / site / 'site_config.json').is_file():
        stop('PROTECTED SITE CONFIG MISSING')
    if not (BENCH / '.ccpc-pr32-snapshots' / folder / 'SHA256SUMS').is_file():
        stop('PROTECTED BACKUP MANIFEST MISSING')
assert_only_expected_honchos([MAIN_PID, WORKER_PID])
assert_honcho(MAIN_PID, 'BENCH')
assert_honcho(WORKER_PID, 'WORKER')
assert_rq_idle()
main_children = snapshot_descendants(MAIN_PID)
worker_children = snapshot_descendants(WORKER_PID)
if not main_children or not worker_children:
    stop('HONCHO DESCENDANT TOPOLOGY CHANGED')
print('DEV TWO HONCHO MANAGERS AND SOURCE/BACKUP GUARDS: PASS')

# Stop main bench manager first (web, socketio, watcher, scheduler, its worker),
# then the additional worker-only manager. No force-kill or group-wide kill.
os.kill(MAIN_PID, signal.SIGINT)
if not wait_for_full_exit(MAIN_PID, main_children):
    stop('BENCH HONCHO OR CHILD STILL RUNNING AFTER GRACE PERIOD; NO SECOND SIGNAL')
print('DEV BENCH HONCHO EXITED')
assert_only_expected_honchos([WORKER_PID])
assert_honcho(WORKER_PID, 'WORKER')
assert_rq_idle()
os.kill(WORKER_PID, signal.SIGINT)
if not wait_for_full_exit(WORKER_PID, worker_children):
    stop('WORKER HONCHO OR CHILD STILL RUNNING AFTER GRACE PERIOD; NO SECOND SIGNAL')
print('DEV WORKER-ONLY HONCHO EXITED')
assert_only_expected_honchos([])
print('DEV TWO-HONCHO GRACEFUL STOP: PASS')
print('SOURCE SWAP / SITE MIGRATION / PROD: NOT PERFORMED')
PY
