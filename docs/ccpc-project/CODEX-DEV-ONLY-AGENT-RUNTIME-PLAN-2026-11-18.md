# CCPC ERPNext — Codex DEV-only agent runtime: approved boundary and implementation plan

**Date:** 2026-11-18 Asia/Manila
**Status:** Owner approved speed-first autonomous Codex DEVELOPMENT engineering; **plan and GitHub preparation only**. A local agent runtime is **NOT YET installed or connected**. This document is not authorization to recreate containers, change existing site data, retire legacy services, edit PRODUCTION, or copy credentials.

## Owner's current production topology statement

The owner confirms that the **real, currently used PRODUCTION site has moved to the dedicated physical server `ccpcerp-prod`** and that the old PRODUCTION site on `ccpcerpserver` is **no longer in use**. This is a first-hand operator statement, not an independently checked production cutover/audit. Live read-only `docker ps` on `ccpcerpserver` still showed `frappe_docker-db-1`, `frappe_docker-redis-cache-1`, and `frappe_docker-redis-queue-1` running. Treat legacy stacks and their data as protected until a separately approved retirement, regardless of current business traffic. **Do not stop/remove these services to accelerate Codex setup.** The dedicated new production host and its network are always excluded from Codex access.

## Goal and approved agent scope

- **Fastest business result:** Have Codex autonomously implement the CCPC ERPNext same-Company Withdrawal, native Stock Ledger/Expense GL, Department consumption and Finance mapping onboarding work, running real Frappe/MariaDB tests as often as needed.
- Reuse the already published isolated **Codex Cloud `ccpcerp`** environment and GitHub task branch/PR flow for immediate code/test progress. It has no current direct network execution path to the owner's local Docker host.
- Extend to a separately identified **DEV-only local agent execution environment** for integration with DEVELOPMENT when isolation is actually enforced. Allow routine code changes, isolated test fixtures, appropriate DEV-scoped migrations and test/retry workflows after documented backup/rollback controls; preserve original DEVELOPMENT data and existing work. Do not equate this with host-wide root/Docker access.
- Real Finance mapping must come from an authorized named Finance preparer and independent named Finance approver and accurate Company-owned accounting masters. No synthetic approvals, Administrator role bypass, or fabricated Expense/Cost Center decisions on persistent sites.
- **Absolutely out of scope:** `ccpcerp-prod`, new-host SSH, its network/DB, old legacy production data/containers, host `.ssh`, shared backup/NAS, `/var/run/docker.sock`, unreviewed broad host paths, deletion/restore of persistent data, production deployment.

## Observed unsafe existing container — do not use as Codex agent

Owner read-only inspection of `frappe_docker_devcontainer-frappe-1`:
- `/home/frappe/.ssh`: **writable bind mount** exposing host SSH credentials.
- `/workspace`: **writable broad host bind mount**.
- `/vscode`: writable Docker volume.
- Attached to `frappe_docker_devcontainer_default`; no separate production access control was proved.
- Existing persistent `development.localhost` and `ccpc-integration2.localhost` share a bench and source checkout. App currently detached HEAD `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87` (PR33) with untracked `AGENTS.md`. Phase 1 review branch head `e781b7c003c4bd0c0b9c80554898cf23364d26e4` (PR35 including merged PR37) **diverges** from PR33; do not blindly check out/pull/reset on shared bench.
- Four real Companies CCPC/RMC/WFC/GSL have Perpetual Inventory enabled and the active Department accounting dimension fields exist. All four currently have **zero** approved Expense and Center mapping revisions in main DEVELOPMENT.

An agent placed inside the existing container with unrestricted shell may access credentials and persistent data despite natural-language restrictions. The old `ccpc-codex --sandbox danger-full-access` alias is not acceptable in that container.

## Local DEV-only agent implementation requirements

