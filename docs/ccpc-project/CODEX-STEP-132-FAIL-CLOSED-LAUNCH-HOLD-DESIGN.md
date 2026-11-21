# Step 132 — Codex fail-closed manual launch-hold design (GitHub-only)

**Date:** 2026-11-21 (Asia/Manila)  
**Status:** DESIGN REVIEW ONLY — NOT INSTALLED, NOT EXECUTED, NOT AUTHORIZED TO START CODEX/SQUID.  
**Source of authority:** CCPC GitHub-first workflow; Step 131 approved read-only host metadata inventory; PR #39 review branch.  
**Owner scope:** Owner approved the **GitHub-only design review** proposed after Step 131; this is *not* authorization for a host-side installer, launch wrapper, marker, firewall mutation, Docker/UFW reload, reboot, network creation, packet probe or agent start.

## 1. Evidence reviewed and its limits

- [Step 131 recovered findings](CODEX-SCOPED-NFT-INSTALL-RECOVERY-REVIEW.md): operator's Step 130 read-only command ended with `STEP_130_READ_ONLY_METADATA_COMPLETE`. Codex was **stopped**, auto-restart **disabled**; Docker socket active/enabled and declared to trigger Docker service; no **direct** Docker↔UFW After/Before or Requires/Wants ordering observed; Docker unit had an ExecReload handler; UFW unit had none; both proposed project units absent; stock `nftables.service` inactive/disabled. `PERSISTENCE_VERIFIED=False`, `CODEX_LAUNCH_AUTHORIZED=False`.
- [Original laboratory guard](../../scripts/security/ccpc_codex_lab_firewall_guard.py): read-only `verify` demands a **stopped** agent, the expected original internal Docker bridge identity and IPv6-disabled network metadata, original iptables INPUT/DOCKER-USER DROP rules and precedence, and UFW/Docker prerequisites. It always says `agent_launch_authorized=False`.
- [Scoped nft controller](../../scripts/security/ccpc_codex_nft_scoped_controller.py): `verify` requires the stopped-agent/original-bridge checks, inactive/disabled stock nftables service, and exact project-only `inet ccpc_codex_lab_guard` table. It has an install capability gated by an independent marker, but **Step 132 does not authorize calling install or creating a marker**. `verify` always prints `agent_launch_authorized=False`.
- [Proposed project systemd unit](../../scripts/security/systemd/ccpc-codex-nft-guard.service.example): an **uninstalled** oneshot example with provisional `After=docker.service ufw.service`, no `[Install]` and no stop/reload hook. It does not provide boot/reload persistence or guard alternate Docker launch paths.
- Step 124 host→synthetic-lab and Step 126 synthetic-lab→host gateway **single IPv4 TCP canaries** passed on operator-reported output, with allowed controls. They did **not** prove nft-only causation, IPv6, unrelated bridges, full application egress, reboot/reload persistence or continuously enforced isolation.

No runtime status has been rechecked as part of this design. Source inspection and operator-reported host output are different evidence categories.

## 2. Nonnegotiable rule: the lab stays HELD

**Current state = HELD / NO-GO.** No Codex or Squid startup, no persistent launch permission, no change to the stopped-agent restart policy, no project unit installation or activation, and no new proxy bridge/container. This document does not issue a launch token or authorize a one-shot startup.

**Desired future safety property (not yet achieved):** An *operator-controlled launch workflow* must refuse to start on failed, stale, missing or inconsistent evidence. An unauthorized direct Docker/root start **cannot be prevented** by a shell script, optional systemd unit, file marker or a post-facto monitor. Do not call this mechanism an unbypassable kernel security boundary.

### Proposed states (none implemented)

| State | Meaning | Permitted action at Step 132 |
| --- | --- | --- |
| **HELD** | Default; agent stopped, restart disabled and current launch permission absent | Documentation/source review only |
| **CHECKING** | Hypothetical one-time read-only examination of pinned code, exact firewall/bridge state and lifecycle context | **Design only**, not permission to execute |
| **INELIGIBLE** | Checks missing, stale, incomplete or other required isolation/credential/proxy gates outstanding | Stop; preserve restrictive rules; no automatic repair/retry |
| **ELIGIBLE FOR SEPARATE REVIEW** | Every future prerequisite independently passed but no launch authorization has been issued | Present results, fresh risk assessment and explicit exact-run request |
| **RUNNING UNDER SUPERVISION** | Future separately approved launch with active isolation and safe stop/revocation | **Unavailable / not authorized** |

No state, boolean or status from an existing `verify` command may be interpreted as `LAUNCH_ALLOWED=True`. There is no implemented permit/transition from HELD to RUNNING.

## 3. Hypothetical prelaunch verification contract (not executable)

A future reviewed implementation must *fail closed* on **any** of:

