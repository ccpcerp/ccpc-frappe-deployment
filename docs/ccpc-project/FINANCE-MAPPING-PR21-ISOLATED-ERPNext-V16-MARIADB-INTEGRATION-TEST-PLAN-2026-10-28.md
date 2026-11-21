# CCPC Finance mapping PR #21 — isolated ERPNext v16 / MariaDB integration test plan

**Prepared:** 2026-10-28 (Asia/Manila)  
**Authority:** Owner explicitly approved **preparing this isolated database integration test plan in GitHub first**. This is DOCUMENTATION ONLY, not permission to start CircleCI, create a VM, pull or run containers, install apps, migrate any site, run HTTP/finance transaction probes, change CI guards, spend on infrastructure, deploy or alter backups.  
**Status:** G0 DESIGN REVIEW; RUNTIME EXECUTION NOT APPROVED. No source code or site data changed under this approval.

## 1. Authoritative GitHub baseline and known evidence

- Follow [GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) and current [Integration2 Finance handoff](INTEGRATION2-FINANCE-AUTHENTICATION-CHECKPOINT-2026-10-27.md). Read [Accounting authority decision](FINANCE-MAPPING-ACCOUNTING-AUTHORITY-DECISION-2026-10-28.md), [lifecycle specification](FINANCE-MAPPING-LIFECYCLE-SCHEMA-ACCOUNTING-GOVERNANCE-SPEC-2026-10-28.md), and [earlier disposable-lab isolation checklist](DEDICATED-BACKUP-STEP135-LAB-ISOLATION-AND-COMPOSE-RENDER-CHECKLIST.md) as applicable.
- App: [ccpcerp/ccpcerp PR #21](https://github.com/ccpcerp/ccpcerp/pull/21) OPEN / DRAFT / UNMERGED. Source **feature/finance-mapping-lifecycle-2026-10-28**, HEAD **76973699a085d3eb4efd6412d21a773ec1499e19**, target **review/circleci-isolated-erpnext-phase2-2026-10-26** at **0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41**. Verify all these values again at G0; do not assume this document freezes future branch tips.
- **Executed, operator-supplied static test evidence at guarded feature HEAD**: test_bc_finance_governance_static.py 6/6, test_ccpc_mapping_schema_static.py 3/3, test_bc_mapping_policy_static.py 15/15; **24/24 PASS**. Earlier source-only JavaScript checks 20/20 PASS separately. Neither proves SQL, HTTP, migration, concurrency or posting behavior.
- New candidate schema: five DocTypes (**CCPC Accounting Mapping Decision; CCPC Mapping Decision Use; CCPC Mapping Rejection Event; CCPC Mapping Retirement Request; CCPC Mapping Retirement Event**) plus additional Rejected state and rejection provenance fields on both existing revision DocTypes. The new schema has no ordinary user grants and creates financial audit records through controlled server code.
- Business state is **NOT a fixture for this experiment**: Integration2 Company TISS Expense Scope fie8da5c59 / Maker Draft Revision fieef2e44j was last independently verified still Draft, no mapped GL/stock, with protected local backup hashes. Do not import, approve, reject, retire or reuse these records. Do not touch either existing DEVELOPMENT site.

## 2. Recommended target and isolation conditions (G0)

**Preferred:** existing **CircleCI-managed disposable SQL integration job**, AFTER review of its exact branch/commit controls and any separately approved feature test harness change. The job defines a fresh Frappe v16/ERPNext v16 bench with ephemeral MariaDB and Redis and a synthetic ci-circleci.localhost site. This is conceptually separated from persistent CCPC DEVELOPMENT and PRODUCTION; execution has NOT been authorized and its isolation must be verified at job start.

**Current hard blocker:** In the reviewed app source .circleci/config.yml the isolated-erpnext-integration job explicitly checks CIRCLE_BRANCH == review/circleci-isolated-erpnext-phase2-2026-10-26, while its fixture guard ci_disposable_site_guard.py also pins that exact review branch plus CircleCI identity/job/pipeline and tested site. PR #21 is on feature/finance-mapping-lifecycle-2026-10-28. **Running that existing job directly against PR #21 should fail closed.** Do not bypass by spoofing environment variables, weakening the existing guard, changing production policy, force-moving the review branch or placing the feature on the default branch.

**Required separate code-review decision before the first CI run:** choose a narrowly scoped, opt-in test harness strategy that (a) verifies exact GitHub source commit plus owner-reviewed branch, (b) preserves all existing CI disposable site/job/organization/ephemeral credentials and allowed test site checks, (c) rejects every persistent site, (d) does not grant access to DEV/PROD SSH, Docker socket, site_config, volumes, NAS shares or production networks and (e) does not automatically enable expensive pipelines. A feature-specific second guarded CI path is preferable to relaxing the existing original guard. No CI change is authorized by this planning document.

**Fallback:** a disposable independently managed VM with its own Docker daemon/network/volumes and separate access identity **only after a new G0 risk and cost approval**. A separate Docker container/Compose project on ccpcerpserver, a reused DEVELOPMENT bench, a cloned existing site or an old host Docker socket does NOT qualify. Never re-use protected backups from real CCPC sites for destructive testing.

**Environment evidence to capture before any authorized run:**
- Runner/VM identity, ownership, expiry, isolation from DEV/PROD host/network/storage/credentials and allowed DNS/routing. Stop on access to live site or Docker socket.
- Exact GitHub repository, branch, SHA, clean checkout and SHA match to CI checkout; PR still OPEN/DRAFT, no unexpected changes in affected fields or test harness.
- Frappe, ERPNext, CCPC app commits, Python/Node/MariaDB versions, DB/Redis endpoints, immutable test site name and database identity, configured time zone, collection of disposable-only credentials, and no reliance on a machine's implicit production environment.
- Prefer explicit reviewed Frappe/ERPNext **v16 commit pins** rather than floating version-16 heads; existing DEVELOPMENT previously reported Frappe 16.33.1 / ERPNext 16.34.2, but that is historical observation, not proof of CI runner versions.
- Confirm run_integration remains opt-in, no schedules, no automatic approval/merge/deployment workflows and no unexpected paid runner work. Stop on any mismatch.

## 3. Phase gates — proposed future execution, not authorized commands

| Gate | Test target / expected artifact | PASS standard / hard STOP |
| --- | --- | --- |
| P0 — review and authorize | Owner approves exact disposable runner/feature-commit/test harness, resource exposure and defined probes | Isolated source/runner/DB identity demonstrably separate; no shared production secrets/daemon; CI guard actually passes without spoofing |
| P1 — read-only inventory + new-site creation | On disposable target only: verify empty/new site, database name distinct from DEV, packages, app HEAD, no imported CCPC data | Never install/migrate if site isn't disposable, clean and approved; no existing live DB |
| P2 — schema installation/migration | Install and migrate CCPC app into a **fresh** disposable ERPNext v16 test site, then validate all 5 new DocTypes and 2 revised mapping DocTypes | Field types/links/unique indexes, controllers and Frappe v16 metadata install successfully; no permission escalation; zero SQL errors |
| P3 — baseline seeded synthetic masters | Synthetic Companies, leaf Item Groups, Accounts, beneficiary Department, Cost Centers, real per-test named Maker/Checker users and exact Company grants | Fully synthetic disposable records only; no main DEV/PROD records, no arbitrary user-role inheritance |
| P4 — rights, review, reject, approve | Actual authenticated HTTP Maker/Checker sessions/CSRF, proposed revision, independent review, internal signed decision, exact one-time approval, terminal rejection of separate Draft | State, Version and unique Decision Use values match; wrong Company, stale token, forged fields, self-approval, replays fail closed |
| P5 — request, decline and prospective retirement | Authorized Maker request, Checker review, decline, new request, signed internal retirement decision and accept | Append-only accepted event, server-owned cutoff; original Approved fields and prior snapshots unchanged; no duplicate Version/event |
| P6 — issue/runtime and concurrency | Original withdrawal Material Issue financial resolver + before_submit; old vs current time; simultaneous conflicting operations | No issue after cutoff, no missing/ambiguous account fallback, no GL/stock changes on denied requests; valid synthetic posting only where separately approved |
| P7 — failure/recovery/compatibility | Inject Version/SQL failure on test-only DB; concurrency/retry tests; before/after snapshots; cleanup of **only** ephemeral site/runner | Atomic rollback and exact cardinalities, no unsafe old-row behavior, no live site contact; retain sanitized evidence before disposable teardown |

**Progressive permission:** Separate approval to start P0/P1 does not implicitly approve synthetic financial postings in P6, destructive failure injection, expensive concurrency saturation or any live site. A single later execution approval should name which P-gates and actions are allowed, a reviewed exact SHA, runner, expected row counts, rollback and stop conditions. Stop after first failed gate, preserve evidence and repair only in GitHub.

## 4. Minimum adversarial test matrix and data-integrity assertions

Each test must have unique synthetic IDs, isolated database transaction, before/after table cardinality, an explicit expected status, operator-readable failure reason, and proof that denied paths left records unchanged. Zero production/business data.

| ID | Scenario | Expected verified result |
| --- | --- | --- |
| S01 | Install and migrate five new DocTypes + B/C Rejected fields | Frappe v16 metadata and MariaDB tables/indexes valid; no unintended role grants or baseline changes |
| S02 | Maker proposes Expense B and Center C with exact scoped masters | Independent Draft, correct revision numbers, original owner; no active mapping |
| S03 | Checker returns exact review and fresh modified token | Authenticated Company-scoped data only; no state change |
| S04 | Sign internal Accounting Mapping Decision for Draft | Signed event/Version only; no activation before separate approve call |
| S05 | Independent Checker approves using signed ID once | Approved revision, exact decision ID as reference, single Decision Use and one Version; effective_from >= approval instant |
| S06 | Approve using arbitrary string, wrong Company/scope, changed master, stale token, duplicate signed ID | Denied; no approved revision, Version, stock or GL side effects |
| S07 | Same Maker self-approves, Guest, Administrator override, Stockroom actor, disabled user, missing Company grant | Denied under real Frappe User/Role/User Permission and session/CSRF |
| S08 | Reject an unrelated Draft using independent Checker + reason | Terminal Rejected, rejection audit event and Version; never Approved |
| S09 | Approve-vs-reject race and duplicate rejection | Exactly one terminal state/event; losing requests roll back; no double audit |
| S10 | Maker requests retirement for open Approved revision | Pending request + Version, no cutoff or accounting effect |
| S11 | Repeat identical Pending request and different-payload request | Same request ID without additional Version for identical retry; changed payload rejected |
| S12 | Checker gets retirement review version then declines with reason | Declined+Version, Approved target unchanged |
| S13 | New Pending request signed and accepted by independent Checker | One accepted immutable event and one Decision Use, prospective server cutoff; Approved history unchanged |
| S14 | Concurrent Checker accepts and retry with same/different signed ID | At most one accepted retirement, no duplicate cutoff or Version, failed caller reconciles by read-only query |
| S15 | Voucher posting timestamp before cutoff but actual submission after cutoff | Denied; no submitted Stock Entry/GL/SLE after cutoff |
| S16 | Synthetic issue while B/C effective, then retire sole B or C | Exact approved source/value before cutoff; after cutoff fail closed without silent native defaults |
| S17 | Modify former Maker/Checker roles after original approval | Historic signed data and already posted vouchers remain auditable while new event authority is denied if revoked |
| S18 | Force Version insertion/constraint failure mid-sign/approve/reject/retire | Full database transaction rollback, no orphan decision/use/event/status, no partial ledger |
| S19 | Existing old Approved revision without new internal Decision ID | Explicit documented compatibility decision: fail closed or migrate with verified evidence; no invented signatures, no silent historical erasure |
| S20 | Old CircleCI synthetic signed-looking fixture with special token | Bypass only inside exact disposable CI identity; never accepted in persistent DEV/PROD |
| S21 | Legacy propose_mapping_replacement / propose_mapping_retirement / approve_mapping_change | Disabled paths fail before database mutations; replacement remains a separate future feature |
| S22 | Two scopes / Company cross-leak, duplicate versions, overlapping effective windows, row-lock deadlocks | Correct deterministic lock order, one winner or safe rejection, zero cross-Company data exposure |
| S23 | B/C half-open intervals and site-local vs UTC comparisons | Posting boundary and now-check deterministic; no backdated retirement or stale approval |
| S24 | Repeated full test suite and clean isolated teardown | Reproducible on fresh site; no persistent host/volume/network changes; evidence retained safely |

**Real MariaDB concurrency methodology:** separate HTTP/Frappe sessions and independent DB connections on a disposable test site, synchronized where possible to produce genuine lock/contention; assert SQL rowcounts, unique key behavior, transaction boundaries, lock waits and deadlocks, then verify final state from a third read-only connection. Mocked unit tests alone cannot establish these invariants.

## 5. Before/after inventory and incident stop rules

Minimum evidence, captured without passwords/session cookies/CSRF, real employee data or unreviewed logs:

- Before: exact repo/branch/SHA, Frappe/ERPNext revisions, site/DB identities and network isolation, ready synthetic Companies/groups/masters, relevant existing roles, counts in 4 original mapping DocTypes plus 5 new DocTypes, Version, User Permission, GL Entry, Stock Entry, Stock Entry Detail, Stock Ledger Entry and any touched operational records.
- After each stage: expected document IDs/names, state, ownership, modified version, signed_by/at, effective_from, cutoff_at, decision-use uniqueness, accepted/rejected audit Version rows, reference linkage, ledger counts and independent DB readback. Audit identifiers may be recorded; omit sensitive decision attachments.
- Failure: record exact stage and sanitized error type, mark **STOP**, rollback current transaction, avoid automatic re-run after ambiguous POST, inventory committed state from another connection, and update PR/handoff with a reproducible minimal sanitized issue.
- Stop immediately if connected to DEV/PROD/mounted NAS, source SHA/branch mismatch, unknown pre-existing records, leaked credentials, unapproved paid job, missing unique constraint, SQL deadlock without controlled rollback, orphan event, partial posting, changed historical approved row, failed test-only rollback, loss of isolation, or unexpected app migration side effects.
- **No destructive Git commands, broad DB cleanup, Docker recreation or site restore** on any CCPC persistent environment. Disposable teardown requires a recorded exact resource inventory, preserved test results and separate execution scope.

## 6. Migration, rollback and compatibility design gates

1. First validate **clean install** on a new disposable Frappe v16 site. Next validate **additive migration** on a *separate disposable copy of a wholly synthetic old-version schema*, not a copy of CCPC operational data. Compare DocType, unique key/index and row counts; retain existing Draft/Approved content.
2. Review hook/setup/patch implications. Existing app after_migrate and patches may alter roles, workflows, custom fields and stock metadata even when the new five DocTypes are the obvious changes. Re-run G0 read-only change inventory before any persistent site deployment.
3. Check compatibility of all read-only historic approvals with the new signed-decision resolver, including whether real legacy approvals require verified conversion records. **Never fabricate new Accounting signoffs to make a test pass.** CI synthetic fixture is not genuine Accounting authority.
4. Do not accept retirement events until all issue builders, validators and relevant workers are running a verified resolver honoring accepted cutoffs. If old code could ignore accepted event, disable acceptance and fail closed during staged rollout.
5. Decide how to handle the intentionally disabled replacement path. Preserve original lifecycle history; do not re-enable direct effective_until rewrites without a separate immutable-event design and tests.
6. A fresh site can be disposed of after sanctioned tests; **this is not a rollback plan for persistent financial data**. Persistent DEVELOPMENT adoption requires a separate owner-approved preflight, exact Git and status check (including untracked AGENTS.md), verified four-part backups and restore boundaries, safe migration rehearsal and independent readback. PRODUCTION requires its own independent release/backup/recovery and explicit approval, never implied by CI success.

## 7. Gating decisions to request next and expected deliverables

**G0 acceptance questions (must be answered before changing CI or running tests):**
1. Which independently owned disposable target will be used (existing CircleCI job with narrowly reviewed branch/commit test harness, or newly approved isolated VM)?
2. Who authorizes the exact opt-in run and compute budget? No automatic triggers or scheduled activity.
3. Which test-only Frappe/ERPNext v16 version/commit pins will be locked for reproducibility?
4. What exact modifications (if any) to CI branch guard and synthetic fixture guard are needed to support feature PR #21 *without weakening persistent-site protections*?
5. Which stages include synthetic GL/stock posting and failure injection, and what precise separate authorization, maximum record count, timeouts and rollback criteria govern them?

**Next proposed workflow:** Approve **only** the exact G0 source/runner/test-harness safety review. Then, with separately authorized app test-code changes, implement disposable-only integration tests in the GitHub feature PR, review PR diff and static guard tests, and request explicit opt-in integration execution permission. Execute on the approved disposable site only; record real MariaDB findings and fixes back to GitHub. If all integration gates pass, revisit a distinct persistent DEVELOPMENT adoption decision. PRODUCTION is never an automatic consequence.

**Current status:** This document plans testing; it does not report an ERPNext v16 integration PASS. Owner-run **24/24 static PASS** is the only executed Python test evidence for feature HEAD listed above. CI workflow source has been reviewed, but no feature-branch integration run was started. PR #21 remains DRAFT/UNMERGED; isolated G0 acceptance, CI harness modifications, schema install/migrate, database tests, replacement-path design, business signatory/crosswalk and all deployment actions remain pending.

## 8. G0 GitHub-only CircleCI safety review completed — 2026-10-28

The owner expressly approved a **GitHub-only CI harness safety review**, with no pipeline execution or ERPNext environment modification. Reviewed the feature/review branch source, original `.circleci/config.yml`, `ci_disposable_site_guard.py`, original negative tests, and old synthetic Finance fixture. The resulting [feature-harness G0 safety review](FINANCE-PR21-CIRCLECI-FEATURE-HARNESS-G0-SAFETY-REVIEW-2026-10-28.md) was created and read-back verified in commit `c9e678adea164c8a12569b40a84b34fe3ca2013d`.

**Decision:** Prefer **a separate opt-in Finance-only CI job and separate, exact-site/branch/job/commit guard**, not widening the existing original CircleCI site guard or manipulating CIRCLE_BRANCH. Keep original Withdrawal/Intercompany fixture safeguards unchanged. The current integration job cannot safely run feature PR21 without a reviewed harness change, and its test list does not include new PR21 lifecycle SQL/HTTP tests. New tests must be written and exercised on a wholly disposable site. Re-pin exact post-harness feature SHA and Frappe/ERPNext versions; require explicit CI runner/isolation and resource-cost acceptance before any execution.

**This completes G0 REVIEW only.** Future G1 requires separate owner authorization to implement the new CI harness/test files in GitHub; G2 separately authorizes a particular opt-in run after guard/negative-test review. There is no new CI app code commit, no pipeline/test run, no database migration, no Finance posting, no DEVELOPMENT/PRODUCTION interaction. PR21 remains draft; last verified feature HEAD `76973699a085d3eb4efd6412d21a773ec1499e19` and prior static Python test results 24/24 PASS.
