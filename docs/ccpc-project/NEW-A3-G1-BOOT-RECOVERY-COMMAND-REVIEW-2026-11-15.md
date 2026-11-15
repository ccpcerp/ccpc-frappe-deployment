# NEW A3 — G1 boot/recovery change and rollback review (NOT EXECUTABLE / NO APPROVAL)

**Prepared:** 2026-11-15 (Asia/Manila). **Scope:** documentation-only command-level decision record on draft PR #35. This is **not** an authorized operator runbook, tested startup gate, installation approval, or reboot approval. **G1 BLOCKED; employee PRODUCTION NO-GO.**

## Entry checkpoint

The operator reported R0 root-only once-only manifest capture and independent NEW-host `--live-readonly` PASS, with four expected verification markers. R0 matched 19 protected container identities, pinned candidate six and image, internal network/private frontend IP/relay, volumes, current systemd boot state, and effective paused scheduler/muted emails. The 38/38 synthetic Python tests and live R0 read-only check are distinct evidence; neither proves a reboot. Protected manifest stays immutable on NEW, must never be printed, regenerated, overwritten, uploaded or weakened.

At this checkpoint: six **existing** `ccpc_prod_erpnext` candidate containers are running with `RestartPolicy=no`; Docker/containerd are active and enabled; HTTPS `caddy.service` and `ccpc-erpnext-upstream.socket` are active but disabled at boot; companion relay service is static, `caddy-api.service` masked. No Docker Compose recreation, migration, workers, scheduler, emails, WAN access, restore, restart, enablement or reboot is authorized.

## Proposed ownership choice (for owner review; not implemented)

1. **Docker owns candidate process recovery:** only the six exact manifest-pinned, currently running candidate container **IDs** would change to `unless-stopped`, **without recreation, stopping, image change, network replacement or volume change**. Docker would restart those processes after unexpected exit/host boot, subject to the documented `unless-stopped` limitation for containers manually stopped before restart. No bulk `docker update` by container-name pattern.
2. **One NEW-only systemd boot gate owns external exposure:** new root-owned, reviewed one-shot unit ordered after Docker/network readiness. Its source (to be separately implemented/tested) verifies original candidate identities, the private network/IP/relay, persistent mounts, liveness (healthy MariaDB; Redis cache and queue PONG; backend/frontend login and websocket), paused scheduler and muted email before starting the **already installed** loopback upstream socket **then** Caddy. The gate, not Caddy/socket independently, is the only new boot-enabled unit. No gateway activation on a failed fresh-boot gate.
3. **All other protected assets are observation-only:** the other **13** existing Docker containers and their volumes (rehearsals / independent restore drill including the intentionally exited backend) must never be updated, started, stopped, recreated or cleaned by G1. Their post-reboot running state **cannot** be assumed: the current R0 guard expects a pre-boot snapshot and is not a post-change/post-reboot acceptance oracle.

**Rejected shortcut:** immediately `systemctl enable caddy.service ccpc-erpnext-upstream.socket` without readiness gating could serve a stale relay IP or partial application. **Alternative:** a single systemd-managed candidate starter with all six restart policies kept `no`; this avoids Docker auto-resume but needs a separately designed process-failure recovery scheme. Do not use both ownership models together.

## Required dependency evidence BEFORE locking an executable plan

Obtain only sanitized, read-only **NEW host** evidence, under a separate reviewed operator step. No root manifest JSON, credentials, certificates, raw environment, site configuration or Docker inspect dump in chat/GitHub.

- Confirm exact 19 root-only manifest IDs still present, the candidate six running and all 13 noncandidate identities preserved. Record **noncandidate restart-policy classes privately**; after boot they must not unexpectedly auto-start duplicate Frappe/restore workloads. Any noncandidate automatic-start policy is a **STOP / separate risk decision** rather than a license to change it.
- Confirm Docker daemon/socket/containerd boot dependencies, shutdown behavior, and Compose restart policy interactions. No `compose up` or container creation.
- Confirm installed `caddy.service`, `ccpc-erpnext-upstream.socket`, `ccpc-erpnext-upstream.service` unit dependencies, actual `ExecStart`, `WantedBy`, `Requires`, `After`, activation paths, current active/enabled/static/masked dispositions and unit-file ownership. Check no indirect boot trigger could activate Caddy/socket ahead of the gate, and no dependency cycle with a gate starting either unit.
- Confirm socket is loopback-only at `127.0.0.1:8080`, Caddy binds only the approved LAN HTTPS surface, `caddy-api.service` remains masked, no candidate host-published ports, private internal six-member network unchanged, frontend IP equals the installed relay target and exact manifest match. Network reconnection after power failure must not be assumed to preserve IP.
- Confirm independent safety of auto-resuming the existing backend: scheduler paused and email muted **do not by themselves prove** no hooks, delayed integrations, queue processing or outbound writes. This is an explicit owner risk/signoff item before enabling automatic startup.
- Confirm on-host Python version, read-only probe availability, service executable paths, probe timeouts, mount availability, logging/alert mechanism, available disk space, preserved rollback access and NEW-only host identity. Manual console recovery and UPS/power conditions are separate prerequisites for a future reboot.

