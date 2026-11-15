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

The executable source **does not exist yet**. These are review contracts, **not commands for the operator to paste**; actual commands require code review, negative offline tests, source SHA256 pinning, NEW identity verification and a separate owner authorization.

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

**Next engineering action:** implement/review the fail-closed G1 code + synthetic tests and resolve the unit/noncandidate dependency gaps **in GitHub only**. Keep PR #35 draft; no Ubuntu command required for this documentation stage.
