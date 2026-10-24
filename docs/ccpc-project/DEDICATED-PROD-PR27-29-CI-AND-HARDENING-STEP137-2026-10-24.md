# Step 137 — PR #27 CI triage and staged PR #27/#29 review corrections (GitHub-only)

**2026-10-24, owner-approved mobile GitHub-only follow-up.** No host, VM, DEVELOPMENT, PRODUCTION, Synology, credentials or database accessed. No Docker Engine, Compose, full Bash suite, image build, paid GitHub Actions job, workflow re-run, PR merge or production change. **Both original PRs and their PR #30 child are UNCHANGED.** Corrections have been **staged only on two separately named review branches** for source review.

## 1. GitHub CI — what failed and what is NOT established

GitHub Actions runs on the exact open draft PR #27 head `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`:

| Workflow run | Name | Failed job(s) | GitHub job metadata |
| --- | --- | --- | --- |
| [39875178484](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/39875178484) | Core / Build Develop | Resolve Versions, other build/publish jobs skipped | no steps; `runner_id: 0`, empty runner name |
| [39875178472](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/39875178472) | Lint | lint | no steps; `runner_id: 0`, empty runner name |
| [39875178513](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/39875178513) | Core / Build Stable | v15/v16 Resolve Versions, remaining jobs skipped | no steps; `runner_id: 0` |

GitHub reports **failure before a runner actually executed any job steps** in the available job data. Downloading job logs failed with `NOT_FOUND / BlobNotFound` via the connector. **Root cause unresolved:** do not claim the checked-in code failed lint/build; do not claim billing, account limits, runner allocation, permissions or workflows definitely caused it. The run metadata and inaccessible logs are insufficient to distinguish these.

Source investigation at PR #27:
- `.github/workflows/core-build-develop.yml`, `core-build-stable.yml` and reusable `core-build-test-images.yml` are generalized upstream Frappe Docker image build/test workflows. Modifying `overrides/**` triggers these on pull requests targeting `main`.
- Reusable image test workflow defines an amd64/arm64 build matrix, QEMU/Buildx, image registry and pytest. These **are not** the narrowly scoped CCPC Compose-only safety tests we need.
- `.github/workflows/lint.yml` runs repository-wide pre-commit checks on PRs targeting `main`.
- Do **not** weaken/disable upstream CI merely to hide failures. Do **not** retry paid/minute-consuming runs to diagnose an unallocated runner. Review account runner availability and workflow policy separately when the owner wants CI.

## 2. Review branch A — PR #27 non-network Bash/profile smoke test

**Branch:** `review/pr27-offline-profile-tests-2026-10-24`, forked at exact PR #27 head `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`.
**Verified branch head after edits:** `4c981ef68bcbb4bd2c766d781c2ba09f54f1a3f4`.

One new file: `tests/test_dedicated_profile_offline.sh` (explicitly run with `bash`; non-executable by default). Validates Bash source syntax, default and explicitly selected four-file `legacy-lan` profile, opt-in fifth dedicated overlay **last**, 8080 loopback health check, invalid profile rejection and source-level `!override`, loopback TCP port and nonempty `DB_PASSWORD` expression. **It does not validate Compose v2 semantics, runtime binds or credentials.**

**Local ephemeral smoke execution:** An isolated temporary Git repository was populated with exact GitHub-source `scripts/config.sh` (verified blob SHA `32614da1044c768bd67dcb9b9491e7c48ff2653a`) and PR #27's dedicated overlay (verified blob SHA `9b69b0c7a1d64191a51da5126ddc82498202446f`). `bash -n` and equivalent profile/source smoke harness returned **PASS** on the four/five-file selection, invalid mode and key source-line checks. The entire newly checked-in GitHub test file was **not** independently exercised byte-for-byte as a repository checkout or in GitHub CI; do not describe this as end-to-end CI PASS. The source-level smoke result is a narrow independent reproduction.

## 3. Review branch B — PR #29 dedicated Docker target guard

**Branch:** `review/pr29-local-docker-target-2026-10-24`, forked at exact PR #29 head `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`.
**Verified branch head after edits:** `7ff62b2fed7e1d6ce60f0f9cb30d1b4ee8cd8010`.

Two modified files: `scripts/modules/docker.sh`, `tests/test_dedicated_env_security.sh`.

**Why:** the existing dedicated `ccpc_compose()` verifies protected external env file/name and tag but invokes `docker compose` without checking whether the CLI context might point to a remote/non-CCPC daemon. A shell's `DOCKER_HOST` / `DOCKER_CONTEXT` can retarget Docker to a different daemon.

**Staged mitigation** (`dedicated-pre-tls` only; legacy Docker invocation untouched):
- Reject any inherited `DOCKER_HOST` or `DOCKER_CONTEXT`.
- Query read-only `docker context show`, require `default`.
- Query `docker context inspect default --format '{{.Endpoints.docker.Host}}'`, require `unix:///var/run/docker.sock`.
- Fail closed before `docker compose` if any check cannot run or produces an unexpected value. Suppress raw context error output to avoid unintended disclosure.
- Extend the existing Docker-mocked Bash regression for a valid local socket and five negatives: remote `DOCKER_HOST`, remote `DOCKER_CONTEXT`, nondefault selected context, SSH endpoint, and localhost TCP endpoint.

**Local bounded behavior test:** A minimal Bash harness reproducing the new guard and Docker context mock passed **1 positive + 5 negative** checks, with `bash -n` successful. **Not executed:** the complete exact checked-in `tests/test_dedicated_env_security.sh` against the full linked checkout or real Docker. No claim of actual host/socket provenance, runtime process ownership, Compose project namespace, or deployment acceptance; `unix:///var/run/docker.sock` string alone cannot prove underlying socket or daemon identity.

**Potential compatibility impact to review:** Any legitimate deployment relying on `DOCKER_HOST`, `DOCKER_CONTEXT`, nondefault contexts, rootless Docker or another Unix socket would now deliberately fail. Check the actual `ccpcerp-prod` approved local Docker CLI context **read-only** before adopting the guard. Review inherited `COMPOSE_PROJECT_NAME`, `COMPOSE_FILE`, `COMPOSE_PROFILES`, Docker socket file provenance, real env-file precedence and rollback separately; not implicitly solved by this patch.

## 4. Branch safety, conclusions and next decisions

The official stacked heads were refetched after staging and remain unchanged:
- PR #27: `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`.
- PR #29: `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`.
- PR #30: `fd751ab7c39c252e469e1d59d6ebbb1408381061`.

The **separate review branches have not been merged or moved onto the dependent PR heads**. This deliberately prevents silently changing PR #29's base while PR #30 depends on its reviewed frozen head. Review the two patches and integration ordering before any future base branch changes/rebase, and retest all affected source pins.

**Next GitHub-only action (owner approval when required):** independent review of the PR #29 mock expectations and compatibility with the standalone `ccpcerp-prod` local socket; then obtain an actual complete Bash test execution in a sanitized local/source-verified checkout if feasible, and plan source-pinned real Compose v2 `config` when an authorized runtime is available. Separately decide whether inherited upstream CI on the private fork should be replaced with a low-cost, manual CCPC-targeted workflow, rather than building amd64/arm64 images by default. No paid CI automatically scheduled or triggered here.

**Overall release status:** PR #27/#29/#30 OPEN/DRAFT/UNMERGED, Step 133 135/135 synthetic tests historical only, Step 136 G0 PARTIAL and G2 not executed, new production deployment/restore unverified. PRODUCTION not touched. Never infer production readiness from these staged tests.
