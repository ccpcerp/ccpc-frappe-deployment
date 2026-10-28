# Finance G2 Stage A — source-only baseline CI patch evidence and remaining gates

**Date:** 2026-10-28 (Asia/Manila)  
**Authorization:** Owner approved only the Finance Stage A source-only CI safety patch and offline tests. Not any CircleCI pipeline/manual hold, actual database fixture, DEVELOPMENT/Integration2/PRODUCTION, application merge, hosted spending or paid automation.

## GitHub branch and draft PR

- Source Finance feature branch `feature/finance-mapping-lifecycle-2026-10-28` was verified at `d154886ab45c51878a87a4ecf42e45602d8d9ccb` (Finance PR21 remains open/draft/unmerged).
- Created `review/finance-g2-baseline-timebox-2026-10-28` **from exactly that SHA** and opened [app DRAFT PR23](https://github.com/ccpcerp/ccpcerp/pull/23), **OPEN/DRAFT/UNMERGED**. Verified PR HEAD `c8607e10bf60bfd03749e165146745b48d6fa1d1` as of this report. Exactly **five commits ahead, zero behind** its feature base and **five changed paths**:
  1. `.circleci/config.yml` (Finance section only).
  2. `.circleci/finance_baseline_deadline.py` (new, pure Python stdlib).
  3. `.circleci/finance_baseline_stage.sh` (new, fixed Finance baseline commands).
  4. `.circleci/test_finance_baseline_deadline.py` (new, 10 offline mock/process tests).
  5. `.circleci/test_finance_ci_config_static.py` (existing static tests extended from 4 to 7).
- Existing Finance PR22 review branch remains independently draft/unmerged at `175207c798fe63b49f22a940d0510f667b798c52`, with prior 23/23 offline PASS, **not part of this Stage A patch**. Neither Finance feature branch nor PR22 was modified.

## Implemented in draft PR23

- Original `.circleci/config.yml` had an unconditional `starter-validation` workflow and Finance `run_finance_lifecycle=false` plus manual hold, feature-only branch filters, externally administered approved SHA, pinned Frappe/ERPNext commits. These remain unchanged. The *pre-Finance* legacy CI section and *post-Finance* workflows are byte-identical with the original baseline source. No legacy Withdrawal/intercompany job was reconfigured.
- Finance initial CI run step still checks organization, project, job, **feature branch only**, site, pipeline/workflow/build IDs, checkout commit and `CCPC_FINANCE_APPROVED_SHA`, and calls the existing Python disposable-site guard. Immediately after passing this gate, it **initializes an exclusive, persistent deadline file** and runs subsequent offline tests/compile within that budget.
- Finance setup now uses exactly three enumerated shell stages: `services`, `install`, and `tests`. These reproduce the original Finance baseline sidecar checks, pinned Frappe/ERPNext bench installation and **the original eight-test module** `ccpcerp.ccpc_erp.test_finance_lifecycle_disposable_integration`. They **do not call** PR22 HTTP/CSRF/race probes or persistent master/fixture builders. Every stage re-checks feature branch, exact checkout/approved SHA, job/site and disposable Python guard.
- `finance_baseline_deadline.py` adds **`MAX_SECONDS = 5400`** (a provisional **90-minute job-local safety ceiling**, **not** an approved runtime/credit allotment). It refuses missing/corrupt/expired/future-inflated deadline state, disallows silently restarting the countdown, and launches each stage as a child process group with cumulative `subprocess.Popen(...start_new_session=True)`, `wait(timeout=remaining)`, `SIGTERM`, then `SIGKILL` grace if required. It preserves child nonzero exits.
- The timer begins only **after identity verification**, and does **not** bound CircleCI container startup, checkout, unconditional starter-validation, CircleCI scheduling/cancellation latency or any independently detached grandchildren. It **cannot enforce a 2,500-credit or any global monetary spending cap**. It is neither CircleCI cost authorization nor an external operator cancellation substitute. The new code still has no guarantee against unrelated external side effects from Frappe hooks or test-master fixture creation.

## Actually executed offline

- Python 3.13.5: new `finance_baseline_deadline.py` and **exact committed 10-method** `test_finance_baseline_deadline.py` locally reconstructed, both `git hash-object` hashes matched current GitHub files:
  - deadline helper `5d4707f24bf9e33ac51df51d694f1e873a59aa17`
  - deadline tests `93d2150ffaeb8d175ba88feb12253624a0f12ec7`
- `python -m compileall -q .circleci`: **PASS** on these locally reconstructed source/test files.
- `python -m unittest discover -s .circleci -p 'test_finance_baseline_deadline.py' -v`: **10/10 PASS, zero failed/errors, ~1.9 seconds**. Tests include exclusive start and prevention of resetting clock, missing/corrupt/expired/too-far-future files, harmless child success, nonzero propagation, child timeout with a local Python sleep, empty command and invalid dispatch. No Frappe import, network or live service was used.
- Exact GitHub Stage A shell `finance_baseline_stage.sh` reproduced locally with blob SHA `1a17067fd57af7d65d11610726016e46794fd323`: `bash -n` **PASS**; executing with deliberately **wrong** `CIRCLE_BRANCH` returned exit **1** before the stage body, with no setup performed.
- A further **25/25** direct JavaScript read-only source structural assertions against the GitHub feature base and PR23 branch **PASS**: byte-identical legacy config/workflows, default-false, manual hold, original feature/SHA gate, timer start position, three individually timed stage invocations, unchanged pinned installation and eight baseline test-method declarations, no PR22 probe activation.
- **Not yet executed:** the updated *exact* existing `.circleci/test_finance_ci_config_static.py` seven-test Python module (its new tests are committed, not currently certified passing), all other original Finance guard offline tests in one complete cloned checkout, actual YAML parsed from PR23 in a local Python environment, provider `circleci config validate/process` compilation and compiled-shell inspection, hosted starter/Finance jobs, Frappe/MariaDB or HTTP. Do not claim 7/7 static Python PASS or production readiness. The stage shell was parsed directly, which does not prove CircleCI YAML interpolation will produce the intended shell on its hosted platform.
- A GitHub push/PR may trigger separately configured automatic **starter-validation** work. No CircleCI pipeline was deliberately triggered or approved through ChatGPT; actual provider-side automatic workflows have not been audited.

## Blocking issues / next stage

1. **Review and validate draft PR23** without merging. Reconstruct/checkout full exact source and run its updated seven-method Finance config tests plus the original six Finance identity guard tests and all appropriate source-only tests.
2. Run a safe **CircleCI CLI configuration validation and compilation** for both default/opt-in Finance parameter values, without creating a pipeline. Verify compiled job graph, manual hold, post-interpolation heredoc and `bash -n`. This cannot be substituted by the 25 source checks.
3. Review mandatory original baseline `self.load_test_records("Stock Entry")` and any real Company/CoA, DB uniqueness, email/hooks and rollback side effects on a genuinely disposable environment.
4. Confirm live CircleCI organization/project/plan, credits, starter-job cost, operator cancellation mechanism, sidecar billing/availability, fixed SHA authorization, maximum permitted runtime and **independently authorized total spend**. Current **5400 seconds is a proposed safety ceiling only**, not a hard ceiling for all CircleCI charges.
5. Only after all gates, obtain a *new explicit user approval* for merge/pipeline/manual hold and any fixture/test-master writes. No equivalent authorization is implied by this commit.

**Disposition:** Source-only Stage A CI patch landed on a **new GitHub review branch and draft PR23**, not merged or run; Finance G2 **NO-GO**.
