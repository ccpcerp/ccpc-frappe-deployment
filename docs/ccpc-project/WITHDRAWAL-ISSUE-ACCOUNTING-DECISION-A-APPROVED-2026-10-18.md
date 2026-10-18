# Withdrawal Slip accounting — Decision A approval and continuation

**Owner approved 2026-10-18 — BUSINESS POLICY ONLY.** This is a small rolling checkpoint because the larger withdrawal workstream handoff could not safely be updated.

## Beneficiary Department selection — approved

1. Resolve the original Material Issue beneficiary from a valid same-company explicit `work_for_department`.
2. If it is missing, use the validated Department of the specified Equipment Registry record.
3. If explicit `work_for_department` conflicts with Equipment Registry Department, **block automatic posting** until an authorized, auditable review resolves the mismatch.
4. If neither identifies the actual beneficiary, **block posting** rather than silently charge the requesting `department`.
5. Require eligible active leaf Department, immutable source provenance, and properly configured Department GL dimensions before describing an expense attribution as verified.

**Not authorized by this approval:** Assigning a conflict reviewer, editing accounting masters, enabling dimensions, changing app posting behavior, deploying, or changing roles.

## Verified GitHub evidence

- Detailed [accounting allocation proposal](WITHDRAWAL-ISSUE-ACCOUNTING-ALLOCATION-DECISION-PROPOSAL-2026-10-18.md) marked **Decision A approved** in verified commit [`25d65c3`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/25d65c3aa92f4a0629a317fbd39c427a4030a739).
- App [draft PR #14](https://github.com/ccpcerp/ccpcerp/pull/14) remains **unmerged/test-only**. In disposable [run `39085044119`](https://github.com/ccpcerp/ccpcerp/actions/runs/39085044119), 72/72 mocked and 8/9 real tests passed, but the CCPC linked Material Issue GL beneficiary assertion still failed; native ERPNext dimension control passed. No CCPC deployed configuration or actual GL records have been inspected.

## Pending decisions

**Decision B — OWNER-APPROVED POLICY (2026-10-18), MAPPING STILL PENDING:** Require an approved company/material-category expense account before Material Issue posting; block missing/ambiguous/invalid accounts rather than silently using the Stock Adjustment Account. The Stock Adjustment Account is permissible only with explicit accounting approval for the purpose. Actual CCPC account numbers and mappings are still undecided. See [Decision B checkpoint](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-B-APPROVED-2026-10-18.md).

**Decision C:** Authorized company-specific beneficiary Department-to-Cost-Center mapping, missing/multiple-center handling and master-data strategy.

**Decision D:** Whether Equipment belongs on the GL as a configured Accounting Dimension or remains an immutable operational reporting tag.

Original-cost physical Material Receipts and supervisor separation retain earlier owner approvals; actual accounting and return posting implementation still needs independent tests and permissions review. **POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.**
