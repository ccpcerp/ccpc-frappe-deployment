# Step 143 — Exact-source Bash regression and Compose caller-option review

**2026-10-25 (Asia/Manila) | OWNER-APPROVED GITHUB-ONLY WORK | REVIEW CANDIDATE, NOT DEPLOYED.**

This checkpoint continues the exact Step 142 review branch and closes the
previous **full Bash regression pending** item. No CCPC host, office PC,
DEVELOPMENT, PRODUCTION, Synology NAS, production secret, container/daemon,
image build/pull, real Compose CLI, backup/restore, migration, PR merge, or
paid GitHub Actions run was used.

## Frozen source and observed complete offline tests

Pinned Step 142 candidate at outset:
`review/dedicated-compose-project-pin-2026-10-25`
HEAD **`dfb84fafff73c2eccecd01a48698779b334a5cb5`**.
The original stacked draft PRs #27/#29/#30 were not moved.

An existing **disposable local fixture** from the previous Step 139 offline
testing contained source files already byte-identical to GitHub. It was copied
into a new disposable `git init` fixture; the exact intervening Step 141
allowlist and Step 142 project-pin changes were reconstructed from the
current GitHub commit comparison and **each resulting `git hash-object`
SHA-1 independently matched its source GitHub blob**:

| Exact GitHub review source | Git blob SHA-1 |
| --- | --- |
| `scripts/config.sh` | `32614da1044c768bd67dcb9b9491e7c48ff2653a` |
| `scripts/lib.sh` | `7f83828f99273445b6b95d171fb9f9b4862c0587` |
| `scripts/modules/docker.sh` | `85f6e19d8c3642caafca5213bfe3ddca11779a9c` |
| `scripts/modules/env.sh` | `38a6fdef14abc9e61ae8425ab606dce6201290c1` |
| `scripts/modules/deployment.sh` | `ab862074235f174bf5de042ea7c6562965a34243` |
| `overrides/compose.dedicated-pre-tls.yaml` | `14fd89a3c2371104f464964137483de9f4a35861` |
| `tests/test_dedicated_profile_offline.sh` | `dd7a400b42574a23d1a2c118bbbdf3468f0eb51e` |
| `tests/test_dedicated_env_security.sh` | `27bd2933eca70e3ee2e5eeddd888aade7a339329` |

**Actual local execution:**
- `bash -n` **PASS for all seven Bash scripts**.
- `bash tests/test_dedicated_profile_offline.sh` **PASS**.
- `bash tests/test_dedicated_env_security.sh` **PASS** in full with a
  synthetic `DB_PASSWORD` and Bash-mocked `docker()`. Every defined
  rejection returned expected failure; unmodified legacy behavior PASS.
- These checks did **not** use Docker/Compose, an ERPNext database or the
  complete repository checkout; they used the eight exact source blobs and
  other existing non-tested fixture files only as test scaffolding.

## Discovered caller-option bypass (mock-red), correction and full retest

The Step 142 `ccpc_compose()` rejects incoming `-p` and
`--project-name` flags, and pins a **UNAPPROVED CANDIDATE**
`ccpc_prod_erpnext` project via `--project-name`. It did **not** reject
other Compose global selectors from the caller. In a **mock-only negative
demonstration** on the pinned Step 142 code, each extra
`--file`, `--env-file`, `--project-directory` and `--profile` flag
reached the mocked `docker()` rather than being stopped. This does **not**
prove the effective behavior of real Compose when flags are placed after a
subcommand; Docker documents the same options as model, environment,
directory and active-service selection controls.

The owner-approved correction was **staged on a NEW review-only branch**
`review/dedicated-compose-cli-selectors-2026-10-25`, forked from Step 142,
verified HEAD **`45e96732269a06a2344091f9ed3ae558b8f45c1c`**.
GitHub comparison: 2 commits ahead, zero behind; **two files only**:

