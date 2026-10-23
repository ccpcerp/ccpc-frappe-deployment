# Step 128 — Full exact-GitHub-blob offline regression verification

**2026-10-23 — COMPLETED offline-only regression checkpoint: 75/75 PASS. NOT DEPLOYED OR PRODUCTION-READY.**

Owner approved the Step 128 objective: test the exact draft PR #30 files **offline**, including the previous backup publication/capture regressions, before any DEVELOPMENT test, NAS action, code merge or PRODUCTION operation. This document supersedes its earlier *42/42 partial* checkpoint: the **remaining 33 tests were subsequently completed successfully in the same isolated test environment**.

## 1. GitHub branch / trust scope

- Source of truth: `ccpcerp/ccpc-frappe-deployment`, draft PR [#30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30), branch `feature/dedicated-prod-backup-safety-2026-10-23`, head **`27b8344529e133887c040a12e104254390a9b6a6`**. At review completion PR #30 was OPEN/DRAFT/UNMERGED based on `security/dedicated-prod-external-env-2026-10-23` (PR #29, head `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`), stacked on PR #27 at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. The code PRs were **not modified** by this test.
- The isolated runtime could not resolve outbound `github.com`. The eight committed Python files were obtained/recreated from the connected GitHub source and previous locally preserved files, **then verified individually byte-for-byte using Git `hash-object` against each exact connected GitHub `fetch_file` blob**. This verifies tested **file identity**, without claiming a normal `git clone` or a live GitHub Actions checkout.
- Environment: Python **3.13.5**, disposable local `/mnt/data/step128` workspace, **outside any CCPC host or NAS**. All test inputs synthetic; Docker inspection and Frappe bench executor are mocked/injected. No backend/database connection, Synology SMB mount, credentials, Frappe site backup, Docker daemon, live ERPNext or production records used.

## 2. The eight exact-tested blob identities

| File | Verified Git blob SHA |
| --- | --- |
| `scripts/dedicated_backup_core.py` | `3650e0acf0832173606d9a8c5ed4c1990b6fc362` |
| `tests/test_dedicated_backup_core.py` | `6e6d3ec23ec8ae2b41622a071847906abe08b012` |
| `scripts/dedicated_backup_capture.py` | `710eb63531a8521af62d708a8e12267f4d968a24` |
| `tests/test_dedicated_backup_capture.py` | `4453a7d237fcb6577e93b0c396d049e157b2f8fd` |
| `scripts/dedicated_backup_runtime.py` | `d94648baf0aa6385cce04e4e45e49e0466a63e65` |
| `tests/test_dedicated_backup_runtime.py` | `e4463e96a524a7c0fba2cd97ec5636cc0944095b` |
| `scripts/dedicated_backup_policy.py` | `9de6d269dcb90ba70302795a7dbb8149ebf5a2b4` |
| `tests/test_dedicated_backup_policy.py` | `adf9e0e53ca875317a0316d78aa5845e0db200d9` |

Exact blob SHA equality was verified by local `git hash-object` and previously connected `fetch_file` results. No files were modified between verification and the final test.

## 3. Full combined observed test result

Executed in isolated disposable tooling:

```text
cd /mnt/data/step128
PYTHONPATH=. python -m unittest discover -s tests -p 'test_dedicated_backup_*.py' -q
----------------------------------------------------------------------
Ran 75 tests in 0.128s

OK

python -m compileall -q scripts tests
PASS: all eight source/test modules compile
```

| Committed suite | Actual tests passed |
| --- | ---: |
| Step 123 — Core four-artifact verification and fail-closed publication | 13 |
| Step 124 — Frappe capture adapter; mocked executor/attestor | 20 |
| Step 125 — Docker/site runtime inventory; mocked Docker responses | 27 |
| Step 127 — Approved manifest, exact mounts, consistency policy claims | 15 |
| **Combined exact-byte regression** | **75/75 passed** |

This resolves the Step 127 note's prior test execution gap: the **actual GitHub-committed policy test file has 15 tests**, and all 15 passed along with the other 60. The earlier 20-test prototype was a distinct prior artifact and is NOT part of the 75.

## 4. Blocking issues untouched by successful unit tests

- Tests are synthetic/mock only. No actual Frappe v16 `bench backup --with-files` against MariaDB, no simultaneous uploads/accounting/stock transaction consistency proof, no validation of Frappe's old-backup cleanup `delete_temp_backups()` on a disposable running site, and no full four-artifact application restore.
- Step 125 runtime verifier currently rejects any extra backend volume, whereas Step 127 policy proposes exactly two **named** `sites` and `logs` volumes; no Compose named `logs` mapping or integration has been made. This **source integration mismatch is not tested away** by separate mocked PASS results.
- The trusted image/release manifest does not yet exist: immutable reviewed image IDs, provenance label, independently approved configuration hashes, trusted manifest digest/approval channel and operational site-volume mappings remain unverified.
- Step 127 `backup_ready=False`, `writes_quiesced=False` and related gates remain deliberately false. No verified DB/file freeze mechanism, complete writer inventory, side-effect/filters/encryption proof, or trusted capture runner is connected.
- Step 123's remote CIFS `renameat2(RENAME_NOREPLACE)` behavior, mount-replacement races, crash-consistent publication, restoration, NAS retention, monitoring/alerts and key escrow remain untested or unimplemented.
- Neither PR #27/#29/#30 was merged; **no** new host or old host was inspected or changed, no Docker services altered, no NAS mount or write, no `/etc/fstab`/cron changes, no backups/restores/deletions in Step 128.

**Next recommended approval gate:** A **separate GitHub-only implementation/review** to reconcile Step 125's runtime volume inventory with Step 127's exact named logs policy and independently approved manifest contract, plus offline synthetic regression tests. The first **real DEVELOPMENT or disposable-Frappe integration** must still receive separate owner approval with verified safety/isolation, clean Git status, an explicit backup/rollback plan and no production impact. Production changes require later dedicated approval.
