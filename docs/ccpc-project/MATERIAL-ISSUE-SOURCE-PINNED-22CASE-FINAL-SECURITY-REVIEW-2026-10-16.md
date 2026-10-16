# CCPC ERPNext — Final security and usefulness review of 22-case source-pinned offline suite

**2026-10-16 | GITHUB-ONLY final review | NO code/test changes, rerun, staging, runtime access, transactions or PRODUCTION activity | POSTING_NO_GO**

## Authorization, source-of-truth and scope

The owner approved the specifically proposed **final GitHub-only security/usefulness review of the existing source-pinned suite** and an **installed-DEVELOPMENT source/effective-hooks attestation design**. No authorization to implement revisions to the test suite, execute local/remote scripts, access DEV/PROD processes, discover the shared Docker daemon, read DB/config/Redis, deploy, perform write-then-rollback or commit Material Issue.

GitHub checks at start:
- Deployment review branch `review/material-issue-first-commit-preparation-2026-10-15`: `91c5a29cb42308720a5d19a65a4936d9e53f4eee`.
- Rolling docs branch `docs/ccpc-checkpoint-2026-10-10`: `09ba0957bd6f36a649d342ef2013927b4f22d78f`.
- CCPC application `feature/withdrawal-material-issue-safety`: `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6` (untouched).
- [Test](../../tests/offline/test_material_issue_source_pinned_reachability_20261016.py): Git blob `b537279f0ace2a2f689f79bc43654bd3d059daac` and documented SHA256 `ee5a5d91152c93e10c2b4cb4a5f5d7478d6b4ec2bcbe9d4752024afbf09d683c`.
- [Snapshot fixture](../../tests/offline/fixtures/material_issue_reachability_source_pins_20261016.json): Git blob `7ca589594fb9ed818da75476ddbe68b471eef444` and documented SHA256 `57344e05f07c2f31445e4140ef6bf543cd97660fb34aa2c18db8dd9443f38bb9`.
- [Original 22-case review](MATERIAL-ISSUE-SOURCE-PINNED-REACHABILITY-E2-OFFLINE-REVIEW-2026-10-16.md).

**Independent cross-check in this review:** all **11/11** fixture excerpts were re-fetched from the fixture's exact GitHub `repo/ref/path` and checked to equal the original source's contiguous text beginning at the recorded line and to have the fixture's recorded original file blob SHA. **11/11 exact match.** This is a fresh *GitHub source comparison*, **not** a fresh unittest run or attestation of a live installed file. The previous **22/22 tests passed** in the preceding GitHub-only implementation session and are historical synthetic evidence.

## Bounded positives

1. Exact excerpt matching is genuine within the pinned GitHub references; the earlier multiline-signature correction is reflected in the final fixture. Exact snapshot source is more auditable than a fully invented behavioral model.
2. Selected functions confirm only limited source semantics: ordinary non-test RIV `on_submit` does not inline-call `repost(doc)`; test mode may; the repeated consuming item/warehouse and future-SLE decisions are conditional; `StockEntry.on_submit` has stock-ledger, GL and repost-decision call sites; immediate cache invalidation can precede after-COMMIT and after-ROLLBACK callbacks; standard document notifications flag `after_commit=True`; webhook enqueue registration is after-COMMIT. The 22 tests separately cover certain mock branches.
3. The test suite uses only Python stdlib imports and synthetic objects under its recorded execution conditions. No real Frappe/ERPNext app, DB, Redis, Docker or business records were contacted during the earlier test run.

## Security and usefulness findings

