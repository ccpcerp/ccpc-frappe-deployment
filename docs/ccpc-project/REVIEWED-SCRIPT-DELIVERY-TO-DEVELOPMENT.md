# CCPC ERPNext — Reviewed GitHub-to-DEVELOPMENT script delivery

**Approved by the owner on 2026-10-15.** This procedure replaces repeated Windows browser download → PowerShell SCP transfers **for newly authorized, reviewed operator scripts** when Ubuntu's access to the private GitHub repository is confirmed. It **does not** grant ChatGPT SSH access or let commits execute automatically. The operator retains the final execution step.

## Scope and prohibited actions

- **GitHub is the authoritative source** for committed script bytes and application code; this document is a delivery/runbook procedure, **not** an authorization to run an unrelated script, repeat a one-shot diagnostic, submit stock/GL, change accounts, migrate, restore, or deploy.
- DEVELOPMENT and PRODUCTION share a host; never use this workflow to modify PRODUCTION, its containers, databases, credentials, configuration or backups.
- Never switch branch, reset, stash, pull, fetch into, or otherwise alter the persistent DEVELOPMENT application's protected checkout. Preserve untracked `AGENTS.md`. Use a **separate, private staging directory** in the operator's home, not the bench or app directories.
- No GitHub push-triggered execution, self-hosted GitHub Actions runner, cron auto-executor, unaudited agent, unrestricted SSH delegation, paid API service or stored server secrets. Never pipe remote script content directly to `bash`.
- Script review must exclude credentials, database exports, site_config, production records, secrets, sensitive endpoint configuration, unreviewed instructions, backups and unnecessary logs. Both CCPC repositories were verified private on 2026-10-15; private visibility is **necessary but not sufficient** for storing an operational script.
- Explicit task-level approval is still required before any business-data write or other high-risk operation. A previously used one-shot filename, even with the same checksum, must **not** be run again. A fresh review and new consent are required for each distinct mutating test.

## Phase 1 — verify Ubuntu's existing *read-only* access before rollout

Log into the **Ubuntu host** as the normal operator (not root) and run this **single nonmutating command**:

```bash
GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10' git ls-remote git@github.com:ccpcerp/ccpc-frappe-deployment.git refs/heads/docs/ccpc-checkpoint-2026-10-10
```

