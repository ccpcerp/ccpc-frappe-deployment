# CCPC ERPNext — Exact-source inert Material Issue v2 offline test evidence

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