1. `scripts/modules/docker.sh` Git blob
   **`a99bcdb2077f55f5ded118159ad72a90d0a9fd7e`**:
   retained prior dedicated-mode project pin and added fail-closed rejection
   of caller flags `-f`/`-fVALUE`, `--file`/`--file=...`,
   `--env-file`/`--env-file=...`,
   `--project-directory`/`--project-directory=...`,
   `--profile`/`--profile=...`, in addition to
   `-p`/`--project-name`. The conditional
   `legacy-lan` path remained unchanged.
2. `tests/test_dedicated_env_security.sh` Git blob
   **`15ab0f9d1c1ea634bbc9f17efe3c5aa7dee628a6`**:
   ten new `expect_rejected` cases for both split and joined flag forms,
   including some following the subcommand; existing tests retained.

**Independent exact-source new-branch retest:** reconstructed both new source
files in a separate temporary fixture from Step 142's byte-verified eight
files, then checked **all eight final Git blob IDs** against connected GitHub.
Observed:
- 8/8 blob identities **PASS**.
- `bash -n` 7/7 scripts **PASS**.
- Complete profile Bash script **PASS**.
- Complete security Bash script **PASS** with five deliberately inherited
  `DOCKER_*` / `COMPOSE_*` variables (the test sanitizes its own fixture).
- All ten new selector-flag rejection messages observed **PASS**, along with
  all previous protected-env, Docker context/host, image build/inspect,
  caller-project override, deployment and legacy-path checks.

**Important test limitation:** the fake `docker()` verifies the expected
command prefix and other mocked constraints; this is **not** proof of real
Compose v2 flag parsing, service/mount/port isolation, process identity,
database recovery, or production readiness. No source test suite other than
the two mentioned Bash scripts was rerun in this step, including Step 133's
135 Python synthetic regressions. ShellCheck/pre-commit were not run.

## Operational compatibility and remaining risks

- The **literal project name `ccpc_prod_erpnext` remains a proposal only**.
  The dedicated host's actual current Compose projects/volumes have not been
  inspected; resource collision, release-manifest `compose_project`
  approval and exact site/database/log volume identities are still pending.
- The new flag restriction deliberately refuses ad hoc extra config/env
  files, working-directory and profile arguments, even if an operator
  intended them for a future workflow. Before adoption, review every legitimate
  invocation; extend the checked-in policy deliberately rather than bypass it.
- The current ambient restrictions cover
  `COMPOSE_PROJECT_NAME/COMPOSE_FILE/COMPOSE_PROFILES`, **not every possible
  `COMPOSE_*` environment control** (e.g. `COMPOSE_REMOVE_ORPHANS`).
  Approved caller source/array provenance, trusted working directory,
  real socket/daemon, Compose v2 `!override` semantics and source/volume
  custody remain separate controls to review. Do not assume this two-file
  patch completely closes unintended Compose side effects.
- As before, the real deployment must be held until actual dedicated-host
  inventory and Compose render, TLS and independent **restorable backup**
  are verified under separate, explicit approvals. Advanced PR #30
  `backup_ready=False` remains deliberately locked.

**Next practical step:** decide the candidate project string using a
separately approved read-only inventory **on the new host only**, or continue
the minimal GitHub-only review of remaining `COMPOSE_*` controls. Do not
turn this into a new paid lab/CI or automatically merge the stacked PRs.

## GitHub and Docker sources

- Branch and blob proofs: connected GitHub PR branch comparison and
  `git hash-object` of reconstructed exact source.
- [Docker Compose CLI flags and merge order](https://docs.docker.com/reference/cli/docker/compose/)
- [Docker predefined environment controls](https://docs.docker.com/compose/how-tos/environment-variables/envvars/)
- [Step 142 project identity candidate](DEDICATED-PROD-STEP142-COMPOSE-PROJECT-PIN-REVIEW-2026-10-25.md)

**End state: staged source + exact Bash test PASS; no PR merge or PROD change.**
