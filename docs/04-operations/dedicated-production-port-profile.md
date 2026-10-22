# Dedicated PRODUCTION host — staged port and TLS policy

**Status:** GitHub-only review candidate. NOT DEPLOYED or approved for PRODUCTION execution.

This profile is designed for the **separate, newly prepared** `ccpcerp-prod` host (`192.168.50.186/24`, interface `enp5s0`). It must not be applied to the existing `ccpcerpserver` shared PRODUCTION/DEVELOPMENT installation. Keep the old host serving users until an independently approved, backed-up cutover.

## Recommended port design

| Port | Role | Exposure |
| --- | --- | --- |
| TCP 443 | Intended future **HTTPS** user entry point (`https://ccpcerp.com`) | LAN-only, after a reviewed TLS reverse proxy/certificate and source-network policy are implemented |
| TCP 80 | Optional HTTP -> HTTPS redirect only | Do not expose until redirect and firewall design are reviewed |
| TCP 8080 | ERPNext frontend HTTP on the new host during preparation | Bind **only** to `127.0.0.1`; do not expose to LAN clients |
| TCP 22 | SSH | Preserve current authorized `192.168.50.0/24`-scoped UFW access; do not modify here |
| TCP 3306, 6379 | MariaDB and Redis container services | No host-published ports |

**Port 443 alone does not enable TLS.** Certificate acquisition, chain validation, trusted client CA, internal DNS, WebSocket proxying, `Host` and `X-Forwarded-Proto` behavior, ERPNext URL configuration, HTTP-to-HTTPS redirects, and app-level tests are separate required gates. Since `ccpcerp.com` is presently an internal-LAN hostname, verify a certificate issuance/trust approach before any HTTPS deployment; do not assume public HTTP challenges or automatically trusted self-signed certificates will work.

## Opt-in pre-TLS profile (GitHub code only)

The pre-TLS override is `overrides/compose.dedicated-pre-tls.yaml`. It must be loaded **after** `overrides/compose.lan-production.yaml` so the prior `80:8080` and base `8080:8080` mappings are replaced. It publishes exactly `127.0.0.1:8080:8080/tcp`; it does **not** publish port 80 or 443. The port restriction is appropriate to Docker Engine 29+ but must still be validated using the effective Compose config and observed Docker bindings before relying on it.

The existing `scripts/config.sh` defaults to `CCPC_DEPLOYMENT_PROFILE=legacy-lan` and preserves the old four-file Compose stack, `HTTP_PUBLISH_PORT` and original `http://127.0.0.1:$HTTP_PUBLISH_PORT` health check. **Nothing changes for the existing deployment unless a new opt-in profile is deliberately selected.**

When `CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls` is explicitly selected for the new host, the scripts append the fifth override and change the host-local health check to `http://127.0.0.1:8080` while preserving the internal Frappe `Host: ccpcerp.local` header. Deployment summary then explicitly labels the URL as host-local preparation, not the final employee-facing URL.

The dedicated overlay also overrides the generic MariaDB template password expression with `${DB_PASSWORD:?Dedicated production requires a nonempty DB_PASSWORD}`. This makes a missing/empty `DB_PASSWORD` an error in Compose interpolation for the dedicated profile. It does **not** measure password strength or substitute for secure on-host credential provisioning. Keep values in owner-controlled secure storage; never place credentials in GitHub, shell history, chat logs, Compose logs, or this document.

## Read-only validation before any execution

On a **separate reviewed checkout** of the feature branch, assess `scripts/config.sh` syntax and resulting variables without deploying anything. Before evaluating any Compose file, arrange an approved secret injection mechanism that does not print or commit credentials. A full `docker compose config` outputs interpolated secrets; avoid printing it. Prefer `docker compose ... config --quiet` for an approved local syntax/effective-model check after the actual environment and secret handling are in place. Confirm the final list of files contains the new overlay **last** and that the effective frontend published port is **loopback-only**, with no published MariaDB/Redis ports.

**Do not run** `docker compose up`, `scripts/deploy.sh`, `scripts/rollback.sh`, `bench migrate`, a restore, a DNS change, or any firewall/network modifications as part of review. No new stack currently exists on this host.

## Gates before making the new server live

1. Review and merge this opt-in profile through the normal GitHub review process; retain the old-host defaults unchanged.
2. Establish off-host, verified, restorable four-artifact Frappe backups and preserve old running services.
3. Review the new server's dedicated project name, persistent volumes, non-default credentials, correct app image/version and security updates.
4. Design and test HTTPS reverse proxy on **LAN IPv4 `192.168.50.186:443`**, with certificate lifecycle, internal DNS, WebSocket proxying and redirect policy. Do not open 80/443 from this pre-TLS profile.
5. Define and independently verify which source network(s) can connect. A binding to one host IP **does not** enforce allowed source subnets; published Docker ports may bypass UFW's regular INPUT rules. Consider the Docker `DOCKER-USER` forwarding chain for applicable traffic only after inspecting exact active rules and preserving SSH/rollback.
6. Separately obtain explicit authorization for new-host application deployment, restoration/migration, validation, DNS cutover, and retirement of the old PRODUCTION role.

**No claim of production readiness:** GitHub static review is not live Docker Compose resolution, database integration testing, TLS verification, or deployment.
