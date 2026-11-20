# CCPC Codex laboratory — firewall persistence and boot-order design review

**State:** GitHub review proposal ONLY. No host deployment, firewall changes, service enablement, container start, image pull or reboot authorized by this document.
**Related:** draft PR #39 and `docs/ccpc-project/CODEX-LAB-SECURITY-ISOLATION.md` on the dedicated audit branch.

## Evidence: read-only host checkpoints

- Step 85 verified the **exact** original-lab host `INPUT` DROP through `iptables -C`; Step 83 separately verified both expected `DOCKER-USER` cross-bridge DROP rules and that `FORWARD` first jumps to `DOCKER-USER`. This resolves Step 83's false negative from textual token ordering. No live reachability test has been performed after installing the rules.
- Step 86 found the proposed `br-ccpc-cdxpx` interface name unused in current Docker networks, interfaces and inspected IPv4 filter/NAT rules. This was not an exclusive reservation. Step 82 found no *local* conflict for `172.30.250.0/29`; external/VPN/remote routes remain unverified.
- Step 87 found `ufw.service` enabled and active; `nftables.service` and `netfilter-persistent.service` disabled/inactive, no nonempty standard saved IPv4 iptables rules file. The nftables configuration was nonempty but not proven active.
- Step 88 inspected three UFW IPv4 rule files, two UFW startup hooks, and the nftables configuration: none contained the three expected laboratory rule comment tags. The rules remained **active in the kernel**.
- Step 89 scanned one regular administrator systemd service/timer/drop-in file, thirteen selected cron files, the root crontab and `/etc/rc.local`: no reference to the original-lab firewall script or its three tags was found in that **bounded selection**. `rc.local` was absent as a regular file. This does NOT rule out vendor units, indirect startup jobs, non-root crontabs, scripts that install equivalent rules without tags or other persistence mechanisms.

**Conclusion:** original-lab rules exist *now*. Their restoration after reboot, UFW reload, or Docker daemon restart is **not verified**, and no established startup ordering for a future second network was found. Do not assert an established security breach or automatic loss of the rules; fail closed until protection is independently verified.

## Security invariants for any future deployment

1. The original `ccpc_codex_dev_agent_lab` network remains intact; synthetic DB/Redis, unrelated DEVELOPMENT/UAT, host SSH, NAS and PRODUCTION are not modified by Codex setup. Existing 3 tagged lab DROP rules must not be overwritten by an installer for the new network.
2. The optional `proxy_clients` bridge has the reviewed deterministic device name `br-ccpc-cdxpx` and provisional `172.30.250.0/29` reservation only after a fresh preflight. A firewall rule matching a **not-yet-created interface by exact name** can be inserted before network creation; its presence alone is not proof of traffic isolation. No window where the agent is attached to that network without host/forward safeguards is acceptable.
3. Before network creation, exact scoped new-bridge rules must be present and ordered before competing permits: unconditional inbound interface `INPUT DROP` for host-directed traffic and two `DOCKER-USER` cross-interface DROP rules. The read-only `scripts/security/ccpc_codex_proxy_bridge_preflight.py` checks these predicates. These are *proposed rules*, not installed rules.
4. **Squid has a separate outward-facing network**. The new agent-client bridge policy does not constrain Squid's own outbound sockets, DNS, or reachability of host/private/VPN/remote networks via the outgoing bridge. The Squid egress firewall and resolved-IP/DNS controls require separate review and negative canary tests.
5. Rules must be restored **before** any path by which the agent or proxy could start at boot, by operator Docker command, daemon restart or auto-restart. Compose `restart: "no"` and `online` profile are safeguards, not substitutes for host enforcement. Handle UFW reload, Docker-created chains, daemon/network recreation and failed startup in a fail-closed way.
6. An unprivileged Codex process must not have access to Docker sockets, host networking, privileged containers, host secrets or permissive runtime command escape; verify real runtime behavior separately.
7. Persistence, rollback and rule ownership must not impact existing SSH access, nonlab networking, DEVELOPMENT/UAT or the separate PRODUCTION server. Never flush chains, reset UFW, prune Docker or delete shared resources for the laboratory.

## Implementation options — no option selected or applied

**Option A — UFW-managed persistent source:** Use a carefully reviewed UFW-supported startup mechanism only after proving exact chain creation and Docker/UFW ordering on this host. Do not blindly insert `DOCKER-USER` references into UFW `before.rules`: that chain may not exist until Docker constructs it. Do not run `ufw reload` for experimentation.

