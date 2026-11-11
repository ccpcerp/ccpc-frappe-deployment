# CCPC dedicated PRODUCTION host — LAN HTTPS gateway design

## November 11, 2026 — Ubuntu Caddy package installed, masked and inactive; Caddyfile adaptation next

**Operator-reported NEW-host package verification PASS** after the prior safe precheck. NEW Ubuntu 24.04 selected the package `caddy=2.6.2-6ubuntu0.24.04.3` from official Ubuntu `noble-updates/universe` and `noble-security/universe` archives; no third-party APT repository required. Before install the operator created both systemd service masks: `/etc/systemd/system/caddy.service -> /dev/null` and `caddy-api.service -> /dev/null`, verified `masked` for both, with marker `CADDY_AUTOSTART_GUARD_PASS`.

**Operator-reported post-install checks PASS:**
```text
install ok installed 2.6.2-6ubuntu0.24.04.3
caddy.service ENABLED=masked ACTIVE=inactive
caddy-api.service ENABLED=masked ACTIVE=inactive
HTTP/HTTPS LISTENERS: (none on TCP 80 or 443)
CADDY_INSTALLED_NOT_STARTED_PASS
```
This confirms **package installation, not HTTPS activation**. Do not unmask, enable, start or reload Caddy yet. The previously tested loopback-only `127.0.0.1:8080` relay to the protected A3 frontend is a separate pilot component; no subsequent relay health test is claimed here. No reported Docker restart, application migration, database/restore action, firewall change, certificate issuance, router change, OLD PROD+DEV change, or employee cutover.

**Next NEW-only operator step:** Run installed Caddy 2.6.2 **adapter-only** against the exact reviewed `overrides/Caddyfile.dedicated-https.review` syntax via a read-only stdin here-document, with disposable absolute-path string placeholders for `CCPC_TLS_FULLCHAIN_FILE` and `CCPC_TLS_PRIVATE_KEY_FILE`. Use `caddy adapt --config - --adapter caddyfile` and discard generated JSON. This parses/adapts only; it must **not** start any listener, attempt certificate issuance, change active systemd services, write a live Caddyfile, or open UFW. The real certificate/key do not exist yet, so do not use `caddy validate` at this stage. If Caddy 2.6.2 rejects syntax such as `strict_sni_host`, STOP and revise review source on draft PR #28 before staging any live configuration. Then plan off-host internal CA key, leaf SAN `DNS:ccpcerp.internal`, protected Caddy-readable PEM/key, LAN-restricted 443 and independent Windows/office Wi-Fi client trust and WAN/guest denial verification.


## November 11, 2026 — Localhost relay activated and HTTP200 PASS; Caddy package source check next

**Operator-reported live NEW-only PASS** after previously verified root-owned matching systemd unit-file staging:
```text
sudo systemctl daemon-reload && sudo systemctl start ccpc-erpnext-upstream.socket
active
LISTEN ... 127.0.0.1:8080 ... 0.0.0.0:*
LOCAL_RELAY_HTTP=200
```
The `0.0.0.0:*` part is the **peer-address wildcard for a listening socket**, not a public bind. The **local listening address is exactly `127.0.0.1:8080`**. The operator's GET `http://127.0.0.1:8080/login` using Host `ccpcerp.local` returned HTTP **200**, verifying systemd socket activation and forwarding from localhost to protected A3 frontend `172.20.0.7:8080`. **No `systemctl enable`**, Docker/container change, MariaDB/ERPNext migration, firewall alteration, Caddy installation, certificate, WAN/employee access or final cutover. Note that systemd socket remains **running** in the present pilot session; after host reboot this socket is not set to auto-activate; a future controlled durable service plan is required before go-live.

**Gateway source reconciliation:** Draft `overrides/Caddyfile.dedicated-https.review` comments previously claimed the only path was publishing Docker frontend to 127.0.0.1 and recreating the A3 frontend. Those comments are obsolete. The same Caddy `reverse_proxy 127.0.0.1:8080` is now backed by a **verified host systemd socket relay**. Revised source-comments commit `951d5430a6b2337fbceaf5a62496661c771f1fd4` on draft PR28; actual Caddy gateway remains **not installed or runtime-tested**. No source configs/keys copied to host yet.

**Next NEW-only safe operator step:** Read-only `apt-cache policy caddy`, `dpkg-query -W` and `systemctl list-unit-files caddy.service caddy-api.service` to identify whether an Ubuntu-supported candidate is available and whether any unrelated package/service state already exists. The vendor notes that installing official Ubuntu/Debian Caddy *automatically starts* `caddy.service`; **never issue `apt install caddy` blindly** because default example config may bind wildcard HTTP80. Source: https://caddyserver.com/docs/install . Next, if package/version/source acceptable, stage precise NEW-only start suppression for both `caddy` and optional `caddy-api` services before package installation; confirm no wildcard/public listener after installation. Do not add a new third-party APT repository or curl-pipe remote script without reviewed trust and approval. Plan CA root signing key off NEW and protected manual leaf SAN `DNS:ccpcerp.internal`, then Caddy adaptation/443 LAN-only UFW gating and Windows/plant phone trust tests, WAN/guest denial. Preserve OLD PROD/DEV, two NEW rehearsals and owner-approved Nov5 restored candidate; no A2/A3 replay.


## November 11, 2026 — Companion systemd relay staged+verified; activation next

**Operator-reported NEW-host action:** staged only the reviewed `/etc/systemd/system/ccpc-erpnext-upstream.service` companion with `set -C` (noclobber); terminal output ended with `MODE=644 OWNER=root:root` and **`CCPC_SERVICE_STAGED_AND_VERIFIED_NOT_STARTED`**. The operator's staging block required the source SHA256 equality `1f75e7a7f6eabda560faa052bc39f520950b1abb3c115afead28cdf7b075b22a` and `sudo systemd-analyze verify` to succeed before that marker. Reported success therefore supports exact reviewed **service-file SHA and systemd static verification PASS**; the socket companion was previously independently checked against GitHub SHA with `root:root` and mode 644. The terminal echo again contains interleaved heredoc/paste fragments, but the later check marker is a stronger test than what the echoed heredoc appears to show. **Neither systemd socket nor service has been started or enabled** by the staging script. No Docker/DB/OLD PROD+DEV/rehearsal, UFW, Internet or employee gateway changes reported.

