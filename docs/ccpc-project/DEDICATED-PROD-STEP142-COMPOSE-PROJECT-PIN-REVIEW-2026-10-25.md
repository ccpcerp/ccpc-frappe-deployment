# Step 142 — Dedicated Compose project-name pin, offline review only

**Date:** 2026-10-25 (Asia/Manila). **Owner approval:** continue the Step 141
GitHub-only project-identity policy/design and offline testing. **Status:
REVIEW CANDIDATE STAGED; NOT AN APPROVED HOST IDENTITY OR DEPLOYMENT.**
No CCPC host, VM, NAS, production/development database, secrets, paid
GitHub Actions, Docker Engine, real Compose CLI, image build, migration,
restore, PR merge or cutover involved.

## Verified branch and scope

- Parent: Step 141 review HEAD `284f8b0b14cc823b93ccaf36152a524798b9705e`.
- New: `review/dedicated-compose-project-pin-2026-10-25`,
  **verified HEAD `dfb84fafff73c2eccecd01a48698779b334a5cb5`**.
- GitHub comparison: **7 commits ahead / 0 behind** parent (includes
  successive focused edits); **only 3 final changed files**:
  - `scripts/modules/docker.sh`: explicit candidate `--project-name`
    plus caller project flag rejection.
  - `tests/test_dedicated_env_security.sh`: Docker mock checks exact
    project-flag argv and four override-flag negative cases.
  - `docs/04-operations/dedicated-production-compose-project-identity.md`:
    clearly marked unapproved policy and exact acceptance steps.
- Original PR #27 `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`,
  #29 `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`,
  #30 `fd751ab7c39c252e469e1d59d6ebbb1408381061`
  independently refetched: **OPEN/DRAFT/UNCHANGED/UNMERGED**.

## Why a new project pin is proposed

GitHub's original dedicated scripts did not choose a fixed Compose project
name. Existing `dedicated_backup_policy.py` validates a signed-release
manifest field `compose_project` against safe syntax and expected named
volume suffixes; it does **not** independently select the Compose project
at deployment time. The new `ccpcerp-prod` hostname does not establish
the live Docker Compose project identity.

Docker documents `-p` / `--project-name` as highest precedence over
`COMPOSE_PROJECT_NAME`, top-level `name:` and directory defaults.
A source-only candidate name `ccpc_prod_erpnext` is proposed, **not
asserted to be the actual or approved host project**.

The dedicated-only `ccpc_compose()` now passes:
`docker compose --project-name ccpc_prod_erpnext --env-file <protected-path>
-f compose.yaml ... -f overrides/compose.dedicated-pre-tls.yaml <subcommand>`.
The shell-selected literal is fixed inside the review-only wrapper. Incoming
`-p`, `-pOTHER`, `--project-name` and `--project-name=OTHER`
subarguments are rejected before reaching Docker. The prior ambient
`COMPOSE_PROJECT_NAME`, `COMPOSE_FILE`, `COMPOSE_PROFILES` rejections
and protected env-file DB_PASSWORD-only allowlist remain staged. Legacy
`legacy-lan` command path remains unchanged.

**Project acceptance does NOT follow from the hardcoded value.** Do not
assume the current/new host has no name collision or compatible resource
layout, or that a release manifest/signature has independently approved it.

## Tests actually performed (not full repository validation)

1. Retrieved the exact GitHub `ccpc_compose()` source excerpt (1496 ASCII
   bytes), compared local reconstructed bytes against source using FNV-1a
   32-bit value `10bf4368`, and ran `bash -n` successfully.
2. Used an independent **offline Bash function-excerpt fixture**, with
   mocked `verify_dedicated_env_file()`,
   `verify_dedicated_local_docker_target()` and `docker()`; modeled the
   real `scripts/lib.sh` `error()` contract as `exit 1`.
   Observed:
   - **PASS:** valid dedicated `config --quiet` invokes the mock
     `docker compose` with the exact proposed `--project-name`,
     protected `--env-file` and source-order `-f` arguments.
   - **PASS:** four caller project-name override forms rejected.
   - **PASS:** three ambient Compose selector variables rejected.
   - **PASS:** old legacy invocation preserved without any project pin.
3. During an initial test harness the mock `error()` returned rather than
   exited, which is **not** the real repository helper's contract. This
   fixture limitation was corrected. The new override branch also explicitly
   `return 1` after its error call as a second fail-closed guard.
   Final excerpt-level checks passed. No statement that the entire repo
   Bash tests passed.
4. GitHub comparison and changed-file identities independently verified.
   **Not executed:** full `tests/test_dedicated_env_security.sh` from a
   byte-complete checkout, Step 133's historical 135 Python mock tests,
   `docker compose config` v2, real image/runtime/volume labels,
   dedicated host inventories, signed manifest trust, HTTPS, backup or
   isolated restore.

## Required review gates before code promotion or cutover

- **Exact name decision, not derivation:** independently inspect on
  `ccpcerp-prod` which projects/volumes already exist before accepting
  `ccpc_prod_erpnext`, rejecting collisions. The proposed name must be
  separately approved by the owner and linked to the intended reviewed
  release-manifest `compose_project`; names from NAS accounts, hostname
  or working directory are not proof.
- **Actual Compose v2 effective rendering:** source-pinned five-file model,
  synthetic protected env file, final project name, named
  `<project>_sites`, `<project>_db-data`, `<project>_logs`, and
  loopback-only frontend bindings, without printing credentials.
- **Deployment input audit:** verify other raw Docker/Compose call paths,
  duplicate `-f`/profile/project-directory options, local Docker
  socket/host identity, symlink/race protections and volume collisions.
  The mock only validates the supplied CLI argument order.
- **Release/recovery:** real dedicated host image/Compose identity and
  provenance, tests on approved DEVELOPMENT/synthetic environments,
  TLS/firewall, safe rollback and isolated successful restore remain
  separately required. `backup_ready=False` remains unchanged.

**Next GitHub-only step:** run the complete exact-source Bash regressions
against this review branch, review any remaining caller-supplied Compose
options, and decide whether this candidate name can be proposed for a
later operator-approved, read-only new-host inventory. **No PR promotion,
production host commands or additional lab provisioning in Step 142.**

Official reference: [Docker project-name precedence](https://docs.docker.com/compose/how-tos/project-name/).
