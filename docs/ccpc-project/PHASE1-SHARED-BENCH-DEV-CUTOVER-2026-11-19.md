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


## November 19 — Migration-impact census PASS; conditional backfills need one targeted read-only assessment

**Owner-reported live read-only migration-impact census (both sites):**

| Metric | MAIN `development.localhost` | Integration2 `ccpc-integration2.localhost` |
|---|---:|---:|
| MRS / MRS Item | 3 / 18 | 0 / 0 |
| Purchase Order | 5 | 0 |
| Withdrawal Slip / Item | 7 / 7 | 1 / 1 |
| CCPC Personnel | 10 | 0 |
| Equipment Registry | 6 | 0 |
| Desktop Layout | 0 | 0 |
| PO missing approval status | 0 | 0 |
| Withdrawal Items with `COALESCE(issue_qty,0) <= 0` | **2** | 0 |
| Personnel with `COALESCE(company,'') = ''` | **3** | 0 |
| Equipment `area` nonblank + `section` blank | 0 | COLUMN NOT PRESENT |
| CCPC MRS / PO / Withdrawal workflows present | YES, each | YES, each |
| Mapping Preparer / Accounting Approver / Group Executive Role definitions present | YES, each | YES, each |

Both per-site inspections reported `DEV MIGRATION IMPACT READ ONLY: ... PASS`, followed by `PHASE1 TWO-SITE IMPACT CENSUS: PASS` and `HONCHO STOP / SOURCE SWITCH / MIGRATION: NOT PERFORMED`. All earlier eight Patch Log entries recorded on both sites, with separate DB connections verified. This is **operator-provided evidence, not independently queried by ChatGPT**. There were no mutations, no shutdown, no code swap.

**Pinned release code interpretation, checked in GitHub at SHA `55eb10b86a57de55a97e293a78228d9dd17b809a`:**

1. `backfill_ccpc_personnel_company()` **only** updates an empty-company Personnel record when it has a populated Department whose Department Company can be resolved. The **3** MAIN blank company rows are a *candidate pool*, not a guarantee that three rows will change. Inspect only aggregated eligibility counts before migration.
2. `backfill_withdrawal_slip_issue_qty()` queries numeric `issue_qty <= 0` and **only** updates rows whose parent Withdrawal Slip status is `Stockroom Review` (uses requested quantity), `Fully Issued`, or `Issued with Shortage` (uses issued, falling back to requested). It requires a positive resolved quantity. The **2** `COALESCE(issue_qty,0) <= 0` rows include potential SQL NULL values and are *not automatically two migration writes*. Inspect eligible count with effective status and quantity.
3. `migrate_equipment_area_to_section()` has a guard `if not meta.has_field("section") or not frappe.db.has_column("Equipment Registry","area"): return`. Thus the missing `area` column on Integration2 currently triggers an intentional skip if still missing at hook time; with **zero** Equipment Registry rows, it is not by itself evidence of a lost record or migration failure. Frappe model synchronization might change columns before `after_migrate`; re-assess any new state.
4. Both sites have **zero** `Desktop Layout` rows; `reset_maintenance_supervisor_desktop_layouts()` would therefore not delete any existing desktop layout in this snapshot, although it still executes role-filtered cache clearing and needs operational review.
5. MAIN has **3 MRS** and `backfill_mrs_display_names()` explicitly calls `frappe.db.set_value` for every MRS row; other MRS item-search/procurement and workflow/permissions operations may also write. `after_migrate()` reruns broadly even when patches are 8/8 recorded. No claim of zero-impact migrations is warranted.

