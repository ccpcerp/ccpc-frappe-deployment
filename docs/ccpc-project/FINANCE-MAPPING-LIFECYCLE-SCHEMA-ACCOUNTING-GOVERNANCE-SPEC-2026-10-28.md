# CCPC Finance B/C mapping — lifecycle schema and Accounting governance specification

**Prepared:** 2026-10-28 (Asia/Manila)  
**Status:** TECHNICAL POLICY DEFAULTS NOW SELECTED IN A LATER COMPANION; SPECIFICATION REMAINS UNIMPLEMENTED — DOCUMENTATION ONLY.  
**Authority:** Owner explicitly approved preparation of this detailed specification in GitHub for review only. That approval is NOT authority to select final signatories, implement code or schema, migrate, run Finance lifecycle endpoints, approve the synthetic Draft, or alter DEVELOPMENT/PRODUCTION.

## 1. Authoritative basis and unchanged runtime boundary

Review branch for application: ccpcerp/ccpcerp, review/circleci-isolated-erpnext-phase2-2026-10-26, verified HEAD **0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41**. Documentation branch: ccpcerp/ccpc-frappe-deployment, docs/ccpc-checkpoint-2026-10-10. Read together:
- [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md)
- [Integration2 authentication, Maker Draft and Checker review checkpoint](INTEGRATION2-FINANCE-AUTHENTICATION-CHECKPOINT-2026-10-27.md)
- [Owner-endorsed rejection and retirement concept](FINANCE-MAPPING-REJECTION-RETIREMENT-LIFECYCLE-DESIGN-2026-10-28.md)
- [B/C Accounting approval design](WITHDRAWAL-B-C-ACCOUNTING-APPROVAL-AND-CENTER-SELECTION-DESIGN-2026-10-18.md)
- [Current mapping workflow source](https://github.com/ccpcerp/ccpcerp/blob/0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41/ccpcerp/ccpc_erp/bc_mapping_workflow.py)

Current **EXISTING** four DocTypes are CCPC Expense Mapping Scope, CCPC Expense Mapping Revision, CCPC Center Mapping Scope and CCPC Center Mapping Revision. Expense scope holds Company, exact leaf Item Group and unique scope_key; Center scope holds Company, beneficiary Department, selector_kind, selector_key and unique scope_key. Both revisions hold mapping_scope, revision_no, expense_account or cost_center, approval_state, effective_from, effective_until, approval_reference, approved_by, approved_at, supersedes, revocation_reason and unique revision_key. Existing approval_state options are **Draft / Approved / Superseded / Revoked**, not Rejected. Current revision DocType permissions arrays are empty; ordinary controller validation rejects non-Draft edits. Current workflow provides propose_mapping, get_mapping_review and approve_mapping; no reject/retire endpoint. Current approve_mapping checks a text approval_reference syntactically, but does not verify genuine Accounting decision evidence. The issue runtime selects Approved intervals and at present also rechecks actors' *current* roles even for old approved decisions.

**Last verified Integration2 test facts** (operator-run read-only checks, not a new live lookup): TISS synthetic Expense Scope **fie8da5c59** and Maker-owned Revision **fieef2e44j**, revision 1, remained Draft after independent Checker review. Zero associated GL and Stock Entry Detail references, zero Items linked to synthetic leaf Item Group, no synthetic Center scope, zero Version approval audit. No activation is authorized.

Use **EXISTING** for pinned-code facts, **PROPOSED** for field and service candidates below, and **OPEN** for choices still requiring a formal owner/Accounting decision.

## 2. Decision and lifecycle model — PROPOSED

| Action | Preconditions | Outcome | Financial effect |
| --- | --- | --- | --- |
| Maker proposes | Named Company-authorized Maker, eligible exact Scope and master | Draft with immutable server owner and revision number | None |
| Checker reviews | Named Company-authorized Checker; exact current version | Scope and proposal facts with modified/fingerprint | None |
| Checker rejects Draft | Independent Checker, locked unchanged Draft, reason, possibly Accounting decision evidence | **Terminal Rejected**; one immutable audit event | Never activates |
| Checker approves Draft | Separate formal Accounting evidence, authorized independent Checker, fresh Draft, no overlaps | Existing Approved revision plus verified approval/audit | Prospective eligible mapping |
| Maker opens retirement request | Target is Approved and unchanged, Company grant, reason and proposal cutoff | Pending request | None |
| Checker declines retirement | Independent authorized reviewer with request version | Terminal Declined request and audit | Approved mapping unchanged |
| Checker accepts retirement | Independent Checker, verified Accounting retirement decision, locked target/request | Immutable accepted event with prospective cutoff | No future issue may use target on/after cutoff |

**OPEN:** Whether revision state should include Rejected versus an event-only terminal state, whether rejection requires formal Accounting signoff, and whether retirement requestor must be the original Maker. The proposed state machine must not allow Rejected → Draft/Approved, or allow silent changes to approved source/value/approval history.

**Historical rule:** Original Approved revision, its approval identity/reference, and historical effective interval remain unchanged. An accepted retirement event is append-only; the resolver computes the cutoff rather than rewriting Approved to Revoked. Direct status flips would make the current resolver drop that row for historical as-of queries and are therefore not recommended.

## 3. Proposed additive revision schema

Apply analogous changes to **both** Expense Mapping Revision and Center Mapping Revision after separate schema authorization.

| Candidate field | Type | Validation / invariants |
| --- | --- | --- |
| Existing approval_state adds Rejected | Select | Terminal transition only through guarded Checker service; keep existing states compatible |
| rejected_by | Link/User, read-only, no_copy | Actual logged-in Checker; never accept from HTTP |
| rejected_at | Datetime, read-only, no_copy | Server-owned site-local timestamp with UTC-aware comparisons |
| rejection_reason | Small Text, read-only | Required and bounded; redact sensitive business details in logs |
| rejection_event | Link/CCPC Mapping Rejection Event | Exact immutable decision-event identity |
| review_fingerprint (optional) | Data length 64 | Canonical reviewed scope/value/owner/interval hash; alternative is locked computed hash with modified token |

Reject service must atomically update state, rejected_by/at/reason, modification/version token, insert rejection event and Version audit. Do not allow ordinary DocType create/save/db_set to bypass the authenticated transition. If two requests race (reject vs approve), only one terminal result can commit; stale retries return an explicit conflict or verified idempotent prior result.

**Unresolved Draft cardinality:** Recommend at most one unresolved Draft per Scope, enforced by a stable Company/Scope lock and a durable compatible uniqueness mechanism. Existing unique revision_key alone prevents duplicate revision numbers for a derived key, not necessarily multiple unreviewed revisions. A MariaDB partial unique index cannot be assumed to exist: design actual constraint/test plan before migration.

## 4. Proposed new immutable lifecycle DocTypes

Use a fixed allowlist mapping_kind = Expense or Center and **two explicit optional revision Links** to the respective DocTypes. Validate exactly one non-null target and kind match, rather than accepting arbitrary client-supplied SQL table names or a forged Company. All Company, Scope, source, value and original approval data must be derived from locked server records. New DocTypes require explicit schema design/index review; **none exist under this authorization**.

### 4A. CCPC Mapping Rejection Event (PROPOSED)

| Field (candidate) | Type | Rule |
| --- | --- | --- |
| mapping_kind | Select Expense/Center | Server-verified family |
| expense_revision, center_revision | Link to respective Revision | Exactly one target; opposite null |
| target_key | Unique Data(64) | Canonical hash of kind + exact target: one rejection event per revision |
| company, scope_identity, source_value_snapshot | Link or typed Link(s), Data | Server-derived and immutable; exact typed scope Link decided at schema review |
| prepared_by, rejected_by, rejected_at | Link/User, Link/User, Datetime | Maker vs independent Checker; server-owned instant |
| requested_modified, reviewed_fingerprint | Data, Data(64) | Bound to reviewed Draft content and optimistic token |
| rejection_reason | Small Text | Mandatory, nonempty, bounded reason |
| evidence_id (optional policy gate) | Evidence registry Link | OPEN for rejection whether Accounting approval required |
| event_fingerprint, version_audit | Unique Data(64), Link/Version | Same-transaction audit and immutable snapshot |

No ordinary update/rename/delete. One accepted rejection can be expressed only once for its revision. A correction is a **new Draft revision_no** in the same Scope.

### 4B. CCPC Mapping Retirement Request (PROPOSED)

| Field (candidate) | Type | Rule |
| --- | --- | --- |
| mapping_kind, expense_revision, center_revision | Select + typed Links | Exactly one exact Approved target |
| request_key | Unique Data(64) | Stable idempotency key bound to canonical payload and authenticated requestor |
| company, scope_identity, reviewed_value | Links/Data snapshot | Server-derived from target |
| requested_by, requested_at, reason | Link/User, Datetime, Small Text | Maker, server instant and mandatory justification |
| proposed_cutoff | Datetime | Optional future cutoff, no automatic effect when Pending |
| target_approval_fingerprint | Data(64) | Binds original decision and intended immutable target |
| expected_modified, request_fingerprint | Data, Data(64) | Staleness and tamper prevention |
| evidence_id | Evidence registry Link | OPEN whether required at submission or only acceptance |
| request_state | Select Pending/Accepted/Declined | No normal edits; only controlled independent Checker decision |
| decided_by, decided_at, decision_reason | Link/User, Datetime, Small Text | Required once terminal |
| accepted_event | Link/CCPC Mapping Retirement Event | Only for accepted request, unique |

Alternate schema to evaluate: immutable request + separate immutable decision event, rather than updating request_state. Any pending or declined request has **zero** effect on Expense/Center resolution.

### 4C. CCPC Mapping Retirement Event (PROPOSED)

| Field (candidate) | Type | Rule |
| --- | --- | --- |
| mapping_kind, expense_revision, center_revision | Select + typed Links | Exactly one Approved target |
| target_key | **Unique Data(64)** | One accepted retirement per kind + revision (unless amendment policy later approved) |
| retirement_request, request_key | Link, Data(64) | Exact accepted request; unique accepted association |
| company, scope_identity | Typed scope/company Links | Server-derived immutable snapshot |
| target_approval_fingerprint | Data(64) | Identifies original Approved decision to which cutoff applies |
| requested_by, accepted_by, accepted_at | Link/User, Link/User, Datetime | Independent Maker/Checker and server instant |
| effective_cutoff | Datetime | Server-owned, non-backdated; must be >= accepted_at |
| reason | Small Text | Mandatory reviewed reason |
| evidence_id, evidence_fingerprint | Evidence Link, Data(64) | Verified Accounting decision, not free-text token |
| event_fingerprint, version_audit | Unique Data(64), Link/Version | Immutable decision and durable audit |

Do not delete accepted events to undo a mistake. A corrected future mapping requires **new** Maker–Checker approved revision and Accounting evidence; old vouchers remain untouched. Whether Superseded/Revoked are maintained as legacy labels or have independent event semantics remains OPEN.

## 5. Proposed Accounting evidence system and governance

**Mandatory design objective:** Current syntactic approval_reference is **not proof** that Accounting approved a real Company/scope/value/cutoff. Add a verifier with a trusted record lookup, evidence retention and exact target binding, not a permissive nonempty string. Either approve a small **CCPC Accounting Decision Evidence** DocType as a controlled immutable registry or a validated adapter to an already authoritative Accounting register; **do not assume either exists**.

Candidate evidence fields: source_system, external_decision_id, decision_version, decision_type (ExpenseApprove, CenterApprove, ExpenseRetire, CenterRetire), Company, mapping_kind, revision ID, Scope key, selected Account/Center value, decision_status, authorized_signatory, signed_at, approved effective/cutoff bounds, source_document_digest, verified_by, verified_at, verifier_version, immutable evidence_fingerprint, and superseding/correction provenance. Unique identity on (source_system, external_decision_id, decision_version) with an explicit policy for corrections and non-reuse. Store actual private Accounting attachments **outside public GitHub**.

Verifier at **event decision time** must confirm: authentic source, authorized signatory for that Company and decision type as of decision time, exact target/scope/value, permitted effective interval/cutoff, unrevoked status and immutable evidence fingerprint. A decision signed for TREQ, another Item Group/Account/Center or another revision is ineligible for TISS. A Checker with a syntactically valid but fabricated reference is denied. Historical signed evidence should not depend on former signatory retaining a current ERPNext role.

**Proposed actor matrix; actual signatories/delegation OPEN:**

| Action | Required current authority | Independent/separation rule |
| --- | --- | --- |
| Draft create | Enabled named CCPC Mapping Preparer + exact Company grant | Never Stockroom, Guest, or Admin override |
| Draft review | Enabled named CCPC Accounting Mapping Approver + Company grant | Read only, Company-scoped |
| Draft reject | Same authorized Checker + reason + reviewed current token | Not Maker rejecting own Draft |
| Draft approve | Authorized independent Checker + validated Accounting approval evidence | Distinct from Maker; no arbitrary reference |
| Retirement request | Company-authorized Maker + target fingerprint + reason | Cannot approve own request |
| Retirement accept/decline | Independent Company-authorized Checker + fresh request; accept requires verified Accounting retirement authority | Separate requestor/Checker, no cross-Company |
| Audit inspection | Specifically authorized Finance auditor with scope-filtered read | No financial edit/create/approve permission |

Before implementation, **Accounting and owner must decide** the authoritative approval registry, identities/delegation, evidence validation service, mandatory vs optional rejection signoff, decision retention and correction rules, and whether extra two-level Accounting approval is required.

## 6. Effective-time semantics, resolver, locking and duplicate prevention

**Proposed time semantics:** half-open UTC intervals [start, end). Existing approval starts no earlier than actual server approval. Accepted retirement event cutoff >= server acceptance timestamp. Actual resolver end for an original Approved revision is min(original effective_until, accepted retirement cutoff), where absent original end is infinite. If the computed end <= original start, fail closed and require a separately authorized Accounting cancellation policy; never silently manufacture historical effect. Normalize Frappe site-local Datetime using configured site timezone; handle midnight/DST transitions in tests.

**Historical integrity:** Keep Approved state and original approved_by/at/reference, value and original time interval **immutable**. At linked Material Issue construction and before_submit, lock Scope, Approved revision and accepted event, test **both** voucher posting time and current server time against cutoff, and reject if mismatched/stale. No default stock adjustment expense Account or Cost Center. If retiring the only Center, future issue posting fails closed until a new independently approved Center is effective. Past Stock Entry Detail, GL Entry, SLE, revision and Equipment provenance are never rewritten. Returns/cancellations need separate signed historical-provenance rules.

**Concurrency:** Resolve Company only as initial locator; stable lock order should be Company → Scope → revision(s) → request/event/evidence under actual InnoDB row locks, with deterministic ordering across B/C and Stock Entry before_submit. Recheck state, tokens, evidence and overlap **under lock**. The current authority helper also acquires User/Role/Permission locks before Company; reconcile that actual order explicitly in a real MariaDB deadlock study. No unbounded scanning. Race with issue/retirement must either serialize or fail closed, never post against a post-cutoff mapping.

**Proposed durable key/index review:**
- Retain existing unique Scope scope_key and Revision revision_key.
- Consider unique (mapping_scope, revision_no) on both revision families, only after inspecting existing data and Frappe naming behavior.
- One unresolved Draft per scope: evaluate transactional guard + MariaDB-compatible unique strategy; do not assume a partial unique index exists.
- Unique rejection event target_key and immutable event_fingerprint.
- Unique Retirement Request request_key; index target + request_state.
- Unique accepted Retirement Event target_key and accepted request reference, index by exact revision/Scope for resolver locks.
- Evidence unique (source_system, external_decision_id, decision_version), verified target binding, Company and decision-type lookup indexes.
- Verify indexes, collation, null Link semantics, lock orders, write races, migration uniqueness and rollback implications with **real** MariaDB; these are not current installed constraints.

**Idempotency:** Bind request_key to authenticated actor + action + canonical payload fingerprint. A retry of *identical* already accepted request must return the existing event without inserting another cutoff or Version; a reused key with changed payload must reject. Ambiguous HTTP timeout requires a **read-only postcondition inventory before any repeat**. One accepted retirement per target, one terminal reject/approve per Draft; no duplicate approval/Version/GL.

**Atomic service contract:** Whitelisted methods enforce actual session role/Company, independent identities, expected_modified or content hash, locked target validity and verified Accounting evidence; in one Frappe transaction write accepted state/event and Version audit, validate result, and let request transaction commit only if all succeed. Audit failures, constraint errors and time conflicts must roll back the whole request. Neither raw SQL nor ignore_permissions may become a bypass for server-side authority. Do not claim Version audit is cryptographically tamper-proof.

## 7. Migration, recovery and tests — acceptance proposal

**Safe ordered delivery subject to separate approval:** finalize owner + Accounting decisions; implement only on a dedicated reviewed GitHub app branch; analyze current MariaDB schema and existing data read-only; add schema/indexes additively while preserving older Draft/Approved records; test migration against real disposable isolated v16/MariaDB; update resolver **before** accepting retirement events (avoid older worker treating retired revision as active); perform independently approved DEVELOPMENT integration with backups and exact Git status; stage bounded synthetic lifecycle tests; update GitHub handoff; independently review release/rollback; PRODUCTION only with separate explicit authorization.

**No silent backfill** of rejection, revocation, Accounting evidence or signatures. No destructive down-migration or site restore over subsequent finance postings. Current local Integration2 four-part backups passed checksums, **not** off-host restore rehearsal. Approve any restore, migration, Docker/restart or production modification separately.

| Test scenario | Required outcome |
| --- | --- |
| Maker Draft, real independent Checker rejects correct token | Exactly one Rejected revision/event/Version; no activation or financial posting |
| Unauthorized Maker reject, wrong Company, disabled actor, Guest/Admin, Stockroom | Fail closed, no changes |
| Forged Company/value, stale modified token, changed request fingerprint | Fail closed; preserve original |
| Concurrent approve-vs-reject, two rejects, HTTP replay | Exactly one terminal decision and event/audit |
| Version insertion failure on rejection/retirement | Full transaction rollback; safe read-only reconciliation |
| Retirement request Pending or Declined | No change to Approved effective interval |
| Retirement accepted by authorized independent Checker with exact evidence | Exactly one immutable event, audit and prospective cutoff |
| Concurrent retirement/issue before_submit and approval | Serialize/fail closed; no post-cutoff issue |
| Future cutoff, server/site timezone, half-open boundary and no backdating | Deterministic UTC effect |
| Historical voucher after signatory User disabled | Historical record and audit preserved without current-role dependency |
| Invalid/reused/wrong-Company/signed-by-wrong-person Accounting reference | Rejected; no fictitious approval |
| Retiring sole Center / multi-center ambiguous selector | No fallback; future issue denied |
| Real ERPNext/MariaDB index conflict, upgrade/rollback compatibility | Safe migration or STOP without data loss |
| Postcommit independent inventory | Exact expected row counts; zero unexpected Stock/GL/master changes |

Report mock/pure unit results separately from real DB integration results. Each approved write test must state exact site, backup manifest, reviewed app HEAD, scope/revision/event IDs and independent postcommit readback; no secrets or business-data attachments in GitHub.

## 8. Owner/Accounting decision register — all OPEN until separately resolved

| Gate | Decision needed |
| --- | --- |
| G1 | Add Rejected to both revision states, or event-only terminal representation |
| G2 | Approve or modify proposed rejection, retirement request, retirement event schemas/field names |
| G3 | Who may request retirement; whether current Checker may decide; second-level Accounting signature requirements |
| G4 | Authoritative Accounting decision register, signatory verification, evidence storage/privacy and correction policy — **release blocker** |
| G5 | Mandatory rejection evidence vs explanation; escalation/rework after rejection |
| G6 | Immediate or future retirement cutoff, lead time, timezone, and never-activated approvals |
| G7 | Unique pending Draft/request policy, idempotency and race semantics |
| G8 | Historical approval verification after personnel changes; returns/cancellations |
| G9 | Exact keys/indexes and migration/rollback compatibility, shared worker release order |
| G10 | Restore rehearsal, backup/off-host recovery and operational stock-issue fail-closed response |
| G11 | Real Company/category→Account and Department→Center crosswalk and named Accounting approval actors: **not supplied** |
| G12 | App implementation branch, code/tests, DEVELOPMENT pull/migrate, PRODUCTION release: **separate explicit approvals** |

**Decision boundary:** This specification records candidate implementation details only. It does **not** install fields/DocTypes, determine Accounting signatories, validate crosswalks or authorize the existing synthetic Draft revision fieef2e44j to be rejected, approved or retired. Do not run any change in Integration2, main DEVELOPMENT, or PRODUCTION as a consequence of this document.

## 9. Subsequent owner-delegated technical policy selection — 2026-10-28

**New authoritative technical policy companion:** [Finance Mapping Accounting Authority Decision](FINANCE-MAPPING-ACCOUNTING-AUTHORITY-DECISION-2026-10-28.md), committed on this documentation branch as `2c4f0bd05a01e2d028f9f48242a0581826e989e0` after the owner instructed **"Approved decide it yourself."** This document's §8 decision register describes the questions as they stood when this specification was authored; it must now be read with the later decisions, not interpreted as still totally undecided.

**Resolved as technical defaults only (G1–G10):** Add terminal Rejected to both B/C revisions; use immutable Rejection Event, Retirement Request and Retirement Event; Maker requests / distinct Checker signs and decides; **CCPC ERPNext internally signed Accounting Mapping Decision** as sole mapping-decision evidence source, with exact Scope/revision/Company/value/fingerprint; signed once, consumed once via unique Decision Use and committed atomically with Version; Checker with named role and Company grant (no automatic personnel assignment); reason-only rejection; **immediate, server-owned non-backdated retirement cutoff only in MVP**; one Draft/request/retirement per exact applicable key; event-time immutable history; additive schema plus real MariaDB/rollback tests and fail-closed accounting resolver. Existing text approval_reference alone is not proof.

**Still not resolved or authorized (G11–G12 and implementation subdetails):** No real Company/category→Account or Department→Center crosswalk; no named real production approver, new role grant or actual signed evidence; precise field/index migration and API implementation have not been reviewed or authorized; no site code/data change, test write, approval/activation, main DEVELOPMENT pull or PRODUCTION deployment. **Synthetic TISS Scope fie8da5c59 / Revision fieef2e44j remains last verified Draft.** Technical document approval cannot substitute for genuine operational Accounting authorization.
