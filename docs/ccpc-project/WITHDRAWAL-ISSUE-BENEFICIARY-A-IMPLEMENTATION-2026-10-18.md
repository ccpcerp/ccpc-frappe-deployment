# CCPC original Material Issue — beneficiary Department source propagation (Decision A)

**2026-10-18 — GitHub-only review milestone, UNMERGED / not deployed.** Owner requested continuing the accounting source-attribution milestone after completion of the provisional Equipment cost report. Business policies A–D were approved earlier; this milestone implements only the **Decision A beneficiary-source selection and GL field propagation** in an isolated accounting review branch, and **does not approve/implement actual company expense-account or Department→Cost Center mapping records**.

## Code scope

- [Draft app PR #14](https://github.com/ccpcerp/ccpcerp/pull/14), branch `review/withdrawal-issue-accounting-ci-2026-10-17` (based on `review/withdrawal-cancellation-ledger-ci-2026-10-16`). Do not treat this as merged or a deployable release.
- New `ccpcerp/ccpc_erp/withdrawal_issue_beneficiary.py`: explicit `Withdrawal Slip.work_for_department` is preferred; `Equipment Registry.department` is used only if no explicit beneficiary exists. If both exist and disagree, block automatic issue for separately authorized auditable review. If neither exists, reject issue: requester `Withdrawal Slip.department` is not a silent fallback. Validate active leaf Department from the issue Company; reject cross-company Equipment. Require **active** Department GL Accounting Dimension with real `department` fields on Stock Entry, Stock Entry Detail and GL Entry; do not infer successful GL attribution from a dormant custom field.
- Updated `withdrawal_slip_stock.py`: populate original Material Issue header and every detail with validated beneficiary Department. Lock/compare source Equipment and beneficiary alongside other Withdrawal Slip fields to detect stale values. Before submission, refuse direct-voucher changed/cleared Department values; preserve existing row provenance and duplicate/transaction safety mechanisms.
- Synthetic disposable tests: existing strict linked original issue GL-Department assertion remains; add explicit-source absence rejection, Equipment/explicit beneficiary conflict rejection and forged Stock Entry Department rejection without SLE/GL posting. The ordinary synthetic stock fixture now explicitly identifies a valid beneficiary rather than relying on requester.
- This branch does not include later Equipment issue-time source snapshot/report modifications from distinct [draft PR #15](https://github.com/ccpcerp/ccpcerp/pull/15). **A deliberate code review/merge reconciliation will be required before either feature is integrated into one app branch.** Do not pull one draft to DEVELOPMENT simply to obtain both.

## Controls still pending

**Decisions B and C are approved business safeguards only.** Accounting must identify for each issue Company and material/item category its **specifically approved expense account** (Company Stock Adjustment Account cannot silently be used), plus the **approved beneficiary Department→Cost Center** selection and procedure for multiple valid centers. Missing/inactive/incompatible/ambiguous mapping must block posting; generic ERPNext account/Cost Center defaults in synthetic CI are **not** approval of live CCPC financial mappings. No posting release until this validation is implemented and real GL attribution verified with approved masters.

Original-cost, linked, independently approved partial material returns remain unimplemented. No Expense Account/Cost Center numerical entries, GL Equipment Accounting Dimension, Stock Entry return receipt, historical edits, user roles, actual DEVELOPMENT test/pull, or PRODUCTION deployment authorized here.

## Test-status reporting requirement

The isolated accounting CI for app [PR #14](https://github.com/ccpcerp/ccpcerp/pull/14) was **started** with extra real missing/conflicting/forged beneficiary checks. The outcome must be checked using GitHub Actions run conclusion and actual test logs; **do not claim a pass from only source commits or the previous 8/9 diagnostic run**. The prior [CI run 39085044119](https://github.com/ccpcerp/ccpcerp/actions/runs/39085044119) remains historical evidence: native explicitly assigned Department reached expense GL but linked CCPC issue omitted Department.

**POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP**. No live CCPC site or data touched.
