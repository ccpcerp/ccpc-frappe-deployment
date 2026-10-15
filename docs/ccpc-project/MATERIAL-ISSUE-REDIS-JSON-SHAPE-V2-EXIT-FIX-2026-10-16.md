# CCPC ERPNext — v2 Redis JSON/URL shape diagnostic: exit-code fix

**2026-10-16 | GitHub-only source and offline testing. NOT STAGED; NOT RUN against DEVELOPMENT.**

## 2026-10-16 — Exact GitHub 33-case offline suite verified and corrected: 33/33 PASS

**This checkpoint supersedes the earlier, historical 33-case pending claim below.** The assistant fetched both exact GitHub review-branch artifacts through the connected GitHub tools, reconstructed their bytes in a **credential-free local test workspace**, and used `git hash-object` to establish that the initial source files matched the independently read GitHub blob SHAs:

- v2 read-only diagnostic: `scripts/development/operator/ccpc_material_issue_redis_json_shape_readonly_v2_20261016.sh`, blob **`da9cc87f6f240a6afa581d4b1a0c7d6d24e9b684`**, SHA256 **`bd306c3324ae1e9acbb583fe61a97b314f6074025c66abd8b5678b77ee307486`** — **unchanged**.
- Initially committed v2 regression suite: `tests/offline/test_material_issue_redis_json_shape_v2.py`, blob **`258141d6fe4681a531969b62de754887d800ee96`**, **33 authored tests**.

**First exact-source execution:** The original unmodified 33-case suite ran against exact v2 source bytes locally, yielding **30 PASS, 3 ERROR**. The three exceptions were in tests `test_29`, `test_30` and `test_31` before the fixture scenarios began: each referenced `pathlib.Path(path)` although the test imported only `from pathlib import Path`. These were **test-harness errors**, not v2 runtime format failures.

**Minimal test-only correction:** Replace exactly three `root = pathlib.Path(path)` statements with `root = Path(path)`. No modification to the v2 script, authorization gate, output labels, config paths, business logic or previous staged/consumed scripts. The full suite was rerun in the **local, non-server workspace**:

```text
Ran 33 tests in 0.178s

OK
```

The run included `bash -n` and unapproved-execution smoke tests that STOP **before any Docker call**, restricted import/output checks, Python subprocess validation of the complete `__main__` success and failure exit paths, unexpected-exception redaction, and synthetic local JSON/config file fixtures. No actual Redis/SQL/network connections, Frappe initialization, host site data, DEVELOPMENT or PRODUCTION container execution occurred.

**GitHub verification:** The minimal test-only fix was committed as **`c903ea48810bdd02347280dfb6c62af355dad44a`**, with Git blob **`ff2b31ef23594b1038d3581875c8174f9db7d8b4`**, matching the independently executed corrected local test file **byte for byte**. Corrected test SHA256 **`ba0f7d92cd5466502f599531409f3c28def25022060a2e2945d90437e4a57fca`**. The earlier **26/26** local suite was distinct; the newly supported claim is **33/33 for the corrected exact GitHub suite**, not for the original broken test blob.

**Scope limitation and next gate:** This confirms only credential-free offline testing of the **v2 diagnostic source**, not Redis endpoint separation, physical service/worker/pubsub isolation or transaction integrity. The v2 source remains review-only and has **NOT** been staged or run on Ubuntu. **Staging the new filename requires separate explicit owner approval**, and subsequent one-shot read-only DEVELOPMENT execution requires another separate approval. The 2026-10-15 staged diagnostic's authorization is consumed; do not rerun or replace it. The original Redis endpoint-overlap preflight STOP remains unclassified. Material Issue Stock Entry/SLE/GL persistent posting **NO-GO**; PRODUCTION excluded.

## Authorization and why this is a new file

The owner explicitly approved **GitHub-only correction and offline testing** following the 2026-10-16 observed false trailing STOP in the prior one-shot redacted JSON/format diagnostic. The old staged and executed file `scripts/development/operator/ccpc_material_issue_redis_json_shape_readonly_candidate_20261015.sh`, blob `fc5617117806b8cd19586ae3c7bf530dab21d632`, SHA256 `b88dadc10cac64c5b6f48a695fbf506b046613cbe4db192da440227934b212b0`, is **consumed, preserved, and must not be rerun or overwritten**. The original separate Redis endpoint-overlap preflight is also consumed and its earlier STOP remains unclassified.

This v2 candidate uses a **different GitHub file path** and **new authorization gate**. The approval here authorizes GitHub artifacts and synthetic offline tests only, NOT Ubuntu delivery/staging, Docker inspection or exec, site JSON access, Redis/SQL connections, ERPNext writes or PRODUCTION access.

## Exact GitHub artifacts and safe changes

Repository `ccpcerp/ccpc-frappe-deployment`, review branch `review/material-issue-first-commit-preparation-2026-10-15`:

