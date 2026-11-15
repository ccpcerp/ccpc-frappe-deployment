# CCPC ERPNext — controlled DEVELOPMENT execution access

**Date:** 2026-11-15 (Asia/Manila). **Status:** GitHub-only review implementation. **User authorization:** broaden DEV investigation/test access and set up an auditable, restricted DEV connection; **not** permission to access NEW PRODUCTION, restart any shared host, remove credentials, run unattended Codex, change DNS/firewall, or publish/rotate secrets. No host access has been configured or tested in this milestone.

## Current state and known hazards

- Dedicated NEW host: `ccpcerp-prod`. This project does **not** authorize changes to it.
- Legacy host: `ccpcerpserver`, operator `gani`. Owner reports OLD PRODUCTION site has now been **cut off**. This is owner-reported operational status, **not yet verified** to imply stopped containers, disabled writers/schedulers/webhooks, removed host mounts, or purged data.
- Historical GitHub architecture: legacy host ran both `frappe_docker` (OLD PROD) and `frappe_docker_devcontainer` (DEV). The running DEV container `frappe_docker_devcontainer-frappe-1` had a bind mount at `/home/frappe/.ssh`, with readable files as the `frappe` user. That is **unsafe for unrestricted agent execution**. The earlier automatic Codex publisher was cancelled; its reporting token was revoked. Do **not** reuse this publisher or expose the SSH files.
- Existing app CI in `ccpcerp/ccpcerp` uses opt-in disposable CircleCI ERPNext/MariaDB tests. Preserve manual opt-in controls and cost checks; don't enable automatic paid/broad jobs or CI triggers merely because direct access is approved.
- This review branch is separate from open NEW G1 production readiness PR #35. Production G1 activation locks remain unchanged.

## Effective scope after verified isolation

**Allowed within named DEV-only disposable target:** source/log/health inspection, non-sensitive metadata, Python compile/tests, Frappe/MariaDB integration on an explicitly designated synthetic test site, repeatable test fixture setup/cleanup, and reviewed code deployment with worktree/commit/backup checks. Mutating procedures must be auditable and limited to DEV-target paths, identities and databases. GitHub remains authoritative for committed code; no overwriting uncommitted changes.

**Still individually controlled:** operations that touch non-synthetic persistent DEVELOPMENT data, migration, high-risk cleanup, service restarts affecting other containers, configuration of firewall/Docker daemon/host networking, credential changes, new CI paid runs, and integration with external production systems. User has not authorized a blanket shell root account. No NEW PROD access, OLD preserved data deletion, Docker socket mount to the agent, host-wide sudo, SSH material in agent workspaces, production DB credentials, NAS credentials, autonomous Codex publishing, or extra paid API access.

## Staged access implementation

1. **GitHub baseline — DONE:** Added `scripts/development/operator/ccpc_dev_execution_boundary_readonly.py` and `tests/test_ccpc_dev_execution_boundary_readonly.py` on the `review/development-execution-access-2026-11-15` branch. The audit is read-only: exact operator/legacy host, old Compose project active count, pinned DEV container active/project, privileged flag, presence of credential mounts/Docker socket. It emits only YES/NO/count and PASS/STOP, not raw Docker inspect, mount paths, secrets or site data.
2. **Owner-run read-only host evidence — PENDING:** Verify legacy host still matches exact known identities and whether OLD PRODUCTION Compose containers are active. The owner's network/site cutoff alone does not establish no background jobs or writes. If the preflight reports STOP, investigate/reconcile; **do not automatically stop/remove containers or change the existing DEV container's SSH mount**.
3. **Separate isolated worker — PENDING:** On the legacy host **after** boundary and backup review, provision a dedicated non-root, non-sudo test-execution identity in a fresh isolated DEV worker (or use existing hosted disposable CI). Require no host Docker socket, no SSH/credential/NAS/prod mounts, no host network, no automatic secrets injection, no access to unrelated host processes/data, appropriate resource and outbound-network limits. DO NOT run an agent in the existing SSH-exposed DEV container. Source and exact versions must be pinned and reviewed before any installation.
4. **Transport and execution — PENDING:** Add an authenticated, auditable, narrow command interface supporting only named diagnostics/tests on **allowlisted DEV synthetic sites and paths**. No arbitrary inbound shell, public unauthenticated endpoint, blanket root Docker privileges, untrusted PR automatic self-hosted workflow, or unreviewed scripts. Prefer a reviewed outbound-only link or existing hosted CI; select the actual connection mechanism only after host evidence and available provider tools are verified. Avoid installing an unbounded self-hosted GitHub Actions runner on a secret-bearing shared host.
5. **Acceptance — PENDING:** Prove source SHA, fixed target, no production/OLD/backup reachability, worktree protection, redacted audit logs, failure STOP, and disposable Frappe/MariaDB stock/GL/billing/permissions/rollback test run. Only then label DEV automatic execution operational. NEW PROD release and cutover remain separate.

## Safety gate semantics

The preflight's PASS means only: the specific Docker metadata assertions at that instant matched. It **does not** prove OLD site inaccessible, no external writers, no orphaned credentials anywhere, firewall isolation, private DB separation, or an approved automated agent. A STOP is actionable evidence, not permission to change host settings.

### One safe next operator observation

At `gani@ccpcerpserver`, run a **read-only** Docker status check, not a setup script:

```bash
test "$(hostname -s)" = "ccpcerpserver" &&
sudo docker ps -a --format '{{.Names}} {{.State}}' |
grep -E '^frappe_docker(-|_devcontainer-)' || true
```

Share only the container names and running/exited states. Do **not** print Docker inspect environmental values, keys, passwords or database records. After names and states are verified, a separately reviewed source-hash-pinned preflight can be run. No production action is part of this command.

## Verified milestones vs pending

**Implemented in GitHub:** review-only source and mock tests for the boundary inspection, plus this access-design record. **Not done:** actual test execution/host preflight, agent/transport installation, DEV operational access, CI activation, source pull, Docker/systemd changes or business DB tests. Don't imply a fully working remote link until a legitimate connection has been created and tested in a subsequent explicitly authorized operator step.
