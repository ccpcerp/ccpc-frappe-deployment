# Finance G2 Stage A PR23 — continued offline validation and compiler blocker

**Date:** 2026-10-28 (Asia/Manila)  
**Owner authorization:** Continue **offline-only** validation of draft Finance G2 Stage A PR23. No CircleCI pipeline, approval hold, provider spending, login, DB or synthetic fixture operation, DEVELOPMENT/Integration2/PRODUCTION, PR merge or further source-code modification was authorized.

## Latest verified GitHub state

- App [draft PR23](https://github.com/ccpcerp/ccpcerp/pull/23), `review/finance-g2-baseline-timebox-2026-10-28` @ **`c8607e10bf60bfd03749e165146745b48d6fa1d1`**, remains **OPEN/DRAFT/UNMERGED**. Compared with Finance feature `d154886ab45c51878a87a4ecf42e45602d8d9ccb`, **5 commits ahead, 0 behind, exactly 5 modified/added Finance CI files**.
- Finance PR21 @ `d154886ab45c51878a87a4ecf42e45602d8d9ccb` and PR22 @ `175207c798fe63b49f22a940d0510f667b798c52` remain OPEN/DRAFT/UNMERGED. No application branch changed this turn.
- All **nine** PR23 test/policy dependencies were fetched at the *exact PR23 head* via connected GitHub tools; recorded content blob SHAs:
  - `.circleci/config.yml`: `7610a5963911adecec696d38b864cbcfa7c77780`
  - `.circleci/test_finance_ci_config_static.py`: `2abc2c59e6d6a5856df592bea634f16da3d57cbc`
  - `.circleci/finance_baseline_stage.sh`: `1a17067fd57af7d65d11610726016e46794fd323`
  - `.circleci/finance_baseline_deadline.py`: `5d4707f24bf9e33ac51df51d694f1e873a59aa17`
  - `.circleci/test_finance_baseline_deadline.py`: `93d2150ffaeb8d175ba88feb12253624a0f12ec7`
  - `ccpcerp/ccpc_erp/test_finance_lifecycle_disposable_integration.py`: `4aeaa7c5b841637fe3c66a0e507f6b0f5db1448b`
  - `.circleci/test_finance_lifecycle_ci_guard.py`: `8913fe6d914e9f5367640c664b2c8bc5a4e69ae4`
  - `ccpcerp/ccpc_erp/ci_finance_lifecycle_site_guard.py`: `87e1f98308d6f2094ab6a45458dcd9cb6e6e5513`
  - `ccpcerp/ccpc_erp/ci_disposable_site_guard.py`: `e20c7822186729bd793e3934a9af46f57c38742b`.

## Validation actually completed this continuation

- **38/38 additional JavaScript source-boundary assertions PASS**, performed directly on connected GitHub file content at exact PR23 commit. This is **not running the Python `unittest` modules**. The checks covered: Finance and legacy default-false parameters, manual approval dependency, both feature-only workflow filters, externally administered SHA and checkout equality, fixed job/site, pinned Frappe/ERPNext SHA, all three stage wrappers, child process-group timeout/kill safeguards, fixed eight-test module and eight method names, original Stock Entry fixture dependency, six guard-test and seven config-test declarations, no PR22 HTTP/race/fixture code activated, and no legacy posting tests in Finance job.
- Local execution runtime: **Python 3.13.5** and **PyYAML 6.0.3** are available, but **no `circleci` or `circleci-v0` binary is installed**. Read-only `git ls-remote https://github.com/ccpcerp/ccpcerp.git HEAD` returned DNS resolution failure for GitHub. Thus an exact full local checkout and actual CircleCI `config validate` or `config process` could **not** be completed here. Search of available connected plugins found no CircleCI plugin.
- **Do not claim** `7/7` current static Python tests or `6/6` identity guard Python tests: those exact modules were inspected but **not executed** in this turn. The previous [Stage A source-only patch review](FINANCE-G2-STAGE-A-SOURCE-ONLY-PATCH-REVIEW-2026-10-28.md) independently reported **10/10 exact deadline Python tests PASS**, shell `bash -n` PASS and wrong-branch refusal at the same PR23 SHA; that result remains historical, not a new execution in this turn.
- No CircleCI account, remote configuration editor, provider CLI compiler, hosted job, live Python/Frappe/MariaDB, HTTP/CSRF or networked source checkout was executed.

## Exact remaining offline gate: CircleCI compiler plus full committed test suite

CircleCI's current official CLI reference confirms the **local configuration** subcommands: <https://cli.circleci.com/reference/>. Under a trusted, source-only machine with pinned GitHub checkout and the official CLI installed, the following **validation-only** commands do **not** create or run a CircleCI pipeline:

```sh
git rev-parse HEAD                       # must be the owner-reviewed PR23 SHA
python -m compileall -q .circleci
python -m unittest discover -s .circleci -p 'test_finance_ci_config_static.py' -v
python -m unittest discover -s .circleci -p 'test_finance_lifecycle_ci_guard.py' -v
python -m unittest discover -s .circleci -p 'test_finance_baseline_deadline.py' -v
circleci config validate .circleci/config.yml
circleci config process .circleci/config.yml --pipeline-parameters 'run_finance_lifecycle: false' > /tmp/finance-compiled-default.yml
circleci config process .circleci/config.yml --pipeline-parameters 'run_finance_lifecycle: true' > /tmp/finance-compiled-optin.yml
```

Do not invoke `circleci run trigger`, `circleci pipeline run`, `circleci local execute`, approve a hosted hold, or configure credentials. Inspect the **compiled** workflow graphs: default Finance absent; opt-in Finance job present behind manual approval; starter-validation still present. Extract the compiled Finance `run.command` values and validate their actual heredoc rendering using `bash -n`; the source spelling of `\\<<` by itself is not compiled shell. CircleCI documentation states `config process` compiles with placeholder pipeline values, not a real branch/project: <https://support.circleci.com/en/articles/17680503-the-config-editor-fills-pipeline-values-with-placeholders>.

Do not treat CLI compilation alone as acceptance of: user-approved budget, enforced 2,500-credit cap, hosted Frappe/MariaDB, disposable site isolation, physical unique indexes, Company/CoA generation, rollback, side effects or the baseline's `load_test_records("Stock Entry")` data setup. The `5400` second deadline is a **job-local** protective ceiling after identity validation, **not** a maximum charge or full pipeline bound.

**Disposition: PR23 source checks expanded; exact Python suite and CircleCI compilation remain PENDING; G2 Finance CI stays NO-GO.** No source code, CircleCI account/project or environment was changed in this validation turn.
