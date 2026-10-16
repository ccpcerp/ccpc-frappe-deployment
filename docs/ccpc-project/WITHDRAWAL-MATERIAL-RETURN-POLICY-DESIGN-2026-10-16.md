# Withdrawal Slip — physical material return policy and accounting design (DRAFT)

**Date:** 2026-10-16  
**Status:** DESIGN / OWNER AND ACCOUNTING DECISION REQUIRED — NO TRANSACTION IMPLEMENTATION APPROVED  
**Repository evidence:** Application review branch `review/withdrawal-cancellation-ledger-ci-2026-10-16` at `6aea58f9d785f037076b75bc9e0b4bc7bf683bd2` (draft PR #13, unmerged); independently passing hosted CI [38900855857](https://github.com/ccpcerp/ccpcerp/actions/runs/38900855857) = 72 mocked Frappe + 7 genuine synthetic MariaDB/WSGI tests = **79/79 PASS**. Previous PRs #7–#12 are also drafts/unmerged.

## 1. Source-verified present behavior — not a real physical return

- In `ccpcerp/ccpc_erp/doctype/withdrawal_slip/withdrawal_slip.py`, `_validate_issue_tracking` validates `0 <= returned_qty <= issued_qty` for each Withdrawal Slip Item; `_set_issue_tracking_totals` computes `net_used_qty = max(issued_qty - returned_qty, 0)`. Those are **document fields and derived quantities**, not necessarily inventory movements.
- `STOCKROOM_ITEM_FIELDS` includes `issue_qty`, `physical_discrepancy`, `discrepancy_remarks`, and `stockroom_remarks`, **but not `returned_qty`**. `_validate_stockroom_controls` therefore does not itself enforce a stockroom-only edit path for the `returned_qty` field. Actual field-level DocPerms/UI/roles need separate review before assigning exploitability or asserting any user has permission.
- `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` recomputes `issued_qty` from *submitted linked Material Issue Stock Entries*, but `returned_qty` is only read while calculating `net_used_qty`. The file does **not** currently create a linked Material Receipt, transfer, returned-item stock ledger movement, or GL credit/debit when `returned_qty` changes.
- `ccpcerp/hooks.py` installs Stock Entry `on_cancel` sync; [CI 38900855857](https://github.com/ccpcerp/ccpcerp/actions/runs/38900855857) verifies real **cancellation of the original submitted issue** on a disposable test site restores Bin quantity and value, reverses GL by account, and resets Slip issue state. Cancelling the original issue is a **different business event from returning unused materials after issue**. Do not cancel original issue merely to register a partial/physical return.

## 2. Decisions required before implementing real return posting

1. **Return business model.** Preferred *candidate*, not approved: create an authorized, individually numbered and submitted **Stock Entry of purpose Material Receipt**, linking each returned item to its original Withdrawal Slip, exact Slip Item, and original submitted Material Issue row. An alternate custody model is a **Material Transfer** from an explicit employee/custody warehouse back to stockroom. Decide whether CCPC tracks issued materials as consumed at issue, or transferred into employee custody. This choice determines the correct voucher and GL flow.
2. **Who is allowed to receive, verify, and approve return** (Stockroom Personnel, receiving witness, supervisor, or different approval chain); which roles may create vs submit vs cancel. Direct `returned_qty` editing should not masquerade as a posted return.
3. **What kinds of return qualify.** Unused/resalable material back to its same company and approved warehouse versus damaged, scrap, wrong company, unusable, partially used, serial/batch-controlled, or consumed supplies. Define reject/quarantine/revaluation workflows separately.
4. **Valuation and GL account policy.** Select whether accepted returned stock is valued at the **original outgoing cost** (with document-row provenance), an ERPNext-generated current valuation/rate, or an authorized accounting adjustment. Confirm desired debit inventory and credit expense/stock-adjustment mapping with accounting; ERPNext's native Material Receipt does **not automatically prove it reverses the original consumption/expense account**. No accounting policy inferred or implemented.
5. **Partial and multiple returns.** Whether repeated partial returns are permitted; maximum returned units = successful original issued units less previously accepted linked return units; whether to support cancelling a mistaken return without cancelling original issue; which Slip statuses to allow.

## 3. Proposed transaction integrity conditions (pending decisions)

- **One source of truth:** Derive accepted `returned_qty` from **submitted, valid, non-cancelled linked return vouchers**, not manual field edits; preserve immutable source Slip Item, company, original issue row, stock UOM, original warehouse, posting author, receipt evidence, and any serial/batch numbers.
- **Permission and provenance:** Fail closed before inserting return draft or posting. Verify returner/receiver role and company/warehouse access via actual DocPerms; avoid broad `ignore_permissions` for already user-editable drafts, reassignments, or cross-company transfers. Capture physical receiver, return time, reason, condition and approval as audit data.
- **Idempotency/concurrency:** A stable return-request ID or nonce must be unique at SQL level; lock the source Slip/issue and return request inside one database transaction; two simultaneous submissions must produce **at most one** accepted return. Reject quantities exceeding the unreturned posted issue balance, stale status, duplicate reference or mixed-document provenance.
- **Accounting:** Require a validated submitted stock voucher, real SLE, Bin stock and valuation, and company-account-balanced GL mapping before updating Slip return totals. A failed submit/GL posting must roll back all rows and Slip totals. Cache invalidation should happen after commit only.
- **Cancellation/exception:** Cancelling an accepted return should reverse its own stock/GL, reduce only its own contribution to `returned_qty`, and leave the original issue intact. No silent deletion/rewriting of original SLE/GL history.
- **Never touch physical CCPC DEV/PROD** before separate verified target provenance, backups, restoration readiness and per-environment approval.

## 4. Independent test plan once policy is approved

- New **GitHub-hosted disposable test branch** from the verified review feature chain; all fixtures use unique synthetic `_Test Company` records. New tests should retain prior 79/79 regression baseline.
- Positive partial receipt and full return with independent MariaDB verification: initial issue -1 / GL 100 in test currency, receipt +approved quantity with correctly reconciled valuation/GL per agreed accounting policy; Slip `issued_qty` must remain historical issue and `returned_qty` must reflect **only** posted return.
- Negative: unauthorized preparer/guest, missing CSRF, wrong company/warehouse/UOM/serial, return exceeding issue, direct spoofed `returned_qty`, zero/damaged return, unapproved condition.
- Two concurrent receive sessions on same return request, duplicate submit/replay, competing partial returns that together exceed available issued balance, transaction error after stock but before GL, and rollback-after-commit visibility.
- Cancel return → stock+GL reversal, historical issue unchanged, net-used amount recalculated; cancelled original issue with an outstanding linked return must have an explicit policy (block or controlled reversal order) and test.
- Full audit comparison by source issue/return voucher including physical custody acknowledgement; backup/restore and server-specific Redis/RQ/browser/proxy remain later independent gates.

## 5. Go/no-go and next owner decision

**GO for policy discussion and further source-only inspection. NO-GO for implementing, merging, deploying, or posting any material return until the business custody model, approval roles, and valuation/accounting policy are explicitly selected.** Current 79/79 tests prove *issuance and original-voucher cancellation*, **not employee material returns**. All production posting remains **POSTING_NO_GO / PRODUCTION NO-GO**.

**Decision requested:** For materials issued to staff, does CCPC treat them as **consumed/expensed immediately** (unused items returned via a separately linked *Material Receipt*) or as **stock held by a staff/custody warehouse** (returned via *Material Transfer*)? Accounting should then approve the corresponding valuation and GL account mapping before code changes.
