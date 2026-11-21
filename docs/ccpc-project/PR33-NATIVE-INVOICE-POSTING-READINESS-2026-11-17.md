# CCPC ERPNext — PR #33 native Draft invoice submission and accounting reconciliation readiness

**Prepared:** 2026-11-17 Asia/Manila. **Approval scope:** Owner answered **"Approved, continue"** after first permanent Draft CCPC SI / Ricor PI pair plus distinct read-only persistence audit both PASSED. Interpret as authorization to **review and prepare** the next DEVELOPMENT accounting-posting milestone. **No native invoice `submit()`, journal/GL/stock posting, cancel, payment, privilege grant, migration, restart, PR merge or PRODUCTION operation is authorized/executed by this preparation.** Any subsequent financial posting requires the exact documents, expected financial effects and separate explicit approval.

## November 17, 2026 — owner selects direct consumption; corrected billing-item design in GitHub (NO DEV DATA WRITE)

Business owner confirmed Ricor departments/equipment **directly consume the CCPC-issued material without Ricor warehouse receipt**. This changes the prior two-option accounting exploration into a selected **direct-expense design**; a Ricor warehouse Purchase Receipt / `2301` clearing approach is no longer the authorized planning path for these withdrawals. It does not authorize any financial record/account/Item master mutation.

**Detailed GitHub-first design:** `docs/ccpc-project/PR33-RICOR-DIRECT-CONSUMPTION-ACCOUNTING-CORRECTION-DESIGN-2026-11-17.md`. Preserve immutable original stock Item/source and CCPC Material Issue. Map the *Ricor PI billing representation* to a distinct Accounting-approved non-stock intercompany-consumption Item with compatible original UOM/quantity/frozen rate, so ordinary native PI validation can retain signed Ricor expense mapping to `5150 - Intercompany Materials Expense - RMC`; preserve PI credit `2121 - Intercompany Payable - RMC` and unchanged CCPC SI item/accounts. A new **one-shot, audited Approved-batch + two-existing-Draft-invoice** correction workflow (different from current fully-cancelled pair workflow) must preserve both current invoice IDs and avoid reapproval/source release. Use real named maker/checker, effective Ricor expense/beneficiary Cost Center mappings, Version audit/unique decision-use, row locks, replay protection and rollback. No bypass of native ERPNext validation or SQL financial edits.

**History and master-data warning:** Original billing child does not freeze original source Item Group; snapshot Department/Section values may be captured at billing preview rather than issue time. Do not convert current Item master or cross-Company Department name into false original historical evidence; require validated source history and signed Accounting attestation before correction. Do not assume a suitable nonstock billing Item or Ricor signed Item Group/Department mapping exists. Dedicated owner-unexecuted **read-only** dependency inventory staged: `scripts/development/operator/ccpc_pr33_direct_consumption_readonly_dependencies_20261117.sh`, immutable Git blob `2c47c7f5b965f0c27f2f65cbc04186ce4c1edf00`. This inventories current Item/UOM candidate counts, Ricor mapping presence, beneficiary Company and current Draft/GL/SLE state, not effective-rule approval.

**Status:** No app code modifications, no new Item, no invoice correction, no GL/SLE, no database schema migrations, no new backups or PROD. The prior local/NAS recovery sets **predate the saved Drafts**, so a fresh post-Draft protected local+offsite backup is required before any separately approved DEV data write. App PR33 remains review/draft; future native submit/GL accounting acceptance is still HOLD.

## November 17, 2026 — MAIN installed native Ricor SRBNB override ROOT CAUSE CONFIRMED (read-only, no posting)

The owner ran the exact GitHub-pinned `scripts/development/operator/ccpc_pr33_ricor_native_srb_rule_readonly_20261117.sh` diagnostic in a fresh MAIN `development.localhost` read-only transaction; actual returned output:

