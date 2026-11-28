# CCPC ERPNext — Build #34 verified acceptance handoff (2026-10-29)

> Supplemental newest checkpoint for the GitHub-first CCPC project. This note records the verified milestone after the existing large `CURRENT-HANDOFF.md` could not be safely updated through the connected file API. The comprehensive historical handoff remains intact. See also [integrated engineering record](INTEGRATED-WITHDRAWAL-LEDGER-BILLING-REVIEW-2026-10-29.md).

## Latest verified Finance / Withdrawal / intercompany integration

**CircleCI build #34, job `finance-lifecycle-isolated-integration` (green in owner-provided CircleCI screenshot)** on disposable `ci-finance-lifecycle.localhost`:

- Original owner-uploaded `build_34_step_105_container_0.txt`: `ccpcerp.ccpc_erp.test_finance_lifecycle_disposable_integration`, 8 green individual tests A–H, `Ran 8 tests in 2.365s`, `OK`, no reported failures/errors/skips.
- Original owner-uploaded `build_34_step_106_container_0.txt`: `ccpcerp.ccpc_erp.test_finance_withdrawal_billing_bridge_disposable`, 4 green tests A–D, `Ran 4 tests in 8.984s`, `OK`, no reported failures/errors/skips. Nonfatal `V17FrappeDeprecationWarning` for `limit_page_length` (use `limit`).
- **Combined same build/site: 12/12 confirmed PASS.** Previously failed C/D in CircleCI build #31 because test fixture attempted Account creation directly on nested `_Test Company 5` without the `_Test Company 3` root prerequisite; root-first test-only PR #27 fix is now verified by the actual four green SQL tests.

### Scope proven

Finance mapping schema, Maker/Checker signed approval and rejection/retirement audit, fail-closed identity/forgery/replay and decision rollback, exact Company/Department Center approval; real signed original Withdrawal Material Issue, SLE and expense GL source reconciliation, intercompany source eligibility and unsigned denial; persisted month-end billing finalization with controlled test-only billing clock, real unsubmitted Sales/Purchase Invoice draft insertion and cross-link, amounts and source quantity, no invoice GL or stock update, double-approval denial; a deliberate failure after the first real Sales Invoice SQL insert causing savepoint removal of orphan and one safe retry. These are **real isolated MariaDB tests**, not mocked accounting. The billing clock is simulated only in the disposable month-end test.

### Verified GitHub state

- Application repo: `ccpcerp/ccpcerp`, Finance branch `feature/finance-mapping-lifecycle-2026-10-28`, HEAD `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`. PR #27 merged, root-first fixture test module blob `530cc3bf197b186ebe08a5a22c2fa25998378fd4`, four test methods. CI config blob `8f64c1c0968934305e3dcb2f5720b93f15a719ec` keeps manual `finance-bridge-manual-approval` and `run_finance_bridge: false` by default.
- This supplied runner log pair does **not print full checkout SHA**; matching source in GitHub and the approved operator workflow establish contextual association but not independent per-step SHA attestation.
- No new application edits, CI reruns, DEVELOPMENT or PRODUCTION operations resulted from receipt of these logs.

## Release boundaries and next priorities

**PRODUCTION NO-GO.** The 12/12 disposable test milestone does **not** prove invoice submission/cancellation/returns or resulting intercompany AR/AP/GL, actual Company accounting signoff, duplicate prevention under concurrent HTTP requests, rollback/recovery of submitted entries, complete security/CSRF/concurrency, four approved day-one reports, or integration into persistent DEVELOPMENT. The precise four frozen report families remain:

1. Department material consumption.
2. Equipment/Job Order consumption.
3. Intercompany Withdrawal and billing, including paired invoice status.
4. Company-wide material consumption and all-company P&L expense with reconciled SLE/GL, never double-count intercompany expense or mix UOM/currencies.

Next GitHub-first engineering milestone: inspect/report existing reporting code and design the four reports, accounting reconciliation, and permissions on a separately reviewed feature branch. Review invoice submission/reversal and actual CCPC accounting masters with the owner. CI reruns, DEVELOPMENT testing and PRODUCTION deployment require their own explicit approvals and safe checks.