**Option B — dedicated root-owned systemd oneshot/guard service:** Model an idempotent exact-match firewall preparation action with a matching read-only verifier, explicit `After=` dependencies for Docker/UFW and a separate guarded lab startup unit that **Requires/After** successful firewall verification. Check that the systemd dependency graph actually provides the intended order and fails closed. A systemd service alone cannot prevent an operator from manually starting a container, and a oneshot may not restore rules when UFW/Docker subsequently reload; this must be addressed with additional controlled guards/monitoring or by a stronger persistent firewall integration.

Neither option is approved for host installation. Choose based on **observed** Docker/ufw startup unit properties, possible UFW hooks, actual iptables-nft backend, and operator rollback capability. Do not enable automatic Codex startup as part of persistence design.

## Separate controlled validation and rollback requirements

- Establish a protected host recovery path and a second SSH session before *any separately authorized* firewall mutation; preserve the existing rule snapshot without publishing raw infrastructure details.
- Verify the proposed interface name and /29 are still unused immediately before an approved rule change. Confirm the agent is still stopped; require an operator-approved exact sequence and do not attach the agent while any requisite rule is missing.
- Install only narrowly scoped, tagged rules; immediately prove `iptables -C` matches, precedence and that no existing Docker/host networking changed unexpectedly. On partial failure, delete **only the exact rules added in that attempt**; never broadly reset firewall chains.
- In a separately authorized and carefully isolated test, demonstrate denial of host gateway SSH, Docker bridge and non-production LAN/remote canaries, with synthetic DB/Redis functionality preserved. Never test real PRODUCTION by default.
- Check whether protection survives an approved UFW refresh, Docker restart and eventually a planned reboot **only under a verified maintenance/rollback procedure**; do not run these now. Capture the exact persisted rule lifecycle and verify the agent cannot race startup.
- Run the 60 source-only regression tests and Squid syntax checks in a trusted isolated runner; GitHub Actions PR checks currently fail without any runner steps, so no test pass is available. Pin/check proxy image provenance, runtime UID and resource budget first.

## Step 90 — service startup ordering observations (2026-11-20)

The operator ran the guarded read-only host inspection with stopped-agent and three original-lab firewall-rule checks. Sanitized output:

- `agent_running=False` and `original_lab_three_rules_present=True`.
- Agent Docker restart policy disabled: `True` (reduces unplanned restart risk but not manual-start or configuration-drift risk).
- `docker.service` active and enabled: `True`; `docker.socket` enabled: `True`.
- `ufw.service` active and enabled: `True`.
- Neither `docker.service After=ufw.service` nor `ufw.service Before=docker.service` nor `ufw.service After=docker.service` was directly declared (`False` for all three).
- `complete_boot_order_verified=False` and `firewall_reboot_persistence_verified=False`.

These results mean **no explicit direct Docker/UFW ordering relationship was observed**, not proof that the units run in an unsafe order or that no transitive ordering exists. Even if they execute in a favorable sequence, the original lab rules still have no verified persistence mechanism. Docker's presence and enabled socket activation mean a future design must consider both ordinary Docker boot and on-demand daemon activation. Unattended Codex restart remains disabled in the observed container; preserve this safety gate.

### Preferred design to evaluate, NOT approved for installation

Maintain strict separation between *firewall persistence* and *starting Codex*. A **systemd-guarded firewall preparation + independent read-only verification** approach is now the preferred candidate for design review, because the current Docker/UFW direct ordering does not itself establish a safe UFW-native `DOCKER-USER` lifecycle. This is **not a final selection or permission to install anything**. Require a dry-run/graph-level examination before generating operational units, because Docker's chain initialization and possible UFW reloads can erase rules after a oneshot has reported success.

A reliable implementation would require: (1) a root-owned, narrowly scoped idempotent restore operation referencing only the exact audited bridge rules; (2) ordering after needed Docker chain availability and after UFW has reached a settled state, while forbidding agent startup before protection is verifiably installed; (3) an independent fail-closed health gate that continuously or at least at every potential Codex launch/relaunch revalidates `INPUT` and `DOCKER-USER` rule presence/precedence; (4) recovery of protection after a firewall/Docker reload without permitting the lab to run during a gap; (5) no global UFW/Docker service edits, chain flushing or automatic Codex start; (6) isolated-SSH rollback and real negative connectivity tests before release. A simple `After=ufw.service` relationship on Docker, by itself, is **insufficient** because it neither persists the custom rules nor handles subsequent reloads.

**Before implementation:** inspect relevant `systemctl show` unit ordering properties beyond the three direct checks (for example `Requires/Wants/PartOf/ExecStartPost` status as sanitised flags), and check whether UFW is using a rule management hook that could safely restore the exact original lab rules once Docker chains exist. No edits to service files, UFW configuration or host containers are authorized by this review.

## Step 91 — dependency and hook precheck (2026-11-20)

The operator ran a guarded **read-only** Docker/UFW/socket systemd property inspection with all three original laboratory firewall rules present and the agent stopped. Sanitized output:

