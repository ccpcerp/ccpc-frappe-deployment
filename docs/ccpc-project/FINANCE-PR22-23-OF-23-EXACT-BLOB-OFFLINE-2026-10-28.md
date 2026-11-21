# Finance PR22 — exact-blob 23/23 committed offline Python tests PASS

**Date:** 2026-10-28, Asia/Manila  
**Authorization:** Owner approved the exact committed 23-test *offline* run only. No new source-code modifications or execution of a hosted CircleCI, live Frappe, MariaDB, DEVELOPMENT, Integration2, or PRODUCTION operation.

## GitHub source identity

- Application [draft PR #22](https://github.com/ccpcerp/ccpcerp/pull/22), review branch `review/finance-http-concurrency-tests-2026-10-28`.
- All nine input files fetched through the connected GitHub tools pinned to full commit `175207c798fe63b49f22a940d0510f667b798c52`; branch and PR head independently confirmed identical, PR open/draft/unmerged.
- Direct network access for a normal full Git checkout was unavailable in the local offline execution runtime; the exact nine files required by these two test modules were reconstructed from GitHub file contents. **This is a complete byte-identical nine-file test fixture, not a full repository clone.** Every file's `git hash-object` matched GitHub's expected blob SHA, including `.circleci/config.yml`.

| Source file | Verified exact blob SHA |
| --- | --- |
| `.circleci/test_finance_probe_source_policy.py` | `6aae61bb988da9ed3648dcda33f9fc932525251d` |
| `.circleci/test_finance_setup_connection_behavior.py` | `47aed80d74cd9a626b9c4933276cd5aabd44b21b` |
| `ccpcerp/ccpc_erp/ci_finance_setup_connection.py` | `dac2dbc10ba18595e726ff4973f15fc843712a2c` |
| `.circleci/finance_http_session_probe.py` | `a50af9e9b36ea33e6719174b35fe271d10c14fb5` |
| `ccpcerp/ccpc_erp/ci_finance_company_lock_probe.py` | `9c890ac5245af7fa837e422d37d09d99593d2705` |
| `ccpcerp/ccpc_erp/ci_finance_business_race_probe.py` | `5555d0a64ed491f76ef68a96b192ba93e5300404` |
| `ccpcerp/ccpc_erp/ci_finance_race_fixture.py` | `b277213e3757359ef17aaf6b9ffc177808e0dcde` |
| `ccpcerp/ccpc_erp/ci_finance_master_bootstrap.py` | `92f40132dbfaebc7b202e86ce81a56241aeff00f` |
| `.circleci/config.yml` | `9aa8c676dfa7b22e7b7035d70a0b461af773908d` |

## Executed test evidence

**Interpreter:** Python 3.13.5.  
**Validation:** `python -m compileall -q ccpcerp .circleci` → **PASS** for the reconstructed source/test files.  
**Command run in the isolated local scratch directory:**

```sh
python -m unittest discover -s .circleci -p 'test_finance_*.py' -v
```

Actual result: **`Ran 23 tests in 0.010s` / `OK` — zero failures, zero errors**.

- **15/15**: Exact committed `.circleci/test_finance_setup_connection_behavior.py` (mock-only Frappe/DB connection, caller restoration/flags, read-only guard, failure paths).
- **8/8**: Exact committed `.circleci/test_finance_probe_source_policy.py` (AST parsing, HTTP/CSRF probe static gates, SQL lock/race policy, gated fixture/master bootstrap, setup isolation source policy, active CircleCI config absence/default-false).
- The policy source test checks *literal source contents*, not live services, and does not establish the correctness of all dynamic behavior.
- This result **supersedes** the earlier report's historical limitation that the newly committed 15+8 test modules were not yet executed. Earlier 11/11 independent smoke and pre-fix 13/13 runs were separate earlier evidence; do not add their counts to 23.

## Safety classification and outstanding gates

- Execution used pure-stdlib source inspection and fake module/DB objects only. **No import of actual Frappe, login, web request, DB connection, CircleCI pipeline, shell execution of probe entry points, fixture commit, external account access, or financial posting.**
- The local source bundle was verified by per-file Git blob hash, but **was not a complete Git checkout** and does not demonstrate CircleCI parameter rendering or shell execution of YAML `command:` blocks. CircleCI's literal source contains `\\<<` syntax in a block command; shell behavior must be verified after CircleCI's own config interpolation rather than drawing conclusions from a raw shell excerpt.
- No actual ERPNext Company Standard CoA bootstrap was executed; no MariaDB indexes, pending transaction concurrency, Python Frappe thread-locals under real framework hooks, or HTTP cookie/CSRF boundaries were live-tested.
- **No autonomous CircleCI spend/cost cap or runtime authorization is implied by 23/23 offline PASS.** The previously discussed 90-minute/2500-credit budget was a proposal, not an enforced limit or owner authorization.
- **Finance G2 CI status remains NO-GO.** Draft PR22 remains unmerged. No persistent DEVELOPMENT/Integration2/PRODUCTION modification has been authorized or made.

## Next concrete engineering decision

Review a separately scoped, fail-closed **preflight-only** plan for G2 (exact review branch/SHA, CircleCI config render/shell syntax, disposable site, approved cost ceiling and controls, unchanged active job gates, privileged Company/CoA side effects, physical DB uniqueness, restoration/backup boundaries). Seek explicit owner approval before triggering any hosted pipeline or building synthetic test masters, and never treat an offline mock run as real database integration.
