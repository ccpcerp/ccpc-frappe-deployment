# CCPC Withdrawal Slip B/C — Initial Accounting Mapping Master Intake

## Owner-directed CCPC suffix for 5149 — proposed workbook label only

**Owner instruction, 2026-10-18:** “put CCPC on it cause theres four company listed and i think this record was already set up before in the development site including the four company.” In context this refers to the discrepancy between the user-pasted Chart of Accounts entry `5149 - Laboratory Supplies` (no suffix) and the CCPC-specific naming convention. **Changed the PRELIMINARY SHORTLIST label to `5149 - Laboratory Supplies - CCPC`**, as requested, within an updated **conversation-only** Excel review workbook `CCPC_BC_Financial_Mapping_CCPC_Naming_Review_2026-10-18.xlsx`.

**Provenance preserved:** `Chart Snapshot` continues to show original pasted `5149 - Laboratory Supplies`, while `Expense Review Shortlist` separately displays the CCPC proposed label and a dedicated original-source column. The workbook's `START HERE` and Company/intake notes say the owner **reports** that four Companies were already configured in DEVELOPMENT; this is NOT independently verified in any current DEVELOPMENT site. It remains scoped solely to **Cagayan Corn Products Corporation (CCPC)**. Do not treat the name with suffix as the actual ERPNext `Account.name` until an authorized read-only DEV `Account`/Company export or equivalent exact master verification confirms it. Do not infer any other Company or Account name.

**No live change or financial approval:** B/C mapping proposal rows, source master tabs and approval log remain blank; the Account has **not** been renamed on DEVELOPMENT or PRODUCTION; no Stock Entry, DocType, Company or general-ledger change occurred. Excel formula error scan was clear after workbook export. `POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP`.

**Prepared:** 2026-10-18 (Asia/Manila). **Status:** READ-ONLY MASTER COLLECTION / REVIEW WORKBOOK PREPARED. **No real CCPC financial mapping row is populated, approved, or activated.** `POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP`.

## Owner instruction and bounded progress

The owner agreed to proceed with preparing the **initial Company + exact leaf Item Group → Expense Account (B)** and **Company + actual beneficiary Department → Cost Center (C)** mapping table for owner review, with later controlled Accounting revisions. This is **permission to prepare a candidate mapping workbook**, **not approval of any actual financial assignment, production master export, role grant, schema migration, or accounting posting**.

During this active conversation, created the attached chat artifact **`CCPC_BC_Initial_Financial_Mapping_Review_2026-10-18.xlsx`** (not a GitHub file). This is an empty but structured and formula-checked Excel workbook, exported with 9 sheets:

1. `START HERE` — instructions, review/readiness counts and GitHub authority references;
2. `B Expense Mapping` — 50 input slots keyed on **Company + exact leaf Item Group**; candidate expense Account, source and scope checks, proposed effective dates, independent review, no default fallback;
3. `C Cost Center Mapping` — 50 input slots for Company + **actual beneficiary Department**, selector kind/key, proposed Cost Center and Company/leaf checks; formula flags duplicate/mixed Department-only and explicit-choice scopes;
4. `Companies`, `Item Groups`, `Accounts`, `Departments`, `Cost Centers` — blank evidence intake areas for **read-only** exact master exports, no fabricated data;
5. `Signoff Log` — proposed preparer/independent reviewer and decision evidence; flags same-user self-review.

The workbook is a **review aid, NOT an ERPNext import, installed approved version, signed authorization, or proof of Accounting role permission**. All row review states and mapping record values are left blank; calculated `REVIEW READY` only means candidate fields and verification controls are complete, **never** that an approved mapping can be activated. Excel formula error scan found no `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?` or `#N/A` at export. Workbook data rows remain empty by design.

## Required source data — no inferred master values

The authoritative current live master inventory **has not been provided** to this conversation and could not be verified from current GitHub code or project documentation. Prior UI screenshots, synthetic CI fixture names, personal Google Drive notes and standard ERPNext default Account/Center values are **not evidence of approved CCPC masters**.

