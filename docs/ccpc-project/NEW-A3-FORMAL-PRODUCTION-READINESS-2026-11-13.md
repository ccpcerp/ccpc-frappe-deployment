# NEW A3 — Formal PRODUCTION readiness assessment and controlled acceptance gates

**Assessment opened:** 2026-11-13 (Asia/Manila).
**Decision at assessment opening: NO-GO for employee business transactions and production cutover.**
**Target:** dedicated NEW Ubuntu `ccpcerp-prod` (`192.168.50.186`), **actual candidate** `ccpc_prod_erpnext` / site `ccpcerp.local`, not the separately restored drill containers.
**Purpose:** start read-only formal readiness verification in the latest actual operator/GitHub context. Owner's request to "proceed to a formal NEW A3 Production Readiness Check" grants read-only inventory/documentation, **not** release, cutover, restart, enabling services, data migration, DNS/router/CA/client-trust changes or production writes.

## Current G1 GitHub checkpoint — 2026-11-15, no production change

The owner's latest read-only terminal outputs on **NEW** confirm the six exact `ccpc_prod_erpnext` candidate containers are running with `RestartPolicy=no`; both `caddy.service` and `ccpc-erpnext-upstream.socket` are active but disabled at boot. This matches the known **pre-activation** baseline, **not** automatic recovery readiness. The owner subsequently approved **GitHub-only hardening and testing**, excluding host mutations.

