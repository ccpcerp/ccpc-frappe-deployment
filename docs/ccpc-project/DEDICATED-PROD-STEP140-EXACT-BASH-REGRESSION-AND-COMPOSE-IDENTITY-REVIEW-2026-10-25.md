# Step 140 — Exact-source Bash regression PASS and dedicated Compose identity review

**2026-10-25 (Asia/Manila). Owner-approved GitHub-only continuation of Step 139.** This is a completed **source-matched, synthetic/offline Bash regression**, a narrowly corrected test fixture, and a **review-only** Docker Compose project-identity finding. **NOT a production-release authorization**; no Docker Engine/Compose binary, GitHub Actions, DEVELOPMENT, PRODUCTION, new host, NAS, Frappe bench, DB, VM or credential involved. No PR merge/rebase, image pull/build, services, migrations, cost or paid runner.

## 1. Frozen source and safe testing scope

The reviewed branch prior to the test fixture update was `review/dedicated-compose-env-guard-2026-10-24` at commit `7735ede2db25cd80918ef118a57a5f5a7a5cc295`. Independent GitHub fetch and local byte reconstruction in a **new ephemeral `git init` working directory** established the exact Git blob SHA-1 of **eight** source files:

| Exact GitHub source | Verified Git blob |
| --- | --- |
| `scripts/config.sh` | `32614da1044c768bd67dcb9b9491e7c48ff2653a` |
| `overrides/compose.dedicated-pre-tls.yaml` | `14fd89a3c2371104f464964137483de9f4a35861` |
| `scripts/lib.sh` | `7f83828f99273445b6b95d171fb9f9b4862c0587` |
| `scripts/modules/docker.sh` (Step 139) | `d6b0647e36653579909004c75e2ffffaeace98d8` |
| `scripts/modules/env.sh` | `38a6fdef14abc9e61ae8425ab606dce6201290c1` |
| `scripts/modules/deployment.sh` | `ab862074235f174bf5de042ea7c6562965a34243` |
| `tests/test_dedicated_profile_offline.sh` | `dd7a400b42574a23d1a2c118bbbdf3468f0eb51e` |
| `tests/test_dedicated_env_security.sh` (Step 139) | `1e70822d8003c74a59d588c700adc6e908a8f4f8` |

`bash -n` **PASS on all seven Bash files**. Observed **`bash tests/test_dedicated_profile_offline.sh` PASS**, including default and explicitly selected legacy, dedicated final overlay and health target, rejected unknown profile, static source-line port and DB-password guards. Observed **`bash tests/test_dedicated_env_security.sh` PASS** in full with mocked Docker and synthetic environment file. This includes the three new ambient Compose-selector rejection cases plus existing protected path, image, Docker context, raw `docker image inspect`/`buildx`, .env backup/edit, release export, and legacy call tests. No real Compose interpolation, daemon operation, socket verification or tested rollback.

## 2. Discovered test isolation defect and narrow review-branch correction

A second invocation with `COMPOSE_PROJECT_NAME=hostile` already inherited by the outer shell **failed the suite before its intended negative-case checks** because the Step 139 mock-test setup cleared inherited `DOCKER_HOST`/`DOCKER_CONTEXT` but did not clear the new `COMPOSE_*` selectors. This is a **test fixture isolation defect**, not proof of a broken production guard: the guard correctly rejects the ambient selector.

Test-only correction on **the same Step 139 review branch** `review/dedicated-compose-env-guard-2026-10-24`:
- Inserted `unset COMPOSE_PROJECT_NAME COMPOSE_FILE COMPOSE_PROFILES || true` in the test fixture initialization.
- Review branch **new verified commit `dd86e8cff71d848e4f88383d7481a2f78b8545da`**, `tests/test_dedicated_env_security.sh` blob **`150f72cffc9d1db8ea2338284b5d58cad870c7df`**, exactly matching independent local Git hash of tested bytes. The source `scripts/modules/docker.sh` remains `d6b0647e36653579909004c75e2ffffaeace98d8`.
- Re-ran the **complete** changed test script locally, both with a clean environment and with `COMPOSE_PROJECT_NAME`, `COMPOSE_FILE`, `COMPOSE_PROFILES`, `DOCKER_HOST`, and `DOCKER_CONTEXT` all deliberately inherited: **both runs PASS**. The PR #27 smoke script also PASS. No source production-control change in this commit.