```text
PINNED_MAIN_DEV_SOURCE=PASS
EXACT_DRAFT_PAIR_UNPOSTED=PASS
INSTALLED_NATIVE_PI_STOCK_CLEARING_RULE=FOUND
RICOR_PERPETUAL_INVENTORY=YES
ITEM_IS_STOCK_ITEM=YES
PI_IS_OPENING_NO=YES
ITEM_IS_FIXED_ASSET=NO
PI_ITEM_HAS_PURCHASE_RECEIPT=NO
PI_ITEM_HAS_PO_DETAIL=NO
PI_ITEM_DROPSHIP=NO
PI_UPDATE_STOCK=NO
RICOR_COMPANY_STOCK_RECEIVED_NOT_BILLED=2301 - Stock Received But Not Billed - RMC
SAVED_PI_LINE_ACCOUNT=2301 - Stock Received But Not Billed - RMC
INTENDED_RICOR_EXPENSE_ACCOUNT=5150 - Intercompany Materials Expense - RMC
NATIVE_NO_RECEIPT_CLEARING_RULE_APPLIES=YES
SAVED_PI_MATCHES_NATIVE_CLEARING=YES
NO_PI_REVALIDATION_OR_POSTING_PERFORMED=PASS
READ_ONLY_SRB_DIAGNOSTIC=PASS
```

**Validated cause:** Installed `PurchaseInvoice.set_expense_account` contains the stock item + perpetual inventory + unreceived Purchase Invoice clearing rule; every relevant actual site and Draft PI flag meets its predicate. The CCPC app initially specifies `5150 - Intercompany Materials Expense - RMC`, but native Purchase Invoice `validate()` overrides that line's `expense_account` to the valid **liability** `2301 - Stock Received But Not Billed - RMC`. The fact that `update_stock=0` does not bypass the rule. Source account mismatch is **not a configuration typo or nonexistent ledger**; it is standard native logic for the supplied stock-item/receipt state. Therefore simply changing line `expense_account` to 5150, editing Account master, toggling perpetual inventory, or invoking invoice submit would not be a verified safe correction.

**Accounting significance / decision:** The validated site facts establish Ricor has *no linked Purchase Receipt* for the stock item; they do **not**, by themselves, establish whether Ricor's legitimate business intention is **receiving stock into Ricor inventory** or **immediately consuming/expensing material**. CCPC's source Stock Entry is a submitted **Material Issue** associated with an intercompany Withdrawal Slip, and the existing batch retains exact stock-item evidence. It is a separate CCPC-side stock movement; do not conflate with Ricor's receipt. Choose/account-approve intended flow before implementing.

**Preferred design if department consumption is confirmed:** Keep immutable material stock source trace, original quantity/frozen rate/department/equipment and CCPC side unaffected; use an appropriately governed **non-stock intercompany billing/charge item** in Ricor invoice line, deliberately mapped to the Ricor `5150` expense account and Ricor cost center/dimensions, with explicit source-to-billing-item audit relationship, unique one-time source claim, both invoice totals and cross-links reconciled. Never globally convert the original inventory Item to non-stock or relax source validation. The existing `Approved` batch and its already committed linked **Draft** SI/PI need a carefully authorized **draft correction** lifecycle; the current controller's canned cancelled-invoice correction is for **fully cancelled invoices** and does not automatically solve existing Drafts. Do not delete/reset drafts, manufacture a Purchase Receipt, change frozen source facts, run ad hoc SQL, override GL entries, or regenerate invoices outside a reviewed, concurrency-safe, auditable workflow.

**Alternative if Ricor genuinely receives stock:** Design Ricor's real Purchase Receipt / inventory valuation, intercompany sale-to-purchase reconciliation, explicit posting to and clearing of `2301`, subsequent internal Material Issue/consumption on Ricor as appropriate; require physical warehouse evidence and prevent duplicate cost recognition across CCPC/Ricor. Do not fake receipts to manipulate the account.

