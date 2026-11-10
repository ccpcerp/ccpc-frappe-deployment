# CCPC dedicated PRODUCTION host — LAN HTTPS gateway design

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