If the user can access the appropriate ERPNext instance and is authorized to review these masters, obtain **read-only, minimum-field exports** of the following DocTypes and capture the source instance/Company and export date; **do not change any records**:

| Master | Minimum proposed fields | Validation intent |
| --- | --- | --- |
| Company | exact `name`, `abbr` (if available) | Exact Company identity, no assumptions from abbreviations |
| Item Group | exact `name`, `parent_item_group`, `is_group` | Only `is_group=0` leaf groups; exact matching; no parent inheritance or Item override |
| Account | exact `name`, `company`, `root_type`, `account_type`, `is_group`, `disabled` | Exact same Company, Expense root type, enabled non-group account. **Accounting business suitability requires separate signoff** |
| Department | exact `name`, `department_name` (if available), `company`, `parent_department`, `is_group`, `disabled` | Actual beneficiary Department Company/eligibility validation, not requesting Department |
| Cost Center | exact `name`, `company`, `parent_cost_center`, `is_group`, `disabled` | Same Company, enabled leaf; multiple legitimate centers require positively selected signed revision with distinct approved scopes |

**Export and handling restrictions:** Use an authorized read-only data export or safe manually supplied minimal fields, never a database mutation; no new API credentials, raw DB backup, user passwords, patient/personnel/customer information, general ledger dumps or SSH secrets. **Do not upload live business master extracts to public GitHub issues or docs.** Provide only the required fields in the appropriate controlled conversation or access-restricted channel; check which ERPNext environment each extract represents. Do not claim DEVELOPMENT and PRODUCTION master sets are identical without verification.

## Approval workflow after master intake

1. Match every expense mapping proposal to **Company + exact leaf Item Group + verified eligible Expense Account**, backed by a source record and reason. Missing, uncertain and exceptional categories remain unapproved.
2. Match Cost Center proposals to **Company + real beneficiary Department** and exact Cost Center, validating center ownership and leaf/active status. If several centers legitimately apply, request a separate owner/Accounting decision on each explicit choice key, source Slip/line and Section rule; **do not guess or pick first**.
3. Review preparation and approval identities under [owner-approved G1–G3 design boundary](WITHDRAWAL-B-C-G1-G3-DESIGN-OWNER-APPROVAL-2026-10-18.md). The owner has **provisionally expressed a preference to be initial approver**, but actual ERPNext Company-scoped role authorization and maker–checker independence remain open.
4. Get actual scoped signoff, proposed effective date/cutover and exception policy in [Accounting approval Issue #25](https://github.com/ccpcerp/ccpc-frappe-deployment/issues/25) or an appropriately restricted referenced approval record. All G1–G4 and release checkboxes remain incomplete until supported by independent evidence.
5. Only after G1–G4 and implementation/CI are independently authorized, consider a separate controlled mapping activation feature and synthetic genuine ERPNext stock/GL validation. **No site change or PR merge is included here.**

## Verified current review repositories

Application: unmerged [PR #16](https://github.com/ccpcerp/ccpcerp/pull/16) `827993e45ae9321e7a936f48f7fc3b17bf842099`, [PR #17](https://github.com/ccpcerp/ccpcerp/pull/17) `374b7155e570ff618fff482510fe65a52fd148d0`, [PR #18](https://github.com/ccpcerp/ccpcerp/pull/18) `f08765c4d6c81665f216081d2dc16a6796c289fb`; all draft and unmerged when checked. Documentation stays on draft [PR #24](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/24), branch `docs/ccpc-checkpoint-2026-10-10`.

The signed actual crosswalk remains in [B/C Accounting worksheet](WITHDRAWAL-ISSUE-B-C-MAPPING-APPROVAL-WORKSHEET-2026-10-18.md), **blank/unsigned**. No live DEV/PROD actions were performed. No automatic Codex reporter or recurring paid automation resumed.
