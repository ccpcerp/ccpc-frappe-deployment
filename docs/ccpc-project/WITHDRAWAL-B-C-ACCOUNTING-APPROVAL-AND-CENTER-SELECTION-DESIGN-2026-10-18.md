# CCPC Withdrawal Slip Decisions B/C — Accounting approval and Cost Center selection design

**Prepared:** 2026-10-18, Asia/Manila. **Decision status: PROPOSED FOR OWNER AND ACCOUNTING APPROVAL; NOT AN OPERATIVE PERMISSION, WORKFLOW, OR FINANCIAL MAPPING.** The owner previously approved a controlled versioned architecture and an **inert four-DocType review**, not the concrete approval actors, permissions, selector source, effective-date policy, revocation workflow, exception processing, or financial allocation.

**STOP:** `POSTING_NO_GO` / `PRODUCTION NO-GO` / `DEV_TARGET_ORIGIN_UNKNOWN_STOP`. Nothing in this document approves installing a schema or workflow, enabling mapping revisions, or issuing stock against new mappings.

## 1. Verified Github baseline and what already exists

- [Owner-approved architecture](WITHDRAWAL-ISSUE-B-C-VERSIONED-MAPPING-ARCHITECTURE-APPROVED-2026-10-18.md) and [bounded four-DocType review approval](WITHDRAWAL-ISSUE-B-C-SCHEMA-DESIGN-OWNER-APPROVAL-2026-10-18.md) authorize a **draft Github review** with exact leaf Item Group classification/no parent inheritance and positive explicit selection of an approved C revision if multiple Cost Centers are eligible.
- [App draft PR #17](https://github.com/ccpcerp/ccpcerp/pull/17) at independently verified head `374b7155e570ff618fff482510fe65a52fd148d0`, base the unmerged A+D [PR #16](https://github.com/ccpcerp/ccpcerp/pull/16) at `827993e45ae9321e7a936f48f7fc3b17bf842099`. Both open, draft and unmerged at inspection. [Static run 39107359784](https://github.com/ccpcerp/ccpcerp/actions/runs/39107359784) **3/3 passed** and [real disposable ERPNext v16/MariaDB run 39107359756](https://github.com/ccpcerp/ccpcerp/actions/runs/39107359756) **6/6 genuine schema tests passed** on exact PR17 head. Those are **not posting, authorization-lifecycle, or GL tests**.
- PR17 defines: `CCPC Expense Mapping Scope`, `CCPC Expense Mapping Revision`, `CCPC Center Mapping Scope`, `CCPC Center Mapping Revision`. Their JSON currently contains `permissions: []`; revision `validate()` rejects **every state other than Draft**, including for Administrator. No mapping is active. Revision `approved_by`/`approved_at` are currently read-only placeholders, **not a safe authority source** until a server-owned approval action exists. Real draft Account and Cost Center checks enforce Company, active/leaf, and Expense root-type where applicable but **cannot substitute for Finance category-specific approval**.
- On PR17 `Withdrawal Slip`, `department`/`section` mean **requesting** while `work_for_department`/`work_for_section` mean **beneficiary**. `REQUEST_INTENT_HEADER_FIELDS` already includes beneficiary Section; the issue-time row lock and both post-lock comparisons in `withdrawal_slip_stock.py` currently lock `work_for_department` but **not `work_for_section` or any new selector**. The Material Issue builder/validator do **not** resolve approved B/C revisions or snap their identities.
- The [B/C Accounting mapping approval worksheet](WITHDRAWAL-ISSUE-B-C-MAPPING-APPROVAL-WORKSHEET-2026-10-18.md) contains **no approved actual CCPC Company/category Account or Company/beneficiary Department Cost Center rows**. No live master or approval authority has been read/assumed.

## 2. Recommended Accounting authority and segregation — approval requested

**Proposal, not an installed role grant.** Prefer distinct, explicitly authorized *responsibilities* even if Accounting later selects different final ERPNext role names. Proposed illustrative role labels: `CCPC Mapping Preparer`, `CCPC Accounting Mapping Approver`, and optional `CCPC Mapping Auditor`. **Do not automatically create or assign these roles yet.**

| Activity | Proposed actor and authorization | Fail-closed control |
| --- | --- | --- |
| Prepare draft scope and revision | Explicitly authorized Mapping Preparer | Validate linked Company, exact leaf Item Group / beneficiary Department and proposed Account/Cost Center. Cannot set status, approval/revocation audit, or impersonate approver. |
| Independently approve revision | Named Accounting Mapping Approver, distinct *ERPNext User identity* from revision creator and proposer | Explicit authenticated server action; check granted active role/Company scope and user identities; validate entire revision, conflicts and master suitability, never trust client `approved_by` or `approved_at`. |
| Maintain approved revision | No ordinary editor, creator, Stockroom user, or approver direct edit | Approved financial values, scope, effective terms and decision reference become immutable; changes require an independently approved **new revision**. No `db_set` shortcut or `ignore_permissions` approval path. |
| Supersede or revoke | Explicit separately authorized Accounting action; preserve prior approval and full event history | Future allocations blocked at the correct effective boundary; never retroactively change posted Stock Entry or GL, never destroy the old revision. |
| Read mappings for issuance | Restricted server-side resolver only after activation approval; Stockroom receives necessary selection information **not raw edit rights** | Approval check repeats at submit while mapping scopes are locked. Missing or ambiguous mappings block the entire linked Material Issue. |
| Audit | Designated Accounting auditor/read-only reviewer | Read history, user/timestamp/approval reference and posted provenance, with no editing or approval capability. |

**Explicit approval decisions still needed:** actual authorized personnel/users and their permitted Companies; whether one or two independent Accounting approvers are required; whether anyone holding Stockroom or requester roles is *categorically* ineligible to approve; System Manager emergency treatment; approver delegation, absence, revocation authority and least-privilege access. Recommend **two distinct logged-in user identities for prepare vs approve** as a minimum; mere role membership is not maker-checker separation. An Administrator emergency bypass must not silently activate mappings.

## 3. Recommended immutable revision lifecycle — approval requested

**Proposed lifecycle:** `Draft → Submitted for Accounting Review → Approved (future/current effective interval) → Superseded or Revoked`. `Rejected/Returned for Correction` leads to a new or editable draft, never a rewrite of approved source values. PR17 currently only supports inert Draft and **must keep rejecting all other states** until these decisions and automated security tests are approved.

1. **Create or edit draft:** server validates Company and category/Department, exact financial master, and proposed dates. Use current DocType and row permission checks. No trust in UI read-only controls.
2. **Submit for review:** freeze key/value/interval under a new review version; bind authenticated creator identity. Changing a pending proposal invalidates signatures.
3. **Approve:** service checks independent approver, scope+Company authorization, identical frozen proposal fingerprint, genuine non-group active P&L Account or valid Cost Center, verified Accounting crosswalk and interval. Lock stable mapping-scope row with `FOR UPDATE`, reject all overlap with already approved valid intervals (including concurrent revisions), record server-owned approver, timestamp and approval reference atomically. **Database uniqueness on revision key alone does not prevent date overlaps.**
4. **Effective interval:** recommend **UTC-normalized instants** and a half-open interval `[effective_from, effective_until)` (open-ended only if independently authorized); require activation no earlier than server-recorded approval instant to prevent retrospectively authorizing old posting. Separately decide which ERPNext posting effective time is authoritative, including backdated Stock Entries and fiscal cutoffs. No version change may rewrite a historical posting.
5. **Supersede/revoke:** new approved revision or separately authorized revocation action/event creates a permanent audit trail. Do **not** overwrite/delete prior approved account/center values or rely only on mutable status; whether Frappe Version tracking alone is an adequate immutable event store **remains a separate design review**. A fifth event DocType is **NOT** authorized by the approved four-DocType arrangement; seek owner approval if needed.
6. **Concurrency:** approval transactions and issue transactions must lock the same stable scope rows in a documented ordering (Slip → ordered Expense scope keys → ordered Center scopes → revisions); ensure newly created scope keys cannot evade uniqueness/overlap checks. Test concurrent opposite-company scopes, revocation during issue and retry/rollback.

**Important unresolved design choice:** whether `Approved` plus effective timestamp is itself active, or whether a separate `Activated` state and second approval are required. Recommend **Approved + valid effective interval** with no manually editable `Active` flag, **only after** Accounting signs the cutoff/exception rules. No automatic action on current drafts.

## 4. Recommended actual beneficiary Cost Center selection — approval requested

**Confirmed policy, already owner-approved:** one correct Company/actual beneficiary Department allocation; when multiple approved Centers are legitimate, **positive validated selection of the specific approved C revision**. No first-match, requester-Department or Company-default fallback.

**New *proposal* for how to implement it:** add one server-validated `ccpc_selected_center_mapping_revision` Link on the **Withdrawal Slip** as the approval-intent source, because its current actual beneficiary Department is header-level and PR16 applies Department to every issue row. Do not infer the revision from a similarly named Cost Center. This is **not an approved fieldname nor a schema change yet**.

| Case | Proposed selection behavior | Control |
| --- | --- | --- |
| One current signed C revision applies to that Company/beneficiary Department | Resolver can select only that approved eligible revision, with an auditable snapshot | No generic Company/requester fallback; changes/expiry while draft require revalidation |
| Multiple signed C revisions apply | Require explicit revision chosen by an authorized Supervisor/Accounting reviewer **before** Stockroom issuance | UI selection alone is insufficient: validate selected revision, Company, beneficiary, approved scope, effective interval and optional Section rule on server |
| No eligible revision, stale/disabled group Cost Center, mismatched beneficiary or Section | **Block material issue before stock/GL** | Never post with guessed, first, expired or foreign Company center |
| Change to beneficiary Department, Section or selector | Invalidate selection and require fresh validation/approval; linked draft issue may be rejected | Protect selected revision and `work_for_section` in Slip intention-lock rules and in the original issue row snapshot |
| Later mapping edit or physical return | Preserve actual originally **posted** Cost Center, Account, Department and Equipment provenance on the original submitted issue row | Do not resolve a new current mapping to reverse a historical issue |

**Section policy is specifically NOT decided:** `work_for_section` is a validated operational field and may help an Accounting eligibility rule, but **must not automatically become** a mandatory Cost Center key or be copied from Equipment as proof of deliberate financial allocation. Proposed default for review: **Section is informational only; choose a specific approved C revision explicitly when multiple centers exist.** If Accounting later elects Section-scoped financial mappings, extend both SQL Slip lock and post-lock comparisons and validate Company/Department/Section relationships. If different items within one Slip genuinely require different Centers, the single-header selector would be insufficient; approve line-level selections separately.

**Audit and anti-forgery detail for future code:** before original Material Issue `submit`, lock source Slip, selected Center revision and B/C scopes; re-check exact current approved version and immutable source intent; compare every `Stock Entry Detail` approved Account/Center, beneficiary and revision ID; after native ERPNext stock/GL posting compare final persisted voucher and GL attribution in genuine isolated tests. A read-only Link field by itself is **not** evidence of user authorization.

## 5. Dedicated review and test gates (not yet performed)

- **Permissions:** 2 distinct ERPNext test users and Companies; preparer denied approval, stockroom denied mapping edit, approver denied self-approval and out-of-scope Company; optional auditor read-only. Test direct API calls and forging `approved_by`/timestamps/roles and System Manager paths. No `ignore_permissions` activation.
- **Revision lifecycle:** approved value/scope/interval immutable; duplicate number/identity, overlap windows, backdating, revoked/superseded revisions and concurrent approval; real MariaDB row locking with deterministic order; no orphan state after exception. Verify installed schema indexes.
- **Selector:** zero/one/multiple current signed revisions, explicit positive selection, stale beneficiary/source Section, auto-filled Equipment Section not assumed Accounting authorization, invalid requester fallback, forged row Cost Center/revision, Company isolation.
- **Real issue:** future approved B/C builder + `before_submit` tests assert actual original Material Issue, Stock Ledger Entry and posted expense GL Account/Cost Center/Department, on same row with Equipment snapshot; verify no SLE/GL on all rejected cases, fail/retry and duplicate issue controls. These tests are **not** covered by PR17's previously passed 3 static + 6 schema tests.
- **Returns:** physical Option A and original-cost reversal remain separate explicit development/release gates. No retroactive GL backfill.

## 6. Approval checklist and next implementation boundary

Owner and the authorized Accounting lead should explicitly accept or correct each unapproved choice in a versioned GitHub decision record:

- [ ] **G1 — maker/checker roles:** preparer vs independent Accounting approver vs optional auditor; authorized users/Companies, conflicts and System Manager emergency review.
- [ ] **G2 — approval lifecycle:** frozen proposal, approved revision immutability, supersession/revocation audit, effective instants and non-retroactive activation; whether a fifth event ledger is needed.
- [ ] **G3 — cost-center selector:** propose one explicit approved Center Mapping Revision Link on Withdrawal Slip; Department-only default with mandatory positive selection for multiple centers; decide who can choose/confirm, and whether Section is informational or accounting-keyed.
- [ ] **G4 — actual financial mapping values:** separately signed complete Company/exact leaf Item Group→Expense Account and Company/actual beneficiary Department→Cost Center crosswalks, including effective boundaries and exception reviewers; blank [B/C worksheet](WITHDRAWAL-ISSUE-B-C-MAPPING-APPROVAL-WORKSHEET-2026-10-18.md) has no approved rows.
- [ ] **G5 — operations:** reviewed Github implementation and isolated genuine Frappe/ERPNext/MariaDB/SLE/GL tests, independent DEVELOPMENT target/origin/uncommitted work/backups and separately authorized DEV deployment/test; later separate PRODUCTION approval.

**Recommendation for the next owner decision:** Approve **G1–G3 as design principles only** if agreeable, but continue to require actual Accounting signoff on users/Companies, G4 crosswalks and exceptions. Even such design approval must **not** be treated as authority to flip `approval_state` or enable production posting until security implementation and verification are separately authorized.

**Nothing implemented here:** no new app commit, login, role assignment, DocType field, revision activation, mapping record, SQL/site mutation, financial posting, DEVELOPMENT or PRODUCTION operation. No personal connected notes or unapproved live accounting masters consulted.