## Proposed exact **effect classes** and guarded command interfaces (not ready to run)

A review-only G1 gate source and systemd unit now exist in draft PR #35. The source contains an explicit **G1_ACTIVATION_REVIEWED = False** interlock that prevents `--gate-once` from performing any systemd starts. These are review contracts, **not commands for the operator to paste**; lifting the interlock requires a separate reviewed change with verified Caddy bind/security configuration, systemd dependencies, source SHA256, NEW identity, and fresh owner approval.

| Stage | Proposed constrained change | Observable postcondition | No-go / compensation |
| --- | --- | --- | --- |
| G1-A — source | Add versioned, fail-closed NEW-only Python G1 gate and offline tests in PR #35 or a follow-on review PR; derive immutable IDs from already protected **read-only** R0 manifest, never from guessed names. Separately review a root-owned one-shot systemd unit before any installation | Unit/script code diff, dependency graph and tests reviewed; no NEW file changed yet | Preserve PR as draft; do not execute |
| G1-B — stage | With separate consent, install verified source to a **new root-only path** and new reviewed `/etc/systemd/system/ccpc-new-a3-g1-boot-gate.service`, using no-overwrite protections and exact SHA256 | Correct root ownership/mode, no existing Caddy/socket/Docker unit overwritten; `systemd-analyze verify`/graph checks PASS | No overwriting/cleanup; preserve evidence and stop |
| G1-C — Docker policy | A guarded **NEW-only** executor must check the immutable manifest, state and exact six IDs immediately before each `docker update --restart=unless-stopped <pinned-candidate-ID>` (one by one); verify the same complete container IDs, mounts and network after each mutation | Six original IDs persist, six policies now `unless-stopped`, no other policy changed, no restart/recreation or data write by executor | On partial failure, halt; supervised compensation restores only changed exact IDs to `--restart=no` after verifying IDs and current state |
| G1-D — enable boot gate | Following successful preflight, `systemctl daemon-reload` and `systemctl enable ccpc-new-a3-g1-boot-gate.service` **without `--now`**; Caddy/socket remain disabled; do not boot or test start implicitly | Only new gate enabled, installed service dependencies verified, current HTTPS pilot remains unchanged | `systemctl disable ccpc-new-a3-g1-boot-gate.service`; preserve files; do not stop healthy gateway |
| G1-E — separate boot test | **Only** after an entirely separate supervised reboot approval/backup+rollback check, test NEW-only boot with original six IDs and volumes, app readiness, relay/IP, HTTPS/LAN, flags, noncandidate preservation and guest/WAN denial | Recovered NEW candidate/gateway actually verified across reboot | STOP on mismatch; do not reconstruct/recreate anything; use manually approved recovery procedure |

**Unit contract proposed for review:** `Type=oneshot`, `WantedBy=multi-user.target`, ordered after `docker.service` and appropriate network readiness; bounded `TimeoutStartSec`; invoke only a pinned root-owned Python G1 gate. **Do not** put `Wants=` or `Requires=` to Caddy/socket in the boot gate so systemd cannot auto-activate the gateway before checks. An internal gate starts upstream socket first and Caddy second, after all checks pass. Validate the actual installed unit graph and startup timing before drafting final unit text. No `ExecStop` that could stop a healthy gateway or candidate.

**Gate profile:** the old R0 snapshot is *pre-change immutable evidence*, not a reusable PASS oracle after policy changes or reboot. The new G1 verifier must explicitly accept only six approved policy differences while continuing to pin immutable IDs/image/volumes/network and deny unexpected candidates, with a reviewed noncandidate post-boot-state policy. No silent baseline rewrite, automatic fallback, mutable manifest, or bypass of `STOP`.

**No auto-remediation:** no `docker start/stop/restart`, `compose up`, image pull, database command, volume restore, scheduler/mail enablement, old-host switch, firewall, DNS/certificate mutation, or privileged log dump. On timeout the new gate exits nonzero with sanitized status and does not newly activate the gateway. If Caddy/socket were independently already active when manually inspected, a failed gate must **not** tear them down; fail-closed guarantee is conditional on their confirmed lack of independent boot activation.

