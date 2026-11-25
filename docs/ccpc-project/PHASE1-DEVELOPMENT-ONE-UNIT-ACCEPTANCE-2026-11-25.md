# CCPC ERPNext — Phase 1, one-unit DEVELOPMENT acceptance (operator-gated)

**Decision:** Owner approved 2026-11-25 after combined [PR #44 CI run #45539930177](https://github.com/ccpcerp/ccpcerp/actions/runs/45539930177) passed 30 offline + 12 real disposable Frappe/MariaDB tests at source SHA `639fe3974ae1153a765fb071c87037babefba9cc`. **No live DEVELOPMENT transaction has yet been executed or verified.** This is a constrained UAT plan, not a command to automate stock posting.

## Exactly approved scope

- **Environment:** physical DEVELOPMENT server `ccpcerpserver`, site `development.localhost` only; never PRODUCTION.
- **Company (issuer/requesting):** `Cagayan Corn Products Corporation`, same Company only.
- **One item / one issue:** `ITEM-00004`, quantity **1 Nos**, Item Group **Bearings**, source `Warehouse 1 - CCPC`.
- **Actual beneficiary:** `Maintenance Department - CCPC` (Withdrawal Slip `Work For Department`), separate from the requesting Department if different.
- **Structured material use:** `Routine Maintenance` only. Annotate record purpose/location as a DEVELOPMENT UAT example; never represent a real capital job as maintenance.
- **Expected approved finance:** Expense revision `o6pflghd31` (`5140 - Repairs & Maintenance - CCPC`), Center revision `dogpv13jma` (`Main - CCPC`). These names were *previously operator-reported* approved, **not independently rechecked for current eligibility**. Account and Cost Center must be active, Company-owned, non-group, and appropriate for GL posting.
- **One distinct requestor/preparer and one authorized Stockroom issuer.** Ordinary signed-in named users, not `Administrator`; no adding roles/permissions as part of this test.
- **Excluded:** second issue, replay, cancellation/reissue, bulk changes, source pull, migration, restart, backup restore, unreviewed permissions/master changes, and all PRODUCTION work. Any unexpected blocked step is a STOP, not permission to bypass a check.

## Readiness gates — verify before pressing Issue Materials

1. From the human/operator's trusted DEVELOPMENT console or approved UI, independently confirm **server/site identity**, installed custom-app Git commit and clean tracked checkout; expected DEV code at `b599395f9c65cc6c6b8cc1b2750bc4559547161a`. Review any drift; do not pull/switch/migrate as part of this UAT. The later `639fe397` adds only tests and CI files and need not be installed to test runtime.
2. Confirm the 2026-11-25 09:10 DEV `--with-files` backup is still accessible and healthy; it was archive-checked, **not restore-tested**, and remained on the same host. If recovery assurance is insufficient for this site, stop for a separately agreed recovery measure.
3. Confirm **one unreserved, currently available `ITEM-00004`** in the designated warehouse, correct Item Group, no serial/batch requirement that invalidates the intended UI flow, and capture quantity + inventory valuation and existing SLE/GL totals for comparison. Prior Bin evidence was 8 Nos @ nominal 12,000 per Nos, not a posting-value guarantee.
4. Confirm signed Finance revision provenance, unique scope, correct active Company Account/Cost Center, effectivity at current real posting time and `Department` accounting dimension, perpetual inventory, required `Stock Entry`/`Stock Entry Detail`/`GL Entry` metadata. Do not hand Codex DB credentials or its accessible Docker socket to run these checks. The prior role listing is **not** a Frappe effective-permission proof.
5. Confirm named requester/supervisor can initiate and approve the relevant Withdrawal Slip workflow, and **different** named Stockroom user has effective Withdrawal Slip write/issuer authorization. Validate no existing draft/submitted Stock Entry for the new Slip before issuance. If any gate fails, **do not post** or silently change roles, accounting masters or policy.

## Controlled UI sequence (after gates pass)

1. Named requesting supervisor logs into **DEVELOPMENT** and creates **one** new `Withdrawal Slip`. Populate actual Requestor, Required By, *Issuing Company* and *Requesting Company* both CCPC, requesting Department appropriate to the user's identity, *Work For Department* `Maintenance Department - CCPC`, warehouse `Warehouse 1 - CCPC`, physical location, explicit UAT purpose/reason, and the structured **Material Use = Routine Maintenance**. Add **only `ITEM-00004` / Requested Qty = 1**. Save the Draft. Note new Slip ID. If a selected Equipment conflicts with beneficiary Company/Department, stop rather than masking it.
2. Authorized preparer uses the normal **Approve & Send to Stockroom** transition; separately signed-in Stockroom user uses **Start Review**, enters *Received By* and **Issue Qty = 1**, and saves. Verify state **Stockroom Review**, Warehouse, beneficiary, Company, classification, quantity, approved revisions and no prior voucher.
3. **One human operator approval gate for the irreversible step:** after reviewing readiness, authorized named Stockroom user presses **Stockroom → Issue Materials** once and confirms. This creates/submits a real DEVELOPMENT `Material Issue` and corresponding Stock Ledger/GL changes. Do not independently create a `Stock Entry`, do not retry a timeout or ambiguous response before checking whether a voucher posted, and do not use Administrator/impersonation to bypass denial.
4. Reconcile generated submitted Stock Entry ID with Slip reference; SLE quantity **-1** for the correct warehouse/item; Bin quantity decrease by 1; GL debits/credits balance and expense/warehouse accounts and cost center/Department match reviewed finance master; material-use classification and approved revision provenance intact. Verify `CCPC Department Material Consumption` shows **exactly one** eligible live issue row, with correct beneficiary/amount. Review remaining day-one reports as relevant, but do not infer untested report coverage from this one transaction.
5. Preserve a **sanitized UAT result**: timestamp and site/commit, Slip and Stock Entry identifiers, state, mapping revision references, SLE/GL quantity/value deltas and report outcome, exceptions and whether any duplicate attempt was made. Do not commit credentials, patient/customer data, full business-ledger extracts or raw secrets to public GitHub. If validation fails, leave records intact for controlled root-cause analysis; cancellation/reversal is a separate authorization.

## Status

- GitHub disposable CI: **GREEN 42/42** tests at `639fe397` (30 offline + 12 real DB).
- MAIN DEVELOPMENT preflight, named-user UI flow and one-unit persistent posting: **NOT YET VERIFIED / NOT EXECUTED**.
- PRODUCTION: **OUT OF SCOPE / UNTOUCHED**.

References: [CURRENT-HANDOFF-5.md](CURRENT-HANDOFF-5.md), [GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md), `ccpcerp/ccpc_erp/withdrawal_slip_stock.py`, `ccpcerp/ccpc_erp/doctype/withdrawal_slip/withdrawal_slip.js`, `ccpcerp/ccpc_erp/phase1_maintenance_use.py` at GitHub review candidate.