| Severity | Finding | Concrete code behavior | Disposition |
| --- | --- | --- | --- |
| **BLOCKER to reuse as security gate** | **`assert` integrity enforcement can disappear under optimized Python.** | `snapshots()` uses `assert hashlib.sha1(...).hexdigest() == FIXTURE_BLOB`; `function()` uses `assert` for type/function checks. `python -O` disables these guards. Original test invocation was not optimized, so the earlier 22 passes remain scoped to that invocation. | Before promotion, use non-optional `if ...: raise IntegrityStop` and test both optimized/unoptimized negative cases. Prefer an explicit SHA-256 source file digest in addition to the Git blob pin. |
| **BLOCKER to treating arbitrary fixtures as safe** | **Fixture content is executed with `exec` and full implicit Python builtins.** | `function()` parses source, strips decorators and compiles the function AST, then `exec(..., names)`. The test `test_02` checks imports only *after* `test_01` has already instantiated all functions; import bans alone do not prevent dangerous function calls or builtin-based imports. Exact immutable source pins mitigate substitution in the original trusted fixture, but are not a process sandbox or proof of safety for future fixture edits. | Review AST/source before any execution, enforce a very small allowlist and restricted mock namespaces; use AST-only checks where possible; execute in disposable unprivileged environment without credentials/network/host sockets. Never apply this harness to unreviewed runtime code. |
| **MATERIAL evidence limitation** | **No test-run check of original upstream source against GitHub.** | Manifest metadata `blob` is compared against literal expected strings; the test validates the *fixture Git blob*, not actual upstream source bytes at run time. We independently reconciled 11/11 here, but future fixture changes need this check again. | Pin per-function content digest or use a controlled GitHub-only refresh procedure with pinned blob and starting-line verification. Do not substitute runtime files silently. |
| **MATERIAL evidence limitation** | **Some assertions are structural, not transitive safety proofs.** | `test_15` checks AST presence of `submit`; `test_16` counts `commit` calls in worker AST and call names in Stock Entry. These do not prove the absence of COMMIT through other modules, hooks, callbacks, middleware or an installed-version divergence. | Retain `SOURCE_REACHABILITY_PARTIAL` and `POSTING_NO_GO`. |
| **MATERIAL evidence limitation** | **Synthetic transaction lifecycle is not integrated.** | `test_18` manually invokes *both* the after-rollback and after-commit cache lambdas successively; useful for direct callback behavior, **not a realistic mutually exclusive transaction lifecycle**. `test_21` establishes webhook callback registration only; neither test proves network delivery/non-delivery after a real SQL COMMIT/ROLLBACK. | Reword acceptance assertions; add dedicated negative tests on deferred callback reset/order before claiming transaction consistency. Real MariaDB + Redis needs separately approved DEV integration. |
| **MATERIAL security boundary** | **Loaded DEVELOPMENT state, hooks and external recipients are unverified.** | Frappe `Document.run_method` can invoke installed app hooks, enabled Notifications, Webhooks, Server Scripts; client/site caches and long-lived process initialization can diverge from files. GitHub fixture source is not live process provenance. | Use separate [DEV source/effective-hooks attestation design](MATERIAL-ISSUE-DEVELOPMENT-SOURCE-AND-HOOKS-ATTESTATION-DESIGN-2026-10-16.md). |
| **LOW / naming clarity** | **Previous offline review path contains “E2”.** | Project's evidence tiers previously reserved E2 for process-bound runtime attestation. This 22-case suite is **E1-strength offline pinned-source evidence**, not live E2. | Preserve existing file name to avoid breaking references, but clarify stage labels in all new checkpoints. |

These findings concern **the verification technique** and its evidentiary limits. They are **not observations of an ERPNext security incident or proof of unsafe live stock transactions**. They also do not contradict the previous observed 22/22 outcome under its non-optimized, offline test conditions.

## Decision / next recommended approvals

**Decision: PASS AS LIMITED SOURCE-PINNED OFFLINE EVIDENCE; DEFER SECURITY-GATE PROMOTION AND ALL DEV STAGING.** Mark `SOURCE_PINS_11_OF_11_MATCH` and historical `OFFLINE_SOURCE_PINNED_22_OF_22_PASS`; do not mark the installed framework or hooks verified, runtime routes verified, transactions safe, or posting authorized.

1. **Optional next GitHub-only code hardening, separately approved:** remove `assert`-only trust boundaries, preflight fixture AST before compilation, forbid unsafe builtins and unintended side effects, add adversarial optimized interpreter and fixture mutation tests, and clarify callback-only versus lifecycle coverage. Modify only review-branch offline tests/fixtures, not application or DEV.
2. **Separate DEV-attestation *design* only:** independent genuinely DEV-bounded scope and source/hook provenance, followed by distinct approvals for implementation, staging and any one-shot execution. Do not assume this scope is attainable from Docker Compose labels or a host path alone. Static expected-state declarations cannot prove long-lived loaded code.
3. **Transaction gate unchanged:** no write-then-rollback or committed Material Issue, SLE, GL or other financial posting until explicitly approved DEV-specific integration and full external-side-effect review. PRODUCTION changes remain prohibited without separate approval.

**No code or tests modified and no tests rerun during this final review. No DEVELOPMENT or PRODUCTION access. `POSTING_NO_GO`.**
