# CCPC ERPNext — First committed one-unit Material Issue: preparation and execution gates

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

A newly reviewed, unique-name operator script must be developed from the **exact full verified code** and tested independently; the previously used one-shot source files were **not available in this chat's filesystem or in the reviewed GitHub repository**, so this preparation does **not** invent an executable replacement with presumed-equivalent guards.

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

**Current completion state:** source reviewed; test acceptance and risk gates documented; read-only delivery proof script prepared for independent staging. Commit-capable posting script **not yet prepared, staged or run**. No business-data writes or SQL COMMIT performed by this documentation milestone.
