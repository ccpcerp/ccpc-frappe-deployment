# CCPC dedicated PRODUCTION host — LAN HTTPS gateway design

**Design status (2026-10-23):** Proposed, GitHub-only. **NOT INSTALLED, TESTED, MERGED OR DEPLOYED.** No authorization to modify live PRODUCTION, DNS, SSH/UFW, Docker, database, backups, or either Ubuntu server is implied.

## Scope and previous verified state

New dedicated `ccpcerp-prod`: `enp5s0`, DHCP-reserved (owner-reported) IPv4 `192.168.50.186/24`, gateway `192.168.50.1`; no IPv6 default route or non-link-local IPv6 address found in read-only operator output. Prior host inspection showed SSH accessible using keys, UFW incoming deny with IPv4 SSH allowed only from `192.168.50.0/24`, and an empty Docker container inventory. This is **not** a proof that all future port publication is safe. The older `ccpcerpserver` still runs live PROD+DEV and must not be disturbed.

Separate [draft PR #27](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/27), `security/dedicated-production-pre-tls-2026-10-23`, proposes an *opt-in* Docker Compose profile: frontend HTTP published on **host loopback only** `127.0.0.1:8080`, MariaDB and Redis not published on the host, nonempty database password required. It is not merged/deployed; this design depends on that or an equivalently reviewed and validated loopback-only backend.

## Recommended architecture

Use a **host-level HTTPS reverse proxy** (recommended candidate: Caddy) rather than putting the external TLS listener inside Docker. This lets new-host IPv4 traffic to port 443 enter the normal host `INPUT` firewall/UFW policy while Docker handles only the localhost-facing HTTP service. This avoids relying on UFW `INPUT` to restrict a **Docker-published** 443 port (which Docker documentation warns may bypass it).

```text
Employee Windows browser on approved LAN
  https://ccpcerp.com:443
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
2. **Otherwise:** use a CCPC-managed internal CA and issue a certificate containing DNS name `ccpcerp.com`; securely distribute and trust the **CA root certificate only** on approved client devices. Protect/off-host back up the CA private key, document revocation and renewal, and test browsers/OS trust. Never distribute the private CA key to clients or store any secrets in GitHub.

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

ccpcerp.com {
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