1. **Identity and immutable source:** wrong host, wrong operator privilege, changed inspected source or unpinned file hashes, mismatched Docker project/container labels, unexpected host mount or daemon/socket state, untrusted service/unit/script metadata, unexpected authorization marker or non-root-writable policy inputs. Never fetch live code or credentials as part of launch.
2. **Current agent state:** agent already running/restarting, restart policy not `no`, new proxy/container/bridge unexpectedly active, or any alternate auto-start route not accounted for. The existing guards intentionally require a stopped agent; preserve that condition until a separately authorized future launch.
3. **Current original-lab firewall:** wrong/missing original bridge ID, changed `internal`/IPv6/IPAM state, missing or reordered original iptables INPUT/DOCKER-USER DROP, broken FORWARD→DOCKER-USER entry, missing UFW/Docker prerequisites or any unknown intervening ACCEPT rule.
4. **Current independent nft firewall:** scoped project table absent/ambiguous/changed; unexpected hook priorities, rules, chain policy, bridge interface match or table family; stock `nftables.service` active/enabled or any global-flush path under consideration. Never run `install` as a hidden fallback for `verify`.
5. **Lifecycle freshness:** Docker socket activation, Docker daemon restart/ExecReload, bridge recreation, UFW reload/CLI action, nft mutation, host reboot or network change **since the last known independent verification**. No unsupported claim that a timestamp alone proves absence of a change; require a controlled lifecycle interlock/fresh check.
6. **Remaining security acceptance:** unapproved image/proxy provenance, missing effective Squid listener/source and DNS/SSRF destination controls, credential and mount access concerns, missing resource limits, missing synthetic-only negative/positive tests (including alternate networks and IPv6), and untested launch/stop behavior. Firewall checks alone are never sufficient for Codex readiness.

Any unknown or failed check results in **HELD/INELIGIBLE**, without automatically starting, fixing, removing or weakening firewall policy. Reporting must be sanitized (fixed status labels only).

## 4. Lifecycle and launch-path handling — specific architectural limits

| Lifecycle or launch path | Review-only required handling |
| --- | --- |
| **Cold boot / Docker socket activation** | Agent remains stopped with restart disabled. A disposable per-launch check cannot rely on systemd `After=` alone; evaluate boot/socket ordering, controlled activation boundary and whether necessary Docker chains/bridge exist before any future startup |
| **Docker daemon restart, ExecReload, bridge recreation** | Invalidate prior inspection; agent start remains held. Require fresh bridge identity and original iptables + project nft exactness, plus separately approved synthetic acceptance before any release |
| **UFW CLI reload / external rule reconciliation / global nft flush** | Do not run as part of Step 132. Treat any possible policy change as invalidating launch eligibility. Stock `nftables.service` remains inactive/disabled because its observed global-flush lifecycle is unsafe |
| **Manual Docker start / Compose up / systemd alternate unit** | A voluntary wrapper can be bypassed by Docker/root users. Require an explicit operating policy limiting these paths; do **not** represent it as enforcement against a privileged actor |
| **After a future launch** | Existing original/nft read-only `verify` functions require the agent **stopped** and cannot be directly reused as a running-agent health monitor. A separate reviewed monitor and safe-stop design are needed, along with failure/race testing. Polling cannot prove zero-gap containment |

There is an **inspection-to-start time-of-check/time-of-use gap** even if all checks run successfully. Unless a stronger isolation boundary and lifecycle interlock are independently demonstrated, do not approve unattended or direct host startup based on a passing verifier.

## 5. Recovery, alternative and verification gates

- Preserve the original lab iptables protections and the installed exact project-owned nft table. No unapproved cleanup, flushing, Docker/UFW restarts, stock nftables service actions, route changes, service install or agent startup. The previously confirmed two administrator/recovery paths and private Stage A firewall baseline remain mandatory for any future active host operation.
- **Faster operationally simple future option** (only if the threat model permits host/root/Docker administrators as trusted): a manual, one-use, SHA-pinned operator workflow with fresh *read-only* prelaunch verification, explicit separate launch authorization, and supervised lifecycle checks. This remains insufficient by itself while other proxy/credential/network gates are open.
- **Stronger isolation option:** run the Codex laboratory inside a dedicated disposable VM/host with no shared DEVELOPMENT Docker daemon/host credentials, independent firewall lifecycle and isolated synthetic resources. This reduces shared-host administrative bypass and bridge-recreation exposure but adds setup work. It should be preferred if security demands containment even if a privileged local Docker command occurs.
- Prior to any implementation, review trust boundaries, practical launch-path coverage, side effects of Docker socket activation, failure/restart behavior, stop/rollback/recovery, image/credential policy, source integrity, and synthetic-only acceptance tests. Keep tests and DEV/PROD changes separately approved, and distinguish mocked/static tests from real host packet/lifecycle results.

## 6. Step 132 decision and next proposed milestone

**Decision:** Document a **manual fail-closed launch hold as a proposed operating workflow**, not a proven or deployed enforcement mechanism. The current root/Docker privilege and lifecycle gaps mean `NO-GO` persists. No code, systemd units, firewall rules, tests, host commands, network topology or runtime settings were changed by this design review.

**Next meaningful engineering action (requires a new scoped request):** Choose whether the future Codex lab must resist *privileged host/Docker bypass*. If yes, prepare a dedicated VM/host isolation plan; if privileged administrators are in the trusted computing base, review a **small source-only, non-executable launch-gate specification with mocked negative tests** that cannot start Codex and checks exact original/nft policy. Either approach still requires fresh negative runtime tests and separate authorizations before any actual launch.

**PR #39 stays DRAFT/UNMERGED. Codex/Squid activation remains NO-GO.**
