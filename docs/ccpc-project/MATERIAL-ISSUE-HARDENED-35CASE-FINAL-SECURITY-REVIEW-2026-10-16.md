# CCPC ERPNext — Final 35-case pinned-source offline harness security/usefulness review

**2026-10-16 | GitHub-only review | No code changes or test reruns | No DEVELOPMENT/PRODUCTION access or Stock Entry activity | POSTING_NO_GO**

## Authorization and verified refs

Owner approved the next **GitHub-only final review** of the hardened source-pinned 35-test suite and a **DEV-identity P0 checklist design**. This does not authorize host commands, staging, application changes, new tests, Docker access, source or site-config inspection in DEVELOPMENT, PRODUCTION reads, redis/SQL/Node/RQ contact, service restarts, or Material Issue writes/rollback-only trials.

Reviewed on:
- Deployment review branch `review/material-issue-first-commit-preparation-2026-10-15` at `49585323602d6b3378a9a4e41011d65ab614f243`.
- Deployment documentation branch `docs/ccpc-checkpoint-2026-10-10` at `a1b7e4f15ef2609e40ae4a6c632aa8c5f6e9b818`.
- CCPC custom app `ccpcerp/ccpcerp@feature/withdrawal-material-issue-safety` at `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6` (**unchanged**).
- [Hardened offline Python suite](../../tests/offline/test_material_issue_source_pinned_reachability_20261016.py), Git blob `38ceb7976d2e6f3faccf2012d27ca98edef6a84b`; [unchanged pinned 11-source fixture](../../tests/offline/fixtures/material_issue_reachability_source_pins_20261016.json), Git blob `7ca589594fb9ed818da75476ddbe68b471eef444`.
- [Prior hardening and test run record](MATERIAL-ISSUE-SOURCE-PINNED-OFFLINE-HARNESS-HARDENING-2026-10-16.md), Git blob `487527aafcf12851d77cdedd9e069e623b229745`.
- [Earlier final 22-case security review](MATERIAL-ISSUE-SOURCE-PINNED-22CASE-FINAL-SECURITY-REVIEW-2026-10-16.md), Git blob `594acef11c7be48d6d633026134cb5df75306a99`.

**Method:** GitHub-only static review of exact currently committed code and documented offline results. **No tests were rerun in this review.** The previously performed tests were **35/35 PASS** in both normal Python and `python -O`, in a disposable local test workspace; that is *historical observed test evidence*, not a current DEVELOPMENT or PRODUCTION result.

## Assessment matrix

| Item | GitHub source finding | Decision |
| --- | --- | --- |
| **Integrity checks under `-O`** | `snapshots()` uses explicit `FixtureIntegrityError`, bounded `read(MAX_FIXTURE_BYTES + 1)`, constant SHA-256 and Git-blob comparisons via `hmac.compare_digest`; trust checks no longer rely on `assert`. Local `-O` negative tests were previously run. | **PASS — scoped byte-integrity control**, not authenticated distribution/signature |
| **Whole-fixture verification before excerpt execution** | `function()` calls `snapshots()`, which validates entire manifest keyset, per-file pinned blob labels, parses/visits eleven ASTs, checks expected function names, disallows decorators, executable defaults/annotations, common dangerous constructs and dynamic attribute reads except the reviewed case. | **PASS — scoped source preflight**, not proof that arbitrary Python code is harmless |
| **Execution restriction** | Only six reviewed function keys are eligible for `compile`/`exec` with restricted builtins; five others, including `riv_worker_repost`, are AST-only. `function()` still accepts test-defined injected globals/mocks, and AST filtering is not a formal code-sandbox mechanism. | **PASS for current trusted fixture only; NO-GO as untrusted-source sandbox** |
| **Adversarial tests** | Previous negative tests include SHA tampering, optimized `-O` acceptance/rejection, digest-recomputed AST violations, oversize fixture, function execution allowlist, unsafe annotations/defaults. | **PASS within covered scenarios**; not an exhaustive exploit-resistance claim |
| **Synthetic callback accuracy** | `test_18` now uses two distinct synthetic callback sets for after-ROLLBACK and after-COMMIT, rather than invoking both on one mocked transaction. | **Improved interpretation**; not real Frappe DB transaction lifecycle |
| **Original pinned source relation** | Historical independent GitHub cross-check verified **11/11** fixture excerpts matched their claimed upstream file blobs and starting lines in immutable refs. The runtime `snapshots()` itself only proves local fixture bytes match constants and manifest labels; it does *not* refetch GitHub, attest running source, or check all transitive Frappe/ERPNext hooks. | **PASS as pinned GitHub fixture**, not installed-runtime proof |
| **SLE/GL financial integration** | AST asserts that Stock Entry `on_submit` references SLE/GL/repost decision in expected order, and that worker source contains commit call sites. It does not execute actual SLE/GL, SQL, stock queues, valuation or physical Redis. | **OUT OF SCOPE; POSTING_NO_GO** |
| **Deployment / source provenance** | A test blob and fixture digest are fixed within a committed Python file. An attacker/editor able to replace the test code and digest constants can change outcomes; GitHub/owner review remains the trust anchor. No live installed-app or hook state has been observed. | **NOT a cryptographic provenance attest to DEV** |

