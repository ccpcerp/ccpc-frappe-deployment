# CCPC Withdrawal Slip accounting — Decision D approved

**Owner approval:** 2026-10-18. **Status:** Approved architectural/business policy; implementation and integration tests pending. This is the current concise continuation checkpoint for Equipment maintenance-cost attribution.

## Approved Equipment treatment

Track Equipment **operationally**, using an immutable Equipment Registry identity and auditable links to Job Orders, submitted Withdrawal Slip / Stock Entry Material Issue rows, accepted separately linked Material Receipts, and valid posted outside service/labor expense evidence. Preserve the originally issued Equipment and linked source accounting for accurate credits and reporting. **An Equipment GL Accounting Dimension is not required initially and is NOT authorized for deployment by this approval.**

A Financial GL entry remains booked to its approved Company, original expense account, beneficiary Department and Cost Center (owner-approved Decisions A–C); Equipment attribution complements this and must **not** post a second charge or substitute for financial dimension controls. Reflect posted issue actual stock valuation and independently approved original-cost returns; exclude or reverse cancelled and invalid postings. Attribute invoices, labor and services once, with deduplication and proper company controls.

## Management goal: repair-versus-replace

Prepare for an Equipment Maintenance Cost & Reliability Report / dashboard showing available data on (a) repair materials net of returns, (b) labor hours and approved cost rates, (c) external maintenance services, (d) job history, breakdown counts and downtime, (e) monthly/annual/lifetime cost and cost per operating hour where operating hours are recorded, and (f) trends that support repair-versus-replace analysis. Distinguish **available**, **not yet captured**, and **estimated** data; do not equate missing downtime/labor rates with zero. Replacement economics requires separately sourced purchase/installation, remaining life, energy/productivity and opportunity-cost assumptions.

## Verified current project sources and limits

- [Equipment Registry](https://github.com/ccpcerp/ccpcerp/blob/review/withdrawal-issue-accounting-ci-2026-10-17/ccpcerp/ccpc_erp/doctype/equipment_registry/equipment_registry.json) contains company, department, equipment number, criticality, status and capacity context.
- [Job Order](https://github.com/ccpcerp/ccpcerp/blob/review/withdrawal-issue-accounting-ci-2026-10-17/ccpcerp/ccpc_erp/doctype/job_order/job_order.json) contains Equipment/Asset links, start/finish, labor hours, failure details and work findings; these do **not** alone establish downtime expense or hourly labor cost.
- [Withdrawal Slip](https://github.com/ccpcerp/ccpcerp/blob/review/withdrawal-issue-accounting-ci-2026-10-17/ccpcerp/ccpc_erp/doctype/withdrawal_slip/withdrawal_slip.json) carries Equipment, linked Job Order and requesting vs beneficiary Department; [Equipment Asset Assignment](https://github.com/ccpcerp/ccpcerp/blob/review/withdrawal-issue-accounting-ci-2026-10-17/ccpcerp/ccpc_erp/doctype/equipment_asset_assignment/equipment_asset_assignment.json) stores time-bounded assignment history.
- [Full issue accounting decision record](WITHDRAWAL-ISSUE-ACCOUNTING-ALLOCATION-DECISION-PROPOSAL-2026-10-18.md) now marks A, B, C and D owner-approved as policies; verified commit [`b623719`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/b62371959f1e72c9c6d245021c262e392fb1b20d).
- [App draft PR #14](https://github.com/ccpcerp/ccpcerp/pull/14) remains test-only/unmerged. [Disposable CI run 39085044119](https://github.com/ccpcerp/ccpcerp/actions/runs/39085044119) verified 72 mocked PASS, 8/9 genuine real tests PASS; original linked issue expense GL beneficiary Department still FAIL despite native Department control PASS. No evidence of correct CCPC deployed ledger allocation.

## Outstanding gates

1. Accounting must approve actual Company/material-category expense-account mappings and Company/beneficiary Department-to-Cost-Center crosswalk. A–C policies do not designate those records, exception reviewer or history corrections.
2. Decide reporting data capture and attribution rules for Job Order labor cost, external invoices, downtime, operating hours, and cost categories; build tests covering partial returns, cancellations, distinct beneficiaries, multiple Equipment in one document, reassignments, and duplicate-charge prevention.
3. Verify actual intended DEVELOPMENT source/configuration and existing uncommitted work before any pull; new transactional code/reports, Accounting Dimensions, role permissions, migrations and releases need separately scoped authorization. Do not change `CCPC Operational Supervisor` naming or grant stockroom return powers.
4. Physical return Material Receipt stock and GL behavior, original-cost reversal and supervisor two-person separation still need real isolated tests. No completed equipment costing report or physical return posting is claimed.

**POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.** No app code, databases, account masters, role assignments, DEVELOPMENT or PRODUCTION operations were changed by this owner policy approval.
