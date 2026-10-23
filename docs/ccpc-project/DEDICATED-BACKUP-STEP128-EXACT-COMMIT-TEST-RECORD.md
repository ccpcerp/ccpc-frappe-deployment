# Step 128 — Exact GitHub blob offline verification checkpoint

**2026-10-23 — PARTIAL REGRESSION VERIFICATION; NO DEPLOYMENT OR LIVE DATA.** Owner replied **"Approved"** to running the exact PR #30 GitHub revision offline and its existing regressions before any DEVELOPMENT integration. This document distinguishes what actually ran from tests that remain pending.

## Source-of-truth and execution environment

- Independently verified GitHub PR #30 **OPEN/DRAFT/UNMERGED**, branch `feature/dedicated-prod-backup-safety-2026-10-23`, pinned head `27b8344529e133887c040a12e104254390a9b6a6`, base `security/dedicated-prod-external-env-2026-10-23` (open/draft PR #29). PR #29 at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c` is stacked on open/draft PR #27 at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. Source files and GitHub-first workflow reviewed using connected GitHub tools.
- **Offline disposable tooling, outside both CCPC hosts:** Python **3.13.5**, test files in a local sandbox directory `/mnt/data/step128`. No Docker daemon, Frappe database, site, Synology, NAS credentials or backup filesystem was contacted. This path is a sandbox test path, **not** a deployable artifact or server path.
- Container direct outbound GitHub DNS resolution was unavailable. Exact Step 127 policy module and tests were reconstructed locally from the GitHub content that was authored and fetched in the prior review; Step 125 module/tests had been retained locally from their previous offline verification. **Each of these four test inputs was checked with Git `hash-object` and exactly matched the GitHub `fetch_file` blob SHA at the pinned PR #30 head**:

| Exact committed file | GitHub/local matching Git blob SHA |
| --- | --- |
| `scripts/dedicated_backup_policy.py` | `9de6d269dcb90ba70302795a7dbb8149ebf5a2b4` |
| `tests/test_dedicated_backup_policy.py` | `adf9e0e53ca875317a0316d78aa5845e0db200d9` |
| `scripts/dedicated_backup_runtime.py` | `d94648baf0aa6385cce04e4e45e49e0466a63e65` |
| `tests/test_dedicated_backup_runtime.py` | `e4463e96a524a7c0fba2cd97ec5636cc0944095b` |

## Tests actually executed against identical committed bytes

```text
cd /mnt/data/step128
PYTHONPATH=. python -m unittest discover -s tests -p 'test_dedicated_backup_*.py' -q
----------------------------------------------------------------------
Ran 42 tests in 0.028s

OK

python -m compileall -q scripts tests
PASS: offline Python compilation
```

**PASS:** 15 Step 127 policy unit tests and 27 Step 125 runtime identity unit tests. The Step 127 verification gap described in `DEDICATED-BACKUP-STEP127-POLICY-REVIEW.md` is **now closed for these exact two newly committed files**: its actual **15** tests were executed against byte-matched GitHub code. Earlier 20 offline prototype cases remain **separate historical evidence**, not a claim of 20 tests in the committed file.

**NOT RERUN:** Step 123 four-artifact/NAS publication module plus its 13 tests, and Step 124 Frappe capture adapter plus its 20 tests. They are part of PR #30 but their full files were not available to this isolated test runner; the earlier test reports remain history, **not** a single combined 75-test run. The connector showed the files are present in PR #30; do not claim 75/75 passed. A fully verified suite still needs all four original modules and all four tests in one SHA-pinned checkout.

## Safety and correctness limitations

- These were **synthetic/mocked unit tests**, not actual Frappe v16 DB integration, trustworthy Docker release manifest/provenance, live site and volume inspection, verified quiescence, files consistency, complete NAS backup, CIFS publication or a restore drill.
- Step 127 policy returns `ValidatedRelease.trusted_runtime=False`, `MountAssessment.backup_ready=False` and `ConsistencyAssessment.writes_quiesced=False/backup_ready=False`. The live Step 125 verifier remains **unwired** to Step 127's new named logs mount policy; it still requires exactly one backend mount and may reject the intended Docker image with an auto-created logs volume. No named logs volume was added to Compose.
- No trusted approval channel for manifest digests, immutable image/build provenance, actual Compose hash, real Frappe v16 backup wrapper, consistency hold, failure redaction, retention, scheduled jobs or recovery key escrow was installed/tested.
- No updates to any GitHub **code** branches in Step 128; PR #27/#29/#30 remain draft/unmerged. No DEVELOPMENT pull, service restart, Docker build, PRODUCTION migration/deployment, mount, NAS write/delete, cron, backup, restore or old production operations were performed.

**Next precise gate:** Run the entire **four-suite, exact SHA-pinned** PR #30 offline regression set (expected historical total 13+20+27+15 = 75 tests, but actual test count must be discovered from that checkout), inspect any failures, then update this record with observed output. If direct isolated GitHub checkout remains inaccessible, preserve this **42/42 partial checkpoint** instead of claiming full verification. No real host action should be requested merely to satisfy offline test completion.
