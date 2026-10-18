# CCPC Withdrawal Slip Material Issue — Decisions B/C Accounting mapping approval worksheet

## Initial mapping intake workbook prepared — read-only masters required

The owner asked to prepare the initial B/C mapping table for review. A 9-sheet **unapproved candidate Excel workbook** (`CCPC_BC_Initial_Financial_Mapping_Review_2026-10-18.xlsx`) was generated as a chat attachment, with empty B/C financial mapping rows, 5 blank Company/Item Group/Account/Department/Cost Center intake tabs, review readiness checks and a maker–checker signoff log. It is **not a signed or activated financial mapping and is not stored as a GitHub binary**.

[Verified minimum-field master intake requirements and handling rules](WITHDRAWAL-B-C-INITIAL-MAPPING-MASTER-INTAKE-2026-10-18.md). The actual current Company, exact **leaf** Item Group, eligible Expense Account, beneficiary Department and active Company Cost Center names cannot be verified from reviewed GitHub records; use **authorized read-only ERPNext master exports**, not example names or CI fixture defaults. Do not upload sensitive exports to public GitHub issues. **G4 rows below remain entirely TO BE PROVIDED / NOT APPROVED** until the exact candidate mapping crosswalk receives authorized Accounting signoff.

## Open Accounting signoff tracker — GitHub Issue #25