## Rollback contract, subject to exact source/host review

Rollback must be **idempotent, identity-checked and narrowly authorized**, never an unconditional paste of commands:

- Restore only the six exact pinned candidate IDs' Docker policies to `no` via guarded `docker update --restart=no <pinned-candidate-ID>` when safe; verify complete original container IDs still match. This is a metadata change and must not stop or recreate running containers.
- Disable **only** the newly installed `ccpc-new-a3-g1-boot-gate.service` (if enabled), leaving pre-existing Caddy/socket **active/disabled**, the static proxy and masked Caddy API service as they were. No blanket `systemctl disable --now`, no gateway stop and no deletion of existing units/data.
- Do not overwrite/recreate the old R0 manifest to obtain a synthetic PASS: new post-change verification compares immutable identity invariants and expected approved policy/configuration deltas.
- If the six candidate IDs, mounts, network, relay or site flags differ, **STOP instead of rollback by guesswork**. Escalate for explicit recovery authorization; no replay of consumed backup/restore executors.

## Required tests and approval gates

Before any host write: syntax/static review; Python synthetic PASS and STOP cases for wrong host, root/manifest permissions, extra/missing/replaced container, noncandidate auto-start hazard, invalid image/network/volumes/IP/relay, published ports, unsafe site flags, DB unhealthy, Redis unavailable, login failure, websocket failure, timeout, gateway unit drift, partial Docker-policy change and partial rollback; systemd unit validation and dependency-cycle review. A synthetic PASS does **not** establish real NEW reboot recovery.

Separate decisions: (a) approve reviewed read-only dependency collection, (b) approve exact G1 script/unit installation and policy changes with rollback, (c) approve a future supervised NEW-only reboot, and (d) after G1–G7 independent evidence, approve employee cutover. None is granted by R0 PASS, writing this document, or opening/merging a PR.

**Next engineering action:** review the new source/test/unit draft in PR #35; then prepare a separate owner-approved, strictly sanitized **read-only NEW-host dependency inventory** for installed Caddy security bindings, systemd activation graph, noncandidate restart policies, startup risk and rollback viability. After those results are reviewed, complete and re-test the gate source before requesting separate installation/policy approval. Keep PR #35 draft; no Ubuntu operation has been authorized under this milestone.


## November 15, 2026 — G1 GitHub-only source and synthetic test implementation (owner authorized)

**Source milestone complete; live G1 remains BLOCKED and staff cutover remains NO-GO.** GitHub PR #35 now contains:

- `scripts/ccpc_new_a3_g1_boot_gate.py` — non-executing offline fixture mode, NEW-host read-only inspection mode, a separate draft `--gate-once` mode, exact original 19 protected identities, post-change six-candidate `unless-stopped` policy profile, all 13 noncandidate containers required to retain `RestartPolicy=no`, pinned volumes/internal network/frontend IP/relay, Caddy/socket disabled-at-boot checks, DB health, Redis PONG, Frappe backend/frontend HTTP200 and websocket TCP readiness, bounded polling, sanitized STOP. **The activation mode is deliberately hard-blocked** by `G1_ACTIVATION_REVIEWED = False` pending host dependency verification and new explicit approval. This draft has no Docker policy editor, no Compose invocation and no auto-start/stop of other containers.
- `scripts/ccpc-new-a3-g1-boot-gate.service` — **review-only**, `Type=oneshot`, after Docker, new-unit-only `WantedBy=multi-user.target`, no direct `Wants=/Requires=` Caddy/socket link, no `ExecStop`, 260-second unit timeout, no `--now`. **Not installed, enabled or started on NEW**. Source verifies its exact pinned SHA256 (unit source SHA256 `be8af72e5e05abe1cabe28cdedb184597db9e1510f91b21e4f48af51e85cd274`).
- `tests/test_ccpc_new_a3_g1_boot_gate.py` — **10/10 synthetic/offline unittest methods PASS** with many additional negative subcases. Cases exercise prechange/postchange and pilot/cold profiles, identity/missing/extra resources, stopped/replaced candidates, preserved drill exited state, noncandidate auto-start hazard, partial restart-policy changes, port exposure, image/volume/network/IP/relay drift, scheduler/mail flags, unexpected gateway activation, Caddy API mask drift, service-start sequencing/failure, wrong host, unit hash mismatch, fixture-only mode, and activation interlock. Test fixtures use a **mock R0 contract**, not a live NEW host.