**State:** MAIN Draft pair `ACC-SINV-2026-00001` + `ACC-PINV-2026-00005` remains unsubmitted and linked to one Approved batch; zero related GL/SLE confirmed in latest read-only diagnostic. No account changes, no user grants, no app branch change, no migration, no restarts, no PRODUCTION. The local and NAS backup remain **pre-Draft**; a fresh post-Draft backup is mandatory before any prospective record mutation. Next action is explicit business accounting treatment decision (consume/expense vs receive/warehouse) and source-reviewed implementation plan, not another invoice submission attempt. PR33 remains draft.

## November 17, 2026 — EXACT READ-ONLY ACCOUNT DIAGNOSIS 3/4: RICOR expense overwritten by native perpetual stock-clearing rule (site confirmation pending)

Owner executed `ccpc_pr33_main_readonly_invoice_account_diagnostic_20261117.sh` under MAIN `development.localhost` `START TRANSACTION READ ONLY`, with no invoice submit or commit. Returned `PINNED_MAIN_DEV_SOURCE=PASS`, `DRAFT_PAIR_NO_POSTING=PASS`, `DIAGNOSTIC_ONLY_NO_ACCOUNT_CHANGES=PASS`, `READ_ONLY_NO_COMMIT_OR_SUBMIT=PASS`; **`EXACT_ACCOUNT_NAMES_MATCHED=3/4`**.

**Exact stored account results:**

| Saved invoice field | Intended controller account | Actually persisted | Account company / root / type | Diagnostic |
|---|---|---|---|---|
| CCPC SI `debit_to` | `1312 - Intercompany Receivable - CCPC` | same | CCPC / Asset / Receivable | MATCH, valid |
| CCPC SI item `income_account` | `6050 - Intercompany Material Charges - CCPC` | same | CCPC / Income / [no account_type] | MATCH, valid |
| Ricor PI item `expense_account` | **`5150 - Intercompany Materials Expense - RMC`** | **`2301 - Stock Received But Not Billed - RMC`** | Ricor / **Liability** / Stock Received But Not Billed | **MISMATCH, invalid for intended expense role** |
| Ricor PI `credit_to` | `2121 - Intercompany Payable - RMC` | same | Ricor / Liability / Payable | MATCH, valid |

Both the actual `2301` and intended `5150` ledger accounts exist in Ricor and are valid in their *respective* roles. They are **not interchangeable**: posted PI debit to stock-received-not-billed liability may clear a Purchase Receipt obligation or represent timing of physical receipt, whereas the business-intended cost recognition is debit `5150` expense. Without prior matching Ricor Purchase Receipt/stock valuation, the company could fail to recognize materials expense and misstate the stock-clearing liability. The current source Stock Entry is a CCPC Material Issue, not evidence of a Ricor Purchase Receipt. This is a material accounting gate, not an innocuous naming difference.

**Source-based cause, strongly supported but actual installed-rule flags NOT YET READ:** Frappe ERPNext public `version-16` `erpnext/accounts/doctype/purchase_invoice/purchase_invoice.py`, Git blob `6df4481aef271fbae0187de71de78ca9f7ae83e2`, `PurchaseInvoice.validate()` invokes `set_expense_account(for_validate=True)`. That method explicitly assigns `item.expense_account = stock_not_billed_account` when the item is a stock item under **perpetual inventory**, PI `is_opening="No"`, not fixed asset or delivered-by-supplier drop-ship, and there is no Purchase Receipt (or relevant PR posts stock not billed). This applies even with `update_stock=0`. The CCPC custom controller (blob `a9a6e609759e77948d40d31bdbd342f727b208a9`) built its Ricor PI item with `expense_account=5150...`, but native validation can overwrite it to `2301...`. The saved mismatch is consistent with this built-in rule. **Do not claim site execution of the native branch until actual item flags / perpetual setting and installed method are independently verified**; do not simply change the field back and assume it survives `validate`.

