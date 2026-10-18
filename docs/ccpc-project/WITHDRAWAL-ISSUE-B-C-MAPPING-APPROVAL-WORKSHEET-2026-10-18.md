# CCPC Withdrawal Slip Material Issue — Decisions B/C Accounting mapping approval worksheet

**Prepared:** 2026-10-18. **Status: DRAFT FOR ACCOUNTING SIGN-OFF; NO MASTER MAPPINGS APPROVED HERE.**  
**Scope:** Original controlled Withdrawal Slip → submitted Stock Entry `Material Issue`, downstream source-linked physical return design. **Not** an instruction to edit Company, Item, Item Group, Department, Cost Center, stock, GL, DEVELOPMENT or PRODUCTION.

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

## 3. Read-only documentary evidence — candidate masters, **not approvals** (2026-10-18)

The [existing shared **ERP Implementation** Google Sheet](https://docs.google.com/spreadsheets/d/1LFkBX1VzMGXHd9GVEF2lbGENAf1qa0ekBQSJTfsBock/edit) was discovered through the connected read-only Google Drive source. Google Drive metadata reported modified `2026-09-18T09:01:05Z`; this is an earlier **planning workbook**, **not** an exported verified current Account/Cost Center/Item Group master from CCPC's active ERPNext database. Do not automatically propagate any of its values into production, application code, fixtures for business acceptance, or signed mapping tables. No spreadsheet cells were changed.

| Source / exact tab + cells | Observed documentary values | Why this is **not** an allocation approval |
| --- | --- | --- |
| `3.1 Chart of Accounts`, row 161 | `5140 - Repairs & Maintenance - CCPC` | Plausible repair expense candidate; not specifically mapped to Bearings, spare parts, categories or any Company/beneficiary |
| Same tab, row 170 | `5149 - Laboratory Supplies` (no ` - CCPC` in the spreadsheet cell) | Potential naming inconsistency; requires exact current ERPNext Account name, company, type and approval |
| Same tab, row 178 | `5400 - Stock Adjustment - CCPC` | Its presence as an account does **not** authorize use as a generic Material Issue expense fallback |
| Same tab, row 19 | `1501 - Parts, Materials and Supplies - CCPC` | Inventory asset candidate, **not** automatically a row consumption expense account |
| `3.2 Default Chart of Accounts`, row 13 | `Default Cost Center = Main - CCPC` | A default is **not** a beneficiary Department→Cost Center crosswalk; do not substitute it without explicit mapped approval |
| `1.2 Item Groups`, rows 13–23, 36–54 | Includes `Bearings`, `Lubricants`, `Bearings & Bearing Accessories`, `Lubricants & Oil`, etc. | Overlapping names and differently structured numbered/unnumbered entries; Accounting must approve the **canonical category identifiers, hierarchical/inheritance policy and exact live Item Group names** before mapping |
| `1.1 Company`, rows 16 and 20 | `Cagayan Corn Products Corporation (CCPC)`; `Ricor Mills Corporation (RMC)` | The inspected `3.1` table is explicitly CCPC-headed. A full RMC original issue accounting chart/crosswalk was **not evidenced** in this workbook search |

**GitHub source comparison:** `ccpcerp/setup.py` on [app PR #14](https://github.com/ccpcerp/ccpcerp/pull/14) defines a `WITHDRAWAL_SECTION_STRUCTURE` for CCPC and RMC Departments/Sections; **Section and Department do not provide an approved Cost Center link**. The existing `ccpcerp/patches/v1_0/create_intercompany_material_accounts.py` defines `5150 - Intercompany Materials Expense - <company abbreviation>` for an **intercompany billing purpose**, and includes four Company names (CCPC, RMC, GSL and WFC) as patch expectations, not verified live installed masters. **Do not treat account 5150 or this patch as a Decision B mapping for consumed original Withdrawal Slip materials**, or assume these four Companies are present in every target environment.

**Recommended evidence-gathering order (no database/site actions approved here):** Accounting identifies which issue Companies are in scope and provides the latest authoritative, *sanitized* Account, Cost Center, Item Group and Department master extracts from the intended environment, with exact ERPNext identifiers, company, disabled/group flags, root type and effective dates. Confirm the existing workbook against those extracts, then sign B/C allocations separately. Item Group overlap and multi-center Department allocation must be resolved explicitly. A read-only site inspection requires verifying DEVELOPMENT target identity and authorizing a non-sensitive output procedure first; do not print site config, credentials, private business records or full database dumps.

## 4. Implementation choices requiring separate owner/Accounting sign-off

- **Mapping authority/storage:** existing master defaults versus a dedicated CCPC controlled mapping DocType/record; ownership, permission model, effective-dating and change audit; whether any migration is needed. **No choice made.**
- **Snapshot and enforcement:** for each line resolve approved account and Cost Center before issue insert; store on Stock Entry Detail; at `before_submit` resolve/revalidate against the locked source and approved effective mapping; reject user-forged or cleared rows and mismatched source. Require actual GL debit to carry approved expense Account, Cost Center and Decision A Department. Avoid permission escalation to edit financial selections.
- **Locking and change safety:** detect mapping changes between issue construction and submission; define whether approval records are immutable once referenced or versioned; preserve original actually **posted** account/center for later physical-return expense credit even if current mapping changes.
- **Exceptions:** Accounting-approved review/override trail, scope and authorized users; no arbitrary correction account, custom duplicate GL posting, or historical backfill without separately approved design.

## 5. Required isolated regression gates (NOT YET EXECUTED)

1. **Positive:** two material categories map to different approved expense accounts; two Departments map to distinct Company centers; requester differs from actual beneficiary; assert real submitted Stock Entry item fields, SLE, posted expense GL account + Cost Center + Department and balance.
2. **Negative B:** generic unapproved Company Stock Adjustment fallback, missing/ambiguous/disabled/group/Balance-Sheet/cross-company/inactive account, stale effective date, unauthorized row-account swap and direct Stock Entry bypass all reject **before stock/GL**.
3. **Negative C:** missing center, multiple candidates without explicit selection, changed/forged selection, wrong Company, disabled/group center and fallback to requester/company defaults all reject **before stock/GL**.
4. **Concurrency/failure:** stale mapping or source change while issue is being created/submitted, double issuance, failed submission rollback, no orphan stock/GL, and retained cancellation behavior.
5. **Return-source design only:** later independent physical return must credit the **actual originally posted** account and Cost Center, original beneficiary Department and original posted cost; never recalculate current Item/Department defaults. Return transactional code is a separate authorization and test gate.
6. **PR #14 + PR #15 reconciliation:** review overlapping `withdrawal_slip_stock.py` logic and retest both Department and immutable Equipment issue-time snapshots together before any merge.

## 6. Release decision

**BLOCKED — POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.**

No CCPC-specific Account or Cost Center values have been independently supplied, verified against live ERPNext masters, or authorized in this worksheet. Do not mark the accounting controls implemented from policy approval alone. **Next action:** Accounting supplies signed Company/category → Account and Company/beneficiary Department → Cost Center crosswalks plus the authoritative selector/storage choice; then implement exact fail-closed controls on a separate reviewed GitHub branch, run disposable Frappe/MariaDB GL tests, and plan DEVELOPMENT validation after target/backup checks. PRODUCTION requires separate explicit authorization.