Source and test files were exercised locally with `python -B -m unittest discover -s tests -p 'test_ccpc_new_a3_g1_boot_gate.py' -v` and then the exact matching Git blobs were independently verified via the GitHub connector: gate blob `4b5764d9b42c6ae39e4e67e981cb8a664074d02c`, unit blob `826762847101af35b83d6c708c1808ea82b6b422`, tests blob `cfa3267d53a063de977ee1ef635297ec22329bdc`. Python compilation passed. An offline `systemd-analyze verify` attempt could not resolve `docker.service` on the ephemeral test environment; **this is not a tested NEW-host systemd dependency graph**. No CI run or NEW-host integration execution has been claimed.

**Outstanding blockers before even removing the interlock:** verify on NEW with separate read-only permission (1) all 13 noncandidate restart policies and any indirect boot triggers; (2) installed Caddy configuration, HTTPS LAN bind/allowlist/certificate references and drift pinning, not merely its active systemd state; (3) exact upstream socket/Caddy/systemd dependency graph and any drop-ins or automatic activation paths; (4) explicit confirmation that auto-resuming backend cannot cause unauthorized writes/integrations despite muted email/paused scheduler; (5) unit/source on-host path/mode/source hash and rollback prerequisites, with any discoveries turned into reviewed source/test changes. The current G1 draft **does not yet attest Caddy config/port security at runtime**, and TCP-only websocket probing does not prove Engine.IO handshake. Do not interpret offline PASS as boot resilience.

**No operator action now:** preserve the immutable R0 manifest; do not stage G1 on NEW, change any of the six Docker policies, enable services, reboot, merge PR #35, or cut over staff access. Future read-only dependency collection, installation/policy change, reboot test, and employee cutover each require separately reviewed and explicitly approved scopes.


## November 15 — G1 read-only dependency inspection approval and first reviewed operator step

The owner explicitly approved a **read-only NEW-host dependency inspection**, following the previous GitHub-only source/test milestone. This approval is **limited to passive observation**: no install/staging of G1 code, Docker policy changes, gateway service start/enable, unit-file writes, manifest recapture, restart, migration, production data edits, reboot, WAN exposure or employee cutover.