Expected: one line ending `refs/heads/docs/ccpc-checkpoint-2026-10-10`, with a 40-character commit hash (which is **not** the application's feature commit). If authentication fails, a trusted `known_hosts` key is missing, or the output is empty, **stop** and report the safe error text. Do not disable SSH host verification, copy private SSH keys into ChatGPT, insert a GitHub token into shell commands/URLs, paste verbose credential output, or assume an HTTPS clone will authenticate. We can separately assess an already-installed credential helper or read-only GitHub deploy key after observing this check; credential changes require their own approval and careful separation from PRODUCTION.

The command runs `git ls-remote` against a private repo and neither writes files locally nor alters Git branches. Only the operator performs this test; ChatGPT cannot reach the private `192.168.50.166` server directly through the GitHub connector.

## Access checkpoint: Ubuntu GitHub SSH probe PASSED — 2026-10-15

**Operator-returned evidence:** Running the exact Phase 1 `git ls-remote` from `gani@ccpcerpserver` returned
```text
27b37bd25f10c0568a668f8bd608dc38b2111f23        refs/heads/docs/ccpc-checkpoint-2026-10-10
```
The connected GitHub tool independently verified the **same** branch HEAD `27b37bd25f10c0568a668f8bd608dc38b2111f23` at the time of the operator test. Noninteractive SSH authentication and strict host-key checking thus succeeded for this private repository **at that moment**, without a new token/key change. **Note:** this branch HEAD may advance as documentation is updated; do not permanently pin it for all future script downloads. This proves repository advertisement/readability, **not** permission to execute anything or that every future `git fetch` will succeed; stage the first reviewed future artifact by exact SHA and verify it on Ubuntu before claiming the full delivery path is tested.

**Current gate:** Phase 1 complete. Phase 2 requires a **new sanitized, expressly reviewed and approved operator script** committed with exact file/commit SHA; no already-consumed Material Issue diagnostic is eligible for replay. No server code run, new script staged, branch checkout modified, cron/runner installed, or PRODUCTION operation performed by this access verification.


## Phase 2 — review and publish a newly authorized script

1. Review the exact source and permissions, business/transaction scope, backup preconditions, rollback/failure handling and disallowed side effects. Store only the sanitized script in a reviewed branch of `ccpcerp/ccpc-frappe-deployment` (a separate path for operator artifacts, not custom application source). A GitHub commit of documentation/scripts is **not** a deployment or execution approval.
2. Fetch the committed blob back through the GitHub connection, verify its text matches the reviewed source, and record **full 40-character commit SHA**, **repository-relative path**, **64-hex SHA256 of the file's exact UTF-8 bytes**, source branch and one-shot execution scope in the current handoff. Keep secrets and exported archives outside GitHub.
3. Before each run, inspect relevant GitHub commits and obtain the **separate explicit consent for that one operation**, stating the target isolated site, expected mutation or rollback-only behavior, and what to do after failure.
4. The operator stages the file using the authenticated Git channel without changing the live DEVELOPMENT checkout. An independently staged file must **not** be executed before the pinned SHA256 comparison succeeds. Use an exclusive filename and owner-only permissions; stop rather than overwriting any prior file.

## Phase 3 — isolated staging pattern (only after Phase 1 PASS)

This template is for a **future approved script that has actually been committed and pinned**. Set the four upper-case values to the exact facts supplied with that script. It stages the file **but deliberately does not execute it**:

```bash
set -euo pipefail
umask 077
APPROVED_BRANCH='REPLACE-WITH-REVIEWED-BRANCH'
APPROVED_COMMIT='REPLACE-WITH-FULL-40-HEX-COMMIT'
APPROVED_PATH='REPLACE-WITH-REPO-RELATIVE-PATH'
APPROVED_SHA256='REPLACE-WITH-FILE-64-HEX-SHA256'
# Validate every pin and restrict scripts to the designated reviewed directory.
[[ "$APPROVED_COMMIT" =~ ^[0-9a-f]{40}$ ]]
[[ "$APPROVED_SHA256" =~ ^[0-9a-f]{64}$ ]]
[[ "$APPROVED_BRANCH" =~ ^[a-zA-Z0-9._/-]+$ ]]
[[ "$APPROVED_BRANCH" != *..* && "$APPROVED_BRANCH" != /* && "$APPROVED_BRANCH" != *//* ]]
[[ "$APPROVED_PATH" =~ ^scripts/development/operator/[a-zA-Z0-9._/-]+[.]sh$ ]]
[[ "$APPROVED_PATH" != *..* && "$APPROVED_PATH" != /* && "$APPROVED_PATH" != *//* ]]
OUT_DIR="$HOME/ccpc-reviewed-scripts"
REPO_URL='git@github.com:ccpcerp/ccpc-frappe-deployment.git'
mkdir -p -m 700 "$OUT_DIR"
TMP_DIR="$(mktemp -d "$OUT_DIR/.fetch.XXXXXXXX")"
GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10' git -C "$TMP_DIR" init -q
GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10' git -C "$TMP_DIR" fetch -q --depth=1 --no-tags "$REPO_URL" "refs/heads/$APPROVED_BRANCH"
test "$(git -C "$TMP_DIR" rev-parse FETCH_HEAD)" = "$APPROVED_COMMIT"
FILE_NAME="$(basename -- "$APPROVED_PATH")"
test ! -e "$OUT_DIR/$FILE_NAME"
MODE="$(git -C "$TMP_DIR" ls-tree FETCH_HEAD -- "$APPROVED_PATH" | awk '{print $1}')"
[[ "$MODE" = '100644' || "$MODE" = '100755' ]]  # Reject symlinks/submodules.
STAGED_TEMP="$(mktemp "$OUT_DIR/.stage.XXXXXXXX")"
git -C "$TMP_DIR" show "FETCH_HEAD:$APPROVED_PATH" > "$STAGED_TEMP"
test "$(sha256sum "$STAGED_TEMP" | cut -d' ' -f1)" = "$APPROVED_SHA256"
chmod 600 "$STAGED_TEMP"
ln -- "$STAGED_TEMP" "$OUT_DIR/$FILE_NAME" # Fails if destination exists.
rm -- "$STAGED_TEMP"                   # Removes only our verified temporary filename.
printf 'STAGED AND VERIFIED, NOT EXECUTED: %s\n' "$OUT_DIR/$FILE_NAME"
```

**Review note:** The template intentionally leaves its dedicated hidden `.fetch.*` repository for operator inspection instead of deleting anything automatically; tidy only those exact owned temporary folders later under a separately reviewed housekeeping step. The `APPROVED_PATH` must be reviewed as an exact relative path under `scripts/development/operator/`; the staged file basename must be unique. The template checks the branch, pinned commit, file SHA256 and blob mode, and rejects `..`, leading `/`, untrusted refs and symlink blobs. If staging fails or an existing output file is present, stop and do not execute. This is a manually reviewed template, not a hardened installed fetch service. **Do not paste placeholder values as executable instructions.**

## Phase 4 — separate manual execution

Only after a successful staging confirmation, explicit one-operation authorization, and review of the run's current prerequisites may the operator run an exact `bash "$HOME/ccpc-reviewed-scripts/<approved-new-script-name>"` command. Check all error/output lines. Never auto-retry. The agent must record **operator-reported**, independently supported PASS/STOP results in GitHub, distinguishing transactional rehearsal from committed business effects. No background scripts, automatic deployment or server access is created by this runbook.

## Current status — FIRST READ-ONLY DELIVERY AND EXECUTION VERIFIED (2026-10-15)

- The owner approved the **GitHub-to-DEVELOPMENT delivery workflow**. Noninteractive SSH `git ls-remote` to the private deployment repository **PASSED** with strict host-key checking.
- A new read-only script and preparation plan were published on `review/material-issue-first-commit-preparation-2026-10-15`, exact reviewed commit `d7e1d0361c14b7ea406479271fb15377ec7b94cd`. Script path: `scripts/development/operator/ccpc_material_issue_delivery_readonly_check_20261015.sh`, exact UTF-8 SHA256 `d81fa05afdef07bf059ccc21c6e9a9bea2eb77195b1a542cd1b95841ddbfd9a6`.
- On 2026-10-15 the operator reported `STAGED AND VERIFIED, NOT EXECUTED` from the private `$HOME/ccpc-reviewed-scripts` directory. In a separate step they reran the SHA256 check and manually executed the staged file. The output was **`PRIVATE GITHUB READ: PASSED`**, **`PINNED MATERIAL ISSUE SOURCE BRANCH: VERIFIED`**, **`DELIVERY PREPARATION READ-ONLY CHECK: PASSED`**, and **`NO ERPNext SITE, DATABASE, DOCKER, BACKUP OR PRODUCTION OPERATION PERFORMED`**.
- Thus the **first manual pinned GitHub → isolated Ubuntu stage → checksum verification → read-only execution** workflow is successful for this script. The GitHub connector independently reverified branch and source bytes, but cannot access the operator's host or independently audit its filesystem.
- The identity-safe rollback-only Material Issue integration diagnostic previously succeeded but **all SQL was rolled back**; it was one-shot and **must never be rerun**. The owner approved **review/preparation only** for a future committed one-unit issue. No commit-capable harness is yet prepared, staged, executed or authorized. Future business-affecting scripts still require fresh review, exact hashes, backups/identity checks and explicit one-operation consent. No PRODUCTION or persistent DEVELOPMENT changes, stock/GL posting or automation were authorized.
