# Phase 1 — approved shared-bench DEVELOPMENT integration and recovery-controlled cutover

**Prepared:** 2026-11-19, Asia/Manila. **Status:** DEV-only integration approved by owner; *pre-cutover read-only discovery is next, code switch and migration have NOT been performed*. This is an operator-reviewed, one-gate-at-a-time workflow; do not combine gates into a blind script.

## Authorized scope and source authority

The owner approved continuing the actual **DEVELOPMENT-only maintenance and Phase 1 integration** after the two-site local+Synology backups and isolated SQL+file restores passed. This permits controlled DEV-only planning, staging and a planned maintenance window, but **does not authorize** accessing, changing or stopping either PRODUCTION environment. Live site migrations and wide after-migrate hooks are risk-bearing and must pass the new pre-cutover and recovery gates before execution. A host-side operator is needed; ChatGPT cannot run commands directly on \`ccpcerpserver\`.

**Latest GitHub verified source at preparation:**
- Release: \`ccpcerp/ccpcerp\` \`release/withdrawal-department-phase1-2026-11-17\` exact commit **\`55eb10b86a57de55a97e293a78228d9dd17b809a\`** (PR #38 and #39 merged).
- Original, separately preserved PR33 branch: \`review/billing-authorization-correction-2026-11-03\` exact **\`25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87\`**.
- Divergence at this checkpoint: Phase1 release 18 release-only vs PR33 44 PR33-only commits. **Never merge full PR33 into Phase 1.**
- Existing DEV bench \`/workspace/development/frappe-bench\`, app dir \`apps/ccpcerp\`, known detached PR33 commit above and exactly untracked protected \`?? AGENTS.md\`. The released Phase1 tree **tracks** root \`AGENTS.md\`. Never force-checkout, \`git reset --hard\`, \`git clean\`, blind \`git pull\`, delete or overwrite the owner's local \`AGENTS.md\`.
- \`ccpcerp/patches.txt\` matches between the branches, but release \`hooks.py\` and \`setup.after_migrate()\` differ. Release \`before_migrate\` bootstraps executive and Finance mapping role definitions; \`after_migrate\` runs existing foundation, personnel, MRS/PO, permission/workflow, stock-field and withdrawal-quantity backfill operations. Page \`ccpc-phase1-finance\` and its roles require sync. This is **not** a Page-only migration; review patch log, company/account masters and record-side effects per site.
- Phase 1 **same-Company-only** issuance and **intercompany billing disabled** must stay enforced; PR33's active billing maker/checker/invoice flow remains unreleased.
- Both valid sites \`development.localhost\` (MAIN) and \`ccpc-integration2.localhost\` share this installed app's Python import path, verified in the live owner probe. The broken \`ccpc-integration.localhost\` exists and must **not** be connected, migrated or swept by \`--site all\` or unrestricted schedulers.

## Gate A: exact current *read-only* pre-cutover inventory — execute now

The first operator step is intentionally non-mutating: it discovers whether the exact release commit already exists as a local Git object, what fetch transport is configured, and the current Honcho process identity. It also verifies the three protected backup snapshot directories, the valid sites and the detached live PR33 checkout. It does not fetch code, stop processes, touch Frappe/SQL, invoke a site import, read secrets, or run migration.

Run at \`gani@ccpcerpserver\`:

\`\`\`bash
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
\`\`\`

**Stop on unexpected output.** Send only the printed PASS/STOP/status lines (no site configs, credentials, SQL files or raw \`git remote\` URLs). Release object availability, credential-safe Git transport, and Honcho PID are needed to choose the next stage.

## Gate B — isolated release staging (after Gate A passes; no live code activation)

**Candidate mechanism:** A fully independent \`git clone --no-hardlinks --no-checkout\` of the existing application into a uniquely named hidden staging directory on the **same underlying DEV workspace filesystem**, then checkout \`--detach\` at the exact pinned release SHA; verify \`git rev-parse HEAD\`, \`git status\` and branch, and that root \`AGENTS.md\` is from tracked release source. Never include the original untracked \`AGENTS.md\` in this staging clone. The stage directory must not replace the live application, install packages, sync assets or point any running Frappe workers at different code. Stage/source availability is contingent on the release commit object and remote tracking discovered at Gate A; if absent, fetch only through an explicitly inspected safe Git transport without displaying tokens. Do not assume default branch or use floating SHA.

## Gate C — protected DEV-only maintenance, code switch and migration

1. Obtain an uncontested DEVELOPMENT maintenance window. Both valid sites may be unavailable because their code is shared. Identify actual current Honcho process identity, children, scheduled jobs and potential third-site scheduler behavior. Do not reuse historical PID 193 or PID 380905; do not kill arbitrary processes, restart Docker/Compose, or touch legacy PRODUCTION resources.
2. Verify the matching exact-code original checkout and staging clone with fresh hashes and both backup manifests; preserve Nov19 + older Nov17 snapshot sets and owner-controlled \`AGENTS.md\`. Before stopping anything, document a bounded rollback and potential need for **database/file restore**, not just source rename, if migration writes schema/data.
3. After safe DEVELOPMENT-only process stop, prefer an atomic same-filesystem directory rename of the **entire** old application checkout to a unique, protected sibling path and the **independent staging clone** into the original \`apps/ccpcerp\` path; no direct \`git checkout\` in the old repo, no overwrite of its untracked \`AGENTS.md\`, and no reuse of the old app's original \`.git\` as the release repo's worktree. Re-verify \`ccpcerp\` Python import origin and exact release commit without starting services.
4. Run separately targeted \`bench --site ccpc-integration2.localhost migrate\` then \`bench --site development.localhost migrate\` only **after** verifying actual app/backend version compatibility, the complete \`setup.after_migrate()\` effect list, SQL patch-log/master prerequisites and FINANCE onboarding/permissions. Migration may modify both sites' databases and metadata, and may fail; if it fails, **stop** and follow the recovery procedure—not a blind Git reset, migration retry or \`--site all\`. Never migrate \`ccpc-integration.localhost\`.
5. After both valid sites pass schema/role/Page checks, restart **only named DEV Honcho-managed processes**, validating that the scheduler does not accidentally enumerate and fail on broken third site before enabling routine scheduling; check HTTP, queue/worker, site routing, UAT and Finance maker/checker permissions. Do not infer health just from HTTP 200.
6. If source switch fails **before any migration**, a guarded two-directory rollback can restore prior app source. If migration fails/partially completes, code-only rollback is insufficient: preserve original, assess DB transactional effects, and use the separately scoped exact backup restore procedure only with verified site targets and explicit operator approval. No automated restore or destructive recovery shortcut is authorized.

**No actual Gate B/C execution has occurred yet.** The staged plan is not proof that installed package paths, full Frappe site boot or live business transactions will succeed; those are DEVELOPMENT acceptance checks after safe execution.