**Checked upstream mechanism:** Official systemd `systemd-socket-proxyd` documentation supports socket-activated `Type=notify` forwarding using `Accept=no` and `ListenStream` (https://www.freedesktop.org/software/systemd/man/254/systemd-socket-proxyd.html). This is not a substitute for on-host functional validation.

**Next small owner-approved NEW-only operation — temporary loopback activation and functional smoke:**
1. Guard on NEW hostname `ccpcerp-prod`, sha256 of both staged units, candidate frontend running/portbindings empty and private IPv4 `172.20.0.7`, host 8080 not already listening, UFW unchanged. Fail closed on mismatch.
2. `sudo systemctl daemon-reload` then **`sudo systemctl start ccpc-erpnext-upstream.socket` only**; **do not `enable`** (temporary pilot); no Docker restart.
3. Verify exactly **one host TCP8080 listener, bound to `127.0.0.1:8080`** (not `0.0.0.0`, `::` or `192.168.50.186`), then single no-body GET `curl -H 'Host: ccpcerp.local' -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/login` must return `200`. Curl causes socket to activate companion service; check active socket state. Do not print session/cookie/html.
4. On any listener/status or HTTP failure, stop **only** these newly introduced socket/service units, leave two staged unit files for inspection, and report safe STOP; do not rerun/overwrite. Rollback for this phase is `sudo systemctl stop ccpc-erpnext-upstream.socket ccpc-erpnext-upstream.service` (only these NEW pilot units); verify port8080 absent.
5. Caddy installation/default-service autostart prevention, CA cert issuance/protection and Windows/mobile trust, host IPv4 LAN-only 443 UFW source allow and true WAN/guest exclusion remain **NOT PERFORMED**. Continue only after functional relay PASS and operator report. Preserve OLD PROD+DEV, A3 app/DB, both NEW rehearsals, worker/scheduler/mail disabled, NOV5 selected restore and distinct employee cutover approval.


## November 11, 2026 — NEW localhost socket file staged and exact-content verified

**Operator-reported on-host result:** one-file staging command yielded `CCPC_SOCKET_FILE_STAGED_NOT_STARTED`. Operator subsequently ran the SHA256 ownership/mode check and returned exact `CCPC_SOCKET_MATCHES_GITHUB_PASS`, `MODE=644 OWNER=root:root` for `/etc/systemd/system/ccpc-erpnext-upstream.socket`. This verifies the NEW-host socket unit file matches the GitHub-reviewed source in the operator's validated SHA256 comparison, with appropriate file owner and mode; **it has not been daemon-reloaded or started/enabled**. The original terminal paste had interleaved heredoc text, but the separate hash check now confirms exact file bytes. The companion service file has not been staged. No front-end, database, Docker port, UFW, WAN or OLD PROD/DEV changes reported.

**Next NEW-only operator step within approved pilot:** Stage only `/etc/systemd/system/ccpc-erpnext-upstream.service` using an exclusive, no-overwrite `sudo sh -c 'set -C; umask 022; cat > "$1"' sh "$unit"` with exact reviewed `overrides/systemd/ccpc-erpnext-upstream.service` bytes, after checking hostname, matching socket file, companion absent and relay binary. Review-source SHA256 for exact **825-byte** UTF-8 service content ending in newline is `1f75e7a7f6eabda560faa052bc39f520950b1abb3c115afead28cdf7b075b22a`; compare a new host SHA256 to expected and run `sudo systemd-analyze verify /etc/systemd/system/ccpc-erpnext-upstream.socket /etc/systemd/system/ccpc-erpnext-upstream.service`. Do not `systemctl daemon-reload`, `systemctl start`, enable, or change UFW yet. If SHA or systemd verification fails, stop without overwriting/rerunning, inspect exact bytes and output. After staged+verified PASS, next approved tiny step: reload manager and start socket only (not enable), reverify 127.0.0.1:8080 exclusively and HTTP200 through relay, with stop-only rollback. Ensure private frontend IP unchanged before activation. TLS/Caddy, host 443 firewall and mobile trust all remain pending.


## November 11, 2026 — Retry state verified clean; stage socket unit alone

**Operator report after staging STOP:** exactly
```text
=== FRONTEND CHECK ===
ACTUAL_BASH_ESCAPED=RUNNING=true\ PORT_BINDINGS=\{\}\ NETWORK=ccpc_prod_erpnext_default\ PRIVATE_IPV4=172.20.0.7\
=== SYSTEMD FILES ===
ccpc-erpnext-upstream.socket ABSENT
ccpc-erpnext-upstream.service ABSENT
=== PORT 8080 ===
```

**Verified by operator output:** Docker inspection matches prior A3 running/private/unpublished identity, except for a **trailing literal space** visible as final `\` in `printf %q`; both intended unit files are **ABSENT**; no host TCP8080 listener. Therefore previous `STOP: FRONTEND_IDENTITY_CHANGED` was a guard false-positive and the intended files were not written. No evidence of service activation or container/data change. Prior script **must not be re-run**.

**Next NEW-only one-small-step within standing bounded HTTPS pilot approval:** Stage only the GitHub-reviewed `overrides/systemd/ccpc-erpnext-upstream.socket` as a root-owned, permissions-0644 file at `/etc/systemd/system/ccpc-erpnext-upstream.socket`. Before creating, guard exact host, exact absence of path/symlink, port 8080 unoccupied, inspected A3 running and still not host-published, and require direct Docker private frontend GET returning HTTP200. Use a short clearly terminated heredoc to copy source; print success only if exact file exists and has `ListenStream=127.0.0.1:8080`. **Do not use `systemctl daemon-reload`, start/enable, UFW or Caddy yet**, and do not install or overwrite if a unit already exists. After the socket file alone stages successfully, stage the companion existing reviewed service separately and perform `systemd-analyze verify` on both; then separately start localhost socket only. Existing draft PR28 units unchanged, no new source commit. If any failure or paste corruption, STOP without rerun; inspect files first.


## November 11, 2026 — First operator relay staging STOP: strict string guard mismatch

**Operator evidence:** The NEW pilot staging block stopped with **`STOP: FRONTEND_IDENTITY_CHANGED`** before its intended unit-file `tee` commands. The pasted terminal text also includes interleaved heredoc fragments, so the absence of writes must be **confirmed** rather than assumed. No observed evidence of Docker/container changes or any service activation, but state check remains pending.

**Review finding in ChatGPT-authored stage block:** The inspection command's Go template `... PRIVATE_IPV4={{$net.IPAddress}} {{end}}` emits a **literal trailing ASCII space** before the closing `{{end}}` when one network is present. Bash `$(...)` strips trailing newlines, **not trailing spaces**, while the expected comparison string had none. Therefore `[ "$actual" = "$expected" ]` can reject a correct unchanged frontend. This is **a command-guard false-negative**, not proof of frontend identity drift. The source-reviewed `.socket`/`.service` files are not implicated. Do not rerun the previous staging block, and do not remove/overwrite any unit file without checking its existence.

**Immediate single safe read-only operator check on NEW:**

```bash
printf '%s\n' '=== FRONTEND CHECK (WHITESPACE VISIBLE) ==='
actual="$(sudo docker inspect --format 'RUNNING={{.State.Running}} PORT_BINDINGS={{json .HostConfig.PortBindings}} {{range $name,$net := .NetworkSettings.Networks}}NETWORK={{$name}} PRIVATE_IPV4={{$net.IPAddress}} {{end}}' ccpc_prod_erpnext-frontend-1)" || exit 1
printf 'ACTUAL_BASH_ESCAPED=%q\n' "$actual"
printf '%s\n' '=== STAGED UNIT FILE PRESENCE ==='
for unit in ccpc-erpnext-upstream.socket ccpc-erpnext-upstream.service; do
  if sudo test -e "/etc/systemd/system/$unit" || sudo test -L "/etc/systemd/system/$unit"; then
    printf '%s EXISTS\n' "$unit"
  else
    printf '%s ABSENT\n' "$unit"
  fi
done
printf '%s\n' '=== TCP 8080 LISTENER ==='
ss -H -ltn '( sport = :8080 )'
```

The command only reads sanitized Docker identity/network/port bindings, NEW unit presence, and TCP8080 listeners. No host, Docker, UFW, TLS or DB changes. If both units are ABSENT, no 8080 listener, and frontend identity is correct apart from trailing space, **build a fresh no-overwrite staging block with a whitespace-safe, structured identity check**, not an exact formatted string; verify one-shot steps with `bash -n`/unit validation where possible. Do not auto-rerun the failed script; stop on unexpected files/listeners. Existing approved NEW-only HTTPS pilot scope remains in force, with OLD PROD/DEV, protected NEW rehearsals and Nov5 restored candidate preserved.


## November 11, 2026 — NEW UFW/relay guards PASS; reviewed pilot socket units authored

**Operator-reported host safety preflight:**
- `ccpcadmin@ccpcerp-prod` is **Ubuntu 24.04.5 LTS**.
- UFW **active**; defaults **deny incoming, allow outgoing, deny routed**; **only explicit inbound exception** reported `22/tcp ALLOW IN 192.168.50.0/24`. *This is a snapshot of UFW, not proof there are no alternate nftables/Docker/WAN bypass paths.*
- NEW candidate frontend `ccpc_prod_erpnext-frontend-1`: **running true**, `HostConfig.PortBindings={}`, solely reported Docker network `ccpc_prod_erpnext_default`, private IPv4 **`172.20.0.7`**. No host listener; current Windows SSH tunnel/ERPNext login must be preserved.
- `systemd-socket-proxyd` binary **available** on host (at one of standard `/usr/lib` or `/lib` paths). The reviewed service uses `/usr/lib/systemd/systemd-socket-proxyd`; this path must be verified on host during staging.
- No Caddy installed in PATH, host TCP 80/443/8080 listeners last observed empty, so no gateway yet.

**Source-implemented on draft PR #28 branch** `docs/dedicated-production-https-gateway-2026-10-23`:
1. `overrides/systemd/ccpc-erpnext-upstream.socket` — **IPv4 127.0.0.1:8080** only, socket activation, Accept=no. Commit `61f54c35b3f121389ef68346a5d2f4e21b50e6b7`, Git blob `f29d31223876e3c50923c1985ce8cbec0cf603e0`.
2. `overrides/systemd/ccpc-erpnext-upstream.service` — executable socket proxy to *observed* private frontend `172.20.0.7:8080`, DynamicUser, restricted capabilities/FS and `Restart=no`, no containers touched. Commit `52a92bf150ab2c7649b087129cf6a4586a0941fe`, Git blob `e701b9e811beac034a0f72e8538b2093186e02ff`.
3. Source static assertions re-fetched both files PASS for IPv4 loopback-only bind, exact private target, no wildcard/public listener, socket match, minimal hardening, no Compose/DB commands. **Not a live `systemd-analyze verify` or operational test.** Read upstream documentation at https://www.freedesktop.org/software/systemd/man/257/systemd-socket-proxyd.html and https://www.freedesktop.org/software/systemd/man/latest/systemd.socket .

**Next single operator step, within approved pilot:** Stage **only these two new systemd unit files** on NEW Ubuntu under `/etc/systemd/system/` using an exact-match, no-overwrite guarded command. Precheck host identity `ccpcerp-prod`, absence of existing unit files and local TCP8080 listener, required relay executable, running unexposed A3 frontend at exact observed `172.20.0.7`, and private upstream `curl -H 'Host: ccpcerp.local' http://172.20.0.7:8080/login` returning HTTP200. Stage files and run `systemd-analyze verify` on NEW, **but do NOT `systemctl daemon-reload`, start/enable any socket or change UFW until staged unit contents and verification output are reviewed**. If guard fails, STOP; no auto-rerun/recovery that overwrites files. This action writes only two previously absent root-owned text unit files; does not alter currently loaded systemd units or change any network listener.

**After verified staging**, next operator action would be `systemctl daemon-reload` and `systemctl start ccpc-erpnext-upstream.socket` (**not enable yet**) then verify the *only* new listener is `127.0.0.1:8080` and a local GET through relay returns HTTP200; record a socket/service-only stop/disable rollback. Caddy installation, sanitized TLS certificate source/CA trust, UFW approved TCP443 LAN-only rule and true Internet-origin exclusion remain subsequent scoped steps. **Do not** run generic Docker deployment, edit OLD production, restart/recreate candidate, replay A2/A3, migrate or restore databases, start workers/scheduler/mail, modify router DNS/NAT, touch protected rehearsals or perform employee cutover. Owner's approved Nov5 backup already restored; no repeat backup validation.


## November 11, 2026 — Owner APPROVES bounded NEW-only HTTPS pilot; scoped execution underway

**Owner explicit authorization (2026-11-11):** “aPPROVED”, in response to “Do you approve this NEW-server-only HTTPS pilot, with no changes to OLD PRODUCTION, no database migrations or restores, and no employee cutover yet?” The bounded approval covers controlled NEW-host-only Caddy HTTPS gateway installation, guarded loopback ERPNext access, LAN-restricted TCP443 firewall, internal HTTPS cert/client trust staging and smoke testing. It **does not authorize** modifying OLD PROD/DEV, changing NEW candidate DB/master/ledger or MariaDB volumes, rerunning one-shot A2/A3 scripts, enabling jobs/mail, touching two preserved rehearsal namespaces, changing ER7206 DNS/port forwarding, unrestricted firewall changes, broad guest/WAN access, or general go-live/cutover.

**Verified facts before this approval:** TP-Link ER7206 office LAN DNS `ccpcerp.internal -> 192.168.50.186` Windows explicit query PASS; phone on plant/staff Wi-Fi uses `192.168.50.x` as do office Windows client and NEW. Operator NEW `hostname` gives `ccpcerp-prod`; `caddy` absent from PATH; host TCP ports 80,443,8080 no listeners at last inspection. The A3 candidate frontend `ccpc_prod_erpnext-frontend-1` remains Docker internal-only, last accessible from SSH-forwarded Docker bridge IP `172.20.0.7:8080`; backend/database are protected and must NOT be recreated for this pilot. Existing GitHub `overrides/Caddyfile.dedicated-https.review` is template-only and expects unavailable host loopback `127.0.0.1:8080`. Branch draft PRs #27 and #32 overlay files are not live; don't assume Compose `up`/generic deploy can safely generate pilot.

**Fastest low-change approach to evaluate:** Prefer a **NEW-host loopback-only byte-stream socket relay** `127.0.0.1:8080` to the **currently inspected** internal frontend IP `<actual A3 private Docker IPv4>:8080`, using existing `systemd-socket-proxyd` if present, **rather than recreating the protected A3 frontend merely to publish Docker ports**. The relay's destination IP may drift on container restart; this must be guarded and is pilot-only until a stable reviewed name/connection is available. The existing Caddy template can then reverse proxy to `127.0.0.1:8080` without change. No new Docker host bindings. Do not presume `systemd-socket-proxyd` is installed or working until host checks. If not present, choose a separately reviewed alternate stable loopback bridge, avoiding Docker restart.

**Immediate authorized first operator action: NEW-only read-only safety evidence** (run on NEW under `ccpcadmin`; no passwords, server configs or private data printed):

```bash
printf '\n=== OS ===\n'
. /etc/os-release; printf '%s\n' "$PRETTY_NAME"
printf '\n=== FIREWALL ===\n'
if command -v ufw >/dev/null 2>&1; then sudo ufw status verbose; else echo UFW_NOT_INSTALLED; fi
printf '\n=== FRONTEND INTERNAL CONTAINER ===\n'
sudo docker inspect --format 'RUNNING={{.State.Running}} PORT_BINDINGS={{json .HostConfig.PortBindings}} {{range $name,$net := .NetworkSettings.Networks}}NETWORK={{$name}} PRIVATE_IPV4={{$net.IPAddress}} {{end}}' ccpc_prod_erpnext-frontend-1
printf '\n=== SYSTEMD SOCKET RELAY ===\n'
if [ -x /usr/lib/systemd/systemd-socket-proxyd ]; then echo RELAY_AVAILABLE=/usr/lib/systemd/systemd-socket-proxyd
elif [ -x /lib/systemd/systemd-socket-proxyd ]; then echo RELAY_AVAILABLE=/lib/systemd/systemd-socket-proxyd
else echo RELAY_NOT_FOUND; fi
```

**Must review output before writes:** The firewall may be inactive or managed by other tooling, and arbitrary UFW changes can impair SSH; inspect current policy and forwarding, source allowlists and Docker bypass. Verify candidate running, no host `PortBindings`, private network name/address, and relay binary path. Never infer that bind to `192.168.50.186` alone blocks WAN NAT. On server, ensure a persisted rollback of any *new gateway-specific* config and that Caddy package installation does not start the default wildcard HTTP/HTTPS service; official Debian/Ubuntu package **auto-starts Caddy** (https://caddyserver.com/docs/install). Pre-mask/otherwise prevent that start in a separately reviewed and validated step before installing. Do not commit/print any cert private keys. An internal CA **root private key must be retained securely off the NEW host**; Caddy runs a manually issued, SAN-checked leaf certificate at protected local paths and approved clients import **public CA certificate only**. Don't rely on public ACME or disable certificate verification to make mobile work.

**Acceptance and rollback:** With employee cutover still forbidden, verify Caddyfile via installed Caddy adapter, exact IPv4 host listeners 443 and loopback 8080 only, no 80 or UDP443/IPv6/public bindings, guarded local proxy HTTP200/WebSockets/Host/forwarded HTTPS, authorized Windows + plant/staff Wi-Fi mobile trust; confirm negative tests from unauthorized guest and true Internet client via a non-DNS-only method; confirm no WAN NAT/UPnP/DMZ to NEW; retain SSH access. If anything fails, stop only the newly introduced Caddy/relay services and remove only new dedicated gateway firewall allows, leaving Docker candidate, DB, OLD and rehearsal containers untouched. Site remains `ccpcerp.local` internally. Record actual operator results before marking any runtime stage PASS.


## November 11, 2026 — Plant Wi-Fi confirmed on 192.168.50.0/24; no extra subnet needed

**Owner confirmed:** the same mobile phone, while connected to the authorized **plant Wi-Fi**, receives IPv4 `192.168.50.xxx`. This is within the same **`192.168.50.0/24`** subnet as the previously verified Windows Ethernet client `192.168.50.194` and dedicated NEW ERPNext server `192.168.50.186`. Together with earlier owner observation that the phone reaches OLD ERPNext login on plant Wi-Fi, this closes the immediate subnet-discovery step. **Do not ask for the phone's full IP or repeat this check.**

**Access policy now specific:** future NEW host TCP 443 should serve authorized **CCPC wired LAN and plant/staff Wi-Fi clients on `192.168.50.0/24`**, subject to staff SSID authentication and ER7206 LAN/VLAN segmentation. Public Internet/mobile data, unauthorized guest/IoT/tailnet and arbitrary outside subnets stay blocked. If guests share `192.168.50.0/24`, an IP-prefix UFW rule **alone cannot distinguish them**: review ER7206 Wi-Fi SSID/VLAN/ACL isolation before claiming guest exclusion. No extra routed Wi-Fi subnet allow rule is needed on current evidence. The phone's full IP was neither requested nor recorded.

**Next implementation stage:** NEW-only, guarded HTTPS integration with **internal CA trust** and existing Caddy review template, with source-address restrictions and no WAN/NAT/port forwarding. The current A3 frontend remains unexposed Docker-internal and has no `127.0.0.1:8080` host listener. Caddy is not installed, and host ports 80/443/8080 were free at the last read-only check. To make the drafted gateway operational, a **separately scoped owner authorization** is required for host-package/systemd installation, secure issuance/storage of a `DNS:ccpcerp.internal` cert and CA key, a deliberate loopback-only frontend bridge, LAN-scoped host firewall TCP443 change and pilot tests. Review service startup behavior and rollback first. Absolutely no generic `deploy_release`, A2/A3 reruns, database restore/migration, scheduler/worker/mail enablement, OLD PROD+co-hosted DEV or employee traffic switch. Capture actual allow/deny evidence from office workstation and staff phone before any go-live claim. The user-approved Nov5 historical backup is already restored; no repeat verification requested.


## November 11, 2026 — Plant Wi-Fi phone opens OLD login page; NEW staff subnet still unknown

**Owner observation:** On a mobile phone connected to CCPC **plant Wi-Fi**, the **OLD live production ERPNext login page** opens. When the same phone uses **mobile cellular data**, that old login page is not reachable. This confirms an **operator-reported, login-page-only** LAN Wi-Fi reachability difference for OLD, not authenticated phone use or any NEW server accessibility. It is compatible with the desired NEW office/plant Wi-Fi allow, cellular/WAN deny security policy.

**Important evidence limit:** The mobile-data failure might be DNS-only (old hostname not publicly resolving) or due to routing/firewall; this observation **cannot prove** OLD or NEW WAN exposure is blocked. Do not substitute it for controlled Internet-origin denial checks of NEW 443 and router WAN NAT/DMZ/UPnP and any IPv6 paths. No known plant Wi-Fi subnet, router/DNS addressing or guest/staff VLAN classification is provided yet. The phone could be on the existing wired `192.168.50.0/24` subnet or a distinct routed staff subnet, and a separate intentional ACL may be needed in the latter case.

**NEXT SINGLE NON-MUTATING OPERATOR STEP:** While connected to the **plant Wi-Fi** (not guest), inspect the phone's Wi-Fi IPv4 address and report only its first three octets (for example `192.168.50.x` or another range), plus router/DNS only if available and useful; do not disclose full device identifiers or passwords. After the actual network classification is known, design office/plant Wi-Fi CIDR-specific TCP 443 source rules and mobile local-DNS + internal-CA root trust tests; no blanket Internet/guest allowance. Maintain prior NEW preflight: `ccpcerp-prod` hostname, Caddy absent in PATH, no host TCP 80/443/8080 listeners; Caddy review config only in draft PR #28 and A3 frontend still internal-only. **No** router, OLD PROD+DEV, NEW candidate, protected rehearsals or production cutover modifications implied or performed.


## November 10, 2026 — NEW host clean HTTPS port preflight; trusted office Wi-Fi mobile clients included

**Operator evidence on NEW `ccpcadmin@ccpcerp-prod`:** `hostname` returned exactly `ccpcerp-prod`; `command -v caddy` had no executable in PATH and printed `CADDY_NOT_INSTALLED`; `ss -ltn '( sport = :80 or sport = :443 or sport = :8080 )'` showed only its header, hence **no TCP listeners on host 80/443/8080 at the time of inspection**. This is a **read-only gateway-host readiness observation**. A missing `caddy` executable in PATH does not prove no package files exist elsewhere, nor does an empty `ss` prove LAN/WAN firewall isolation or a functioning HTTPS gateway. The current NEW A3 candidate frontend remains **internal Docker-only with no 127.0.0.1:8080 host upstream**; do not start Caddy against the inert template until a controlled loopback frontend transition is separately planned and authorized.

**Explicit owner policy amendment:** “The mobile phone should be allowed to access also but connected to the Local network.” Therefore **authorized mobile phones over CCPC staff/office Wi-Fi are in scope**, alongside authorized wired desktop/laptop clients. **Mobile cellular/public Internet remains out of scope and blocked**, as do unapproved guest/IoT Wi-Fi, router WAN access, remote VPN/tailnet paths and any arbitrary client on an unrelated VLAN. The previous word “LAN-only” includes **authenticated/trusted office Wi-Fi**, not wired Ethernet only. *An SSID labeled office does not prove it is in the `192.168.50.0/24` subnet*; inspect the phone's Wi-Fi IPv4 network/gateway and office SSID category (not credentials/device MAC) before selecting precise UFW source ranges and ER7206 ACL scopes. If staff Wi-Fi is routed from a different VLAN, approve and permit **only that designated staff subnet** to TCP 443; do not open 443 to `0.0.0.0/0`, every VLAN, or the WAN as a shortcut.

**Certificate and device trust:** Both approved Windows and mobile browsers must successfully resolve `ccpcerp.internal` to `192.168.50.186` via permitted local DNS, reach LAN TCP 443, and **trust the internal-CA root** that issues a leaf certificate containing SAN `DNS:ccpcerp.internal`. iOS/Android trust enrollment differs by OS/browser; plan controlled distribution of the **public CA root certificate only**, and explicit trust activation where required; never distribute the CA private key. Some mobile “Private DNS”/secure DNS, VPN, cellular fallback or guest isolation can bypass the ER7206 LAN DNS, so test an authorized staff Wi-Fi mobile browser with mobile data/VPN disabled. Do not bypass TLS warnings, use a self-signed leaf as an employee workaround or open public port forwarding to make mobile work. Caddy's official documentation confirms that internal-issued certificates are trusted only where the root is installed, and that the official Ubuntu package installation automatically starts the `caddy` systemd service. **Do not run `apt install caddy` casually:** it is a persistent host-service and firewall-affecting operational stage requiring reviewed NEW-only scope and safeguards, not a harmless package download.

**Next one read-only client check:** On one authorized phone, connect to the **staff office Wi-Fi** (not guest), inspect its Wi-Fi connection details and report only the **IPv4 subnet pattern** (e.g. `192.168.50.x` versus another range), whether the listed router/DNS is `192.168.50.1` (if exposed), and whether the phone is on a staff rather than guest SSID. No passwords/MACs/screenshots of private identifiers. This distinguishes whether the initially proposed office-only `192.168.50.0/24` host UFW source rule includes the phone, before planning the gateway pilot.

**Plan for next NEW-only implementation stage (NOT performed):** establish recoverable NEW candidate loopback-only HTTP upstream `127.0.0.1:8080` without touching preserved MariaDB/sites volumes, 2 rehearsal projects or OLD PROD+DEV; separately stage Caddy package/service installation with its auto-start risk explicitly managed, CA certificate issuance/retention/client trust, exact host IPv4 443/TCP and staff-Wi-Fi-specific UFW constraints, inspect actual listeners/route/WebSockets and verify LAN success plus a true externally originated WAN denial. Keep A3 workers/scheduler/mail disabled and never use generic `deploy_release` or rerun consumed A2/A3 scripts. Source remains the owner-approved previously restored November 5 four-artifact backup, no repetition.

References:
- https://caddyserver.com/docs/install
- https://caddyserver.com/docs/automatic-https
- https://caddyserver.com/docs/caddyfile/directives/tls


## November 10, 2026 — Owner requires LAN-only ERPNext with no public Internet access

**Owner security requirement:** “I hope this site will be exclusive to LAN and can't be access from internet.” Record this as **a mandatory release-acceptance condition** for NEW `https://ccpcerp.internal`, not just a preference. Approved office LAN clients may use the ERPNext HTTPS gateway; public Internet clients, guest/IoT VLANs and remote VPN/tailnet devices **must be denied by default** unless a subsequent explicitly scoped exception is approved. DNS name resolution is not access control.

**Defense-in-depth implementation and verification requirements before go-live:**
1. Router **ER7206**: keep selected `.internal` DNS mapping LAN-scoped; audit WAN NAT/virtual-server/port forwarding, UPnP mappings, DMZ, remote management, exposed IPv6 paths and any routing policies that could make NEW host reachable from Internet. No forwarding of TCP 443/80/8080, SQL/Redis or SSH to NEW; any existing unrelated router rule must not be changed unilaterally. No reliance on private IPv4 alone to claim Internet isolation.
2. **NEW Ubuntu host-level Caddy**: bind TCP 443 only to actual NEW LAN IPv4 `192.168.50.186` and require a locally managed, trusted TLS certificate for `ccpcerp.internal`; no automatic WAN ACME/HTTP80/QUIC/IPv6 listeners. Source-address firewall must restrict TCP 443 to the authorized **office** network(s) after confirming actual VLAN segmentation; for the known user workstation `192.168.50.194/24`, `192.168.50.0/24` is a candidate but may include non-office devices. Do not automatically authorize guest/IoT devices on the same subnet. Preserve existing SSH access.
3. **App isolation**: route Caddy only to a separately verified host loopback `127.0.0.1:8080` upstream; do not expose Docker Nginx/DB/Redis to any office LAN or WAN address; inspect published port bindings and Docker/nftables/UFW pathways, as Docker-published ports may not be controlled by a plain UFW INPUT rule.
4. **Acceptance from distinct client positions:** authorized LAN workstation can open trusted HTTPS and ERPNext login; a genuinely external network (for example an authorized test device on cellular data, with Wi-Fi/tunnel/VPN disabled) **cannot reach** the NEW server via any public address/NAT path; unauthorized guest/VLAN clients denied. Confirm intended LAN DNS returns private target; test firewalls/listeners and, if applicable, IPv6. Do not equate failure to resolve `.internal` on cellular with proof the WAN IP/port is blocked. Record sanitized evidence only.
5. Maintain OLD PROD+co-hosted DEV, original Nov5 backup, preserved NEW rehearsals and single-writer cutover rollback. **No network, proxy, container, certificate, DNS, or router modification authorized by this documentation entry.**

**Current evidence:** ER7206 LAN DNS `ccpcerp.internal -> 192.168.50.186` Windows query PASS. Neither effective WAN/NAT/UPnP rules, NEW host 443 firewall/listeners, Caddy installation, actual frontend loopback upstream, client CA trust nor external network denial has been tested or claimed PASS. **No statement of present Internet inaccessibility can be definitive until the above checks pass.**


## November 10, 2026 — NEW LAN DNS `ccpcerp.internal` resolves successfully

**Operator-confirmed resolution PASS** following creation of a new enabled, IP-type **ER7206 LAN DNS** profile `ccpcerp_prod`, domain `ccpcerp.internal`, target `192.168.50.186`, blank alias, `Apply To: LAN` (the operator was explicitly instructed to choose LAN, not ALL). The previously existing `ccpcerp.com` router entry is separate; there is no user report that it was modified. Operator ran the explicit router-resolver test from Windows:

```text
nslookup ccpcerp.internal 192.168.50.1
Server:  UnKnown
Address:  192.168.50.1

Name:    ccpcerp.internal
Address:  192.168.50.186
```

**Scope:** This verifies one Ethernet LAN Windows client's direct DNS lookup via router `192.168.50.1` to the correct NEW IPv4. It does **not** independently establish DNS propagation to every office/VLAN client, whether the DNS router survives WAN outage, HTTPS/TLS trust, proxy/WebSocket behavior, host 443 listener, or app write cutover. DNS is now configured; **do not repeat earlier DNS provisioning** or alter old `ccpcerp.com`.

**Next single NEW-only, read-only operator step:** In a normal SSH session on NEW `ccpcadmin@192.168.50.186` (not in the Windows SSH-forwarding PowerShell), inspect `hostname`, local Caddy installation/version availability, and TCP listening ports **80, 443, 8080** using `ss`. Output only these sanitized observations, no private keys, credentials, full network configuration or server secrets. No `apt install`, `systemctl start/restart`, `docker compose up`, `docker restart`, `ufw allow` or network changes from this preflight. The currently running candidate frontend was last proven internal-only (no host 8080), so if Caddy is absent and no listeners exist, that is **expected**, not a reason to install/unilaterally publish ports. Follow with a separately reviewed host-level HTTPS pilot using internal CA trusted by client workstations and a stable protected loopback-only backend; do not assume draft template is executable/validated. Old PROD+DEV and two protected NEW rehearsals remain untouched. The selected November 5, 2026 backup is already restored in NEW; no repeated backup validation demanded.


## November 10, 2026 — ER7206 router LAN DNS capability confirmed by operator UI

Owner identified the actual gateway as **TP-Link Omada ER7206** and supplied its authenticated **LAN > LAN DNS** screen. The screenshot shows an existing distinct **enabled IP-type** profile named `ccpcerp` for domain **`ccpcerp.com`**, with **no alias** shown, alongside `Add`, `Delete` and existing-row edit/delete controls. **Leave the preexisting `ccpcerp.com` record untouched**: its current target address is not shown, and it might support OLD PRODUCTION access. The previously observed router DNS NXDOMAIN for `ccpcerp.internal` therefore requires a **separate** entry, not modification of the historical one.

TP-Link/Omada official guidance for ER7206-supported **LAN DNS IP** entries confirms the expected fields: Profile Name, enabled Status, Domain Name, optional Alias Domain Name, Type **IP**, explicit IPv4 **IP Address**, and **Apply To LAN** selection, with Save/OK after review. For CCPC's proposed NEW host, prepare **new profile `ccpcerp-new`**, Domain `ccpcerp.internal`, Type `IP`, IPv4 `192.168.50.186`, no aliases/IPv6, apply only to the office `192.168.50.0/24` LAN (identify the corresponding actual LAN label in the router). Do not infer the label if VLAN/network names differ. This is **pure DNS routing**, not readiness of HTTPS or authorization to make NEW the live writer.

**Immediate safe operator step:** Click **Add** (not the edit/pencil on existing `ccpcerp.com`) to inspect the new-entry form, optionally populate the reviewed fields, and share a screenshot of the prepared form **before saving**. Avoid showing administrator tokens, credentials, device inventory, or other network configuration. **Do not click OK/Save until the operator explicitly authorizes this router-network change and the intended LAN scope is checked.** No need for new DNS infrastructure if router record creation and lookup validation succeed. After an authorized save, verify `nslookup ccpcerp.internal 192.168.50.1` returns only `192.168.50.186`; preserve `ccpcerp.com` by not editing it. No NEW proxy, Caddy, TLS or Docker alterations under this UI inspection. A later accepted HTTPS pilot must have a LAN-trusted cert with SAN DNS `ccpcerp.internal`, a guarded backend upstream, and correct WebSockets/Host behavior before office traffic.

Official reference: https://www.omadanetworks.com/us/document/40077/ ; Omada Controller User Guide v6.0: https://support.omadanetworks.com/en/document/111217?app=web .


## November 10, 2026 — Office router DNS returns NXDOMAIN for selected NEW name

**Operator-reported read-only Windows DNS test**:

```text
nslookup ccpcerp.internal 192.168.50.1
Server: UnKnown
Address: 192.168.50.1
*** UnKnown can't find ccpcerp.internal: Non-existent domain
```

**Interpretation:** At test time the configured Ethernet DNS resolver/router **192.168.50.1** returned **NXDOMAIN** for the selected new hostname **ccpcerp.internal**. The reverse-name presentation `Server: UnKnown` does **not** by itself indicate a bad DNS server; the explicit resolver response is what matters. This does not indicate an ERPNext application/backend problem; the future office HTTPS hostname will not work via this resolver until an A record is provided. NXDOMAIN does not establish whether the router supports local DNS static mappings or whether all client networks use the same DNS.

**Next single safe operator step:** In Windows browser on the authorized Ethernet LAN navigate to `http://192.168.50.1`, identify **router brand/model from the login page or router label**, and report only the make/model; avoid opening configuration panels if not necessary, making DNS/DHCP/port-forward/firewall changes or pasting administrator credentials. If router administration is HTTPS-only, the owner may use its existing approved administrative address; do not bypass certificate warnings. Identify the relevant supported custom local DNS record capability after the model is known, before preparing any network-change authorization. Keep NOV5 approved source, restored NEW database and OLD PROD+DEV untouched. NEW candidate/frontend remains private-only; no Caddy install/TLS/port 443 live. 


## November 10, 2026 — Windows LAN DNS resolver identified; non-mutating hostname check next

Owner provided Windows `ipconfig /all` from the authorized CCPC Ethernet LAN. Sanitized relevant observations: Windows Ethernet IPv4 `192.168.50.194/24`, DHCP server and default gateway `192.168.50.1`, and DNS server **`192.168.50.1`**; DNS connection suffix currently `lan`. The Tailscale virtual interface is not the active Ethernet DNS path, and the Hyper-V default switch is a distinct virtual subnet. The host's DNS-server setting proves **use of router IP as the Windows DNS resolver**, but not that the router permits static local A records, authoritative local zones, or successful `.internal` resolution. No sensitive MAC/client identifier needs to be reproduced.

**One safe next operator action:** in Windows PowerShell on that same LAN run `nslookup ccpcerp.internal 192.168.50.1`, returning only the DNS answer/status. NXDOMAIN (non-existent domain) is a normal result before provisioning a local record, not an application or HTTPS failure; if an A record already exists, compare it with the approved NEW host `192.168.50.186` before any edits. Do not create DNS records, sign into a router admin UI, change DHCP/DNS clients, or alter OLD PROD/DEV, NEW Docker, firewall, proxy or TLS as part of this lookup.

**Next implementation decision after lookup:** determine whether the existing router/local DNS can host an explicit `ccpcerp.internal` A record reliably on the office LAN and whether it serves all authorized client VLANs during WAN outages; otherwise use a separately reviewed managed internal resolver. Any change to router DNS or DHCP is a distinct network-operation approval, not implied by the hostname selection. The manually selected November 5 backup is already restored in the isolated NEW candidate; do not repeat verification or restore.


## November 10, 2026 — Owner selects `https://ccpcerp.internal` for NEW LAN ERPNext

**Newer owner decision; supersedes earlier illustrative hostname and undecided-name notes below.** Owner proposed `https://ccpcerp.internal` as the employee address in response to the explicit hostname-choice question; proceed with this as the preferred LAN hostname for the NEW dedicated ERPNext server, distinct from legacy `ccpcerp.com` and the actual internal Frappe site identity `ccpcerp.local`. ICANN's 2024-07-29 board resolution permanently reserved the `.internal` TLD for private-use applications; this name is not a public Internet DNS or a publicly ACME-issued certificate endpoint.

**Implementation design requirements:**
- Authoritative **office-only DNS A record** `ccpcerp.internal -> 192.168.50.186`, served reliably to authorized users (including during WAN outage); no router DNS, DHCP, Windows hosts, public DNS or live traffic switched yet. Verify actual DNS infrastructure before making any change.
- The intended **SAN** is `DNS:ccpcerp.internal`. Prefer an explicitly managed internal CA (or an equivalently controlled internal issuer) with trusted root deployed to approved client computers, secured/off-host CA-key recovery, renewal and revocation; never publish private CA keys in GitHub or send them through chat. Browser trust is required even when local DNS resolves correctly. Caddy can issue `tls internal` certificates, but the current inert template uses **explicit externally provisioned PEM paths**, disables automatic issuance and is deliberately not a working CA setup.
- Updated inert `overrides/Caddyfile.dedicated-https.review` now pins the HTTPS site address to `https://ccpcerp.internal:443`; it retains host bind `192.168.50.186`, `auto_https off`, no automatic port 80, h1/h2, strict SNI, and an upstream planned as `127.0.0.1:8080`. Refetch and review the branch; actual Caddy parsing/runtime behavior is untested.
- The **current isolated A3 frontend has NO published host ports**, so the planned 127.0.0.1:8080 upstream does not yet exist. Do not activate this template, indiscriminately recreate live containers or run generic deployment/scripts; future NEW-only loopback publication, LAN-specific UFW policy, actual TLS certificate handling, WebSockets, Frappe host/forwarded scheme, recovery and pilot must be separately reviewed and validated. OLD PROD and co-hosted DEVELOPMENT are not affected by this hostname choice.
- Continue using the **owner-approved Nov 5, 2026 source**, already restored in isolated NEW candidate. Do not repeat backup verification or restore solely due to source date. Any later OLD change known before cutover must not be discarded without an explicit source-data decision. HTTPS rollout and final single-writer cutover remain separate explicit production-operation approvals.

**Next read-only operator preflight (not a deployment):** identify which local DNS service/router is actually handed to the Windows operator machine, using a bounded `ipconfig /all` inspection of **DNS Servers only**, with no full output, credentials, IP inventory, or network changes; then determine how to safely create the internal `ccpcerp.internal` A record after the separately approved operational plan. Do not query a public resolver for the reserved private name.


## November 10, 2026 — Option A HTTPS gateway review template prepared, NOT deployed

The owner again approved continuing **NEW-only HTTPS gateway preparation** and reaffirmed that the **November 5, 2026 02:00:01 four-artifact backup** is the latest and selected Option A source. This source has already been restored to the distinct `ccpc_prod_erpnext` candidate, and the owner reports authenticated Windows SSH-tunnel access and completion of browser business-area checks. Do **not** repeat that restore, require a newer backup solely based on age, or restart the browser inspection loop. The Nov 5 **data cutoff** remains separate: an old-host change made after that timestamp would not magically appear in NEW. Do not discard known later records without a deliberate source-data decision. No new backup/restore or OLD/DEV modification is authorized by selecting Nov 5.

Added a **non-active host-Caddy source template** at [`overrides/Caddyfile.dedicated-https.review`](../../overrides/Caddyfile.dedicated-https.review) on this draft PR #28 branch. Its intended future data path is **office HTTPS TCP 443 on NEW host 192.168.50.186 → Caddy → host 127.0.0.1:8080 → Docker frontend**, not an employee-facing Docker port or the Windows-local SSH tunnel. It includes `auto_https off` (no ACME issuance or automatic port-80 redirect), an explicit host IPv4 bind, HTTP/1.1+HTTP/2 (no HTTP/3 UDP 443), disabled Caddy admin endpoint and strict SNI/Host matching. It deliberately references external file paths for a separately trusted full-chain certificate and private key and contains **no certificates or secrets**. Configuration variables required at future render time are `CCPC_HTTPS_HOST`, `CCPC_TLS_FULLCHAIN_FILE`, and `CCPC_TLS_PRIVATE_KEY_FILE`; no defaults are embedded. Certificate choice and final employee hostname are **still undecided**, not inferred from the example `erp.ccpc.internal` below. Caddy only needs the cert/key path values, not private-key bytes supplied in shell history, GitHub or chat.

**Crucial implementation boundary:** The **currently running A3 candidate frontend remains internal-only, with no host-published port**. There is NO `127.0.0.1:8080` frontend upstream established by the template. The candidate's observed Docker IP `172.20.0.7` is dynamic; do **not** hardcode it as a production proxy target or assume the temporary Windows `127.0.0.1:18080` SSH tunnel exists on NEW. Establishing loopback-only frontend publication requires a **separately reviewed, NEW-candidate-scoped container/network transition**, preserving volumes and not automatically running configurator, scheduler, workers or migrations. Do not blindly apply PR #27 generic deploy code to achieve this. Until that transition is explicitly approved and verified, the Caddy template must **NOT** be activated.

**Before any eventual server change**, determine the employee HTTPS hostname and a trusted certificate/CA lifecycle; verify the effective Caddy version/parser and exact site address, PEM coverage, chain, permissions and service identity; confirm host IP and listener occupancy without touching SSH; verify runtime frontend's loopback-only binding, intended Frappe routing and forwarded-scheme/WebSocket behavior; and review specific UFW allowed LAN subnets, off-host recovery and rollback. The config must be adapted/validated against the actually installed Caddy version in a non-operational review step with synthetic environment values, **without** starting/reloading a listener. Neither Caddy, trusted certificates, proxy, port 443, DNS, client trust nor final cutover is installed or confirmed by this commit.

The fastest available route after these choices is a narrowly scoped NEW-only loopback upstream + host-gateway pilot that leaves OLD PROD/DEV and the two protected NEW rehearsals intact, followed by a single-writer final cutover only under separate explicit approval. PR #27 is still draft pre-TLS code, PR #28 is the current draft gateway configuration/design, and Option A PR #32 is the isolated acceptance profile; they are not automatically deployable as one combined generic Compose stack.


**Design status (2026-10-23):** Proposed, GitHub-only. **NOT INSTALLED, TESTED, MERGED OR DEPLOYED.** No authorization to modify live PRODUCTION, DNS, SSH/UFW, Docker, database, backups, or either Ubuntu server is implied.

## Scope and previous verified state

New dedicated `ccpcerp-prod`: `enp5s0`, DHCP-reserved (owner-reported) IPv4 `192.168.50.186/24`, gateway `192.168.50.1`; no IPv6 default route or non-link-local IPv6 address found in read-only operator output. Prior host inspection showed SSH accessible using keys, UFW incoming deny with IPv4 SSH allowed only from `192.168.50.0/24`, and an empty Docker container inventory. This is **not** a proof that all future port publication is safe. The older `ccpcerpserver` still runs live PROD+DEV and must not be disturbed.

Separate [draft PR #27](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/27), `security/dedicated-production-pre-tls-2026-10-23`, proposes an *opt-in* Docker Compose profile: frontend HTTP published on **host loopback only** `127.0.0.1:8080`, MariaDB and Redis not published on the host, nonempty database password required. It is not merged/deployed; this design depends on that or an equivalently reviewed and validated loopback-only backend.

## Reliability-first correction — reported unreliable current hostname (2026-10-23)

**New owner information:** CCPC does not currently manage a known DNS provider, and employee access through `ccpcerp.com` is intermittent. The underlying cause is **not yet diagnosed**: the current domain might resolve via router-local DNS, public DNS, client hosts entries, DNS caches, or a separate fault in network reachability or application availability. Do not assume that CCPC owns `ccpcerp.com`, or that an external DNS solution is available.

**Preferred candidate for a LAN-only installation:** a locally managed name such as **`erp.ccpc.internal`**, mapping via internal DNS to the new host's existing `192.168.50.186`, with **direct-IP emergency recovery**. `.internal` is reserved for private-use namespace (ICANN 29 July 2024); the name is a proposal, **not owner-approved final naming**. The router/DHCP or a managed local DNS system must reliably serve the private zone to **all authorized employee clients**, including when WAN Internet connectivity fails. If the router DNS itself is unreliable, move authoritative local resolution to reliably powered, backed-up local DNS infrastructure with an appropriate second independent resolver, rather than merely adding a record to an unreliable service. A public DNS server is not a fallback for a private-only `.internal` zone.

**Alternatives:** browser access by `https://192.168.50.186` is a DNS-independent fallback only with an IP-SAN certificate trusted by clients; selected Windows hosts-file mappings can bypass DNS for a small fleet but require per-client maintenance; a legitimately controlled public domain with split-horizon local DNS is a future optional solution, not a prerequisite for offline LAN operation. Avoid `.local` as an ordinary unicast-only DNS name because of multicast DNS ambiguity. Verify router DHCP reservation persistence and ensure the IP is unique and stable before deploying.

**Certificate direction:** prefer **managed internal CA and client trust rollout** if no authoritative public domain management can be established. Caddy's `tls internal` is a candidate implementation, but CA-root trust must be rolled out to each authorized browser/device, and CA private-key security, renewal, backup and recovery are mandatory. Certificates must cover the chosen DNS name and any approved direct-IP HTTPS fallback as SANs. Use public DNS-01 only if legitimate domain/DNS control is later independently verified; never attempt ACME for `.internal`.

**First read-only diagnostic on an affected Windows workstation while it is connected to the current CCPC LAN:** `nslookup ccpcerp.com`. Record the responding DNS server and A/AAAA answers both when the browser works and when it fails; note that `nslookup` bypasses Windows client hosts-file resolution and DNS cache. Distinguish DNS-response failure from application/network/TLS errors before changing employee name resolution. Do not change Windows hosts, router/DHCP, DNS, firewall, server, or production service during this investigation.

**Architectural guard:** until the LAN naming, certificate trust, and cutover method are approved, every `ccpcerp.com` mention below is a legacy illustrative label, not an assumption of a reliable final entry point. Do not install the illustrative Caddyfile or repoint DNS. The target remains HTTPS TCP 443 over the LAN.

## Recommended architecture

Use a **host-level HTTPS reverse proxy** (recommended candidate: Caddy) rather than putting the external TLS listener inside Docker. This lets new-host IPv4 traffic to port 443 enter the normal host `INPUT` firewall/UFW policy while Docker handles only the localhost-facing HTTP service. This avoids relying on UFW `INPUT` to restrict a **Docker-published** 443 port (which Docker documentation warns may bypass it).

```text
Employee Windows browser on approved LAN
  https://erp.ccpc.internal:443  (illustrative candidate; not approved)
       |
Internal LAN DNS -> 192.168.50.186 (only AFTER cutover approval)
       |
New Ubuntu host: UFW INPUT permits approved IPv4 source subnet(s) -> TCP 443
       |
Host-level Caddy TLS listener, IPv4 192.168.50.186:443
       |
Proxy HTTP to host loopback 127.0.0.1:8080
       |
Docker frontend Nginx -> Frappe backend / websocket; private DB / Redis
```

**Target public-facing port:** 443/TCP HTTPS. **Port 80/TCP:** no listener during initial deployment; a LAN-limited HTTP-to-HTTPS redirect may be considered separately after secure HTTPS is verified. **Port 443/UDP:** do not implicitly activate HTTP/3/QUIC; prefer HTTP/1.1 and HTTP/2 over TCP until separately reviewed. **Ports 8080, 3306, 6379:** do not expose on the LAN. **Port 22:** preserve the existing narrowly scoped SSH rule.

## Certificate/trust decision — blocker before runnable TLS configuration

There are two plausible options. **Do not pick one silently without validating its prerequisites:**

1. **Preferred if CCPC controls the public authoritative DNS zone for `ccpcerp.com`:** issue a publicly trusted certificate by a **DNS-01 challenge** for the hostname, without enabling inbound Internet access to the ERP server. Public authoritative TXT challenge publication must be possible. Use an external trusted validation/renewal mechanism and narrowly scoped DNS credentials (not a broad DNS token on the ERPNext server). Plan automatic certificate renewal and secure delivery/reload. Public certificate issuance may make the hostname visible in Certificate Transparency logs, but does not require a public A/AAAA record or router port forwarding to the ERP host.
2. **Otherwise:** use a CCPC-managed internal CA and issue a certificate for the approved private DNS name (candidate `erp.ccpc.internal`) and, if desired, the approved fallback IP SAN; securely distribute and trust the **CA root certificate only** on approved client devices. Protect/off-host back up the CA private key, document revocation and renewal, and test browsers/OS trust. Never distribute the private CA key to clients or store any secrets in GitHub.

For both options: validate hostname, certificate chain, rotation, expiration monitoring and recoverability. Public DNS control, public zone status, trusted CA availability, and employee device management **have not yet been confirmed**. Do not obtain certificates, publish DNS TXT records or install a CA as part of this document-only proposal.

## Host-level proxy configuration — illustrative design, NOT RUNNABLE/APPROVED AS-IS

A future version-reviewed Caddyfile could be based on the following, **only after** an approved certificate and private-key delivery path has been selected and the actual Caddy version has been validated. The PEM paths are **placeholders**, not files claimed to exist:

```caddyfile
{
    auto_https disable_redirects
    servers 192.168.50.186:443 {
        protocols h1 h2
    }
}

erp.ccpc.internal {
    bind 192.168.50.186
    tls /approved/secure/fullchain.pem /approved/secure/privkey.pem
    reverse_proxy 127.0.0.1:8080
}
```

Design rationale: `bind` limits the host listener to the intended IPv4; `auto_https disable_redirects` avoids an automatic HTTP port 80 listener; `protocols h1 h2` avoids opening UDP 443 for HTTP/3. For the actual system, verify the **effective socket addresses** after startup, because options may vary with Caddy version and site configuration. The upstream `Host` header should remain `ccpcerp.com` as received by Caddy; Docker frontend already carries `FRAPPE_SITE_NAME_HEADER=ccpcerp.local` to identify the site. Caddy normally handles WebSocket upgrades, but browser-based Socket.IO and correct upstream forwarded-host/scheme behavior must be tested with the actual ERPNext image and site settings. Never disable TLS certificate verification as a workaround.

**Important:** A Caddy configuration with a hostname can try automatic public certificate issuance if not given an appropriate explicit certificate policy. No unreviewed ACME attempt, automatic internal CA trust installation, automatic HTTP redirect, or new listener is authorized. Before applying any config, use Caddy's installed version's **`caddy validate`/`caddy adapt`** and carefully inspect its planned listeners without leaking private material.

## Firewall, segmentation and DNS design

- Maintain an explicit new-host UFW **deny incoming** default; during a later separately approved change allow TCP 443 **to `192.168.50.186` only** from the intended source IPv4 networks (tentative `192.168.50.0/24`, but decide whether guest/IoT/VLANs should be excluded and whether additional plant networks need access). This is illustrative firewall policy, **not a command to execute**.
- Since the proposed 443 listener lives on the **Ubuntu host**, packets should be filtered by the host's normal `INPUT` path. Reinspect effective iptables/nftables and UFW rules before and after any controlled deployment. Independently test permitted and denied LAN/VLAN clients.
- Keep router WAN NAT/port forwarding/UPnP/DMZ unchanged: no Internet-exposed ERP service. Test from a genuinely external network as a separate acceptance gate.
- Preserve `ccpcerp.com` internal DNS pointing to the **old** working production server until recovery, new-host services, user sign-in, TLS and attachments have been accepted. A planned DNS record change is a distinct **cutover** operation requiring explicit approval and a documented rollback.
- No IPv6 443 listener should appear; verify with `ss -lntup` and `ip6tables` during accepted integration testing. Do not disable the host's IPv6 stack merely because an IPv4-only initial design is desired.

## Health, security, and functional acceptance criteria

1. **Before any containers:** ensure PR #27 (or approved replacement) passes exact-code review, `bash -n`, applicable lint, and non-secret-leaking `docker compose ... config --quiet`. Check the *effective* frontend published ports and no DB/Redis publishes. Do not assume YAML syntax alone proves Compose resolution. Use a separately reviewed Docker project name, data-volume plan, secure secrets, backups and image versions.
2. **After separate deployment approval:** inspect actual host/bridge listeners, Docker NAT/filter rules, and Caddy/host 443 listener. Confirm **only** `127.0.0.1:8080` can reach frontend directly from host; deny direct access to 8080 from other LAN devices.
3. Test `https://ccpcerp.com` against the new host using safe temporary DNS/host-file resolution **without changing production LAN DNS**, with correct certificate trust and no mixed-content or redirect loops. Test browser sign-in, ERPNext session cookies, CSRF, site routing, links/email-generated URLs, WebSocket/Socket.IO, attachments, representative read-only records and backup recovery. Do not test by posting real accounting/stock transactions without an approved isolated process.
4. Verify 443 is accessible only from explicitly allowed IPv4 sources, denied from disallowed subnets, and denied through Internet-facing tests. Confirm UDP 443 and TCP 80 remain closed unless separately allowed.
5. Verify certificate renewal/reload with an owner-approved lifecycle, recovery assets, alerting and rollback procedures. Preserve previous production services and DNS until a separate cutover approval.

## Open decisions and safeguards

- Confirm CCPC controls public authoritative `ccpcerp.com` DNS and can issue DNS-01 TXT records; otherwise choose a managed internal CA and employee-client trust rollout.
- Decide allowed LAN/VLAN subnets and whether existing host UFW rule policy remains sufficient after an explicitly scoped 443 rule.
- Decide host proxy package/source, version pin, service permissions, certificate secret locations, persistence, logs and backup/restore procedures.
- Determine final ERPNext canonical `https://ccpcerp.com` host/scheme config and any interactions with existing site `ccpcerp.local` header.
- Arrange off-host recovery assets and clear rollback steps before even a pilot cutover.
- Maintain the distinction between GitHub changes, tests in isolated environment, new-host preparation, actual PRODUCTION deployment, and final business-user cutover.

## References

- Docker packet filtering / UFW behavior: https://docs.docker.com/engine/network/packet-filtering-firewalls/
- Docker published ports: https://docs.docker.com/engine/network/port-publishing/
- Caddy `bind`: https://caddyserver.com/docs/caddyfile/directives/bind
- Caddy global `auto_https` and `servers.protocols`: https://caddyserver.com/docs/caddyfile/options
- Caddy `reverse_proxy`: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
- Let's Encrypt DNS-01 for non-public servers: https://letsencrypt.org/ca/docs/challenge-types/
