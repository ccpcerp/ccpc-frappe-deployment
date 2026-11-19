# Phase 1 — approved shared-bench DEVELOPMENT integration and recovery-controlled cutover

**Prepared:** 2026-11-19, Asia/Manila. **Status:** DEV-only integration approved by owner; *pre-cutover read-only discovery is next, code switch and migration have NOT been performed*. This is an operator-reviewed, one-gate-at-a-time workflow; do not combine gates into a blind script.

## Authorized scope and source authority

The owner approved continuing the actual **DEVELOPMENT-only maintenance and Phase 1 integration** after the two-site local+Synology backups and isolated SQL+file restores passed. This permits controlled DEV-only planning, staging and a planned maintenance window, but **does not authorize** accessing, changing or stopping either PRODUCTION environment. Live site migrations and wide after-migrate hooks are risk-bearing and must pass the new pre-cutover and recovery gates before execution. A host-side operator is needed; ChatGPT cannot run commands directly on `ccpcerpserver`.

**Latest GitHub verified source at preparation:**
- Release: `ccpcerp/ccpcerp` `release/withdrawal-department-phase1-2026-11-17` exact commit **`55eb10b86a57de55a97e293a78228d9dd17b809a`** (PR #38 and #39 merged).
- Original, separately preserved PR33 branch: `review/billing-authorization-correction-2026-11-03` exact **`25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`**.
- Divergence at this checkpoint: Phase1 release 18 release-only vs PR33 44 PR33-only commits. **Never merge full PR33 into Phase 1.**
- Existing DEV bench `/workspace/development/frappe-bench`, app dir `apps/ccpcerp`, known detached PR33 commit above and exactly untracked protected `?? AGENTS.md`. The released Phase1 tree **tracks** root `AGENTS.md`. Never force-checkout, `git reset --hard`, `git clean`, blind `git pull`, delete or overwrite the owner's local `AGENTS.md`.
- `ccpcerp/patches.txt` matches between the branches, but release `hooks.py` and `setup.after_migrate()` differ. Release `before_migrate` bootstraps executive and Finance mapping role definitions; `after_migrate` runs existing foundation, personnel, MRS/PO, permission/workflow, stock-field and withdrawal-quantity backfill operations. Page `ccpc-phase1-finance` and its roles require sync. This is **not** a Page-only migration; review patch log, company/account masters and record-side effects per site.
- Phase 1 **same-Company-only** issuance and **intercompany billing disabled** must stay enforced; PR33's active billing maker/checker/invoice flow remains unreleased.
- Both valid sites `development.localhost` (MAIN) and `ccpc-integration2.localhost` share this installed app's Python import path, verified in the live owner probe. The broken `ccpc-integration.localhost` exists and must **not** be connected, migrated or swept by `--site all` or unrestricted schedulers.

## Gate A: exact current *read-only* pre-cutover inventory — execute now

The first operator step is intentionally non-mutating: it discovers whether the exact release commit already exists as a local Git object, what fetch transport is configured, and the current Honcho process identity. It also verifies the three protected backup snapshot directories, the valid sites and the detached live PR33 checkout. It does not fetch code, stop processes, touch Frappe/SQL, invoke a site import, read secrets, or run migration.

Run at `gani@ccpcerpserver`:

```bash
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver || { echo "STOP: WRONG HOST"; exit 1; }
test "$(id -un)" = gani || { echo "STOP: WRONG OPERATOR"; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo "STOP: DEV CONTAINER NOT RUNNING"; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || { echo "STOP: WRONG COMPOSE PROJECT"; exit 1; }
test "$(findmnt -rn -M /mnt/erpnext_backups -o SOURCE,FSTYPE)" = "//192.168.50.132/erpnext_backups cifs" || { echo "STOP: NAS MOUNT CHANGED"; exit 1; }
nas=/mnt/erpnext_backups/ccpc-development-phase1-two-site-preswitch-20261118T233444Z-35c00130d53b457e
test -f "$nas/development.localhost-20261118T233442Z-8db803832468/SHA256SUMS" || { echo "STOP: MAIN NAS SNAPSHOT MISSING"; exit 1; }
test -f "$nas/ccpc-integration2.localhost-20261118T233442Z-8db803832468/SHA256SUMS" || { echo "STOP: INTEGRATION2 NAS SNAPSHOT MISSING"; exit 1; }
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev" /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
from pathlib import Path
import importlib.util
import subprocess

B = Path("/workspace/development/frappe-bench")
A = B / "apps/ccpcerp"
OLD = "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
NEW = "55eb10b86a57de55a97e293a78228d9dd17b809a"
RELEASE = "refs/remotes/origin/release/withdrawal-department-phase1-2026-11-17"

def git(*args):
    return subprocess.run(["git", "-C", str(A), *args],
                          capture_output=True, text=True, timeout=30)

def stop(condition, label):
    if not condition:
        raise SystemExit("STOP: " + label)

stop(A.is_dir() and not A.is_symlink(), "APP ROOT")
stop(git("rev-parse", "--show-toplevel").stdout.strip() == str(A), "GIT ROOT")
stop(git("rev-parse", "HEAD").stdout.strip() == OLD, "LIVE SOURCE CHANGED")
stop(git("symbolic-ref", "-q", "--short", "HEAD").returncode == 1, "APP NOT DETACHED")
stop(git("status", "--porcelain=v1", "--untracked-files=all").stdout.strip() == "?? AGENTS.md",
     "GIT WORKTREE CHANGED")
stop((A / "AGENTS.md").is_file() and not (A / "AGENTS.md").is_symlink(),
     "PROTECTED LOCAL AGENTS")
stop(git("ls-tree", "-r", "--name-only", "HEAD", "--", "AGENTS.md").stdout.strip() == "",
     "LOCAL AGENTS TRACKED")
spec = importlib.util.find_spec("ccpcerp")
stop(spec is not None and spec.origin and Path(spec.origin).resolve()
     == (A / "ccpcerp/__init__.py").resolve(), "INSTALLED APP IMPORT CHANGED")
for site in ("development.localhost", "ccpc-integration2.localhost"):
    stop((B / "sites" / site / "site_config.json").is_file(), "VALID DEV SITE ABSENT")
    snap = B / ".ccpc-pr32-snapshots" / (
       "development.localhost-20261118T233442Z-8db803832468" if site == "development.localhost"
       else "ccpc-integration2.localhost-20261118T233442Z-8db803832468")
    stop((snap / "SHA256SUMS").is_file(), "LOCAL SNAPSHOT ABSENT")
stop((B / "sites/ccpc-integration.localhost/site_config.json").is_file(),
     "BROKEN THIRD SITE STATE CHANGED")
print("DEV LIVE SOURCE + AGENTS + TWO SITE RECOVERY SETS: PASS")
print("RELEASE COMMIT OBJECT PRESENT: " +
      ("YES" if git("cat-file", "-e", NEW + "^{commit}").returncode == 0 else "NO"))
remote = git("remote", "get-url", "origin")
stop(remote.returncode == 0, "GIT REMOTE MISSING")
url = remote.stdout.strip()
mode = "SSH" if url.startswith(("git@", "ssh://")) else (
    "HTTPS" if url.startswith("https://") else "LOCAL_OR_OTHER")
print("APP GIT ORIGIN TRANSPORT: " + mode)
track = git("rev-parse", "--verify", RELEASE)
print("RELEASE REMOTE TRACKING EXACT: " +
      ("YES" if track.returncode == 0 and track.stdout.strip() == NEW else "NO"))
all_ps = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True,
                        text=True, timeout=20)
stop(all_ps.returncode == 0, "PROCESS INVENTORY")
honcho = []
for line in all_ps.stdout.splitlines():
    if "/honcho start" in line or "/honcho', 'start" in line:
        pid = line.strip().split()[0]
        if pid.isdigit():
            honcho.append(pid)
print("DEV HONCHO MATCHING PROCESS IDS: " + (",".join(honcho) if honcho else "NONE"))
print("READ-ONLY DEV CUTOVER DISCOVERY: PASS")
PY
```

**Stop on unexpected output.** Send only the printed PASS/STOP/status lines (no site configs, credentials, SQL files or raw `git remote` URLs). Release object availability, credential-safe Git transport, and Honcho PID are needed to choose the next stage.

## Gate B — isolated release staging (after Gate A passes; no live code activation)

**Candidate mechanism:** A fully independent `git clone --no-hardlinks --no-checkout` of the existing application into a uniquely named hidden staging directory on the **same underlying DEV workspace filesystem**, then checkout `--detach` at the exact pinned release SHA; verify `git rev-parse HEAD`, `git status` and branch, and that root `AGENTS.md` is from tracked release source. Never include the original untracked `AGENTS.md` in this staging clone. The stage directory must not replace the live application, install packages, sync assets or point any running Frappe workers at different code. Stage/source availability is contingent on the release commit object and remote tracking discovered at Gate A; if absent, fetch only through an explicitly inspected safe Git transport without displaying tokens. Do not assume default branch or use floating SHA.

## Gate C — protected DEV-only maintenance, code switch and migration

1. Obtain an uncontested DEVELOPMENT maintenance window. Both valid sites may be unavailable because their code is shared. Identify actual current Honcho process identity, children, scheduled jobs and potential third-site scheduler behavior. Do not reuse historical PID 193 or PID 380905; do not kill arbitrary processes, restart Docker/Compose, or touch legacy PRODUCTION resources.
2. Verify the matching exact-code original checkout and staging clone with fresh hashes and both backup manifests; preserve Nov19 + older Nov17 snapshot sets and owner-controlled `AGENTS.md`. Before stopping anything, document a bounded rollback and potential need for **database/file restore**, not just source rename, if migration writes schema/data.
3. After safe DEVELOPMENT-only process stop, prefer an atomic same-filesystem directory rename of the **entire** old application checkout to a unique, protected sibling path and the **independent staging clone** into the original `apps/ccpcerp` path; no direct `git checkout` in the old repo, no overwrite of its untracked `AGENTS.md`, and no reuse of the old app's original `.git` as the release repo's worktree. Re-verify `ccpcerp` Python import origin and exact release commit without starting services.
4. Run separately targeted `bench --site ccpc-integration2.localhost migrate` then `bench --site development.localhost migrate` only **after** verifying actual app/backend version compatibility, the complete `setup.after_migrate()` effect list, SQL patch-log/master prerequisites and FINANCE onboarding/permissions. Migration may modify both sites' databases and metadata, and may fail; if it fails, **stop** and follow the recovery procedure—not a blind Git reset, migration retry or `--site all`. Never migrate `ccpc-integration.localhost`.
5. After both valid sites pass schema/role/Page checks, restart **only named DEV Honcho-managed processes**, validating that the scheduler does not accidentally enumerate and fail on broken third site before enabling routine scheduling; check HTTP, queue/worker, site routing, UAT and Finance maker/checker permissions. Do not infer health just from HTTP 200.
6. If source switch fails **before any migration**, a guarded two-directory rollback can restore prior app source. If migration fails/partially completes, code-only rollback is insufficient: preserve original, assess DB transactional effects, and use the separately scoped exact backup restore procedure only with verified site targets and explicit operator approval. No automated restore or destructive recovery shortcut is authorized.

**No actual Gate B/C execution has occurred yet.** The staged plan is not proof that installed package paths, full Frappe site boot or live business transactions will succeed; those are DEVELOPMENT acceptance checks after safe execution.


## November 19 — Gate A PASSED; Phase 1 Git object absent; exact GitHub SSH staging step

**Owner-supplied real read-only gate output:**
```text
ORIGINAL PR33 CHECKOUT: VERIFIED
PROTECTED AGENTS.md: VERIFIED
RELEASE COMMIT OBJECT PRESENT: NO
APP GIT ORIGIN TRANSPORT: SSH
RELEASE REMOTE TRACKING EXACT: NO
DEV HONCHO PROCESS IDS: 543180
DEVELOPMENT PRE-CUTOVER INSPECTION: PASS
```

**Interpretation:** On the live bench, PR33 is intact and the protected untracked file remains. The release commit and its remote tracking ref are absent, so an in-place checkout or a local clone then direct checkout **cannot** supply the release without fetching GitHub. `543180` is a **read-only process match**, not a validated process tree or authorization to send a signal to that PID. Re-inspect PID/session/ownership separately before any DEV maintenance stop. No shutdown or release fetch occurred in Gate A.

**GitHub re-confirmed:** Phase1 release exact `55eb10b86a57de55a97e293a78228d9dd17b809a`; PR33 exact `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`.

**Gate B implementation:** Use an independent SSH clone from the **known repository** `git@github.com:ccpcerp/ccpcerp.git` directly into a previously nonexistent, hidden staging directory outside `apps` and `sites`. The command below will **write only to that new staging directory**. It checks the exact live source and local `AGENTS.md` before/after; requires an already trusted GitHub SSH host key; rejects interactive password or host-key prompts. No Git remote URL, token, key or sensitive configuration is printed. The clone is deliberately `--no-checkout` followed by checkout `--detach` of the exact verified release SHA. **Do not** execute the later cutover/migration from this staging approval.

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = "ccpcerpserver" || { echo "STOP: WRONG HOST"; exit 1; }
test "$(id -un)" = "gani" || { echo "STOP: WRONG OPERATOR"; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = "true" || { echo "STOP: DEV CONTAINER NOT RUNNING"; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = "frappe_docker_devcontainer" || { echo "STOP: WRONG COMPOSE PROJECT"; exit 1; }
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev" bash -s <<'DEV'
set -euo pipefail
umask 077
bench=/workspace/development/frappe-bench
live="$bench/apps/ccpcerp"
stage="$bench/.ccpc-phase1-release-stage-20261119-55eb10b86a57"
old=25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87
release=55eb10b86a57de55a97e293a78228d9dd17b809a
branch=release/withdrawal-department-phase1-2026-11-17

test -d "$live" && test ! -L "$live" || { echo "STOP: LIVE APP DIRECTORY"; exit 1; }
test "$(git -C "$live" rev-parse HEAD)" = "$old" || { echo "STOP: LIVE APP HEAD CHANGED"; exit 1; }
test -z "$(git -C "$live" branch --show-current)" || { echo "STOP: LIVE HEAD NOT DETACHED"; exit 1; }
test "$(git -C "$live" status --porcelain=v1 --untracked-files=all)" = "?? AGENTS.md" || { echo "STOP: LIVE GIT STATUS CHANGED"; exit 1; }
test -f "$live/AGENTS.md" && test ! -L "$live/AGENTS.md" || { echo "STOP: LOCAL AGENTS NOT PROTECTED"; exit 1; }
test ! -e "$stage" && test ! -L "$stage" || { echo "STOP: STAGING PATH ALREADY EXISTS"; exit 1; }
test -w "$bench" || { echo "STOP: BENCH DIRECTORY NOT WRITABLE"; exit 1; }
for s in development.localhost ccpc-integration2.localhost; do
  test -f "$bench/sites/$s/site_config.json" || { echo "STOP: DEV SITE CONFIG MISSING"; exit 1; }
done
printf '%s\n' "LIVE PR33 / AGENTS.md: VERIFIED" "ISOLATED STAGING PATH: AVAILABLE" "FETCHING PINNED PHASE1 RELEASE FROM GITHUB SSH"
if ! GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no -o ConnectTimeout=15' \
    git clone --quiet --no-checkout --single-branch --depth 1 --branch "$branch" \
    git@github.com:ccpcerp/ccpcerp.git "$stage" >/dev/null 2>&1; then
  echo "STOP: GITHUB SSH CLONE FAILED; DO NOT DELETE OR RETRY BLINDLY"
  exit 1
fi
if ! git -C "$stage" -c advice.detachedHead=false checkout --quiet --detach "$release" >/dev/null 2>&1; then
  echo "STOP: EXACT RELEASE CHECKOUT FAILED; STAGE RETAINED"
  exit 1
fi
test "$(git -C "$stage" rev-parse HEAD)" = "$release" || { echo "STOP: STAGED RELEASE SHA MISMATCH"; exit 1; }
test -z "$(git -C "$stage" branch --show-current)" || { echo "STOP: STAGED RELEASE NOT DETACHED"; exit 1; }
test -z "$(git -C "$stage" status --porcelain=v1 --untracked-files=all)" || { echo "STOP: STAGED RELEASE NOT CLEAN"; exit 1; }
test -n "$(git -C "$stage" ls-tree -r --name-only HEAD -- AGENTS.md)" && test -f "$stage/AGENTS.md" || { echo "STOP: RELEASE AGENTS.md MISSING"; exit 1; }
test -f "$stage/ccpcerp/__init__.py" || { echo "STOP: STAGED APP PACKAGE MISSING"; exit 1; }
test "$(git -C "$live" rev-parse HEAD)" = "$old" || { echo "STOP: LIVE SOURCE CHANGED DURING STAGE"; exit 1; }
test "$(git -C "$live" status --porcelain=v1 --untracked-files=all)" = "?? AGENTS.md" || { echo "STOP: LIVE STATUS CHANGED DURING STAGE"; exit 1; }
echo "STAGED PHASE1 RELEASE COMMIT: $release"
echo "STAGED RELEASE SOURCE: CLEAN, DETACHED, SEPARATE"
echo "LIVE PR33 SOURCE / LOCAL AGENTS.md: UNCHANGED"
echo "PHASE1 STAGING: PASS"
echo "SOURCE SWITCH / MIGRATIONS / DEV RESTART: NOT PERFORMED"
DEV
HOST
```

**STOP instructions:** If `GITHUB SSH CLONE FAILED` appears (unknown SSH host key, missing credentials, blocked port or other fetch failure), preserve any newly created staging directory. Do **not** turn off `StrictHostKeyChecking`, export private keys, switch to HTTPS with embedded tokens, remove/retry blindly, or attempt an in-place fetch of the live PR33 repository. If `PHASE1 STAGING: PASS`, the next milestone is a read-only **source path/mount topology and Honcho+worker process inventory**, then actual maintenance source activation; a PASS here is **not a migration or application acceptance**.


## November 19 — Gate B SOURCE STAGING PASS; active DEV service/mount preflight next

**Owner-reported live staging terminal output, exact (last terminal line in user paste truncated after NOT PERFOR):**
```text
LIVE PR33 / AGENTS.md: VERIFIED
ISOLATED STAGING PATH: AVAILABLE
FETCHING PINNED PHASE1 RELEASE FROM GITHUB SSH
STAGED PHASE1 RELEASE COMMIT: 55eb10b86a57de55a97e293a78228d9dd17b809a
STAGED RELEASE SOURCE: CLEAN, DETACHED, SEPARATE
LIVE PR33 SOURCE / LOCAL AGENTS.md: UNCHANGED
PHASE1 STAGING: PASS
SOURCE SWITCH / MIGRATIONS / DEV RESTART: NOT PERFOR
```

**Assessment:** GitHub's exact release SHA was cloned over the already-trusted SSH GitHub transport into `frappe-bench/.ccpc-phase1-release-stage-20261119-55eb10b86a57` as a separate tracked-clean, detached release. The original `apps/ccpcerp` PR33 checkout and its untracked `AGENTS.md` were unchanged. The final line was truncated during user paste; given the script's explicit earlier PASS and lack of a switch operation, source activation has **not** been reported/performed. The earlier read-only check observed DEV Honcho matching PID **543180**, which is not a validated safe stop target; no service shutdown authorized by mere PID match.

**Next safe step — READ ONLY:** Verify inside the named DEVELOPMENT container that both Git checkouts are unmodified and on exactly pinned SHAs; source directory and stage are on the same filesystem (atomic rename prerequisite); `apps/ccpcerp` is not an exact separate Docker bind mount; both site configs and recent checksum manifests still exist; identify the **current** Honcho PID, parent, process group and session, ensure one `frappe` owner, and report worker/group count. If mount/process identity differs, STOP and redesign. No DB/site initialization, network, Git fetch, renames, migrations, service stops or PID signalling in this inventory.

Operator command:

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver || { echo "STOP: WRONG HOST"; exit 1; }
test "$(id -un)" = gani || { echo "STOP: WRONG OPERATOR"; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo "STOP: DEV NOT RUNNING"; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || { echo "STOP: WRONG COMPOSE PROJECT"; exit 1; }
sudo docker inspect --format '{{json .Mounts}}' "$dev" | python3 -c '
import json,sys
mounts=json.load(sys.stdin)
must_not="/workspace/development/frappe-bench/apps/ccpcerp"
if any(str(m.get("Destination","")).rstrip("/") == must_not for m in mounts):
    sys.exit("STOP: ACTIVE APP HAS AN EXACT DOCKER MOUNT")
print("ACTIVE APP SEPARATE DOCKER MOUNT: NO")
print("DEVELOPMENT CONTAINER MOUNT INVENTORY: PASS")
'
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev" \
  /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
from pathlib import Path
import os
import re
import subprocess
B=Path("/workspace/development/frappe-bench")
A=B/"apps/ccpcerp"
S=B/".ccpc-phase1-release-stage-20261119-55eb10b86a57"
OLD="25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
NEW="55eb10b86a57de55a97e293a78228d9dd17b809a"
def stop(ok,why):
    if not ok: raise SystemExit("STOP: "+why)
def git(repo,*args):
    p=subprocess.run(["git","-C",str(repo),*args],capture_output=True,text=True,timeout=30)
    stop(p.returncode==0,"GIT CHECK FAILED")
    return p.stdout.strip()
stop(A.is_dir() and S.is_dir() and not A.is_symlink() and not S.is_symlink(),"SOURCE DIRECTORY")
stop((S/".git").is_dir() and not (S/".git").is_symlink(),"STAGING GIT DIR")
stop(git(A,"rev-parse","HEAD")==OLD,"ORIGINAL SHA CHANGED")
stop(git(S,"rev-parse","HEAD")==NEW,"STAGED SHA CHANGED")
stop(git(A,"status","--porcelain=v1","--untracked-files=all")=="?? AGENTS.md","PR33 STATUS CHANGED")
stop(git(S,"status","--porcelain=v1","--untracked-files=all")=="","STAGED STATUS CHANGED")
stop((A/"AGENTS.md").is_file() and not (A/"AGENTS.md").is_symlink(),"PROTECTED AGENTS MISSING")
stop((S/"AGENTS.md").is_file() and bool(git(S,"ls-tree","-r","--name-only","HEAD","--","AGENTS.md")),"RELEASE AGENTS MISSING")
stop(B.stat().st_dev == A.stat().st_dev == S.stat().st_dev == (B/"apps").stat().st_dev,"NOT SAME FILESYSTEM")
for site,folder in (
  ("development.localhost","development.localhost-20261118T233442Z-8db803832468"),
  ("ccpc-integration2.localhost","ccpc-integration2.localhost-20261118T233442Z-8db803832468"),
):
    stop((B/"sites"/site/"site_config.json").is_file(),"SITE CONFIG MISSING")
    stop((B/".ccpc-pr32-snapshots"/folder/"SHA256SUMS").is_file(),"SNAPSHOT MANIFEST MISSING")
stop((B/"sites/ccpc-integration.localhost/site_config.json").is_file(),"BROKEN SITE STATUS CHANGED")
p=subprocess.run(["ps","-eo","pid=,ppid=,pgid=,sid=,user=,stat=,args="],capture_output=True,text=True,timeout=20)
stop(p.returncode==0,"PROCESS INSPECTION FAILED")
rows=[]
for line in p.stdout.splitlines():
    fields=line.split(None,6)
    if len(fields)<7: continue
    pid,ppid,pgid,sid,user,state,cmd=fields
    if re.search(r"(?:^|/)honcho start(?:\s|$)",cmd):
        rows.append((pid,ppid,pgid,sid,user,state))
stop(len(rows)==1,"HONCHO COUNT NOT ONE")
pid,ppid,pgid,sid,user,state=rows[0]
stop(user=="frappe" and not state.startswith("Z"),"HONCHO OWNER/STATE")
stop(pid=="543180","HONCHO PID CHANGED SINCE READ-ONLY GATE A")
group_count=sum(1 for line in p.stdout.splitlines()
    if len(line.split(None,6))>=7 and line.split(None,6)[2]==pgid
    and line.split(None,6)[4]=="frappe" and not line.split(None,6)[5].startswith("Z"))
print("LIVE PR33 / LOCAL AGENTS: PASS")
print("STAGED RELEASE EXACT SHA / CLEAN: PASS")
print("APP SOURCE + STAGE SAME FILESYSTEM: PASS")
print("TWO SITE SNAPSHOTS PRESENT: PASS")
print("HONCHO PID:",pid)
print("HONCHO PPID:",ppid)
print("HONCHO PGID:",pgid)
print("HONCHO SESSION:",sid)
print("HONCHO GROUP FRAPPE PROCESS COUNT:",group_count)
print("DEV SHARED-BENCH PRE-MAINTENANCE READ-ONLY: PASS")
PY
HOST
```

**STOP on any deviation** rather than changing the expected PID or disabling checks. These outputs will establish whether a same-filesystem guarded directory rename is technically viable. Do not send `SIGINT` to PID 543180 based on this command alone; a precise DEV-only service interruption plan, app import behavior and site migration impact still need review. No source switch or database write is part of this step.


## November 19 — Mount/filesystem preflight PASS; Honcho parent PID zero requires targeted read-only topology check

**Owner's exact operator output from previous read-only preflight** (two leading heredoc delimiters also appeared in paste):
```text
ACTIVE APP SEPARATE DOCKER MOUNT: NO
DEVELOPMENT CONTAINER MOUNT INVENTORY: PASS
LIVE PR33 / LOCAL AGENTS: PASS
STAGED RELEASE EXACT SHA / CLEAN: PASS
APP SOURCE + STAGE SAME FILESYSTEM: PASS
TWO SITE SNAPSHOTS PRESENT: PASS
HONCHO PID: 543180
HONCHO PPID: 0
HONCHO PGID: 543180
HONCHO SESSION: 543180
HONCHO GROUP FRAPPE PROCESS COUNT: 5
DEV SHARED-BENCH PRE-MAINTENANCE READ-ONLY: PASS
```

**Interpretation:** Correct named DEV Docker project, separate app bind mount absent, staged exact release and original PR33 clean/protected, matched source+stage filesystem and site snapshot manifests verified. Honcho still has exact observed PID **543180**, own PGID+SID **543180**, but **PPID 0**. A reported parent of zero can reflect PID namespace boundaries or other unusual process parent visibility; it does not prove the process can be safely stopped, who would restart it, whether its workers are all healthy, or whether unrelated services share the group. Five group members do **not** automatically prove five healthy Procfile services. No services have been stopped and no code/DB changes have been made.

**Next: exact read-only process/topology census.** Do not signal/kill PID 543180 based on earlier broad process count. Run only the command below from `gani@ccpcerpserver`. It checks the named DEV Docker container, PID namespace mode and one named live Honcho instance; examines process parent/group/session relationship and its descendants **without exposing full command lines or environment variables**; confirms configured Procfile labels but does not read config secrets, access the database, or touch other containers. Its only output is sanitized process counts and statuses.

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver && test "$(id -un)" = gani || { echo "STOP: WRONG HOST OR OPERATOR"; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo "STOP: DEV NOT RUNNING"; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || { echo "STOP: WRONG DEV COMPOSE PROJECT"; exit 1; }
mode=$(sudo docker inspect --format '{{.HostConfig.PidMode}}' "$dev")
case "$mode" in ""|"private") echo "DEV CONTAINER PID MODE: PRIVATE_OR_DEFAULT";; "host") echo "DEV CONTAINER PID MODE: HOST";; *) echo "DEV CONTAINER PID MODE: OTHER";; esac
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev" \
 /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
from pathlib import Path
import re
import subprocess

BENCH = Path("/workspace/development/frappe-bench")
EXPECTED_PID = 543180
p = subprocess.run(["ps", "-eo", "pid=,ppid=,pgid=,sid=,user=,stat=,comm=,args="],
                   capture_output=True, text=True, timeout=20)
if p.returncode:
    raise SystemExit("STOP: PROCESS SNAPSHOT FAILED")
rows = {}
for line in p.stdout.splitlines():
    parts = line.split(None, 7)
    if len(parts) != 8:
        continue
    pid, parent, group, session, user, state, executable, args = parts
    if all(s.isdigit() for s in (pid, parent, group, session)):
        rows[int(pid)] = (int(parent), int(group), int(session), user, state, executable, args)
honcho_pids = [pid for pid, row in rows.items()
               if re.search(r"(?:^|/)honcho start(?:\s|$)", row[-1])]
if honcho_pids != [EXPECTED_PID] or EXPECTED_PID not in rows:
    raise SystemExit("STOP: HONCHO IDENTITY OR COUNT CHANGED")
parent, group, session, owner, state, executable, cmd = rows[EXPECTED_PID]
if owner != "frappe" or state.startswith("Z") or group != EXPECTED_PID or session != EXPECTED_PID:
    raise SystemExit("STOP: HONCHO OWNER/PROCESS GROUP/SESSION CHANGED")
procfile = BENCH / "Procfile"
if not procfile.is_file():
    raise SystemExit("STOP: PROCFILE MISSING")
labels = re.findall(r"^([a-z][a-z0-9_-]*):", procfile.read_text(), re.M)
if set(labels) != {"web", "socketio", "watch", "schedule", "worker"} or len(labels) != 5:
    raise SystemExit("STOP: PROCFILE SERVICE LABELS CHANGED")
descendants = set()
frontier = {EXPECTED_PID}
while frontier:
    current = {pid for pid, row in rows.items() if row[0] in frontier and pid not in descendants}
    current.discard(EXPECTED_PID)
    descendants |= current
    frontier = current
members = {pid for pid, row in rows.items() if row[1] == group and row[3] == session}
non_frappe = [pid for pid in (members | descendants)
              if rows[pid][3] != "frappe"]
if non_frappe:
    raise SystemExit("STOP: NON-FRAPPE PROCESS IN HONCHO GROUP/TREE")
cwd = Path("/proc") / str(EXPECTED_PID) / "cwd"
try:
    cwd_ok = cwd.resolve() == BENCH.resolve()
except (OSError, PermissionError):
    cwd_ok = False
print("HONCHO PROCESS IDENTITY: VERIFIED")
print("HONCHO PID:", EXPECTED_PID)
print("HONCHO REPORTED PPID:", parent)
print("HONCHO SESSION/GROUP LEADER: YES")
print("HONCHO CWD BENCH MATCH:", "YES" if cwd_ok else "NO_OR_UNAVAILABLE")
print("PROCFILE SERVICE LABELS: web socketio watch schedule worker")
print("HONCHO SAME-SESSION GROUP PROCESSES:", len(members))
print("HONCHO DESCENDANT PROCESSES:", len(descendants))
print("HONCHO DESCENDANT PROCESS GROUPS:", len({rows[pid][1] for pid in descendants}))
print("HONCHO GROUP/TREE OWNER CHECK: FRAPPE ONLY")
print("DEV HONCHO TOPOLOGY READ-ONLY: PASS")
PY
HOST
```

**Risk gate:** If parent remains zero or Honcho cwd is not confirmed, do not guess a safe signal, shutdown mechanism, or agent ownership. Review the output and verify Honcho supervisor/restart mechanism and absence of site transactions/critical queued jobs before any maintenance stop. For actual cutover, the source-only directory swap still requires the site-specific patch log and `setup.after_migrate` review, a planned DEV outage for both sites, and a rollback strategy that may require both databases/files (not merely the Git code). Absolutely no `docker compose down`, global `pkill`, automatic restart, `--site all migrate` or PRODUCTION involvement.


## November 19 — Honcho topology PASS; detached exec provenance and SQL read-only patch/masters gate

**Owner supplied actual process census** (no mutation):
```text
DEV CONTAINER PID MODE: PRIVATE_OR_DEFAULT
HONCHO PROCESS IDENTITY: VERIFIED
HONCHO PID: 543180
HONCHO REPORTED PPID: 0
HONCHO SESSION/GROUP LEADER: YES
HONCHO CWD BENCH MATCH: YES
PROCFILE SERVICE LABELS: web socketio watch schedule worker
HONCHO SAME-SESSION GROUP PROCESSES: 5
HONCHO DESCENDANT PROCESSES: 11
HONCHO DESCENDANT PROCESS GROUPS: 3
HONCHO GROUP/TREE OWNER CHECK: FRAPPE ONLY
DEV HONCHO TOPOLOGY READ-ONLY: PASS
```

**Provenance check from existing deployment docs:** `docs/ccpc-project/DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md` documents a DEV-only `docker exec -d --user frappe ... exec /home/frappe/.local/bin/honcho start` launch and observed past detached Honcho PID **380905 PPID 0**. The current **PPID 0** is consistent with this precedent, although today's exact launch mechanism and later shutdown/restart are not directly proved. Honcho CWD matches exact bench and all process group/tree owners were reported as `frappe`; no service has been signalled. These checks are topology, not site health or migration acceptance.

**Next Gate C prerequisite (READ ONLY):** Given that the currently staged Phase1 `ccpcerp/patches.txt` matches the old source list but numerous `setup.after_migrate` operations can update site tables and permissions, check the actual *two site's* Patch Log and presence of prerequisite masters before stopping DEV services. The older runbook documents a corrected Frappe read-only inspection launched **from `frappe-bench/sites`** with `sites_path="."` and `FRAPPE_STREAM_LOGGING=1` to avoid an invalid logging CWD. Do **not** run `bench migrate`, touch the broken third site, create missing master data, or assign Finance roles based on these counts.

Run at `gani@ccpcerpserver`:

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver && test "$(id -un)" = gani || { echo 'STOP: WRONG HOST OR OPERATOR'; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo 'STOP: DEV CONTAINER DOWN'; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || { echo 'STOP: WRONG DEV COMPOSE PROJECT'; exit 1; }
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev"  env FRAPPE_STREAM_LOGGING=1 /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
from pathlib import Path
import frappe
import subprocess

base = Path("/workspace/development/frappe-bench")
old = "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
release = "55eb10b86a57de55a97e293a78228d9dd17b809a"
def git_head(path):
    p = subprocess.run(["git","-C",str(path),"rev-parse","HEAD"],
                       capture_output=True,text=True,timeout=30,check=True)
    return p.stdout.strip()
if git_head(base/"apps/ccpcerp") != old or    git_head(base/".ccpc-phase1-release-stage-20261119-55eb10b86a57") != release:
    raise SystemExit("STOP: SOURCE OR STAGING CHANGED")
patch_list = [
    x.strip() for x in (base/"apps/ccpcerp/ccpcerp/patches.txt").read_text().splitlines()
    if x.strip().startswith("ccpcerp.patches.")
]
release_patch_list = [
    x.strip() for x in (base/".ccpc-phase1-release-stage-20261119-55eb10b86a57/ccpcerp/patches.txt").read_text().splitlines()
    if x.strip().startswith("ccpcerp.patches.")
]
if patch_list != release_patch_list or len(patch_list) != 8:
    raise SystemExit("STOP: PATCH LIST CHANGED")
databases = []
for site in ("development.localhost", "ccpc-integration2.localhost"):
    frappe.init(site=site, sites_path=".")
    try:
        frappe.connect()
        frappe.db.sql("START TRANSACTION READ ONLY")
        dbname = frappe.db.sql("SELECT DATABASE()")[0][0]
        if not dbname:
            raise RuntimeError("DATABASE NAME EMPTY")
        databases.append(dbname)
        recorded = {r[0] for r in frappe.db.sql("SELECT patch FROM `tabPatch Log`", as_list=True)}
        print("DEV SITE PATCH INVENTORY:", site)
        for patch in patch_list:
            print("  " + patch.rsplit(".",1)[-1] + ":", "RECORDED" if patch in recorded else "NOT RECORDED")
        for table in ("tabCompany", "tabAccount", "tabCustomer", "tabSupplier"):
            count = int(frappe.db.sql("SELECT COUNT(*) FROM `" + table + "`")[0][0])
            print("  " + table + " COUNT:", count)
    finally:
        try:
            if frappe.db:
                frappe.db.rollback()
        finally:
            frappe.destroy()
if len(set(databases)) != 2:
    raise SystemExit("STOP: DEV SITES SHARE SAME DATABASE")
print("TWO DEV SITES: SEPARATE DATABASE CONNECTIONS VERIFIED")
print("DEV PATCH LOG + MASTER COUNTS READ-ONLY: PASS")
print("SOURCE SWITCH / MIGRATION / STOP: NOT PERFORMED")
PY
HOST
```

**Important limits:** A `PASS` here proves that SQL reads and patch history can be queried with two distinct active site connections, **not** that required Chart of Accounts branches, canonical Company names, intercompany Customer/Supplier relationships, permission mappings or patch side effects are safe. A `NOT RECORDED` patch must be evaluated against its actual patch source and live master config before a migration. If a read-only inspection fails, STOP rather than adding missing accounting masters or enabling `--site all`. End-user DEVELOPMENT traffic and queued job quiescence must still be established before any Honcho stop, and a code-only rollback after DB migration remains unsafe.


## November 19 — Both sites 8/8 patches recorded; migration side-effect census before cutover

**Owner-supplied actual read-only results (verified operator command):**

```text
DEV SITE PATCH INVENTORY: development.localhost
  check_work_request_job_order_duplicates: RECORDED
  migrate_phase1_equipment_costing: RECORDED
  create_equipment_accounting_dimension: RECORDED
  grant_operational_requestor_roles: RECORDED
  grant_purchase_order_approver_role: RECORDED
  create_intercompany_material_accounts: RECORDED
  create_intercompany_parties: RECORDED
  add_intercompany_material_billing_indexes: RECORDED
  tabCompany COUNT: 25
  tabAccount COUNT: 2870
  tabCustomer COUNT: 16
  tabSupplier COUNT: 16
DEV SITE PATCH INVENTORY: ccpc-integration2.localhost
  check_work_request_job_order_duplicates: RECORDED
  migrate_phase1_equipment_costing: RECORDED
  create_equipment_accounting_dimension: RECORDED
  grant_operational_requestor_roles: RECORDED
  grant_purchase_order_approver_role: RECORDED
  create_intercompany_material_accounts: RECORDED
  create_intercompany_parties: RECORDED
  add_intercompany_material_billing_indexes: RECORDED
  tabCompany COUNT: 2
  tabAccount COUNT: 199
  tabCustomer COUNT: 1
  tabSupplier COUNT: 1
TWO DEV SITES: SEPARATE DATABASE CONNECTIONS VERIFIED
DEV PATCH LOG + MASTER COUNTS READ-ONLY: PASS
SOURCE SWITCH / MIGRATION / STOP: NOT PERFORMED
```

**Assessment:** Both valid DEVELOPMENT sites have all eight existing `ccpcerp` Patch Log entries, and their database connections were confirmed separate. MAIN has 25 Companies vs Integration2 only 2, and drastically different master volumes. This **does not** mean migration cannot alter data: `ccpcerp.setup.after_migrate()` is always invoked from release `hooks.py`. The pinned release `55eb10b86a57de55a97e293a78228d9dd17b809a` code directly invokes role/permission setup, MRS print/workflow replacement, workforce assignments, Purchase Order approval status backfill, stock field creation, Withdrawal Slip workflow replacement and issue quantity backfill. Specifically `reset_maintenance_supervisor_desktop_layouts` calls `frappe.delete_doc_if_exists("Desktop Layout", user_name, force=True)` for operational roleholders. `backfill_mrs_display_names` updates all MRS rows; `backfill_mrs_item_search_text` and procurement status update records as needed. Neither `8/8 RECORDED` nor a backup SQL import alone proves these effects are safe on both sites.

**Next step is still READ ONLY** and prints only table presence/aggregate counts, no business-row values, no user identities, and no credentials. This is a scoped pre-migration risk census, not a release activation. Run the following at `gani@ccpcerpserver`:

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver && test "$(id -un)" = gani || { echo 'STOP: WRONG HOST OR USER'; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo 'STOP: DEV CONTAINER NOT RUNNING'; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || { echo 'STOP: NOT DEV PROJECT'; exit 1; }
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev" \
 env FRAPPE_STREAM_LOGGING=1 /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
from pathlib import Path
import subprocess
import frappe

B=Path("/workspace/development/frappe-bench")
repos=((B/"apps/ccpcerp","25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"),
       (B/".ccpc-phase1-release-stage-20261119-55eb10b86a57","55eb10b86a57de55a97e293a78228d9dd17b809a"))
for path,expected in repos:
    p=subprocess.run(["git","-C",str(path),"rev-parse","HEAD"],
                     capture_output=True,text=True,timeout=20)
    if p.returncode or p.stdout.strip()!=expected:
        raise SystemExit("STOP: SOURCE COMMIT MOVED")

def table_columns(t):
    names=frappe.db.sql(
      "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s",
      ("tab"+t,),as_list=True)
    return {row[0] for row in names}

def count(label, table, columns=(), where=None):
    known=table_columns(table)
    if not known:
        print(label+": TABLE NOT PRESENT")
        return
    if not set(columns).issubset(known):
        print(label+": COLUMN NOT PRESENT")
        return
    q="SELECT COUNT(*) FROM `tab"+table+"`"+(" WHERE "+where if where else "")
    print(label+": "+str(int(frappe.db.sql(q)[0][0])))

for site in ("development.localhost","ccpc-integration2.localhost"):
    frappe.init(site=site, sites_path=".")
    try:
        frappe.connect()
        frappe.db.sql("START TRANSACTION READ ONLY")
        print("DEV MIGRATION IMPACT CENSUS:",site)
        for table in ("MRS","MRS Item","Purchase Order","Withdrawal Slip",
                      "Withdrawal Slip Item","CCPC Personnel","Equipment Registry","Desktop Layout"):
            count("  EXISTING "+table,table)
        count("  PO WITHOUT APPROVAL STATUS","Purchase Order",
              ("ccpc_approval_status",),"COALESCE(ccpc_approval_status,'') = ''")
        count("  WITHDRAWAL ITEMS NONPOSITIVE ISSUE QTY","Withdrawal Slip Item",
              ("issue_qty",),"COALESCE(issue_qty,0) <= 0")
        count("  PERSONNEL WITHOUT COMPANY","CCPC Personnel",
              ("company",),"COALESCE(company,'') = ''")
        count("  EQUIPMENT AREA WITH EMPTY SECTION","Equipment Registry",
              ("area","section"),"COALESCE(area,'') != '' AND COALESCE(section,'') = ''")
        if table_columns("Workflow"):
            values=("CCPC MRS Workflow","CCPC Purchase Order Approval",
                    "CCPC Withdrawal Slip Workflow")
            for name in values:
                n=frappe.db.sql(
                  "SELECT COUNT(*) FROM `tabWorkflow` WHERE name=%s",(name,))[0][0]
                print("  WORKFLOW DEFINITION PRESENT:",name,"YES" if n else "NO")
        for role in ("CCPC Mapping Preparer","CCPC Accounting Mapping Approver",
                     "CCPC Group Executive Reporting"):
            n=frappe.db.sql(
              "SELECT COUNT(*) FROM `tabRole` WHERE name=%s",(role,))[0][0]
            print("  ROLE DEFINITION PRESENT:",role,"YES" if n else "NO")
        print("DEV MIGRATION IMPACT READ ONLY:",site,"PASS")
    finally:
        try:
            if frappe.db:
                frappe.db.rollback()
        finally:
            frappe.destroy()
print("PHASE1 TWO-SITE IMPACT CENSUS: PASS")
print("HONCHO STOP / SOURCE SWITCH / MIGRATION: NOT PERFORMED")
PY
HOST
```

**Limits of census:** A `PASS` means read-only counts completed, *not* that all migration dependencies or transaction/business invariants are satisfied. If any table/column is absent, record it rather than creating it during inspection. In particular, approval status/workflow counts need human review before triggering broad `after_migrate` logic. One earlier Frappe integration case had a CWD/logger issue: the above starts in `frappe-bench/sites` with `sites_path="."` and stream logging. Preserve both protected backup sets and the original checkout/AGENTS, and keep Honcho live until this impact review is complete. No PRODUCTION operation authorized.