## 3. Compatibility / security finding: protected --env-file is a separate selector source

Source review: `verify_dedicated_env_file()` validates absolute path, owner/mode, symlink status, immediate parent mode and lack of a checkout `.env`, **not the contents**. `ccpc_compose()` rejects ambient shell `COMPOSE_PROJECT_NAME`, `COMPOSE_FILE`, and `COMPOSE_PROFILES` but calls `docker compose --env-file "$CCPC_VERIFIED_ENV_FILE" ...`. The reviewed dedicated-credentials document allows `DB_PASSWORD` plus later reviewed non-secret interpolation entries in that file.

A **synthetic mock-only reproduction** created a private fake external env file containing `DB_PASSWORD=NOT_A_REAL_PASSWORD` and `COMPOSE_PROJECT_NAME=anotherproject`. Existing `verify_dedicated_env_file` and mocked `ccpc_compose config --quiet` **both accepted the file**. This establishes **the wrapper does not reject the key in file contents**, not that actual Compose selected or started the unintended project.

Docker official documentation describes `COMPOSE_PROJECT_NAME` as an input for resource/project identity, `COMPOSE_PROFILES` for service selection, and describes pre-defined Compose variables loaded from environment files; the documented precedence of explicit `-f` versus `COMPOSE_FILE` matters. References:
- [Docker Compose pre-defined environment variables](https://docs.docker.com/compose/how-tos/environment-variables/envvars/)
- [Docker Compose project-name precedence](https://docs.docker.com/compose/how-tos/project-name/)
- [Docker Compose variable interpolation / --env-file](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation)
- [Docker Compose CLI -f/-p flag behavior](https://docs.docker.com/reference/cli/docker/compose/)

**Implication:** The Step 139 ambient-only guards are **defense-in-depth**, not an attestation of effective project identity. An approved remediation must use a **reviewed and pinned Compose project name** (for example, explicit `-p` after verifying what is actually intended on `ccpcerp-prod`), a controlled allowlist of credential-file interpolation keys, or both. Do NOT infer the project name from an old working-directory assumption and apply it to production. Rootless/nondefault Docker context compatibility and all ancestor directory ownership remain separate concerns. Do not automatically broaden the review patch to unspecified host-specific identities.

## 4. Stack-safe disposition and next engineering gate

- **PR #27** `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, **PR #29** `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`, **PR #30** `fd751ab7c39c252e469e1d59d6ebbb1408381061` remain original draft review heads: no parent-history rewriting or promotion.
- Step 138 consolidation `08d725255263ebff9216e7e3b89727b4bf72f792` remains unchanged; Step 139 review branch is test-fixture-corrected at `dd86e8cf...`.
- **Next possible GitHub-only review:** determine an explicit, non-secret Compose project identity policy and reject any unreviewed `COMPOSE_*` control keys in the protected `--env-file`, with red/green offline tests. Do not choose/pin host identity without reading reviewed documentation and obtaining later read-only actual-host evidence. Keep legacy path unchanged. No need for a new paid CI runner or VM for this source-level planning.
- **Blocked until separately approved:** true Compose v2 rendered config, local Docker socket/runtime identity verification, actual dedicated server compatibility, persistent-volume/project identities, TLS, backup consistency, isolated full restore and cutover authorization. Prior Step 133 135/135 Python mock/static tests **not rerun** in Step 140. Step 136 G0 PARTIAL / G2 unexecuted; backup_ready remains FALSE.
