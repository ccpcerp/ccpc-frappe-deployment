# CCPC Withdrawal Slip B/C — Initial Accounting Mapping Master Intake

## Owner confirmation: Account 5149 enabled, non-group; same COA structure across four business companies — 2026-10-18

**Owner clarification:** Following the previously reported **enabled** status for CCPC Account number **5149 — Laboratory Supplies**, the owner confirms that **`Is Group` is UNCHECKED** on that Account record and that **CCPC, RMC, GSL and WFC use the same Chart of Accounts structure**. These are **owner-reported configuration details**, not a direct Account DocType export or independently observed DEVELOPMENT database verification. Record the 5149 eligibility evidence as **preliminary ENABLED / NON-GROUP** only; do not mark the exact ERPNext `Account.name`, `company`, `root_type`, `disabled` field, parent, effective mapping, or GL postings as verified. In particular, source chart text **`5149 - Laboratory Supplies`** and preliminary target label **`5149 - Laboratory Supplies - CCPC`** must not be treated as identical document IDs without verification.

**Scope policy:** A **reusable mapping-review template** may be shared among the four business companies because the owner reports the same account structure. However, ERPNext financial **Account records, Cost Centers, Item Group mapping revisions and approvals remain Company-scoped**. Do not assume Company-independent Account link keys, auto-fill a CCPC expense account into RMC/GSL/WFC, or include extra DEVELOPMENT test companies in live mapping scope. A same-looking Account numbering scheme does **not** approve the same financial usage/Cost Center for all companies.

**Next missing evidence and decision:** Obtain the **exact leaf Item Group master** and Company-specific Account master field names/eligibility from verified DEVELOPMENT (authorized read-only only), then draft **Company + exact leaf Item Group → Account** candidates for owner/Accounting approval. For C mappings also need **beneficiary Department and Cost Center** records and explicit selector-policy signoff. `POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP`. No code, Account rename, Company master, financial mapping, or DEV/PROD modification is authorized here.

## Owner-confirmed four business companies and DEVELOPMENT test defaults — 2026-10-18

The owner clarified the **four business-company codes** as **CCPC, RMC, GSL and WFC**, stated that **other Company records present in DEVELOPMENT are default test companies**, and reported that **all four business companies already exist in PRODUCTION**. This replaces the earlier ambiguous statement that DEVELOPMENT contains *only four* Companies: the total number of DEVELOPMENT Company records may be greater than four because default test Company records may coexist. **This is a direct owner confirmation of operating scope, not an independently observed live DEV or PROD `Company` database export; exact `Company.name` document identifiers remain unverified.** Never infer or invent the full names of RMC, GSL or WFC.

An updated **chat-only** Excel artifact `CCPC_BC_Mapping_Four_Business_Companies_Owner_Confirmed_2026-10-18.xlsx` retains the existing 12-sheet review workbook and fills only the owner-reported Company codes on the `Companies` evidence tab; exact Company-name and master-export cells remain **blank**. It adds separate DEV-business and owner-reported PRODUCTION-presence fields and an explicit **`NO — export pending`** exact-name verification field. The `DEV 5149 Check` sheet now distinguishes **four business companies versus possibly additional default DEV tests**; its observed names and Account 5149 fields remain blank, with comparison flags `PENDING COMPANY LIST` and `PENDING ACCOUNT EXPORT`. B and C actual mapping assignments, Cost Centers, Account validity and Accounting approvals remain unfilled. Spreadsheet formula error scan returned **zero matches**.

**Boundary:** Only CCPC is presently in scope for the candidate Financial Mapping workbook. RMC, GSL and WFC are distinct Companies requiring their own separately verified account/cost-center master and mapping review when authorized; never copy CCPC mappings to them by default. No PRODUCTION connection, verification, edit, account rename, ERPNext import, Company creation, stock/GL posting, role permission or database write was performed.

**Next safe read-only check:** on a verified **DEVELOPMENT** site, inspect the Company List with an exact-name/abbr filter for CCPC, RMC, GSL, WFC and distinguish any additional default test companies; then inspect Account number `5149` filtered to the exact CCPC Company and record `Account.name`, `account_name`, `company`, `root_type`, `is_group`, `disabled` before any B mapping signoff. There is **no need to connect to or modify PRODUCTION** to complete this step. `POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP`.

## DEVELOPMENT verification of Account 5149 and reported four Companies — read-only UI procedure

**2026-10-18 continuation:** User asked to continue after requesting `5149 - Laboratory Supplies - CCPC` as a candidate label and recalling four Companies configured in DEVELOPMENT. No connected ERPNext DEVELOPMENT session, independently verified target URL, Company master export, or Account master export is available to this conversation; GitHub source is authoritative for code/checkpoints **but not proof of current database rows**.

A new **conversation-only** workbook `CCPC_BC_Financial_Mapping_DEV_5149_Verification_2026-10-18.xlsx` preserves the earlier CCPC-name shortlist and 11 existing review sheets and adds **`DEV 5149 Check`** as sheet 12. Its Company 1–4 exact-name fields, Account number/ID/name/Company/root_type/account_type/is_group/disabled fields, evidence source and reviewed-at fields are **all blank**, status **NOT VERIFIED**. The formula compares the eventual exact `Account.name` to proposed `5149 - Laboratory Supplies - CCPC` but is only an evidence cue, never mapping approval. Workbook checking shows `PENDING ACCOUNT EXPORT` and `PENDING COMPANY LIST` with blank source cells; no workbook formula errors. No live database action.

**User can collect evidence via ERPNext Desk, read-only, in this precise order:**

1. **Confirm the current browser session is DEVELOPMENT** using a known verified DEV environment address/identity before opening records. If environment identity is uncertain, **STOP**; do not use the shared PRODUCTION site merely because the login or company names look similar.
2. In DEVELOPMENT **Company List**, record the count and **exact `Company.name`** of the observed Companies (owner recalls four; do not invent names or require it to be four).
3. In DEVELOPMENT **Account List** (or Chart of Accounts with Company scoped), search/filter by **Account Number `5149`**; Company scope must be explicit if the number is reused in other Companies. Open the actual Account record without editing it. Copy only `name` (exact document identifier), `account_number`, `account_name`, `company`, `root_type`, `account_type`, `is_group`, `disabled` and source evidence date. UI labels may vary; use Data Export read-only if necessary.
4. Upload a screenshot or minimal read-only export to the **controlled conversation**, rather than a public GitHub issue. No credentials, tax IDs, payroll, accounting ledger balances or business transaction records are requested. Do not click **Save, Rename, Import or Delete**.
5. If the actual Account title differs from the proposed suffix, **record the difference**; do not immediately rename or auto-merge/activate financial mappings. Check transaction dependencies and separate explicit authorization before any master data change.

**Existing authorization boundary:** owner has approved G1–G3 architecture/design principles only and provisionally offered to act as initial approver, with maker-checker independent review still required. **No verified exact Account master, approved Item Group→Account financial assignment, role grant, DEVELOPMENT pull, or PRODUCTION operation.** `POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP`.

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
