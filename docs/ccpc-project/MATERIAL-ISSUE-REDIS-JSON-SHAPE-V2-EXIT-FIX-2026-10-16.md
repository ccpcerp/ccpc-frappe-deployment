# CCPC ERPNext — v2 Redis JSON/URL shape diagnostic: exit-code fix

**2026-10-16 | GitHub-only source and offline testing. NOT STAGED; NOT RUN against DEVELOPMENT.**

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
