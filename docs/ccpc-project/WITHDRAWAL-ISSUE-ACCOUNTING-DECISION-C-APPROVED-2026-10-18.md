# Withdrawal Slip accounting — Decision C approved Cost Center safeguard

**Owner approved 2026-10-18 — business policy only.** Earlier approved accounting policies remain authoritative: [Decision A (beneficiary Department)](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-A-APPROVED-2026-10-18.md) and [Decision B (expense-account validation)](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-B-APPROVED-2026-10-18.md). The detailed [allocation decision document](WITHDRAWAL-ISSUE-ACCOUNTING-ALLOCATION-DECISION-PROPOSAL-2026-10-18.md) marked Decision C approved in [verified commit `8eb36b7`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/8eb36b712e17d61db436f30fc7fa4a9d0005dc1a).

## Owner-approved scope

- Every controlled Withdrawal Slip **Material Issue** must resolve a valid, explicitly approved **Company and actual beneficiary Department → Cost Center** mapping before posting.
- Confirm the Cost Center is active, non-group, within the issue Company, and suitable for the expense. Do not infer correctness from its displayed name or a generic company-wide default.
- If a beneficiary Department has several legitimate approved Cost Centers, **explicitly choose and validate the correct mapped Cost Center** under accounting-controlled rules and retain the supporting audit context. Do not silently use the first available candidate.
- When an approved, suitable and unambiguous Cost Center cannot be resolved, **block posting and request accounting resolution**, not a fallback to the requester Department or unrelated Company Cost Center.
- When later returning unused material through a separately approved linked Material Receipt, preserve the **actual original issue's posted Cost Center**, together with its posted expense account, beneficiary Department, Equipment provenance where relevant, and original valuation basis. Do not re-resolve to a changed current mapping.

## Not decided or not implemented

- Exact CCPC Department–Cost Center crosswalk for each Company, whether Section contributes to selection, the source-of-truth master-data design, selection workflow, accounting exception authority, historical corrections and how to address already-posted entries.
- **Decision D — OWNER APPROVED 2026-10-18:** Equipment is an **operational maintenance-cost attribution field with auditable source links**; no Equipment GL Accounting Dimension is required initially. See [Decision D approval checkpoint](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-D-APPROVED-2026-10-18.md). Reporting logic, integrations, master-data procedures and Equipment GL dimension configuration remain unimplemented and unapproved for deployment.
- App [draft PR #14](https://github.com/ccpcerp/ccpcerp/pull/14) is **unmerged/test-only**: [disposable run 39085044119](https://github.com/ccpcerp/ccpcerp/actions/runs/39085044119) passed 72/72 mocked and 8/9 genuine integration tests, with the strict original linked issue Department GL assertion still failing (native ERPNext explicit Department control passed). No evidence of correct actual CCPC master-data mappings or deployed posting behavior.

**Safety:** This is only a recorded owner business decision. No application transactional changes, Accounting Dimension configuration, account or Cost Center master-data edits, permissions, migrations, DEVELOPMENT or PRODUCTION actions were made. **POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.**