- `docker_requires_ufw=False`, `docker_wants_ufw=False`.
- `docker_after_network_online=True`, `ufw_before_network_pre=True`.
- `docker_has_dropins=False`, `ufw_has_dropins=False`.
- `docker_has_start_pre_hook=False`, `docker_has_start_post_hook=False`.
- `ufw_has_reload_handler=False`.
- `docker_socket_requires_service=False`.
- `complete_dependency_graph_verified=False`, `reboot_persistence_verified=False`.

**Interpretation:** This narrows the observed host design: no Docker dependency on UFW; no inspected service drop-in or Docker pre/post-start hook; UFW reports `Before=network-pre.target` and Docker reports `After=network-online.target`. Those *distinct target relationships* are **not proof** of a full dependency path, successful firewall persistence, nor of an ordering guarantee after a reload. `docker.socket Requires=docker.service` being false does **not** rule out socket activation; systemd socket `Service=` wiring and unit dependencies must be independently reviewed before assuming Docker cannot start on demand. Likewise absence of an `ExecReload` in `ufw.service` does not mean `ufw reload` is impossible or harmless.

### Design decision for the GitHub-only review stage

Adopt a **two-layer candidate design**, strictly for review; **do not install it**:

1. A root-owned, idempotent *original-lab firewall restoration* action, guarded for hostname, Docker daemon and known lab/bridge identity, stopped-agent state, iptables-nft backend, and no change to other chains or namespaces. Intended to run after Docker chains exist and after UFW's initial setup. It must check exact three existing rules before adding only missing ones, and preserve existing tags without duplication.
2. A separate, fail-closed *manual Codex startup gate*, explicitly invoked **every time** the agent would be launched, not merely once during boot. The gate must verify all original lab INPUT/FORWARD rules **and**, if the proposed second `proxy_clients` network is to be attached, its pre-enforced INPUT/FORWARD rules, precedence and collision checks. If any rule is missing or altered, the agent must remain stopped. Disallow or operationally restrict bypass via unguarded `docker start` or `docker compose up`. Do not create any auto-start systemd unit for Codex itself.

A single systemd oneshot is **insufficient** to make the lab secure after arbitrary later UFW reloads or Docker chain re-creation. Before approving implementation, decide whether the host needs UFW-supported persisted rules, a dedicated post-Docker firewall reconciliation unit plus explicit hooks for reload paths, or a stricter service dependency design. Protect administrative SSH recovery, preserve DEVELOPMENT/UAT networking, and test exact-match rollback. The optional Squid `outgoing` network needs its own enforced egress isolation. No component should silently grant Squid broad internet/host/private-network access.

**Important remaining blockers:** The source-only validator and all 75 declared Python tests have now executed successfully in an isolated, independent Python workspace; GitHub Actions itself still fails before runner steps, and real Docker/Squid/firewall negative integration tests are still outstanding. There has been no approved host firewall modification, Docker pull/start, network creation, or controlled negative reachability validation. The proposed systemd/UFW plan is **not production-ready**.

## Step 92 — uninstalled original-lab restoration implementation (2026-11-20)

The owner approved continuation of **GitHub-only Step 92 implementation planning**, not execution on `ccpcerpserver`. Source was added on `review/codex-proxy-network-hardening-2026-11-19` to make the proposal inspectable and testable:

- `scripts/security/ccpc_codex_lab_firewall_guard.py`: NEW, **read-only** `preflight`/`verify` for the *original* lab. Fails closed unless root, hostname and Docker daemon identity, stopped/known-label agent with restart disabled, intended original Docker bridge+gateway and iptables-nft backend match. Confirms UFW active and availability/ordering of the `FORWARD → DOCKER-USER` path. `verify` additionally uses exact `iptables -C` calls for the existing `INPUT` host and two `DOCKER-USER` cross-bridge DROPs, and a **token-order-independent** narrow parser of `iptables -S` to ensure they precede other INPUT and forwarding rules. No mutation or container startup mode; every success prints `agent_launch_authorized=False`.
- `scripts/security/systemd/ccpc-codex-lab-firewall-restore.service.example`: NEW, **uninstalled** systemd service *template*, not a `.service` unit. It requires an absent-by-default root-controlled approval marker, intended reviewed scripts in a specifically installed, pinned source tree, and Docker/UFW startup. Its hypothetical future actions would be original-lab guard `preflight` → existing `ccpc_codex_dev_lab_firewall.sh apply` → guard `verify`; it neither starts Codex nor creates a network. The existing original firewall script is unchanged; no ExecStop removes protection. This unit is **inert in GitHub**, not enabled or executed anywhere.
- `codex-dev-agent/tests/test_lab_firewall_guard.py`: NEW, 15 offline mock-only regression methods on rule matching, precedence, refusal of unsafe modes, fail-closed behavior and inert unit structure. Alongside the prior 60 source-only methods the PR now declares **75**; the full Python suite later **executed successfully with 75 tests and 0 failures** in an independent isolated workspace, after each required source file's Git blob SHA was matched. GitHub Actions runner execution remains unverified because jobs fail before any runner steps. The CI path filter also watches the new code and unit template.

