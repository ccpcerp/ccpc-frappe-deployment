# CCPC Withdrawal Slip — physical return workstream checkpoint

**Verified:** 2026-10-17, source/documentation-only work on branch `docs/ccpc-checkpoint-2026-10-10`. GitHub is authoritative. The full rolling `CURRENT-HANDOFF.md` is larger than practical for safe replacement through the current connector; this small checkpoint records the latest policy decisions while preserving existing handoff contents.

## Approved owner decisions

- **Option A:** Original Material Issue expensed on issue; physical return uses a **separate linked Material Receipt** (never cancel the valid source issue merely to return unused material).
- **Original posted issued-unit cost:** Net Equipment and beneficiary Department material consumption decreases by the approved value of accepted material; valuation exceptions require accounting review, no arbitrary rate change.
- **Two-person segregation:** Stockroom Personnel physically receives/verifies material; a **different authorized stockroom supervisor** independently approves/submits the receipt. Audit both identities and times.
- **Return condition:** Only unused, serviceable, identifiable correct-company material is eligible for automatic return to available stock. Damaged, partially used, contaminated, uncertain-condition and scrap material requires separate inspection/appropriate quarantine and no automatic stock or expense reversal.
- **Multiple partial returns:** Separately accepted and approved receipts may return part of an original issue over time, but cumulative submitted accepted stock quantity must not exceed that same original issue row, even during concurrent requests.
- **Return cancellation — latest owner approval:** An authorized stockroom supervisor may cancel an incorrectly submitted **return receipt**, subject to accounting controls. Reverse only that receipt's stock/GL and its accepted return quantity; recompute net Equipment/Department consumption, preserve the original Material Issue and other valid returns, and keep the audit history. **Block original Material Issue cancellation while any submitted, non-cancelled linked return exists**; do not auto-cascade reversals. Check resulting stock availability, period locks and duplicate/retry safety before cancellation.

## Current verified GitHub artifacts

- [Owner-approved return policy](WITHDRAWAL-MATERIAL-RETURN-POLICY-DESIGN-2026-10-16.md): updated with cancellation approval in commit [`849628e`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/849628e33f3d2a78689e30cfcf802c46fa030049); conflicting outdated 'undecided' statements corrected at [`010765b`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/010765bc23c18a61f244c4db5705ce64554c7356).
- [Accounting and controls review](WITHDRAWAL-RETURN-ACCOUNTING-AND-CONTROLS-REVIEW-2026-10-17.md): cancellation design/test plan committed at [`451d39e`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/451d39e2772b850ec910082ab746f0649e006998), consistency update at [`92c6c59`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/92c6c592cd296a4d1fb571d4d3c26d3dcdc4b47f).
- App [draft PR #13](https://github.com/ccpcerp/ccpcerp/pull/13) still open/unmerged at `6aea58f9d785f037076b75bc9e0b4bc7bf683bd2`. [CI run 38900855857](https://github.com/ccpcerp/ccpcerp/actions/runs/38900855857) **79/79 PASS** is the **prior original-issuance and original-cancellation synthetic checkpoint**; it DOES NOT verify separate physical returns or return cancellations. No new code/tests/host operations in these policy-approval conversations.

## Next review and safety gate

Verify original Material Issue `expense_account`, `cost_center`, Equipment and beneficiary Department allocation; decide precise GL credit/valuation exception mechanics with accounting, map authorized stockroom receiver/supervisor/canceller to verified existing Frappe roles, determine handling of serial/batch/condition exceptions and receipt cancellation when returned items were consumed. Then authorize a GitHub-only scoped implementation/test branch, real isolated MariaDB/SLE/GL verification; maintain 79/79 baseline. **NO app implementation authorized by these policy decisions. NO DEVELOPMENT/PRODUCTION mutations or deployments. POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.**
