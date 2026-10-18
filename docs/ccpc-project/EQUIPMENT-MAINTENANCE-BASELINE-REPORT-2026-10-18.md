# CCPC Equipment Maintenance Cost & Reliability — first read-only report milestone

**Checkpoint date:** 2026-10-18. **Owner direction:** Continue implementation of approved Decision D operational Equipment tracking for management's repair-versus-replace analysis. **Not production-ready or deployable.**

## GitHub milestones verified

- New **app review branch**: [`review/equipment-maintenance-baseline-2026-10-18`](https://github.com/ccpcerp/ccpcerp/tree/review/equipment-maintenance-baseline-2026-10-18), deliberately based on [PR #13's prior issue/cancellation test branch](https://github.com/ccpcerp/ccpcerp/pull/13) at `6aea58f9d785f037076b75bc9e0b4bc7bf683bd2`, **not** on draft PR #14's unresolved accounting assertion.
- New separate **[draft PR #15](https://github.com/ccpcerp/ccpcerp/pull/15)**: standard CCPC ERP **read-only Script Report** `CCPC Equipment Maintenance Baseline`, Python/JS/Report JSON plus ten mocked tests. Latest report workflow commit `fc66a0e399dad03145022611b4d3ab84b51defd7` was verified from GitHub; full PR head to be checked again before merge or deployment.
- Dedicated GitHub-hosted mocked workflow [run 39089639936](https://github.com/ccpcerp/ccpcerp/actions/runs/39089639936) **PASS 10/10**. Follow-up [run 39089830336](https://github.com/ccpcerp/ccpcerp/actions/runs/39089830336) **PASS 10/10** at verified [app PR #15 head `a10617571dd03475a9ba6280e0ca2cde4335e510`](https://github.com/ccpcerp/ccpcerp/commit/a10617571dd03475a9ba6280e0ca2cde4335e510). These are Python **mocked** tests for access guards, date/company filters, parameterized SQL text, duplicate aggregation, explicit scope warnings and unknown-vs-zero labor handling. **No actual Frappe/MariaDB/SLE/GL queries were executed in either workflow.**
- Separate earlier app [draft PR #14](https://github.com/ccpcerp/ccpcerp/pull/14) **still intentionally fails** the original linked Material Issue GL beneficiary Department real test. Approval of report architecture is **not** approval to bypass original issue accounting corrections.

## Approved end goal and limited first delivery

**Approved Decision D:** Equipment is a **non-GL operational maintenance-cost tracking identity** with links to actual posted transactions and Job Orders. Do **not** create an Equipment General Ledger Accounting Dimension initially. Company/beneficiary Department/expense account/Cost Center GL controls A–C remain separate and required.

**What draft PR #15 presently computes:**

- Equipment and description from Equipment Registry, grouped within the **required Company**.
- **Gross submitted linked Material Issue stock-value decrease**, using `Stock Ledger Entry.stock_value_difference` joined by **exact** Stock Entry item `voucher_detail_no`. The query filters to `Material Issue`, submitted vouchers, noncancelled SLE, issue quantity, valid Withdrawal Slip provenance and Equipment Registry company. It does **not** claim the reported amount is a reconciled expense GL or the Equipment's complete net material cost.
- Number of noncancelled Job Orders and sum of **recorded/unpriced** `labor_hours`, with `date_assigned` as the Job Order period reference (not an estimate of downtime), plus number of Job Orders with **positive hours** (to avoid treating a default zero as evidence of recorded time). The real data-capture completeness remains unverified.
- Explicit visible **PARTIAL** disclosure and anomaly count for nonnegative stock value on an issued row. The report intentionally **excludes** approved physical returns (no return posting workflow implemented), outside service charges, actual labor cost, downtime, operating hours and replacement economics.
- Server-side `System Manager` restriction and source-document read checks; no grant of broad cost visibility to `CCPC Operational Supervisor` based on its role title. Parameterized Company/Equipment/date filters and cross-company rejection.

**Not ready for managerial repair-or-replace decisions.** A zero activity result means *no linked eligible rows within the chosen period*, not proof of zero maintenance spending; dates/jobs/materials may be incomplete. No Equipment life-cycle cash flow, productivity loss or actual maintenance total is yet available.

## Mandatory next review and test gates

1. **Real isolated Frappe v16/MariaDB tests:** Verify the new SQL against posted Material Issue + actual SLE (including multiple item batches/ledger rows), correct Group By totals, date filtering, canceled entries, Company isolation, and row/item linkage. Confirm the full Report DocType installs and the Standard report can be opened with the intended `System Manager` user. **Current 10/10 mocks are not substitutes.**
2. **Source immutability:** Existing query groups by `Withdrawal Slip.equipment` at report time; review and enforce a durable submitted-source Equipment snapshot or verify immutability. A later change to slip Equipment must **not** silently reattribute historical costs; equipment reassignment/asset handoffs need effective-date handling. Report on mismatches rather than silently guess.
3. **Accounting:** Original Material Issue's beneficiary Department expense GL in draft PR #14 remains uncorrected; owner-approved mappings A–C must be backed by real CCPC Company/account and Department-to-Cost-Center master data and accounting exception design. Report must reconcile source amounts before reporting total net financial maintenance costs.
4. **Return transactions:** Complete two-person verifier/supervisor Material Receipt authorization, original issued-unit cost basis, partial return cumulative limits, independence/lock/rollback and cancellation control. Then count linked **approved posted returns** once as credits against their actual source Equipment, never subtract UI-only `returned_qty`.
5. **Labor and services:** Verify labor-rate authority, Job Order-to-invoice/service line links, vendor service amounts, and controls preventing duplicate cost inclusion. Separate actual hours from unavailable/estimated data; do not estimate unapproved wage rates.
6. **Reliability:** Establish event and operating-time data to measure breakdown frequency, actual downtime and cost per operating hour; distinguish production downtime from Job Order elapsed time. Do not infer financial loss from missing records.
7. **Management evaluation:** Only after audited costs/reliability are available add repair-vs-replace comparisons including purchase/installation, remaining life, energy consumption, throughput impact and lifecycle economics.
8. **Performance/security:** Add relevant stock source/Equipment/date lookup indexes only after independent schema/migration review. Assess query plan and scaling, ERPNext user permissions, company isolation, potentially sensitive cost access, and zero/incomplete data labels.

## Deployment and continuing work

[Owner-approved equipment operational tracking checkpoint](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-D-APPROVED-2026-10-18.md), [accounting A–D source decision record](WITHDRAWAL-ISSUE-ACCOUNTING-ALLOCATION-DECISION-PROPOSAL-2026-10-18.md), [Option A return workstream](WITHDRAWAL-RETURN-CURRENT-CHECKPOINT-2026-10-17.md) and [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) remain authoritative.

**State:** Draft source at PR #15 head `a10617571dd03475a9ba6280e0ca2cde4335e510` + 10/10 mocked checks **verified** in two independent GitHub-hosted runs; real DB, installed report, permission enforcement, valuation, ledger reconciliation and source immutability **untested**. Review branches unmerged. No DEVELOPMENT pull, migrations, production database or role changes. **POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.**