### Source-only operational sequence (NOT AUTHORIZATION TO APPLY)

1. Independently verify current host access, operator SSH recovery, agent stopped/restart disabled, no pending host changes, UFW/Docker readiness, the source SHA, script file ownership/mode and the exact existing network bridge ID. Before any future use, inspect the full effective unit dependency graph, Docker socket activation and reload hooks. Reject if the expected state has changed.
2. Preserve a **private**, restorable snapshot of the current *scoped* active firewall/DOCKER-USER rule state without recording raw infrastructure data in GitHub/chat. Record which of the three exact original-lab rules exist and at which positions **before** an operator-approved action.
3. In a reviewed maintenance window and *only after distinct host approval*, choose an approved root-owned installation path and install/validate the scripts and a real service file derived from the template; the example paths and approval marker are placeholders. Do not install new packages or enable any service as part of the GitHub proposal. Require UFW and Docker settled and no other Docker/firewall mutation racing the operation. Do not add automatic Codex startup.
4. The template's intended flow is `preflight` (fails before write on unexpected identity, running agent or changed Docker firewall) → existing exact-scoped `apply` (adds missing original-lab DROP rules idempotently; it rolls back only additions on its own detected partial apply failure) → independent `verify` (checks exact rule existence **and precedence**).
5. On a failed preflight, **make no changes**. On failed apply, use the script's verified partial-addition cleanup and keep Codex stopped. If post-verify fails, leave newly present protective DROP rules in place until an operator reviews the exact state; **do not automatically flush/remove security rules or restart UFW/Docker**.
6. Recheck rules after a separately approved reload or Docker service restart and demonstrate they are reliably restored *without* running Codex while unprotected. The example **does not implement** automatic restore after a later reload. Before any agent launch a separately enforced guard must verify the original rules, new bridge host/cross-bridge rules if deployed, and independently enforced Squid outbound/DNS isolation. This requirement remains unsatisfied by the proposal.

### Exact rollback concept (independently approved host operation only)

- First verify the Codex agent **and optional proxy are stopped**, that the reviewed host identity still matches, and that an administrative SSH/recovery session remains available. Stop and disable only a newly installed CCPC-specific service **if one was actually installed**, then remove only its exact project files/approval marker under an approved, recorded path. Never disable UFW or Docker, and never clean up other workloads.
- Compare before/after exact rule existence and chain positions. If **no new rules were added**, rollback must not remove any original protection. If specific new DROP rules were added by the approved attempt, remove **only those exact additions, by their verified identity**, and only with a separate explicit firewall-removal approval and assurance no agent/proxy could run unprotected. Do not blindly invoke the legacy script's broad `rollback` mode: it removes all matching original lab rules, including rules present before the attempt.
- Post-rollback verification must demonstrate original active lab protections are at least as strong as the pre-change snapshot, Docker/SSH/DEV unaffected, and that neither Codex nor Squid was activated. If state is ambiguous, preserve restrictive DROP rules and hold all starts pending review.
- If an approved installation produced a partial or failed unit, **do not assume systemd will automatically undo its iptables changes**. No `ExecStop` cleanup is included for precisely this reason.

### Specific unresolved go/no-go items

- A oneshot template and a human-operated `verify` are *not* an unbypassable runtime launch gate. Docker-enabled operators can start containers directly, and firewall rules can be changed by a later UFW/Docker reload. An enforcement strategy for all launch/relaunch paths and runtime firewall drift is still required before activation.
- Proposed `proxy_clients` network has not been created. Its pre-enforced firewall and Squid's independent `outgoing` egress/DNS restrictions remain untested and uninstalled.
- Manual negative connectivity tests, UFW/Docker restart/reload tests, actual Python/Squid tests, runner availability, bridge IPAM conflicts and a reviewed proxy image digest/runtime UID are all pending. None of these gates is closed by a test *declaration* or by a GitHub commit alone.
- The service template needs target-host dependency and security review before deriving any installable `.service` file; the approval marker must be root-controlled, and source pinned to reviewed commit rather than arbitrary mutable checkout.

## Step 93 — combined firewall ordering fix and isolated full-test validation (2026-11-20)

