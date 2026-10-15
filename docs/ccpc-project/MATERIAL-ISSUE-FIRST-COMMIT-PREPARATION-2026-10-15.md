# CCPC ERPNext — First committed one-unit Material Issue: preparation and execution gates

## Live read-only configured database separation preflight PASSED — operator evidence 2026-10-15

**Owner approval:** Explicit separate consent was given for **one** read-only preflight, including limited inspection of PRODUCTION `ccpcerp.local/site_config.json` database-name configuration inside the running PRODUCTION backend. This was **not** authorization to change PRODUCTION or permanently issue any stock.

**Operator result:** After GitHub-pinned staging and SHA256 verification of `scripts/development/operator/ccpc_material_issue_db_isolation_readonly_20261015.sh`, operator supplied the following complete console output:
```text
FOUR DISTINCT RUNNING DEV/PROD COMPOSE SERVICE ROLES: VERIFIED
SEPARATE DEV/PROD MARIADB STORAGE MOUNTS: VERIFIED
PRODUCTION SITES MOUNT DISTINCT FROM DEV WORKSPACE: VERIFIED
ISOLATED TEST, SHARED DEVELOPMENT AND PRODUCTION DB NAMES: DISTINCT
ONLY SITE CONFIG DATABASE NAMES WERE READ; NO VALUES OR SECRETS PRINTED
NO SQL, FRAPPE, STOCK, GL, BACKUP, DOCKER LIFECYCLE OR PRODUCTION DATA WRITE
DATABASE CONFIGURATION ISOLATION READ-ONLY PREFLIGHT: PASSED
```

**Verified meaning:** Source and immutable review branch commit `d1bf86ae7170a6b7401d513d97f0a00174de3348` were re-fetched through GitHub. The script checks four distinct running Docker Compose project/service-role containers, disjoint MariaDB mount Source locations, disjoint development workspace vs production site storage mounts, and distinct HMAC representations of `db_name` keys for test DEVELOPMENT `ccpc-integration2.localhost`, shared DEVELOPMENT `development.localhost`, and PRODUCTION `ccpcerp.local`. With the operator's supplied PASS output, this gate has **operator-reported runtime PASS**. It did not query actual MariaDB SQL connections or inspect site business records; live output cannot be independently obtained by ChatGPT's GitHub-only connector. Source design limits operation to reading configured `db_name` values, mount metadata and Compose labels. Nothing in this pass changes the existing no-production-writes restriction.

**Remaining financial posting gates (all NOT YET PASSED):** Need a separately reviewed isolated-only direct SQL/read-only Frappe database connection identity and current baseline check, verify 12 protected recovery checkpoint sets / 48 artifacts and snapshots without modifying them, reconsider actual accounting defaults and all ledger/mutation side effects of the new commit-capable candidate, and obtain new exact owner authorization for **one** committed 1 Nos Material Issue. The preflight passed **configured identity and mount separation only**, not direct SQL, complete network isolation, permissions, recoverability, committed GL/SLE behavior, CSRF or concurrency. The commit-capable script has not been staged, armed or executed. Never replay the consumed rollback-only diagnostic or auto-repeat any first commit attempt.

## New read-only DEVELOPMENT/PRODUCTION isolation preflight prepared — 2026-10-15

**Scope: preparation and GitHub source review only. No server execution or permission for permanent Material Issue posting.** The operator said “Continue” after the recommendation to *prepare and review a nonmutating database-isolation preflight*, not after a request for actual financial posting.

**New reviewed script:** `scripts/development/operator/ccpc_material_issue_db_isolation_readonly_20261015.sh` on `review/material-issue-first-commit-preparation-2026-10-15`. Its creation commit was `fc3650f7be48b6f1d72ddcd32529046bc02d0d9d`; exact file SHA256 **`a376a6fd3e6e6fd363ee6fd711154159737ac73ff5f7bacc4eb5714755b85a52`**, Git blob SHA `29d2a64c7ca179732029597be1ff93b61ea1604b`, 7,449 UTF-8 bytes / 163 source lines (trailing newline). GitHub re-fetched file at that exact blob SHA. The script was syntax checked with `bash -n`, both embedded Python blocks parsed with `ast.parse`, and **four mocked cases passed** without any Docker connection: ordinary separate layout (PASS), overlapping site DB names (STOP), overlapping MariaDB mount sources (STOP) and missing PRODUCTION DB service (STOP). These are mocks, **not** a live host, production or Frappe database test.

