# CCPC ERPNext — Source-pinned offline harness hardening checkpoint

**2026-10-16 | GitHub-only tests/hardening | DEVELOPMENT/PRODUCTION runtime untouched | POSTING_NO_GO**

## 1. Authority and source of truth

Owner approved the specific [final suite review](MATERIAL-ISSUE-SOURCE-PINNED-22CASE-FINAL-SECURITY-REVIEW-2026-10-16.md) recommendation: **GitHub-only hardening of the 22-case source-pinned offline harness**, with fail-closed integrity under Python `-O`, AST pre-execution inspection, restricted mock globals, adversarial fixture mutation tests, and correction of the callback lifecycle model. This approval does **not** authorize host/DEVELOPMENT execution, shared Docker inspection, Redis/SQL/Node/RQ access, application deployment, real Stock Entry/GL/SLE posting, write-then-rollback, or PRODUCTION access.

Branches verified before implementation: deployment review `review/material-issue-first-commit-preparation-2026-10-15` HEAD `1bf7dc0e4edcb61c370f22a71f373a665122714e`; handoff `docs/ccpc-checkpoint-2026-10-10` HEAD `562e0a0bc28cf99537893d2717bfef965b09a6fd`; CCPC app `feature/withdrawal-material-issue-safety` HEAD `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`.

**Code artifact revised (only the existing offline test module):**
- [Hardened suite](../../tests/offline/test_material_issue_source_pinned_reachability_20261016.py)
- Final read-back Git blob `38ceb7976d2e6f3faccf2012d27ca98edef6a84b`; local SHA256 `862f58e886f5c79676a07e26c0d1e137b0a20442be475190ba3912d460040392`.
- GitHub final implementation commit `ba60aa8485270f799e42c3462693868578f553f8`. Prior sequential test-only revision commits `45ce91282bfc958b8878962b7fabec08cb567b62` and `6f91bc86fd59a0dd1754dff7602bde6a83e9ec7e` were formatting/byte reconciliation, not a separate staging cycle.
- **Fixture unchanged:** [11 pinned excerpts](../../tests/offline/fixtures/material_issue_reachability_source_pins_20261016.json), Git blob `7ca589594fb9ed818da75476ddbe68b471eef444`, SHA256 `57344e05f07c2f31445e4140ef6bf543cd97660fb34aa2c18db8dd9443f38bb9`. All 11 excerpts had previously been independently matched to their immutable upstream GitHub blobs. No fresh upstream-source comparison was claimed in this hardening step.
- **No custom application code changed.**

## 2. Hardening changes and honest guarantees

| Change | Implementation detail | What it guarantees / what it does not |
| --- | --- | --- |
| Optimization-independent integrity | `FixtureIntegrityError` raised by explicit `if` checks; SHA256 and Git-blob digest verified with `hmac.compare_digest`, never by `assert`. | Modified fixture bytes are rejected even with `python -O`. **Does not** prevent a privileged editor from replacing both file and trusted digest constants. |
| Bounded fixture reading | Open fixture in binary mode and read at most **65,537 bytes**, reject over 65,536 before parsing. | Bounded bytes copied from this fixture; not whole Python-process memory confinement. |
| Entire-fixture AST preflight | Confirm eleven expected unique keys, known file-blob pins, single source function, expected names, no decorators; check every excerpt *before* executing any selected function. Ban imports, globals, nonlocals, async/await, class definitions, `__*` names/attributes, direct `exec`, `eval`, `open`, `__import__`, etc.; reject executable parameter defaults/annotations; restrict `getattr` to the known webhook queue literal. | Detects common malicious edits and definition-time execution that could occur before the test function is invoked. **Not** a formally complete Python safety proof or a sandbox for arbitrary source. |
| Restrict executable snippets | Only six approved keys may be compiled/executed under synthetic dependencies. Five other excerpts (including heavy RIV worker function) remain **AST-only**. Inject limited `SAFE_BUILTINS` and the `StockController` annotation placeholder; prevent external test globals overriding restricted builtins. | Avoids accidentally invoking full repost/stock business paths inside this harness. Object introspection or attacker-edited harness code remains outside its defensive guarantees. |
| Adversarial test expansion | Added tampered fixture test, optimized `-O -I -B -S` tests, dynamically recomputed digest + malicious AST tests, oversize rejection, execution allowlist and restricted builtins tests. | Shows fail-closed responses in covered offline attacks; no real SQL/Redis/PRODUCTION event performed. |
| Correct callback interpretation | Reworked previous `test_18`: synthetic after-COMMIT and after-ROLLBACK callbacks are run in **separate synthetic cases**, not both during a single fake transaction. | Avoids a misleading lifecycle claim; not an actual DB/Redis transaction test. |