### Material remaining limitations

1. **The runner still uses `exec` against pinned ASTs and mock objects.** This is acceptable only as a controlled offline regression harness for the reviewed, byte-exact fixture. `SAFE_BUILTINS`, denylisted AST nodes and no-import assertions do not make Python bytecode/object graphs safe for untrusted fixtures or credential-bearing environments. Do not run this on the Ubuntu host or in DEV just to identify installed code.
2. **The fixture's source metadata and the SHA-256 root live alongside the test.** The checks detect accidental or malicious fixture changes *when the test program itself is trusted*; they do not independently attest GitHub vs current installed DEV state, and cannot secure a compromised runner.
3. **Tests do not establish complete app behavior.** Event ordering and conditional reposting are mock/AST observations; effective site records, custom hooks, installed Frappe/ERPNext commit, loaded long-lived processes and SQL transaction boundaries remain unverified. An after-commit flag can still differ from actual delivery behavior in an unknown Redis topology.
4. **Code security improvements are not financial posting approval.** CCPC's immediate `frappe.clear_cache(doctype="Withdrawal Slip")` remains a source-level pre-COMMIT external invalidation concern; configured Notifications, Webhooks and Server Scripts remain unenumerated; active Redis endpoints remain unproven; real duplicate/concurrent issue tests, SLE/GL and rollback tests were not performed.

### Security/usefulness decision

**PASS: suitable as bounded offline, pinned-source E1 regression evidence. DEFER: elevating it into a runtime readiness gate, shared-host host diagnostic, or authorization for Material Issue posting.** The harness is not being modified in this review and needs no additional immediate code churn for its present offline purpose. If changing its fixture/source pins later, re-review its allowed AST, mock context, assertions and provenance *before* executing altered input.

The useful next bottleneck is **P0 genuine DEVELOPMENT identity**, not further test count. The accompanying [P0 operator provenance checklist](MATERIAL-ISSUE-DEV-IDENTITY-P0-OPERATOR-ATTESTATION-CHECKLIST-2026-10-16.md) is **design-only** and has no assumed DEV trusted anchor. It must produce **`DEV_PROVENANCE_UNVERIFIED_STOP`** unless owner/operator can independently establish a DEV-only read scope without Docker labels, guessed paths or PRODUCTION enumeration. Even if P0 later passes, source-at-rest, effective hooks, and in-process loaded state are distinct authorization/evidence gates.

**Current state:** `SOURCE_PINNED_HARDENED_OFFLINE_35_OF_35_PASS` (historical), `SOURCE_PINS_11_OF_11_MATCH` (historical GitHub comparison), `HARNESS_REVIEW_PASS_LIMITED`, `DEV_PROVENANCE_UNVERIFIED_STOP`, `INSTALLED_SOURCE_UNVERIFIED`, `EFFECTIVE_HOOKS_UNVERIFIED`, `NODE_ROUTE_UNVERIFIED`, `WORKER_ROUTE_UNVERIFIED`, `DEV_PROD_SEPARATION_UNVERIFIED`, **`POSTING_NO_GO`**.

**No code/test changes, new test execution, or host/DEVELOPMENT/PRODUCTION activity in this review.**
