# Step 133 — Full exact-GitHub-blob offline combined regression verification

**2026-10-23 — COMPLETED, isolated OFFLINE tests 135/135 PASS. NOT deployed, integrated with running Docker or backup-ready.**

The owner approved Step 133 **offline verification only**, to rerun all current draft PR #30 tests using exact GitHub source, particularly the Step 132 signed approval verifier together with the full Step 127 manifest validator and Step 131 provenance checks together with complete source files. No code alterations, PR merge, DEVELOPMENT pull, dedicated or legacy PRODUCTION operation, NAS mount/write, image build, backup, restore, cron or retention changes were authorized or performed.

## GitHub source and pinned review point

Connected GitHub verified [draft PR #30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30) **OPEN/DRAFT/UNMERGED**, feature branch `feature/dedicated-prod-backup-safety-2026-10-23`, pinned head **`fd751ab7c39c252e469e1d59d6ebbb1408381061`**, based on open/draft PR #29 at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`, stacked on open/draft PR #27 at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. No PR branch was changed by these tests.

An isolated local workspace `/mnt/data/step133` was assembled **from the connected GitHub fetch_file source bytes** at that exact head. The isolated execution environment could not directly clone GitHub, so the files were reconstructed via source transfer and every resulting local Git `hash-object` compared to its connected GitHub exact blob ID. This was **not** a conventional `git clone` and no claims about a GitHub Actions run are made. Local transfer/decompression tooling is **not** application source and was not committed.

### All 17 exact file identities verified

| File | Verified Git blob SHA |
| --- | --- |
| `scripts/dedicated_backup_core.py` | `3650e0acf0832173606d9a8c5ed4c1990b6fc362` |
| `scripts/dedicated_backup_capture.py` | `710eb63531a8521af62d708a8e12267f4d968a24` |
| `scripts/dedicated_backup_runtime.py` | `49a9c3f9d882cf4296f87b21989e672f3ca3e9fc` |
| `scripts/dedicated_backup_policy.py` | `9de6d269dcb90ba70302795a7dbb8149ebf5a2b4` |
| `scripts/dedicated_backup_approval.py` | `8ff82b242192628104b1c2fd82df9566e3af7ca6` |
| `tests/test_dedicated_backup_core.py` | `6e6d3ec23ec8ae2b41622a071847906abe08b012` |
| `tests/test_dedicated_backup_capture.py` | `4453a7d237fcb6577e93b0c396d049e157b2f8fd` |
| `tests/test_dedicated_backup_runtime.py` | `e009f0da977c6e242470de4a66144190923277be` |
| `tests/test_dedicated_backup_policy.py` | `adf9e0e53ca875317a0316d78aa5845e0db200d9` |
| `tests/test_dedicated_backup_approval.py` | `bd095a874d12906e943041e13cb2a677fe1e12be` |
| `tests/test_dedicated_compose_logs.py` | `8baf9a60b4b3588a7c441b2a454143651f9d6543` |
| `tests/test_dedicated_image_provenance.py` | `15f79170a26cd3da10b71fb4d6963c750d293b99` |
| `compose.yaml` | `752b86e1ba4c1977a2636b1916f6015771f4c28c` |
| `overrides/compose.dedicated-pre-tls.yaml` | `14fd89a3c2371104f464964137483de9f4a35861` |
| `images/custom/Containerfile` | `523ad5f3a7a58c8c9da23ad822d3f3d8526e16d2` |
| `scripts/config.sh` | `32614da1044c768bd67dcb9b9491e7c48ff2653a` |
| `scripts/modules/docker.sh` | `453959daf3b548fa67f8bdc647be0f147acd603e` |

Each file's byte identity was checked again in the final run; **17/17 exact GitHub blob matches**.

## Actual combined observed test output

Disposable Linux offline environment outside CCPC infrastructure, Python **3.13.5**, PyYAML **6.0.3**, cryptography **46.0.4**. Tests use synthetic temp directories and injected mocked Docker/Frappe inspection/capture behavior; Ed25519 keys exist **only as ephemeral in-memory test keys**.

```text
cd /mnt/data/step133
PYTHONPATH=. python -m unittest discover -s tests -p 'test_dedicated_*.py' -q
----------------------------------------------------------------------
Ran 135 tests in 0.217s

OK

python -m compileall -q scripts tests
PASS: Python compileall
PASS: all 17 GitHub blob identities reproduced in isolated offline workspace
```

| Suite | Actual passed tests |
| --- | ---: |
| Step 123 — core publication (synthetic) | 13 |
| Step 124 — Frappe v16 capture adapter (mocked executor) | 20 |
| Step 127 — release, named mounts and consistency policy (synthetic) | 15 |
| Step 125/129 — runtime identity/volume inspection (mocked Docker) | 37 |
| Step 130 — opt-in dedicated Compose configuration (static YAML and merge model) | 16 |
| Step 131 — backend image provenance labels/source contract (static complete source) | 7 |
| Step 132 — signed independent release approval/revocation (in-memory test keys) | 27 |
| **Combined exact-file regression run** | **135/135 PASS** |

### What Step 133 resolves

- Step 132's 27 Ed25519 tests now run against the **complete, exact GitHub policy** (not the earlier contract-compatible fixture).
- Step 131's 7 source-provenance tests now run against **byte-matched complete GitHub Containerfile, scripts/config.sh and scripts/modules/docker.sh** (not representative fixtures).
- All current dedicated-backup-related test suites now pass **together**, rather than relying on historical isolated runs.

## Unverified and prohibited conclusions

**135/135 is an offline synthetic/mock regression milestone, not operational readiness.** In this step there was:
- NO real `docker compose config` CLI, Docker daemon, container, running site, immutable image build/digest or trusted release distribution, and no Docker socket security assessment.
- NO actual Frappe v16 MariaDB dump, consistent database-to-public/private attachment capture, controlled freeze of API/queue/scheduler/integration writers, backup cleanup side effects or encryption/filter and secret restoration checks.
- NO dedicated Synology CIFS `renameat2` atomicity/durability, unattended NAS backup, full four-artifact isolated restore, monitoring/retention/recovery drill.
- NO independent signing/reviewer-identity service, high-integrity Ed25519 public key/trust anchor, monotonic approval-generation service, key revocation freshness or trusted clock distribution. Signed snapshots can be replayed during their allowed lifetime without such an external high-water mechanism.
- NO real BACKUP permission enabled: Step 127 policy, Step 129 runtime and Step 132 approval all continue to set `backup_ready=False`. No connection from these modules to a live backup executor was authorized.
- NO physical DEVELOPMENT or PRODUCTION commands, service changes, database migrations, image builds, NAS mounting or changes to `/etc/fstab`, cron, backup schedules or data. Existing live PROD/DEV on `ccpcerpserver`, old Synology `erpnext_backups`, and NEW dedicated host `ccpcerp-prod` remain unchanged by Step 133.

## Next independently approved gate

Review integration blockers and an **isolated DEVELOPMENT/disposable Docker/Frappe test plan** first, including exact Compose version/file order, immutable image provenance and source input verification, safe Docker privilege, workload and volume identity, backup consistency and Frappe deletion side effects, restore drill, logs-volume lifecycle and rollback. Do not pull on DEVELOPMENT before checking branch, commit, Git status and preserving outstanding work; do not operate any PRODUCTION host or NAS on this review-only approval. Separate authorization for any real build, image pull, Docker `compose config`, NAS mount, service freeze, database backup or deployment.