**Source-review defect discovered:** `ccpc_codex_lab_firewall_guard.py` and `ccpc_codex_proxy_bridge_preflight.py` initially each required **their own** bridge rule to occupy the first `INPUT` position and first two `DOCKER-USER` positions. Those requirements are mutually incompatible once both networks' protections are pre-installed. Neither a successful isolated unit test nor the old firewall's present state could justify activation with that inconsistency.

**GitHub-only correction:** Added pure, shared `scripts/security/ccpc_firewall_rule_order.py`; both verifiers now use its narrow canonical iptables rule parser, which tolerates reordered nonpermissive flags and either inversion spelling while rejecting unreviewed expressions. It permits the exact original-only prefix (one host DROP, two cross-bridge DROPs), or the complete two-bridge prefix (**two host INPUT DROPs and four DOCKER-USER cross-bridge DROPs in either relative order**) when the new bridge has any rule reference or `require_proxy=True`. A partially installed new bridge, intervening ACCEPT/unknown jump, missing original rule, or unexpected rule before the prefixes causes fail-closed rejection. The helper never executes iptables, Docker, subprocess or network calls.

Added five `test_lab_firewall_guard.py` regression cases for both ordering permutations, partial proxy protection, permits ahead of protections, missing old-bridge rule and alternate inversion syntax. Also updated source-test import paths and the CI file path filters. Total **75 Python unit tests** (60 original + 15 firewall guard).

**Independent execution:** Reconstructed the full source-only test tree in a private isolated local Python workspace using exact content fetched from the private GitHub connector. For each dependent file, computed Git blob SHA and compared with the returned GitHub blob SHA before invoking tests. Executed `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s codex-dev-agent/tests -p 'test_*.py' -v` with no Docker, host network, external credential, Squid binary or host file modifications. **Result: Ran 75 tests; OK; 0 failures, 0 errors.** Synthetic-secret test data was generated only under a temporary directory, without sharing values. This validates the Python source-only security assertions, not actual Docker Compose renderer semantics, proxy resolution, rule persistence, or live isolation.

**Persistent CI blocker remains separate:** The latest GitHub Actions job on the review branch has still failed before assigning a runner or recording any steps, with job log requests returning `BlobNotFound`/404. An unrelated scheduled `Autoupdate pre-commit hooks` workflow also failed with no runner and zero steps (run `44563127843`), supporting a broader runner provisioning/account-level concern rather than blaming only the new test code. Root cause is **not verified**; possible runner provisioning, plan/usage/billing restriction or temporary GitHub service issues should be checked via the **workflow-run Summary/Annotations and account Actions usage**, with no payment-method/budget changes authorized. Do not repeatedly rerun or change workflow syntax without concrete evidence.

**NO-GO unchanged:** Draft PR #39 remains unmerged. No host firewall persistence or reload recovery mechanism installed, no unbypassable runtime launch gate, no second bridge created, no Squid egress/DNS enforcement or actual negative tests. Nothing was deployed to DEVELOPMENT/PRODUCTION. A successful source-only suite is necessary but insufficient for activation.

## Step 94 — GitHub Actions run blocked by account billing or spending eligibility (2026-11-20)