**Next minimal read-only evidence:** New GitHub docs review script `scripts/development/operator/ccpc_pr33_ricor_native_srb_rule_readonly_20261117.sh` (pinned blob before host execution). It checks exact pinned MAIN app/site/batch and Draft no-posting state, reads Ricor perpetual inventory setting, source Item stock/fixed asset flags, PI Purchase Receipt and Purchase Order details, opening/drop-ship/update_stock flags, actual Company SRBNB default, and checks that the **installed** `PurchaseInvoice.set_expense_account` source contains matching stock-clearing rule. Outputs `NATIVE_NO_RECEIPT_CLEARING_RULE_APPLIES=YES/NO` and `SAVED_PI_MATCHES_NATIVE_CLEARING=YES/NO` without invoking `set_expense_account` or touching data. Operator must pin exact docs Git commit + file Git blob, run Bash syntax and Python AST checks before invoking. **No financial write until site rule and Accounting policy are decided.**

**Policy options (not selected or implemented):** (a) if Ricor should receive the physical stock, design an explicit Ricor Purchase Receipt/inventory and subsequent consumption sequence with correct Stock Received But Not Billed clearing, business source links and no double-recognition; or (b) if Ricor directly consumes material and should record a direct departmental expense without inventory receipt, design an appropriate non-stock intercompany charge item/controlled accounting adjustment mapped to `5150` while retaining exact original material stock Item evidence in immutable CCPC source record, with no duplicate stock or cost posting. Do not reclassify a master Item globally, force `update_stock`, bypass validation, create a fake PR, or use `is_opening`/manual SQL override merely to coerce the target expense. Either path needs approved business accounting policy, code changes in app PR33 as appropriate, reconciliation, fresh post-Draft recovery and separate authorization for any financial posting/record mutation.

## November 17, 2026 — first MAIN read-only posting preflight STOPPED at account-name mismatch; no posting

The owner executed the exact-GitHub pinned read-only posting preflight `scripts/development/operator/ccpc_pr33_main_draft_pair_readonly_posting_preflight_20261117.sh` (Git blob `d18feaba3c4dea7c7345bb703b296dcb5c6bec16`) on original MAIN DEVELOPMENT. Complete operator-provided result:

```text
READ_ONLY_SCRIPT_SOURCE_AND_SYNTAX=PASS
PINNED_DEVELOPMENT_READ_ONLY_SOURCE=PASS
EXACT_PERSISTED_DRAFT_PAIR_NO_LEDGER=PASS
Traceback (most recent call last):
  File "<stdin>", line 142, in <module>
  File "<stdin>", line 18, in must
RuntimeError: STOP: INVOICE_ACCOUNT_MISMATCH
```

**Exact evidence:** Pinned app/worktree passed, saved batch exact Draft SI `ACC-SINV-2026-00001` and PI `ACC-PINV-2026-00005` with zero voucher-linked GL/SLE passed; script performed its Company currencies, conversion rates and base totals assertions before failing at first discrepancy among four **exact account name** equalities: SI `debit_to` vs expected CCPC `1312`, SI item `income_account` vs CCPC `6050`, PI item `expense_account` vs Ricor `5150`, PI `credit_to` vs Ricor `2121`, with names built from live Company abbreviation. **It did not report which field mismatched**, and execution never reached its checks of account metadata, Cost Center, or native `submit` rights. The original user terminal reports no `READ_ONLY_POSTING_PREFLIGHT=PASS`. This is an observed **preflight discrepancy**, not proof that saved accounting is wrong; ERPNext may have assigned or transformed an account during native Draft validation, or the expected assumption may be too strict.

**No financial write:** The preflight executes under `START TRANSACTION READ ONLY` and rolls back in `finally`. No `.submit()`, `.save()`, `frappe.db.commit()` or grant, no ledger postings, no invoice record changes, and no PRODUCTION action. Existing committed Drafts and SHA256 recovery sets must remain untouched. **HOLD all submit/GL testing**, including rollback-only submit rehearsals, until actual account mismatch is identified and reviewed; do not forcibly edit invoice accounts, rename ledger accounts, grant permissions or bypass native validations.

