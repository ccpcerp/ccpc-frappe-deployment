# NEW A3 — Formal PRODUCTION readiness assessment and controlled acceptance gates

**Assessment opened:** 2026-11-13 (Asia/Manila).
**Decision at assessment opening: NO-GO for employee business transactions and production cutover.**
**Target:** dedicated NEW Ubuntu `ccpcerp-prod` (`192.168.50.186`), **actual candidate** `ccpc_prod_erpnext` / site `ccpcerp.local`, not the separately restored drill containers.
**Purpose:** start read-only formal readiness verification in the latest actual operator/GitHub context. Owner's request to "proceed to a formal NEW A3 Production Readiness Check" grants read-only inventory/documentation, **not** release, cutover, restart, enabling services, data migration, DNS/router/CA/client-trust changes or production writes.

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
