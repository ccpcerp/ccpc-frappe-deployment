# Dedicated CCPC production — GitHub-only readiness review of draft PRs #27, #29 and #30

**Date:** 2026-10-24 (Asia/Manila). **Scope:** owner-approved source, change/branch, PR-status, documented test-evidence and CI metadata review **only** while away from office. **Decision: NOT READY TO MERGE OR DEPLOY.** No runtime or integration tests were executed, no code was changed, no workflow was rerun, and neither CCPC host, Hyper-V/WSL2 lab, Synology, secrets nor production database was contacted.

## Verified source baseline and dependency ordering

| PR | Purpose | Base branch | Reviewed head | State |
| --- | --- | --- | --- | --- |
| [#27](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/27) | localhost-only PRE-TLS Compose overlay, dedicated profile | `main` | `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f` | OPEN, DRAFT, mergeable per GitHub metadata |
| [#29](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/29) | dedicated external credentials and release image/tag | #27 branch | `bd92ade7ac859b9f6b21b157bdc1629e93f4540c` | OPEN, DRAFT, mergeable |
| [#30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30) | inert four-artifact capture/publication, runtime verification, policy, signed approval design | #29 branch | `fd751ab7c39c252e469e1d59d6ebbb1408381061` | OPEN, DRAFT, mergeable |

The three stacked bases/heads matched the documented Step 135 snapshot when independently checked on 2026-10-24. **Mergeable is not tested or approved.** Review branch heads and merge bases again before any future operation.

Separate [draft PR #28](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/28) `622e41e47c0dcf81016b4e03c349ceeee05953b0` is **documentation-only** for an HTTPS 443 gateway; it is not a working gateway or deployed certificate.

## Findings prioritized by production risk

### R1 — Release blocking: configuration/network/TLS not proven

- **PR #27 source-reviewed controls:** `scripts/config.sh` explicitly opts into `dedicated-pre-tls` and appends dedicated Compose overlay **last**; the overlay replaces frontend publication with `127.0.0.1:8080:8080/tcp`, and MariaDB uses `${DB_PASSWORD:?…}`. Existing `legacy-lan` remains the default. The PR alters three files; no live configuration or listener validation was reported.
- **Actual Compose v2 semantic render absent.** `!override` requires a compatible Docker Compose v2 CLI (Step 135 minimum 2.24.4); PyYAML structural checks and Step 133 mocked tests do **not** prove the five-file merge, actual binds or named volumes. Step 135 CMP-01..12 remain unexecuted.
- **Three GitHub Actions results associated with PR #27 head show completed failure**: `Core / Build Develop` (run 39875178484, failed `Resolve Versions` job), `Lint` (run 39875178472, failed `lint` job), and `Core / Build Stable` (run 39875178513, failed v15/v16 `Resolve Versions` jobs; build/publish skipped). **Do not assume these failures were caused by PR #27**: this review could not retrieve detailed job logs (GitHub log request returned NOT_FOUND / blob unavailable), and no diagnosis or rerun has occurred. PR #29/#30 did not return PR-triggered runs from the queried commit-run endpoint; this is **not** proof that no other checks exist.
- **TLS remains design-only:** PR #28 suggests host-level HTTPS 443 → 127.0.0.1:8080, but no executable gateway/certificate/client-trust/firewall integration is verified. A pre-TLS loopback profile alone is not employee-accessible production HTTPS.

**GitHub-only next work:** inspect existing CI workflow/configuration and possible inherited baseline failure; prepare a narrowly bounded, manually runnable Compose-config-only, source-pinned test (no real credentials, no services), and independently review HTTPS 443 gateway source and certificate decision. Do not pay for runner upgrades merely to validate Compose semantics.

### R2 — Release blocking: credentials and runtime deployment controls require further hardening/acceptance

- **PR #29 source-reviewed controls:** `verify_dedicated_env_file()` rejects non-absolute, final-path symlink, checkout-local, wrongly owned, world-readable or overly permissive immediate-parent credentials. `ccpc_compose()` passes `--env-file` explicitly; `deploy_release()` exports dedicated `CUSTOM_IMAGE` and `CUSTOM_TAG` and skips legacy `.env` backup/rewrite. These checks were previously tested with mocked Docker; there is no equivalent real Docker/Compose acceptance.
- **Review questions requiring explicit tests before live use:** validation currently checks mode/owner of the file and its **immediate parent**, not independently attested all ancestor directory trust; permitted values and inherited environment/Compose project/profile variables should be reviewed so a later shell or CI environment cannot redirect operations; dedicated env-file contents/required nonempty dummy password must be checked by the actual Compose negative render. These are **hardening candidates**, not a proven exploitation report.
- **Rollback boundary:** `deploy_release()` proceeds from container deployment to service wait, checks, **migrations**, and health check; its dedicated `restore_env()` deliberately does not roll back app/database changes. A guarded DEVELOPMENT rehearsal, idempotence assessment and recoverable rollback plan are necessary before a real release.

**GitHub-only next work:** expand mocked negative tests/guards only after separately approving an exact code-change scope; review logs for accidental env/secret exposure; document stop/recovery semantics.

### R3 — Release blocking: backup/restore framework is intentionally not integrated

- **PR #30 has inert code rather than a live backup daemon.** Source `scripts/dedicated_backup_runtime.py` has `VerifiedIdentity.backup_ready` hardcoded `False`; `dedicated_backup_approval.py` has `VerifiedApproval.trust_source_authenticated=False`, `backup_ready=False`, and explicitly states independently authenticated trust-key/revocation/high-water delivery is not implemented. `dedicated_backup_core.py` and `dedicated_backup_capture.py` intentionally exit `NOT ENABLED` if invoked as scripts; production runner/orchestration, quiescence and publication authorization are not wired.
- The recorded **Step 133: 135/135 synthetic/mock/static offline tests PASS** at the exact pinned PR #30 sources; it is a valid historical evidence set but **not** live Docker/Frappe/DB/NAS testing or proof a backup can be restored.
- `capture_with_verified_runner()` accepts an injected callback, but there is no production attestor/executor; validating caller-declared flags is not a verified pause of writers. Frappe's `delete_temp_backups()` side effects, four-artifact DB/files consistency, encrypted/partial backups, Docker socket permissions, worker logs/anonymous volumes and full restore remain open separate gates.
- `publish_verified_set()` has exclusive lock, SHA verification and no-replace publication design. CIFS mount identity, TOCTOU/dismount races, actual NAS durability, interruption/replay, and recovery correctness remain unverified in a real environment.
- Required outcome **before production data cutover:** demonstrate a tested, operator-recoverable backup and **isolated successful restore**. Whether the advanced PR #30 framework is on the critical path to *initial* cutover versus a separately approved simpler proven backup method is a **project scope decision**, not an implied permission to relax recovery safeguards.

**GitHub-only next work:** separate the minimum viable safe cutover requirements from longer-term advanced release signing / fault injection; keep PR #30 draft and not backup-ready. Integration later on a synthetic isolated target, with new specific approval.

## Efficient work order with no office access / no new expense

1. **Now in GitHub, read-only:** review PR #27 CI workflow dependencies and availability; do not rerun paid CI or assume a failure cause. Inspect PR #29/30 code paths for specific gaps and prepare small test/patch proposals.
2. **No office needed after narrow approval:** modify review-branch tests/guards and use available non-paid source-level local verification. Keep actual test provenance explicit; no silent workflow installation/publishing.
3. **At the next suitable approved runtime opportunity:** one batch of **source-pinned, sanitized Compose v2 G2 configuration checks** (CMP-01..12), not a full ERPNext deployment. The existing Hyper-V lab's `Guest Service Interface` was owner-observed **Disabled**; there is no need to keep troubleshooting it while mobile.
4. **Before cutover:** test actual dedicated-host deployment/TLS/credential boundaries and a recoverable backup and isolated restore, with explicit approvals and a rollback plan. No shared-live Docker/NAS destructive simulations.

## Review evidence and exclusions

- Compared GitHub PR metadata and all PR changed-file path inventories (3, 6 and 22 files), read `scripts/config.sh`, dedicated overlay, PR #29's `docker.sh`, `deployment.sh`, `env.sh`, security test and PR #30's core/capture/policy/runtime/approval modules, plus Steps 133–136 and current GitHub-first workflow.
- No new unit tests or Compose CLI runs performed; no source code modified, no PR merge, no paid GitHub Actions or runner rerun, no production/development/server access.
- Verdict: **SOURCE REVIEW COMPLETE, PRODUCTION READINESS NOT ESTABLISHED.** Unresolved runtime, TLS, signer/trust, backup consistency, NAS durability and restore requirements remain as explicitly identified above. Avoid turning these into an infinite new VM project; use the smallest separately approved test environment for each remaining risk.
