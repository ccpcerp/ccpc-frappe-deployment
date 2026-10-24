# Step 139 — Dedicated Compose selector hardening (staged review, not release)

**2026-10-24, owner-approved GitHub-only continuation.** The current authoritative handoff already records Step 138. This Step 139 review **does not redo or override Step 138**. No DEVELOPMENT/PRODUCTION/NAS/VM operations, secret use, CI run, Docker invocation, image pull/build, PR merge or host deployment.

## Baseline and new review-only branch

- Step 138 source and combined mock Bash testing baseline: `review/dedicated-prod-stack-consolidation-2026-10-24` at `08d725255263ebff9216e7e3b89727b4bf72f792`, **unchanged**.
- **New branch:** `review/dedicated-compose-env-guard-2026-10-24`, forked from the exact Step 138 consolidation commit. **Verified head:** `7735ede2db25cd80918ef118a57a5f5a7a5cc295`.
- GitHub comparison: **2 commits ahead, 0 behind; two modified files only**:
  - `scripts/modules/docker.sh`, blob `d6b0647e36653579909004c75e2ffffaeace98d8`: six added lines.
  - `tests/test_dedicated_env_security.sh`, blob `1e70822d8003c74a59d588c700adc6e908a8f4f8`: four added lines.
- Original PR #27/#29/#30 heads remain frozen `0bf8c6a2` / `bd92ade7` / `fd751ab7`. **Do not transfer to their branches without a separate reviewed integration plan.**

## Finding and minimal correction

The Stage 138 guarded `ccpc_compose()` checks the external protected env file, explicit image/tag, `DOCKER_HOST`, `DOCKER_CONTEXT` and local default Unix socket. It did **not** guard three inherited Docker Compose environment selectors. An inherited `COMPOSE_PROJECT_NAME` could select a different Compose project name and resource namespace; `COMPOSE_FILE` and `COMPOSE_PROFILES` could change model/service selection under circumstances not covered by the existing source checks. Exact impact depends on Compose precedence and is **not** independently reproduced with Compose CLI.

This review adds to the dedicated-only `ccpc_compose()` path a **fail-closed check for presence**, not merely non-empty value, of:

- `COMPOSE_PROJECT_NAME`
- `COMPOSE_FILE`
- `COMPOSE_PROFILES`

The legacy `legacy-lan` Compose invocation remains byte-for-byte unchanged. Three extra `expect_rejected` mock cases were added to the existing dedicated Bash test to cover each variable.

**Verification performed:** source file re-fetch; check each of the three Bash presence guards and matching negative test cases exist; GitHub compare to the pinned Step 138 base shows only the two expected file edits; the legacy Compose branch is unchanged. **Not performed:** complete Bash test execution, ShellCheck, Docker Compose v2 config/variable precedence, integration tests or actual environment compatibility. Therefore this is a **static review patch**, not a reported passing test or production-ready correction.

## Compatibility limitations and remaining risk

- If an authorized dedicated deployment intentionally sets `COMPOSE_PROJECT_NAME`, `COMPOSE_FILE`, or `COMPOSE_PROFILES` in the shell, the new code will stop; first review the intended project identity and whether any explicitly selected Compose variable is operationally required.
- These guards apply to ambient shell variables entering `ccpc_compose()`; they **do not** prove whether protected `--env-file` contents, project names from top-level Compose config, or Docker daemon metadata could alter resource identity. Do not treat them as complete production-target authentication.
- Raw `docker buildx` and `docker image inspect` already have the separately staged Step 138 local target guard. Other Docker/Compose entrypoints must still be reviewed before promotion.
- A coherent acceptance test requires the exact five-file Compose v2 rendering, validated effective project and volumes, correct host, and real synthetic restore. The Step 136 G0 isolation remains partial; G2 not executed.

**Next:** run the complete byte-matched Bash suite in a disposable non-network fixture and inspect whether the hardened behavior is compatible with the actual dedicated host configuration, without running production Docker commands. If compatible, decide how to safely incorporate Stage 138/139 patches into the stacked PRs without rewriting parent history. Production unchanged; draft PRs remain unmerged.