**First step, pending operator execution:** inspect only the 19 protected Docker identities, statuses and current restart policies against the **existing immutable R0 root-only manifest**. GitHub review-only file [scripts/ccpc_new_a3_g1_dependency_policy_readonly.py](../../scripts/ccpc_new_a3_g1_dependency_policy_readonly.py), SHA256 \`5f32439574fb45f11d24686ae6c2c89bbbc87c5179b090c94d2730a69ad1359d\`, Git blob \`e9255dfbdafb61e195793f51112869b333463d09\`, on review branch PR #35. Seven independent synthetic/offline unittest methods PASS, including wrong host/operator, name/ID drift, candidate/noncandidate restart policy drift, and unexpectedly running preserved failed backend. Test Git blob \`53d45f511e2f92bf5b313827322bb68e3b251978\`. No NEW server accessed by offline testing.

Operator should run the **exact audited Python source in memory** with \`sudo python3 -B -\` as a pasted here-document on \`ccpcadmin@ccpcerp-prod\`. Do not save/download/stage scripts or inspect/print manifest JSON. Script reads only root-only manifest metadata and issues \`docker ps -a --format\` and \`docker container inspect\` (captured internally, not printed), then prints only four PASS status markers or one STOP marker. It has no Docker update/start/stop, systemd, database/bench, network, file-write or HTTP call.

Expected success markers:

\`\`\`
CCPC_NEW_A3_G1_PROTECTED_IDENTITIES_19_PASS
CCPC_NEW_A3_G1_CANDIDATE_POLICY_NO_6_PASS
CCPC_NEW_A3_G1_NONCANDIDATE_POLICY_NO_13_PASS
CCPC_NEW_A3_G1_POLICY_READONLY_CHECK_PASS
\`\`\`

On \`CCPC_NEW_A3_G1_POLICY_STOP_REVIEW_REQUIRED\`, exceptions, or any missing marker, **STOP** and review safely; do not modify policies or container state to force PASS. The script does not disclose the specific failed rule; its only conclusion is whether the exact baseline matched at the time checked. PASS does **not** prove backend auto-resume safety, installed Caddy security scope, unit graph, or boot resilience. **Next after verified PASS:** separately prepare the remaining Caddy/systemd checks inside the same read-only inspection approval, one reviewed step at a time.

No running NEW, OLD PROD or DEV service was changed to prepare this inspection. Formal G1 remains BLOCKED and production cutover NO-GO.


## November 15 — G1 Step 1 protected Docker restart-policy inspection — operator PASS

The operator on NEW reported the four exact success markers from the scoped read-only policy audit:

```text
CCPC_NEW_A3_G1_PROTECTED_IDENTITIES_19_PASS
CCPC_NEW_A3_G1_CANDIDATE_POLICY_NO_6_PASS
CCPC_NEW_A3_G1_NONCANDIDATE_POLICY_NO_13_PASS
CCPC_NEW_A3_G1_POLICY_READONLY_CHECK_PASS
```

**Result: G1 Step 1 PASS, at inspection time.** The 19 pinned identities, expected 18 running plus one preserved failed isolated backend, six candidate `RestartPolicy=no`, and thirteen noncandidate `RestartPolicy=no` met this script's checks. This is **operator-reported live evidence**, separate from seven offline synthetic tests. The script has no write actions. It does **not** prove a successful reboot, independent gateway boot ordering, Caddy's precise LAN-only security configuration, backend job safety, or that the values will remain unchanged.

**Next within the existing approved read-only inspection:** a separate one-step NEW-host systemd unit-state and scoped TCP listener inspection; review actual Caddy configuration and unit/drop-in graph after that without disclosing credentials. Do not enable the gateway, alter Docker restart policies, re-create the protected R0 manifest, install the G1 draft or reboot. G1 still BLOCKED and employee production cutover NO-GO.

## November 15 — G1 Step 2 systemd and listener inspection prepared (operator execution PENDING)

Under the already-approved **read-only NEW-host dependency inspection** scope, a second, independent one-shot in-memory audit is reviewed. It is NOT an installation or execution approval for the G1 startup gate. The operator has not yet reported Step 2 output.

- Source: [`scripts/ccpc_new_a3_g1_unit_listener_readonly.py`](../../scripts/ccpc_new_a3_g1_unit_listener_readonly.py), exact Git blob `1cc2fb042fae6da2631c03911bfe0fc09b86d19d`, SHA256 `c56d441cba3ff4f813659933af261ba243d2942cfa0fa9868d8e79b79b5ad8fa`. Execute its reviewed contents in memory using `sudo python3 -B -` only from `ccpcadmin@ccpcerp-prod`; no download, staging or service changes.
- Test: [`tests/test_ccpc_new_a3_g1_unit_listener_readonly.py`](../../tests/test_ccpc_new_a3_g1_unit_listener_readonly.py), exact Git blob `1c9b9fd0a5e5bcbdc4b31dc21414056d1e7d43a8`. **6/6 synthetic tests PASS** with exact identical Git blob source and test content, covering baseline, public 443/8080 listeners, independent Caddy enablement, unexpected G1 gate installation and unmasked Caddy API.
- Read-only operations: `systemctl show` with only `LoadState,ActiveState,UnitFileState` for Docker, containerd, Caddy, upstream socket/relay, masked Caddy API and proposed G1 gate; `ss -H -ltn` listening TCP ports parsed internally. This audit compares existing expected pilot state, requires G1 unit to remain not installed, requires TCP 443 only bound on `192.168.50.186` and TCP 8080 only bound on `127.0.0.1`. It does not inspect or disclose Caddyfile contents, certs, raw systemd unit text, env, manifest, Docker inspect, keys or passwords. It never writes files or changes services.
- Expected markers: `CCPC_NEW_A3_G1_SYSTEMD_BASELINE_PASS`, `CCPC_NEW_A3_G1_GATE_UNIT_NOT_INSTALLED_PASS`, `CCPC_NEW_A3_G1_HTTPS_443_LAN_BIND_PASS`, `CCPC_NEW_A3_G1_RELAY_8080_LOOPBACK_BIND_PASS`, `CCPC_NEW_A3_G1_SYSTEMD_LISTENERS_READONLY_PASS`. Failure marker: `CCPC_NEW_A3_G1_SYSTEMD_LISTENERS_STOP_REVIEW_REQUIRED`; any STOP overrides earlier partial PASS, no retry/modification without review.
- **Important limitations:** checking active TCP listeners and top-level unit states **does not prove** the content or effective routing of Caddy, TLS trust, WAN/guest denial, indirect systemd boot dependencies/drop-ins, UDP/QUIC listeners, scheduler/runtime safety, or recovery after a reboot. Detailed Caddy/config/systemd graph inspection is a separate next step, not presumed PASS. No G1 boot change, reboot, or cutover permitted.
