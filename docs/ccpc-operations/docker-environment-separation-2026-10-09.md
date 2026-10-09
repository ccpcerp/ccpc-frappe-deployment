# CCPC ERP — Docker Environment Separation Verification

**Verification date:** 2026-10-09  
**Host:** `ccpcerpserver`  
**Project stage:** CCPC ERP T8 / F7.4U (read-only host topology verification)  
**Status:** Docker network and MariaDB-volume separation verified from host metadata; complete application-level isolation and disposable-test readiness **not established**.

## Purpose and safety scope

This document records operator-observed command outputs from the Ubuntu Docker host during the CCPC ERP T8 security-test preparation. Every verification was a read-only Docker CLI inspection. No database or Redis connection was made, no ERPNext transactions were performed, and no containers, volumes, networks, repositories, migrations, services, or production data were changed.

The two Compose projects are named `frappe_docker_devcontainer` (confirmed DEVELOPMENT) and `frappe_docker` (other ERPNext deployment, **likely** production based on service layout; production identity was not independently authenticated by these checks). The Docker context was `default` with a local `unix:///var/run/docker.sock` endpoint.

## Observed deployment inventory

| Property | DEVELOPMENT | Other ERPNext deployment (likely production) |
| --- | --- | --- |
| Compose project | `frappe_docker_devcontainer` | `frappe_docker` |
| Docker network | `frappe_docker_devcontainer_default` | `frappe_docker_default` |
| Network driver / scope | `bridge` / `local` | `bridge` / `local` |
| MariaDB container | `frappe_docker_devcontainer-mariadb-1` | `frappe_docker-db-1` |
| MariaDB data mount | `frappe_docker_devcontainer_mariadb-data` | `frappe_docker_db-data` |
| Data mount target | `/var/lib/mysql` | `/var/lib/mysql` |
| Redis Cache | `frappe_docker_devcontainer-redis-cache-1` | `frappe_docker-redis-cache-1` |
| Redis Queue | `frappe_docker_devcontainer-redis-queue-1` | `frappe_docker-redis-queue-1` |
| Application container | `frappe_docker_devcontainer-frappe-1` | `frappe_docker-backend-1` plus frontend/workers |
| Compose-labelled container count (including stopped) | 4 | 10 (9 running, 1 exited configurator) |

DEVELOPMENT container ports reported by `docker ps -a`: `127.0.0.1:8000-8005->8000-8005/tcp` and `127.0.0.1:9000-9005->9000-9005/tcp` on Frappe; MariaDB and both Redis containers had no host-published port listed. This is a Docker-reported snapshot, not a full host firewall or remote access audit.

The other project's active network members were: `frontend`, `backend`, `websocket`, `scheduler`, `queue-short`, `queue-long`, `db`, `redis-cache`, and `redis-queue` (all prefixed `frappe_docker-` with `-1` suffix). `frappe_docker-configurator-1` was `Exited (0)`, and therefore not an active network member in the recorded snapshot.

## Evidence and exact read-only commands

### 1. Identify Compose projects and services

```bash
docker ps -a --format '{{.Label "com.docker.compose.project"}}' | sort -u
docker ps -a --filter 'label=com.docker.compose.project=frappe_docker_devcontainer' --format 'Name={{.Names}} Service={{.Label "com.docker.compose.service"}} Status={{.Status}} Ports={{.Ports}}'
docker ps -a --filter 'label=com.docker.compose.project=frappe_docker' --format 'Name={{.Names}} Service={{.Label "com.docker.compose.service"}} Status={{.Status}}'
```

Observed project names: `frappe_docker` and `frappe_docker_devcontainer`. DEVELOPMENT contained four running services: `frappe`, `mariadb`, `redis-cache`, `redis-queue`. The other project contained ten listed containers; nine running services and one completed `configurator`.

### 2. Identify network ownership and membership

```bash
docker network ls --filter 'label=com.docker.compose.project=frappe_docker_devcontainer' --format 'Network={{.Name}} Driver={{.Driver}} Scope={{.Scope}}'
docker network ls --filter 'label=com.docker.compose.project=frappe_docker' --format 'Network={{.Name}} Driver={{.Driver}} Scope={{.Scope}}'
docker network inspect frappe_docker_devcontainer_default --format '{{range .Containers}}{{println .Name}}{{end}}'
docker network inspect frappe_docker_default --format '{{range .Containers}}{{println .Name}}{{end}}'
```

