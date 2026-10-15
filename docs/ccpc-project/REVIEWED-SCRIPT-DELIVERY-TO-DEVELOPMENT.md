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
OUT_DIR="$HOME/ccpc-reviewed-scripts"
REPO_URL='git@github.com:ccpcerp/ccpc-frappe-deployment.git'
mkdir -p -m 700 "$OUT_DIR"
TMP_DIR="$(mktemp -d "$OUT_DIR/.fetch.XXXXXXXX")"
GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10' git -C "$TMP_DIR" init -q
GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10' git -C "$TMP_DIR" fetch -q --depth=1 --no-tags "$REPO_URL" "refs/heads/$APPROVED_BRANCH"
test "$(git -C "$TMP_DIR" rev-parse FETCH_HEAD)" = "$APPROVED_COMMIT"
FILE_NAME="$(basename -- "$APPROVED_PATH")"
test "$FILE_NAME" = "$APPROVED_PATH" || test "$APPROVED_PATH" != "$FILE_NAME"
test ! -e "$OUT_DIR/$FILE_NAME"
git -C "$TMP_DIR" show "FETCH_HEAD:$APPROVED_PATH" > "$OUT_DIR/$FILE_NAME"
test "$(sha256sum "$OUT_DIR/$FILE_NAME" | cut -d' ' -f1)" = "$APPROVED_SHA256"
chmod 600 "$OUT_DIR/$FILE_NAME"
printf 'STAGED AND VERIFIED, NOT EXECUTED: %s\n' "$OUT_DIR/$FILE_NAME"
```

**Review note:** The template intentionally leaves its dedicated hidden `.fetch.*` repository for operator inspection instead of deleting anything automatically; tidy only those exact owned temporary folders later under a separately reviewed housekeeping step. The `APPROVED_PATH` must be provided and reviewed as an exact relative path under the operational scripts directory; do **not** accept arbitrary `..`, leading `/`, a symlink or untrusted ref. If staging fails or an existing output file is present, stop and do not execute. A production-grade reusable staging helper should additionally validate these inputs mechanically before being introduced. **Do not paste placeholder values as executable instructions.**

## Phase 4 — separate manual execution

Only after a successful staging confirmation, explicit one-operation authorization, and review of the run's current prerequisites may the operator run an exact `bash "$HOME/ccpc-reviewed-scripts/<approved-new-script-name>"` command. Check all error/output lines. Never auto-retry. The agent must record **operator-reported**, independently supported PASS/STOP results in GitHub, distinguishing transactional rehearsal from committed business effects. No background scripts, automatic deployment or server access is created by this runbook.

## Current status on adoption

- Owner approved the **delivery workflow**, not a new Material Issue posting, restore or diagnostic replay.
- The identity-safe rollback-only integration diagnostic already ran successfully on 2026-10-15 and **must never be rerun**.
- At time of writing, **Ubuntu private-GitHub SSH access is unverified**; Phase 1 is the only next recommended terminal command. No new script has been published for execution under this workflow.
