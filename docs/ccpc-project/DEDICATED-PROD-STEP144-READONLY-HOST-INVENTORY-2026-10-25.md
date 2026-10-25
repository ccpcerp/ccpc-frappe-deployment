# Step 144 — Dedicated production host project/volume metadata-only inspection preparation

## Later owner-executed, read-only SSH hostname verification (2026-10-25)

**PASS — owner-provided Windows OpenSSH `-vvv` terminal output, not a ChatGPT-originated host connection:** The owner ran a one-shot SSH remote command using their existing protected Ed25519 private key for `ccpcadmin@192.168.50.186` with `hostnamectl --static`. After a successful local `ssh-keygen -y -f <private-key> > $null` check (Windows `$LASTEXITCODE=0`), the SSH diagnostic command showed successful remote session request, **exact stdout `ccpcerp-prod`**, and **`debug1: Exit status 0`**. Earlier debug showed the server offering/accepting the corresponding SSH public key, and the host key matched the client's saved known-hosts entry. The connection closing after the remote command is normal for noninteractive SSH; the earlier interactive-shell closure cause remains unverified. The key passphrase/private key were never supplied to ChatGPT.

**Scope:** This verifies the *reported static hostname and successful one-shot SSH execution* at the observed time, not the machine's stronger provenance beyond SSH host-key continuity, current Docker socket/context, exact Compose project ID, running/stopped container labels, named Docker volumes, networks, DNS/TLS, backups or production readiness. **The full dedicated Docker metadata inventory helper has NOT been transferred or run.** Next approved read-only incremental check: on the same trusted Windows terminal, invoke `docker context show` as a single remote SSH command with the existing private-key path; expect `default`, otherwise STOP. Then independently check local Docker endpoint, and only later inspect names/labels. Do not run `docker compose up/down/config`, use sudo, change files, open remote Docker endpoint, run cleanup or deploy.

**2026-10-25 | Owner-approved read-only inventory scope, GitHub-side preparation completed; ACTUAL HOST INVENTORY NOT PERFORMED.** This review does not merge PRs, approve the proposed Compose project name, transfer or execute anything on a CCPC host, or modify production/development/NAS/VM. GitHub connection has repository access but no SSH/host-terminal capability; the actual server state **cannot** be established from committed GitHub documents.

## Verified baseline

- Follow current [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) and Step 143 record; `CURRENT-HANDOFF.md` is authoritative for ongoing status.
- Step 143 review branch `review/dedicated-compose-cli-selectors-2026-10-25` remained at `45e96732269a06a2344091f9ed3ae558b8f45c1c`.
- New review-only branch `review/dedicated-host-readonly-inventory-2026-10-25` created **from that exact head**, final verified HEAD `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e`.
- Branch comparison: 1 commit ahead, 0 behind, **only one newly added file**, `scripts/review_dedicated_host_inventory.sh`; Git blob SHA-1 **`df2f5ecc69141de9f6a9dc987acfcef1a22315ca`**. Existing Step 143 scripts, 3 stacked draft PR heads and production services untouched.
- Script was reconstructed locally from its exact committed bytes, verified with `git hash-object` SHA-1 matching the GitHub blob and `bash -n` PASS.
- Ten **offline Bash-mocked** safety scenarios PASS: allowed local read-only metadata query, wrong hostname, wrong login account, `DOCKER_HOST`, `DOCKER_CONTEXT`, `DOCKER_CONFIG`, nondefault context, wrong endpoint, missing Compose version (informational only), and denied container inventory. Tests intercepted all Docker invocations and confirmed only the six permitted read-only method families. **No live Docker daemon or server was contacted.**

## Script behavior and safety boundary

Before making Docker queries, it requires:

1. `id -un` exactly `ccpcadmin` (no `sudo` or escalation).
2. `hostnamectl --static` exactly `ccpcerp-prod` (not shared `ccpcerpserver`).
3. Unset `DOCKER_HOST`, `DOCKER_CONTEXT` and `DOCKER_CONFIG` (no remote/redirected endpoints).
4. Docker CLI available; `docker context show` exactly `default`; endpoint string from `docker context inspect default` exactly `unix:///var/run/docker.sock`.