**Bounded inspection design:** Runs as `gani` (rejects root); uses only `docker ps` with Compose project/service labels, `docker inspect --format '{{json .Mounts}}'` for expected mounting points, and `docker exec --user frappe ... python3 -c` to **read-only open the existing site_config.json** on the DEVELOPMENT frappe container and PRODUCTION backend container. Reads only the `db_name` JSON key internally for `ccpc-integration2.localhost`, `development.localhost` and `ccpcerp.local`, producing a per-run HMAC-SHA256 for each name; compares digests inside the host script and prints only fixed PASS/STOP strings, **never** DB names, host paths, passwords, full configuration or other secrets. Confirms distinct DEV/PROD Compose-role containers; distinct underlying DEV and PROD MariaDB named-volume mount sources; separate production sites volume and development workspace; and three distinct configured database names. Fails closed if container labels/counts/layout/permissions differ, JSON is invalid, or volume/source names overlap. Suppresses raw Docker stderr. It never connects to MariaDB or Frappe and does not execute transactions, migrate, alter Docker lifecycle, modify files/services, or read production business tables/records.

**Material limitation:** The script **does start a short-lived, nonmutating read-only Python process in the PRODUCTION backend to inspect one site_config field**, so operator must understand that production is *read*, though not changed. It establishes **configured database identities and storage mount separation**, not direct SQL `SELECT DATABASE()` connection identity, runtime network correctness, complete container isolation, verified restore recoverability or a blanket guarantee that development code could never reach production. A separate isolated-only direct SQL read-only audit is still needed before posting. Host layout was inferred from the 2026-10-10 Docker architecture runbook and tracked production `compose.yaml` / `overrides/compose.mariadb.yaml` plus the tracked devcontainer template; **live Compose resources have not been checked by ChatGPT**.

**Next gate:** After owner review, manually stage **only** this new, read-only script in the private `$HOME/ccpc-reviewed-scripts` directory using the runbook's exact immutable review-branch HEAD, file path and SHA256. Staging **must not automatically execute** it. Then the operator may separately approve its read-only execution; if it STOPs, do not retry, change host layout, expose secrets or touch production. The existing *commit-capable* Material Issue candidate remains **unstaged, unexecuted, unapproved**; do not use its arming flag. No PRODUCTION write, inventory deduction, Stock Entry submit/SQL COMMIT or restoration authorization follows from this milestone.

## Candidate operator artifact prepared for REVIEW ONLY — 2026-10-15

**This is not permission to run, and is not certified production- or DEVELOPMENT-transaction-ready.** Following an operator-supplied copy of the consumed successful rollback-only diagnostic, its exact original SHA256 was independently verified: `951ff6be3ae561b21fe86bd5b62b708d672b7e2166d5995d518914a11b9af996`. The original was used **only as private source material**; it was not executed or committed to GitHub.

