# CCPC ERPNext — Exact-source inert Material Issue v2 offline test evidence

## Follow-on exact-source write-target review — 12 offline tests PASS, 2026-10-15

**Authority:** Owner said “Continue” to the prior **GitHub-only** SQL write-path tracing and offline testing work. No ERPNext server staging, Frappe integration run, SQL COMMIT, restoration, or PRODUCTION action was authorized.

**Exact source hashes matched local, GitHub-backed file blobs after reviewed edits:**
```text
scripts/development/operator/ccpc_material_issue_first_commit_review_only_v2_20261015.sh
GitHub and local git hash-object: 0a17d53cc0badac1de05745ef9edfb60d342ed89
bytes: 41591

tests/offline/test_material_issue_v2_guards.py
GitHub and local git hash-object: 6469997eb93efb523a308ca015c755902132764d
bytes: 7951

tests/offline/test_material_issue_v2_dml_surface.py
GitHub and local git hash-object: 29fbbd8c3603b24488d4bc8e2ad671b667536edf
bytes: 5279
```

**GitHub review commits:** v2 DML target hardening `19d3227b37a640252d4caf1141262b30746bde6d`; original seven-test suite dependency adjustment `c096255a98835488fc160e669cb134fcfb513a6e`; added five-test DML surface suite `6efb3b89e5c50aedb74a50fae29aa380a4121926`.

**Source change:** Added `review_dml_scope`, called from the existing `limited_sql` proxy. This is a **provisional, fail-closed regex gate**, not a real SQL parser or proven ERPNext DML boundary. It accepts only simple, backtick-quoted `INSERT INTO` forms for `tabStock Entry`, `tabStock Entry Detail`, `tabStock Ledger Entry`, `tabGL Entry` and `tabVersion`; accepts simple `UPDATE ... SET ... WHERE` forms targeting `tabWithdrawal Slip`, `tabWithdrawal Slip Item`, `tabStock Entry`, `tabStock Entry Detail`, `tabStock Ledger Entry`, `tabGL Entry`, `tabBin`; rejects DELETE, INSERT IGNORE, unrelated tables, unqualified broad updates and the currently unmapped `tabSeries` naming-counter writes. The previous high-level SQL prefix/comment/COMMIT phase checks remain present.

**Run locally in a credential-free, non-server review container:** SHA-pinned local script and two exact-source unittest files underwent `bash -n`, Python embedded AST parse and `python3 -m unittest discover -v -s <offline-test-dir> -p 'test_material_issue_v2_*.py'` with `CCPC_V2_SCRIPT` pointing at the source-matched v2 file. The **existing 7 + new 5 tests = 12 tests: ALL PASSED** (0.054 sec of Python unittest execution, timing incidental). The old seven-test harness was updated to inject the newly required pure DML helper dependency in its isolated `limited_sql` extraction; the independent new suite evaluates the actual `review_dml_scope` AST and tests 10 named negative patterns. A dry shell invocation with the *old* approval environment variable still exited status 1 with the permanent `NO-GO` message **before any Docker operation**. This is an **offline static/helper test** and no integration test.

**Critical interpretation:** One cannot infer release/posting safety from these PASS results:
- The regex recognizes only first DML verbs and table names. It does not prove WHERE row selection, embedded subqueries, stored functions, multi-table effects, driver-level commands, all DDL/implicit COMMIT paths, or completeness of Frappe's write path. For instance, a `WHERE 1` update to an otherwise listed table is not a safe record-scoped operation.
- In pinned Frappe `frappe/model/naming.py:getseries`, naming series updates `tabSeries` directly. `tabSeries` is **intentionally blocked in v2**, so the synthetic issue could fail if it uses that naming counter. Do not add permission absent exact naming metadata, expected prefix and current-row invariants.
- Real Frappe/ERPNext posting may legitimately write currently denied auxiliary, child, repost, reservation, global-search or ledger-related DocTypes, as well as Redis/cache/filesystem effects outside SQL. Exact shape must be separately traced in a reviewed rollback-only integration test, not inferred.
- The v2 shell has an **unconditional early `exit 1`** and must remain inert. The old candidate remains unchanged and NO-GO. The v2 script was not staged/executed on Ubuntu, and no business transaction or PRODUCTION access occurred.

**Next safety gate:** Continue GitHub-only source mapping of exact table/delta list including `tabSeries`, Frappe/ERPNext auxiliary SQL and callbacks. Update negative tests with independently reviewed output. Only then seek owner authorization for a **new distinct, rollback-only** synthetic DEVELOPMENT integration rehearsal; do not unarm v2 or run a first persistent one-unit stock/GL COMMIT.

---
### Previous seven-test checkpoint (historical source blob)

The previous seven-test PASS below refers to the **earlier v2 blob `1d75461ec5bcb22e3e67f2ebfb503b79b3606243`**, not the updated 41,591-byte source. Retained for audit continuity.

**Date:** 2026-10-15  
**Disposition:** **PASS for seven offline helper guard tests and exact-source syntax/inertness. STILL NO-GO for deployment or posting.**

## Provenance and method