Only after those guards pass, output:

- `docker compose version --short` (informational; failure does not authorize install).
- `docker ps -a --format` showing **container names and Compose project/service labels only**.
- `docker volume ls --format` **volume names only**.
- `docker network ls --format` **network names only**.

No `docker inspect` for containers, no environment dumps/config interpolation, site/database paths, secrets, Docker socket mounting, `docker compose config/up/down`, image build/pull, backup/restore, `sudo`, DNS/firewall changes, file mutation or removal. A local Unix endpoint string is a narrow safety check and **not cryptographic proof of the Docker daemon's identity**, and the Docker socket itself is privileged. The command assumes the operator trusts the installed Docker CLI, Linux shell and host; these are not proved by mocks.

## Findings from source review, not host observation

GitHub's current staging pins **candidate-only** Compose project name `ccpc_prod_erpnext` in dedicated `ccpc_compose()`; this is **NOT** an approved actual project on `ccpcerp-prod`. Expected *possible* project-scoped volume names if later approved: `ccpc_prod_erpnext_sites`, `ccpc_prod_erpnext_db-data`, `ccpc_prod_erpnext_logs`. Only an actual host inventory can identify collisions, existing resources or an older stack.

Docker documents an additional relevant inherited control: `COMPOSE_REMOVE_ORPHANS=true` can remove orphaned containers during `up`. The currently staged guards reject `COMPOSE_PROJECT_NAME`, `COMPOSE_FILE`, `COMPOSE_PROFILES`, and caller CLI model selectors, **not all ambient Compose knobs**. This is a **separate code hardening/design candidate**, not proof that the variable is set on either host, and the read-only inventory script does not invoke `up`.

The Stage 143 source-level tests PASS, but they do not prove the safe effective Compose project or backup/recovery. The signed release manifest `compose_project` and existing runtime verifier must independently agree with the actual approved project and expected volumes.

## Operator execution gate (NO forced phone copy/paste)

The project owner reported that on-phone remote PuTTY pasting is impractical. **Do not demand executing a large script from the phone** or running unreviewed `curl|bash`. When a trustworthy SSH terminal to the *new host* is convenient, the **smallest first read-only step** is:

```bash
hostnamectl --static
```

Expected `ccpcerp-prod`; if different, **STOP** without accessing Docker. After verifying hostname, authorize/choose a safe way to use the exact committed GitHub script, **without overwriting checkout work**, or carry out the same fixed metadata queries in a reviewed operator procedure. Script transfer and execution must match the pinned commit/blob; do not blindly clone/pull/run from a moving branch or copy any private key/credential. No automatic background action, billing or schedule.

When an approved read-only metadata inventory becomes available, compare *reported* container Compose labels and all volume/network names against the **candidate** `ccpc_prod_erpnext` namespace. A collision/previously populated volume is a **STOP** for code promotion and requires a separately reviewed disposition; never `docker rm`, `volume rm`, prune, rename or adopt unknown resources. An empty inventory also **does not** authorize creating/recreating a stack, imply future name ownership or demonstrate data recovery.

## End state / next decision

- **GitHub safe script prepared + mocked tests PASS; LIVE new-host Docker inventory PENDING.**
- The review-only naming candidate is **not** approved, and PRs #27/#29/#30 remain open/draft/unmerged, with unchanged source heads.
- Before any production deployment/merger: review the candidate project name and release-manifest/volume identity with real inventory, resolve inherited `COMPOSE_REMOVE_ORPHANS` and similar selectors, run real Compose v2 source-pinned config in an approved environment, review TLS/credential/recovery, and complete **isolated successful restore**.
- Neither old `ccpcerpserver` PRODUCTION/DEVELOPMENT nor Synology backup shares were contacted or changed in this step.

Source for remaining Compose variable risk: [Docker predefined Compose environment variables](https://docs.docker.com/compose/how-tos/environment-variables/envvars/).
