# CCPC ERPNext — Departmental expense accounting and reporting architecture

**Design selection:** 2026-11-20, Asia/Manila. **Owner instruction:** "Approved, you can design it yourself" following clarification that management eventually needs **all Department expenses** (materials, payroll, electricity, maintenance services and operating expenses), not only material withdrawals.

**Status: OWNER-AUTHORIZED ARCHITECTURE/DOCUMENTATION DESIGN ONLY.** This document does not constitute approval of individual financial Account or Cost Center crosswalks, appointment of real Accounting signers, actual salary/utility allocation rates, new accounting master rows, expense posting, ERPNext configuration changes, deployment, schema migrations, Git app code implementation, or any PRODUCTION operation. Those require normal Accounting governance and separately authorized actions.

## 1. Management outcome and measures

Offer management a Company-scoped and date-scoped **Department Expense Statement** for Cagayan Corn Products Corporation (CCPC) and Ricor Mills Corporation (RMC), with:
- One Company at a time; fiscal period/month; Department hierarchy/leaf; expense-category/Account; source voucher; cost center; Item/equipment/warehouse drill-through where available; total in that Company's accounting currency.
- Actual **posted GL expense amounts by the authenticated, valid beneficiary Department**, not a sum of unrelated source documents. Net expenses should reflect appropriately posted reversing and correcting entries and period close adjustments.
- A visible **Unassigned/Invalid Department** reconciliation bucket for GL expense entries lacking a valid same-Company Department; no silent allocation or hiding exceptions. Reports label partial coverage and do not falsely certify Department totals if unassigned expenses remain.
- The separate **Material Consumption Register** remains an operational gross original issue report sourced from stock ledger (SLE), with Item/quantity/valuation and exact original Withdrawal Slip/Stock Entry links. It is **not an additional expense** to add to GL expenditure. Returns, cancellations and valuation adjustments require distinct policy and controls, not naïve subtraction from today's SLE.
- Budget-versus-actual and full departmental P&L can be later phases; never classify stock purchases as consumed expense merely because inventory was purchased.

## 2. Dimension policy — selected technical architecture

| Accounting concept | Source of truth | Selected rule |
| --- | --- | --- |
| Company / legal entity | Company on source document and every GL posting | Filter and validate exact Company; no cross-company pooling, no automatic intercompany cost attribution |
| Beneficiary Department | Enabled, leaf Department within Company | **Canonical management dimension for who benefited.** Capture on source row and propagate to GL expense rows. A requester is not necessarily beneficiary |
| Expense Account / nature | Same-Company eligible leaf Expense-root Account | Retain approved Company Chart of Accounts. Do not duplicate salaries, repairs or utility accounts once per Department |
| Cost Center | Same-Company enabled leaf Cost Center | Independent ERPNext financial allocation/budget dimension. Do not infer Department from Cost Center, or vice versa. Initial technical candidates: `Main - CCPC` and `Main - RMC`; only a real signed Company+beneficiary Department → Center mapping can make one usable for actual controlled stock issue |
| Original material attribution | Withdrawal Slip → submitted Material Issue → Stock Ledger + GL | Preserve actual beneficiary at issue and immutable source references; confirm same-Company Expense Account + Cost Center mappings and signed revision before issuing stock |
| Equipment / jobs | Separate operational tags and snapshots | Supplementary reporting; not a mandatory new GL accounting dimension in first release |
| Shared expenses | Approved documented allocation policy | Each portion charged once, with approved basis and audit trail; no automatic proportional distribution, arbitrary defaults, or retroactive reinterpretation |

**Choice for initial limited Phase 1:** Preserve the two currently configured leaf centers (`Main - CCPC`, `Main - RMC`), avoid creating sixteen speculative departmental centers and avoid changing defaults. **Department is the primary reporting dimension for departmental expenses**, and the posting guard must verify Department reaches the actual GL, not just source UI. It is legitimate for more than one Department to share a Cost Center *only where Accounting has explicitly approved each exact Company/Department mapping* and has accepted the aggregated native cost-center reporting. The existing approved Decision C explicitly prohibits blind fallback to `Main`.

**Longer-term option:** If Accounting requires native Cost Center budget-control hierarchy, payroll allocation mechanics, or a dedicated cost-center P&L, design new **Company-specific leaf departmental Cost Centers** under each Company group, with explicit effective dates, current payroll integration tests, and approved individual Department → Cost Center mappings. Do not impose mandatory one-to-one Department–Cost Center identity unless business policy requires it; do not silently rewrite already posted entries. Department accounting dimension remains present even if Cost Centers become granular.

