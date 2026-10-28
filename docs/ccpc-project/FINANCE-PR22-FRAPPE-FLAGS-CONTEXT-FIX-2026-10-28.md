# CCPC Finance PR22 — Frappe fixture caller-context isolation follow-up

**Date:** 2026-10-28 (Asia/Manila)  
**Authorization:** Owner approved a narrowly scoped source-only fix and mock regression tests on Finance PR22 following [pinned Company/CoA/context review](FINANCE-PR22-PINNED-COMPANY-COA-CONTEXT-REVIEW-2026-10-28.md). Not a CircleCI, database, Frappe HTTP, DEVELOPMENT, Integration2, PRODUCTION, PR merge, or financial fixture authorization.

## Verified application state

- App [PR #22](https://github.com/ccpcerp/ccpcerp/pull/22): `review/finance-http-concurrency-tests-2026-10-28` **OPEN/DRAFT/UNMERGED**, source HEAD **`175207c798fe63b49f22a940d0510f667b798c52`**; base remains `feature/finance-mapping-lifecycle-2026-10-28`.
- GitHub compare from pre-fix HEAD `54dd6ee3d021bfd2b0f13ce81459d720a7850e00`: **7 commits ahead, 0 behind; exactly three changed paths**, all originally present in PR22:
  - `ccpcerp/ccpc_erp/ci_finance_setup_connection.py`
  - `.circleci/test_finance_setup_connection_behavior.py`
  - `.circleci/test_finance_probe_source_policy.py`
- Current helper Git blob SHA **`dac2dbc10ba18595e726ff4973f15fc843712a2c`**. CircleCI YAML unchanged; probes still not automatically wired.

## Implemented and source-reviewed

1. The isolated fixture DB helper snapshots `frappe.local.flags`, then creates an independent *Frappe-init-shaped* flags dictionary with clean nested `currently_saving` list rather than inheriting the caller's potentially permissive flags, such as `ignore_root_company_validation`. Pinned Frappe v16 source declares `frappe.flags` a `LocalProxy` to `local.flags`; this allows the worker to use a temporary flags bag while preserving the original object identity for the caller.
2. The helper explicitly refuses a caller with `flags.read_only` instead of bypassing read-only state by introducing writable fixture flags. This check runs before creating a child connection.
3. On exit, the helper still rolls back and closes **only the independent child DB** and restores the original database pointer/user. The nested `finally` additionally restores the exact original flags object even if rollback, close, or user restoration raises. The same-connection reuse path continues to avoid rolling back/closing the caller.
4. The committed mock test module expands from five to **15 test methods**, covering fresh flag isolation, no nested `currently_saving` contamination, Company-controller flag changes, body failure, wrong database, connect failure, reused caller connection, rollback/close failure, failed user restoration, `frappe.in_test` and read-only rejection, in addition to the original DB semantics. The source-policy module still has **eight test methods**, now asserting the new flag-context/read-only lines. **These numbers describe committed test declarations, not tests executed.**

## Offline validation actually executed

- The helper was reconstructed into an isolated local scratch workspace `/mnt/data/pr22_flag_offline`, with canonical Git `hash-object` **`dac2dbc10ba18595e726ff4973f15fc843712a2c`**, matching GitHub's current file blob SHA. This is an **exact helper-file snapshot**, not a private repository checkout.
- **Python 3.13.5** `compileall -q`: **PASS** for the reconstructed helper and independent smoke test module.
- **11/11 separate pure-stdlib mocked smoke checks PASS**, 0 failures/errors, covering success + child commit, no parent mutation, flag isolation, exception paths, wrong DB, same-connection reuse, failed connect, child rollback failure, child close failure, set_user restoration failure, `in_test`, read-only rejection, and absence of an implicit commit in helper source.
- These smoke tests are *independently authored* and **are not the committed `.circleci/test_finance_setup_connection_behavior.py` or `.circleci/test_finance_probe_source_policy.py`**. The newly committed **15 + 8** tests have not been executed here, nor was full PR22 reconstructed; **do not claim 23/23 PASS**. The older **13/13 PASS** was on pre-fix SHA `54dd6ee3`, and must not be attributed to the current SHA.

## Remaining limitations / release decision

- The fresh flag bag isolates Frappe `local.flags` changes; it does **not** isolate every other Frappe global/thread-local object, cache, hook, email, job, filesystem change, or external action. If `frappe.set_user` itself fails, the code still restores DB/flag pointers but cannot guarantee the user identity was successfully restored. It will propagate the exception.
- No real ERPNext Company controller invocation, transactional hook behavior, physical MariaDB unique-index audit, two-connection Finance approval/retirement race, HTTP/CSRF test, or hosted CircleCI execution occurred.
- Frappe CI `run_finance_lifecycle` remains default-false, existing manual holds remain. **Finance G2 remains NO-GO**; do not merge or execute builder or races based on these isolated smoke results.
- **Next action:** Run **all committed offline Python policy + mocked-behavior tests** from a correctly pinned exact PR22 Git checkout/snapshot (without Frappe, secrets or network), then review resulting evidence. Before any G2 execution, separately review isolated runtime/secret/network/cost controls, pristine test DB, Company/CoA generation, actual indexes and exact authorizations. No DEVELOPMENT/Integration2 or PRODUCTION action follows automatically.

**App branch/commit:** `review/finance-http-concurrency-tests-2026-10-28` @ `175207c798fe63b49f22a940d0510f667b798c52`.  
**Evidence class:** Source review + exact-helper offline smoke, not end-to-end integration.