1. **Separate runtime and separate authority:** Dedicated Linux identity, Docker Compose project/container and working tree. Start with independent disposable Frappe/ERPNext v16 + CCPC app, MariaDB and Redis. Never reuse or attach the existing shared MAIN DEVELOPMENT Frappe home or production volumes.
2. **Credential exclusion verified at container boundary:** No host `.ssh`, SSH agent socket, host Docker socket, Docker daemon TCP socket, NAS, backups, host `.env`, old or new PRODUCTION `site_config.json`, broad `/workspace` bind, or home-directory mount. Require only narrow agent-owned source/test volumes. `AGENTS.md` inside MAIN DEV is protected and must not be overwritten.
3. **Network isolation proven rather than assumed:** Agent must not be able to reach dedicated `ccpcerp-prod`, retired production containers/services on the old host, host SSH, shared NAS or unrelated LAN subnets. Docker Compose network names alone are not sufficient proof: require host-enforced egress/ingress rules and a narrowly constrained route for only required Codex sign-in/API endpoints and approved DEV test dependencies. If that cannot be proved, **keep remote Codex Cloud only**; do not broaden access as a workaround.
4. **Least privilege:** No `--privileged`, host networking/PID, root Docker daemon access, credential helper sharing, blanket filesystem writes or unrestricted host SSH. Agent can run its own disposable DB migrations/fixture cleanup. Logged, rollbackable writes on persistent DEV require a controlled DEV-only executor with narrow site credentials and source commit pinning; do not hand Codex host-level root authority.
5. **Real DEV deployment separately:** Before granting any persistent site write, verify independent current backup of database + site config + public + private files, recovery path, exact Git branch/commit/status and protected untracked files. Reconcile PR33 and Phase 1 release in GitHub first; do not drop PR33-only work or revive Phase 1 intercompany billing. Exact target site must be `development.localhost` (and only other explicitly approved test sites); exclude broken `ccpc-integration.localhost`. Site-specific migrations must not imply `--site all` or uncontrolled background changes.
6. **Auth and audit:** Codex must use normal approved ChatGPT/Codex authentication, not a paid extra API integration, and never receive credentials in GitHub, prompts or logs. Record task branch, commit, setup script versions, commands run, test exit codes, changes and handoff. Test concurrency/duplicate issuance, rollback, correct GL dimensions, roles and signed mapping validity. Never claim production readiness from synthetic tests.

## Implementation sequence, optimized for speed

**Phase A — immediately:** Continue Codex Cloud coding/testing from `ccpcerp/ccpcerp` current release candidate through issue #36; no new local infrastructure is required for source progress.

**Phase B — one-time setup, pending:** Implement the dedicated DEV-only agent runtime in version-controlled deployment scripts on a review branch, including a non-invasive preflight that checks mounts, socket privilege, networks, source worktree separation and no route to production/NAS. Review the exact rendered Compose config and fail closed on any unmet isolation requirement. Do **not** deploy or restart existing containers during code authoring.

**Phase C — local validation, pending:** On the host, after separate checked installation approval, launch only the new agent project. Verify it cannot read host SSH keys or old/new production, cannot access Docker socket or MAIN DEV host source, and can operate solely its own synthetic test bench. Then connect normal Codex authentication and run exact-source acceptance tests.

**Phase D — persistent DEV, pending:** After safe backing/branch reconciliation, optionally expose a DEV-only broker/runner that executes narrowly scoped site and source operations against `development.localhost`, with limits and auditability. Approve the initial persistent DEV access gate separately. Preserve real historic CCPC↔Ricor records, existing open source branches and all finance signoffs. Production remains entirely separate.

## Clear status

- **Verified:** Owner's current dedicated PRODUCTION operating arrangement by report; old host currently exposes writable SSH and workspace mounts to its original DEV container; four DEVELOPMENT Companies' Perpetual Inventory enabled; Department GL metadata present; 0 signed mapping coverage; current divergent GitHub branches; Codex Cloud's successful previously reported 129 targeted synthetic tests and merged PR37 code.
- **Not yet verified:** Production cutover technical details, isolation of a new local runner, absence of production network reachability, persistent DEV backup recency, Finance mapping signoff, actual DEVELOPMENT migration/UAT.
- **Not performed by this document:** Server connection, Docker Compose execution, container creation/recreation, SSH-key removal, MAIN DEV pull/migration, any production operation.

**Security principle:** Give Codex as much **DEVELOPMENT capability** as the environment can enforce, not as much host access as the instructions say it should refrain from using.