## 3. Posting source requirements and rollout gates

| Posting source | Department source/validation | Rollout |
| --- | --- | --- |
| Approved Withdrawal Slip → independently posted Material Issue | Actual Work-for Department, else valid Equipment Department; block conflict/missing; stamp Stock Entry and each Stock Entry Detail; verify GL Department + eligible Expense Account and Cost Center | **Phase 1 priority**, same legal Company only; user-signed Finance mapping decision required |
| Direct native Stock Entry Material Issue | Require equivalent Company/beneficiary/Account/Center protections or explicit exclusion; do not allow uncontrolled bypass | Verify with integrated tests before release |
| Purchase Invoice for outside services, electricity, utilities | Department on each expense-bearing item/accounting distribution; multi-Department invoices split by approved line allocation, retain supplier invoice and calculation basis | Later, test native GL dimension propagation and cancellation |
| Payroll / Salary Slip / Payroll Entry | Employing Company, employee's beneficiary Department and payroll Cost Center where ERPNext requires it; split shared staff only with approved payroll allocation policy | Later, dedicated payroll posting and GL test |
| Expense Claim / employee reimbursement | Company and beneficiary Department on each expense-bearing row; approval and GL propagation | Later, test and scope permissions |
| Journal Entry / accruals and allocations | Explicit Company/Department per appropriate GL line, approved reversal dates and allocations; no generic Company-level default masked as a Department | Later, controlled maker/checker |
| Depreciation / equipment / shared maintenance | Classify to beneficiary Department or exception bucket; preserve Equipment attribution; verify native depreciation GL behavior | Later; new fields/automation require separately reviewed app changes |
| Intercompany billing and material transfer | Explicit two-Company agreement, separate GL and approvals | **Outside same-Company Phase 1**, no implied authorization |

### Mandatory integrity principles
1. A relevant expense posting without verified Company/Department should fail closed in controlled CCPC routes or be surfaced as **Unassigned/Invalid Department** for native/legacy flows; do not guarantee universal enforcement until each document type is implemented and tested.
2. Company-specific fields, role permissions, and signed mapping identities must be verified server-side; stockroom operators cannot grant financial mapping authority.
3. Stock SLE values and expense GL are related **reconciliation views**, never additive cost sources. Expense GL is primary for full departmental actuals; stock consumption SLE is primary for actual item quantities and gross issue-time valuation.
4. Reverse/return transactions must preserve original Account, Department, Cost Center, valuation basis and Company where required by approved return policy; cancellation and amended postings must be accounted exactly once.
5. Reporting must separate recognized posting date/period, company currency, source quality and canceled documents. Do not sum quantities across different stock UOMs and do not aggregate currencies across Companies.
6. Sensitive payroll/HR detail, personnel data and departmental budget reports require purpose-specific role authorization and Company/Department visibility; System Manager report privilege today must not be broadened by UI-only controls.

## 4. Proposed report suite

**A. Department Material Consumption — Phase 1:** Existing `CCPC Department Material Consumption` is an item-level, company/date/Department-filtered, read-only **gross original outbound SLE value** report. Its verified at-issue Department and quality exceptions are intentional. Add an optional bounded monthly Department summary only after reviewing exact data source, return/net valuation semantics and permissions. Never label this as full GL Department P&L.

**B. Department Expense Statement — future:** Posted, noncanceled GL expense Account rows (with proper signed balances, accounting currency and period dates) grouped by Company, Department and expense Account/category. Each row supports voucher drill-through and approved Cost Center and expense-type breakdown. Show unassigned/invalid Department amounts and data-coverage metrics beside allocated amounts. Design exact debit/credit sign and tax/clearing/capitalization rules against live ERPNext v16 schemas before implementation.

**C. Department-wide management dashboard — future:** Trend by month, Department and expense nature, actual vs approved budget and prior period, with optional shared-cost distribution and explicit exclusions. Reconcile the Department Expense Statement to the *same* set of Company expense GL Accounts in native ERPNext; drill from expense totals to original source and, for materials, to SLE details without double-counting.

## 5. Current verified MAIN DEVELOPMENT evidence (2026-11-20)