**Important security caveat:** `exec` of even allowlisted pinned Python functions is **not a general-purpose sandbox**. The safety claim is restricted to the reviewed, SHA-pinned eleven-source fixture under a disposable, unprivileged local offline test environment with no secrets, sockets, application imports or network clients. Future fixture/source changes require a fresh security review before reuse. Python sandbox escapes are not a release-test target of this harness.

## 3. Actual offline execution and byte verification

Test workspace: disposable `/mnt/data/ccpc-reachability` on the local artifact environment, **not** the Ubuntu CCPC server or a Frappe bench.

```bash
cd /mnt/data/ccpc-reachability
PYTHONDONTWRITEBYTECODE=1 python -W error -m unittest discover \
  -s tests/offline -p 'test_material_issue_source_pinned_reachability_20261016.py' -q

PYTHONDONTWRITEBYTECODE=1 python -O -W error -m unittest discover \
  -s tests/offline -p 'test_material_issue_source_pinned_reachability_20261016.py' -q
```

**Actual final tested results:** normal mode **35/35 PASS (Ran 35 tests, OK)**, optimized mode **35/35 PASS (Ran 35 tests, OK)**. The prepublication initial working copy had five test harness `NameError: bool` errors under the restricted builtin namespace; added the minimal `bool` annotation binding and reran to 33/33 PASS, then added two further adversarial definition-time-execution tests and reran both modes to 35/35 PASS. These were fixture harness changes, not observed ERPNext defects.

**Exact-byte verification:** `git hash-object` of the locally tested, finalized test module is `38ceb7976d2e6f3faccf2012d27ca98edef6a84b`. GitHub readback of the committed file returned the **same** Git blob; the unchanged fixture readback returned `7ca589594fb9ed818da75476ddbe68b471eef444`. No post-test source modifications occurred locally. Offline subprocesses invoke the local Python interpreter with isolated flags to verify `-O` behavior; they do not call Frappe/ERPNext, Docker, network, Redis or SQL.

**Result category:** `SOURCE_PINNED_HARDENED_OFFLINE_35_OF_35_PASS` under the two stated local modes. `OPTIMIZED_FIXTURE_DRIFT_REFUSED` in covered negative cases. Not `DEV_INSTALLED_SOURCE_VERIFIED`, `LIVE_RQ_ROUTE_VERIFIED`, `SQL_ROLLBACK_SAFE`, `POSTING_ALLOWED` or `PRODUCTION_READY`.

## 4. Remaining next gates

- **Still unverified:** installed DEVELOPMENT Frappe/ERPNext/CCPC code, effective site hooks/Notifications/Webhooks/Server Scripts, loaded long-running process code, Node/RQ Redis routes, Redis instance/physical DEV-PROD isolation, actual MariaDB rollback behavior after Stock Entry/SLE/GL events, duplicate issuance/concurrency and live recovery.
- **Previous [DEV source/effective-hooks attestation design](MATERIAL-ISSUE-DEVELOPMENT-SOURCE-AND-HOOKS-ATTESTATION-DESIGN-2026-10-16.md) remains design-only:** independent genuine-DEV provenance is still NOT proven. No host path, process, Docker label, service name, socket or shared mount can be guessed and treated as a safe anchor.
- **Recommended separate next approval:** conduct a *GitHub-only final security/usefulness review* of the hardened suite before deciding whether an independently scoped operator P0 DEVELOPMENT-only source/hook attestation checklist is feasible. Do **not** stage or execute this harness on Ubuntu: its primary purpose is offline source regressions, not collecting runtime data.
- **Explicit separate approval** would be required for any future DEVELOPMENT host-based read, app pull/test, database integration or PRODUCTION action. No stale one-shot token can be reused.

**No production or DEV operation. No Stock Entry, SLE or GL transaction. POSTING_NO_GO.**
