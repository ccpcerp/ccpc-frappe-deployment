# LAN Production Access

## Purpose

CCPC ERPNext is available to LAN users at `http://ccpcerp.com`. This configuration provides HTTP access on the standard port without exposing a `:8080` URL.

The request path is:

```text
LAN client
  -> LAN DNS resolves ccpcerp.com to the ERP server
  -> ERP server port 80
  -> Docker frontend port 8080
  -> Frappe site ccpcerp.local
```

## Compose Override

Use the production service overrides and LAN production override with the base Compose file:

```bash
docker compose \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.lan-production.yaml \
  config
```

The override publishes `${HTTP_PUBLISH_PORT:-80}:8080`. Set `HTTP_PUBLISH_PORT` only when a different host port is required.

To override the port for a framework operation, set `HTTP_PUBLISH_PORT` in the environment that invokes the deployment or rollback script; the framework exports the resolved value to Docker Compose.

The internal Frappe site remains `ccpcerp.local`. `FRAPPE_SITE_NAME_HEADER` defaults to that identity so requests for the LAN-facing `ccpcerp.com` name route to the existing site.

## Deployment Framework

The CCPC deployment configuration defines the Compose file arguments once in `scripts/config.sh`. The shared `ccpc_compose` helper applies the base file, MariaDB and Redis service overrides, and LAN production override to deployment, container verification, and migration operations used by both deploy and rollback workflows.

Do not call plain `docker compose` for CCPC production operations because that would omit the LAN production override.

## Network Requirements

LAN DNS must resolve `ccpcerp.com` to the ERP server's LAN IP address. Router, DNS, VLAN, and firewall configuration are environment-specific and are not managed by this repository.

This is a LAN-only HTTP design. It does not configure HTTPS, public DNS, Internet-facing NAT, port forwarding, or public Internet exposure.