The local isolated test container had no GitHub network/DNS access. The source content and exact blob SHA were independently retrieved via the *connected GitHub tool* from `ccpcerp/ccpc-frappe-deployment` on `review/material-issue-first-commit-preparation-2026-10-15`. To avoid untrusted direct downloads or GitHub credentials in the test container, the full v2 file was deterministically reconstructed there from the independently byte-verified original first-commit candidate and the sequence of reviewed GitHub edits. That reconstructed file was only accepted as the **exact committed source** after `git hash-object` returned the **same GitHub blob SHA**. No network/production secrets, user data, business records or server credentials were used in the local test.

**Exact v2 script:**
```text
scripts/development/operator/ccpc_material_issue_first_commit_review_only_v2_20261015.sh
expected GitHub blob: 1d75461ec5bcb22e3e67f2ebfb503b79b3606243
actual local git hash-object: 1d75461ec5bcb22e3e67f2ebfb503b79b3606243
39982 bytes
```

**Exact unit test source:** Existing isolated local test file was independently checked byte-for-byte against GitHub using `git hash-object`:
```text
tests/offline/test_material_issue_v2_guards.py
expected GitHub blob: 772abee3e57eb844deee1bcd2f40df67d0bebf71
actual local git hash-object: 772abee3e57eb844deee1bcd2f40df67d0bebf71
7763 bytes
```

The v2 script retains its **unconditional early `exit 1`** before Docker, marker creation or embedded Python. The read-only local test used no Docker/ERPNext/SQL/Redis connection.

## Offline checks performed on exact GitHub source

```text
$ bash -n scripts/development/operator/ccpc_material_issue_first_commit_review_only_v2_20261015.sh
PASS

$ python -c 'ast.parse(extracted_embedded_python_heredoc)'
PASS

$ CCPC_V2_SCRIPT=<exact_v2_path> python3 -m unittest -v test_material_issue_v2_guards.py

test_entrypoint_unconditionally_inert ... ok
test_exact_dev_endpoint_fail_closed ... ok
test_full_backup_hashing_outside_write_transaction ... ok
test_realtime_only_synthetic_notifications_suppressed ... ok
test_recovery_metadata_gate_detects_change ... ok
test_source_syntax_without_execution ... ok
test_sql_command_denials_and_exact_commit_phase ... ok

Ran 7 tests
OK
```

**Additional inertness check** (local isolated container; previous legacy approval environment string set deliberately to prove it cannot arm v2):
```text
CCPC_FIRST_ISSUE_EXECUTION_APPROVED=ccpc-integration2-one-unit-stock-gl-commit bash <exact_v2_path>
exit status: 1
NO-GO: Review-only v2; Docker/SQL execution is deliberately disabled.
EARLY HARD STOP BEFORE DOCKER: PASS
```

### What the seven tests actually exercise

The suite parses the exact v2 embedded source into AST, dynamically extracts **individual pure/local guard function definitions** (without invoking the full posting path), and runs mock negative cases for strict DEV DB host/port/override parsing, unexpected SQL/DDL/comment/transaction-control and duplicate COMMIT requests, recognized/denied after-commit realtime events, and fixture-only backup file metadata changes/missing-file rejection. Additional source-structure tests enforce the unconditional shell stop and prevent bulk recovery SHA256 inside the intended locked transaction.

### What this does **not** prove

- No live Frappe/ERPNext site, DEVELOPMENT/PRODUCTION Docker service, MariaDB data, customer record or Redis server was accessed.
- No `Stock Entry.insert()`, `submit()`, Stock Ledger Entry, GL Entry, Frappe callback, row lock or **real SQL COMMIT** was executed.
- The suite does **not** simulate the full pinned Frappe/ERPNext stock posting call chain, all `tabSeries`/child/ancillary table DML, raw driver cursor behavior, cache or external side effects.
- No archive was restored; sample files in the test are 48 small **dummy fixtures**, not historical backup archives. No off-host backup or independent restore proof.
- `ast.parse` and static tests prove source syntax/guard behavior only. They do not prove that the hardened v2 would work correctly if someone removed its unconditional stop.
- The original first-commit candidate remains unchanged and is separately **NO-GO**.

## Next safety gates

1. Continue **GitHub-only** source-level table-write mapping of the exact synthetic Stock Entry issuance, naming/serial/reservation/repost/Version/child tables and deterministic SQL/Redis callbacks; add negative offline tests for newly identified guards.
2. Review isolated recovery archives and an independently approved recovery plan (off-host copy and/or disposable isolated restore), without any PRODUCTION interaction.
3. Only after a renewed source review and separate owner permission may a **new**, independently reviewed rollback-only integration rehearsal be considered. A permanent synthetic one-unit stock/GL COMMIT requires its own explicit authorization and **must not** be inferred from this offline pass.

**Status at test completion:** v2 and prior original candidate NOT STAGED on Ubuntu and NOT EXECUTED; v2 deliberately inert. Historical DEV/PROD separation and isolated read-only SQL/recovery checks remain the last operator-reported live audit. No development database write, ledger posting, stock movement, merge, Docker lifecycle change or PRODUCTION modification was performed.