**Immediate next bounded diagnosis:** Added separate `scripts/development/operator/ccpc_pr33_main_readonly_invoice_account_diagnostic_20261117.sh` on docs PR37, a GitHub-pinned read-only diagnostic for exact two stored Draft invoices. In a fresh `START TRANSACTION READ ONLY`, confirm pinned app/worktree, original Approved batch, reciprocal Draft invoices and zero voucher-linked postings; print four `EXPECTED` vs `ACTUAL` stored account names, whether each is a valid non-group enabled Account in the correct Company/root/type, and exact name-match summary. Does not change records, invoice status or user grants and does not attempt native invoice submit rights. Operator must validate exact GitHub docs commit, diagnostic file blob, Bash syntax and embedded Python AST before running one step. Follow-up action depends on which account field differs; **do not infer values or fix data before evidence**.

## Verified immutable current development inputs

- App draft PR33 `review/billing-authorization-correction-2026-11-03` HEAD `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`; controller `intercompany_material_billing_batch.py` blob `a9a6e609759e77948d40d31bdbd342f727b208a9`; authority module blob `8de2d6ba2aa0f8995b727157491e236d2a0a8ae2`.
- MAIN DEV `development.localhost` on `ccpcerpserver`, Docker `frappe_docker_devcontainer-frappe-1`. Original one-line billing batch `Approved` under `finance_controller@ccpc.com` with existing Draft CCPC SI **`ACC-SINV-2026-00001`** and Draft Ricor PI **`ACC-PINV-2026-00005`**, reciprocal references, month-end date, frozen item/quantity/rate, no draft taxes/stock updates.
- Both original one-shot controller postcommit and **independent distinct Frappe/MariaDB `START TRANSACTION READ ONLY`** audit PASSED. Zero GL Entry and Stock Ledger Entry rows **for those two voucher identities**, not a database-wide assertion. Exactly one matching source-batch `remarks` each.
- Local recovery snapshot `development.localhost-20261117T043152Z-1582f342f870` and Synology copy `ccpc-development-pr33-main-precommit-20261117T044035Z-591a9f7e2b035cae` were four-part/SHA256 PASS **before the persistent Draft pair existed**; restore not tested. A **NEW post-Draft, pre-submit** database+files backup and independent offsite copy must be taken before any persistent native invoice submission to retain the current Draft pair if rollback/restore is necessary.
- Preserve old one-shot markers including `~/.ccpc-pr33-main-persist-draft-pair-once-20261117`; never rerun/clear prior approval/backup markers.

## Source-derived expected debit / credit, not actual posted GL

The CCPC custom controller `_get_company_invoice_defaults` constructs exact accounts per Company abbreviation, verifies Company/root/account type at Draft creation, and `_build_sales_invoice` sets `debit_to` and each invoice item `income_account`; `_build_purchase_invoice` sets `credit_to` and each item `expense_account`. These map to the expected **base-currency** four-account pattern for the original one-line Draft source, subject to actual submitted ERPNext validations and rules:

| Company / exact existing voucher | Expected debit | Expected credit | Basis |
|---|---|---|---|
| CCPC — SI `ACC-SINV-2026-00001` | `1312 - Intercompany Receivable - {CCPC abbr}` | `6050 - Intercompany Material Charges - {CCPC abbr}` | Sales Invoice `debit_to` vs item `income_account` |
| Ricor — PI `ACC-PINV-2026-00005` | `5150 - Intercompany Materials Expense - {Ricor abbr}` | `2121 - Intercompany Payable - {Ricor abbr}` | Purchase Invoice item `expense_account` vs `credit_to` |