**Next operator action — aggregate read-only eligibility probe on MAIN only**, so the real likely data updates can be assessed before a DEV-only outage. It never retrieves or prints record names, emails, quantities, prices, credentials or complete site configuration:

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver && test "$(id -un)" = gani || { echo 'STOP: WRONG HOST OR OPERATOR'; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo 'STOP: DEV CONTAINER NOT RUNNING'; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || { echo 'STOP: NOT DEV COMPOSE PROJECT'; exit 1; }
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev" \
 env FRAPPE_STREAM_LOGGING=1 /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
import frappe
import subprocess
from pathlib import Path

B=Path("/workspace/development/frappe-bench")
for directory,sha in (
    (B/"apps/ccpcerp", "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"),
    (B/".ccpc-phase1-release-stage-20261119-55eb10b86a57",
     "55eb10b86a57de55a97e293a78228d9dd17b809a"),
):
    p=subprocess.run(["git","-C",str(directory),"rev-parse","HEAD"],
                     capture_output=True,text=True,timeout=20)
    if p.returncode or p.stdout.strip()!=sha:
        raise SystemExit("STOP: SOURCE CHECKOUT CHANGED")

frappe.init(site="development.localhost",sites_path=".")
try:
    frappe.connect()
    frappe.db.sql("START TRANSACTION READ ONLY")
    personnel = frappe.db.sql("""
        SELECT
            COUNT(*) AS missing_company,
            COALESCE(SUM(CASE WHEN COALESCE(p.department,'') != ''
                                  AND COALESCE(d.company,'') != ''
                              THEN 1 ELSE 0 END),0) AS eligible,
            COALESCE(SUM(CASE WHEN COALESCE(p.department,'') = ''
                              THEN 1 ELSE 0 END),0) AS missing_department
        FROM `tabCCPC Personnel` p
        LEFT JOIN `tabDepartment` d ON d.name=p.department
        WHERE COALESCE(p.company,'')=''
    """,as_dict=True)[0]
    issue = frappe.db.sql("""
        SELECT
            COUNT(*) AS nonpositive_or_null,
            COALESCE(SUM(CASE WHEN i.issue_qty IS NULL
                              THEN 1 ELSE 0 END),0) AS null_qty,
            COALESCE(SUM(CASE
                WHEN i.issue_qty<=0
                  AND ((w.status='Stockroom Review' AND i.requested_qty>0)
                       OR (w.status IN ('Fully Issued','Issued with Shortage')
                           AND COALESCE(NULLIF(i.issued_qty,0),i.requested_qty)>0))
                THEN 1 ELSE 0 END),0) AS eligible
        FROM `tabWithdrawal Slip Item` i
        LEFT JOIN `tabWithdrawal Slip` w ON w.name=i.parent
        WHERE COALESCE(i.issue_qty,0)<=0
    """,as_dict=True)[0]
    print("MAIN PERSONNEL COMPANY MISSING:",int(personnel.missing_company))
    print("MAIN PERSONNEL COMPANY BACKFILL ELIGIBLE:",int(personnel.eligible))
    print("MAIN PERSONNEL WITH NO DEPARTMENT:",int(personnel.missing_department))
    print("MAIN WITHDRAWAL ITEMS NONPOSITIVE/NULL:",int(issue.nonpositive_or_null))
    print("MAIN WITHDRAWAL ITEMS NULL QTY:",int(issue.null_qty))
    print("MAIN WITHDRAWAL ISSUE QTY BACKFILL ELIGIBLE:",int(issue.eligible))
    print("MAIN CONDITIONAL BACKFILL CENSUS: PASS")
finally:
    try:
        if frappe.db:
            frappe.db.rollback()
    finally:
        frappe.destroy()
print("DEV SOURCE/MIGRATION/SERVICE CHANGES: NOT PERFORMED")
PY
HOST
```

**Post-census gate:** Compare eligible row counts to the user's intended personnel/stock workflows. Even if eligibility is zero, do not treat the migration as risk-free: MRS names, workflow transitions, permissions, stock-related custom fields and Frappe schema sync remain potentially site-mutating. Before Honcho stop, require safe queue/user quiescence, a separate two-site schema/role compatibility review, rollback readiness for **both** SQL+files, and the expected Finance Phase1-only same-Company rules. Never run `--site all migrate`, alter the broken third site, or perform PRODUCTION operations.


## November 19 — Conditional backfills: ZERO eligible; classify five existing exceptions before outage

**Owner-reported bounded read-only SQL from MAIN `development.localhost`:**

```text
MAIN PERSONNEL COMPANY MISSING: 3
MAIN PERSONNEL COMPANY BACKFILL ELIGIBLE: 0
MAIN PERSONNEL WITH NO DEPARTMENT: 0
MAIN WITHDRAWAL ITEMS NONPOSITIVE/NULL: 2
MAIN WITHDRAWAL ITEMS NULL QTY: 0
MAIN WITHDRAWAL ISSUE QTY BACKFILL ELIGIBLE: 0
MAIN CONDITIONAL BACKFILL CENSUS: PASS
DEV SOURCE/MIGRATION/SERVICE CHANGES: NOT PERFORMED
```

**Meaning, grounded in pinned Phase1 release `55eb10b86a57de55a97e293a78228d9dd17b809a` `ccpcerp/setup.py`:**

- The three personnel have a populated `department` value, but none resolves through `tabDepartment.company` to a nonempty Company. They could have **orphaned Department links or linked Departments with no Company**; the current aggregate alone cannot distinguish. Release's `backfill_ccpc_personnel_company()` would not populate these records in the observed state.
- Both Withdrawal Slip Items have numeric zero/negative (none SQL NULL); neither meets `backfill_withdrawal_slip_issue_qty()` conditions: its parent's `status` must be `Stockroom Review` or `Fully Issued` or `Issued with Shortage`, and the selected source quantity must be positive. Their statuses and values are not yet classified; the migration should not be expected to correct these rows.
- These five candidates are **not a direct Phase1 migration failure**. Do not auto-fix accounting/operational master records based only on this query. Other on-migrate effects still exist, including three MAIN MRS display-name writes, permissions/workflow/role edits and schema sync; migration is **not read-only**.
- No source switch, migration, Honcho stop, PRODUCTION operation, or site record write has occurred.

**Next (LAST data-exception classification, READ ONLY):** Classify the three broken-or-unconfigured personnel Department→Company links, and the two Withdrawal Item parent/status/source-quantity conditions **only as aggregate counts**; return no row IDs, names, prices, amounts or credentials. Then determine whether these existing defects should be handled in later owner-authorized master-data cleanup or warrant a halt to the Phase1 DEV cutover. The command continues to enforce immutable live/stage SHAs and an explicit SQL READ ONLY transaction.

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver && test "$(id -un)" = gani || { echo 'STOP: WRONG HOST OR USER'; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo 'STOP: DEV CONTAINER DOWN'; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || { echo 'STOP: WRONG DEV COMPOSE PROJECT'; exit 1; }
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev" \
 env FRAPPE_STREAM_LOGGING=1 /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
from pathlib import Path
import subprocess
import frappe

B=Path("/workspace/development/frappe-bench")
for path,expected in (
    (B/"apps/ccpcerp","25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"),
    (B/".ccpc-phase1-release-stage-20261119-55eb10b86a57",
     "55eb10b86a57de55a97e293a78228d9dd17b809a"),
):
    p=subprocess.run(["git","-C",str(path),"rev-parse","HEAD"],
                     capture_output=True,text=True,timeout=20)
    if p.returncode or p.stdout.strip()!=expected:
        raise SystemExit("STOP: SOURCE PIN MOVED")

frappe.init(site="development.localhost",sites_path=".")
try:
    frappe.connect()
    frappe.db.sql("START TRANSACTION READ ONLY")
    p=frappe.db.sql("""
        SELECT COUNT(*) AS missing,
               COALESCE(SUM(CASE WHEN d.name IS NULL THEN 1 ELSE 0 END),0) AS missing_link,
               COALESCE(SUM(CASE WHEN d.name IS NOT NULL
                              AND COALESCE(d.company,'')=''
                         THEN 1 ELSE 0 END),0) AS department_no_company,
               COALESCE(SUM(CASE WHEN d.name IS NOT NULL
                              AND COALESCE(d.company,'')!=''
                         THEN 1 ELSE 0 END),0) AS resolvable
        FROM `tabCCPC Personnel` p
        LEFT JOIN `tabDepartment` d ON d.name=p.department
        WHERE COALESCE(p.company,'')=''
    """,as_dict=True)[0]
    w=frappe.db.sql("""
        SELECT COUNT(*) AS nonpositive,
               COALESCE(SUM(CASE WHEN s.name IS NULL THEN 1 ELSE 0 END),0) AS missing_parent,
               COALESCE(SUM(CASE WHEN s.name IS NOT NULL
                              AND (s.status IS NULL OR s.status NOT IN
                                   ('Stockroom Review','Fully Issued','Issued with Shortage'))
                         THEN 1 ELSE 0 END),0) AS other_status,
               COALESCE(SUM(CASE WHEN s.status='Stockroom Review'
                         THEN 1 ELSE 0 END),0) AS review_status,
               COALESCE(SUM(CASE WHEN s.status IN ('Fully Issued','Issued with Shortage')
                         THEN 1 ELSE 0 END),0) AS issued_status
        FROM `tabWithdrawal Slip Item` i
        LEFT JOIN `tabWithdrawal Slip` s ON s.name=i.parent
        WHERE COALESCE(i.issue_qty,0)<=0
    """,as_dict=True)[0]
    print("PERSONNEL COMPANY MISSING:",int(p.missing))
    print("PERSONNEL DEPARTMENT LINK INVALID:",int(p.missing_link))
    print("PERSONNEL DEPARTMENT COMPANY BLANK:",int(p.department_no_company))
    print("PERSONNEL COMPANY RESOLVABLE:",int(p.resolvable))
    print("WITHDRAWAL ITEMS NONPOSITIVE:",int(w.nonpositive))
    print("WITHDRAWAL ITEMS PARENT MISSING:",int(w.missing_parent))
    print("WITHDRAWAL ITEMS OTHER PARENT STATUS:",int(w.other_status))
    print("WITHDRAWAL ITEMS STOCKROOM REVIEW:",int(w.review_status))
    print("WITHDRAWAL ITEMS ISSUED STATUSES:",int(w.issued_status))
    if int(p.missing)!=3 or int(p.resolvable)!=0 or int(w.nonpositive)!=2:
        raise SystemExit("STOP: LIVE RECORD COUNTS CHANGED")
    print("MAIN DATA EXCEPTION CLASSIFICATION: PASS")
finally:
    try:
        if frappe.db:
            frappe.db.rollback()
    finally:
        frappe.destroy()
print("SOURCE / MIGRATION / SERVICES: UNCHANGED")
PY
HOST
```

**Interpretation / boundary:** If all counts remain consistent, document the remaining data-quality tasks; do not fix Department/Company relations or change Issue Qty without owner-authorized master/stock workflow decisions. Next maintenance gate is queue/user quiescence and two-site-aware stopping/restart/rollback, with protected backup sets and PR33 checkout unchanged. The four aggregate status categories sum to exactly the number of nonpositive items; on any surprising values or STOP marker, investigate read-only first.


## November 19 — Five historical exceptions classified; DEV-only worker/scheduler status gate

**Operator-provided actual classification (explicit READ ONLY SQL on MAIN):**
```text
PERSONNEL COMPANY MISSING: 3
PERSONNEL DEPARTMENT LINK INVALID: 0
PERSONNEL DEPARTMENT COMPANY BLANK: 3
PERSONNEL COMPANY RESOLVABLE: 0
WITHDRAWAL ITEMS NONPOSITIVE: 2
WITHDRAWAL ITEMS PARENT MISSING: 0
WITHDRAWAL ITEMS OTHER PARENT STATUS: 2
WITHDRAWAL ITEMS STOCKROOM REVIEW: 0
WITHDRAWAL ITEMS ISSUED STATUSES: 0
MAIN DATA EXCEPTION CLASSIFICATION: PASS
SOURCE / MIGRATION / SERVICES: UNCHANGED
```

**Decision:** The three MAIN CCPC Personnel links are **valid Department references**, but `tabDepartment.company` is blank for each linked Department. Existing `backfill_ccpc_personnel_company` will not fill these three records without a separate authorized Department/Company business-master decision. The two MAIN Withdrawal Slip Items have valid parents, but both parent statuses are **outside** `Stockroom Review` / `Fully Issued` / `Issued with Shortage`. Existing `backfill_withdrawal_slip_issue_qty` will not update them; no evidence of an invalid stock posting follows from the aggregation alone. They are **outstanding data-quality/workflow questions, not demonstrated migration failures**. Do NOT silently fill Company, choose a stock status, or alter quantities. Record these exceptions for targeted authenticated DEV UAT after source integration. Their unresolved business intent requires separate review before any stock/finance posting that depends on them. The printed `PASS` certifies classification only.

**Next safety gate: check *both* DEV sites' live worker/scheduler/queue overview and obtain operator confirmation that nobody is using the sites before a future DEV-only outage.** The existing deployment operations document `DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md` records that site-scoped `bench doctor` ran successfully after the previous 2026-10-27 DEV maintenance. That command reports registered workers and queue/scheduler diagnostics but does not guarantee every active HTTP request, running job, unsaved user form or transaction is absent. Treat this only as a no-write diagnostic; do not interpret a worker count alone as a safe stop permit. We have **not** stopped Honcho or opened a maintenance window yet.

On the verified original `gani@ccpcerpserver` Ubuntu host:

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver && test "$(id -un)" = gani || { echo "STOP: WRONG HOST OR OPERATOR"; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo "STOP: DEVELOPMENT CONTAINER DOWN"; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || { echo "STOP: WRONG DOCKER PROJECT"; exit 1; }
sudo docker exec --user frappe --workdir /workspace/development/frappe-bench "$dev" bash -lc '
set -euo pipefail
app=apps/ccpcerp
stage=.ccpc-phase1-release-stage-20261119-55eb10b86a57
test "$(git -C "$app" rev-parse HEAD)" = 25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87 || { echo "STOP: LIVE APP HEAD MOVED"; exit 1; }
test "$(git -C "$app" status --porcelain=v1 --untracked-files=all)" = "?? AGENTS.md" || { echo "STOP: LIVE GIT STATUS CHANGED"; exit 1; }
test "$(git -C "$stage" rev-parse HEAD)" = 55eb10b86a57de55a97e293a78228d9dd17b809a || { echo "STOP: STAGED RELEASE MOVED"; exit 1; }
test -z "$(git -C "$stage" status --porcelain=v1 --untracked-files=all)" || { echo "STOP: RELEASE STAGE CHANGED"; exit 1; }
for site in development.localhost ccpc-integration2.localhost; do
  echo "DEV DOCTOR SITE: $site"
  FRAPPE_STREAM_LOGGING=1 bench --site "$site" doctor
done
echo "BOTH DEV SITES BENCH DOCTOR INVOCATIONS: PASS"
echo "NO HONCHO STOP / APP SWITCH / SITE MIGRATION PERFORMED"
'
HOST
```

**Interpretation and further action:** Return the full scheduler/worker/queue diagnostic output with any sensitive user data redacted if unexpectedly printed. If `bench doctor` exits nonzero, reports pending/enqueued/running jobs, no active worker, site exceptions, scheduler errors or a broken-site crossover, STOP for analysis. If both doctor invocations pass, ask the operator explicitly whether **both valid DEV sites are free of active users and unsaved transactions** and whether a DEV-only maintenance outage can start now; this cannot be inferred from the queue diagnostics. Recheck exact stopped Honcho identity immediately before sending a scoped graceful signal. Preserve original PR33 repo `AGENTS.md`, separate release stage, 2-site Nov19 + Nov17 backups and verified NAS copies; never use broad Docker/Compose shutdowns or production services. Full site migration still requires controlled ordered site scope and post-acceptance tests, and the original two-site isolated SQL/files recovery does not prove full app-site recovery.


## November 19 — DEV workers zero with pending jobs: pre-maintenance NO-GO; test Company deletion deferred

**Owner's actual site-scoped `bench doctor` output** (read-only, after previous five-record classification):

```text
DEV DOCTOR SITE: development.localhost
-----Checking scheduler status-----
Workers online: 0
-----development.localhost Jobs-----
Queue: default
Number of Jobs: 18
Methods: frappe.core.doctype.user.user.create_contact : 18
Queue: long
Number of Jobs: 2
Methods: build_index_for_all_routes : 2
DEV DOCTOR SITE: ccpc-integration2.localhost
-----Checking scheduler status-----
Workers online: 0
-----ccpc-integration2.localhost Jobs-----
Queue: long
Number of Jobs: 2
Methods: build_index_for_all_routes : 2
BOTH DEV SITES BENCH DOCTOR INVOCATIONS: PASS
NO HONCHO STOP / APP SWITCH / SITE MIGRATION PERFORMED
```

**Interpretation:** Commands returned success, but current scheduler/queue operational acceptance is **NOT PASS**. Both site-specific diagnostics reported **0 registered online workers** with pending jobs: MAIN 18 User contact creation jobs in default + 2 long route index builds, Integration2 2 long route index builds. Queue counts are **reported per site**; do not assume independent Redis queue ownership or distinct unique jobs until validated (shared bench, shared worker queues). Do not assume jobs are stale or safe to discard, requeue, force-run, purge, or restart anything. These jobs might include delayed user/contact records that must be preserved; another site may be affected by shared queues. Frappe official documentation confirms `bench doctor` reports worker counts and pending tasks; `bench purge-jobs` would delete queued work and is not authorized.

**Maintenance decision:** **HOLD** DEVELOPMENT Honcho shutdown, Stage→live app source swap and both site migrations until present worker processes/Redis queue state, job ages and ownership, queue recovery needs and site user quiescence are reviewed. Specifically avoid `bench purge-jobs`, `docker compose down`, broad Redis flush, force-kill, and premature migration. Protected two-site local/NAS Nov19 and earlier Nov17 backups and original PR33 `AGENTS.md` stay preserved. This is not evidence of a deployment failure: there has not been a Phase1 deployment yet.

**Owner follow-up:** Owner asked `Can i delete the default test company`. No Company name or target site identified, and no delete operation authorized/executed. Company master deletion is **distinct** from ERPNext's `Delete Transactions` action, which is destructive and leaves masters; the latter is not a way to safely remove Company. Ask owner for the **exact Company name and target DEVELOPMENT site**, then perform a site-scoped read-only Company dependency audit (default setting, account/warehouse/cost center and custom CCPC links, transactions/stock/GL), with explicit approval before any master/data removal. Never delete a production Company or clear linked objects merely to bypass Frappe link constraints. Do not clean test Company as a workaround for the backlog or use data cleanup to remove jobs.


## November 19 — Owner proposes MAIN Company cleanup: preserve CCPC/RMC, later add GSL/WFC

**Owner request and evidence:** User screenshots show the ERPNext Company list with **20 of 25** rows currently displayed; the two intended real Companies are **`Cagayan Corn Products Corporation`** (CCPC, PHP, Philippines) and **`Ricor Mills Corporation`** (RMC, PHP, Philippines). Other visible Companies include `_Test Company` variants, `Wind Power LLC`, `Parent Group Company India`, `Child Company US`, `Best Test`, VAT test Companies and `Trial Balance Company`. User intends to **delete all remaining test/demo Companies** and subsequently **add real GSL and WFC Companies**, aiming for 4 real Companies. The screenshot is partial, so **not all 23 deletion candidates are identified or verified**. This aligns with the earlier reported 25 Companies on MAIN `development.localhost`, but the screenshot has no independently confirmed site URL; the following diagnostic is purposely MAIN-only and does not touch Integration2 or PRODUCTION.

**Safety and release boundaries:** No approval to force-delete any accounting/stock transactions, chart-of-accounts, Warehouse, Cost Center, users or GL/SLE records; do not run `Delete Company Transactions`, `bench purge-jobs`, manual SQL `DELETE`, or `ignore_links`. Frappe/ERPNext test code uses `_Test Company`; these fixtures can be required by tests and removing them from the shared MAIN DEV site can disrupt repeatable regression testing. Preserve a separate isolated testing strategy. ERPNext `Delete Company Transactions` deletes transaction records, not Company/master data (official Frappe docs); immutable-ledger restrictions and linked defaults matter. In current DEV, `bench doctor` reported 0 online workers and queued create_contact/route-index jobs, so the Phase1 source cutover and any destructive cleanup remain **ON HOLD** pending review. Do not infer all 25 are disposable from names alone.

**Read-only Stage D1: exact MAIN Company inventory, including parent groups and defaults.** First operator step below does not delete or create anything. It fails if old PR33, independent release stage or total count differ, preserves their respective `AGENTS.md`, and queries only MAIN `tabCompany` and `tabDefaultValue` in a SQL READ ONLY transaction. It prints Company names and group/parent relationships (user is authorized to inspect this MAIN DEV master list), no financial or user data.

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver && test "$(id -un)" = gani || { echo "STOP: WRONG HOST OR OPERATOR"; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo "STOP: DEV CONTAINER DOWN"; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || { echo "STOP: WRONG DEV PROJECT"; exit 1; }
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev" \
 env FRAPPE_STREAM_LOGGING=1 /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
import subprocess
from pathlib import Path
import frappe
B=Path("/workspace/development/frappe-bench")
for path,sha in (
    (B/"apps/ccpcerp","25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"),
    (B/".ccpc-phase1-release-stage-20261119-55eb10b86a57",
     "55eb10b86a57de55a97e293a78228d9dd17b809a"),
):
    p=subprocess.run(["git","-C",str(path),"rev-parse","HEAD"],
                     capture_output=True,text=True,timeout=20)
    if p.returncode or p.stdout.strip()!=sha:
        raise SystemExit("STOP: APP SOURCE COMMIT CHANGED")
keep={"Cagayan Corn Products Corporation","Ricor Mills Corporation"}
frappe.init(site="development.localhost",sites_path=".")
try:
    frappe.connect()
    frappe.db.sql("START TRANSACTION READ ONLY")
    rows=frappe.db.sql(
        "SELECT name,is_group,parent_company,default_currency FROM `tabCompany` ORDER BY name",
        as_dict=True)
    names={x.name for x in rows}
    if len(rows)!=25 or not keep.issubset(names):
        raise SystemExit("STOP: COMPANY COUNT/PROTECTED IDENTITIES CHANGED")
    other=[x for x in rows if x.name not in keep]
    default_values={r[0] for r in frappe.db.sql(
        "SELECT DISTINCT defvalue FROM `tabDefaultValue` WHERE defkey IN ('company','default_company')",
        as_list=True)}
    children={}
    for x in rows:
        if x.parent_company:
            children[x.parent_company]=children.get(x.parent_company,0)+1
    print("MAIN DEV TOTAL COMPANIES:",len(rows))
    print("PROTECTED COMPANIES:",len(keep))
    print("PROPOSED DELETION CANDIDATES:",len(other))
    print("== PRESERVE ==")
    for x in rows:
        if x.name in keep:
            print(x.name,"| currency:",x.default_currency,
                  "| company default:", "YES" if x.name in default_values else "NO")
    print("== CANDIDATES: INVENTORY ONLY, NOT CLEARED FOR DELETION ==")
    for x in other:
        print(x.name,"| group:",int(x.is_group or 0),
              "| children:",children.get(x.name,0),
              "| parent:",x.parent_company or "NONE",
              "| configured default:", "YES" if x.name in default_values else "NO")
    print("COMPANY INVENTORY READ ONLY: PASS")
finally:
    try:
        if frappe.db: frappe.db.rollback()
    finally:
        frappe.destroy()
print("NO COMPANY DELETED / CREATED; NO DEV SERVICE CHANGE")
PY
HOST
```

**Stage D2 (not yet authorized/executed):** After reviewing *all* 23 exact candidates, conduct a per-Company **read-only comprehensive linked-Doctype / GL / SLE / transactional / Company default / child tree / custom CCPC field dependency audit**, and identify ERPNext test fixture dependencies and any queued contacts tied to records before deciding which can be removed. Explicitly preserve legitimate CCPC/RMC Company/Accounts/Cost Centers/Warehouses. Use the ordinary permission/linked-document mechanisms, never `ignore_links`, direct SQL deletion, DB restores or Delete Company Transactions as shortcuts. Any irreversible destructive cleanup needs a separately verified rollback/backups and exact owner approval; GSL/WFC creation separately requires confirmed legal names, abbreviations, currency, country, parent/group status, ledger/inventory defaults and Chart of Accounts, before posting any transaction. No action in PRODUCTION or broken third site.


## November 19 — Corrected Company keep-list: GSL and WFC ALREADY EXIST, 21 not 23 deletion candidates

**Critical correction to earlier provisional two-Company deletion plan:** The owner's full **MAIN DEVELOPMENT** `development.localhost` read-only inventory reported exactly **25 Companies** and printed all 23 outside the original CCPC/RMC keep-list. Among those supposedly disposable records are **`GSL Realty Corporation`** and **`Woodland Farms Corporation`**, plausible matches for intended GSL and WFC; **do not delete these records or recreate duplicate Companies**. Owner should confirm their intended legal identity/abbreviations/currency before promotion as actual Company masters. Revised **provisional** keep-list:
- `Cagayan Corn Products Corporation` — preserve
- `Ricor Mills Corporation` — preserve
- `GSL Realty Corporation` — preserve pending owner's identity confirmation
- `Woodland Farms Corporation` — preserve pending owner's identity confirmation

Thus the proposed cleanup list is now **21 candidates, not 23**, all unapproved for deletion. The owner's inventory reported no currently saved default for any of the original 23 candidates, but this is NOT evidence that they have no accounting, stock, hierarchy or dynamic links. Five of 21 are group Companies: `_Test Company 3` (one child `_Test Company 4`), `_Test Company 4` (one child `_Test Company 5`), `_Test Company 6` (one child `_Test Company 7`), `_Test Company 7` (zero children), `Parent Group Company India` (two children `Child Company India`, `Child Company US`). This parent/child hierarchy forbids arbitrary deletion order. Tests may depend on these fixture names. Do not apply to Integration2 or PRODUCTION. No delete/create action occurred.

**Next Gate D1b: read-only identity + linked-record SCREENING counts for all 25 on MAIN only.** This reports the four provisional keep-record names, abbreviations, countries, currencies and group/parent flags, then per-candidate counts of direct Company references in a fixed list of standard accounting/inventory/procurement documents. It does NOT inspect all Frappe Link/Dynamic Link fields, custom CCPC references or all transactions, and a zero count is **NOT** deletion clearance. `Company` child relationships, saved defaults and exact SHA guards are checked. Run from original host `gani@ccpcerpserver`:

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver && test "$(id -un)" = gani || { echo "STOP: WRONG HOST OR USER"; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo "STOP: DEV CONTAINER DOWN"; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || { echo "STOP: WRONG DEV PROJECT"; exit 1; }
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev" \
 env FRAPPE_STREAM_LOGGING=1 /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
from pathlib import Path
import subprocess
import frappe
B=Path("/workspace/development/frappe-bench")
for directory,sha in (
  (B/"apps/ccpcerp","25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"),
  (B/".ccpc-phase1-release-stage-20261119-55eb10b86a57",
   "55eb10b86a57de55a97e293a78228d9dd17b809a"),
):
    r=subprocess.run(["git","-C",str(directory),"rev-parse","HEAD"],
                     capture_output=True,text=True,timeout=20)
    if r.returncode or r.stdout.strip()!=sha:
        raise SystemExit("STOP: GIT SOURCE PIN CHANGED")
keep={
    "Cagayan Corn Products Corporation",
    "Ricor Mills Corporation",
    "GSL Realty Corporation",
    "Woodland Farms Corporation",
}
tables=(
    "Account", "Cost Center", "Warehouse", "GL Entry", "Stock Ledger Entry",
    "Journal Entry", "Sales Invoice", "Purchase Invoice", "Stock Entry",
    "Payment Entry", "Sales Order", "Purchase Order", "Material Request",
    "Delivery Note", "Purchase Receipt",
)
frappe.init(site="development.localhost",sites_path=".")
try:
    frappe.connect()
    frappe.db.sql("START TRANSACTION READ ONLY")
    rows=frappe.db.sql("""
        SELECT name, abbr, country, default_currency, is_group, parent_company
        FROM `tabCompany` ORDER BY name
    """,as_dict=True)
    names={x.name for x in rows}
    if len(rows)!=25 or not keep.issubset(names):
        raise SystemExit("STOP: MAIN COMPANY INVENTORY CHANGED")
    children={}
    for r in rows:
        if r.parent_company:
            children[r.parent_company]=children.get(r.parent_company,0)+1
    dv=frappe.db.sql("""
        SELECT DISTINCT defvalue FROM `tabDefaultValue`
        WHERE defkey IN ('company','default_company')
    """,as_list=True)
    default_names={x[0] for x in dv}
    qualified=("tab"+t for t in tables)
    available={
        r[0] for r in frappe.db.sql(
          "SELECT TABLE_NAME FROM information_schema.COLUMNS "
          "WHERE TABLE_SCHEMA=DATABASE() AND COLUMN_NAME='company' "
          "AND TABLE_NAME IN ("+",".join(["%s"]*len(tables))+")",
          tuple("tab"+t for t in tables),as_list=True)
    }
    counts={r.name:{} for r in rows}
    for table in tables:
        if "tab"+table not in available:
            continue
        query="SELECT company, COUNT(*) FROM `tab"+table+"` WHERE company IS NOT NULL AND company != '' GROUP BY company"
        for name,n in frappe.db.sql(query,as_list=True):
            if name in counts:
                counts[name][table]=int(n)
    print("MAIN DEV COMPANY INVENTORY:",len(rows))
    print("PROVISIONAL FOUR-COMPANY KEEP LIST:")
    for r in rows:
        if r.name in keep:
            print("KEEP:",r.name,"| abbr:",r.abbr,"| country:",r.country,
                  "| currency:",r.default_currency,"| group:",int(r.is_group or 0),
                  "| parent:",r.parent_company or "NONE",
                  "| selected direct links:",sum(counts[r.name].values()))
    print("COMPANY DELETE CANDIDATES: 21 — SCREENING ONLY")
    for r in rows:
        if r.name in keep: continue
        links=counts[r.name]
        linked=", ".join(t+"="+str(links[t]) for t in tables if links.get(t,0))
        print("CANDIDATE:",r.name,
              "| children:",children.get(r.name,0),
              "| default:",int(r.name in default_names),
              "| direct links:",linked or "NONE IN SCREENED TABLES")
    print("SCANNED TABLES WITH COMPANY COLUMN:",sum("tab"+t in available for t in tables))
    print("MAIN DEV COMPANY IDENTITY + LIMITED LINK SCREEN: PASS")
finally:
    try:
        if frappe.db: frappe.db.rollback()
    finally:
        frappe.destroy()
print("NO COMPANIES / TRANSACTIONS / SERVICES MODIFIED")
PY
HOST
```

**Before any deletion:** This limited survey must be followed by full Doctype Link, Dynamic Link, default-value, nested Company and custom CCPC references plus GL/SLE/Stock/Financial document verification, separately protected backups, test-fixture preservation strategy, human-reviewed explicit 21-Company deletion authorization and an operations plan. Some linked standard Company documents must not be cascaded or force-deleted at all. GSL/WFC **already exist on MAIN**; do not create duplicate names, abbreviations or accounting trees. Existing DEV worker backlog remains ON HOLD (`Workers online: 0` both sites; queued contact creation and route builds). Phase1 maintenance/checkout/migrate is also ON HOLD. No PRODUCTION action.


## November 19 — All four real Companies confirmed in MAIN; every one of 21 cleanup candidates has linked masters

**Owner-provided actual read-only 15-table Company link screening:** 25 Companies total. Protected four `Cagayan Corn Products Corporation` (CCPC), `Ricor Mills Corporation` (RMC), `GSL Realty Corporation` (GSL), and `Woodland Farms Corporation` (WFC) all report `country=Philippines`, `default_currency=PHP`, `is_group=0`, `parent=NONE`. Their selected direct-link record totals were 393, 194, 193 and 193 respectively. These are correct *configured names/abbreviations* but do not independently establish owner legal approval for GSL/WFC.

**All 21 non-protected candidates have Company-linked `tabAccount`, `tabCost Center` and `tabWarehouse` master records**, in most cases about 94–135 Accounts plus 2 Cost Centers and 5 Warehouses. Critically, `_Test Company` has **132 Accounts, 6 Cost Centers, 16 Warehouses, 2 Stock Ledger Entries, 2 Stock Entries, and 2 Material Requests**. The other 20 candidates had no additional direct references among the fifteen screened table `company` columns, but the audit is explicitly LIMITED and cannot prove absence of other DocTypes, Dynamic Links, custom CCPC records or defaults. Group/child dependencies described previously still exist. **Do not delete ANY Company, master or transaction** or use Frappe ignore-links/forced deletion to remove obstacles. The Phase1 cutover remains HOLD due to 0 workers and queued jobs.

**Next read-only linked-reference inventory:** Inspect physical Frappe tables which have a `company` column or are described in DocField/Custom Field metadata as having a `Link` to `Company`. Return aggregate counts for the 21 candidates, plus docstatus distribution of `_Test Company` stock entries and cancellation distribution of its stock ledger entries. *This is extended screening, NOT a complete Delete safety proof*: Dynamic Link records, single-value defaults, arbitrary custom SQL, cross-site test dependencies and indirect references still need a separate examination before deletion. On `gani@ccpcerpserver`, run:

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver && test "$(id -un)" = gani || { echo "STOP: WRONG HOST OR USER"; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo "STOP: DEV CONTAINER DOWN"; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || { echo "STOP: WRONG DEV PROJECT"; exit 1; }
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev" \
  env FRAPPE_STREAM_LOGGING=1 /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
from collections import defaultdict
from pathlib import Path
import subprocess
import frappe

B=Path("/workspace/development/frappe-bench")
for directory,sha in (
    (B/"apps/ccpcerp","25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"),
    (B/".ccpc-phase1-release-stage-20261119-55eb10b86a57",
     "55eb10b86a57de55a97e293a78228d9dd17b809a"),
):
    p=subprocess.run(["git","-C",str(directory),"rev-parse","HEAD"],
                     capture_output=True,text=True,timeout=20)
    if p.returncode or p.stdout.strip()!=sha:
        raise SystemExit("STOP: SOURCE PIN CHANGED")
keep={"Cagayan Corn Products Corporation","Ricor Mills Corporation",
      "GSL Realty Corporation","Woodland Farms Corporation"}

def qid(s):
    return "`"+s.replace("`","``")+"`"

frappe.init(site="development.localhost",sites_path=".")
try:
    frappe.connect()
    frappe.db.sql("START TRANSACTION READ ONLY")
    names=[x[0] for x in frappe.db.sql("SELECT name FROM `tabCompany` ORDER BY name")]
    if len(names)!=25 or not keep.issubset(names):
        raise SystemExit("STOP: COMPANY INVENTORY CHANGED")
    targets=[x for x in names if x not in keep]
    if len(targets)!=21:
        raise SystemExit("STOP: CANDIDATE COUNT CHANGED")
    cols=defaultdict(set)
    for table,col in frappe.db.sql(
        "SELECT TABLE_NAME,COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME LIKE 'tab%'",
        as_list=True):
        cols[table].add(col)
    links=frappe.db.sql("""
        SELECT parent,fieldname FROM `tabDocField`
        WHERE fieldtype='Link' AND options='Company'
        UNION
        SELECT dt,fieldname FROM `tabCustom Field`
        WHERE fieldtype='Link' AND options='Company'
    """,as_list=True)
    fields={(t,"company") for t,cc in cols.items() if "company" in cc}
    fields.update(("tab"+dt,field) for dt,field in links
                  if dt and field and field in cols.get("tab"+dt,set()))
    results=defaultdict(list)
    params=tuple(targets)
    for table,field in sorted(fields):
        sql=("SELECT "+qid(field)+",COUNT(*) FROM "+qid(table)+" WHERE "
             +qid(field)+" IN ("+",".join(["%s"]*len(targets))+") GROUP BY "+qid(field))
        for value,n in frappe.db.sql(sql,params,as_list=True):
            results[value].append((table[3:],field,int(n)))
    print("MAIN DEV PROTECTED COMPANY COUNT:",len(keep))
    print("MAIN DEV CLEANUP CANDIDATES:",len(targets))
    print("PHYSICAL COMPANY-LINK FIELD PAIRS SCANNED:",len(fields))
    for name in targets:
        matches=results.get(name,[])
        masters=[(dt,n) for dt,field,n in matches
                 if dt in {"Account","Cost Center","Warehouse"} and field=="company"]
        other=[dt+"."+field+"="+str(n) for dt,field,n in matches
               if not (dt in {"Account","Cost Center","Warehouse"} and field=="company")]
        print("CANDIDATE:",name)
        print("  ACCOUNT/COST CENTER/WAREHOUSE DIRECT COUNTS:",
              " ".join(dt+"="+str(n) for dt,n in masters) or "NONE")
        print("  OTHER DIRECT COMPANY REFERENCES:",
              ", ".join(other) or "NONE FOUND IN SCANNED FIELDS")
    if "tabStock Entry" in cols and {"company","docstatus"}.issubset(cols["tabStock Entry"]):
        print("TEST COMPANY STOCK ENTRY DOCSTATUS COUNTS:",
              frappe.db.sql("""
                  SELECT docstatus,COUNT(*) FROM `tabStock Entry`
                  WHERE company=%s GROUP BY docstatus ORDER BY docstatus
              """,("_Test Company",),as_list=True))
    if "tabStock Ledger Entry" in cols and "company" in cols["tabStock Ledger Entry"]:
        if "is_cancelled" in cols["tabStock Ledger Entry"]:
            print("TEST COMPANY STOCK LEDGER CANCELLATION COUNTS:",
                  frappe.db.sql("""
                      SELECT is_cancelled,COUNT(*) FROM `tabStock Ledger Entry`
                      WHERE company=%s GROUP BY is_cancelled ORDER BY is_cancelled
                  """,("_Test Company",),as_list=True))
        else:
            print("TEST COMPANY STOCK LEDGER is_cancelled COLUMN: NOT PRESENT")
    print("EXTENDED MAIN COMPANY DIRECT-LINK AUDIT: PASS")
finally:
    try:
        if frappe.db:
            frappe.db.rollback()
    finally:
        frappe.destroy()
print("NO COMPANY / LEDGER / SERVICE MODIFICATION")
PY
HOST
```

**Guardrail:** This covers physical `company` columns and declared direct Link→Company fields, not all dynamic/indirect links or every accounting constraint. The `Stock Ledger Entry` entries warrant particular care; never erase/modify these to make a Company deletable. Record output and evaluate deeper dependencies before an explicit, separately authorized cleanup plan. No PRODUCTION or Integration2 cleanup. Worker backlog/Phase1 source-switch HOLD remains a separate problem.


## November 19 — Extended Company-link audit PASS; active test stock ledger: NO-GO for immediate 21-Company purge

**Owner's actual latest MAIN DEVELOPMENT read-only output:**
- `MAIN DEV PROTECTED COMPANY COUNT: 4`, `MAIN DEV CLEANUP CANDIDATES: 21`, `PHYSICAL COMPANY-LINK FIELD PAIRS SCANNED: 167`. This was a read-only scan of physical `company` fields and DocField/Custom Field Link→Company declarations, **not** a full Dynamic Link or informal reference audit.
- All 21 candidates have `Account`, `Cost Center`, `Warehouse`, `Department`, `Mode of Payment Account` and `Process Deferred Accounting` references. Many also have Item Tax Templates, Purchase/Sales Taxes and Charges Templates and other Item/Party/Asset links. `_Test Company 3/4/6` and `Parent Group Company India` have nested `Company.parent_company` and `Company.existing_company` references. `_Test Company with perpetual inventory` has `Customer.represents_company`, `Supplier.represents_company` and `Allowed To Transact With` links.
- **`_Test Company`: 132 Accounts, 6 Cost Centers, 16 Warehouses plus Asset/Item/Department/Tax references, 2 `Stock Entry` records with `docstatus=1` (submitted), and 2 `Stock Ledger Entry` records with `is_cancelled=0` (noncancelled). It also has 2 `Material Request` records and 3 `Bin` references.** The owner reported `TEST COMPANY STOCK ENTRY DOCSTATUS COUNTS: [[1, 2]]` and `TEST COMPANY STOCK LEDGER CANCELLATION COUNTS: [[0, 2]]`.
- Final terminal markers `EXTENDED MAIN COMPANY DIRECT-LINK AUDIT: PASS` and `NO COMPANY / LEDGER / SERVICE MODIFICATION`. This confirms only the scoped read-only inspection completed, not any delete readiness.

**Safety ruling and available non-destructive route:**
1. **Do not execute bulk Company deletes or linked master cascade deletes in MAIN.** The two submitted Stock Entries and noncancelled SLE history must not be deleted or edited via SQL, Frappe `ignore_links`, `bench purge-jobs`, direct Journal/GL/SLE manipulation, broad `Delete Company Transactions`, or a global `Delete Transactions` option. Official ERPNext docs `docs.frappe.io/erpnext/delete_company_transactions` and `docs.frappe.io/erpnext/immutable-ledger-in-erpnext` describe, respectively, the destructive per-Company transaction removal mechanism (masters stay) and traceable immutable stock/accounting history. Do not infer that cancelling submitted test records is necessarily permitted or sufficient: stock valuation, later movements, and linked documents may constrain corrections.
2. Preserve the **four actual** MAIN Company records `Cagayan Corn Products Corporation` (CCPC), `Ricor Mills Corporation` (RMC), `GSL Realty Corporation` (GSL), `Woodland Farms Corporation` (WFC): all Philippines/PHP, non-group, parent NONE. Do not create duplicate GSL/WFC; no Company creation is required for this four-Company list.
3. For a **clean four-Company user-facing environment**, first design an independently backed-up, explicitly authorized **isolated DEVELOPMENT/UAT site/bench** (not an existing third broken `ccpc-integration.localhost`, and not PRODUCTION) that can be provisioned without altering the shared live DEV database, current app checkout, original PR33 `AGENTS.md`, or staged Phase1 release. Do not assume simply copying Company rows carries safe Chart of Accounts, item defaults, customer/supplier relations, permissions, or already approved mappings; site setup and data movement need a separate migration/validation plan.
4. If the owner instead requires deleting existing 21 records in MAIN, prepare a separate **destructive cleanup plan** including a full dependency graph of Link/Dynamic Link/Single defaults/child tables/test fixtures, stock and accounting transaction review and closure rules, isolated full-site restore validation, staged child-to-parent deletion with scoped approvals, and a realistic failure/recovery plan. A superficial absence of a link in 167 screened field pairs cannot authorize deletion.
5. **Phase1 DEV cutover remains ON HOLD** due to 0 online workers and queued `create_contact` / `build_index_for_all_routes` jobs in shared DEV. No server operations, app source activation, site migration or new Company/master setup occurred in this exchange, and no PRODUCTION changes are authorized.

**Immediate next decision:** The owner should select **preserve test history + prepare separate clean four-Company UAT environment** (recommended) or **design a high-risk, separately approved in-place MAIN cleanup**. The current evidence does not justify running Company deletion commands in either case.