A **new and differently named** candidate was created from those exact reviewed bytes and committed to this private deployment review branch:
- **Candidate:** `scripts/development/operator/ccpc_material_issue_first_commit_guarded_candidate_20261015.sh`.
- **Creation commit:** `1d6f023cb17a1ebc6af3850cc9e2a3880f1147f3` (review branch was verified at this SHA immediately after file creation).
- **Candidate blob SHA (git SHA-1):** `323967737cd762f7018a739fc7d67d1b25520259`, confirmed by retrieving GitHub file and by local `git hash-object`.
- **Full UTF-8 SHA256:** `0d935e3ce6c50cad1d94682690015cf8c3ed4b6fe17e576d097bdf588337c702`, calculated from the same source; 649 lines, 34,697 UTF-8 bytes.
- **Checks performed with NO ERPNext calls:** `bash -n` pass, embedded Python `ast.parse` pass, 13 source-level condition checks pass (one issuer handler call, one explicit commit method call, commit gate after in-transaction posting/stock/GL audit, postcommit fresh-connection audit, internal-commit/email/enqueue block, strong SLE/GL object identity, no old unconditional rollback, persistent one-shot marker, explicit inert-by-default arming requirement). A local unarmed shell invocation returned the expected early `NOT AUTHORIZED` error **before the Docker line**; this did not access the site or create an attempt marker. No live functional/integration test of the candidate was performed.
- The isolated DEV site's expected identifiers remain bound in candidate source to the previously reviewed synthetic fixture. The handler and hook source were rechecked at app feature commit `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`. Pinned Frappe `Database.commit` source `988e54f3c4c291e2077a83809663f123731abe76` was read: an explicit Frappe commit runs before-commit callbacks, SQL COMMIT, begins another transaction, then after-commit callbacks. Therefore any exception **after a commit was attempted is outcome-uncertain** until an independent read-only SQL audit. The candidate treats it this way and never automatically retries.

**Review-required risks and constraints:** The candidate was **not** staged on Ubuntu and is **not authorized to execute**. Its new `Document.insert` allowlist for only scoped Version/Stock Entry/SLE/GL documents has not been empirically confirmed against a live committed site and may fail safely on an ERPNext-generated ancillary document; a STOP could leave non-DB cache effects. The guard checks isolated database identity against **persistent DEVELOPMENT** but cannot yet independently confirm isolation from the separate PRODUCTION database because this candidate intentionally avoids reading PRODUCTION site configuration. **Production DB separation must be independently established by an approved nonmutating test before any actual posting.** A transaction may also have filesystem/Redis and commit-hook side effects outside ordinary SQL rollback. The newest 12-backup set / 48 files and live inventory baseline must be reverified before any write, with recovery/restore limitations disclosed. Real HTTP POST/CSRF, concurrency, duplicate request, full restore drill and actual CCPC expense-account mapping are untested. Do not stage or execute the new script based only on this static milestone.

**Explicit execution gates (still unmet):** independently review exact new candidate source and all guard/SQL transitions; obtain current isolated-vs-shared-vs-production DB separation evidence without exposing production secrets; verify current protected recovery assets and last committed isolated Slip/Bin/ledger baseline; resolve any source review issues with **a new Git commit/SHA256**; obtain a new, precise owner's approval to perform **one** 1 Nos synthetic Material Issue permanent SQL COMMIT on `ccpc-integration2.localhost`; then and only then separately stage exact new GitHub commit/sha and manually arm/run the script. An early arming failure or missing marker is a stop, not permission to retry. Do not run the original diagnostic or perform PRODUCTION operations.

**Prepared:** 2026-10-15. **Status:** REVIEW/PREPARATION ONLY — NO POSTING AUTHORIZATION OR EXECUTABLE COMMIT-CAPABLE RUNNER YET.

This document is a forward-looking design review, not a record of a successful committed posting. Read the current GitHub-first workflow, rolling handoff, and reviewed GitHub-to-DEVELOPMENT delivery runbook before continuing. Earlier one-shot diagnostic files were consumed and must never be rerun, modified for replay, or represented as newly reviewed script source.

## Authorization and project boundaries

The latest owner approval covers **review and preparation of the next committed-posting test only**. It does **not** authorize actual business-data changes, a Stock Entry submit/SQL COMMIT, a live HTTP POST, migration, backup restoration, new users or fixtures, an application merge, branch reset, changes to persistent DEVELOPMENT, or any PRODUCTION operation.

The proposed future operation, subject to a **separate explicit execution authorization**, is exactly one synthetic 1 Nos Material Issue against `WS-2026-00001` in isolated Frappe site `ccpc-integration2.localhost`; no retry after success or failure. Persistent shared DEVELOPMENT and PRODUCTION operate on the same Ubuntu host but must remain unchanged. Do not mutate their Git working trees, databases, containers, cron jobs, mounts, settings or backups.