- App worktree at clean detached `55eb10b86a57de55a97e293a78228d9dd17b809a`; both `development.localhost` and `ccpc-integration2.localhost` share its bench and code checkout.
- Eligible Finance roles by Company: one named CCPC Mapping Preparer and one named CCPC Accounting Mapping Approver, **zero overlap within each Company**. Role counts alone do not certify business appointments, signed decisions or live API approval.
- **No Expense or Center mapping scopes/revisions exist in MAIN DEV** as of operator SQL. Leaf Cost Centers: `Main - CCPC` and `Main - RMC`, under their respective group roots; ten CCPC and six RMC eligible Departments. Exact mapping choices are **unapproved**.
- Same-Company candidate pilot `ITEM-00004` `Bearing, 6406 Z Ball Dg` in `Warehouse 1 - CCPC`: 8 Nos actual, 0 reserved, Bin valuation rate 12,000 and value 96,000 (currency unverified), Company perpetual inventory enabled. `Bearings` Group contains 19 enabled stock Items; `Consumable` Group contains zero Items. `5140 - Repairs & Maintenance - CCPC` is a keyword-matched **candidate** for Accounting to review across the *entire exact Bearings group*, not an approved value. `Maintenance Department - CCPC`→`Main - CCPC` is an analogous **unapproved candidate**.
- MAIN DEV four-part Nov20 backup generated, format-verified, byte-compared on a separately verified Synology NAS CIFS mount with checksum manifest; separate Nov19 two-site NAS checkpoint exists; **no independent restore rehearsal** performed.
- Code `withdrawal_issue_beneficiary.py` requires registered `department` accounting dimension on Stock Entry, Stock Entry Detail and GL Entry, but actual current MAIN DEV metadata and real GL propagation are **not yet operator verified**. The existing Department report source returns gross SLE and quality flags, **not** Expense GL/net issue costs/all expenses.

## 6. Concrete acceptance and permissions milestones

**Gate 1 — Read-only metadata inspection (next):** On `development.localhost`, verify `department` is among ERPNext Accounting Dimension fieldnames; metadata includes `department` on `Stock Entry`, `Stock Entry Detail`, `GL Entry`. Check indicative native `Purchase Invoice Item`/`Journal Entry Account`/`Expense Claim Detail` fields as *informational only*; a field's existence does not prove posting. Do not issue stock, save masters, or use Finance APIs which lock data just for inspection.

**Gate 2 — Finance source/value decisions:** Named authenticated Accounting maker and independent Checker approve one exact Company+`Bearings` group→eligible Expense Account revision and one exact Company+`Maintenance Department - CCPC`→eligible Cost Center revision, with signed server-controlled version and approved effective date, after reviewing suitability for every Item in group, central-vs-granular Center policy and current user access. Drafts/approvals are data writes requiring separate operator scope.

**Gate 3 — DEV pilot and reconciliation:** In isolated disposable v16+MariaDB integration first where practical and then separately approved persistent MAIN DEV, issue **at most one unit** after stock/period/valuation/permission/current back-up prechecks. Verify one Stock Entry and linked SLE, correct actual expense GL Account/Cost Center/**Department** and stock-credit counterpart, total value/currency and Company, no duplicate/retry, correct material report source, independent Finance signing and negative tests; rollback/cancel and return behavior should be tested separately in controlled environment, not by unreviewed DEV production-like reversals.

**Gate 4 — Expand beyond materials:** For each native source type, add tests for proper Department and allocation, then activate only after Accounting source-policy approval, security testing and balanced GL reconciliation. Record deliberate exceptions and historical missing tags without asserting automatic migration.

**Gate 5 — Production:** Explicit separate approval, tested restoration/recovery, current branch/source/permissions verification and release readiness. **No PRODUCTION actions arise from this design.**

## 7. Controlling project references

- [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md)
- [Owner-approved beneficiary Decision A](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-A-APPROVED-2026-10-18.md)
- [Owner-approved Expense mapping safeguard Decision B](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-B-APPROVED-2026-10-18.md)
- [Owner-approved Cost Center safeguard Decision C](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-C-APPROVED-2026-10-18.md)
- [Finance mapping Accounting authority policy](FINANCE-MAPPING-ACCOUNTING-AUTHORITY-DECISION-2026-10-28.md)
- [First release tracker](FIRST-RELEASE-30-DAY-EXECUTION-TRACKER-2026-11-17.md)
- [Latest operational handoff](CURRENT-HANDOFF-4.md)
- App source `ccpcerp/ccpc_erp/withdrawal_issue_beneficiary.py`, `withdrawal_slip_stock.py`, `bc_mapping_workflow.py`, and `report/ccpc_department_material_consumption/ccpc_department_material_consumption.py` on the Phase 1 release candidate, also exact DEV pin `55eb10b86a57de55a97e293a78228d9dd17b809a`.