- [New v2 diagnostic](../../scripts/development/operator/ccpc_material_issue_redis_json_shape_readonly_v2_20261016.sh), create commit **`6f391de2226956514590998b88df1e71dd5a72dd`**, Git blob **`da9cc87f6f240a6afa581d4b1a0c7d6d24e9b684`**, exact file SHA256 **`bd306c3324ae1e9acbb583fe61a97b314f6074025c66abd8b5678b77ee307486`**.
- [New v2 GitHub regression suite](../../tests/offline/test_material_issue_redis_json_shape_v2.py), create commit **`dcf3440f21d43cc4e08e117decda7af2364cc84f`**, Git blob **`258141d6fe4681a531969b62de754887d800ee96`**. It contains **33 authored test cases**, adapted from the prior 25 checks plus eight targeted process/exit regressions. **Important testing distinction:** this new combined 33-case exact GitHub test file was *not independently executed as a suite* during this turn. Do not report 33/33 PASS.

**The correction:** The old code used `try: sys.exit(main())` / `except BaseException`, which caught `SystemExit(0)` and emitted a false failure after success. The replacement uses:

```python
if __name__ == '__main__':
    try:
        result = main()
    except Exception:
        print('CONFIG SHAPE: STOP; POSTING: NO-GO')
        result = 1
    sys.exit(result)
```

Thus normal success returns `0`; explicit `main()` failure returns `1`; unexpected exceptions of type `Exception` are redacted and return `1`. `SystemExit` and `KeyboardInterrupt` deliberately are not intercepted by `Exception`. No retry, write, production touch or endpoint comparison is added.

**New one-shot script gate:** `CCPC_REDIS_SHAPE_V2_READONLY_APPROVED=ccpc-redis-json-shape-v2-one-shot`. The original gate `CCPC_REDIS_SHAPE_READONLY_APPROVED` cannot arm v2. The still-earlier boundary preflight uses a different gate and script path. The v2 shell separately confirms the single named running DEVELOPMENT Frappe Compose container before `docker exec -i --user frappe`; the only Python command has `-I -B -S` and `PYTHONDONTWRITEBYTECODE=1`. No Docker or site action was run as part of this source development.

## Actual local offline test result — 26/26 PASS

A **distinct 26-test local synthetic regression suite** was executed on the exact v2 script bytes that GitHub readback independently verified (Git blob `da9cc87f6f240a6afa581d4b1a0c7d6d24e9b684`). Local Python command:

```bash
PYTHONDONTWRITEBYTECODE=1 python -W error -m unittest discover \
  -s /mnt/data/ccpc_redis_shape_v2_review/tests/offline \
  -p test_material_issue_redis_json_shape_v2.py -q
```

**Result: `Ran 26 tests ... OK`** (second confirmation run 2026-10-16). Bash `bash -n` and embedded Python AST parse also **PASS**. Locally tested standalone script SHA256 is **`bd306c3324ae1e9acbb583fe61a97b314f6074025c66abd8b5678b77ee307486`**; its `git hash-object` is exactly the GitHub blob. The **26-test local suite is not byte-identical** to the 33-case GitHub regression suite: the local suite uses more extensive simulated entrypoint/synthetic-fixture variants and its blob `f134d2255ef3322c7e49a7f0d87fee2ff1a9ff22`, SHA256 `7212ccf634caa43b3195d0b0255b8d66476f983474ebc2aafe5589ab41635fc8`, is not itself the GitHub test file.

The 26 executed tests cover (a) shell syntax and original-approval refusal before any Docker invocation, (b) distinct v2 flag, exact DEVELOPMENT identity and module allowlisting, (c) **actual Python subprocess execution** of the full `__main__` successful return `0`, failure return `1`, and unexpected exceptions with redaction, and (d) actual subprocess execution of the complete `main()` on locally synthesized three-site files for successful JSON/URL formats, malformed/nonmapping/UTF-8/oversized/symlink/FIFO cases, Sentinel STOP and invalid Redis URL formats. No real site, Redis, Docker, production, database or host credentials are used. **This is NOT a complete Docker/Bash runtime integration test; it does establish exit semantics of the exact embedded Python source under synthetic conditions.**

The GitHub regression suite's 33 authored cases must be run from their exact committed bytes in a credential-free review workspace before citing a **33/33** result or clearing any subsequent staging gate. More tests or changes may then be required based on outcomes. The earlier 25/25 claim applied to the consumed 2026-10-15 source and omitted the subprocess entrypoint path.

## Scope limits and future approval gates

The format candidate reads three fixed DEVELOPMENT JSON paths, bounded at 65,536 bytes each with readonly/nonblocking/nofollow checks, and only `FRAPPE_REDIS_QUEUE`/`FRAPPE_REDIS_CACHE` for the temporary exec process. It models the pinned Frappe config precedence (common -> site -> environment last) but does not reproduce dynamic `extra_config` hooks or running worker environments. It prints fixed safe stage labels only; no credentials, URLs, endpoints or JSON values. Even `FORMAT_OK` neither proves *actual Redis endpoint overlap absence*, physical Redis isolation, worker/Socket.IO/pubsub isolation nor a recoverable stock/GL transaction.

**New staging needs its own explicit approval** after the exact 33-case committed suite is verified, pinned branch HEAD and SHA256 are checked, and the private GitHub-to-Ubuntu procedure is reviewed. A subsequent **separate one-shot read-only execution approval** would be required even if staging succeeds. Never reuse the previously staged filename or approval flags; no automatic retries, app checkout changes, SQL writes, service restarts or PRODUCTION changes. **Persistent first Material Issue Stock Entry/SLE/GL COMMIT: NO-GO.**
