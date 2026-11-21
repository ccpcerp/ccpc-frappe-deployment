# CCPC Withdrawal Slip B/C — Owner Approval of G1–G3 Design Principles

**Decision date:** 2026-10-18, Asia/Manila. **Status: G1–G3 DESIGN PRINCIPLES OWNER APPROVED; NO ACCOUNTING USER, MAPPING, ACTIVATION OR DEPLOYMENT APPROVAL.** `POSTING_NO_GO` / `PRODUCTION NO-GO` / `DEV_TARGET_ORIGIN_UNKNOWN_STOP`.

## Approval provenance and exact boundary

In the active CCPC ERPNext conversation, the owner responded **“Approved”** to the explicit question: **“Do you approve G1–G3 as the design principles for the next GitHub-only implementation?”** This approval refers to the immediately preceding [G1–G3 Accounting approval, revision lifecycle and Cost Center selection design proposal](WITHDRAWAL-B-C-ACCOUNTING-APPROVAL-AND-CENTER-SELECTION-DESIGN-2026-10-18.md). It supplements the already approved [versioned mapping architecture](WITHDRAWAL-ISSUE-B-C-VERSIONED-MAPPING-ARCHITECTURE-APPROVED-2026-10-18.md) and [four-DocType inert review design](WITHDRAWAL-ISSUE-B-C-SCHEMA-DESIGN-OWNER-APPROVAL-2026-10-18.md).

**The owner's response is authorization to develop and test the G1–G3 design on a separate unmerged GitHub review branch, using synthetic identities and records, while preserving the existing PR17 activation block.** It is not an Accounting person's sign-off, an authorization to assign actual user permissions, creation of a live workflow, permission to activate an approved revision, or approval to map any CCPC financial account.

## G1 — Independently controlled Accounting maker–checker: APPROVED DESIGN

- Distinguish Mapping Preparer from independent Accounting Mapping Approver. The same authenticated ERPNext User must not approve their own proposed mapping. A role label or UI checkbox alone cannot implement this.
- The eventual approval service must be authenticated, server-owned, scoped to explicitly authorized Company and role/member identities, resistant to forged `approved_by`/`approved_at` and direct API bypass; no silent Stockroom authorization or generic System Manager override.
- An optional read-only auditor can review immutable history without creating, editing or approving revisions.
- **Still pending:** named users, permitted Companies, exact ERPNext Role names and access assignments, approval delegation, one-versus-two Accounting approvers, emergency controls, conflict-of-interest matrix. Do not auto-create or assign roles in setup.

## G2 — Immutable approved mapping revision and auditable lifecycle: APPROVED DESIGN

- Proposed lifecycle for further implementation review: Draft → independently reviewed proposal → approved immutable revision → future supersession/revocation by separately authorized auditable action. No retroactive reassignment of originally posted expense or cost center.
- Preserve approved scope, account/center, effective interval, identity, actor and approval decision as historical evidence. Reject direct edits and unreviewed status flips. Updates create new approved revisions, not overwrites of existing financial decisions.
- Validate Company/master suitability; reject duplicates and ambiguous/overlapping applicable approvals under transaction-safe locks on stable scope rows. Normalized half-open effective intervals `[from, until)` and UTC time handling are proposed technical conventions; the exact ERPNext posting-time/backdate/cutover accounting policy and whether an extra append-only event record is necessary **remain for separate sign-off**.
- **Still pending:** specific approvers, schema migration/index review, exact state transition implementation, approval authority source, effective time/cutoff/retroactivity, immutable event storage/supersession, exception signoff. **No revision may be activated by this decision alone.**

## G3 — Explicit choice of beneficiary Cost Center revision: APPROVED DESIGN

- Base accounting allocation on Company and **actual beneficiary Department**, not requesting Department/Section or default Company center. When only one approved eligible Center applies, validate its authorization; when several apply, require **positive, auditable selection of the exact eligible approved C revision** before issuing stock.
- Approve **Slip-level selection as the review design starting point** because PR16's beneficiary Department and issue intent are header-level; the proposed field `ccpc_selected_center_mapping_revision` is a **candidate fieldname**. Do not represent the field as an activated schema/permission.
- `work_for_section` is **informational unless separately approved** by Accounting as an allocation key; do not infer financial consent from an Equipment-populated Section.
- More than one simultaneously eligible Cost Center for the same Department requires distinguishable **explicit-choice scope keys** (or a separately approved alternative). One Department-only scope with non-overlapping approved revision dates cannot represent several competing choices. A Department-only default and explicit-choice scopes must not silently compete.
- **Still pending:** exact selector field, chooser/reviewer identity and stage, immutable Slip source locking, Section/line-level exceptions, Company/Department eligibility, protection against forged linked Stock Entries. No active multi-center selection in existing PR17.

## GitHub code/test scope and release stops

At decision time the verified application [draft PR #17](https://github.com/ccpcerp/ccpcerp/pull/17) head is `374b7155e570ff618fff482510fe65a52fd148d0` (based on the still-unmerged [A+D PR #16](https://github.com/ccpcerp/ccpcerp/pull/16) head `827993e45ae9321e7a936f48f7fc3b17bf842099`). PR17 has previously verified **3/3 static** and **6/6 disposable real Frappe/ERPNext v16/MariaDB schema** tests, but no G1–G3 activation or GL posting tests.

**Permitted next GitHub review step:** implement and unit-test pure fail-closed G1–G3 policy/eligibility helpers or inert metadata **without wiring them to Stock Entry posting, changing workflow state, granting roles or altering existing production-used DocTypes**. Use a separate review branch/PR so PR17's verified head and passing schema tests remain independently reviewable. Final approver identity, accounting rows, transaction-scope locking and real posting remain separate explicit approvals.

**Still NOT APPROVED:** G4 real Company/leaf Item Group → Expense Account or Company/beneficiary Department → Cost Center crosswalk rows in the [blank Accounting worksheet](WITHDRAWAL-ISSUE-B-C-MAPPING-APPROVAL-WORKSHEET-2026-10-18.md); approving user lists, role grants, activation, migration, financial voucher integration, historical correction, DEVELOPMENT pull/testing, PR merges, and PRODUCTION. Those require independent Accounting, target verification, tests, backups, rollback and owner authorization. No private personal Google Drive notes used.