Invoice grand totals and currencies were verified to match the batch at the earlier Draft acceptance; **actual live abbreviations, selected account names, exchange/base conversion, outstanding effect, rounded amounts and submit rights have not yet been re-inventoried by the posting preflight**. Do not invent actual Ricor abbreviation or currency/amount. CCPC income vs Ricor expense is across distinct legal ledgers; do not claim they net in a single Company's trial balance. The original issuing-side Material Issue Stock Entry was already **submitted** and is a separate transaction; do not double-book inventory from these invoices without a reviewed source-stock accounting reconciliation.

## Native ERPNext v16 source review and risks

Reviewed public `frappe/erpnext` `version-16` source `erpnext/accounts/doctype/sales_invoice/sales_invoice.py` (blob `297310abe9f4a17b2cee332bb8904a73a90a15a4`) and `purchase_invoice.py` (blob `6df4481aef271fbae0187de71de78ca9f7ae83e2`). Their `on_submit()` flows call `make_gl_entries()`; `update_stock==1` branches can create stock ledger entries, while the saved drafts have `update_stock=0`. They also run native tax withholding, accounting authority, linked-document status, credit/payment, common-party, and other hooks. The public upstream revision is **not proof of exact installed ERPNext source**, so review installed exact SHA/overrides, fiscal/accounting period, any financial freeze, accounts and party validity and real submit permissions before applying. Even `update_stock=0` does not prove zero accounting effects or no unrelated hooks.

Risks and required controls before a financial commit:
1. **Submittability**: eligible named user with native Sales Invoice **and** Purchase Invoice `submit` DocPerm and both Company grants; existing `Finance Controller` billing batch write privilege is NOT inherently native invoice submit authorization. No silent grants or `ignore_permissions=True` to bypass accounting approval.
2. **Posting period**: correct month-end fiscal year, accounting period/closing restrictions, frozen-date handling and approval hierarchy; don't silently move historical posting dates or bypass locks.
3. **Financial values**: frozen original source, correct internal parties and accounts, Company cost center, currency and rate, no discounts/taxes/rounding/TDS/write-off/asset or stock surprises, expected effective debit/credit and per-Company balanced GL; separately consider prior stock movement.
4. **Transaction + idempotency**: native SI/PI submit may run linked-document updates or outbound notifications; a two-invoice submit is not automatically one atomic financial decision. Simulate in a verified isolated disposable Frappe/ERPNext/MariaDB environment first if practical, or design a one-shot guarded MAIN DEV rollback-only rehearsal with exact external-effect containment and post-rollback audit. A successful rollback-only test does not prove persistent submit outcome. No retry after uncertain commit.
5. **Recovery**: take NEW four-part and offsite SHA256-verified backup **after** first Draft pair, BEFORE any eventual submit; document exact backup, targeted restore procedure and potential effects on concurrent DEV work. Do not restore over existing changes or PRODUCTION.

## Next one safe operator gate: CURRENT Draft accounting / native submit permission READ-ONLY inventory

New docs-only review script: `scripts/development/operator/ccpc_pr33_main_draft_pair_readonly_posting_preflight_20261117.sh` (Git blob to pin after review). This is **not a submit rehearsal**. It checks named DEV container, exact pinned detached app SHA and protected worktree; connects to MAIN with `START TRANSACTION READ ONLY`; asserts exactly one original Approved batch, exact Draft SI/PI links, frozen line, month-end/amount, no nonstandard amounts/tax/stock flags, zero voucher-linked GL/SLE; reads the actual Company abbreviation/currency and existing invoice fields/Account root/type/disabled status and cost centers; queries **native** SI/PI `submit` permissions for nominated `finance_controller@ccpc.com`; prints expected mapped debit/credit and currency/amount, and clearly marks native fiscal/hook checks as pending. Finally, it calls `frappe.db.rollback()` and destroys connection; it **never calls `submit()`, creates GL, or commits**. Stop on any drift. Its output will determine whether the next path is a limited finance role/authority review or an isolated native submit+GL test plan.

**Status as of this doc:** Script prepared in review branch **but not operator-executed**; all changes GitHub-only. PR33 still draft. No new backups or financial writes under this review approval.