## Verified inputs carried forward from the October 15 handoff

- Custom app feature branch: `ccpcerp/ccpcerp:feature/withdrawal-material-issue-safety`, SHA `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6` (independently reverified this conversation).
- Separate persistent shared DEVELOPMENT branch: `review/intercompany-approval-failure-tests`, SHA `806fa23516490ec7beefcff03a1baa09d722120e` (GitHub branch independently reverified; server checkout must be checked again).
- App PR #7 and deployment docs PR #24 remained open and draft at verification.
- Installed runtime versions reported from operator's prior site test, not rechecked live in this preparation: ERPNext `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`; Frappe `988e54f3c4c291e2077a83809663f123731abe76`.
- Last independently audited isolated-site SQL baseline: one `WS-2026-00001`, `Stockroom Review`, empty `received_by` and `issued_by`, one child row with 1 Nos requested/reviewed and 0 issued; zero linked Stock Entries, one historical SLE, two historical GL entries, ten Nos and PHP 1,000 valuation for fictional `CCPC-INT-TEST-CONSUMABLE-001` in `Stores - TISS`. These are historical operator-reported results and must be confirmed again before any write.
- Recovery assets: twelve preserved checkpoint sets / forty-eight archive-verified files, including the 2026-10-15 post-Slip pre-Material-Issue recovery checkpoint. These are site-private backups; no successful restore drill and no independently verified off-host backup are claimed.
- Expected accounting on the **synthetic** issuer Company from prior isolated-site configuration: debit `Stock Adjustment - TISS`, credit `Stock In Hand - TISS`, cost center `Main - TISS`; approximately PHP 100 each at last-observed moving-average cost. Actual posting accounts/valuation must be checked before any COMMIT, not presumed a final real-company expense policy.

## GitHub code review completed at pinned feature source

`ccpcerp/ccpc_erp/withdrawal_slip_stock.py`:
- `issue_withdrawal_slip` is POST-whitelisted and does not contain an explicit application-level commit.
- It requires a Stockroom user, obtains an exclusive lock on the Withdrawal Slip, verifies current slip fields, requires `received_by`, checks an independent Stockroom issuer with a different saved owner/preparer, rejects a submitted issue and any existing draft, then creates **one new** linked draft Stock Entry using narrow `ignore_permissions` and submits it through standard ERPNext stock/GL hooks.
- Stock Entry validation/before-submit hooks enforce provenance, source Warehouse, issue quantity and available stock; the after-submit hook updates Slip issue state.
- This is static GitHub review; it does not establish real committed persistence, HTTP authentication/CSRF or concurrency safety.

Prior single-run rollback-only harness reached normal Stock Entry → SLE → two GL ledger submissions and passed its transient account/stock checks, but **rolled SQL back** and the independent readback confirmed unchanged committed rows. It was not a successful permanent posting. Earlier harnesses initially rejected legitimate SLE and GL submissions; the final working harness tracked GL objects with strong references instead of solely numeric Python object IDs. Reintroducing either harness error would invalidate a new test.

## Required future commit-capable runner design

A new unique-name candidate script has now been prepared and committed as **review-only source** using the exact SHA256-matched operator-uploaded original (which itself was not republished). It passed local syntax/static checks, but has **not** been staged, tested in ERPNext, or authorized for an actual SQL COMMIT. See the milestone above for its exact commit, file hash, scope and remaining risks.

Before one SQL write is allowed, the candidate script must fail closed on:

1. An exact pinned script-file SHA256 and immutable Git commit; exact installed Frappe/ERPNext and CCPC feature source SHAs; an isolated, non-serving source path; correct branch and clean protected shared Git status (preserve `?? AGENTS.md`).
2. Positive proof that the target isolated site's database identity differs from persistent DEVELOPMENT **and** PRODUCTION, with no shared or production host/container database effect.
3. All twelve protected checkpoint sets / 48 original artifacts independently hashed and unchanged, archive structure verified, latest post-Slip pre-posting site backup available and restore limitations disclosed. No backup deletion, retention or restoration.
4. A fresh isolated, committed preposting baseline including the one Slip/child row, peer Stockroom identities and permissions, no linked Stock Entries, original one SLE/two GL, Bin 10 Nos/PHP 1,000, exact source warehouse/item/UOM, live accounting and valuation configuration, and no unexpected Email Queue delta.
5. Source-level proof that only the approved new one-Stock-Entry Material Issue handler can be called, once, by independent fictional Stockroom B. Retain narrowly scoped document insert/submit guards that allow standard related SLE/GL lifecycle, and strong Python object-reference tracking for GL identity. Block unrelated DocTypes, item/voucher changes, email, async jobs, and internal commits.
6. A **single explicit commit gate** following an in-transaction audit of one submitted Stock Entry, one new negative one-Nos SLE, precisely two balanced GL entries with the verified account pair, 10 → 9 Nos with expected valuation tolerance, full Slip issue fields, backup/source integrity and no unrelated records. All deviations force precommit SQL rollback with a sanitized STOP report.
7. After the one attempted commit, a fresh independently opened read-only SQL connection must confirm the committed Slip, linked Stock Entry, SLE/GL and Bin deltas. Distinguish: precommit rollback; COMMIT attempted with uncertain outcome; and independently verified COMMIT. **Never automatically retry**, especially when COMMIT outcome is uncertain.
8. No unreviewed blanket exception handling, false-success output, unsafe SQL rollback claim about Redis or other external effects, remote code piping, self-hosted runner, or auto-execution. Live HTTP/CSRF, double-submit and concurrency testing remain separate later approvals.

A successful transaction should be expected to yield **one** submitted Stock Entry for the Slip, Slip `Fully Issued` with 1 Nos issued, 9 Nos remaining in Bin, one new negative SLE and **two** new balanced GL entries for the synthetic Company. No result is claimed until postcommit independent readback passes. Any STOP requires preserve-the-state investigation; no script replay and no automatic restore.

## First delivery workflow check — newly prepared, nonmutating

New repository path: `scripts/development/operator/ccpc_material_issue_delivery_readonly_check_20261015.sh`.

This shell script checks only (1) authenticated read access to the private deployment documentation branch and (2) the expected pinned application feature SHA via noninteractive strict-host-key `git ls-remote`. It rejects root and mismatched/empty refs. It does not open a Frappe site, Docker container, MariaDB connection, backups or local app checkout; it cannot post Material Issues. It is intended to test the previously **unverified GitHub→Ubuntu delivery-by-pinned-commit/checksum process** safely before any business-affecting script is published or considered for execution. GitHub staging into `$HOME/ccpc-reviewed-scripts` is a separate operator step; merely viewing or committing this script does not run it.

The first manual staging operation must follow `REVIEWED-SCRIPT-DELIVERY-TO-DEVELOPMENT.md`: pinned full branch commit + file SHA256, exact path, owner-private new destination, no overwrite, separate from DEVELOPMENT app checkout. **No staging/execution has occurred in this chat.**

## Next decision gate

1. Verify the new read-only artifact was fetched into the operator-private staging directory with its expected SHA256; report the staging output.
2. Reconstruct/review the exact full commit-capable runner guard implementation from operator-supplied original source under a new filename, or design and test a new source-independent equivalent. Independently syntax-check, instrument negative tests and review all failure paths before committing. Do not publish consumed scripts themselves as reusable artifacts.
3. Obtain **fresh owner approval for the exact one-time committed test** only after a reviewed script, live-readiness confirmation and appropriate isolated recovery decision. No production release follows automatically.

**Current completion state (latest):** read-only GitHub-to-Ubuntu transfer and script execution PASSED by operator report; matched original rollback diagnostic privately reviewed; **a new commit-capable candidate's source is now committed to GitHub for REVIEW ONLY**, with syntax/static checks passing. It has **not been staged, executed or integration-tested**. No Material Issue, business-data write, SQL COMMIT, or PRODUCTION operation was performed by this preparation.