The operator opened [GitHub Actions run #44650795584](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44650795584) for draft PR #39, branch `review/codex-proxy-network-hardening-2026-11-19`, and supplied its exact job annotation:

> The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings

The run shows `policy-regression`, **Failure**, total duration **3 seconds**, one annotation error, and no generated artifacts. Connected GitHub API inspection previously confirmed no runner allocation, zero job steps, and no retrievable job log. This annotation **resolves the pre-execution diagnosis at the category level**: GitHub Actions blocked the job for an **account payment / spending-limit eligibility condition**, *before* Python ran. It does **not** establish which alternative (recent failed payment versus spending limit) is the actual account-specific cause. Do not present it as an assertion that a particular card charge failed or that the user has exceeded a particular paid budget.

**Owner policy and decision:** Do **not** add a payment method, increase paid spending limits, change GitHub billing settings, activate a self-hosted runner, or repeatedly re-run failing GitHub-hosted jobs. GitHub Actions status remains blocked; there is no CI execution/CI pass to report. The existing **75/75 independent offline Python unittest pass** (source matched against GitHub blob SHAs) remains valid and separately documented in Step 93; it does not satisfy host persistence, Squid parsing, Docker runtime, or negative-network integration gates. Continue code review and no-cost offline validation in authorized isolated environments. The owner may independently review GitHub **Settings → Billing & plans** if they wish to determine the account-specific billing state, but this review document requests **no change**.

No files in the firewall guard, original lab scripts, Compose, Squid policy or CI workflow were modified in response to the annotation. Draft PR #39 must stay **open, draft and unmerged**. Codex agent stopped and Squid inactive at last operator-reported host snapshot; no current host command or fresh host verification. Proposed proxy bridge remains uncreated at last verification. PRODUCTION and DEVELOPMENT not touched.

**Next technical milestone independent of GitHub-hosted runner:** Finish review of unbypassable per-launch enforcement, post-reload persistence, Squid outbound/DNS isolation and network negative-test plan. Only request a separately explicit and scoped host-operation approval after prerequisite documentation, tested source and recovery/rollback procedure are ready.

## Step 95 — manual CircleCI alternative prepared for standalone deployment repository (2026-11-20)

Owner offered CircleCI as an alternative to the account-restricted GitHub-hosted Actions runner. The connected GitHub repository `ccpcerp/ccpcerp` already contains an independently established opt-in CircleCI test configuration on the current Finance release branch. **But `ccpcerp/ccpc-frappe-deployment` (this deployment/Codex repo) did not have `.circleci/config.yml` on PR #39 review branch, its PR33 base or main**, as checked through the connected GitHub tools. Whether the deployment repository is connected to the owner's CircleCI organization and whether free credits remain is **not known**; the available plugin directory search exposed **no CircleCI connector**, so this assistant cannot inspect CircleCI account state or trigger its pipelines.

**Review-only GitHub changes (no external connection/run):**
- Added `.circleci/config.yml` on `review/codex-proxy-network-hardening-2026-11-19` at verified commit `11e7b3944a76d74047e3b936d27438ee038ea013`. Its single workflow has a boolean `run_codex_source_tests` pipeline parameter **default false**, a full-SHA `approved_codex_commit` string **default empty**, an explicit approval/hold job, and branch filters locked to the reviewed PR #39 head branch. Its single `cimg/python:3.14`/`small` executor checks CircleCI repo/branch/job identity, nonempty pipeline/workflow/job metadata, exact checkout `CIRCLE_SHA1` matching the manually approved full SHA, expected source files and unchanged worktree. It then verifies **exactly 75** unittest methods and runs the entire source-only suite under 120 seconds. No Docker daemon, Frappe, database, Squid, Codex CLI, credentials, deployment actions, cron/schedules or automatic PR push tests are configured; workflow remains disabled until the operator manually opts in.
- Added `docs/ccpc-project/CODEX-LAB-CIRCLECI-REVIEW.md` with plan/credit review, deployment-repo connection check, exact-SHA/manual pipeline parameters, approval hold, log validation and unchanged release NO-GO conditions, at verified commit `a9fe5b09f8b131fe502b160abd8ed1490754837e`.
- Copied the **exact fetched CircleCI YAML** to an isolated local validation file, computed Git blob SHA `06548b915e3685f655cccefa4bd9a122613a8cce` and matched the connected GitHub blob SHA. Parsed it with PyYAML 6.0.3 and passed **six structural guard assertions** (parameter defaults, workflow condition, manual approval, job dependency, small resource). This is **YAML static validation**, **not** CircleCI's config validator or a real CircleCI run.
- CircleCI's current official documentation confirms that parameters default false can gate workflows using `when`, and a pipeline may be manually triggered with supplied parameters through CircleCI's web app. CircleCI credits are usage-based; do not infer a particular free balance or automatic free operation from the account's existence.

**Important:** Merely committing this YAML does NOT create a CircleCI project or authorize its onboarding. No CircleCI connection, jobs, approvals or credits were used by this session. The existing GitHub Actions YAML remains unchanged but blocked by the owner's supplied account-eligibility annotation. No change to unrelated `ccpcerp/ccpcerp` CircleCI jobs.

**Next safe step:** Ask the owner only whether the *deployment* repo `ccpcerp/ccpc-frappe-deployment` is already listed/connected in the CircleCI dashboard, and independently have them check plan credits before any manual pipeline. If it is not connected, require separate authorization to connect/enable triggers and review any CircleCI account or org policies. No run or paid change without explicit approval.

**NO-GO unchanged:** 75/75 offline Python pass does not establish actual firewall/boot persistence, launch enforcement, Squid DNS/egress or negative runtime isolation. Draft PR #39 remains unmerged, Codex stopped at last operator snapshot, optional bridge uncreated, and DEVELOPMENT/PRODUCTION untouched.

## Immediate next action

The GitHub Actions annotation has identified an account payment/spending-limit eligibility blocker before any runner steps. No billing change is approved or requested. Continue **independent no-cost offline code validation** and review unbypassable startup gating, firewall reload persistence, the second bridge, Squid egress and controlled nonproduction negative tests. No host command is requested at Step 94.

**Release gate:** NO-GO. Draft PR #39 remains unmerged. Agent stopped, Squid inactive, bridge uncreated, DEVELOPMENT and PRODUCTION untouched.

## Step 105 — review-only scoped restore and offline startup interlock (2026-11-20)

After the owner approved implementation and testing of firewall persistence/startup controls, source-only changes were committed to PR #39's review branch. The user has **not** approved any exact host installation command, UFW reload, Docker restart, firewall mutation, boot hook enablement or Codex/Squid start. The production server, protected DEVELOPMENT and UAT remain untouched.

- NEW `scripts/security/ccpc_codex_lab_firewall_reconcile.py`: root-only `restore` action requires an independently created exact-content, root-owned `/etc/ccpc/codex-lab-firewall-restore-authorized` marker, nonworld/group-readable, plus the original read-only host identity/stopped-agent/UFW checks; uses an exact lock and plans only missing original-lab tagged DROP rules. Refuses partial/modified/duplicate/displaced tagged rules, unsafe top-of-chain result or any unapproved second proxy-bridge rule. Inserts scoped rules into the existing `INPUT` and `DOCKER-USER` chains; exact verification follows, with rollback **only of its own additions** when the stopped-agent host condition remains verifiable. If that safety condition cannot be reconfirmed, leave restrictive insertions in place instead of weakening a possibly running agent. This is no substitute for host-level concurrency controls, kernel-wide policy, persistence or rollback validation.
- UPDATED inert `scripts/security/systemd/ccpc-codex-lab-firewall-restore.service.example`: invokes new reconciler rather than legacy broad `ccpc_codex_dev_lab_firewall.sh apply`. Sample unit remains **uninstalled** and cannot establish UFW/Docker chain reload preservation or block a privileged manual `docker start`.
- NEW `scripts/security/ccpc_codex_lab_start_interlock.py`: root-marker-gated, **read-only offline prelaunch check** of original bridge protection, stopped-agent runtime limits, an immutable pinned bench image reference, nonroot/read-only/capability restrictions, no Docker/host binds, only the existing internal bridge and no public ports. It has no start/restart/monitor/stop methods and always reports `agent_launch_authorized=False`. Current host container was historically not pinned/capped and has an existing synthetic DB-user secret bind; this source proposal is **not** a directly runnable host approval gate until separate image, mount and runtime profile review. The online proxy path is explicitly excluded and remains prohibited.
- NEW 17 mocked reconciler and 20 mocked interlock tests; historical 66 Compose + 15 firewall-guard tests remain. GitHub Actions [run 44678740312](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44678740312) at commit `04165711e910c286da38cca3c27bf966b202b07a` **executed all 118 tests with 0 failures/errors**. This is mock/source test evidence only, not a host install, UFW integration test, reboot test or effective launch interlock. An earlier intermediate commit failed CI because an existing static unit-template test still expected the old script; the corrected reviewed head passed.

**Mandatory remaining work before host installation:** independently review actual root-controlled marker/install paths, immutable source placement/permissions, service ordering and reload behavior, bridge/iptables identity across Docker daemon restarts, UFW reload reapplication (or stronger network policy independent of UFW), continuous protection while running, manual Docker-start bypass controls, negative controlled nonproduction network probes, image signature/digest and actual container resource/mount constraints. A polling health guard or systemd oneshot alone does **not** provide a zero-exposure fail-closed network guarantee. Do not authorize agent startup from these review-only changes. Before any host write, present the exact scope/commands, approved SSH recovery path, and exact rollback of only newly installed artifacts.


## Step 106 — independent nftables runtime isolation candidate (2026-11-20)

**Scope:** Owner approved continued engineering of runtime protection. All changes remain confined to GitHub and GitHub-hosted disposable CI: no host firewall/Docker/UFW/nftables/systemd mutations, network creation, agent/proxy start, DEVELOPMENT or PRODUCTION access. The last observed stopped state remains operator-reported Step 104, not a new live-host inspection.

**Defense-in-depth concept:** The previous idempotent original-lab iptables reconciler and per-launch read-only guard cannot prevent an exposure window if a Docker/UFW reload destroys the rules. A separately controlled nftables inet table, with hook priority -301, could block host-in, host-out and cross-bridge forwarded traffic for the original Codex bridge independently of the iptables-nft filter chains. Native nftables DROP verdicts cannot be undone by a later ACCEPT in another base chain; nevertheless this is a proposed independent policy, NOT a demonstrated reboot/reload-persistent or bypass-proof kernel barrier. Native semantics references: https://netfilter.org/projects/nftables/manpage.html and https://documentation.ubuntu.com/security/security-features/network/firewall/nftables/ .

**Source on draft PR #39:**
- NEW scripts/security/ccpc_codex_nft_guard_review.py: defaults to read-only plan, renders an in-memory candidate table inet ccpc_codex_lab_guard for the exactly verified br-12hex bridge. Three scoped input, output and forward chains have accept defaults for unrelated traffic, and four interface-specific DROP rules. Neither a broad nft flush nor an installation/daemon/start command exists.
- Read-only verify requires the original root/stopped-agent/internal-lab identity, original iptables safeguards, and an exact nft -j list table JSON snapshot. It refuses absent/mutated/extra rules, unexpected hook/priority/policy, host source narrowing, broadened interface matches and ACCEPT verdicts. JSON version normalization on the real target host remains untested; unsupported representations fail closed.
- UPDATED scripts/security/ccpc_codex_lab_start_interlock.py: offline prelaunch check also requires this independently verified nft layer before it can report a static preflight pass. It remains unable to start/stop/monitor Codex, and success never authorizes launch.
- NEW codex-dev-agent/tests/test_independent_nft_guard.py: 20 mocked tests and one additional interlock negative test. The entire suite now discovers **139 Python security tests** (66 Compose + 15 original guard + 17 reconciler + 21 offline interlock + 20 nft guard). GitHub Actions and manual-only CircleCI count gates reflect 139.

**Verified tests:** GitHub Actions [run 44680095608](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44680095608) at commit 5dd2cfae04243d0276ae7c7aac87c34b2ef318c7 passed 139/139 mocked/source tests. A later [run 44680327848](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44680327848) at commit 1c2f1f0195c068f3fe4d119b144d28dc50fe5190 also passed 139/139 and a **native nft --check --file -** parser validation of the proposed synthetic-interface policy on a disposable GitHub-hosted Ubuntu runner; no rules were applied. Neither CI run examined live CCPC host isolation.

**Unresolved threats and host gate:** (1) The original bridge host interface name is derived from a Docker-generated network ID; Docker network recreation can make previously installed name-matched nft policy ineffective. (2) An nftables.service or administrative flush ruleset can remove a separate table; ordinary UFW/Docker reload survival is not known on this host. (3) nft syntax acceptance does not prove packet-path routing or negative egress canaries. (4) A privileged manual Docker start or firewall flush can bypass cooperative prelaunch checks. (5) The online proxy and separate outgoing/DNS policy are unverified. A systemd oneshot or polling process cannot promise zero exposure.

**Next single step:** Perform a sanitized, read-only live-host preflight with the agent stopped: verify nftables availability, kernel parser support using nft --check without applying rules, current dedicated-table absence/presence, nftables.service status, and whether the bounded main nftables config contains a global flush statement. No daemon reload or Docker restart. The result informs an exact reviewed maintenance/recovery design. Before any installation/reload, separately approve the precise commands, two-session SSH recovery, private scoped firewall snapshot, rollback of only newly added objects, and nonproduction negative network tests.

**Codex release gate remains NO-GO.**


## Step 107 — original-host nftables check-only pass and inactive global-flush risk (2026-11-20)

The owner ran the bounded read-only nftables capability preflight on `ccpcerpserver` and reported:
```text
main_nft_config_flush_ruleset=True
main_nft_config_has_includes=False
agent_stopped=True
original_bridge_identity_verified=True
independent_nft_table_already_present=False
nft_userspace_and_kernel_query_available=True
nft_candidate_check_only_passed=True
nftables_service_active=False
nftables_service_enabled=False
nft_reload_persistence_verified=False
ufw_docker_reload_persistence_verified=False
agent_launch_authorized=False
NO_HOST_CHANGES_PERFORMED
```

The proposed nftables table is **not installed**. Target-host check-only acceptance establishes syntax compatibility, not applied packet filtering, reload survival or a safe Codex launch. The main host nftables configuration contains an active `flush ruleset` directive, while `nftables.service` is inactive/disabled. Starting or reloading a service that loads that file could delete unrelated UFW/Docker-managed kernel firewall rules. These are **operator-supplied observations** rather than direct ChatGPT access, and exact effective systemd unit commands have not been inspected. Do not enable/start/reload/stop nftables.service, run `nft -f /etc/nftables.conf`, reload UFW, restart Docker or start/attach Codex in response.

**Design consequence:** Do not propose enabling the stock nftables.service as the persistence solution. First inspect the **effective systemd ExecStart/ExecReload/ExecStop** paths (and relevant UFW/Docker dependencies) in a read-only host command which returns only boolean status; keep the existing global-flush file untouched. The alternative must have a narrowly scoped independent table policy, install/reconcile only that table, avoid all global flushes, preserve administrative SSH/DEVELOPMENT connections, and be proven against a controlled reload/bridge-recreation sequence with a separate operator-approved recovery plan. A separate table still does not guarantee zero-gap policy during privileged mutation; DO NOT launch Codex until stronger enforcement and isolated negative traffic tests pass.

**Codex activation NO-GO.** PR #39 remains draft/unmerged; no current host installation approved.
