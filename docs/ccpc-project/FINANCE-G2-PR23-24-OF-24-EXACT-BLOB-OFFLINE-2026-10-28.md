# Finance G2 PR23 — exact GitHub blob offline test milestone: 24/24 PASS

**Date:** 2026-10-28 (Asia/Manila)  
**Scope:** Owner explicitly approved continuing **offline-only** PR23 validation after the sidecar duplicate-wait fix. No Finance CircleCI pipeline, CircleCI approval hold, provider spend, Frappe/ERPNext/MariaDB runtime, synthetic test master/fixture commit, DEVELOPMENT/Integration2, PR merge or PRODUCTION action was authorized or performed.

## Verified GitHub checkpoint

- Custom app [draft PR23](https://github.com/ccpcerp/ccpcerp/pull/23), review branch `review/finance-g2-baseline-timebox-2026-10-28`, exact HEAD **`cf4b1ef5ee1bc4d29d4871787e2a0381ec1ef779`**.
- PR23 remains **OPEN/DRAFT/UNMERGED**; base is `feature/finance-mapping-lifecycle-2026-10-28`. The latest sidecar double-wait fix was commit `5005c869282cc8564e829cba6378cf8daa065ad6`, and the negative regression test commit `cf4b1ef5ee1bc4d29d4871787e2a0381ec1ef779`.
- GitHub source was retrieved through the connected GitHub connector at the exact PR23 head. Because the local environment cannot resolve `github.com` and cannot directly clone, nine file contents were reconstructed into a scratch directory, **not a complete repository clone**. Every local `git hash-object` exactly matched its independently fetched GitHub blob:

| Exact file | GitHub + local blob SHA |
| --- | --- |
| `.circleci/config.yml` | `933d1945afb2eea34a65f9cb98bd98397d5dcd19` |
| `.circleci/test_finance_ci_config_static.py` | `e62b827fb97d58807c6d96aae9e6180c4a4f2300` |
| `.circleci/finance_baseline_stage.sh` | `1a17067fd57af7d65d11610726016e46794fd323` |
| `.circleci/finance_baseline_deadline.py` | `5d4707f24bf9e33ac51df51d694f1e873a59aa17` |
| `.circleci/test_finance_baseline_deadline.py` | `93d2150ffaeb8d175ba88feb12253624a0f12ec7` |
| `.circleci/test_finance_lifecycle_ci_guard.py` | `8913fe6d914e9f5367640c664b2c8bc5a4e69ae4` |
| `ccpcerp/ccpc_erp/ci_finance_lifecycle_site_guard.py` | `87e1f98308d6f2094ab6a45458dcd9cb6e6e5513` |
| `ccpcerp/ccpc_erp/ci_disposable_site_guard.py` | `e20c7822186729bd793e3934a9af46f57c38742b` |
| `ccpcerp/ccpc_erp/test_finance_lifecycle_disposable_integration.py` | `4aeaa7c5b841637fe3c66a0e507f6b0f5db1448b` |

## Actual executed evidence — Python 3.13.5

Commands executed within the exact nine-file reconstruction `/mnt/data/pr23_exact_source`:

```bash
python -m compileall -q .circleci ccpcerp
python -m unittest discover -s .circleci -p 'test_finance_*.py' -v
bash -n .circleci/finance_baseline_stage.sh
```

**Results:** compileall **PASS**, `unittest` **24/24 PASS**, zero failures, zero errors in **2.286 seconds**. Exact 24 consisted of **10** deadline subprocess/negative-condition tests, **8** Finance CI configuration static/policy tests (including the new no-unwrapped-duplicate-service-wait regression), and **6** Finance site/branch/SHA identity negative tests. `bash -n` of the committed stage script **PASS**.

The complete `unittest -v` output was captured locally in `/mnt/data/pr23_exact_source/24-tests-2026-10-28.log`; this path is local scratch **not a GitHub blob** and does not imply a repository file. It contains all 24 test names and Python's reported duration.

**Local PyYAML 6.0.3 parse / structural checks: PASS.** The exact `.circleci/config.yml` parses as YAML version 2.1. Both integration pipeline parameters have default `false`. `starter-validation` is unconditional and still contributes cost when a pipeline is started. The manually held Finance workflow is guarded by `when: << pipeline.parameters.run_finance_lifecycle >>`; its approval gate is required by the Finance job; both are branch-filtered to `feature/finance-mapping-lifecycle-2026-10-28`.

**Four Finance run-command shell blocks** were extracted from the YAML and each passed `bash -n` **after a *locally simulated* heredoc escape replacement** `\\<<` to `<<`. This only checks the anticipated rendered shell; it is **NOT actual CircleCI CLI compilation** or proof of hosted command semantics. The current CircleCI CLI is unavailable in this local environment, and attempting a direct GitHub checkout fails DNS resolution. No CircleCI account was contacted, no CLI `config validate` or `config process` was executed, and no job graph was actually compiled by CircleCI.

## Interpretations and remaining readiness gates

1. **Milestone accomplished:** 24 committed exact-file offline tests really ran and passed at PR23 SHA `cf4b1ef`. This supersedes handoff statements saying 24 were merely declared/unexecuted. Earlier 10/10 and JavaScript 38/38 source checks are historical or parallel evidence, **not** counts to add to the current 24/24.
2. **Not a complete checkout or integration proof:** this is an exact **nine-file** reconstruction, not the entire application repository, Frappe import, ERPNext, DB, authenticated HTTP, worker process, CircleCI runner, or financial transaction proof. The eight ERPNext lifecycle methods were parsed as source and were not run; the test suite's `setUp()` would load `Stock Entry` fixtures in an authorized disposable DB.
3. **CircleCI compiler gate still PENDING:** On a trusted offline source checkout with official CircleCI CLI installed, execute the exact SHA's `circleci config validate .circleci/config.yml` and `circleci config process` for both `run_finance_lifecycle: false` and `true`. Inspect compiled workflow/manually-held job and run `bash -n` on *actual* compiled commands. **Do not trigger any pipeline.** Source YAML parsing, simulated heredoc replacement and `bash -n` are *partial* evidence only.
4. **Hard time/cost and fixture gates still PENDING:** `MAX_SECONDS=5400` (90min) is a provisional **post-identity job-local** ceiling; not a user-approved runtime/spend amount or enforceable total CircleCI credits. Unconditional starter-validation, checkout, sidecars, cancellation delays, retries and plan/auto-refill must be accounted for. The feature branch must contain exact approved code before its feature-only Finance CI job could run; PR23 is review-only and not merge-authorized. Synthetic Company/CoA, physical uniqueness, audit/version hooks, transaction side effects, cleanup and recovery are not validated in runtime.
5. **No-GO maintained** for Finance G2 hosted CI, merge, DEVELOPMENT/Integration2 and PRODUCTION. Separate and specific owner authorization remains necessary for each such step.

**Next step:** obtain official offline CircleCI compiler evidence for both parameter states; review the exact rendered syntax and remaining cost/disposable master gates before proposing any hosted CI GO/NO-GO.