The DEVELOPMENT network had exactly four listed members: its Frappe, MariaDB, Redis Cache, and Redis Queue containers. The other network had nine listed members, all carrying the `frappe_docker-` prefix. Neither network inspection listed any container from the other Compose project.

### 3. Verify explicit network attachments of database, Redis, and development Frappe

```bash
docker inspect frappe_docker_devcontainer-mariadb-1 --format '{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}'
docker inspect frappe_docker_devcontainer-redis-cache-1 frappe_docker_devcontainer-redis-queue-1 --format '{{.Name}}: {{range $name, $_ := .NetworkSettings.Networks}}{{$name}} {{end}}'
docker inspect frappe_docker_devcontainer-frappe-1 --format '{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}'
docker inspect frappe_docker-db-1 --format '{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}'
docker inspect frappe_docker-redis-cache-1 frappe_docker-redis-queue-1 --format '{{.Name}}: {{range $name, $_ := .NetworkSettings.Networks}}{{$name}} {{end}}'
```

Each DEVELOPMENT command reported only `frappe_docker_devcontainer_default`. The other deployment's database and both Redis containers reported only `frappe_docker_default`. Individual attachment inspection of the other deployment's frontend, backend, workers, websocket, and scheduler was not performed; network membership for the snapshot is documented above.

### 4. Verify MariaDB mounts and Docker-visible mount users

```bash
docker inspect frappe_docker_devcontainer-mariadb-1 --format '{{range .Mounts}}{{if eq .Destination "/var/lib/mysql"}}Volume={{.Name}} Type={{.Type}} Destination={{.Destination}}{{end}}{{end}}'
docker inspect frappe_docker-db-1 --format '{{range .Mounts}}{{if eq .Destination "/var/lib/mysql"}}Volume={{.Name}} Type={{.Type}} Destination={{.Destination}}{{end}}{{end}}'
docker ps -a --filter 'volume=frappe_docker_devcontainer_mariadb-data' --format 'Name={{.Names}} Status={{.Status}}'
docker ps -a --filter 'volume=frappe_docker_db-data' --format 'Name={{.Names}} Status={{.Status}}'
```

DEVELOPMENT mounted a Docker named volume, `frappe_docker_devcontainer_mariadb-data`, at `/var/lib/mysql`; Docker listed only `frappe_docker_devcontainer-mariadb-1` using that volume. The other deployment mounted `frappe_docker_db-data` at the same in-container destination; Docker listed only `frappe_docker-db-1` using it. Thus, the two database containers did not share the same Docker named volume in these observations.

## Interpretation and limits

**Confirmed from the observed host metadata:** Two distinct Compose projects; two distinct project-labelled bridge networks; no cross-project containers listed on either project's inspected network; separate MariaDB containers and Docker named data volumes; only the expected database container listed as a user of each respective volume; database and Redis containers attached solely to their respective project networks in the explicit attachment checks.

**Not proven by these checks:** The business identity of the `frappe_docker` deployment; absence of shared bind mounts or externally mounted files; isolation of secrets, credentials, site configuration, DNS, external integrations, host-level routing, backup locations, host processes, or outside database clients; effectiveness of ERPNext/Frappe deletion hooks; atomicity and concurrency behavior of the intercompany billing protections; or recoverability from a full restore. Network and volume inventory is a point-in-time observation and does not guarantee future state.

Importantly, **the existing DEVELOPMENT bench is not a disposable test environment**. Successful Docker separation from the other deployment is not permission to execute destructive Transaction Deletion Record, accounting, or invoice tests on that bench.

## Next control gates

1. **F7.4R (approved for read-only verification only):** Check DEVELOPMENT Frappe hook/controller registration and potential stale worker/console processes. Start with strictly read-only evidence collection, one reviewed command at a time; do not contact or modify production.
2. **Destructive integration tests remain blocked:** First provision a separate, synthetic-data-only disposable Compose project/bench with its own MariaDB and Redis services, volumes, network, files, and workers; disable external integrations and scheduler where appropriate.
3. **Recovery gate:** Establish a test snapshot and demonstrate a successful restore before any destructive experiments.
4. **Production changes remain unauthorized:** No migration, deploy, restart, deletion, volume cleanup, DB writes, Git changes to the custom application, or production hook reload is implied by this documentation.

## Evidence provenance

Transcribed from the operator's Docker CLI output in the CCPC ERP T8 conversation, verification Steps 1–19, concluding with the Redis network checks. This is documentation of observations, not a new independent test run or a guarantee of comprehensive isolation.
