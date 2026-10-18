# CCPC Equipment maintenance baseline — snapshot-source report cutover and direct-voucher tests

**Date:** 2026-10-18. **Owner directive:** Continue GitHub-only review branch development; test forged direct Stock Entry submissions and move the read-only gross Material Issue report from mutable Withdrawal Slip Equipment to independently stored issue-row snapshots. **No historical transaction backfill, real-site schema migration, DEVELOPMENT pull, PRODUCTION release, or financial accounting posting change was authorized.**

## Source-of-truth changes under review

- App [draft PR #15](https://github.com/ccpcerp/ccpcerp/pull/15), branch `review/equipment-maintenance-baseline-2026-10-18`, builds on previously verified [10/10 real snapshot issue validation tests](https://github.com/ccpcerp/ccpcerp/actions/runs/39094318174).
- The read-only report now associates submitted original Material Issue SLE rows through exact `Stock Entry` / `Stock Entry Detail.name = Stock Ledger Entry.voucher_detail_no` and groups **gross stock-value differences** by the snapshot fields `ccpc_equipment_at_issue` and `ccpc_equipment_code_at_issue` rather than grouping by the **current** `Withdrawal Slip.equipment`.
- A **left** join to Equipment Registry, restricted to the original voucher Company, permits valid Equipment Link+Data attribution but preserves anomalous source values. A source-quality classification isolates:
  - `SNAPSHOT_MATCHES_SOURCE`: original row Link and Data agree, Equipment Registry is same Company, and current Slip Equipment matches.
  - `SLIP_SNAPSHOT_CONFLICT`: original matched snapshot is retained under its original Equipment but current Slip conflicts, shown **separately** and flagged as requiring review.
  - `LEGACY_NO_SNAPSHOT`: old submitted issue row with both source values blank; surfaced as an unattributed **positive or negative gross stock-value difference**, not silently assigned to current Equipment and not zeroed.
  - `SNAPSHOT_PAIR_CONFLICT`: original Link/Data missing on only one side or disagree, quarantined unattributed.
  - `MASTER_OR_COMPANY_INVALID`: missing or cross-Company Equipment master, quarantined unattributed.
  - `JOB_ORDER_ONLY`: available Job Order activity without eligible original posted issue; not priced or certified Equipment financial cost.
- A selected Equipment filter intentionally shows eligible source rows only. It warns that **unattributed company-wide material issues are excluded by the filter**. The Company-wide report is required to assess outstanding original-Equipment source exceptions. Do not silently combine conflicting values with verified snapshots or priced Job Order data.
- Direct-voucher negative real tests create an independent synthetic Withdrawal Slip, try forged `Stock Entry.insert(ignore_permissions=True)` with absent source Link and try `Stock Entry.submit()` with mutated saved original-number Data. Both must reject before SLE/GL creation. A separate real test intentionally changes stored snapshot Data on a disposable DB to verify that the company-wide report still accounts for the stock value as unattributed, without editing underlying GL.
- Read-only report is still a **gross issue-valuation baseline**, **not** a complete equipment maintenance cost, posted-return netting, GL expense or investment/repair-vs-replace recommendation. The frozen Equipment Link/Data source is not tamper-proof against privileged direct database editing; corrections need audit trail and Accounting review. Labor, outside services, downtime, operating hours, partial returns and accounting mapping A–C remain unfinished.

## Current testing and release gate

The code changes are on the GitHub draft branch. GitHub-hosted **mocked** [run `39096282908`](https://github.com/ccpcerp/ccpcerp/actions/runs/39096282908) **COMPLETED SUCCESS: 12/12 mocked** (review branch query/classification unit tests). The [real disposable ERPNext v16/MariaDB run `39096282930`](https://github.com/ccpcerp/ccpcerp/actions/runs/39096282930) was **in progress when this checkpoint was first recorded**, intended to execute **13 actual source and report integration tests**. Do not call real DB report or forged voucher checks successful until run logs and workflow conclusion are separately reviewed, then update this checkpoint.

Pending after these specific tests: true source lineage and Accounting Dimension/Cost Center policy audit with PR #14, controlled original physical Material Receipt return workflow, actual labor/invoice/downtime/operating-hour sources, legacy exception review drilldown, query-plan/index review, nuanced source permissions, and verified DEVELOPMENT origin and backup before any authorized migration or pull. **Draft PR #14** remains unmerged with unresolved original Material Issue beneficiary Department GL assertion.

**STOP:** `POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP`. Neither CCPC deployment environment, accounting master data, roles, posted stock records nor production operations were changed by this GitHub work.
