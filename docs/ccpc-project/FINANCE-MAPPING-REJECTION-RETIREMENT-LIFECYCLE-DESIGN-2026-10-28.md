# CCPC Finance B/C mapping — Draft rejection and Approved retirement lifecycle (design proposal)

**Prepared:** 2026-10-28 (Asia/Manila). **Authority:** Owner explicitly approved **preparing the lifecycle-control design in GitHub only**, without application code, Integration2 data, DEVELOPMENT or PRODUCTION modifications. **Status: OWNER-ENDORSED DESIGN DIRECTION IN PRINCIPLE; ACCOUNTING/SCHEMA DETAILS OPEN; NOT IMPLEMENTATION OR MAPPING APPROVAL.**

**Current authoritative branches:** CCPC custom app [review/circleci-isolated-erpnext-phase2-2026-10-26](https://github.com/ccpcerp/ccpcerp/tree/review/circleci-isolated-erpnext-phase2-2026-10-26) at verified commit **0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41**; deployment/docs branch **docs/ccpc-checkpoint-2026-10-10**. Read [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md), [Integration2 Finance checkpoint](INTEGRATION2-FINANCE-AUTHENTICATION-CHECKPOINT-2026-10-27.md), [original versioned mapping architecture](WITHDRAWAL-ISSUE-B-C-VERSIONED-MAPPING-ARCHITECTURE-APPROVED-2026-10-18.md), and [Accounting approval design](WITHDRAWAL-B-C-ACCOUNTING-APPROVAL-AND-CENTER-SELECTION-DESIGN-2026-10-18.md). Earlier design documents reflect their historical approval scope; this document uses the later verified app branch for current implementation facts.

## 1. Baseline, evidence and explicit stop gate

- The real authenticated Maker produced **one** synthetic TISS Expense Scope **fie8da5c59** and Maker-owned Draft Revision **fieef2e44j** (revision 1); the independent Checker review-only API passed. No accounting approval was made.
- Owner-run, read-only Integration2 preflight subsequently reported isolated site and verified backup hashes; TISS Company and role isolation; zero linked Items/defaults on the synthetic leaf Item Group; zero GL Entries and Stock Entry Detail references for synthetic Expense Account/revision; exactly one TISS Expense scope and Draft revision, no TISS/TREQ Center scope; zero Version records for the revision. **These are operator-reported observations at the checkpoint, not a live query by this GitHub document.**
- [bc_mapping_workflow.py](https://github.com/ccpcerp/ccpcerp/blob/0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41/ccpcerp/ccpc_erp/bc_mapping_workflow.py) exposes propose_mapping, get_mapping_review, approve_mapping; it does **not** provide reject, retire or revoke endpoints. Existing approval directly sets Approved state, server-owned effective timestamp and a Version decision snapshot within a single database transaction; its textual approval_reference is **not independently checked against an Accounting decision record**.
- [Expense revision JSON](https://github.com/ccpcerp/ccpcerp/blob/0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41/ccpcerp/ccpc_erp/doctype/ccpc_expense_mapping_revision/ccpc_expense_mapping_revision.json) and [Center revision JSON](https://github.com/ccpcerp/ccpcerp/blob/0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41/ccpcerp/ccpc_erp/doctype/ccpc_center_mapping_revision/ccpc_center_mapping_revision.json) have state options **Draft / Approved / Superseded / Revoked**, **not Rejected**; they contain proposed effective_until, supersedes, revocation_reason fields, but no established workflow to populate lifecycle evidence. Both revision controllers prohibit ordinary non-Draft saves and deletions.
- [bc_issue_runtime.py](https://github.com/ccpcerp/ccpcerp/blob/0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41/ccpcerp/ccpc_erp/bc_issue_runtime.py), called by the guarded Withdrawal Slip issue builder/validator, currently selects rows with approval_state == Approved and applies effective_from/effective_until. Merely changing the historical Approved row to Revoked would remove the row from **all as-of queries**, including periods when it was valid. Merely editing effective_until also conflicts with immutable signed approval intent without a separate change record.
- Current runtime provenance helper **rechecks that Maker and Checker are presently enabled and possess current roles/Company grants**, even for historic Approved rows; this merits code/policy review because an employee's later permission change should not rewrite already-proven posting history. The source's comment implies historical preservation, while its live authority helper still validates current actor grants.
- **STOP:** No endpoint execution, data migration, role grant, schema installation, approval, synthetic activation, Issue/GL/stock posting, app code change or DEVELOPMENT/PRODUCTION activity is approved by this design. No fake Accounting approval references may be invented.

## 2. Decision principles and proposed state machine

Keep both B Expense (Company + exact leaf Item Group) and C Center (Company + beneficiary Department, current Department-only selector) company-scoped, with independent authenticated Finance Maker and Checker identities, no Administrator/Stockroom override and no native accounting-default fallback.

| Event | Initial condition | Proposed result | Financial effect |
| --- | --- | --- | --- |
| Maker proposes | Eligible new/revised scope | Draft revision; server-assigned revision number and owner | None |
| Checker reviews | Exact scope/revision, Checker grant | Return immutable intended facts and optimistic version token | None |
| **Checker rejects Draft** | Draft, unmodified since reviewed, independent Checker, mandatory reason | **Rejected terminal state** and durable rejection audit; keep immutable source/value/owner | **No activation**; never creates an active mapping |
| Checker approves (existing initial path, not authorized for test now) | Independent valid Draft + genuine Accounting evidence, nonoverlapping interval | Approved historical decision; Version audit; server-owned approval instant | May become effective prospectively |
| Maker requests retirement of Approved | Exact Approved revision, authorized Company, real reason and Accounting case | Pending retirement request, with immutable target and request version | None |
| **Independent Checker authorizes retirement** | Pending, separately reviewed request and current Approved target; full evidence validated | Immutable **accepted retirement event**, server-owned cutoff and audit | No new issues may use target at/after cutoff |
| Checker declines retirement | Pending request | Terminal declined request and audit, original Approved unchanged | None |

**Proposal, not a schema fact:** Add **Rejected** to revision state options, with server-owned rejected_by, rejected_at, rejection_reason and linked rejection audit, or a separately controlled rejection event with an equivalent terminal-state invariant. Avoid reusing revocation_reason (reserved for Approved lifecycle) as an ambiguous rejection field. The actual schema choice must receive separate owner authorization and index/migration review.

A rejected revision is never edited back into Draft or Approved. If correction is needed, the Maker creates **a new revision number within the same scope**, preserving the old rejected record and Version history. Require at most one pending review Draft per exact mapping scope, enforced under a stable Company/scope lock and appropriate durable database uniqueness mechanism; an ordinary revision_key uniqueness check alone is insufficient. The current propose_mapping path must be adapted for this rule at implementation time.

## 3. Recommended retirement model: append-only decision, computed cutoff

**Prefer a separate controlled retirement request plus immutable accepted retirement event**, not a direct state flip from Approved to Revoked and not deletion/rewrite of an Approved revision. Provisional conceptual records:

1. **Retirement Request**: request ID, kind (Expense/Center), immutable mapping_scope/revision and reviewed Company/source/value snapshot, requesting Maker, original approval decision/reference digest, reason, optional proposed future cutoff, created_at, decision status (Pending/Accepted/Declined), modified/version or content fingerprint. Pending requests are not effective.
2. **Retirement Event** (append-only once accepted): unique event/request key and idempotency key, exact target revision, approving independent Checker, validated genuine Accounting authorization reference (and protected evidence fingerprint), server-owned approved_at, effective_cutoff, human-readable reason, request ID, immutable snapshot, and linked Version/audit event. Do not allow ordinary edit/delete. One accepted retirement per Approved target unless separate owner-approved amendment rules are defined.

**Effective-time contract:** Use a **half-open [start, end)** interval. The effective retirement cutoff must not predate the server-owned retirement approval instant. If Accounting requested a later permitted cutoff, use that future instant; if immediate, use the server time while holding the lock. Never backdate an accepted retirement to alter past issue authorization. Define the applicable end of the approved revision as the **earliest** of its originally approved effective_until and any accepted retirement effective_cutoff. Original Approved status, original effective interval, approved_by/at/reference and historical version remain intact; “Retired” is **a computed view/state of the active interval**, not a destructive rewrite of the signed row.

**Race/anti-duplicate contract:** Every accepted request and derived event must be unique and idempotent: a retry of the *same* signed request should return the existing accepted event without a second cutoff/audit; a different payload or second accepted request for the same target must fail closed. Design durable unique keys for (kind, target_revision) for the accepted event, for request_id and caller-supplied idempotency token bound to authenticated actor + canonical payload digest. Define response semantics for network timeout followed by operator inventory before retry. No new approval may create an interval overlapping the **computed** active windows; overlap checks must be updated to account for accepted retirement events.

**Atomicity:** The transition Pending -> Accepted, insert accepted event, insert linked Version audit, and any controlled state projection must occur in one DB transaction, with no application-level intermediate commit. Fail if any audit insert or validation fails; caller rolls back the request. Ensure a failed request is not recorded as a successful event. The Version record is an ERPNext audit history, **not a tamper-proof external Accounting signature**.

## 4. Permissions, evidence, scope and optimistic review

- **Reject:** Only logged-in, enabled, Company-granted CCPC Accounting Mapping Approver may reject. The actor must be distinct from the revision creator. Require exact revision ID and expected_modified matching the *locked* Draft; require an explicit canonical nonempty rejection reason. No Administrator or Guest bypass and no Stockroom role.
- **Retirement request:** Propose Maker role with exact same target Company grant and eligibility to open a request. Maker cannot authorize their own request. No stockroom/requester role acting on behalf of Finance. Pending request is not executable approval evidence.
- **Retirement approval:** Require a distinct enabled Company-scoped Checker, exact target Company/scope/revision (do not trust client-supplied Company), current pending request fingerprint/version, retained original Approval decision and a genuinely authorized Accounting retirement decision reference. Authorizing Checker must be different from the request preparer; decide whether original mapping Maker/Checker independence must be revalidated only from historical signed evidence, not their **current** role membership.
- **Approval evidence:** Before any release, define authoritative Accounting evidence source, lookup/validation method, verifier, immutable snapshot/hash/ID, permission boundary and retention. A nonempty arbitrary string **is not** proof of authorization. Do not put actual financial attachments or private approvals in public GitHub.
- **Identity authority:** Check current roles and grants for actors performing **a new event**. Use immutable event-time identity/Company/approval provenance for historical decisions; do not invalidate historical truth because a former approver leaves the company. Keep read endpoints Company-scoped and never expose other Companies' evidence.
- **Review freshness:** A Checker must review exact target facts, request details and relevant existing retirements under stable locks. Reject stale expected_modified/fingerprint and conflicting concurrent actions, and require an independent review after material edits.

## 5. Concurrency, resolver correctness and historical transactions

**Stable lock order to be designed and tested:** Resolve Company from server-side target; acquire Company row lock, then exact Scope row, target Revision and relevant retirement request/event rows in deterministic order. Coordinate all prepare/approve/reject/retire paths; issue construction and Stock Entry before_submit already lock the Scope and revisions, so avoid reverse-lock acquisition and possible deadlocks. Verify transaction isolation, lock waits and durable uniqueness under real MariaDB concurrency.

**Resolver change required before retirement is deployable:** It must read accepted retirement events in the **same locked transaction** as selected Approved revisions. It should evaluate original Approved interval, approval instant, computed retirement cutoff, Company/scope/Item Group/beneficiary evidence and unique match. Re-evaluate at Stock Entry before_submit and at current wall-clock to prevent a stale pre-cutoff voucher from posting after cutoff; existing issue-time freshness checks must extend to event cutoffs. A mapper retired mid-issue must cause a safe fail/rollback, not post using an expired mapping. No silent default Account or Center on retirement, missing replacement or ambiguity.

**Historical ledger invariants:** Never mutate historical submitted Stock Entry Detail expense_account, cost_center, selected B/C revision IDs, Equipment provenance, Stock Ledger Entry or GL Entry. Returns/cancellations must follow separately approved historical provenance rules; retirement does not retroactively unpost transactions. If a retrospective replay/report needs an as-of mapping, it uses original Approved evidence and cutoff date, not the actor's current role grants.

**No Center fallback:** Retiring a sole Center mapping should cause future eligible issue postings to fail closed until a separately approved successor Center is active. Replacing an Expense or Center requires new explicit Maker–Checker mapping revision, Company eligibility and nonoverlapping **computed** intervals. A future-dated retirement does not authorize a future replacement by itself.

## 6. Failure, recovery and rollout safety

- If validation, evidence, Version/audit insertion or DB transaction fails: roll back everything; check the actual database before retrying a possibly ambiguous HTTP response. Use a stable idempotency key and explicit post-commit readback in integration tests.
- To correct a **mistaken retirement**, do **not** delete the accepted event, backdate it, or silently reactivate the old Approved revision. Require new Accounting decision and a new independently approved revision with prospective start, preserving both historical decisions.
- An immediate retire/overlap can block future stock issue; that is a deliberate fail-closed consequence requiring a documented operational pause/escalation, not a reason to use generic stock-adjustment defaults.
- Pre-deployment: targeted backup of all four Frappe components, manifest verification, restoration rehearsal in a disposable **isolated** environment and explicit rollback plan that respects any transactions after deployment. Existing local Integration2 snapshots are verified checksums but **restoration ability/off-host resilience have not been demonstrated**.
- Do not use old-site restore or direct UPDATE to reverse an approval/retirement on live financial data. For failed **schema deployment before use**, a separately approved tested rollback may be possible; after financial use, use controlled compensating/versioned Accounting decisions.
- DEVELOPMENT test and PRODUCTION release must each have distinct owner approvals. Preserve unknown uncommitted state and compare Git branch/commit, DB identity, backup and container/site scope before any site operation. Do not assume shared infrastructure is isolated.

## 7. Proposed implementation work packages — not authorized

1. **Design approval / Accounting gates:** Decide role delegation, who can reject/retire, evidence schema, immediate/future cutoff policy, event representation and historical query guarantees. Get written owner/Accounting signoff.
2. **Schema and migration review:** Draft field/schema/index changes (Rejected state, reject evidence and/or lifecycle request/event DocTypes), immutable constraints, required Company/Scope indexes, uniqueness/idempotency strategy, Version attachment, migration/backfill defaults and rollback compatibility. Avoid adopting this document as a migration approval.
3. **GitHub feature implementation:** On a separately selected app feature/review branch, add narrowly whitelisted reject Draft, create retirement request, decide retirement request, and read-only lifecycle review endpoints. Reuse strict actual Frappe role/Company authorization and stable lock ordering; never enable an Administrator shortcut.
4. **Runtime integration:** Update Expense and Center approved-interval resolution and before_submit cutoff validation; reconcile current historical _real_authority rechecks with signed event-time provenance. Preserve existing Stock Entry/GL and Decision A/D invariants.
5. **Adversarial tests / review:** Unit tests of pure policy with explicit mocked-vs-real labeling, real ERPNext v16/MariaDB transaction tests, Company-crossing and race/failure injection, and external Accounting evidence contract tests before a TEST/DEVELOPMENT fixture.
6. **Controlled integration/deployment:** Independently approve any code-to-DEVELOPMENT pull and any synthetic reject/retire API execution. Verify resulting Git commits and tests, then update handoff. PRODUCTION only with separate specific deployment/backup/recovery authorization.

## 8. Minimum acceptance matrix

| Test class | Required outcome |
| --- | --- |
| Checker rejects exact Draft after reviewing current token | Terminal Rejected + one durable audit; no mapping activation |
| Maker tries to reject; Checker tries own created Draft; disabled/wrong-Company/Stockroom/Guest | Denied, zero lifecycle changes |
| Stale token; forged Company; mismatched target, malicious reason/idempotency payload | Denied and unchanged |
| Concurrent reject-vs-approve; two reject calls; network timeout replay | Exactly one valid terminal decision; no duplicate Version or event |
| Declined/Pending retirement request | Approved target retains original effective behavior; zero accepted cutoff events |
| Two racing Checker retirement decisions; retire-vs-issue/approve | Serializable cutoff; one accepted event; no stock/GL after cutoff |
| Retirement at current/future time, timezone crossing, half-open boundary | Correct server-owned UTC comparisons; no backdating or overlap |
| Historical issue with now-disabled former approver; later return/cancel | Existing posted snapshots preserved; historical approvals readable from event-time evidence |
| Version/audit insertion failure or SQL exception | Whole request rolled back; retry/inspection safe |
| Real MariaDB schema/index upgrade and rollback before use | Explicit migration compatibility and no loss of existing Drafts/history |
| Role re-grant, retirement evidence update, Company scope change | Authorization rechecked for new event; old signed history immutable |
| Runtime Center retired without successor | Missing mapping causes safe fail closed; never implicit fallback |
| Postcommit readback after synthetic lifecycle tests | Correct Scope/Revision/Event/Audit cardinalities and zero unintended GL/stock changes |

## 9. Open decisions and acceptance gates

**OPEN (owner/Accounting):** precise state model and DocType/event schema; whether the Rejected state is added to both B/C revisions; identity and role of the retirement requestor; who signs retirement and whether second-level Accounting approval is necessary; authoritative approval/rejection/evidence registry; maximum future effective time and timezone policy; multiple-scope multi-center retirement handling; audit ownership, data retention, legal/Accounting evidence; idempotency key strategy; historical as-of and return/reversal behavior; version validity after personnel/role changes; and tested safe recovery path.

**Current decision:** Documentation-only design is drafted for review. Neither the existing synthetic Draft revision fieef2e44j nor any real expense/center crosswalk is authorized to be approved. Code implementation, schema migration and any runtime/database tests that write data require **subsequent specifically scoped owner approval**, relevant Accounting signoff, GitHub-first code review and separate DEVELOPMENT integration gates. PRODUCTION remains NO-GO.

## Owner follow-up decision: lifecycle design direction endorsed in principle (2026-10-28)

Following delivery of this GitHub-only design and the updated project handoff, the owner replied **"Approved."** This is recorded as approval of the **high-level rejection/retirement design direction** for continued controlled design review: terminal, audited Draft rejection; independent Maker–Checker retirement request and decision; immutable original approval plus append-only prospective cutoff; fail-closed runtime resolution and historical posting preservation.

**Interpretation boundary:** The owner's short confirmation did **not** settle the specifically enumerated open decisions in §9 (exact DocType/schema/index changes, user delegation/Accounting evidence authority, event-time cutoff policy, source of verifiable Accounting approvals, idempotency/rollback plan, or role changes). It did **not** approve any application code implementation, branch merge, schema migration, runtime state transition (including current synthetic Draft), GL/stock entry, DEVELOPMENT pull or PRODUCTION deployment. Those need explicit, concrete scope authorization and required Accounting decisions. Keep `fieef2e44j` Draft.

**Next recommended authorized deliverable:** A narrower **schema + Accounting governance specification for review** (fields, immutable event schema/indexes, rejection and retirement decision authority, evidence validation contract, exact cutoffs, audit and migration acceptance). Seeking approval to prepare this specification is distinct from permission to implement it.

## Detailed schema and Accounting governance companion (documentation only)

Following a further explicit owner approval **to prepare a detailed specification in GitHub for review only**, the companion [Finance mapping lifecycle schema and Accounting governance specification](FINANCE-MAPPING-LIFECYCLE-SCHEMA-ACCOUNTING-GOVERNANCE-SPEC-2026-10-28.md) was created on this documentation branch (commit `a50f181c1c25a22e9d8ac5df104ffe49bfcb8241`). It sets out *proposed*, not installed, rejection and retirement event/request fields, evidence verification rules, actor separation, transaction and uniqueness safeguards, forward-only effective cutoffs, migration requirements and test matrix. It explicitly preserves OPEN Accounting decision and approval gates. **No app implementation, schema installation, Finance record write or activation was authorized.**