On open draft [PR #35](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/35) the exact-ID Docker policy transition has now been further locked: `G1_POLICY_MUTATION_REVIEWED=False` blocks `--apply` and `--compensate` before host/Docker calls, while `--check` remains read-only. Source commit `9756ee5`, test commit `0e2cfdb`, documentation commit `e14f220` are on the **review branch only**. Added two regression methods; **10/10 focused offline tests of the fetched `main()` excerpt passed**, but the updated full module test suite/actual host recovery were **not** run. Details: [G1 policy transition/cutover record](NEW-A3-G1-RECOVERY-POLICY-TRANSITION-CUTOVER-2026-11-15.md).

**Current decision: G1 BLOCKED; employee cutover NO-GO.** Both activation interlocks remain false. Do not change restart policies, install/enable/start any G1 units, restart/reboot, promote gateway access or cut over until the actual deployed process/image provenance and single-writer/OLD-freeze risks, effective Caddy/boot graph, recovery compensation and separate owner approvals are settled. Immediate engineering follow-up: complete the full offline policy regression run under a trusted disposable runner, then close real-runtime single-writer/provenance evidence before proposing a narrowly scoped host operation.

## Scope and authoritative sources

- Source-control policy: [GitHub-first development workflow](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/docs/ccpc-checkpoint-2026-10-10/docs/ccpc-project/GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md).
- New A3 candidate backup: [one-time four-artifact NAS backup checkpoint](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/review/new-a3-isolated-restore-2026-11-12/docs/ccpc-project/NEW-A3-ONE-TIME-SYNOLOGY-BACKUP-2026-11-12.md) (owner-reported exact run `20261112T090214Z-0148d36b2cb678b3`, SHA256 local+Synology readback PASS).
- Independent restored copy: [NEW A3 isolated restore drill](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/review/new-a3-isolated-restore-2026-11-12/docs/ccpc-project/NEW-A3-NAS-ISOLATED-RESTORE-DRILL-2026-11-12.md), latest review commit `80f53ae25c901913a0219f38296622989a748e20`, draft PR #34 open, **not merged/deployed**.
- Earlier [production readiness critical path](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/docs/ccpc-checkpoint-2026-10-10/docs/ccpc-project/PRODUCTION-READINESS-CRITICAL-PATH-2026-10-28.md) lists owner-frozen stock/GL, maker/checker, intercompany billing, reports and security gates; older NO-GO assessment is a historical baseline, not a fresh runtime inspection.
- Application PR [#32](https://github.com/ccpcerp/ccpcerp/pull/32) was confirmed **merged on 2026-11-02** at PR head `7557e4b00f13a16ad9e62dbcf75ffdc52d50a06c`; this does **not** prove its code was deployed in the actual NEW candidate. Deployment HTTPS PR [#28](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/28) is still draft/open as of this assessment. Avoid using old development PR statuses as if they were current. Distinguish GitHub review code, installed image, tested isolated copy, working NEW candidate and live OLD PRODUCTION.

## Verified evidence and limitations at assessment opening

1. **NEW A3 six containers present:** operator's 2026-11-13 read-only `docker ps -a` showed candidate frontend, websocket, backend, Redis queue, Redis cache and healthy MariaDB all `Up`; six November 7 rehearsal support containers were also `Up`. The independently restored drill had six running test services and its original failed backend intentionally `Exited (1)`; **19 expected total, 18 Up + 1 preserved failed evidence**. No host-published ports appeared in the operator's Docker `PORTS` column; `6379/tcp` and `3306/tcp` are container-only exposure, not host publication. This snapshot does not prove next-boot recoverability or full service health.
2. **NEW A3 LAN HTTPS pilot previously worked:** operator-reported Caddy `192.168.50.186:443` and a Windows authorized browser accessed the **actual candidate** Desk and viewed selected Company, Work Request, inventory and accounting history, per the November 12 backup checkpoint. This does not prove all staff devices trust the CA, WAN/guest isolation, persistent boot services, exact permission matrices, or financial posting acceptance.
3. **Four-artifact NAS backup and restore:** exact one-use Nov 12 candidate backup completed with SQL, site config, public and private archives, hashes and Synology readback; a separate isolated restored MariaDB/sites test yielded four Company rows, three File metadata rows and one linked 16,501-byte private file. Isolated backend/frontend `/login` HTTP200, guest private GET denied HTTP403 at both endpoints, Engine.IO polling handshake HTTP200, protected `get_logged_user` guest denial consistent with local installed decorator, and operator later successfully signed in via localhost-only Windows SSH tunnel and informally inspected data. The temporary tunnel then exited. **No full role/permission suite, authorized private-file retrieval, transaction/GL tests, or release approval** follows from these checks. Do not rerun consumed Stage3A/3R/3S/3T or one-use backup script.
4. **Source-to-target freshness NOT proven:** last approved Nov 5 source backup/restore and Nov 12 NEW candidate backup do **not** show OLD PRODUCTION had no intervening writes or that candidate and OLD source remain identical. A separately authorized single-writer freeze, final reconciliation/backup, cutover and rollback will be required.
5. **Boot persistence gap in latest candidate documentation:** the six candidate Docker containers had `RestartPolicy=no`, and Caddy plus `ccpc-erpnext-upstream.socket` were active for the pilot but **disabled at boot**. A NEW-host power failure/reboot may leave employee access unavailable. Do not reboot or enable anything until a safe reviewed boot sequence, exact network targets and recovery procedure are approved.
6. **Business acceptance gap:** one cohesive approved app release and real maker/checker/stockroom separation, Company+category Expense Account and Company+Department Cost Center mappings, Withdrawal Slip → Stock Entry/SLE → Expense GL → intercompany invoices with idempotency/rollback/cancellation, plus four day-one reports and financial reconciliation have **not** been evidenced as passed end-to-end on this actual NEW candidate. No final new-server cutover authorization is recorded.
7. **Security/operations gap:** staff CA trust and browser/phone validation across intended devices; LAN allowlist, negative guest/WAN checks across relevant ISP links, mail/workers/scheduler operational policy, monitored backups with alerts/retention, periodic restore and backup recovery key custody, uptime and post-reboot checks remain pending or not fully evidenced.

## Formal release gates (all mandatory; unverified is not PASS)

| Gate | Acceptance requirement | Assessment opening status |
| --- | --- | --- |
| G0 — Source and isolation | Exactly identify actual NEW candidate vs isolated drill and ORIGINAL OLD PROD/DEV; image/branch/site/volumes/network/ports/status read back, no mistaken writes | **PARTIAL** — Docker names/states known; comprehensive direct candidate inspection pending |
| G1 — Resilience and reboot | Verified non-destructive restart policy and boot/reconnect behavior for app, DB, gateway, relay; backup/recover from power loss | **BLOCKED** — candidate restart policies/boot services documented disabled; no reboot authorized |
| G2 — HTTPS and client security | Valid trusted certificate on approved staff clients, intended DNS, LAN HTTPS/realtime, WAN/guest negative checks, no unnecessary port exposure | **PARTIAL** — owner LAN HTTPS pilot worked; staff-wide trust and WAN denial pending |
| G3 — Data currency and consistency | Final OLD-to-NEW source database/files ledger/user/master/timestamp reconciliation and single-writer/freeze plan; no missing writes | **BLOCKED** — source data freshness not established |
| G4 — ERPNext functional integrity | Authorized real/approved test role, stock, GL, billing and four report end-to-end acceptance incl negative controls, replay/concurrency, accounting reconciliation | **BLOCKED** — informal UI browsing and isolated recovery are insufficient |
| G5 — Permissions and credential handling | Actual Company-scoped maker/checker/issuer privileges and roles, approved employee access, attachment authorization, no secret disclosure | **PARTIAL/UNVERIFIED** — guest file denial checked; positive protected workflows unverified |
| G6 — Backups, monitoring and recovery | Restorable four artifacts, consistent schedules/retention, failure alerts, NAS access control, recovery runbook/rollback drill, power-failure support | **PARTIAL** — one-time NAS backup and independent restore PASS; reliable ongoing operations not established |
| G7 — Owner cutover approval | Exact reviewed release SHA, final backups, freeze and delta checks, release/rollback plan, testing signoffs, maintenance announcement and explicit go-live authorization | **NOT AUTHORIZED** |

**GO/NO-GO:** Currently **NO-GO**. Do not let staff use actual NEW A3 for live business transactions or decommission OLD PRODUCTION. Do not convert the **isolated test copy** into employee production. There is no defensible go-live date/percentage based on this evidence.

## Immediate next operator action — read-only G0/G1 state check

On **NEW Ubuntu** only (`ccpcadmin@ccpcerp-prod`), first inspect exact six candidate Docker containers (identity, running, DB health, restart policy, no host-published ports), along with installed `caddy.service` and `ccpc-erpnext-upstream.socket` **active vs enabled** status. Print sanitized values only; no secrets, volume or user data. **Do not run `docker compose up`, `systemctl enable`, `reboot`, `bench migrate`, `bench backup`, DNS/firewall edits or any container restart.** Once operator output arrives, update G0/G1 evidence and choose the smallest next read-only check. If any guard mismatches, stop and document the unexpected state before deciding anything write-capable.

## Protection and release rule

Keep OLD PRODUCTION/DEVELOPMENT, working NEW A3, both November 7 rehearsals and the completed isolated recovery drill intact, including data volumes, private files, root-only markers, backup artifacts and failed-backend evidence. All prior one-use recovery scripts are consumed. Future NEW changes that could affect services, accounting, permissions, networking, credentials, jobs, reboot, production release or cutover require separately scoped review and explicit approval. GitHub commits document evidence but do not constitute live deployment authorization.

## November 13, 2026 — G0/G1 ACTUAL NEW A3 READ-ONLY RUNTIME AND BOOT-STATE CHECK

- Owner ran exact read-only Python Docker/systemd preflight from `ccpcadmin@ccpcerp-prod` against **working NEW A3** `ccpc_prod_erpnext`, distinct from the independent restored drill. Operator reports:

```text
NEW_A3_RUNNING_CONTAINERS=6/6
NEW_A3_DB_HEALTHY=YES
NEW_A3_RESTART_POLICY_NO=6/6
NEW_A3_HOST_PUBLISHED_PORTS=NONE
CADDY_ACTIVE=active
CADDY_BOOT_STATE=disabled
UPSTREAM_SOCKET_ACTIVE=active
UPSTREAM_SOCKET_BOOT_STATE=disabled
CCPC_NEW_A3_READINESS_READONLY_CHECK_COMPLETE
```

- **G0 infrastructure runtime:** Six exact candidate containers exist and report running, candidate MariaDB health status healthy; Docker inspect `HostConfig.PortBindings` and `NetworkSettings.Ports` showed **no host-published ports** on these six. This does not verify site identity, mounted volumes, pinned image or entire LAN firewall exposure yet. **G0 remains PARTIAL.**
- **G1 reboot resilience:** All six actual NEW candidate containers have `RestartPolicy=no`, Caddy `ActiveState=active` but `UnitFileState=disabled`, and `ccpc-erpnext-upstream.socket` likewise active/disabled. **G1 remains BLOCKED** pending separately authorized, reviewable boot-order and restart design and verification. A surprise power loss/reboot could leave application/gateway unavailable. The present audit does not establish whether another independent boot orchestrator might start components; do **not** conclude it is impossible for any service to start automatically until checking. Do not reboot, enable services, edit restart policies, recreate Docker containers or restart original systems merely to test this.
- **Next one operator read-only inspection:** check only the systemd unit inventory of `docker.service`, `containerd.service`, `caddy.service`, `ccpc-erpnext-upstream.socket`, `ccpc-erpnext-upstream.service` and any CCPC/Frappe/ERPNext startup units without printing `ExecStart`, `Environment`, Caddyfile contents, password/secret paths or application data. This reveals whether an existing launch mechanism exists and determines the safest boot plan before requesting approval for changes. No modification authorized.
- **NO-GO unchanged:** G2 staff security and WAN/guest negative checks pending; G3 OLD-to-NEW current source/cutover consistency pending; G4 end-to-end GL/stock/billing/reports pending; G5 roles/attachments pending; G6 ongoing backup and monitoring pending; G7 explicit final production approval not granted. Preserve all original and test containers, OLD PROD/DEV, Synology copies and one-use markers. Prior recovery --execute stages consumed; never rerun.

## November 13, 2026 — G1 SYSTEMD BOOT UNIT INVENTORY AND STATIC RELAY TARGET RISK

- Owner reports exact read-only `systemctl show` and `systemctl list-unit-files` from NEW `ccpcadmin@ccpcerp-prod`:

```text
UNIT=docker.service
ActiveState=active
LoadState=loaded
UnitFileState=enabled
UNIT=containerd.service
ActiveState=active
LoadState=loaded
UnitFileState=enabled
UNIT=caddy.service
ActiveState=active
LoadState=loaded
UnitFileState=disabled
UNIT=ccpc-erpnext-upstream.socket
ActiveState=active
LoadState=loaded
UnitFileState=disabled
UNIT=ccpc-erpnext-upstream.service
ActiveState=active
LoadState=loaded
UnitFileState=static
=== RELATED INSTALLED SYSTEMD UNITS ===
caddy-api.service masked
caddy.service disabled
ccpc-erpnext-upstream.service static
containerd.service enabled
docker.service enabled
ccpc-erpnext-upstream.socket disabled
docker.socket enabled
CCPC_NEW_A3_BOOT_UNIT_INVENTORY_READONLY_COMPLETE
```

- **G1 operational finding:** Docker/containerd and Docker socket are enabled at boot; Caddy and the socket activation endpoint are currently active but disabled, the companion relay service is active and static (activated via matching socket), and all six real candidate containers `ccpc_prod_erpnext` have Docker `RestartPolicy=no`. No CCPC/ERPNext-named independent boot orchestrator appears among systemd *service/socket* unit filenames; still do not claim cron/timers or other mechanisms exhaustively absent. The current all-up state is not reboot-durable under the demonstrated configuration; **G1 remains BLOCKED**, NO-GO, no change authorized.
- Refetched exact [PR28](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/28) source at open draft branch `docs/dedicated-production-https-gateway-2026-10-23`: `overrides/systemd/ccpc-erpnext-upstream.socket` Git blob `f29d31223876e3c50923c1985ce8cbec0cf603e0` binds only `127.0.0.1:8080`, invokes `ccpc-erpnext-upstream.service`; `overrides/systemd/ccpc-erpnext-upstream.service` blob `e701b9e811beac034a0f72e8538b2093186e02ff` uses a **fixed pilot upstream `172.20.0.7:8080`**, `Restart=no`, and only `Requires/After=ccpc-erpnext-upstream.socket`, **not docker.service or candidate readiness**. `overrides/Caddyfile.dedicated-https.review` forwards to `127.0.0.1:8080`. These are GitHub reviewed source assumptions; installed live unit content must be independently checked before deciding boot changes. A Docker container recreation/IP change would risk a stale upstream address. Never change a live relay blindly or recreate working candidate just to adopt Compose.
- **Next single operator read-only step:** on NEW, inspect **only** the exact frontend container `ccpc_prod_erpnext-frontend-1`, its Docker private IPv4/network and restart policy; then read only the *locally installed* `/etc/systemd/system/ccpc-erpnext-upstream.service` `ExecStart` target **inside a fixed check that does not print the line**, verifying whether target is `<current candidate frontend IPv4>:8080`, IP exact safe RFC1918, and whether socket unit still binds only `127.0.0.1:8080`. Print sanitized `RELAY_TARGET_MATCHES_LIVE_FRONTEND` and other statuses, no credential paths or environment contents. Stop if unexpected. This determines whether the static target is currently matched and how much the boot plan must change. **Read-only and no power-cycle.**
- Still pending: reviewed boot orchestrator preserving original container IDs/volumes, database dependency readiness, Caddy/relay ordering with LAN-only bind, automatic backups/alerting, OLD->NEW reconciliation and single-writer cutover, employee role/permission and G4 financial workflows, separate explicit final owner GO. Preserve twelve originals, both NEW rehearsals, independent restore drill, all markers/NAS backups; consumed scripts NEVER rerun.

## November 13, 2026 — G1 LIVE A3 FRONTEND TO RELAY IP AND LOOPBACK MATCH PASS

- Owner reports guarded **read-only** Python inspection from `ccpcadmin@ccpcerp-prod` of the **actual NEW A3 candidate** frontend `ccpc_prod_erpnext-frontend-1` and two locally installed systemd relay files, without modifying their contents:

```text
NEW_A3_FRONTEND_RUNNING=YES
NEW_A3_FRONTEND_IPV4=172.20.0.7
UPSTREAM_TARGET_MATCHES_FRONTEND=YES
UPSTREAM_SOCKET_LOOPBACK_ONLY=YES
CCPC_NEW_A3_RELAY_READONLY_CHECK_PASS
```

- Installed `ccpc-erpnext-upstream.service` uses exactly `/usr/lib/systemd/systemd-socket-proxyd 172.20.0.7:8080`, matching the one-network running NEW candidate Docker frontend's private IPv4; `ccpc-erpnext-upstream.socket` uses exactly `ListenStream=127.0.0.1:8080`; no candidate Docker host-published ports. This is **PASS for current relay target consistency and loopback-only local bind**, not proof that IP will remain the same across Docker recreation/reboot, nor proof that Caddy/relay and app will auto-recover after power loss. PR28 still draft/open with code relay target fixed to same IP; systemd source `f29d31223876e3c50923c1985ce8cbec0cf603e0` and service source `e701b9e811beac034a0f72e8538b2093186e02ff` were fetched and reviewed. PR28 head `aa1a5dee62ad198112d0443033846aad0aa46e4f`.
- Previous confirmed runtime observations remain: candidate Docker **6/6 Up**, MariaDB **healthy**, `RestartPolicy=no` **6/6**, host-published Docker ports NONE; Docker/containerd active/enabled; Caddy service active/disabled; relay socket active/disabled; relay companion active/static. **G0 isolation/infrastructure PARTIAL PASS; G1 automatic boot/readiness BLOCKED, overall PRODUCTION NO-GO.**
- **Next small read-only check:** on NEW inspect exact six candidate container **network membership, image ID consistency, expected site/logs/data volume names and Docker host port bindings**, plus whether *other* containers using the candidate network are unexpected. Avoid printing mounts' host bind paths, credential locations, environment variables or source application data. These details inform a future **separately approved** preservation-safe startup orchestrator/systemd design, and must be verified before any service enable or Docker policy changes. Do not start/stop/restart containers, change RestartPolicy, rename/recreate images, reboot or enable Caddy/relay.
- Preserve original twelve Docker containers, restored isolated drill seven containers including exited backend evidence, OLD PROD/DEV, all test volumes, root-only one-use markers and Synology backups; consumed stages never rerun. Employee cutover not authorized, no business transactions on NEW until all readiness gates satisfied.

## November 13, 2026 — G0 CANDIDATE NETWORK IMAGE AND VOLUME DEPENDENCIES ALL PASS

- Owner reports guarded root read-only `docker container inspect` and `docker network inspect` on **actual NEW A3 candidate** `ccpc_prod_erpnext` (not restored drill), exact six containers, with eight affirmative checks and final marker:

```text
SIX_CONTAINERS_RUNNING=YES
ONE_SHARED_NETWORK=YES
SHARED_NETWORK_INTERNAL=YES
THREE_APP_CONTAINERS_SAME_IMAGE=YES
APP_SITES_LOGS_VOLUMES=YES
DATABASE_PERSISTENT_VOLUME=YES
REDIS_QUEUE_PERSISTENT_VOLUME=YES
NO_HOST_PUBLISHED_PORTS=YES
CCPC_NEW_A3_DEPENDENCIES_READONLY_PASS
```

- This establishes 6 running candidate containers (DB health guarded), a common single Docker network with `Internal=true`, matching image **IDs** for backend/frontend/websocket (not the exact GitHub app source version unless separately verified), at least the expected persistent `ccpc_prod_erpnext_sites` and `ccpc_prod_erpnext_logs` volumes on the app trio, `ccpc_prod_erpnext_db-data` for MariaDB and `ccpc_prod_erpnext_redis-queue-data` for Redis queue, with **no Docker host-published ports**. Volume checks are subset checks; they do not independently exclude unexpected extra mounts or inspect the exact site database consistency. Network check verifies common internal network, not its label/member allowlist. No volume contents or credentials were displayed.
- Together with prior checks: systemd Docker and containerd active/enabled; candidate 6/6 `RestartPolicy=no`; Caddy active/disabled; `ccpc-erpnext-upstream.socket` active/disabled; socket-proxyd companion active/static; installed relay target exactly matches live frontend private `172.20.0.7:8080` and socket binds `127.0.0.1:8080`. **G0 infrastructure runtime good but still only PARTIAL; G1 reboot resilience BLOCKED; overall NO-GO.**
- **Boot-recovery design recommendation (planning only; no server modifications approved):** preserve exact six existing candidate container identities and named data volumes, avoid Compose `up`/recreate/redeploy/DB migration; separately assess applying Docker `unless-stopped` restart policies to *only these exact six preverified candidate IDs* via guarded `docker update` (not yet authorized) after verifying existing networks, service configurations and dependencies; separately plan enabling **only** existing `ccpc-erpnext-upstream.socket` and `caddy.service` while checking ordering/readiness and route target consistency, and preserve `caddy-api.service` masked. Existing service `ccpc-erpnext-upstream.service` is `static`, socket-activated; do not try enabling it. Boot-time host/frontend IP could drift if Docker endpoints are recreated, so plan an explicit target validation and fail-closed alert/runbook, not blind forwarding to any Docker network participant. Docker restart policies may start app containers before MariaDB is healthy; review health/dependency behavior and do not assume startup order. Favor a bounded operator-approved dry-run safety review **before** changing any policies. Any actual boot changes require explicit separate approval and a rollback procedure. **No reboot approved** until both readiness and recovery plan are reviewed.
- **Next single read-only check:** `systemctl show` allowlisted `After/Wants/Requires` edges for `caddy.service`, `ccpc-erpnext-upstream.socket`, `ccpc-erpnext-upstream.service` and `docker.service` WITHOUT logging `ExecStart`, `Environment`, secrets, raw Caddy config or arbitrary unit text. Inspect whether existing systemd graph imposes an order that could safely survive Docker network/service readiness. This informs a reviewed boot plan without changing an installed unit. Optionally inspect exact Docker image digests and healthchecks after ordering review; never start/restart/stop/recreate any container or enable units in the read-only stage.
- App/finances/employee cutover G2–G7 remain unverified or blocked, including OLD->NEW source freshness and single-writer freeze, staff TLS trust/WAN denial, maker/checker and stock/GL/billing/day-one reports, ongoing backup/alerts, and final owner GO. Recovery drill Stage3A/3R/3S/3T and one-use NAS backup execute consumed; **NEVER RERUN**. Preserve all original 12 and isolated test resources, data volumes, root markers and NAS backups.

## November 13, 2026 — G1 SYSTEMD ORDER EDGES READONLY VERIFIED

- Owner ran the precise read-only `systemctl show ... LoadState,After,Requires,Wants` inspection on NEW `ccpcadmin@ccpcerp-prod` for `caddy.service`, `ccpc-erpnext-upstream.socket`, `ccpc-erpnext-upstream.service`, `docker.service`:

```text
CADDY_AFTER_DOCKER=NO
CADDY_AFTER_UPSTREAM_SOCKET=NO
CADDY_REQUIRES_UPSTREAM_SOCKET=NO
SOCKET_AFTER_DOCKER=NO
SOCKET_REQUIRES_DOCKER=NO
RELAY_AFTER_SOCKET=YES
RELAY_REQUIRES_SOCKET=YES
DOCKER_AFTER_CONTAINERD=YES
CCPC_NEW_A3_STARTUP_ORDER_READONLY_COMPLETE
```

- **Interpretation**: the relay correctly has direct ordering/requirement against the socket, and Docker orders after containerd. Caddy has no direct ordering or requirement against Docker/the socket, and the socket has no direct ordering or requirement against Docker. **Missing direct edges are evidence of absent explicit ordering, not proof the currently running HTTPS path is broken, nor proof that all extra dependencies are necessary**: socket and Caddy can listen before the upstream if client retries and gateway failure behavior are acceptable. For production, a reviewed readiness/failure policy and preservation-safe startup sequence are needed; do not add `Requires=docker.service` blindly or create dependency cycles.
- Prior independently reported observations: exact NEW A3 6/6 running, healthy DB, 6/6 `RestartPolicy=no`, shared internal network; candidate app images consistent, expected persistent sites/logs/db-data/redis-queue-data volumes, no host Docker port binding; installed relay target matches active frontend `172.20.0.7:8080` and socket listens on host `127.0.0.1:8080`. `docker.service`/`containerd.service` active+enabled, `caddy.service` and `ccpc-erpnext-upstream.socket` active+disabled, relay active+static. **G1 BLOCKED**, overall NEW A3 employee PRODUCTION **NO-GO**; no change, reboot or cutover authorized.
- **Next one read-only operator check:** inspect effective candidate-only mail/scheduler/background-job exposure **without any credentials or secrets**. Exact container list `ccpc_prod_erpnext-frontend-1`, `-websocket-1`, `-backend-1`, `-redis-queue-1`, `-redis-cache-1`, `-db-1`; separately inspect only boolean `pause_scheduler` and `mute_emails` config from the approved site `ccpcerp.local` and common-site config (never print full JSON), and confirm no Docker scheduler/worker container for this candidate. This identifies whether enabling auto-start could prematurely enable outbound email/jobs before cutover. Verify actual site mount/backend identity and current pinned image first. No `bench` mutating commands, no service starts/restarts, no Docker changes. If site flags are missing or unexpected, do not assume safe; review before boot design.
- Other production gates still pending: OLD PRODUCTION data freshness/single-writer, staff TLS trust and WAN denial, complete maker-checker + stock/GL/billing + four reports, monitored backups/restore and final owner GO. Preserve 12 original protected containers plus independent recovery drill and failed-backend evidence, all NAS backup copies and one-use markers. Never replay consumed one-use Stage3A/3R/3S/3T or NAS backup commands.

## November 13, 2026 — G1 NEW A3 PRE-CUTOVER SCHEDULER AND MAIL FLAGS BOTH SAFE

- Owner executed reviewed, **read-only**, exact-candidate-only `docker inspect` and `docker exec ... python3 -B -` flag probe from `ccpcadmin@ccpcerp-prod`. The probe checked that exactly the six `ccpc_prod_erpnext-*` candidate containers exist and are running, MariaDB healthy, all share a private/internal Docker network and no candidate host-published ports, exact backend mounts include protected named sites+logs, and read only effective keys from `common_site_config.json` and `ccpcerp.local/site_config.json` without printing config or credentials. Operator output:

```text
CANDIDATE_CONTAINERS_EXACTLY_SIX=YES
CANDIDATE_NETWORK_INTERNAL=YES
SCHEDULER_PAUSED=YES
OUTGOING_EMAIL_MUTED=YES
CCPC_NEW_A3_CONFIG_FLAGS_READONLY_COMPLETE
```

- **PASS (limited)**: effective `pause_scheduler` and `mute_emails` flags are on, and six containers exist with no additional `ccpc_prod_erpnext-*` worker/scheduler container. This **reduces pre-cutover duplicate activity** but **does not prove no workers/processes embedded inside backend, outstanding queues, outbound SMTP, other integrations, manual job execution or remote integrations**. No account, company, transaction or system setting was modified. Site flags must remain as-is until a separate explicit employee cutover approval; later when enabling operations, test with controlled maker/checker and email policies.

### Draft G1 boot-recovery plan — design only, NOT authorized for deployment

1. **Pre-action preservation manifest:** bind only NEW `ccpcerp-prod` operator and exact six existing `ccpc_prod_erpnext-{frontend,websocket,backend,redis-queue,redis-cache,db}-1` containers to current immutable Docker container IDs, image IDs and expected named volumes, one internal Docker network and existing HTTPS/relay unit identities; verify full prior twelve originals and independent restore drill remain untouched. Preserve present `pause_scheduler=1`, `mute_emails=1`, protected secrets and backup files. Identify and reject any unexpected candidate-only container names, published ports, network attach changes or missing volumes. Strictly no Compose up, image pull, migration, database restoration, snapshot replacement, delete or recreate.
2. **Select reversible boot strategy:** Prefer a narrowly reviewed, guarded NEW-only startup design that uses **existing six container IDs** without recreation, includes Docker/containerd availability, existing database readiness, app/backend/websocket/frontend health/readiness and no duplicate scheduler/mail workers, and retains LAN-only Caddy/127.0.0.1 relay boundary. Evaluate (a) Docker restart-policy update on ONLY six exact IDs plus explicit readiness checks against (b) a separate dedicated systemd orchestrator starting ONLY those six in a verified sequence. Do not silently combine mechanisms that cause duplicate start/recovery or alter protected rehearsal/isolated containers. Existing all-six `RestartPolicy=no` is the baseline and rollback target; Caddy and socket presently boot-disabled. A service `static` because socket-activated must not be enabled directly. Docker policy changes can be reversed without `docker compose up` but **do not assume** they alone guarantee database readiness and fixed frontend address.
3. **Avoid stale relay IP:** installed socket-proxyd `172.20.0.7:8080` presently matches real frontend; a future network reconstruction/recreation may change private IP. Plan a stable, preverified resolution strategy or fail-closed boot-time target/address verification that leaves employee gateway unavailable and raises a clear alert if mismatched, rather than forwarding to a different container. Never restart/recreate frontend merely to publish a port; keep the socket `127.0.0.1:8080` and Caddy LAN-restricted.
4. **Failure handling:** do not automatically reset databases, attempt migrations, restore from NAS, clear queues, change users, or delete Docker volumes if a startup health check fails. Alert and stop *new* gateway activation only under a separately authorized procedure; do not stop currently running app/DB or other environments. A clean rollback of proposed future reversible boot flags should restore `RestartPolicy=no` and Caddy/relay boot-disabled without stopping existing services, unless owner approves an exact alternate action.
5. **Staged review and acceptance:** create reviewed GitHub versioned implementation/procedure first, compare source bytes to installed units and current Docker identities, run read-only guard/preflight, then seek separate explicit approval for each live NEW-only change. Verify service state post-change and safe rollback at each stage; a real reboot test needs its **own explicit approval** and local fallback access with complete backups. No employee/OLD cutover from a boot policy alone.

**G1 state remains BLOCKED** until a reviewed, approved boot plan is deployed and actual recovery behavior is verified; no boot-policy changes made under this assessment so far. **Overall production remains NO-GO** pending source OLD-to-NEW data freshness, role/permission/security, end-to-end financial workflow/report checks, continuous backup/alerts, cutover/rollback and separately authorized owner GO.

**Next read-only candidate preflight to finalize boot design:** verify that the candidate Docker network's exact attached member names are only the six expected candidate containers, and gather sanitized `State.Health.Status` and `Config.Healthcheck` presence for each existing candidate service. We already know MariaDB reports healthy; frontend/backend/websocket/Redis readiness at boot must not be inferred from Docker `Running` alone. Do not dump healthcheck test commands, Docker inspect env/secret mounts or raw process command lines. No writes or restarts.

## November 13, 2026 — G1 EXACT SIX-MEMBER INTERNAL NETWORK AND DOCKER HEALTHCHECK INVENTORY

- Owner reports guarded **read-only** Docker `container inspect` and `network inspect` checks for the actual NEW candidate (`ccpc_prod_erpnext`) on `ccpcadmin@ccpcerp-prod`, with complete sanitized output:

```text
NETWORK_INTERNAL=YES
NETWORK_MEMBERS_EXACTLY_SIX=YES
DB_HEALTH=HEALTHY
REDIS_CACHE_HEALTH=NO_HEALTHCHECK
REDIS_QUEUE_HEALTH=NO_HEALTHCHECK
BACKEND_HEALTH=NO_HEALTHCHECK
WEBSOCKET_HEALTH=NO_HEALTHCHECK
FRONTEND_HEALTH=NO_HEALTHCHECK
CCPC_NEW_A3_HEALTH_INVENTORY_READONLY_COMPLETE
```

- **PASS for this precise scope:** all six existing NEW A3 candidate containers are Running; all use one exact **internal** Docker network; the network's current endpoint-container IDs are **exactly the six candidate IDs** (no unexpected attached test/rehearsal endpoints). Database is **HEALTHY** under Docker's configured check. The two Redis services and three application services have **no Docker health checks defined**, so `Running` is **not equivalent to application-ready** and `NO_HEALTHCHECK` is **not an unhealthy/fail status**. This inventory did not query health endpoints, Redis response, application routing, Frappe session state, or actual DB transaction integrity.
- **G1 reboot resilience remains BLOCKED:** all six exact candidate containers have `RestartPolicy=no`; Caddy and `ccpc-erpnext-upstream.socket` are currently active but boot-disabled; the relay's installed static private IP target `172.20.0.7:8080` currently matches candidate frontend. Do not automatically enable these units or modify restart policies before an owner-reviewed boot plan and restore/manual rollback procedure. Do not reboot to test readiness. Current operator-confirmed `pause_scheduler=YES` and `mute_emails=YES` must be preserved.
- **Next one strictly bounded live-service READ-ONLY verification:** guarded against the six exact candidate IDs and network, perform small local GET `/login` probes for **both** backend (`8000`) and frontend (`8080`) using `Host: ccpcerp.local`, TCP reachability of websocket (`9000`), and Redis `PING` of cache/queue (`6379`) from the existing backend container. A GET may produce application access logs and Redis PING transient activity, but does not authorize document submission, scheduler, email, DB writes/migration, account/password changes, restarting containers, port publishing, external access or old production changes. Print only PASS/FAIL markers, no headers, response bodies, session IDs, credentials or raw config. A Redis server may require authentication, so a PING refusal would be a **test limitation**, not direct proof of a failed Redis service. MariaDB Docker healthy previously established. Successful probes prove **current liveness**, not post-reboot reliability.
- Then author/review a **non-destructive** per-container service-readiness and fail-closed boot policy. Future boot changes require explicit new approval, and all user-facing production gates G2–G7 remain pending. Preserve OLD PROD/DEV, 12 original protected Docker containers, isolated restored test resources and failed-backend evidence, Nov07 rehearsals, NAS recovery artifacts and one-use markers. All consumed Stage3A/3R/3S/3T executions must **NEVER** be replayed; no cutover authorized.

## November 13, 2026 — G1 ACTUAL NEW A3 FIVE-SERVICE LIVENESS PROBES ALL PASS

- Owner reports guarded read-only identity/membership/published-port inspection and narrow in-network probe from actual NEW candidate backend container `ccpc_prod_erpnext-backend-1`. The process performed `GET /login` with `Host: ccpcerp.local` against the candidate backend:8000 and frontend:8080, Redis RESP `PING` to both candidate Redis services on 6379, and websocket TCP9000 connectivity. It printed only sanitized results; GET requests could create ordinary access logs and PING/TCP connection transient activity, but no business transaction was requested. Results:

```text
BACKEND_LOGIN_HTTP200=YES
FRONTEND_LOGIN_HTTP200=YES
REDIS_CACHE_PING=YES
REDIS_QUEUE_PING=YES
WEBSOCKET_TCP9000=YES
CCPC_NEW_A3_SERVICE_LIVENESS_PROBES_PASS
```

- **Current-service availability checks all PASS**. Backend and frontend serve `/login` HTTP200, both existing Redis respond `+PONG` without authentication error for this local internal-only probe, websocket has TCP listener 9000. Prior candidate DB reported `HEALTHY`; network `Internal=true` and exact six candidate members; no candidate published Docker ports; expected persistent volumes and same app image IDs; `pause_scheduler=YES`, `mute_emails=YES`. This combination establishes current liveness of the six services but **does not establish authenticated transactions, stock/GL/billing/report integrity, file permissions, WAN/guest controls, steady-state monitoring, worker/scheduler readiness for employee operations, or boot/power-failure recovery**.
- **G0 candidate container/network and current core service liveness: PASS (scoped); G1 automatic boot/recovery: BLOCKED.** All six candidate `RestartPolicy=no`, Caddy and upstream socket active but boot-disabled; upstream service static/socket-activated; confirmed live relay points to frontend `172.20.0.7:8080`. Current Docker unit ordering lacks direct Caddy/socket dependencies; not necessarily a runtime fault. A safe boot sequence needs readiness gates and fail-closed behavior for stale relay IP or unready DB/Redis/backend/frontend/websocket before exposing HTTPS.
- **Decision:** stop repetitive liveness probes. Prepare a GitHub **review-only** boot-recovery plan distinguishing Docker crash restart, orderly host boot, Caddy/relay activation, verified target network identity, nonbusiness activity guards, rollback and manual emergency access. Any NEW-host Docker restart-policy update, service activation/enablement, startup script installation, reboot, host firewall or production cutover must be separately approved after reviewing exact operations and risks. A one-time NAS backup and isolated restore PASS already exist; never replay their consumed executors. No employee go-live.

## November 13, 2026 — R0 GITHUB-ONLY READONLY GUARD AND 21 OFFLINE TESTS VERIFIED

- Owner **“aPPROVED continue”** after explicit plan to prepare a **GitHub-only**, non-executing startup safeguard and synthetic offline tests. Treated strictly as R0 source/test/review authorization; **not** consent to modify or reboot NEW host/OLD PROD/DEV, change any Docker restart policy or systemd enablement, touch business/site database or perform cutover.
- Implemented `scripts/ccpc_new_a3_boot_r0_readonly.py` on current GitHub review branch, exact verified Git blob `a65b6c0907c0b28e390557b153d220ffd110c42b`. It has `--offline-fixture` and `--live-readonly` modes requiring an explicit pinned manifest, with **no --execute/start/update/enable/restart command path**. Strict identity, 19 protected container ID pins (12 originals + 7 isolated restored including failed evidence), one six-member internal network, site/logs/DB/queue persistent volume identity, same app image, healthy DB, no published Docker ports, frontend private IP/socket relay target match, systemd enabled/disabled baseline and paused scheduler/muted email. Root-only local manifest required for live mode, and source prints only sanitized PASS/STOP. **No live NEW-host execution or staging has occurred.**
- Offline tests committed at `tests/test_ccpc_new_a3_boot_r0_readonly.py`, exact verified Git blob `feabe9b32bea40f56a54ee5ee616933677a9bc04`. Python standard-library unittest from a synthetic isolated checkout produced **21/21 PASS**, including simulated container/IP/network/volume/image/port/flags/manifest drift and end-to-end offline CLI PASS/STOP. The exact blob bytes of checked-out local tested files were independently matched to GitHub fetch blobs; this is **not** production database or Docker integration validation.
- Review document: `docs/ccpc-project/NEW-A3-BOOT-R0-READONLY-GUARD-REVIEW-2026-11-13.md`. Draft GitHub PR **[#35](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/35)** opened against `docs/ccpc-checkpoint-2026-10-10`, **OPEN/DRAFT/UNMERGED**. No automated CI or paid run requested/started, and no deploy action taken.
- **Next precise separate approval boundary:** review a guarded read-only live Docker identity capture procedure and plan creation of a new root-owned mode0600 manifest plus SHA-verified R0 script staging on NEW. A **live `--live-readonly` inspection would still require a precise operator plan** and is a separate step. No boot policy/host service mutations or reboot are approved merely because R0 is implemented. G1 and overall employee PRODUCTION readiness remain **NO-GO** until actual boot resilience and G2–G7 business/security/cutover gates are satisfied.

## November 13, 2026 — R0 owner-authorized NEW-only manifest staging PREPARED, not yet executed

- Owner explicitly approved the separately described limited NEW-only R0 preparation: create a protected local manifest, stage SHA-verified read-only audit source and run its first live read-only preflight. **No approval** for Docker restart policy update, systemd enablement/service restart, reboot, migration, business/site data update, old production changes or employee cutover.
- Prepared/committed reviewed helper `scripts/ccpc_new_a3_boot_r0_manifest_once.py` Git blob `4d9eac17bb99f9285f58c331fd37c011d612561d`; verifies current exact 19 protected container names/states, pinned candidate image, no published ports, six-member internal Docker network/known frontend IP, then calls existing full R0 check **before** creating unique new root-owned 0700 folder + 0600 identity-only JSON manifest. Refuses existing paths and no overwrite/retry after failure. Not yet transferred/run on NEW.
- Offline helper tests `tests/test_ccpc_new_a3_boot_r0_manifest_once.py` exact Git blob `c05f2cbb6faf4662a55fcc0527d000ce0ce0bbe5`, **17/17 synthetics PASS** with stubbed R0 interface; original R0 21/21 synthetics PASS. Not an actual live Docker/systemd integration result. See `NEW-A3-BOOT-R0-READONLY-GUARD-REVIEW-2026-11-13.md` for SHA256 pins, safeguards and next exact operator step.
- Next: owner Windows PowerShell **download source only** from pinned GitHub commit and verify exact SHA256, then separate SCP/root-only no-overwrite staging, one-time snapshot manifest creation and first live R0 inspection under existing approval. Preserve OLD PROD/DEV, 12 originals plus 7 test-only containers, NAS artifacts and one-use markers. **G1 still blocked; overall NEW A3 production NO-GO.**

## November 15, 2026 — R0 NEW HOST ROOT-ONLY BASELINE AND INDEPENDENT LIVE PREFLIGHT PASS

- Approved R0 **completed** on actual NEW `ccpcadmin@ccpcerp-prod`, per operator's exact reported markers: `CCPC_NEW_A3_R0_ROOT_STAGING_VERIFIED_PASS`; guarded capture `CCPC_NEW_A3_R0_CAPTURE_PREFLIGHT_PASS`, `CCPC_NEW_A3_R0_IDENTITY_CAPTURE_VERIFIED_PASS`, `CCPC_NEW_A3_R0_ROOT_ONLY_MANIFEST_CREATED_PASS`; and **separate live read-only inspection** `CCPC_NEW_A3_R0_PROTECTED_FILES_PASS`, `CCPC_NEW_A3_R0_IDENTITY_STORAGE_NETWORK_PASS`, `CCPC_NEW_A3_R0_GATEWAY_AND_PRECUTOVER_FLAGS_PASS`, `CCPC_NEW_A3_R0_READONLY_PREFLIGHT_PASS`.
- Root-only mode0700 source staging path `/root/ccpc-new-a3-r0-20261115` holds exact SHA256-verified two GitHub Python files, both mode0600. One-time mode0600 metadata-only manifest in mode0700 `/var/lib/ccpc-new-a3-r0-manifest-20261113` **must NOT** be displayed, committed, replaced, recopied, uploaded or created again. Preserve as immutable **pre-boot-change** snapshot.
- Scope of **R0 PASS**: saved exact 19 protected container IDs and running/exited test evidence, six candidate running/DB healthy/no restart policies/private exact-member network, same candidate app image, persistent sites/log/DB/Redis-queue volumes, fixed frontend relay+loopback socket, systemd live vs boot enabled states, `pause_scheduler=YES` and `mute_emails=YES`. Does not verify actual power-loss/reboot behavior, post-cutover scheduler/worker operations, downstream employee transactions or production security/monitoring. Garbled terminal paste artifact appears before exact PASS lines; none of the reported markers indicate a STOP.
- **Decision:** Stage R0 preparation and live audit **PASS / DONE**; G1 reboot automatic recovery **BLOCKED / not configured**; overall production **NO-GO**. No Docker restart-policy updates, systemd enabling, reboot, migration, data changes, WAN/guest access changes, worker/email enablement, OLD PROD/DEV changes or cutover approved/reported. Next is **GitHub-only G1 command-level design and rollback review**, then new separate owner authorization for any specific live NEW-only boot policy changes. The existing R0 baseline intentionally expects current `RestartPolicy=no` and boot-disabled Caddy/socket: after a later approved boot change it must not be re-run expecting PASS without an updated, reviewed **post-change** audit design. Details in `NEW-A3-BOOT-R0-READONLY-GUARD-REVIEW-2026-11-13.md` and `NEW-A3-PRESERVATION-SAFE-BOOT-RECOVERY-DESIGN-2026-11-13.md`.
