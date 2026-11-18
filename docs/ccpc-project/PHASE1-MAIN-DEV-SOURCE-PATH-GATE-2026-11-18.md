# CCPC Phase 1 — MAIN DEVELOPMENT source-path and staging gate

**Date:** 2026-11-18 Asia/Manila. **Status:** Source and runbook preparation only; no host operation performed. **Target:** `ccpcerpserver` old-host DEVELOPMENT container `frappe_docker_devcontainer-frappe-1`; **exclude** old retained PRODUCTION and separate `ccpcerp-prod`.

## Why this gate is needed

- Approved merged Phase 1 app release is `ccpcerp/ccpcerp` branch `release/withdrawal-department-phase1-2026-11-17`, exact HEAD `55eb10b86a57de55a97e293a78228d9dd17b809a` (includes PR #38 Finance onboarding, PR #39 Phase 1 guard tests and runbook).
- Current shared MAIN DEV checkout is detached PR33 `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87` with only protected untracked `?? AGENTS.md`; its history diverges from Phase 1. The release **tracks** a different root `AGENTS.md`. Do not `git checkout`/`pull`/`reset`/`clean`/`stash` in the shared checkout or overwrite/remove the untracked file.
- The existing DEV bench serves `development.localhost` and `ccpc-integration2.localhost` with **one shared app code installation**. Merely applying `bench --site development.localhost migrate` does **not** prevent source imports in the other site from changing. A new staging Git worktree in another directory does not by itself change where Python imports the installed app.
- `ccpc-integration.localhost` is a known incomplete site; never use `--site all`, unrestricted scheduler/start, or broad restarts to bypass it.
- Release and PR33 have **identical `ccpcerp/patches.txt` blob** `42cd0635e2d6ccb5464f98de6377105e9c93bf1d`; this does **not** mean migration is no-op. Release `ccpcerp/hooks.py` blob `28e8b5d8bf03a9f2ce0b9c75f555978227f0c411` differs from PR33 `816afe85a64e743dec843c7a86531a6fb2818f18`, and PR33 `setup.py` adds the separately unreleased Billing Preparer role to `after_migrate`. The release `setup.after_migrate()` still changes Foundation, MRS, personnel, permissions, procurement workflow, withdrawal stock fields/workflow and issue quantities; Page/Role sync will also happen.
- Four-part MAIN DEV Nov 17 backup hashes verified **local 4/4 PASS, Synology 4/4 PASS, matching**. No independent restored copy validated and a new snapshot as of this deployment is not yet taken. Older one-shot backup scripts pin specific billing business state and must **not** be rerun.

## First operation: single bounded READ-ONLY import/checkout identity probe

Execute only as the human operator `gani` on `ccpcerpserver`. This calls the verified, running DEV Frappe container as non-root user `frappe` and the bench virtualenv Python **without initializing a Frappe site or reading site configuration content**. It does not access production, databases, remote Git, or private SSH material. Run only if the hostname and Compose identity are unchanged.

```bash
set -euo pipefail
test "$(hostname -s)" = "ccpcerpserver" || { echo "STOP: HOST"; exit 1; }
test "$(id -un)" = "gani" || { echo "STOP: OPERATOR"; exit 1; }
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || { echo "STOP: DEV NOT RUNNING"; exit 1; }
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = "frappe_docker_devcontainer" || { echo "STOP: WRONG COMPOSE PROJECT"; exit 1; }
sudo docker exec -i --user frappe --workdir /workspace/development/frappe-bench/sites "$dev" /workspace/development/frappe-bench/env/bin/python -B - <<'PY'
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

BENCH = Path("/workspace/development/frappe-bench")
APP = BENCH / "apps/ccpcerp"
EXPECTED = "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"

def must(ok, label):
    if not ok:
        raise SystemExit("STOP: " + label)

def git(*args, ok=True):
    r = subprocess.run(["git", "-C", str(APP), *args],
                       capture_output=True, text=True, timeout=30)
    if ok:
        must(r.returncode == 0, "GIT " + args[0])
    return r

must(Path.cwd() == BENCH / "sites", "BENCH WORKDIR")
must(APP.is_dir() and not APP.is_symlink(), "APP ROOT")
must(git("rev-parse", "--show-toplevel").stdout.strip() == str(APP), "GIT ROOT")
must(git("rev-parse", "HEAD").stdout.strip() == EXPECTED, "APP COMMIT CHANGED")
must(git("symbolic-ref", "-q", "--short", "HEAD", ok=False).returncode == 1, "APP NOT DETACHED")
must(git("status", "--porcelain=v1", "--untracked-files=all").stdout.strip() == "?? AGENTS.md", "WORKTREE DIRTY OR PROTECTED FILE CHANGED")
protected = APP / "AGENTS.md"
must(protected.is_file() and not protected.is_symlink(), "PROTECTED AGENTS")
must(not git("ls-tree", "-r", "--name-only", "HEAD", "--", "AGENTS.md").stdout.strip(), "AGENTS TRACKED UNEXPECTEDLY")
for site in ("development.localhost", "ccpc-integration2.localhost", "ccpc-integration.localhost"):
    must((BENCH / "sites" / site / "site_config.json").is_file(), "SITE CONFIG PRESENCE " + site)

spec = importlib.util.find_spec("ccpcerp")
must(spec is not None and spec.origin, "CCPC PYTHON IMPORT NOT FOUND")
actual = Path(spec.origin).resolve()
wanted = (APP / "ccpcerp/__init__.py").resolve()
must(actual == wanted, "CCPC PYTHON IMPORT IS NOT LIVE APP")
must(Path(sys.executable).name.startswith("python"), "PYTHON INTERPRETER")

print("PR33 DETACHED SOURCE: VERIFIED")
print("TRACKED SOURCE: CLEAN")
print("PROTECTED LOCAL AGENTS.md: PRESERVED")
print("THREE SITE CONFIGS: PRESENT (NOT CONNECTED)")
print("BENCH CCPC IMPORT PATH: POINTS TO SHARED APP")
print("READ-ONLY SOURCE PATH GATE: PASS")
PY
```

**STOP if any gate fails.** Do not bypass by changing the expected HEAD or source path. Output only these safe markers, not Frappe configuration, account data, SSH material, site DB names, or raw environment variables. The probe may fail if the editable package is installed differently; review the installation layout before changing anything.

## Next DEVELOPMENT progression, write gates not authorized by this document

1. Interpret exact import path and compare host / container bind-mount topology (privileged SSH mount is a risk to agents, so no Codex on the existing DEV container). A staging *source* checkout in a separately approved path must be isolated from the running shared bench. Never assume a new worktree is equivalent to switching the actual Frappe app.
2. Before applying new source on MAIN, arrange a maintenance strategy for **both** sites sharing app code, including broken-third-site scheduler behavior, and verify whether a separately isolated bench is required. Preserve PR33 on its GitHub branch and the existing `AGENTS.md`.
3. Near the exact approved deployment, take a **new** four-artifact `development.localhost` backup (DB, site_config, public, private) with a separate, checksum-verified Synology copy and retained Nov17 checkpoint. Validate rollback and if possible isolated restore; do not reuse Nov17 one-shot backup scripts unchanged.
4. Obtain separately scoped approval for DEV source switching, site-specific migration (and broad `setup.after_migrate` side effects), role/Page synchronization and synthetic UAT. Give real Finance masters and independent named mapping maker/checker the required authentic signoff. No real data modifications without this gate.
5. No modifications to old retained PRODUCTION or the physically separate `ccpcerp-prod`. The local Codex agent stays stopped while outbound isolation remains unverified.

**Evidence levels:** This document is a vetted **plan** and contains a read-only diagnostic; it does not assert that this probe, a fresh backup, restore, migration, or live UAT has been executed.


## November 18 — live operator result: ALL SIX GATES PASS

**Evidence:** The operator ran the exact guarded read-only command on the legacy `ccpcerpserver` DEVELOPMENT container and returned the complete output:

```text
PR33 DETACHED SOURCE: VERIFIED
TRACKED SOURCE: CLEAN
PROTECTED LOCAL AGENTS.md: PRESERVED
THREE SITE CONFIGS: PRESENT (NOT CONNECTED)
BENCH CCPC IMPORT PATH: POINTS TO SHARED APP
READ-ONLY SOURCE PATH GATE: PASS
```

**Interpretation:** The persistent bench's Python resolves `ccpcerp` through `/workspace/development/frappe-bench/apps/ccpcerp` at detached PR33 commit `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`, with only protected untracked `AGENTS.md`. This is **operator-reported execution**, not direct ChatGPT remote access. No active DB connection, backup, live site action or PRODUCTION change occurred. **Further repeating the import-path read-only probe is unnecessary unless source/bench changes.**

**Decision for next gate:** Do **not** treat a separate Git clone/worktree as deployment: the same bench imports the old checkout and serves both `development.localhost` and `ccpc-integration2.localhost`. A real code activation will change imports for both sites and requires a **DEV-only maintenance window** or genuinely independent bench. Before such a switch, prepare (and separately authorize execution of) **new, same-window, uniquely named** four-part backups for both affected sites; preserve the Nov17 original local/NAS sets, never reuse the Nov17 one-shot marker scripts, confirm source SHA and exact target list, and create SHA256-confirmed off-host NAS copies. Backups are data-bearing writes to backup storage; owner approval for read-only probing alone did not authorize them.

**Unresolved deployment design:** Need safe import/checkout transition without overwriting untracked `AGENTS.md`, release-tracked `AGENTS.md` collision handling, a defined pre-switch PR33 return path, explicit protection of Integration2 from Phase 1 metadata incompatibility, reviewed `setup.after_migrate` effects, site-specific schema transition, and safe rollback/recovery. Prefer the simplest verified DEVELOPMENT-only maintenance plan; do not restart shared services or migrate the broken third site simply to accelerate integration. Checkpoint remains GitHub-only until the owner approves actual backup and source operations.
