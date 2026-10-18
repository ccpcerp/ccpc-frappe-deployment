# CCPC B/C G1–G3 owner-approved principles — pure policy GitHub draft checkpoint

**Date:** 2026-10-18, Asia/Manila. **State:** GitHub-only code/design review; **NO active mapping approvals, stock posting or deployable Finance feature**. `POSTING_NO_GO` / `PRODUCTION NO-GO` / `DEV_TARGET_ORIGIN_UNKNOWN_STOP`.

## Authoritative decision and branch

- The owner explicitly approved G1 independent Accounting maker–checker, G2 immutable auditable revision lifecycle, G3 positive exact eligible C revision selection for multiple centers **as design principles for the next GitHub-only review**. See [decision and boundaries](WITHDRAWAL-B-C-G1-G3-DESIGN-OWNER-APPROVAL-2026-10-18.md), GitHub doc commit `c4c6239fffaf0e8a4024e5ade824d32f50b1902e`.
- Created a **separate app review branch**, `review/bc-approval-selector-policy-2026-10-18`, from the exact prior [draft PR #17](https://github.com/ccpcerp/ccpcerp/pull/17) commit `374b7155e570ff618fff482510fe65a52fd148d0`.
- Opened [**app draft PR #18**](https://github.com/ccpcerp/ccpcerp/pull/18) targeting PR #17's branch, **not main**; creation-verified head `f08765c4d6c81665f216081d2dc16a6796c289fb`. PRs #16 and #17 remain separately unmerged/draft. Re-verify branch tip before future edits.

## Exact code delta

- `ccpcerp/ccpc_erp/bc_mapping_policy.py`, file/blob `d7c3cdf99c871c470c66cfd00f480900b6c8e6e4`:
  - `assert_independent_review` checks named maker/checker are non-identical and not Guest/Administrator, explicitly **does not validate real Accounting roles or Company authorization**;
  - `intervals_overlap` and `is_effective_after_approval` are pure timestamp-aware half-open-window arithmetic guards for future approved revision checks and non-retrospective evaluation; **not database locking, calendar effective-policy approval or SQL uniqueness**;
  - `select_center_revision` rejects absent, duplicate, malformed, forged or ambiguous candidates; if more than one candidate remains, requires a positive exact revision choice and forbids silent competition between Department-only and explicit-choice scopes. **Input candidates must already be signed/effective/Company+beneficiary verified under future server locks; this module cannot establish their approval.**
- `ccpcerp/ccpc_erp/test_bc_mapping_policy_static.py`, blob `f1c15df37c5dc6104995eb1c8530e3b8005ba16e`, provides **15 independently inventoried standard-library unittest methods** for positive/negative actor separation, UTC boundary/overlap, approval-time and explicit multi-Center selection cases. Read-back GitHub source verifies these two files are the **only changed files** in PR #18 (GitHub PR patch inspection).
- No new Frappe hooks, DocType fields, role assignments, approval transition, mapping records, Stock Entry/GL builder changes, DEVELOPMENT deployment or PRODUCTION actions.

## Verification and remaining test gate

- Read-back **verified exact GitHub source/blob hashes**, branch origin and draft PR head. Static inventory found **15 defined test methods**, not 15 test passes.
- No GitHub Actions workflow was successfully created for PR #18 and **NO executed CI, Python unit-test run, Frappe site run, MariaDB or GL test result is claimed for the new helper**. An attempted separate Actions file creation did not succeed; do not imply Actions is set up. Require reviewed tests/CI before adopting helper in any live issue or mapping activation.
- Prior PR #17 genuine [6/6 database schema tests](https://github.com/ccpcerp/ccpcerp/actions/runs/39107359756) and [3/3 static schema tests](https://github.com/ccpcerp/ccpcerp/actions/runs/39107359784) passed on **prior PR17 head**, not on PR18 helper. They do not validate G1–G3 workflows or GL.

## Unresolved Finance/release gates

- Accounting approval of exact named users/roles and Company scopes, maker-checker segregation implementation with actual authenticated user/permissions, exceptions and emergency controls.
- Approved cutoff/posting timestamp, effective interval/revocation record policy, scope-row locking, duplication and concurrent approval/issuance validation with genuine disposable Frappe v16/MariaDB tests.
- Actual G3 Slip-selection field, who chooses/approves it, any Section/line exception, distinct explicit-choice scopes, source locking and before-submit forged voucher rejection.
- Signed B2 Company/exact leaf Item Group→Expense Account and C1 Company/beneficiary Department→Cost Center rows in [blank B/C worksheet](WITHDRAWAL-ISSUE-B-C-MAPPING-APPROVAL-WORKSHEET-2026-10-18.md); none supplied or inferred.
- Review/merge of dependent drafts, independently verified DEVELOPMENT target/origin/dirty work/backups and explicit separate PRODUCTION approval. No automatic Codex reporter, personal notes, deployment, or posting.

**Next safe step:** Obtain reviewed static-unit execution for PR18 and exact Finance/Accounting approval identity/Company scope decisions; only then design secure server-side workflow/selection integration, separately test it with synthetic real Frappe/ERPNext/MariaDB stock/GL cases and obtain release permission.