[**Issue #25: B/C Accounting authority, effective rules, explicit Center selection and signed mappings**](https://github.com/ccpcerp/ccpc-frappe-deployment/issues/25) is the **OPEN** tracked gate for unresolved G1 role/Company/user authority, G2 activation/cutover/retrospective posting/effective-time and revocation policy, G3 Slip-or-line center choice and Section behavior, and actual G4 Company/leaf Item Group→Expense Account and Company/beneficiary Department→Cost Center approved crosswalks. Opening the issue is **not** Accounting approval and does not supply mapping rows. Keep any sensitive real business data/identities in appropriately access-controlled records; do not include credentials, production exports, or unreviewed private data in issue comments.

**Next authorization boundary:** signed exact Accounting decisions, approval actors, mapping exceptions and financial masters must be verified before approval transitions, selector hookup or Stock Entry/GL posting logic is enabled. **POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.**

**Prepared:** 2026-10-18. **Status: DRAFT FOR ACCOUNTING SIGN-OFF; NO MASTER MAPPINGS APPROVED HERE.**  
**Scope:** Original controlled Withdrawal Slip → submitted Stock Entry `Material Issue`, downstream source-linked physical return design. **Not** an instruction to edit Company, Item, Item Group, Department, Cost Center, stock, GL, DEVELOPMENT or PRODUCTION.

## Owner-approved G1–G3 design principles — actual Finance assignments and rows still pending

On 2026-10-18 the owner expressly **APPROVED the G1–G3 design principles for a GitHub-only review**, as recorded in the [owner decision](WITHDRAWAL-B-C-G1-G3-DESIGN-OWNER-APPROVAL-2026-10-18.md). This approves (G1) independent preparer/Accounting approver design; (G2) immutable reviewed revisions with auditability and no retroactive posted-ledger rewrites; and (G3) positive explicit eligible signed C revision selection for multi-center Departments, with Slip-level choice as the starting *review design* and no implied Section financial-key rule.

**Still not authorized:** specific mapped Companies/accounts/Cost Centers; actual named approvers or ERPNext roles, Company permissions and user grants; approval-state activation, effective-date/backposting cutoffs, live audit-event storage, G3 selector field/Section/key granularity and exception authority. **All blank B2/C1 Accounting crosswalk rows below remain TO BE PROVIDED / NOT APPROVED.**

[App draft PR #18](https://github.com/ccpcerp/ccpcerp/pull/18) contains only pure G1–G3 policy functions with static unit test source, on top of unmerged draft PR #17. **No verified CI result for PR #18** and no live workflow, Stock Entry/GL integration or release approval.

## Accounting approval and multi-center selector design pending signoff

A specific [maker–checker approval lifecycle, revision-effective-time and explicit beneficiary Cost Center selection proposal](WITHDRAWAL-B-C-ACCOUNTING-APPROVAL-AND-CENTER-SELECTION-DESIGN-2026-10-18.md) is ready for owner and Accounting review. **It is not approved**: no Accounting users/role permissions, activation/revocation method, audit-event storage, Cutoff timezone, Section policy, or selector field is authorized. The proposed model deliberately separates **one Department-only Center** from **multiple valid Center choice scopes**; the latter needs a distinct explicitly approved selection scope and positive choice of an eligible signed revision. The current PR17 design **still refuses all activation and explicit multi-Center scopes**.

**Approval steps G1–G3 outstanding:** name the authorized preparer/independent approver and Company scope; approve immutable revision lifecycle/interval and revocation controls; decide whether the selector belongs to the whole Slip or item rows and whether `work_for_section` is informational or part of the financial scope. **B2/C1 signed actual financial mappings are still TO BE PROVIDED/NOT APPROVED.** Do not enable accounts or cost allocation because this design has been documented.

## Owner-approved schema review implemented as draft PR #17 (2026-10-18)

The owner [approved the detailed four-DocType scope/revision design for inert GitHub review](WITHDRAWAL-ISSUE-B-C-SCHEMA-DESIGN-OWNER-APPROVAL-2026-10-18.md), including **exact leaf Item Group without automatic parent inheritance** and the rule that multiple eligible Centers require **positive, validated explicit approved C revision selection** (the actual Section/UI/selection authority remains unapproved). [App draft PR #17](https://github.com/ccpcerp/ccpcerp/pull/17) now holds four inactive, draft-only schema/controller definitions; see [PR17 review checkpoint](WITHDRAWAL-B-C-MAPPING-SCHEMA-GITHUB-REVIEW-CHECKPOINT-2026-10-18.md). The static schema run passed; disposable Frappe/MariaDB schema tests must be verified separately.

**No actual Accounting crosswalk entries have been approved here.** All live Company/category→Account and Company/beneficiary Department→Center rows below stay **TO BE PROVIDED / NOT APPROVED**. PR #17 does not authorize material issue posting or DEVELOPMENT/PRODUCTION deployment.

## Detailed schema proposal ready for review (2026-10-18)

The [specific B/C mapping schema and transaction-control design proposal](WITHDRAWAL-ISSUE-B-C-MAPPING-SCHEMA-AND-CONTROL-DESIGN-PROPOSAL-2026-10-18.md) is now available for owner/Accounting review. **Proposed, NOT APPROVED:** four logical DocTypes (two unique stable mapping scopes plus immutable B/C revision records), per-company Account/Cost Center eligibility, audited approvals, effective intervals, overlap checks under scope-row locks, selected revision IDs on original issue rows, and before-submit anti-forgery revalidation.

**Proposed but NOT APPROVED choices:** use exact Item Group as material-category authority without automatic parent inheritance; explicitly select a specific signed C revision if multiple Cost Centers apply; decide whether `work_for_section` is a selection key and enforce appropriate locking only if it is approved. The document includes a review checklist for schema, permissions, effective timestamps, exceptions and cutover. **The real B/C mapping tables in this worksheet remain blank and unsigned.**

## Owner approval: controlled, versioned B/C mapping arrangement (2026-10-18)

The project owner **approved the controlled, versioned, company-scoped CCPC accounting mapping arrangement**. [Authoritative architecture decision and its exact boundary](WITHDRAWAL-ISSUE-B-C-VERSIONED-MAPPING-ARCHITECTURE-APPROVED-2026-10-18.md).

- **Approved architectural choice:** B and C allocations must be based on explicit, approved, versioned CCPC-controlled mapping records, with suitable audit history and fail-closed missing/ambiguous selection. Do **not** treat standard ERPNext account or Cost Center defaults as approved simply because they are populated.
- **Not approved by this architecture decision:** actual Company/category→Expense Account rows, Company/beneficiary Department→Cost Center rows, category precedence, Section/selector, exact mapping DocTypes/field schema, permission/approval workflow, role assignments, effective-time semantics, exceptions, migration, application posting integration or site deployment.
- The blank B/C rows in sections 1–2 below **still require Accounting approval**. The [B/C implementation readiness record](WITHDRAWAL-ISSUE-B-C-IMPLEMENTATION-READINESS-AND-APPROVAL-GATE-2026-10-18.md) now treats the architecture as selected and keeps detailed BC1 schema/governance choices open.

## Latest joint A+D review and B/C readiness (2026-10-18)

- [Joint app draft PR #16](https://github.com/ccpcerp/ccpcerp/pull/16) at `827993e45ae9321e7a936f48f7fc3b17bf842099` reconciles PR #14's beneficiary Department with PR #15's Equipment-at-issue snapshots; all four isolated regression groups passed **72 mocked + 13 real Accounting/GL + 12 mocked Equipment + 13 real Equipment/SLE/GL tests**. **This is not evidence of approved Company/category expense-account or beneficiary Department→Cost Center mapping.** PR #16 remains draft/unmerged.
- [B/C implementation-readiness and explicit decision register](WITHDRAWAL-ISSUE-B-C-IMPLEMENTATION-READINESS-AND-APPROVAL-GATE-2026-10-18.md) records which existing fields are reusable, unresolved B/C master authority/Section/selector decisions, an optional versioned mapping architecture **for approval**, source-lock implications if `work_for_section` is adopted, and detailed fail-closed test expectations. **No new mapping or schema has been approved.**
- The remainder of this worksheet remains the blank, authoritative **request for actual Accounting approval**, not an import of default ERPNext settings or personal notes.

## Verified current code and test boundary

- [Decision A review PR #14](https://github.com/ccpcerp/ccpcerp/pull/14) on `review/withdrawal-issue-accounting-ci-2026-10-17` at `ebeec379f623e8596c1d178ad7b45d0f8859c2e5` is **draft and unmerged**. [Disposable CI 39097918235](https://github.com/ccpcerp/ccpcerp/actions/runs/39097918235) passed **72 mocked + 13 real Frappe/ERPNext/MariaDB** tests, including actual expense GL beneficiary Department propagation.
- Current `withdrawal_slip_stock._build_material_issue` sets row Item, quantity, warehouse, provenance and the resolved beneficiary Department, but **does not independently select an Accounting-approved expense account or Cost Center**. `validate_withdrawal_slip_stock_entry` checks the Department before submission but does not compare row `expense_account`/`cost_center` to approved CCPC mappings.
- Existing real GL test asserts populated expense account/Cost Center and a matching GL debit using **synthetic native defaults** (`Stock Adjustment - _TC`, `_Test Cost Center 2 - _TC`). This is **not** evidence those defaults are approved for any CCPC live Company/category/Department. An ordinary or direct Stock Entry with an unsuitable default or overridden account/center has **not** passed an Accounting-mapping safeguard.
- Owner-approved policies: [Decision B](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-B-APPROVED-2026-10-18.md), [Decision C](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-C-APPROVED-2026-10-18.md). **Policy is approved; the actual mapping records, schema/authority and exception workflow are not.**
- [Draft PR #15](https://github.com/ccpcerp/ccpcerp/pull/15) separately adds Equipment-at-issue snapshots and a gross issue-value report. Do not merge its overlapping builder changes blindly or represent gross issues as net maintenance cost.

## 1. Decision B — Company and material/item category to expense account

Accounting should fill one row **for every approved scope**, including exceptional categories. Values below are **field labels, not actual CCPC records**.

| Company (exact ERPNext name) | Category identifier and authority (e.g. approved Item Group; specify hierarchy rule) | Exact approved expense Account (ERPNext full name) | Effective from / through | Accounting approver / decision reference | Status |
| --- | --- | --- | --- | --- | --- |
| **TO BE PROVIDED** | **TO BE PROVIDED** | **TO BE PROVIDED** | **TO BE PROVIDED** | **TO BE PROVIDED** | **NOT APPROVED** |

Accounting decision points to record before code selection:
1. Which existing CCPC record is **authoritative** for material category: Item Group, Item-specific override or a separate controlled category? Specify hierarchy, parent-category inheritance, priority, and whether a company-specific override is allowed. **None is automatically endorsed here.**
2. Can `Company.stock_adjustment_account` ever be an approved consumption expense account? If yes, explicitly identify the Company, category, account and approval; **otherwise reject it as a silent fallback**.
3. For missing, overlapping, expired, blocked or mismatched accounts, posting **must stop** pending an auditable Accounting decision; no arbitrary or first-match fallback.
4. Confirm expense ledger suitability for the Company: existing **non-group, active, appropriate P&L account** and any applicable ERPNext account restrictions. The specific exception-authorizing role/procedure is undecided.

## 2. Decision C — Company and actual beneficiary Department to Cost Center

| Company (exact ERPNext name) | Beneficiary Department (exact name) | Approved Cost Center (ERPNext full name) | Selector / Section rule if more than one | Effective from / through | Accounting approver / reference | Status |
| --- | --- | --- | --- | --- | --- | --- |
| **TO BE PROVIDED** | **TO BE PROVIDED** | **TO BE PROVIDED** | **TO BE PROVIDED** | **TO BE PROVIDED** | **TO BE PROVIDED** | **NOT APPROVED** |

Accounting decision points:
1. Determine whether a beneficiary Department has exactly one approved active leaf Cost Center, or several; for multiple centers define **the mandatory explicit selector** and who can validate it. Never pick the first candidate or infer by name.
2. Decide whether **Section** participates in allocation, and which source field records the selection as immutable/auditable issue intent.
3. Confirm Company ownership and active/non-group Cost Center at posting time; reject disabled, foreign-company, expired, missing, ambiguous or unsupported allocations.
4. No fallback to the requesting Department's center or a generic Company default unless that exact mapping is affirmatively approved for the **beneficiary**.

## 3. Implementation choices requiring separate owner/Accounting sign-off

- **Mapping authority/storage:** **owner approved the controlled, versioned CCPC company-scoped mapping arrangement** rather than implicit ERPNext default selection. **Still to approve:** exact record/DocType schema, revision and approval lifecycle, roles/permissions, effective-dating semantics, migration impact and how any approved native master reference is validated. See [architecture decision](WITHDRAWAL-ISSUE-B-C-VERSIONED-MAPPING-ARCHITECTURE-APPROVED-2026-10-18.md).
- **Snapshot and enforcement:** for each line resolve approved account and Cost Center before issue insert; store on Stock Entry Detail; at `before_submit` resolve/revalidate against the locked source and approved effective mapping; reject user-forged or cleared rows and mismatched source. Require actual GL debit to carry approved expense Account, Cost Center and Decision A Department. Avoid permission escalation to edit financial selections.
- **Locking and change safety:** detect mapping changes between issue construction and submission; define whether approval records are immutable once referenced or versioned; preserve original actually **posted** account/center for later physical-return expense credit even if current mapping changes.
- **Exceptions:** Accounting-approved review/override trail, scope and authorized users; no arbitrary correction account, custom duplicate GL posting, or historical backfill without separately approved design.

## 4. Required isolated regression gates (NOT YET EXECUTED)

1. **Positive:** two material categories map to different approved expense accounts; two Departments map to distinct Company centers; requester differs from actual beneficiary; assert real submitted Stock Entry item fields, SLE, posted expense GL account + Cost Center + Department and balance.
2. **Negative B:** generic unapproved Company Stock Adjustment fallback, missing/ambiguous/disabled/group/Balance-Sheet/cross-company/inactive account, stale effective date, unauthorized row-account swap and direct Stock Entry bypass all reject **before stock/GL**.
3. **Negative C:** missing center, multiple candidates without explicit selection, changed/forged selection, wrong Company, disabled/group center and fallback to requester/company defaults all reject **before stock/GL**.
4. **Concurrency/failure:** stale mapping or source change while issue is being created/submitted, double issuance, failed submission rollback, no orphan stock/GL, and retained cancellation behavior.
5. **Return-source design only:** later independent physical return must credit the **actual originally posted** account and Cost Center, original beneficiary Department and original posted cost; never recalculate current Item/Department defaults. Return transactional code is a separate authorization and test gate.
6. **PR #14 + PR #15 reconciliation:** the combined [draft PR #16](https://github.com/ccpcerp/ccpcerp/pull/16) now has joint mocked and genuine ERPNext/GL tests **passed** for Decisions A+D; retain review, recheck its head and retest whenever approved B/C integration is added. These passes **do not** implement B/C, authorize a merge or remove DEVELOPMENT/PRODUCTION safeguards.

## 5. Release decision

**BLOCKED — POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.**

No CCPC-specific Account or Cost Center values have been independently supplied, verified against live ERPNext masters, or authorized in this worksheet. Do not mark the accounting controls implemented from policy approval alone. **Next action:** The owner-approved **controlled/versioned mapping architecture** now governs the approach. Accounting still must supply signed Company/category → Account and Company/beneficiary Department → Cost Center crosswalks, category/Section/selector rules and the detailed controlled mapping schema/permissions/revision workflow. Only after those separately reviewed approvals implement exact fail-closed controls on a GitHub review branch, run disposable Frappe/MariaDB GL tests, and plan DEVELOPMENT validation after target/backup checks. PRODUCTION requires separate explicit authorization.
