# Withdrawal Slip accounting — Decision B approved expense-account validation

**Owner approved 2026-10-18 — business policy only.** The owner approved the expense-account validation safeguard for CCPC material issues, following approved [Decision A: beneficiary Department precedence](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-A-APPROVED-2026-10-18.md). The source of truth for the complete decision set is the [accounting allocation design](WITHDRAWAL-ISSUE-ACCOUNTING-ALLOCATION-DECISION-PROPOSAL-2026-10-18.md), updated in verified commit [`8f16245`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/8f162457047470dd8288b64024fc2933ec973db3).

## Approved scope

- Before submitting a linked Withdrawal Slip **Material Issue**, require a valid **approved expense account for the issue Company and material/item category**.
- ERPNext's generic Company **Stock Adjustment Account is NOT an automatic authorization**: it may be selected only if specifically approved for that company/material category and suitable for the actual accounting purpose.
- Missing, ambiguous, inactive, incompatible, cross-company or otherwise unverified account mapping must **block the controlled posting** and require an accounting-controlled resolution. Never silently use an arbitrary or unrelated fallback.
- An accepted separately linked material return must reverse consumption against the **actual expense account posted on the original submitted Material Issue**, not recompute expense accounts from changed Item, Item Group or Company defaults.
- Continue to enforce Decision A beneficiary Department precedence and its stop-and-review controls; approval of the expense-account rule does **not** approve any particular account mapping or financial exception.

## Not yet approved or verified

- Exact CCPC Company/item/material-category account numbers and mapping authority, including whether Item or Item Group defaults are approved masters; exception reviewer; any schema or master-data changes; history corrections.
- **Decision C — OWNER-APPROVED SAFEGUARD (2026-10-18):** The beneficiary Department must resolve to an approved Company-specific Cost Center; multiple valid centers require explicit validated selection; missing/ambiguous mappings must block posting. **Exact Department-to-Cost-Center mappings and mapping master-data design are still pending.** See [Decision C checkpoint](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-C-APPROVED-2026-10-18.md). **Decision D remains undecided:** whether Equipment is a GL Accounting Dimension or immutable operational cost tag.
- Actual CCPC DEVELOPMENT/PRODUCTION account and Accounting Dimension configurations, plus stock valuation and GL correction behavior for original-cost physical Material Receipts.

## Verification and safety status

App [draft PR #14](https://github.com/ccpcerp/ccpcerp/pull/14) remains a test-only, unmerged review; previously verified [disposable CI run `39085044119`](https://github.com/ccpcerp/ccpcerp/actions/runs/39085044119) passed 72/72 mocked and 8/9 genuine MariaDB tests but correctly failed the CCPC beneficiary accounting assertion (native ERPNext Department control passed). **No application posting code, role names/assignments, accounting configuration, database, DEVELOPMENT or PRODUCTION systems were changed for this approval.**

**POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.**
