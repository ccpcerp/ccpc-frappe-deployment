# Dedicated production host — external credentials review

**Status: review-only proposal. NOT approved for rollout or for production deployment.**
This procedure applies exclusively to the **new, separately prepared** `ccpcerp-prod` host when
`CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls` is deliberately selected. It does not change
the current shared `ccpcerpserver` PRODUCTION/DEVELOPMENT deployment.

## Why the existing .env mechanism cannot be reused

The current legacy workflow backs up the **entire** checkout `.env` with
`scripts/modules/env.sh:backup_env` before updating `CUSTOM_TAG`. A checkout `.env`
containing `DB_PASSWORD` would therefore be duplicated as a secret-bearing backup.
Adding `.env` to `.gitignore` does **not** protect those copies, other local users,
machine backups, accidental uploads, or Docker metadata.

This candidate changes the **dedicated opt-in path only**:

- Docker Compose receives `--env-file "$CCPC_DEDICATED_ENV_FILE"` for the dedicated profile.
- That variable must reference an **existing absolute path outside the Git checkout**.
- The file must be a readable regular file (not a symlink), owned by the invoking user,
  with mode **0600**, and its immediate directory must be owned by that user with **0700**.
- Checkout `.env` is rejected in dedicated mode, as is an ambient `DB_PASSWORD`.
- The dedicated release process supplies the image `CUSTOM_TAG` only in the
  deployment process environment and **skips** legacy `backup_env` / `update_env`.
  Separate manual Compose commands must supply an explicit, reviewed `CUSTOM_TAG`;
  there is no persisted implicit image tag.
- Legacy `legacy-lan` still uses its original `.env` backup, edit and Compose argument
  paths; **do not apply this review branch to the old host**.
- On a dedicated deployment failure, the existing helper emits a warning and does not
  try to restore a non-existent `.env` backup. This is **not** a container or
  database rollback. Migrations and live recovery require separate safeguards.

## Proposed credential storage (do not create yet)

A future separately approved provisioning procedure could choose a private location such as
`/home/ccpcadmin/.config/ccpc-prod/compose.env`, with the parent directory **0700** and
the file **0600** owned by `ccpcadmin`. This is an *example path only*.
The protected file would supply at minimum `DB_PASSWORD` and any later reviewed
non-secret Compose interpolation variables. Avoid `CUSTOM_TAG` in the protected file:
the reviewed release tag is supplied explicitly at invocation.

The operator must generate the password locally with a secure method that does not
expose it in Bash history, process arguments, terminal output, GitHub, chat, logs, or
interpolated `docker compose config`. Never include real credentials in this document.
Keep a protected, access-controlled off-host recovery copy with an independently
reviewed rotation and restoration plan. Do not rely on Git ignore or the host's local
disk alone as recoverability.

`CCPC_DEDICATED_ENV_FILE` is a **path**, not the password. Exporting the path for an
approved session does not automatically create the file or authorize deployment.
A real `docker compose config` without `--quiet` exposes interpolated secrets;
use tightly controlled, non-printing validation only when approved. With Compose's
environment-based MariaDB password model, privileged Docker API access / container
metadata can still expose the credential. This patch is **not** Docker Secrets,
end-to-end secret isolation, or a credential vault.

## Review checks, not deployment authorization

Run the repository's offline `tests/test_dedicated_env_security.sh` in an isolated,
credential-free test checkout. Its Docker command is mocked. It verifies safe fixture
acceptance, insecure mode/symlink/path rejection, an explicit image tag, prevention
of dedicated `.env` backup/edit, failure handling, and unchanged legacy Compose
invocation. Static test success is **not** a database-integrated or live Docker test.

Before any rollout: independent code review, a verified Git commit and PR, a
separately approved new-host checkout update, a secure secret provisioning plan,
correct custom image and version, project and persistent-volume separation,
backup/restore validation, HTTPS/TLS, firewall/actual Docker network observations,
failure and rollback review, and **separate explicit approval** for starting
containers, restoring data, or cutover. No modifications to existing live
PRODUCTION or DEVELOPMENT are authorized by this review.

The reviewed `dedicated-pre-tls` profile and its source branch are still a
pre-TLS **draft candidate**, not a released production stack.
