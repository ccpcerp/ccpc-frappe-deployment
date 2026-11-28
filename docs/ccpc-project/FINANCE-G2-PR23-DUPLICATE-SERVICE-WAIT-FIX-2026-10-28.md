# Finance G2 PR23 — offline source audit found and fixed duplicate unbounded service wait

**Date:** 2026-10-28 (Asia/Manila)  
**Authorization:** Owner approved further Stage A offline validation, fail-closed correction review and documentation. **No hosted CI/pipeline, manual hold, merge, Frappe/MariaDB, fixture commit, DEVELOPMENT/Integration2/PRODUCTION, or CircleCI spending was authorized.**

## GitHub state and concrete finding

- [App draft PR23](https://github.com/ccpcerp/ccpcerp/pull/23) on `review/finance-g2-baseline-timebox-2026-10-28`, base `feature/finance-mapping-lifecycle-2026-10-28` @ `d154886ab45c51878a87a4ecf42e45602d8d9ccb`.
- Reviewed PR23 prior HEAD `c8607e10bf60bfd03749e165146745b48d6fa1d1`, config blob `7610a5963911adecec696d38b864cbcfa7c77780`. Source inspection found **TWO** consecutive Finance steps both called `Confirm disposable database and Redis sidecars`:
  - first original inline `for port in 3306 13000 11000` wait with its own `sleep 2` / 60 tries, **outside** the new cumulative deadline, and
  - second step invoking `finance_baseline_deadline.py run bash .circleci/finance_baseline_stage.sh services`, **inside** the deadline.
- This duplicated sidecar wait and allowed the first wait to consume job minutes outside the claimed post-identity cumulative timebox. The earlier 38/38 read-only source checks lacked an assertion for duplicate unwrapped service steps; **38/38 PASS was not a comprehensive safety pass**. Exact compiler and actual runtime still unverified.

## Remediation committed and verified

1. **App commit `5005c869282cc8564e829cba6378cf8daa065ad6`**: removed only the first original unwrapped sidecar run block from `.circleci/config.yml` (531 bytes). New config Git blob `933d1945afb2eea34a65f9cb98bd98397d5dcd19`.
2. **App commit `cf4b1ef5ee1bc4d29d4871787e2a0381ec1ef779`**, now PR23 HEAD: augmented `.circleci/test_finance_ci_config_static.py` with `test_finance_has_no_unwrapped_duplicate_sidecar_wait`. Updated static test Git blob `e62b827fb97d58807c6d96aae9e6180c4a4f2300`. It rejects `count(name: Confirm...) != 1`, forbids the raw port loop in Finance YAML, requires exactly one timeboxed `services` wrapper and confirms the fixed port loop still exists in the dedicated stage script.
3. **Independently verified by GitHub blob before/after comparison:** original Finance section had `serviceCount=2`, `rawWait=true`, `wrappedCount=1`; updated Finance section has `serviceCount=1`, `rawWait=false`, `wrappedCount=1`. The common prefix/suffix diff showed exactly the intended 531-byte redundant block removed. All non-Finance YAML preceding the Finance job and all `workflows:` YAML after it were **byte-identical**. Finance remains default disabled, retains manual hold and exact feature-branch approved-SHA guard.
4. [PR23](https://github.com/ccpcerp/ccpcerp/pull/23) remains **OPEN/DRAFT/UNMERGED** with two additional commits versus the earlier checkpoint, **7 commits ahead / 0 behind** the unchanged feature base, and the same five Finance-only changed paths.

## Test evidence and explicit unresolved gates

- Previously run at older PR23 head: **10/10 exact new Python deadline tests PASS**; *not rerun at updated HEAD* (those two test/helper files are unchanged).
- This continuation: exact source negative-control comparison and **12/12 focused read-only structural assertions PASS** on GitHub source after fix. These JS assertions are **not a substitute** for committed Python test execution or provider config compilation.
- There are now **8** declared Finance static YAML/Python tests + **6** original guard tests + **10** deadline tests = **24 targeted offline Python test methods**. **All 24 must still be run together from an exact current commit checkout**; do not re-report the prior 23-target plan as current.
- Local runtime has Python 3.13.5 and PyYAML 6.0.3, but `circleci` CLI is absent and direct shell-to-GitHub DNS resolution fails. Connected GitHub tools can read source blobs but cannot themselves run the Python test files or provider config compilation. No real CircleCI `config validate` / `config process` was executed; never label a static YAML parse as provider compilation.
- Current PR23 branch, while reviewable in GitHub, **cannot run** existing Finance hosted G2 job under its strict feature-only workflow/guard, and no branch spoofing or merge was attempted.
- The 5400-second timer remains a **provisional job-local protection**, not an owner-approved total runtime, guaranteed 2,500-credit spending limit, nor a timeout on container boot, checkout, unconditional starter job or external sidecars.

## Next safe gate

Retrieve an exact GitHub PR23 checkout in a trusted environment that has official CircleCI CLI installed. Run `python -m compileall` and the **24 exact committed Python tests**; validate `.circleci/config.yml` twice (Finance default `false` and opt-in `true`) using `circleci config validate` and `circleci config process`; verify the compiled workflow/manual hold and `bash -n` compiled run scripts, and ensure the unwrapped duplicate cannot reappear. **Do not start a CircleCI pipeline**. After those offline results, independently review actual budget, credentials, ephemeral fixture and DB disposal before any separate G2 hosted authorization.

**Disposition: source-level duplicate-wait fix verified; full 24-test Python suite and official CircleCI compiler are still PENDING; Finance G2 NO-GO.**
