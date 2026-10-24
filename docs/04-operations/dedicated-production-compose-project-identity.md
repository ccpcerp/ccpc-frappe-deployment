# Dedicated production Docker Compose project identity — review candidate only

**2026-10-25 — GitHub review branch, NOT ACTIVE PRODUCTION CONFIGURATION.**
**No deployment, migration, backup, restore, live Docker inspection or cutover authorized.**

## Candidate project namespace

The separate CCPC dedicated production host is called `ccpcerp-prod`; that
**hostname is not a validated Compose project name**. The project name used
by the current pre-TLS Compose commands is not yet established from the
dedicated host's Docker inventory.

For source-level review, the new **proposed, unapproved** Compose project
name is `ccpc_prod_erpnext`. It is deliberately distinct from the older
`frappe_docker` / `frappe_docker_devcontainer` project identities in
historical CCPC records. This proposal **does not prove** the new name is unused,
correct for `ccpcerp-prod`, or accepted in a signed deployment manifest.
Do not run the new review branch against any CCPC host until those facts are
independently verified and the operator explicitly approves the value.

## Proposed behavior (source-only)

The `dedicated-pre-tls` path in `scripts/modules/docker.sh` passes
`docker compose --project-name ccpc_prod_erpnext` **before** the reviewed
protected `--env-file` and the checked-in list of Compose `-f` files.

- The `-p` / `--project-name` CLI option has highest precedence over
  `COMPOSE_PROJECT_NAME`, top-level `name:` and working-directory defaults
  (Docker documented precedence).
- The wrapper rejects incoming project-name switches in additional arguments
  (`-p`, `-p...`, `--project-name`, `--project-name=...`).
- Previous review stages reject ambient `COMPOSE_PROJECT_NAME`,
  `COMPOSE_FILE`, `COMPOSE_PROFILES` and limit the protected
  `--env-file` to `DB_PASSWORD`. This does **not** prove the trust of
  other ambient variables, Docker CLI executable, running daemon, or actual
  Compose project resources.
- The legacy `legacy-lan` invocation is not modified.

This literal is a **review proposal only**. Using the candidate as a fixed
value is safe to study offline, but its eventual operational value must
be approved using real host evidence; simply obtaining a mocked test PASS
cannot authorize starting any container.

## Naming and volume acceptance — prerequisites to promotion

1. On a **later separately authorized read-only check of the new host only**,
   confirm hostname, Docker context/Unix socket, current checked-out Git
   branch and dirty state, Docker Compose v2 version, existing project labels
   and named volumes. Stop on any unexpected running/stopped resources.
2. Confirm proposed `ccpc_prod_erpnext` does not collide with an existing
   project, foreign volumes, site or unrelated resources. Do **not** delete,
   rename, stop, prune, recreate or adopt any unexpected resource.
3. Independently approve the exact project string and bind it to the reviewed
   release-manifest `compose_project` field. Compare expected resources:
   `ccpc_prod_erpnext_sites`, `ccpc_prod_erpnext_db-data`,
   `ccpc_prod_erpnext_logs`; do not interpret filename-based
   expectations as actual Docker inspections.
4. On an authorized, synthetic/offline Docker Compose v2 CLI, render all
   five exact source files in order, check `--project-name` precedence,
   log only sanitized service/project/volume/port metadata, assert local-only
   `127.0.0.1:8080` publication, and reject unexpected or external mounts.
   Do not dump interpolated `DB_PASSWORD` into logs or GitHub.
5. Before deployment, separately test on an authorized dedicated-host
   runtime: release image IDs and Compose config hashes, backend/db
   container and volume labels, site identity, migration rollback,
   HTTPS/TLS gateway, off-host backups, and isolated **successful restore**.
   No release gate is currently satisfied by this proposed name.

This is intentionally an explicit approval gate, not an instruction to
change any current host or older production/DEVELOPMENT workload.

## Evidence and limitations

Review branch: `review/dedicated-compose-project-pin-2026-10-25`.
The exact current `ccpc_compose()` function excerpt was independently matched
to GitHub source by 32-bit FNV hash `10bf4368` (1496 ASCII bytes at checkpoint)
and `bash -n` passed. With mocked `verify_dedicated_env_file`,
`verify_dedicated_local_docker_target`, and `docker` but an actual
`exit 1`-style error helper, observed one pinned-command PASS, four
caller-option rejection PASS, three ambient selector rejection PASS and
legacy command preservation PASS. **This was an exact function-excerpt
test, not a byte-for-byte execution of the whole repository Bash suite,
real Compose CLI, or live Docker.** An initial test double incorrectly made
`error()` return instead of exit; corrected to match the actual
`scripts/lib.sh` `error()` contract before final verification. An
explicit `return 1` was also added to the new project-option rejection.

Sources: [Docker project-name precedence](https://docs.docker.com/compose/how-tos/project-name/),
[Docker Compose CLI](https://docs.docker.com/reference/cli/docker/compose/),
and [Docker predefined environment settings](https://docs.docker.com/compose/how-tos/environment-variables/envvars/).

**Status: REVIEW ONLY. Full Bash regression, real Compose v2 render,
new-host compatibility, signed release linkage, and restore test all pending.**
