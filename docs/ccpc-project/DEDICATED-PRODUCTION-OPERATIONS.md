# CCPC ERPNext — Dedicated PRODUCTION Operations and Deployment Record

## NEW REHEARSAL STAGE 6 NOVEMBER 5 BACKUP STRUCTURE VERIFIED — 2026-11-07

**PASS — owner-run read-only Stage 6 backup structure inspection on NEW `ccpcadmin@ccpcerp-prod`.** Owner pasted:

```text
SQL_GZIP_READ_OK
SQL_MYSQL_STYLE_HEADER=True
SQL_CREATE_TABLE_COUNT=741
SQL_INSERT_INTO_COUNT=165
SQL_CREATE_DATABASE_COUNT=0
SQL_USE_DATABASE_COUNT=0
SQL_CREATE_USER_COUNT=0
SQL_GRANT_COUNT=0
SQL_SET_GLOBAL_COUNT=0
PUBLIC_ARCHIVE_MEMBERS=1
PUBLIC_ARCHIVE_FILES=0
PUBLIC_ARCHIVE_DIRECTORIES=1
PUBLIC_ARCHIVE_OTHER=0
PUBLIC_ARCHIVE_UNSAFE_PATHS=0
PRIVATE_ARCHIVE_MEMBERS=2
PRIVATE_ARCHIVE_FILES=1
PRIVATE_ARCHIVE_DIRECTORIES=1
PRIVATE_ARCHIVE_OTHER=0
PRIVATE_ARCHIVE_UNSAFE_PATHS=0
SITE_CONFIG_HAS_DB_NAME=True
SITE_CONFIG_HAS_DB_PASSWORD=True
SITE_CONFIG_HAS_ENCRYPTION_KEY=True
SITE_CONFIG_HAS_DB_HOST=False
SITE_CONFIG_HAS_DB_PORT=False
SITE_CONFIG_HAS_BACKUP_ENCRYPTION_KEY=False
BACKUP_STRUCTURE_INSPECTION_COMPLETE
```

**Interpretation:** The 2026-11-05 02:00 `database.sql.gz` can be streamed as a plain MariaDB/MySQL SQL dump, with 741 apparent CREATE TABLE and 165 INSERT INTO line starts. The inspector found no line-start `CREATE DATABASE`, `USE`, `CREATE USER`, `GRANT`, `SET GLOBAL` statements, but this is **not proof that all SQL directives are benign**; SQL comments, multi-statement lines, file-reads or triggers need separate review before a raw manual SQL import. Public tar contains a single directory (no public attachments); private tar contains one file plus a directory, and no absolute/parent-traversal archive paths were observed by the inspector. Site config includes essential site database name, historical password, and encryption key; no reported backup encryption key. The private file might be operationally important despite its small size. Archive member path shapes and old DB identity values were deliberately not printed.

**Restore design and safety:** Use the official Frappe `bench --site <site> restore <sql.gz> --with-public-files <tar> --with-private-files <tar>` mechanism where feasible; Frappe reference documents `--db-root-username`, `--db-root-password`, `--db-name`, `--admin-password` options (https://docs.frappe.io/framework/user/en/bench/reference/restore). **Do not blindly supply a root password on process argv or paste it into chat**. Protect OLD `encryption_key` within NEW rehearsal site while replacing historical DB credentials with new rehearsal-only credentials; no OLD PRODUCTION database user/password reuse, no mail/queue/scheduler/frontend activation, no live DNS or ports. Prep must check the SQL dump/header and MariaDB target emptiness and site configuration mapping before selecting `bench restore` or controlled SQL import. Initial Docker network `Internal=true` and no published ports do not independently prove host-access or all outbound restrictions; avoid starting Frappe processes with restored production data until independently verified. Historic Nov 5 input remains rehearsal-only, not a final cutover snapshot.

**Next step under owner-approved staged isolated rehearsal:** A bounded *read-only* pre-restore target/mapping check, without displaying any DB names, old passwords, encryption key, private attachment filenames or data rows. Verify backup site `db_name` is a valid portable SQL identifier and `encryption_key` nonempty; inspect SQL for additional potentially privileged/out-of-scope directives and references to explicit cross-schema names; inspect tar root layout without exposing private member names; confirm target MariaDB has no non-system database (via socket/local-root access without displaying the root credential), and only the three vetted rehearsal services are running. Review results before creating database/site or running restore. No schema import or backup file changes in this step.

## NEW REHEARSAL STAGE 5 PRE-RESTORE INTEGRITY VERIFIED — 2026-11-07

**PASS — operator-run Stage 5 read-only pre-restore validation on NEW `ccpcadmin@ccpcerp-prod`.** User pasted:

```text
REHEARSAL_THREE_CONTAINERS_VERIFIED
REHEARSAL_DATABASE_HEALTHY
REHEARSAL_REDIS_CACHE_TMPFS_VERIFIED
REHEARSAL_REDIS_PING_OK=redis-cache
REHEARSAL_REDIS_PING_OK=redis-queue
BACKUP_HASH_VERIFIED=20261105_020001-ccpcerp_local-database.sql.gz
BACKUP_HASH_VERIFIED=20261105_020001-ccpcerp_local-files.tar
BACKUP_HASH_VERIFIED=20261105_020001-ccpcerp_local-private-files.tar
BACKUP_HASH_VERIFIED=20261105_020001-ccpcerp_local-site_config_backup.json
BACKUP_SITE_CONFIG_JSON_VALID
REHEARSAL_BACKUP_ARCHIVES_VALID
REHEARSAL_PRE_RESTORE_INTEGRITY_CHECK_PASSED
```

**Validated scope:** Three NEW rehearsal containers' GitHub/OLD-matched immutable image IDs, project/service labels, single `ccpc_restore_rehearsal_20261107_default` network, no host port mappings, no privileged/restart mode, MariaDB healthy state, exact intended DB/Redis queue volume mounts and Redis cache `HostConfig.Tmpfs=/data`. Network `Internal=true`, three attached containers; exactly four named rehearsal Docker volumes. The user-run `redis-cli ping` returned PONG for each Redis instance. All four historical 2026-11-05 02:00 backup files in NEW `/home/ccpcadmin/.ccpc-nov05-backup-transfer-20261106` again matched exact recorded names, sizes and SHA-256 with `ccpcadmin:0600` file permissions and `ccpcadmin:0700` directory. `gzip -t` for the SQL archive, `tar -tf` for both file archives, and JSON parse of the small credential-containing site_config backup passed without printing content. No database SQL import, site file restore, Frappe process, mail, queue, schedulers, integrations or cutover in this step.

**Next safe concrete operation under existing NEW-only isolated-rehearsal approval:** Read-only inspect backup *structure* (SQL dump header markers/type and public/private archive member path shape), reporting only sanitized indicators and counts, no actual table contents or site_config JSON values. Confirm database dump is a Frappe-compatible plain SQL archive versus needing a `bench restore` special handler, check whether it contains `CREATE DATABASE` / `USE` / unsafe privileged or global statements, whether backup tar members contain expected Frappe `public/files` and `private/files` relative paths, and whether `site_config` contains essential key *names only*. Do not pipe full SQL output or archive paths containing sensitive names into chat. Then implement the narrowest safe NEW-only restore without exposing new or old credentials and without starting any app services; note a private restore requires preserving encryption_key and DB-name/user mapping. If SQL format/header deviates from expectations, stop for careful restore planning rather than using broad DB imports. Runtime outbound isolation has not been tested by network attribute alone, so do not start ERPNext, scheduler, queue workers, frontend, email or integrations. Final cutover still requires new consistent data snapshot and separate approval.

## NEW REHEARSAL STAGE 4 DIAGNOSTIC RESOLVED: REDIS CACHE TMPFS PRESENT — 2026-11-07

**PASS — owner-run read-only diagnostic after Stage 4 verification STOP; no rerun, restart or cleanup.** On NEW `ccpcadmin@ccpcerp-prod` the user reported these filtered Docker observations:

```text
SERVICE=db
  STATUS=running
  HEALTH=healthy
  RESTART=no
  PUBLISHED_PORTS=False
  NETWORKS=ccpc_restore_rehearsal_20261107_default
  MOUNT=volume|/var/lib/mysql|ccpc_restore_rehearsal_20261107_db-data
  TMPFS_PATHS=none
SERVICE=redis-cache
  STATUS=running
  HEALTH=not-reported
  RESTART=no
  PUBLISHED_PORTS=False
  NETWORKS=ccpc_restore_rehearsal_20261107_default
  TMPFS_PATHS=/data
SERVICE=redis-queue
  STATUS=running
  HEALTH=not-reported
  RESTART=no
  PUBLISHED_PORTS=False
  NETWORKS=ccpc_restore_rehearsal_20261107_default
  MOUNT=volume|/data|ccpc_restore_rehearsal_20261107_redis-queue-data
  TMPFS_PATHS=none
=== DOCKER VOLUME NAMES ===
ccpc_restore_rehearsal_20261107_db-data
ccpc_restore_rehearsal_20261107_logs
ccpc_restore_rehearsal_20261107_redis-queue-data
ccpc_restore_rehearsal_20261107_sites
=== REHEARSAL NETWORK ===
INTERNAL=true ATTACHED=3
REHEARSAL_READ_ONLY_DIAGNOSTIC_COMPLETE
```

**Root cause of apparent Stage 4 STOP:** `redis-cache` uses the intended Docker `HostConfig.Tmpfs` mapping at `/data`, while Docker's high-level `Mounts` array is empty for this mount. The original validator required `Mounts` to contain `("tmpfs", "", "/data")`, a false assumption. The diagnostic shows **no unintended anonymous Redis cache volume**, and only the four expected named rehearsal volumes. The three intended container services report running; MariaDB health status `healthy`; both Redis services have no Docker healthcheck reported. All three show no published ports, no automatic restart, and only the dedicated internal network. There are three network attachments. **Stage 4 startup and these observable isolation checks are thus PASS with a verifier-only correction; no container restart or change needed.**

**Remaining independent checks before any Nov 5 business-data restore:** Read-only verify three actual container IDs against pinned image IDs, exact project/service labels and actual mounts (recognize Redis cache's `HostConfig.Tmpfs` instead of `Mounts`), check Redis `PING`/MariaDB health without printing passwords, and independently rehash the four historical Nov 5 backups inside private NEW staging. External egress and host-to-container access are **not yet independently validated** by the `internal=true` attribute; avoid app/frontend/queue/scheduler activation, outbound email or third-party integrations until separately fail-closed. No business backup restore or production cutover reported. Retain all prior resources.

## NEW REHEARSAL STAGE 4 THREE CONTAINERS STARTED; REDIS-CACHE MOUNT CHECK STOP — 2026-11-07

**PARTIAL SUCCESS / STOP — operator-run approved Stage 4 on NEW `ccpcadmin@ccpcerp-prod`.** Owner pasted:

```text
PRIVATE_REHEARSAL_SECRET_REVERIFIED
REHEARSAL_STAGE4_DOCKER_PREFLIGHT_OK
REHEARSAL_REAL_SECRET_CONFIG_CHECK_PASSED
REHEARSAL_EXPLICIT_THREE_SERVICE_ALLOWLIST_READY
STARTING_REHEARSAL_DATABASE_AND_REDIS_ONLY
[+] up 3/3
Container ccpc_restore_rehearsal_20261107-redis-queue-1 Started
Container ccpc_restore_rehearsal_20261107-db-1 Started
Container ccpc_restore_rehearsal_20261107-redis-cache-1 Started
STOP: unexpected container mount: redis-cache
```

The script reached `docker compose up -d --no-deps --no-build --pull never --no-recreate db redis-cache redis-queue` and Docker reported all three container starts. The script's subsequent in-memory filtered `docker inspect` validator stopped on `redis-cache` because its `Mounts` set differed from the hardcoded expectation `{("tmpfs", "", "/data")}`. **Do not equate this mismatch with failed Redis runtime, nor treat "up 3/3" as complete isolation verification.** The final `REHEARSAL_DB_AND_REDIS_STARTED_NO_BUSINESS_DATA` marker was NOT reached. Because the shell exited at this point, the later network attachment count and named-volume inventory checks did not execute. Actual current container health, Redis cache mount representation, and any anonymous volumes remain **unverified**. The safe general hypothesis is different representation of Redis `/data` tmpfs in `HostConfig.Tmpfs` vs `Mounts` or an image-declared anonymous volume, but no live Docker inspection has confirmed either yet. No business-data restore was invoked by this command.

**No rerun, cleanup or restart before diagnosis.** Next operator step is strictly **read-only**: reverify NEW hostname/user and local Docker context, list three current container IDs/statuses, inspect `Config.Labels` only for project/service, `State.Status` and DB health status, `Image` ID match, published host ports/restart policy, network names, `Mounts` type/volume-name/destination, `HostConfig.Tmpfs` key names, named/anonymous Docker volume inventory and isolated network internal/attachment count; output only these filtered fields, never complete `docker inspect` JSON or `Config.Env`, DB secret or site backup. Determine whether cache uses actual tmpfs or has an unexpected anonymous persistent volume. If isolation mismatch is material, stop before backup restore and plan explicit fix; do not delete volumes or overwrite production. Any changes are limited to the previously approved isolated NEW rehearsal; no OLD PRODUCTION/DEV, live cutover, worker/scheduler, frontend or data restore yet.

## NEW REHEARSAL DATABASE SECRET CREATED PRIVATELY — 2026-11-07

**PASS — owner-run Stage 3 after explicit phased rehearsal approval.** Owner pasted these markers from the guarded NEW-host script:

```text
REHEARSAL_DOCKER_RESOURCES_REVERIFIED
REHEARSAL_PRIVATE_DIRECTORY_700_OK
REHEARSAL_CREDENTIAL_FILE_600_OK
REHEARSAL_STRONG_RANDOM_PASSWORD_CREATED
REHEARSAL_CREDENTIAL_READY_NO_SECRET_DISPLAYED
NEW_REHEARSAL_CREDENTIAL_PREPARED
```

**State:** On NEW `ccpcadmin@ccpcerp-prod`, Docker network `ccpc_restore_rehearsal_20261107_default` remained an isolated bridge with zero attached containers; named local volume inventory consisted only of four labeled rehearsal resources `sites`, `db-data`, `logs`, `redis-queue-data`. The guarded script created a new `/home/ccpcadmin/.ccpc-rehearsal-secrets-20261107/` directory owned by `ccpcadmin` mode `0700`, and `db.env` owned by `ccpcadmin` mode `0600` (created with `O_CREAT|O_EXCL|O_NOFOLLOW`). File contains exactly `DB_PASSWORD=<random 64-character lowercase hexadecimal secret>` plus newline, produced via Python `secrets.token_hex(32)`; the actual secret was **never printed or provided to ChatGPT**. No production or old database password reused, and synthetic `CCPC_SYNTHETIC_TEST_ONLY` is not used. Neither database nor Redis services have been started, and no business data restored.

**Next approved Stage 4, operator-run only, not yet performed:** Revalidate correct NEW host account, default local Docker socket, existing isolated network/zero containers/four labels and names, five GitHub-pinned Compose source blobs, sixth scratch-only override SHA-256 `65832a8be0f57e24c1134549136638e82833957ae785675fd9f2b543f92672e8`, exact trusted imported image IDs, and private env file owner/mode plus a nonprinting format check. Use `sudo -n env -i` with `--env-file /home/ccpcadmin/.ccpc-rehearsal-secrets-20261107/db.env` and project `ccpc_restore_rehearsal_20261107` to render the exact six-file effective Compose model and check in a JSON-to-Python pipe that it includes no published ports, only the declared internal default network and four labeled named volumes, disabled restart policies, and appropriate inactive profiles. No complete config/secret output. Only then run exactly `docker compose up -d --no-deps --no-build --pull never --no-recreate db redis-cache redis-queue` against the rehearsal project. **Do not start configurator, backend, frontend, websocket, scheduler, or queue workers at this stage.** After the operation inspect all NEW containers, their project/service labels, image IDs, single isolated network, no host ports, and health/running state; stop after output. Never invoke `docker compose up` without explicit service allowlist. On partial failure leave resources intact, inspect before any rerun or cleanup. Stage 4 uses real NEW rehearsal secret but **no production backup data**. Do not print credentials or unfiltered `docker inspect`/Compose JSON.

**Approval and continuity:** Owner's 2026-11-07 explicit `Approved` encompasses phased isolated NEW-only rehearsal including Stage 4. OLD PRODUCTION/DEVELOPMENT remains untouched. A future restore of immutable Nov 5 02:00 snapshots is rehearsal only and requires isolation validation after DB/Redis start. Go-live, cutover, enabling workers/email/integrations or accessing old production remain excluded.

## NEW ISOLATED REHEARSAL FOUR DOCKER VOLUMES CREATED AND VERIFIED — 2026-11-07

**PASS — owner-run Stage 2 on NEW `ccpcadmin@ccpcerp-prod`, after explicit overall phased rehearsal approval.** Reported success markers:

```text
REHEARSAL_SUBNET_ROUTING_CHECK_PASSED
REHEARSAL_VOLUME_PREFLIGHT_OK
REHEARSAL_VOLUME_VERIFIED=sites
REHEARSAL_VOLUME_VERIFIED=db-data
REHEARSAL_VOLUME_VERIFIED=logs
REHEARSAL_VOLUME_VERIFIED=redis-queue-data
NEW_REHEARSAL_FOUR_VOLUMES_CREATED_AND_VERIFIED
```

The guarded command checked host/account, Docker local default socket context, existing six-file scratch rehearsal YAML SHA-256, expected isolated Docker bridge network labels and `Internal=true`, exact network subnet `172.18.0.0/16`, zero attached containers, and zero previously existing volumes/containers. A Python check examined IPv4 host interfaces and route table for overlaps against the rehearsal network, excluding its own bridge. Then Docker created four **NEW-only** named local volumes with Compose project/volume and rehearsal-scope labels:
- `ccpc_restore_rehearsal_20261107_sites`
- `ccpc_restore_rehearsal_20261107_db-data`
- `ccpc_restore_rehearsal_20261107_logs`
- `ccpc_restore_rehearsal_20261107_redis-queue-data`

The script verified all four volume driver/project/volume/scope labels and reported no new containers. The operator's paste began with garbled echoed script fragments but all expected success markers appeared. This is **operator-reported evidence**, not direct ChatGPT access to the host. **Stage 2 status: volume creation and basic routing guard passed**. Volume content was not independently inspected; the volumes are newly created by the guarded script and intended to be empty. Do not claim Docker runtime egress restriction, database initialization, app health, or actual recovery has been tested.

**Next approved guarded stage:** Before DB/Redis startup, generate a NEW nonproduction-only strong random DB password under `/home/ccpcadmin/.ccpc-rehearsal-secrets-20261107` (owner/mode `ccpcadmin:700`) with exactly one `DB_PASSWORD=<random>` line in `0600` private file. Avoid real OLD/NEW PRODUCTION database credentials, production `.env`, shell history, STDOUT, ChatGPT messages, Git, and weak synthetic `CCPC_SYNTHETIC_TEST_ONLY` value. Guard that path does not already exist and do not overwrite existing secrets. After output verifies password file path metadata and that there are still zero containers, inspect a dedicated project six-file Compose model and service allowlist with the real file **without dumping the rendered JSON/secret** before starting only `db`, `redis-cache`, `redis-queue`. Keep network internal, no published ports, restart policies disabled, no scheduler/queue workers/frontend/websocket; note even backend must remain stopped at this stage. Confirm authorized project/volume names and labels first. Stop and review after every mutation.

**OLD PRODUCTION / DEVELOPMENT untouched; no database or files restored; no cutover authorized.** November 5 02:00 four-file backup remains an immutable, independently checked rehearsal source, not current final cutover snapshot.

## NEW ISOLATED REHEARSAL DOCKER NETWORK CREATED AND VERIFIED — 2026-11-07

**PASS — owner-run NEW-server-only Stage 1, after explicit approval.** On `ccpcadmin@ccpcerp-prod`, the guarded operation verified correct host and account, local default Docker context, expected immutable image IDs, absence of Docker containers/volumes and preexisting project network, and SHA-256 of six-file rehearsal scratch override before creating exactly one new Docker bridge network. Operator output:

```text
REHEARSAL_NETWORK_PREFLIGHT_OK
REHEARSAL_NETWORK_NAME=ccpc_restore_rehearsal_20261107_default
REHEARSAL_NETWORK_INTERNAL_VERIFIED
REHEARSAL_NETWORK_ZERO_CONTAINERS
REHEARSAL_NETWORK_SUBNET=172.18.0.0/16
NEW_REHEARSAL_NETWORK_CREATED_AND_VERIFIED
```

**Observed state:** Unique NEW rehearsal network `ccpc_restore_rehearsal_20261107_default`, bridge, `Internal=true`, `Attachable=false`, `EnableIPv6=false`, correct Compose project/network labels, zero attached containers, Docker IPAM subnet `172.18.0.0/16`. The terminal success markers are operator-reported and verified against the stated guarded command; ChatGPT did not access Docker remotely. The network is a deliberate NEW Docker host mutation authorized for this phased non-live rehearsal. No new volumes, DB/Redis/ERPNext containers, real credentials, database/file restore, or OLD PRODUCTION/DEVELOPMENT changes were requested or reported by this step.

**Remaining risk before connecting services or restoring business records:** `Internal=true` is a Docker network attribute, not proof of traffic filtering or absence of host routing/LAN overlap. Verify NEW host routes and interface subnets against `172.18.0.0/16`, confirm only expected network labels/driver/IPAM and no newly attached containers, and verify Docker volume/containers still absent. If conflict or mutation is discovered, stop without deleting/recreating the approved network blindly. Later start must use explicit service allowlist and real locally generated credentials, not synthetic parser password. A November 5 02:00 backup restore remains a *rehearsal*, never a final cutover dataset.

## OWNER APPROVED PHASED ISOLATED NEW-HOST RESTORATION REHEARSAL — 2026-11-07

**Owner explicitly replied "Approved"** to the immediately preceding bounded question: a phased, NEW-server-only, isolated NON-LIVE restoration rehearsal with guarded stage-by-stage verification. Approval includes (i) creating and inspecting NEW-only internal Docker network, staged volumes and DB/Redis containers, (ii) restoring the four previously independently verified November 5, 2026 02:00 historical OLD PRODUCTION backup artifacts into that isolated environment, and (iii) validating preserved records, permissions, accounting, schema and attachments with no active schedulers, queue workers, email, external integrations or employee access. Do NOT conflate approval with permission for final production cutover, OLD PRODUCTION/DEVELOPMENT changes, activating external connections, migrating to unmerged custom app code, destructive cleanup, or any network/DNS changes outside NEW.

**Source/preflight already verified by owner:** Three immutable Docker image IDs match OLD PRODUCTION: `ccpcerp:v16.50.0` `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`, `mariadb:11.8` `sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4`, `redis:8.6-alpine` `sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763`. NEW had no containers or Docker volumes after import. Six-file rehearsal scratch Compose YAML has SHA-256 `65832a8be0f57e24c1134549136638e82833957ae785675fd9f2b543f92672e8`, accepted by real Compose config parser with synthetic credentials, declared an `internal: true` network, no published ports, restart policies `no`, and nondefault profiles for frontend/websocket/scheduler/queue workers. This is source-model verification only, not live isolation.

**Design decision:** Use an unmistakably separate rehearsal project `ccpc_restore_rehearsal_20261107`, NOT the candidate production project `ccpc_prod_erpnext`, for all later rehearsed Docker resources; the six-file scratch model must later be rendered again with this project name and guarded against unexpected selectors. Retain the original five GitHub pinned files and sixth scratch-only override unchanged. No `docker compose up` of the complete default stack; explicit service allowlists, engine scope and startup dependencies must be reviewed before DB/Redis activation. Profiles are *not* themselves a sandbox. Any future real database password must be newly generated, stored locally in user-private `0600` file within `0700` directory and never pasted into chat, git, logs or command history. The synthetic string `CCPC_SYNTHETIC_TEST_ONLY` is prohibited for real DB service startup.

**Stage 1, next operator action (approved, not yet executed):** On NEW only, guard `hostnamectl --static=ccpcerp-prod` and `id -un=ccpcadmin`, reject ambient remote Docker context, verify local Docker Unix socket target and all three image IDs, confirm no unexpected containers/volumes and no preexisting network/project label, check six-file override hash, then create only the unique Docker bridge network `ccpc_restore_rehearsal_20261107_default` via `docker network create --driver bridge --internal` with Compose ownership labels `com.docker.compose.project=ccpc_restore_rehearsal_20261107`, `com.docker.compose.network=default` and an extra rehearsal-purpose label. Immediately inspect `Driver=bridge`, `Internal=true`, `Attachable=false`, `EnableIPv6=false`, project/network labels and zero attached containers; record its actual IPAM subnet. STOP if any mismatch. This is a Docker host network change permitted only under this newly scoped approval, **not** yet a fully tested firewall or data isolation. Do not allocate Docker volumes, start any container or restore data in stage 1; stop and review operator output. If create succeeded but inspection failed, leave the network for investigation rather than blindly rerunning or removing it.

**Stage 2 and beyond, separately gated by evidence (but within owner's stated overall rehearsal approval):** Verify newly created network, check reserved names, formulate sanitized `docker compose` allowlisted DB/Redis startup with real secret and no startup side effects, validate engine isolation, then verify backup file hashes and restore in isolated staged steps. Keep OLD PRODUCTION serving untouched and never describe November 5 02:00 snapshot as final or current cutover data. Go-live still needs a new consistent, write-fenced backup, reconciliation, independent restore test and explicit separate authorization. Preserve all existing backups/archives and avoid Docker prune/cleanup.

## NEW SIX-FILE REHEARSAL-ONLY COMPOSE OVERRIDE VALIDATED — 2026-11-07

**PASS — owner-run on NEW `ccpcadmin@ccpcerp-prod` during preparation-only approval.** The operator generated a new rehearsal-only scratch override at `/home/ccpcadmin/.ccpc-compose-review-c12d46f/source-only/compose.rehearsal-only.yaml`, preserving the original five pinned GitHub Compose files and the two original checkout worktrees. Prior to creation, the guarded command verified NEW host/user, private scratch location, absence of an existing override or checkout `.env`, and the five original Git blob hashes. The override is a private 0600 scratch YAML, **not** reviewed release code and not installed as a live deployment.

The operator pasted:

```text
REHEARSAL_INTERNAL_NETWORK_CONFIG_OK
REHEARSAL_NO_PUBLISHED_PORTS_OK
REHEARSAL_BACKGROUND_PROFILES_INACTIVE_BY_DEFAULT
REHEARSAL_RESTART_POLICIES_DISABLED
REHEARSAL_SYNTHETIC_CONFIG_VALIDATED
REHEARSAL_OVERRIDE_SHA256:
65832a8be0f57e24c1134549136638e82833957ae785675fd9f2b543f92672e8  /home/ccpcadmin/.ccpc-compose-review-c12d46f/source-only/compose.rehearsal-only.yaml
REHEARSAL_PREPARATION_ONLY_COMPLETE
```

**Test scope:** The exact first five pinned YAMLs were layered with this sixth scratch override, rendered via real NEW Docker Compose CLI `config --format json`, and checked in-memory by Python using `env -i` and a **synthetic** `DB_PASSWORD`; no interpolated full model or production credential was displayed. Verified project name `ccpc_prod_erpnext`, declared internal default network, no published ports, restart policy `no` for every service, and `frontend`, `websocket`, `scheduler`, `queue-short`, `queue-long` assigned `ccpc-rehearsal-disabled` profile. The core service definitions `configurator`, `backend`, `db`, `redis-cache`, `redis-queue` were not assigned such profiles. The operator's terminal input echo was partially garbled, but all end-of-script expected markers and an exact SHA-256 line were printed.

**What this does not prove:** Compose parser acceptance and profiles do *not* establish runtime isolation, actual service activation order, absence of egress/DNS to external destinations, site schedulers/events disabled in persisted data, lack of email/integration side effects, restored data correctness, or persistent on-host server state. Profiles are opt-in but can be overridden; default `docker compose up` could start core backend and Redis/DB services even with other services profiled. Do **not** run `up`, `run`, `start`, network create, volume create, DB/file restore, `bench migrate`, scheduling, network cutover or cleanup under preparation-only authorization.

**Next distinct authorization gate (not yet granted):** A phased **NEW-host-only, isolated non-live rehearsal** with preserved OLD PRODUCTION/DEVELOPMENT and no traffic cutover. Before giving any mutating command, prepare and review exact guarded Compose/project/volume selection, vetted real Docker image IDs, secret source and non-printing handling, no host-port publication, internal-network enforcement, explicit *service allowlist* excluding frontend/websocket/scheduler/queue workers, no unintended public routing, reversible new-only resource names/rollback strategy and staged stop-on-failure proof. The four independently transferred 2026-11-05 02:00 production backup artifacts are historical rehearsal inputs, not authoritative final cutover snapshot; a real restore of them requires explicit scoped approval and must be free of outgoing email/external integration effects. Do not silently use `CCPC_SYNTHETIC_TEST_ONLY` as actual database password. Later separate cutover always requires a new, consistent reconciled backup and its own approval. Nothing was started or restored in this checkpoint.

## NEW SANITIZED DEDICATED COMPOSE LAYOUT VERIFIED — 2026-11-07

**PASS — owner-run source-pinned sanitized render on NEW `ccpcadmin@ccpcerp-prod`**, during explicitly approved preparation-only scope; three pre-existing GitHub-verified Docker image tags and zero existing containers/volumes as last checked. Operator output:

```text
BEGIN_SANITIZED_COMPOSE_LAYOUT_CHECK
COMPOSE_PROJECT_OK
EXPECTED_TEN_SERVICES_AND_IMAGES_OK
FRONTEND_LOOPBACK_127.0.0.1_8080_OK
NO_OTHER_PUBLISHED_PORTS
DECLARED_VOLUMES_AND_MOUNTS_OK
NO_EXTERNAL_NETWORKS_OR_VOLUMES
SCHEDULER_AND_WORKERS_PRESENT_NOT_DISABLED
SANITIZED_COMPOSE_LAYOUT_CHECK_PASSED
```

The operator command rechecked all five source YAML Git blob hashes against pinned source at `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e`, then passed a synthetic `DB_PASSWORD`, explicit local image tags and `PULL_POLICY=never` through a sanitized `env -i docker compose ... config --format json | python3` pipeline. The Python parser did not print the complete Compose JSON or any environment-variable values. Source-only checks established the candidate project name `ccpc_prod_erpnext`, ten expected service definitions and expected tags, only one loopback frontend published port, pinned named volume/mount sets, no additional declared external Docker networks/volumes, and absence of privileged/network_mode/PID/devices/extra_hosts values. Opening terminal input echo had paste artifacts; the meaningful success markers all printed.

**Risk:** This is strictly a static *effective model* inspection, **not** verification of actual runtime network egress isolation. The services `scheduler`, `queue-short`, and `queue-long` are still present **and not disabled**; default Compose network is not declared `internal: true` in the pinned five-file model. Published loopback frontend does not prevent outbound traffic. Existing production image/site backup are not yet restored, and no new containers, volumes, networks, actual credentials, real data, or cutover were created by this test. Original OLD PRODUCTION/DEVELOPMENT are untouched.

**Next engineering step within already approved *preparation-only* scope:** Prepare a distinct private, **rehearsal-only scratch override**, layered *sixth*, never overwriting any of the five pinned GitHub files or checkouts. It must: (1) put the scratch default bridge network in `internal: true` state; (2) leave `frontend` not scheduled and replace its ports with `!override []`; (3) place `scheduler`, `queue-short`, and `queue-long` behind non-default Compose profiles; (4) avoid real secrets and network/backup operations, and (5) enforce fail-closed, no-deployment real parser checks on the resulting synthetic configuration before any separate write-capable rehearsal approval. Explicitly disallow `--profile`, `COMPOSE_PROFILES`, host networking, all port publication, and any additional external network. Since Compose profiles are opt-in and can be explicitly enabled, profiles alone are **not** a security boundary; the operator must later run a narrowly scoped allowlist of service names. A network declared `internal: true` is intended to isolate containers externally, but actual engine behavior/host routing must be independently checked before production-data restore.

**Approval gate unchanged:** Creating or starting any Docker networks, containers, volumes, restore, migrations, enabling jobs/email/integrations, applying real secrets, updating OLD PRODUCTION/DEV or cutover still requires explicit separate owner authorization. The four Nov 5 02:00 transferred files are rehearsal inputs, not verified final cutover backup.

## NEW FIVE-FILE SYNTHETIC DOCKER COMPOSE CONFIG PARSER PASSED — 2026-11-07

**PASS — owner-run on NEW `ccpcadmin@ccpcerp-prod`** after script reverified the exact GitHub blob hashes of all five scratch `source-only` YAML files, correct host/account, and private directory ownership/modes. Owner pasted:

```text
PINNED_SOURCE_REVERIFIED
BEGIN_SYNTHETIC_COMPOSE_CONFIG_CHECK
PINNED_COMPOSE_SYNTHETIC_CONFIG_OK
```

**Bounded test:** `env -i` with test-only `DB_PASSWORD=CCPC_SYNTHETIC_TEST_ONLY`, explicit `CUSTOM_IMAGE=ccpcerp`, `CUSTOM_TAG=v16.50.0`, `PULL_POLICY=never`, default legacy-lan publish inputs overridden by the last dedicated-pre-TLS YAML, and explicit `--project-name ccpc_prod_erpnext`; ran only `docker compose -f compose.yaml -f overrides/compose.mariadb.yaml -f overrides/compose.redis.yaml -f overrides/compose.lan-production.yaml -f overrides/compose.dedicated-pre-tls.yaml config --quiet` in protected scratch `/home/ccpcadmin/.ccpc-compose-review-c12d46f/source-only`. Exit success was confirmed by final script marker. Terminal input echo had harmless garbling, but the actual three success markers printed. No actual credential file was created, and no real production credentials used.

**Meaning:** Real Docker Compose parser accepted the pinned YAML layering with synthetic values. This does **not yet** verify service names, published ports, engine network isolation, volumes, scheduler disablement, runtime startup, host deployment wrapper, database restore or newer custom app release. The original `ccpcerp:v16.50.0` image remains separate from newer draft custom app PR #33. Current NEW Docker has no containers or volumes as of previous independent operator inventory; no mutation was performed by the parser command.

**Next preparation-only check:** Produce a **sanitized** effective Compose model inspection by piping `docker compose ... config --format json` directly to a Python parser running under a wiped environment with synthetic `DB_PASSWORD`; print only allowlisted service names, image tags, frontend host binding, named volumes, network declarations and queue/scheduler presence, **never the full JSON or all environment variables**. Guard source file hashes again and reject unexpected services, binding, host network, bind mounts, external networks, privileged services, docker socket or unknown mounts. On discrepancy, STOP and review without starting services. `scheduler` and queue workers remain defined and must be separately excluded/disabled and externally isolated before any rehearsal startup. Need a separate owner approval for any Compose runtime resources, restore or cutover.

## NEW FIVE-FILE COMPOSE SCRATCH SOURCE VERIFIED ON HOST — 2026-11-07

**PASS — owner-run local source assembly on NEW `ccpcadmin@ccpcerp-prod`** following the source-only, GitHub-blob-pinned procedure in the preceding checkpoint. Terminal report:

```text
SOURCE_FILE_VERIFIED compose.yaml
SOURCE_FILE_VERIFIED overrides/compose.mariadb.yaml
SOURCE_FILE_VERIFIED overrides/compose.redis.yaml
SOURCE_FILE_VERIFIED overrides/compose.lan-production.yaml
SOURCE_FILE_VERIFIED overrides/compose.dedicated-pre-tls.yaml
PINNED_FIVE_FILE_SOURCE_READY
```

The opening terminal echo was garbled, but all five per-file `git hash-object` matches and terminal success marker printed. Guarded script checked NEW host/user, prior checkout `/home/ccpcadmin/ccpc-pr29-review` exact commit `bd92ade7ac859b9f6b21b157bdc1629e93f4540c` and clean status, source YAML hashes, private scratch parent ownership/mode and nonexistent output before creating `/home/ccpcadmin/.ccpc-compose-review-c12d46f/source-only` and copying four unchanged files and writing fifth. This is **script-reported** exact source matching, not independent SSH access by ChatGPT.

**Five resulting GitHub blob pins:** `compose.yaml` `752b86e1ba4c1977a2636b1916f6015771f4c28c`, `compose.mariadb.yaml` `94e177c38707a40bdd2715287565c80e41c4f3d3`, `compose.redis.yaml` `64bc05ac2e955719822718e5118a62d0c9771e24`, `compose.lan-production.yaml` `3e65debe8d007b73d23f46f880cc53a182a19829`, `compose.dedicated-pre-tls.yaml` `14fd89a3c2371104f464964137483de9f4a35861`. All correspond to GitHub review commit `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e`.

**Next operation within owner's preparation-only approval:** On NEW, run **non-deploying** `docker compose ... config --quiet` for exactly these five YAML files in original order, selected project `ccpc_prod_erpnext`, and synthetic non-secret `DB_PASSWORD`, explicit `CUSTOM_IMAGE=ccpcerp` / `CUSTOM_TAG=v16.50.0` from a sanitized environment; re-verify five file hashes and server identity first. Do not create an actual `.env`, load any real secret, contact GitHub/NAS, use `compose up/run/start/pull`, or request Docker engine mutation. If quiet render succeeds, next separately inspect sanitized effective service/port/volume metadata without printing interpolated real credentials.

**Rehearsal boundaries unchanged:** No real Compose runtime/render has yet been observed, no service/container/network/volume has been started, and no site/db/attachment restore has been done. The November 5 02:00 backup is an archived rehearsal source only. Do not enable schedulers, workers, outbound mail/integrations, or do OLD PRODUCTION/DEVELOPMENT/cutover changes without separate approval.

## FIVE-FILE COMPOSE SOURCE CAN BE ASSEMBLED LOCALLY WITHOUT ZIP OR SSH — 2026-11-07

**User prefers no manual ZIP transfer and asked about NAS backup.** Clarification: the four November 5 database/site backup artifacts are already checksum-verified on NEW; the requested five-file Compose source set is a separate GitHub code artifact, not the NAS backup. Neither backup retransfer nor any NEW permanent GitHub SSH credentials are necessary for this source-only step.

**Verified GitHub blob equality:** NEW has clean (as of prior operator inspection) historical deployment checkout `/home/ccpcadmin/ccpc-pr29-review` at `security/dedicated-prod-external-env-2026-10-23` commit `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`. Current reviewed candidate branch `review/dedicated-host-readonly-inventory-2026-10-25` HEAD is `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e`. GitHub `fetch_file` proved **exact blob equality** for four Compose files across those two commits:
- `compose.yaml`: `752b86e1ba4c1977a2636b1916f6015771f4c28c`
- `overrides/compose.mariadb.yaml`: `94e177c38707a40bdd2715287565c80e41c4f3d3`
- `overrides/compose.redis.yaml`: `64bc05ac2e955719822718e5118a62d0c9771e24`
- `overrides/compose.lan-production.yaml`: `3e65debe8d007b73d23f46f880cc53a182a19829`
The fifth file differs: `overrides/compose.dedicated-pre-tls.yaml` on pinned review has Git blob `14fd89a3c2371104f464964137483de9f4a35861`, whereas older on-host branch has `9b69b0c7a1d64191a51da5126ddc82498202446f`.

**Faster safe source-only procedure proposed (not yet run):** On NEW guard hostname/user, protect existing `/home/ccpcadmin/.ccpc-compose-review-c12d46f` 0700 parent and existing checkout, check actual local old HEAD is `bd92ade...` and clean, `git hash-object` all four existing YAML files against their recorded reviewed blob IDs, copy exactly those four into a new private scratch subdirectory `source-only`, and create the sole differing pinned fifth YAML from directly reviewed source literal. Verify all five resulting `git hash-object` values exactly. No GitHub server authentication, ZIP, file transfer, NAS mount, secrets, containers, volumes, database restore, or production service start required. **It produces only the five pinned Compose YAML files, not a full reviewed Git checkout or validated deploy wrapper.** Stop on unexpected existing scratch content or any hash mismatch; do not overwrite user files or reset source worktrees. Then separately validate `docker compose config --quiet` using synthetic credentials and no service startup.

## PINNED FIVE-FILE COMPOSE SOURCE BUNDLE PREPARED OFF-HOST — 2026-11-07

**Confirmed read-only NEW host diagnostic:** Operator pasted `SCRATCH_DIRECTORY=ccpcadmin:700`, `SCRATCH_REPO_PATH_ABSENT`, `PINNED_COMMIT_NOT_LOCAL_IN=ccpc-frappe-deployment`, `PINNED_COMMIT_NOT_LOCAL_IN=ccpc-pr29-review`, `LOCAL_SOURCE_AVAILABILITY_CHECK_COMPLETE`. Neither existing NEW checkout has the pinned `c12d46f` commit, and the failed GitHub SSH clone left only the isolated private scratch parent. Do not modify or reset either historical checkout.

**Credential-free alternative prepared in the active ChatGPT conversation:** A source-only ZIP named `ccpc-compose-source-c12d46f-five-files.zip` was constructed from five *GitHub connector-fetched* Compose YAML files at exact deployment review commit `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e`. Each source byte sequence was locally checked against its GitHub Git-blob SHA:
- `compose.yaml`: `752b86e1ba4c1977a2636b1916f6015771f4c28c`
- `overrides/compose.mariadb.yaml`: `94e177c38707a40bdd2715287565c80e41c4f3d3`
- `overrides/compose.redis.yaml`: `64bc05ac2e955719822718e5118a62d0c9771e24`
- `overrides/compose.lan-production.yaml`: `3e65debe8d007b73d23f46f880cc53a182a19829`
- `overrides/compose.dedicated-pre-tls.yaml`: `14fd89a3c2371104f464964137483de9f4a35861`

Bundle also contains non-secret `SOURCE-MANIFEST.json` and `README.txt`; archive SHA-256: `55e7dd0a8777192ff3fa5e5af5254ce307b695d670f9dd4e9334bbb4e03fac45`; size `4238` bytes. ZIP entries were read back and SHA256-verified. **Source bundle is NOT a full Git checkout or deployable release; no runtime/source validation on NEW has occurred.** This ChatGPT artifact is transient and must not be presented as already installed on NEW or as GitHub authoritative source itself; exact GitHub commit and file hashes are authoritative.

**Next operator step, PREPARATION ONLY:** Download the small ZIP from the current chat and transfer it over the operator's already authorized secure administration/SFTP connection into the existing private NEW directory `/home/ccpcadmin/.ccpc-compose-review-c12d46f` (no root, no NEW GitHub SSH credential). Verify archive SHA and intended path on NEW before extraction; guard against archive traversal, symlinks or unexpected paths. This introduces only scratch YAML files and metadata; no `.env`, real passwords, container, volume, network or restore. Follow with a **separately reviewed synthetic-credential, no-deploying `docker compose config --quiet`** check using the exact five file layering, and sanitized port/mount inspection. Do not confuse this raw Compose parser test with the still-unvalidated dedicated wrapper guards, nor treat `config --quiet` as permission for `up`.

## NEW ISOLATED SCRATCH CLONE BLOCKED BY GITHUB SSH AUTH — 2026-11-07

**Owner-reported result:** The approved preparation-only attempt to shallow-clone pinned review branch `review/dedicated-host-readonly-inventory-2026-10-25` on NEW `ccpcadmin@ccpcerp-prod` ended with:

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
Please make sure you have the correct access rights
and the repository exists.
```

**Status:** GitHub SSH authentication **BLOCKED**. The GitHub connector independently confirms review branch exists and HEAD is `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e`. The attempted command created private scratch parent `/home/ccpcadmin/.ccpc-compose-review-c12d46f` with `0700` before invoking `git clone`; its precise remaining directory contents are **not verified**. There is **no verified successful clone**, Compose config render, new server credential, Docker operation, container, volume, DB restoration, or cutover. The source checkout and original production remain protected. Avoid rerunning the same clone, deleting scratch blindly, loosening SSH checking, or restoring previously revoked temporary SSH keys.

**Next safe owner-run read-only diagnostic on NEW:** Confirm the private scratch directory status and whether exact `c12d46f...` commit object is already present in one of the two earlier clean NEW host Git checkouts (`/home/ccpcadmin/ccpc-frappe-deployment` and `/home/ccpcadmin/ccpc-pr29-review`). No printing SSH private keys, `.env`, git remote URLs or sensitive data. If pinned object is present, plan a distinct scratch worktree without modifying those checkouts; if absent, use a verified connector-sourced offline transfer artifact or an explicitly scoped temporary access method (not a permanent host secret) for read-only Compose validation. **Do not restore or start services** under preparation-only approval.

## OWNER APPROVED RESTORE-REHEARSAL PREPARATION AND SOURCE REVIEW — 2026-11-07

**Owner said "Approved Continue" after the explicitly limited proposal of preparation/validation only**, following the verified NEW image inventory; this does not approve Docker container/volume creation, Compose `up`, service starts, database/file restore, migrations, credential provisioning, production cutover or changes to OLD PRODUCTION/DEVELOPMENT.

**Fresh GitHub review (2026-11-07) — verified immutable tips:**
- Dedicated Compose candidate `review/dedicated-host-readonly-inventory-2026-10-25` @ `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e`; **review-only**, not merged or deployed.
- App PR #33 `review/billing-authorization-correction-2026-11-03` @ `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc` still **OPEN / DRAFT**, not production accepted.
- Source code in candidate's `scripts/config.sh` still pins `CCPC_REF=release-2026-09-16` and `CCPC_SHA=cfcc19394a6646548f2b7050db040c8cf5ebafde`; `apps.json` still uses `release-2026-09-16`. This is **not** the newer business-feature candidate; do not silently change the existing original `ccpcerp:v16.50.0` Docker image to draft code.
- Five review Compose files (order): `compose.yaml`, `overrides/compose.mariadb.yaml`, `overrides/compose.redis.yaml`, `overrides/compose.lan-production.yaml`, `overrides/compose.dedicated-pre-tls.yaml`. Last uses YAML `!override` to set loopback-only `127.0.0.1:8080:8080/tcp` and requires `DB_PASSWORD`; source lists both `scheduler` and queue workers with potentially active behavior. **Do not run full stack for rehearsal without isolation.**
- Candidate's `scripts/modules/docker.sh` enforces dedicated env file ownership/modes, refuses ambient Compose selectors, requires default local Docker socket, and pins candidate Compose project `ccpc_prod_erpnext`. These are **source-only guard findings**; real Docker Compose parser/runtime behavior has not been validated.

**Next operator step within approved preparation only:** create an isolated user-private **scratch clone** on NEW `ccpcadmin@ccpcerp-prod` from the pinned GitHub review branch, with strict SSH host-key checking and exact HEAD assertion. The scratch clone must be separate from the two prior NEW checkouts and never execute deployment scripts, alter existing Git worktrees, print secrets, or start Docker containers. Git clone creates only a new lab directory; inspect exact output before a subsequent synthetic, no-services-started `docker compose config --quiet` check. If source authentication or commit check fails, STOP; do not weaken SSH validation. No real production credentials used. This is the fastest source-to-real-Compose-parser path without touching existing NEW production checkouts.

**Data boundary:** The independently copied November 5 02:00 four-artifact source remains rehearsal data, not final cutover. Full restore acceptance still pending; reconcile any later writes before live cutover. Preserve OLD source and NEW archives.

## NEW DOCKER POST-IMPORT READ-ONLY INVENTORY VERIFIED — 2026-11-07

**PASS — owner-run read-only verification on NEW `ccpcadmin@ccpcerp-prod`** after the guarded supporting-image import. Exact reported output:

```text
[ccpcerp:v16.50.0] sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8
[mariadb:11.8] sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4
[redis:8.6-alpine] sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763
NEW_DOCKER_IMAGES_PRESENT_NO_CONTAINERS_OR_VOLUMES
```

The guarded script verified NEW hostname and `ccpcadmin` account, inspected all three Docker tags and immutable image IDs, then confirmed `docker ps -aq` and `docker volume ls -q` were empty. **All three tags match the pinned exact OLD PRODUCTION image IDs; no Docker containers or volumes exist on NEW at the time of this check.** This is an operator-reported read-only observation, not live remote access by ChatGPT. No Docker image re-import required. Source archive, app image, supporting images, and November 5 transferred four-part backup are preserved.

**Checkpoint / next gate:** Image preparation and verification complete. Next prepare a deliberately isolated, no-external-effects NEW-host restoration *rehearsal plan*, with read-only inspection of existing Compose/config/backup inputs and review of rollback, hostname/ports, network, secrets, background schedulers, email/integrations, database volumes, schema, and four backup artifacts. The 2026-11-05 02:00 backup is a rehearsal input and **not a verified current cutover point**; reconcile writes after that cutoff before any live switch. **No new container/volume/network creation, Compose up, site/database/file restore, scheduler activation, migration, DNS/routing change, or OLD PRODUCTION/DEVELOPMENT action is authorized** by this inventory or prior image-import approval. Seek a separately bounded approval for write-capable rehearsal after the review.

## NEW SUPPORTING DOCKER IMAGES IMPORTED AND IDS VERIFIED — 2026-11-07

**PASS — owner-run execution completed** on NEW `ccpcadmin@ccpcerp-prod`. The operator pasted the guarded command's preflight and completion markers:

```text
SUPPORT_IMAGES_ARCHIVE_AND_DOCKER_PREFLIGHT_OK
BEGIN_APPROVED_NEW_SUPPORT_IMAGES_DOCKER_LOAD
Loaded image: mariadb:11.8
Loaded image: redis:8.6-alpine
MARIADB_IMAGE_ID=sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4
REDIS_IMAGE_ID=sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763
NEW_SUPPORT_IMAGES_IMPORTED_AND_IDS_VERIFIED
```

**Interpretation:** Script-reported exact source SHA-256, expected two manifest tags, owner/mode/size, NEW host/user, original application image ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`, absent conflicting tags, and no preexisting Docker containers or volumes passed the preflight. The two newly imported immutable Docker image IDs exactly match the pinned originals from OLD PRODUCTION. The opening terminal paste echo was partially garbled; the clean execution output includes all expected completion markers. **Do not rerun image load** now that target tags exist.

**Boundary:** This establishes the successful owner-reported Docker image import, not an independent post-import Docker inventory; no NEW container or volume creation, Compose execution, database/file restoration, Frappe migration, traffic cutover, or change to OLD PRODUCTION/DEVELOPMENT was approved or reported. Preserve staging archives and verified November 5 backup files. Existing application, database, and Redis image tags are available for later separately approved rehearsal.

**Next safe step:** On NEW only, conduct an owner-run **read-only** post-import Docker inventory: inspect all three tagged image IDs and confirm there are still no containers or Docker volumes. Review output and document results before requesting any distinct rehearsal/container/restore authorization. The November 5 02:00 backup remains a *rehearsal input*, not an established final cutover backup; preserve OLD PRODUCTION until separately authorized cutover and validation.

## OWNER APPROVED NEW DOCKER LOAD OF EXACT SUPPORTING IMAGES — 2026-11-07

**Owner explicitly replied "aPPROVED"** to a separately scoped NEW-host-only Docker load of the already transferred and independently verified two-image archive. Approval covers only importing `mariadb:11.8` and `redis:8.6-alpine` into NEW `ccpcadmin@ccpcerp-prod` Docker image storage and comparing their resulting immutable IDs to those of OLD running PRODUCTION. It does **not** authorize containers/volumes creation, service start, Compose changes, DB restore, migrations, network/traffic cutover, OLD PROD/DEV changes or any backup cleanup.

**Source/archive:** NEW protected stage `/home/ccpcadmin/.ccpc-support-images-transfer-20261106` (`ccpcadmin:700`); `mariadb-11.8_redis-8.6-alpine.tar` (`ccpcadmin:600`, **145522176** bytes, SHA-256 `e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`). The previously approved transfer SSH key was revoked and retired on both servers, verified by OLD key retirement and NEW authorization count zero. Existing `ccpcerp:v16.50.0` already loaded with ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`. NEW database and Redis tags absent as of last NEW preflight.

**Exact expected NEW imported image IDs:**
- `mariadb:11.8`: `sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4`.
- `redis:8.6-alpine`: `sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763`.

**ONE owner-run bounded command on NEW** checks identity, archive metadata/hash, manifest tags, existing app image ID, absent target tags, absent containers/volumes; loads only exact tar, then inspects imported IDs. Stop on failures, do not retry blindly or remove files. `set -euo pipefail` confined to child Bash.

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != 'ccpcerp-prod' ] ||
   [ "$(id -un)" != 'ccpcadmin' ]; then
  echo 'STOP: wrong NEW host or account'
  exit 1
fi

stage="$HOME/.ccpc-support-images-transfer-20261106"
archive="$stage/mariadb-11.8_redis-8.6-alpine.tar"
expected_sha='e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08'
app_expected='sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8'
db_expected='sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4'
redis_expected='sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763'

if [ -L "$stage" ] || [ ! -d "$stage" ] ||
   [ "$(stat -c '%U:%a' "$stage")" != 'ccpcadmin:700' ] ||
   [ -L "$archive" ] || [ ! -f "$archive" ] ||
   [ "$(stat -c '%U:%a:%s' "$archive")" != 'ccpcadmin:600:145522176' ]; then
  echo 'STOP: archive type, owner, mode or size mismatch'
  exit 1
fi

if [ "$(sha256sum "$archive" | awk '{print $1}')" != "$expected_sha" ]; then
  echo 'STOP: archive checksum mismatch'
  exit 1
fi

if ! tar -xOf "$archive" manifest.json |
  python3 -c 'import json,sys; m=json.load(sys.stdin); tags=sorted(t for item in m for t in item.get("RepoTags",[])); sys.exit(0 if tags==["mariadb:11.8","redis:8.6-alpine"] else 1)'; then
  echo 'STOP: source archive contains unexpected image tags'
  exit 1
fi

sudo -v

if [ "$(sudo -n docker image inspect --format '{{.Id}}' ccpcerp:v16.50.0)" != "$app_expected" ]; then
  echo 'STOP: existing ERPNext application image ID mismatch'
  exit 1
fi

for tag in mariadb:11.8 redis:8.6-alpine; do
  if sudo -n docker image inspect "$tag" >/dev/null 2>&1; then
    echo "STOP: target image tag already exists: $tag"
    exit 1
  fi
done

if [ -n "$(sudo -n docker ps -aq)" ] ||
   [ -n "$(sudo -n docker volume ls -q)" ]; then
  echo 'STOP: unexpected existing NEW Docker containers or volumes'
  exit 1
fi

echo 'SUPPORT_IMAGES_ARCHIVE_AND_DOCKER_PREFLIGHT_OK'
echo 'BEGIN_APPROVED_NEW_SUPPORT_IMAGES_DOCKER_LOAD'
sudo -n docker image load --input "$archive"

db_actual="$(sudo -n docker image inspect --format '{{.Id}}' mariadb:11.8)"
redis_actual="$(sudo -n docker image inspect --format '{{.Id}}' redis:8.6-alpine)"
app_actual="$(sudo -n docker image inspect --format '{{.Id}}' ccpcerp:v16.50.0)"

if [ "$db_actual" != "$db_expected" ] ||
   [ "$redis_actual" != "$redis_expected" ] ||
   [ "$app_actual" != "$app_expected" ]; then
  echo 'STOP: imported Docker image IDs or existing app image mismatch'
  printf 'DB_ID=%s\nREDIS_ID=%s\nAPP_ID=%s\n' "$db_actual" "$redis_actual" "$app_actual"
  exit 1
fi

printf 'MARIADB_IMAGE_ID=%s\nREDIS_IMAGE_ID=%s\n' "$db_actual" "$redis_actual"
echo 'NEW_SUPPORT_IMAGES_IMPORTED_AND_IDS_VERIFIED'
EOF
```

**Expected success markers:** `SUPPORT_IMAGES_ARCHIVE_AND_DOCKER_PREFLIGHT_OK`, `BEGIN_APPROVED_NEW_SUPPORT_IMAGES_DOCKER_LOAD`, `NEW_SUPPORT_IMAGES_IMPORTED_AND_IDS_VERIFIED`, plus exact two image IDs. If wrong host/ownership/hash/tags/conflicting images/containers/volumes, STOP without load. If a load fails or imported image ID differs, preserve status for inspection; do not automatically repeat. After output verify in GitHub; next step is NEW read-only image/container/volume check, then assess separate rehearsal planning approval. **No containers or database restore authorized by this action.**

## SUPPORTING-IMAGES TEMPORARY SSH KEY RETIRED ON OLD — 2026-11-07

**Owner executed the previously approved guarded deletion of exactly the dedicated support-image transfer SSH private/public key pair on OLD `gani@ccpcerpserver`**. The owner pasted:

```text
SUPPORT_IMAGE_OLD_TEMP_SSH_KEY_PAIR_RETIRED
SUPPORT_IMAGE_OTHER_SSH_KEYS_UNTOUCHED
```

**PASS — temporary supporting-image transfer credential lifecycle complete.** Previous independent NEW-host inspection returned `SUPPORT_IMAGE_TEMP_SSH_KEY_ENTRIES=0` for `ccpc-support-images-transfer-20261106`; the OLD temporary pair `/home/gani/.ssh/id_ed25519_ccpc_support_images_transfer_20261106` and `.pub` was validated against expected fingerprint `SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA` and the guard script reported deletion. The existing scheduled backup key `~/.ssh/id_ed25519_ccpc_backup` and unrelated SSH keys were not targeted.

**Current NEW pre-restore assets:**
- Original exact PRODUCTION application Docker image `ccpcerp:v16.50.0` already imported on NEW, immutable image ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`.
- Four November 5 2026 02:00 selected backup files from OLD NAS independently checked and stored privately at `/home/ccpcadmin/.ccpc-nov05-backup-transfer-20261106/`. These are **rehearsal inputs**, not yet proven final cutover backup; user has not explicitly confirmed Nov 5 post-02:00 application writes.
- Exact MariaDB/Redis images tar privately staged and independently validated at `/home/ccpcadmin/.ccpc-support-images-transfer-20261106/mariadb-11.8_redis-8.6-alpine.tar`, **145522176 bytes**, SHA-256 `e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`.
- The corresponding source archive at `/var/tmp/ccpc-prod-support-images.HlHFN8R6/mariadb-11.8_redis-8.6-alpine.tar` is retained on OLD; original ERPNext image archive and old PROD/DEV remain preserved.
- Supporting-image tags `mariadb:11.8` and `redis:8.6-alpine` **not loaded on NEW**, as of last verified NEW preflight; no NEW ERPNext containers, volumes, database restoration, networking cutover, or service start has been authorized.

**NEXT OWNER APPROVAL GATE — REQUEST, NOT YET AUTHORIZED:** On NEW `ccpcadmin@ccpcerp-prod` only, run `docker image load -i /home/ccpcadmin/.ccpc-support-images-transfer-20261106/mariadb-11.8_redis-8.6-alpine.tar` after independently rechecking staging ownership/modes and exact SHA-256. Then inspect the imported image IDs and ensure MariaDB `mariadb:11.8` is exactly `sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4` and Redis `redis:8.6-alpine` exactly `sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763`. Check any existing image tag ID before import to avoid overwriting unexpected NEW tags. The request excludes container creation/startup, Compose changes, mounting backup files, DB restore, migrations, production updates, network changes, and traffic cutover. Obtain **explicit separate user approval** before performing any Docker load. Do not authorize or imply database restoration or final migration completion.

## SUPPORTING-IMAGE TRANSFER SSH AUTHORIZATION INDEPENDENTLY ABSENT — 2026-11-07

**Owner-run read-only independent verification on NEW `ccpcadmin@ccpcerp-prod`** after guarded removal of the single temporary supporting-image transfer public key from `~/.ssh/authorized_keys` returned:

```text
SUPPORT_IMAGE_TEMP_SSH_KEY_ENTRIES=0
```

**PASS:** The marker `ccpc-support-images-transfer-20261106` has **zero** remaining entries in the NEW `ccpcadmin` authorized-keys file. This verifies the specific temporary authorization was removed; it is not a separate active-authentication test. Existing SSH authorizations were preserved by previous guarded atomic removal. NEW archive remains independently verified at `/home/ccpcadmin/.ccpc-support-images-transfer-20261106/mariadb-11.8_redis-8.6-alpine.tar`, exact size **145522176** and SHA-256 **`e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`**. Keep archive/staging/receiver intact pending separately approved future action. OLD source archive remains `/var/tmp/ccpc-prod-support-images.HlHFN8R6/mariadb-11.8_redis-8.6-alpine.tar`.

**NEXT previously owner-approved cleanup on OLD `gani@ccpcerpserver`:** retire **only** the dedicated temporary support-image SSH key pair `/home/gani/.ssh/id_ed25519_ccpc_support_images_transfer_20261106` and `.pub`, after guarded verification of host/user, no symlinks, owner/modes, expected public key fingerprint `SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA`, and private/public key pair consistency. Do not touch scheduled backup key `~/.ssh/id_ed25519_ccpc_backup`, any previous transfer keys, production data, or source/NEW archives.

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != 'ccpcerpserver' ] ||
   [ "$(id -un)" != 'gani' ]; then
  echo 'STOP: wrong OLD host or user'; exit 1
fi

key="$HOME/.ssh/id_ed25519_ccpc_support_images_transfer_20261106"
pub="$key.pub"
expected_fp='SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA'
expected_comment='ccpc-support-images-transfer-20261106'

for file in "$key" "$pub"; do
  if [ ! -f "$file" ] || [ -L "$file" ] ||
     [ "$(stat -c '%U' "$file")" != 'gani' ]; then
    echo "STOP: missing or unexpected temporary key file: $file"; exit 1
  fi
done

if [ "$(stat -c '%a' "$key")" != '600' ] ||
   [ "$(stat -c '%a' "$pub")" != '644' ]; then
  echo 'STOP: unexpected temporary key permissions'; exit 1
fi

pub_fp="$(ssh-keygen -lf "$pub" | awk '{print $2}')"
private_fp="$(ssh-keygen -lf "$key" | awk '{print $2}')"
pub_comment="$(awk '{print $3}' "$pub")"
if [ "$pub_fp" != "$expected_fp" ] ||
   [ "$private_fp" != "$expected_fp" ] ||
   [ "$pub_comment" != "$expected_comment" ]; then
  echo 'STOP: temporary key identity mismatch'; exit 1
fi

private_public="$(ssh-keygen -y -f "$key" | awk '{print $1,$2}')"
recorded_public="$(awk '{print $1,$2}' "$pub")"
if [ "$private_public" != "$recorded_public" ]; then
  echo 'STOP: temporary private/public key mismatch'; exit 1
fi

rm -- "$key" "$pub"

if [ -e "$key" ] || [ -L "$key" ] ||
   [ -e "$pub" ] || [ -L "$pub" ]; then
  echo 'STOP: temporary key file still present'; exit 1
fi

echo 'SUPPORT_IMAGE_OLD_TEMP_SSH_KEY_PAIR_RETIRED'
echo 'SUPPORT_IMAGE_OTHER_SSH_KEYS_UNTOUCHED'
EOF
```

Expected exact two success markers. This command affects **only** those two temporary OLD files, with no sudo, no Docker commands, no SSH connection, no source/NEW archive deletion, no PRODUCTION/DEVELOPMENT changes. On any STOP/error, do not blindly rerun. After output confirms cleanup, record final SSH retirement and request separate explicit approval before loading exact MariaDB/Redis images into NEW Docker. Preserve all existing backup files and verify loaded image IDs, if later approved, against pinned OLD MariaDB `sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4`, Redis `sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763`. **No Docker image load authorized yet.**

## SUPPORTING-IMAGE TRANSFER TEMPORARY SSH REVOCATION REPORTED — 2026-11-07

**Owner executed the previously approved guarded exact-line revocation on NEW `ccpcadmin@ccpcerp-prod`** after independent verification of the transferred MariaDB/Redis image archive. Terminal-paste echo was visibly garbled before all three success markers:

```text
SUPPORT_IMAGE_TEMP_SSH_AUTH_REVOKED
OTHER_AUTHORIZED_KEYS_PRESERVED
VERIFIED_SUPPORT_IMAGE_ARCHIVE_RETAINED
```

**Status:** Script-reported removal of precisely one `ccpc-support-images-transfer-20261106` temporary public-key authorization from NEW `~/.ssh/authorized_keys` with atomic replacement, byte-for-byte preservation of all other lines, and retention of verified root-origin archive (NEW `/home/ccpcadmin/.ccpc-support-images-transfer-20261106/mariadb-11.8_redis-8.6-alpine.tar`, 145522176 bytes, SHA-256 `e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`). Because of garbled echo and to independently verify removal, a **separate read-only marker count** is required before retiring the OLD temporary private key. No supporting images have yet been loaded into NEW Docker, no containers started or DB restore/cutover authorized.

**NEXT read-only operator step on NEW `ccpcadmin@ccpcerp-prod`:**

```bash
if [ "$(hostnamectl --static)" != 'ccpcerp-prod' ] ||
   [ "$(id -un)" != 'ccpcadmin' ]; then
  echo 'STOP: wrong server or user'
elif [ ! -f "$HOME/.ssh/authorized_keys" ]; then
  echo 'STOP: authorized_keys missing'
else
  count="$(grep -Fc 'ccpc-support-images-transfer-20261106' "$HOME/.ssh/authorized_keys" || true)"
  printf 'SUPPORT_IMAGE_TEMP_SSH_KEY_ENTRIES=%s\n' "$count"
fi
```

**Expected:** `SUPPORT_IMAGE_TEMP_SSH_KEY_ENTRIES=0`. If STOP or nonzero, investigate only; do not delete OLD private key or touch the backup key. If zero, then specifically authorized OLD temporary key retirement follows with fingerprint check `SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA`. Preserve all archives, existing credentials, running OLD PROD+DEV and NEW imported application image. A subsequent NEW Docker load of MariaDB/Redis images requires **separate explicit owner approval**.

## SUPPORTING-IMAGES ARCHIVE INDEPENDENTLY VERIFIED ON NEW — 2026-11-07

**Owner-run independent local read-only verification on NEW `ccpcadmin@ccpcerp-prod`**, following the encrypted OLD-to-NEW transfer of the root-private supporting-image archive, returned:

```text
SUPPORT_IMAGE_DESTINATION_METADATA_OK
SUPPORT_IMAGE_DESTINATION_SHA256_OK
SUPPORT_IMAGE_ARCHIVE_INDEPENDENTLY_VERIFIED
```

**PASS:** NEW archive `/home/ccpcadmin/.ccpc-support-images-transfer-20261106/mariadb-11.8_redis-8.6-alpine.tar` has expected private `0700` staging and `0600` file modes, owner `ccpcadmin`, exact **145522176** bytes, and independent SHA-256 match **`e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`**. The OLD archive remains preserved, as do all four previously independently verified November 5 database/site backup files and exact ERPNext app image. **MariaDB and Redis supporting images are NOT YET loaded into NEW Docker**. No new containers, database restore, or cutover have occurred.

**NEXT previously expressly approved security step on NEW only:** Remove exactly the one temporary support-image public key line from the NEW `ccpcadmin` account's `~/.ssh/authorized_keys`, preserving all other lines and verified archive intact. Temporary key marker `ccpc-support-images-transfer-20261106`, public key text `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDcONU7BtDoctg4uLbro/flvs3FLdOgxLCr5+G931X3z ccpc-support-images-transfer-20261106`, OLD source restriction `from="192.168.50.166",restrict`, forced command path `/home/ccpcadmin/.ccpc-support-images-transfer-20261106/receive-support-images.sh`. Guard host/user, existing file types/owner/modes, archive presence, exact one authorization; use atomic temp file replacement and no deletion of archive or staging. Stop and investigate on any unexpected state, do not rerun blindly. Following successful marker, independently confirm marker count zero, then retire the exact OLD temporary support-transfer SSH key pair after matching fingerprint `SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA`.

**Verified original supporting-image IDs** for eventual separately approved NEW Docker import: MariaDB `sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4`; Redis `sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763`. **Do not load** without separate authorization. New containers/restore/cutover still outside scope.

## SUPPORTING-IMAGES ARCHIVE RECEIVER TRANSFER PASSED — 2026-11-06

**Owner executed the approved OLD-to-NEW encrypted supporting-images archive transfer** from `gani@ccpcerpserver` to the forced `receive-support-images` receiver on `ccpcadmin@ccpcerp-prod`, after the restricted SSH probe passed. Reported output:

```text
[sudo: authenticate] Password:
BEGIN_APPROVED_SUPPORT_IMAGES_TRANSFER
SUPPORT_IMAGE_ARCHIVE_SHA256_OK
SUPPORT_IMAGES_TRANSFER_SOURCE_AND_RECEIVER_CHECKS_OK
```

**PASS — source and receiver in-band verification:** The guarded OLD-host source command verified the source archive's owner-only metadata, exact size **145522176** and SHA-256 **`e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`**, and pinned NEW server ED25519 host identity before streaming. The NEW forced-command receiver verified the received archive against the same exact byte count and digest, then finalized it in its protected stage. Original OLD root-private archive remains `/var/tmp/ccpc-prod-support-images.HlHFN8R6/mariadb-11.8_redis-8.6-alpine.tar`. **Separate read-only independent NEW-host filesystem verification still pending**. Temporary SSH key and restricted NEW authorized-keys entry remain active until independent verification; do not delete or retransfer.

**NEXT one read-only operator step on NEW `ccpcadmin@ccpcerp-prod`:**

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != 'ccpcerp-prod' ] ||
   [ "$(id -un)" != 'ccpcadmin' ]; then
  echo 'STOP: wrong destination host or account'; exit 1
fi

stage="$HOME/.ccpc-support-images-transfer-20261106"
archive="$stage/mariadb-11.8_redis-8.6-alpine.tar"
expected='e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08'

if [ -L "$stage" ] || [ ! -d "$stage" ] ||
   [ "$(stat -c '%U:%a' "$stage")" != 'ccpcadmin:700' ]; then
  echo 'STOP: destination stage metadata mismatch'; exit 1
fi

if [ -L "$archive" ] || [ ! -f "$archive" ] ||
   [ "$(stat -c '%U:%a:%s' "$archive")" != 'ccpcadmin:600:145522176' ]; then
  echo 'STOP: destination archive metadata mismatch'; exit 1
fi

actual="$(sha256sum "$archive" | awk '{print $1}')"
if [ "$actual" != "$expected" ]; then
  echo 'STOP: independent destination SHA-256 mismatch'; exit 1
fi

echo 'SUPPORT_IMAGE_DESTINATION_METADATA_OK'
echo 'SUPPORT_IMAGE_DESTINATION_SHA256_OK'
echo 'SUPPORT_IMAGE_ARCHIVE_INDEPENDENTLY_VERIFIED'
EOF
```

Expected exactly the three indicated success markers. No archive contents, secrets, DB records or `authorized_keys` entries are printed. Stop on any error; preserve partial/complete file for investigation. After verification, revoke exactly the dedicated `ccpc-support-images-transfer-20261106` SSH authorized key on NEW and independently count marker occurrences, then retire only that temporary OLD key pair (previously explicitly approved). Do not touch the existing `id_ed25519_ccpc_backup` key. **Not authorized:** NEW Docker import of supporting images, container startup, ERPNext restore, schema migrations, OLD PROD/DEV changes or cutover. Those require separate owner approval. Pinned source image IDs MariaDB `sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4` and Redis `sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763` must be checked *after any separately approved Docker load*.

## SUPPORTING-IMAGES RECEIVER SSH PROBE PASSED — 2026-11-06

**Owner-run from OLD `gani@ccpcerpserver` using temporary dedicated key and independently matched NEW ED25519 SSH server fingerprint**, after the restricted NEW receiver was installed. Actual output:

```text
SUPPORT_IMAGE_TRANSFER_SSH_AUTH_OK
SUPPORT_IMAGE_TRANSFER_SSH_PROBE_PASS
```

**PASS:** The NEW receiver accepts the restricted `probe` request from OLD `192.168.50.166`; one-off transfer credentials are working. No image archive contents transferred yet; NEW MariaDB and Redis image load is *not authorized*. Existing OLD PROD/DEV and NEW Docker runtimes untouched.

**NEXT single already-approved action:** Stream **only** the root-private existing OLD Docker image archive `/var/tmp/ccpc-prod-support-images.HlHFN8R6/mariadb-11.8_redis-8.6-alpine.tar`, exactly 145522176 bytes and SHA-256 `e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`, over SSH to the NEW forced `receive-support-images` command. Revalidate OLD hostname and `gani` user, source archive root owner, `0700` stage, `0600` archive, exact byte count and digest; validate temporary user key and pinned NEW ED25519 fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`; never expose private key or change old scheduled-backup key. Keep `sudo -v` outside the transfer pipeline to avoid prompt output mixing with binary data; `sudo -n cat` streams the root-private tar as bytes. `pipefail` must remain inside a child shell to protect the operator's interactive terminal.

```bash
bash <<'EOF'
set -euo pipefail
umask 077

if [ "$(hostnamectl --static)" != "ccpcerpserver" ] ||
   [ "$(id -un)" != "gani" ]; then
  echo 'STOP: wrong source host or account'; exit 1
fi

stage='/var/tmp/ccpc-prod-support-images.HlHFN8R6'
archive="$stage/mariadb-11.8_redis-8.6-alpine.tar"
key="$HOME/.ssh/id_ed25519_ccpc_support_images_transfer_20261106"
expected_key_fp='SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA'
expected_host_fp='SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c'
expected_sha='e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08'

if [ ! -f "$key" ] || [ -L "$key" ] ||
   [ ! -f "$key.pub" ] || [ -L "$key.pub" ] ||
   [ "$(stat -c '%U:%a' "$key")" != 'gani:600' ] ||
   [ "$(ssh-keygen -lf "$key.pub" | awk '{print $2}')" != "$expected_key_fp" ]; then
  echo 'STOP: temporary transfer identity invalid'; exit 1
fi

sudo -v
if sudo -n test -L "$stage" || sudo -n test -L "$archive"; then
  echo 'STOP: source path is a symbolic link'; exit 1
fi
if [ "$(sudo -n stat -c '%U:%a' "$stage")" != 'root:700' ] ||
   [ "$(sudo -n stat -c '%U:%a:%s' "$archive")" != 'root:600:145522176' ]; then
  echo 'STOP: source archive ownership, permissions or size changed'; exit 1
fi

actual_sha="$(sudo -n sha256sum "$archive" | awk '{print $1}')"
if [ "$actual_sha" != "$expected_sha" ]; then
  echo 'STOP: source archive SHA-256 mismatch'; exit 1
fi

scanned="$(ssh-keyscan -T 5 -t ed25519 192.168.50.186 2>/dev/null)"
actual_host_fp="$(printf '%s\n' "$scanned" | ssh-keygen -lf - | awk '{print $2}')"
if [ "$actual_host_fp" != "$expected_host_fp" ]; then
  echo 'STOP: destination SSH host fingerprint mismatch'; exit 1
fi

kh="$(mktemp)"
trap 'rm -f -- "$kh"' EXIT
chmod 600 "$kh"
printf '%s\n' "$scanned" > "$kh"

echo 'BEGIN_APPROVED_SUPPORT_IMAGES_TRANSFER'
if response="$(sudo -n cat -- "$archive" | ssh -T -i "$key" \
  -o IdentitiesOnly=yes -o BatchMode=yes \
  -o PreferredAuthentications=publickey -o PasswordAuthentication=no \
  -o KbdInteractiveAuthentication=no -o StrictHostKeyChecking=yes \
  -o HostKeyAlgorithms=ssh-ed25519 -o UserKnownHostsFile="$kh" \
  -o ConnectTimeout=8 -o ServerAliveInterval=15 -o ServerAliveCountMax=4 \
  ccpcadmin@192.168.50.186 receive-support-images)"; then
  if [ "$response" != 'SUPPORT_IMAGE_ARCHIVE_SHA256_OK' ]; then
    echo 'STOP: unexpected receiver confirmation; do not retry'; exit 1
  fi
  echo "$response"
  echo 'SUPPORT_IMAGES_TRANSFER_SOURCE_AND_RECEIVER_CHECKS_OK'
else
  echo 'STOP: encrypted transfer failed; do not retry blindly'; exit 1
fi
EOF
```

**Expected success:** `BEGIN_APPROVED_SUPPORT_IMAGES_TRANSFER`, `SUPPORT_IMAGE_ARCHIVE_SHA256_OK`, then `SUPPORT_IMAGES_TRANSFER_SOURCE_AND_RECEIVER_CHECKS_OK`. Any error means STOP; do not retry or clear a `.partial` because receiver intentionally refuses overwrite. After successful transfer, independently verify NEW file size, owner-only permissions and SHA-256 at `/home/ccpcadmin/.ccpc-support-images-transfer-20261106/mariadb-11.8_redis-8.6-alpine.tar`. Then, and only then, revoke NEW temporary public authorization and remove OLD temporary private/public key pair as expressly approved. **Do not invoke `docker load` or create containers without separate consent.**

## SUPPORTING-IMAGES TRANSFER RECEIVER SETUP REPORTED — 2026-11-06

**Owner-run NEW `ccpcadmin@ccpcerp-prod` temporary receive-only SSH receiver setup** for exact `mariadb:11.8` and `redis:8.6-alpine` Docker archive. Operator's command paste showed garbled echo fragments before the two expected success markers:

```text
SUPPORT_IMAGE_RECEIVER_STAGING_READY
SUPPORT_IMAGE_TEMP_TRANSFER_KEY_AUTHORIZED
```

**Status:** Setup script reported that it created owner-only `~/.ccpc-support-images-transfer-20261106` protected staging, the forced-command receiver `receive-support-images.sh`, and appended the public key restricted to OLD source IP `192.168.50.166` with SSH `restrict` options. This remains **reported, not independently authenticated**, until a probe succeeds. No supporting archive bytes have been transferred and no Docker images were loaded on NEW. Existing PROD and DEV have not been changed.

**NEXT one source-side read-only SSH probe**, on OLD `gani@ccpcerpserver`, with key `/home/gani/.ssh/id_ed25519_ccpc_support_images_transfer_20261106` (ED25519 public fingerprint `SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA`), NEW `192.168.50.186` server pinned ED25519 SSH fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`. Do not invoke `receive-support-images` yet.

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != "ccpcerpserver" ] ||
   [ "$(id -un)" != "gani" ]; then
  echo 'STOP: wrong OLD host or account'; exit 1
fi

key="$HOME/.ssh/id_ed25519_ccpc_support_images_transfer_20261106"
pub="$key.pub"
expected_key_fp='SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA'
expected_host_fp='SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c'

if [ ! -f "$key" ] || [ -L "$key" ] ||
   [ ! -f "$pub" ] || [ -L "$pub" ] ||
   [ "$(stat -c '%U:%a' "$key")" != 'gani:600' ]; then
  echo 'STOP: temporary transfer key invalid'; exit 1
fi

key_fp="$(ssh-keygen -lf "$pub" | awk '{print $2}')"
if [ "$key_fp" != "$expected_key_fp" ]; then
  echo 'STOP: transfer key fingerprint mismatch'; exit 1
fi

scanned="$(ssh-keyscan -T 5 -t ed25519 192.168.50.186 2>/dev/null)"
host_fp="$(printf '%s\n' "$scanned" | ssh-keygen -lf - | awk '{print $2}')"
if [ "$host_fp" != "$expected_host_fp" ]; then
  echo 'STOP: NEW SSH server fingerprint mismatch'; exit 1
fi

kh="$(mktemp)"
trap 'rm -f -- "$kh"' EXIT
chmod 600 "$kh"
printf '%s\n' "$scanned" > "$kh"

if ssh -T -i "$key" \
  -o IdentitiesOnly=yes \
  -o BatchMode=yes \
  -o PreferredAuthentications=publickey \
  -o PasswordAuthentication=no \
  -o KbdInteractiveAuthentication=no \
  -o StrictHostKeyChecking=yes \
  -o HostKeyAlgorithms=ssh-ed25519 \
  -o UserKnownHostsFile="$kh" \
  -o ConnectTimeout=8 \
  ccpcadmin@192.168.50.186 probe; then
  echo 'SUPPORT_IMAGE_TRANSFER_SSH_PROBE_PASS'
else
  echo 'STOP: SUPPORT_IMAGE_TRANSFER_SSH_PROBE_FAILED'
  exit 1
fi
EOF
```

Expected:
```text
SUPPORT_IMAGE_TRANSFER_SSH_AUTH_OK
SUPPORT_IMAGE_TRANSFER_SSH_PROBE_PASS
```

**Stop on any other output.** The command only contacts the restricted receiver with `probe` and creates/deletes a temporary client known_hosts pin; it does not transfer or change image/archive contents, Docker, database, or containers. `set -euo pipefail` is in a child Bash, avoiding interactive-shell closure. Following a PASS, the next separately bounded operation is the already-approved encrypted transfer of OLD root-owned archive `/var/tmp/ccpc-prod-support-images.HlHFN8R6/mariadb-11.8_redis-8.6-alpine.tar`, exactly **145522176** bytes SHA-256 `e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`. On NEW, independently verify checksum, then revoke temporary SSH authorization and remove the OLD temporary key. No Docker import/load or restore/cutover without separate owner approval.

## SUPPORT IMAGE TRANSFER PUBLIC KEY INDEPENDENTLY CHECKED — 2026-11-06

**Owner executed the guarded OLD-host public-key-only read** after temporary key creation and supplied:

```text
SUPPORT_TRANSFER_PUBLIC_KEY_VERIFIED
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDcONU7BtDoctg4uLbro/flvs3FLdOgxLCr5+G931X3z ccpc-support-images-transfer-20261106
```

**PASS — verified public key**, fingerprint `SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA`. Private key must remain on OLD `gani@ccpcerpserver`, never printed or committed. No supporting archive transferred yet.

**NEXT: already approved NEW-host restricted SSH receiver setup**, only on `ccpcadmin@ccpcerp-prod`: ensure correct host/account; public fingerprint; existing `~/.ssh/authorized_keys` owner-only `0600`, SSH directory `0700`, no existing new staging/marker; create `/home/ccpcadmin/.ccpc-support-images-transfer-20261106` as `0700`, guarded `receive-support-images.sh` forced command executable by user, and authorize exactly the verified public key once with `from="192.168.50.166",restrict,command="/home/ccpcadmin/.ccpc-support-images-transfer-20261106/receive-support-images.sh"`. Script allows **only** `probe` (echo `SUPPORT_IMAGE_TRANSFER_SSH_AUTH_OK`) and `receive-support-images`; latter accepts exactly `145522176` bytes, SHA-256 `e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`, deposits private `0600` `mariadb-11.8_redis-8.6-alpine.tar`, and refuses existing destination/partial files. Use an extra-byte cap while reading stdin, no-overwrite hard-link finalize, and print `SUPPORT_IMAGE_ARCHIVE_SHA256_OK` only on full success. Do not print or read database records, secrets, or user data. Success setup markers: `SUPPORT_IMAGE_RECEIVER_STAGING_READY`, `SUPPORT_IMAGE_TEMP_TRANSFER_KEY_AUTHORIZED`. **Setup does not transfer archive bytes.**

Next after setup is a *read-only* SSH `probe` from OLD pinned to previously independently verified NEW ED25519 SSH host fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`. Then separate guarded approved archive transfer and independent NEW hash. Revoke temporary NEW authorization and retire OLD temporary key after verified transfer. Archive source remains OLD root-private `/var/tmp/ccpc-prod-support-images.HlHFN8R6/mariadb-11.8_redis-8.6-alpine.tar`. The associated `mariadb:11.8` and `redis:8.6-alpine` Docker image IDs are pinned in the preceding section. Do not load new images on NEW, create containers, restore data or cut over; those are outside present approval.

## SUPPORT IMAGE TRANSFER TEMPORARY KEY CREATED — 2026-11-06

**Owner executed approved temporary SSH key creation on OLD `gani@ccpcerpserver`.** Reported terminal output:

```text
SUPPORT_TRANSFER_TEMP_KEY_CREATED
256 SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA ccpc-support-images-transfer-20261106 (ED25519)
```

**PASS — newly generated key creation reported:** Temporary key at `/home/gani/.ssh/id_ed25519_ccpc_support_images_transfer_20261106`, paired public key `.pub`, verified ED25519 fingerprint `SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA`. Key is uniquely dedicated to approved support-image archive transfer; no NEW-host authorization, receiver, or image bytes yet. Private key must never be printed/shared/committed.

**NEXT one OLD-host read-only operator step — fingerprint-check and print only PUBLIC key:**

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != 'ccpcerpserver' ] ||
   [ "$(id -un)" != 'gani' ]; then
  echo 'STOP: wrong OLD host or account'; exit 1
fi

pub="$HOME/.ssh/id_ed25519_ccpc_support_images_transfer_20261106.pub"
expected='SHA256:ONJlWrCRTBIJ1anTVYJTpre2E56D4RtjsLXREEdJFqA'

if [ ! -f "$pub" ] || [ -L "$pub" ] ||
   [ "$(stat -c '%U:%a' "$pub")" != 'gani:644' ]; then
  echo 'STOP: unexpected or missing public key'; exit 1
fi

actual="$(ssh-keygen -lf "$pub" | awk '{print $2}')"
if [ "$actual" != "$expected" ]; then
  echo 'STOP: public-key fingerprint mismatch'; exit 1
fi

echo 'SUPPORT_TRANSFER_PUBLIC_KEY_VERIFIED'
cat -- "$pub"
EOF
```

Expected `SUPPORT_TRANSFER_PUBLIC_KEY_VERIFIED` and exactly one `ssh-ed25519` public key line with comment `ccpc-support-images-transfer-20261106`. **Never request/print private key.** On unexpected result STOP. After recording exact public key, install restricted source-IP-only forced receiver on NEW `ccpc-prod`; then probe SSH before transferring the exact archive `/var/tmp/ccpc-prod-support-images.HlHFN8R6/mariadb-11.8_redis-8.6-alpine.tar` (145522176 bytes; SHA-256 `e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`). No Docker load, start, restore, old PROD/DEV modifications, or cutover approved.

## SUPPORT IMAGE ARCHIVE ENCRYPTED TRANSFER APPROVED — 2026-11-06

**Owner explicitly replied "Approved"** to the separately scoped transfer of the single previously verified 145,522,176-byte `mariadb:11.8` + `redis:8.6-alpine` archive from OLD `gani@ccpcerpserver` (source IP `192.168.50.166`) to private staging on NEW `ccpcadmin@ccpcerp-prod` (IP `192.168.50.186`). This explicitly includes setup of one **new, dedicated, short-lived, source-IP-limited, forced-command SSH transfer key**, then **revoking the NEW authorization and retiring OLD key** following successful destination verification. This does not authorize loading the support images into NEW Docker, creating containers, starting ERPNext, restoring MariaDB data, modifying OLD PROD/DEV, or cutting over.

**Verified source archive unchanged as of most recent export output:** `/var/tmp/ccpc-prod-support-images.HlHFN8R6/mariadb-11.8_redis-8.6-alpine.tar`; byte size **145522176**; SHA-256 **`e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`**. Root-owned 0700 parent, 0600 tar. Proven original running PROD image IDs: MariaDB `sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4`; Redis `sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763`.

**NEXT single step on OLD `gani@ccpcerpserver`:** Generate only a NEW temporary, user-owned ED25519 public/private key pair (no SSH connection or file transfer during this step); do not touch `id_ed25519_ccpc_backup` or any retired transfer keys. The operator must not paste/print the private key.

```bash
bash <<'EOF'
set -euo pipefail
umask 077

if [ "$(hostnamectl --static)" != "ccpcerpserver" ] ||
   [ "$(id -un)" != "gani" ]; then
  echo 'STOP: wrong OLD server or account'; exit 1
fi

sshdir="$HOME/.ssh"
key="$sshdir/id_ed25519_ccpc_support_images_transfer_20261106"

if [ ! -d "$sshdir" ] || [ -L "$sshdir" ] ||
   [ "$(stat -c '%U:%a' "$sshdir")" != 'gani:700' ]; then
  echo 'STOP: SSH directory ownership or permissions unexpected'; exit 1
fi

if [ -e "$key" ] || [ -L "$key" ] ||
   [ -e "$key.pub" ] || [ -L "$key.pub" ]; then
  echo 'STOP: dedicated temporary key path already exists; unchanged'; exit 1
fi

ssh-keygen -q -t ed25519 -N ''   -C 'ccpc-support-images-transfer-20261106'   -f "$key"

chmod 600 "$key"
chmod 644 "$key.pub"

echo 'SUPPORT_TRANSFER_TEMP_KEY_CREATED'
ssh-keygen -lf "$key.pub"
EOF
```

Expected marker `SUPPORT_TRANSFER_TEMP_KEY_CREATED` plus the **new** ED25519 public-key fingerprint. Child-shell `set -euo pipefail` will not close the operator's current shell. If any STOP/error, do not blindly rerun; verify. After owner supplies the marker and fingerprint, retrieve **only public** key text, create a NEW private `0700` staging and restricted `authorized_keys` receiver that accepts only an explicit `probe` and this one archive, with exact size and SHA-256 validation and no overwrite. NEW SSH server ED25519 fingerprint previously independently verified: `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`. After read-only probe and transfer, independently hash the NEW archive before cleanup. Preserve all existing SSH authorized lines, NEW app image, historical backup files, Docker runtimes and OLD backup system.

**Current status:** Transfer and key creation are **approved but not yet executed** for the supporting-images archive. All three image IDs are known, with only the app image loaded on NEW and four owner-selected Nov 5 backup artifacts privately staged; NEW database and Redis images absent at last inspection.

## EXACT MARIADB AND REDIS SUPPORTING IMAGE ARCHIVE EXPORTED — 2026-11-06

**Owner-executed expressly approved OLD-host export**, following preflight checks for correct OLD host `ccpcerpserver`, `gani` user, immutable local image IDs, actual running PRODUCTION database/two Redis container images, and OLD disk space. The guarded command wrote just the `mariadb:11.8` and `redis:8.6-alpine` Docker images to one new root-private archive. The owner reported:

```text
SUPPORT_EXPORT_PRIVATE_STAGE=/var/tmp/ccpc-prod-support-images.HlHFN8R6
BEGIN_APPROVED_SUPPORT_IMAGE_EXPORT
SUPPORT_IMAGE_ARCHIVE_PATH=/var/tmp/ccpc-prod-support-images.HlHFN8R6/mariadb-11.8_redis-8.6-alpine.tar
SUPPORT_IMAGE_ARCHIVE_BYTES=145522176
SUPPORT_IMAGE_ARCHIVE_SHA256=e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08
SUPPORT_IMAGES_EXPORTED_AND_CHECKED
```

**PASS — source archive generated and validated by the guarded command:** Root-owned `0700` private staging at `/var/tmp/ccpc-prod-support-images.HlHFN8R6`; image tar expected root-owned `0600`, size **145522176 bytes**, SHA-256 **`e301707c5ff75fd48c4a782e0ddf0c95608062016b9ae64e136f185bd6b8ac08`**, archive `tar -tf` validated and Docker manifest includes both named tags. Pinned original running PRODUCTION image IDs, independently checked before this export:
- MariaDB `mariadb:11.8`: `sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4`
- Redis `redis:8.6-alpine`: `sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763`

No user database records/volumes exported; this is a **Docker image archive only**. OLD running PROD and DEV containers, existing NAS backup files, NEW imported application image, and NEW securely staged four Nov 5 backups remain unchanged by this image export.

**NEXT OWNER APPROVAL GATE — not yet approved:** Request permission to transfer **only this precise supporting-images archive** from OLD to NEW `ccpcerp-prod`, using encrypted SSH, a *new dedicated, short-lived, source-IP-restricted and receiver-command-limited transfer key*, and verification of exact destination archive SHA-256. Explicitly include revocation of the NEW temporary authorization and retirement of the OLD key pair after successful transfer verification in the approval scope. Do not reuse retired keys or alter `id_ed25519_ccpc_backup`. Transfer approval does **not** authorize loading images into NEW Docker, starting containers, database restore, Compose operations, secret changes, or traffic cutover.

After approval, guide the operator in small verified steps: create only new OLD temporary key, read public key/fingerprint, set up forced-command NEW receiver in `0700` isolated staging with byte-count/SHA-256 validation, probe from OLD with pinned NEW SSH ED25519 fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`, transfer the single verified archive, independent NEW-host checksum verification, revoke NEW authorized key and retire OLD key. The OLD source file must be preserved. Request separate approval before NEW Docker image load and ID verification. No restore/start/cutover authorized.

## OWNER APPROVED EXACT PRODUCTION MARIADB AND REDIS IMAGE EXPORT — 2026-11-06

**Owner explicitly said "Approved"** to creating **one protected local Docker image archive** of the exactly verified `mariadb:11.8` and `redis:8.6-alpine` tags on the OLD `gani@ccpcerpserver` host. This authorizes **local image export only**, not copying the archive to NEW, Docker image load on NEW, container creation, database restore, changes to OLD PROD/DEV, or production cutover.

**Pinned source image IDs from nine confirmed running OLD PRODUCTION `frappe_docker` containers:**
- `mariadb:11.8` image ID `sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4`, size `106208155` bytes.
- `redis:8.6-alpine` image ID `sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763`, size `34498212` bytes.
- Six app containers on exact already-migrated `ccpcerp:v16.50.0` image ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`.

**ONE operator step on OLD `gani@ccpcerpserver`:** Run child-shell script checking host/account, source image IDs, three running PROD container identities/project labels, at least 1GiB local free space; `sudo docker image save` to a newly created root-owned 0700 `/var/tmp/ccpc-prod-support-images.XXXXXXXX` directory, archive mode 0600; verify entire tar structure, Docker manifest includes both expected tags, record byte count and SHA-256. The runbook must preserve the reported unique archive path/hash/size from terminal output. If failure after staging creation, leave partial content protected for inspection—**no blind rerun or cleanup**.

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != "ccpcerpserver" ] ||
   [ "$(id -un)" != "gani" ]; then
  echo 'STOP: wrong OLD host or account'
  exit 1
fi

expected_db='sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4'
expected_redis='sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763'

sudo -v

db_id="$(sudo -n docker image inspect --format '{{.Id}}' mariadb:11.8)"
redis_id="$(sudo -n docker image inspect --format '{{.Id}}' redis:8.6-alpine)"
if [ "$db_id" != "$expected_db" ] || [ "$redis_id" != "$expected_redis" ]; then
  echo 'STOP: supporting Docker image IDs changed'
  exit 1
fi

for name in frappe_docker-db-1 frappe_docker-redis-queue-1 frappe_docker-redis-cache-1; do
  case "$name" in
    frappe_docker-db-1) expected="$expected_db" ;;
    *) expected="$expected_redis" ;;
  esac
  current="$(sudo -n docker inspect --format '{{.Image}}|{{.State.Running}}|{{index .Config.Labels "com.docker.compose.project"}}' "$name")"
  if [ "$current" != "$expected|true|frappe_docker" ]; then
    echo "STOP: PROD container identity or running status unexpected: $name"
    exit 1
  fi
done

free_kb="$(df -Pk /var/tmp | awk 'NR==2 {print $4}')"
if [ -z "$free_kb" ] || [ "$free_kb" -lt 1048576 ]; then
  echo 'STOP: less than 1 GiB local export space'
  exit 1
fi

stage="$(sudo -n mktemp -d /var/tmp/ccpc-prod-support-images.XXXXXXXX)"
echo "SUPPORT_EXPORT_PRIVATE_STAGE=$stage"
if [ -L "$stage" ] ||
   [ "$(sudo -n stat -c '%U:%a' "$stage")" != 'root:700' ]; then
  echo 'STOP: export staging directory is not root-private'
  exit 1
fi

archive="$stage/mariadb-11.8_redis-8.6-alpine.tar"
echo 'BEGIN_APPROVED_SUPPORT_IMAGE_EXPORT'
sudo -n docker image save --output "$archive" mariadb:11.8 redis:8.6-alpine
sudo -n chmod 600 "$archive"

if [ -L "$archive" ] ||
   [ "$(sudo -n stat -c '%U:%a' "$archive")" != 'root:600' ]; then
  echo 'STOP: archive permissions or ownership unexpected'
  exit 1
fi

sudo -n tar -tf "$archive" >/dev/null
if ! sudo -n tar -xOf "$archive" manifest.json |
  python3 -c 'import json,sys; m=json.load(sys.stdin); tags={t for item in m for t in item.get("RepoTags", [])}; sys.exit(0 if {"mariadb:11.8","redis:8.6-alpine"}.issubset(tags) else 1)'; then
  echo 'STOP: Docker archive manifest does not contain both expected tags'
  exit 1
fi

bytes="$(sudo -n stat -c '%s' "$archive")"
digest="$(sudo -n sha256sum "$archive" | awk '{print $1}')"
if [ "$bytes" -le 0 ] || [[ ! "$digest" =~ ^[0-9a-f]{64}$ ]]; then
  echo 'STOP: archive size or hash invalid'
  exit 1
fi

echo "SUPPORT_IMAGE_ARCHIVE_PATH=$archive"
echo "SUPPORT_IMAGE_ARCHIVE_BYTES=$bytes"
echo "SUPPORT_IMAGE_ARCHIVE_SHA256=$digest"
echo 'SUPPORT_IMAGES_EXPORTED_AND_CHECKED'
EOF
```

**Precautions:** The `set -euo pipefail` is confined to the child shell to avoid the old interactive-shell exit incident. Docker image export is not a DB dump and does not include business records or database volumes. Do not transfer or load this archive without later explicit scope approval. Leave OLD running PROD+DEV intact; use separate encrypted transfer and independent destination verification following a fresh narrowly authorized SSH credential if approved.

## OLD PRODUCTION SUPPORTING IMAGE IDS VERIFIED — 2026-11-06

**Owner-run read-only Docker inspection on OLD `gani@ccpcerpserver`**, scoped to running containers with Compose project label `frappe_docker`, returned nine active PRODUCTION containers, and exact supporting image IDs:

```text
NAME=/frappe_docker-frontend-1 SERVICE=frontend IMAGE_REF=ccpcerp:v16.50.0 IMAGE_ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8 STATUS=running
NAME=/frappe_docker-queue-short-1 SERVICE=queue-short IMAGE_REF=ccpcerp:v16.50.0 IMAGE_ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8 STATUS=running
NAME=/frappe_docker-backend-1 SERVICE=backend IMAGE_REF=ccpcerp:v16.50.0 IMAGE_ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8 STATUS=running
NAME=/frappe_docker-queue-long-1 SERVICE=queue-long IMAGE_REF=ccpcerp:v16.50.0 IMAGE_ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8 STATUS=running
NAME=/frappe_docker-websocket-1 SERVICE=websocket IMAGE_REF=ccpcerp:v16.50.0 IMAGE_ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8 STATUS=running
NAME=/frappe_docker-scheduler-1 SERVICE=scheduler IMAGE_REF=ccpcerp:v16.50.0 IMAGE_ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8 STATUS=running
NAME=/frappe_docker-redis-queue-1 SERVICE=redis-queue IMAGE_REF=redis:8.6-alpine IMAGE_ID=sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763 STATUS=running
NAME=/frappe_docker-redis-cache-1 SERVICE=redis-cache IMAGE_REF=redis:8.6-alpine IMAGE_ID=sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763 STATUS=running
NAME=/frappe_docker-db-1 SERVICE=db IMAGE_REF=mariadb:11.8 IMAGE_ID=sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4 STATUS=running
=== OLD LOCALLY TAGGED SUPPORTING IMAGE IDS ===
TAG=mariadb:11.8 IMAGE_ID=sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4 SIZE_BYTES=106208155
TAG=redis:8.6-alpine IMAGE_ID=sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763 SIZE_BYTES=34498212
OLD_PRODUCTION_SUPPORT_IMAGE_INSPECTION_COMPLETE
```

**PASS:** All nine running PROD containers were identified through exact Compose project label; the six Frappe app containers use the original app image, two Redis containers use exact same Redis ID, and database container uses exact MariaDB ID. Tagged supporting images **match their live container image IDs**. No DEVELOPMENT containers were targeted, no secrets or database records read, no service modifications. NEW already has exact app image loaded but lacked the MariaDB and Redis tags at previous read-only preflight, with ~735GB free and zero existing containers/volumes.

**Recommendation, not yet authorized:** Preserve reproducibility and avoid mutable remote image tags by exporting these two exact locally tagged supporting images via `sudo docker image save` into **one new root-private local archive on OLD**, then independently verify archive byte count and SHA-256. This read-only Docker operation writes a new temporary tar file to OLD local staging (space needed), leaves running containers intact and does not export databases or volume data. Do **not** export yet: owner authorization must be obtained separately. Subsequently, with further approval, encrypted-copy the archive to NEW private staging, independently check checksum, load tags into NEW Docker and compare both new image IDs to the pinned ones. Keep old backup images and records preserved; do not trigger `docker compose`, `docker pull`, `bench migrate`, restores, scheduler/integration startups, or cutover without separate approvals.

**Important:** No MariaDB data/ERPNext site restoration has occurred on NEW. Latest approved Nov 5 02:00 backup remains verified, with later November 5 business and asynchronous writes not independently reconciled. Live cutover requires separate backup-cutoff verification.

## NEW HOST READ-ONLY DOCKER PREFLIGHT VERIFIED — 2026-11-06

**Owner-run on dedicated NEW `ccpcadmin@ccpcerp-prod`** checked existing Docker image tags, running/stopped containers, Docker volumes, and filesystem space without any image pulls or Docker mutation. Full reported output:

```text
=== APP IMAGE ===
IMAGE_ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8
=== DATABASE AND REDIS IMAGES ===
IMAGE_NOT_PRESENT mariadb:11.8
IMAGE_NOT_PRESENT redis:8.6-alpine
=== EXISTING CONTAINERS ===
=== EXISTING DOCKER VOLUMES ===
=== DOCKER FILESYSTEM AVAILABLE ===
Filesystem                         Size  Used Avail Use% Mounted on
/dev/mapper/ubuntu--vg-ubuntu--lv  787G   12G  735G   2% /
NEW_HOST_READ_ONLY_PREFLIGHT_COMPLETE
```

**PASS — read-only preflight:** NEW has exact imported app image `ccpcerp:v16.50.0` with pinned original ID; neither `mariadb:11.8` nor `redis:8.6-alpine` currently present under those tags; **zero existing Docker containers and volumes** returned in the listing; ~735G free on Docker's filesystem. This is **preparation only**, not a restore readiness or end-to-end integration test. Four Nov 5 02:00 backup files were independently checksum-verified and remain in private NEW staging. Both one-purpose temporary transfer keys already retired and SSH authorizations removed. No containers/services/restoration/cutover performed.

**NEXT one read-only inspection on OLD `gani@ccpcerpserver`**, to identify exact Docker database/Redis image IDs actually used by the `frappe_docker` **PRODUCTION Compose project only**, not DEV `frappe_docker_devcontainer`; no secrets, mounts or configs printed and no Docker changes:

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != "ccpcerpserver" ] ||
   [ "$(id -un)" != "gani" ]; then
  echo 'STOP: wrong server or account'; exit 1
fi

sudo -v
echo '=== OLD PRODUCTION RUNNING CONTAINER IMAGE REFERENCES ==='
ids="$(sudo -n docker ps -q --filter 'label=com.docker.compose.project=frappe_docker')"
if [ -z "$ids" ]; then
  echo 'STOP: no OLD PRODUCTION containers found'; exit 1
fi

while IFS= read -r id; do
  [ -n "$id" ] || continue
  sudo -n docker inspect --format     'NAME={{.Name}} SERVICE={{index .Config.Labels "com.docker.compose.service"}} IMAGE_REF={{.Config.Image}} IMAGE_ID={{.Image}} STATUS={{.State.Status}}' "$id"
done <<< "$ids"

echo '=== OLD LOCALLY TAGGED SUPPORTING IMAGE IDS ==='
for image in mariadb:11.8 redis:8.6-alpine; do
  if sudo -n docker image inspect "$image" >/dev/null 2>&1; then
    sudo -n docker image inspect --format       'TAG={{index .RepoTags 0}} IMAGE_ID={{.Id}} SIZE_BYTES={{.Size}}' "$image"
  else
    echo "IMAGE_TAG_NOT_PRESENT $image"
  fi
done

echo 'OLD_PRODUCTION_SUPPORT_IMAGE_INSPECTION_COMPLETE'
EOF
```

This does not inspect container environment variables, network credentials, database rows, volume contents, or site config. If actual PROD supporting image IDs differ from local tags, investigate without pulling or exporting. A later move of these missing support images, a new isolated Compose stack, image pulls, database restore, and final cutover all require separately scoped owner approval. The Nov 5 02:00 backup freshness relative to later Nov 5 writes must still be assessed before live migration.

## NOV 5 TEMPORARY OLD TRANSFER KEY RETIRED — 2026-11-06

**Owner-run previously authorized, fingerprint-checked cleanup on OLD `gani@ccpcerpserver` finished successfully**, after NEW SSH authorization was independently verified absent (`NOV05_TEMP_TRANSFER_KEY_ENTRIES=0`). The owner supplied actual output:

```text
NOV05_OLD_TEMP_TRANSFER_KEY_PAIR_RETIRED
EXISTING_BACKUP_KEY_UNTOUCHED
```

**PASS — source-side script-reported retirement:** The two named OLD temporary SSH key files for `ccpc-nov05-backup-transfer-20261106` were removed after confirming host, account, original public and private key fingerprint `SHA256:f/ZQCIfeauyPQ7RpP1rQlXs4/Ej50pvxuGCTAF0wIeA`, ownership and mode. The unrelated scheduled-backup SSH identity was not a deletion target. This normal unlink is not physical secure erasure. The OLD November 5 backup remains on NAS; all four NEW copies were independently hash-matched. NEW Docker `ccpcerp:v16.50.0` is loaded with identical pinned original image ID. **No NEW ERPNext runtime containers, MariaDB/site restore, PROD cutover or OLD PROD/DEV runtime change has been authorized/performed**.

**Next read-only preparation** on NEW `ccpcadmin@ccpcerp-prod`: inspect locally present MariaDB 11.8 and Redis 8.6-alpine images, Docker containers and volumes, and free disk space, to plan an isolated, no-scheduler/no-external-effects restoration rehearsal. No pulling/building images, starting services, or restoring databases until a separate owner approval.

```bash
bash <<'EOF'
set -euo pipefail
if [ "$(hostnamectl --static)" != 'ccpcerp-prod' ] ||
   [ "$(id -un)" != 'ccpcadmin' ]; then
  echo 'STOP: wrong server or account'; exit 1
fi
sudo -v
echo '=== APP IMAGE ==='
sudo -n docker image inspect ccpcerp:v16.50.0 --format 'IMAGE_ID={{.Id}}'
echo '=== DATABASE AND REDIS IMAGES ==='
for image in mariadb:11.8 redis:8.6-alpine; do
  if sudo -n docker image inspect "$image" >/dev/null 2>&1; then
    printf 'IMAGE_PRESENT %s\n' "$image"
  else
    printf 'IMAGE_NOT_PRESENT %s\n' "$image"
  fi
done
echo '=== EXISTING CONTAINERS ==='
sudo -n docker ps -a --format 'CONTAINER={{.Names}} IMAGE={{.Image}} STATUS={{.Status}}'
echo '=== EXISTING DOCKER VOLUMES ==='
sudo -n docker volume ls --format 'VOLUME={{.Name}}'
echo '=== DOCKER FILESYSTEM AVAILABLE ==='
df -h /var/lib/docker
echo 'NEW_HOST_READ_ONLY_PREFLIGHT_COMPLETE'
EOF
```

This probe uses Docker inspection/listing only, no network pulls, writes, Docker image load, container creation, restart or backups manipulation. Check any unexpected existing containers/volumes before designing an isolated rehearsal. Existing deployment git checkouts remain unchanged.

**Data cutoff caveat:** Owner says 2026-11-05 02:00 is latest *backup* and no transactions occurred after November 5. This alone does not establish whether any record or file writes happened between Nov 5 at 02:00 and end of that day. Reconcile the final source and cutover transaction boundary before ever treating the restored snapshot as authoritative.

## NOV 5 TEMPORARY SSH AUTHORIZATION INDEPENDENTLY ABSENT — 2026-11-06

**Owner-run independent read-only check on NEW `ccpcadmin@ccpcerp-prod` returned:**

```text
NOV05_TEMP_TRANSFER_KEY_ENTRIES=0
```

**PASS:** The dedicated `ccpc-nov05-backup-transfer-20261106` entry is absent from the NEW `ccpcadmin` `~/.ssh/authorized_keys` file checked separately from the preceding atomic revocation. The backup receiver originally allowed only four files and a probe from OLD `192.168.50.166`; that authorization has now been retired. This result does not inventory unrelated SSH mechanisms or keys; the check is intentionally scoped. All four Nov 5 backup destination hashes matched the OLD sources, staging `0700` and file modes `0600` were verified previously. The NEW Docker image `ccpcerp:v16.50.0` is loaded with pinned image ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`. No containers or database restores have started.

**NEXT single already-approved security operation:** On **OLD `gani@ccpcerpserver` only**, retire the newly created temporary November 5 backup-transfer SSH key pair after independently verifying correct host/user, exact named regular files with expected owner and mode, and matching public/private fingerprint `SHA256:f/ZQCIfeauyPQ7RpP1rQlXs4/Ej50pvxuGCTAF0wIeA`. Do not delete or modify the pre-existing backup-specific key `id_ed25519_ccpc_backup`, either archive, or any of the four backup artifacts. Child Bash confines `set -euo pipefail` to avoid terminating user's interactive terminal.

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != 'ccpcerpserver' ] ||
   [ "$(id -un)" != 'gani' ]; then
  echo 'STOP: wrong host or user'; exit 1
fi

key="$HOME/.ssh/id_ed25519_ccpc_nov05_backup_transfer_20261106"
pub="$key.pub"
expected='SHA256:f/ZQCIfeauyPQ7RpP1rQlXs4/Ej50pvxuGCTAF0wIeA'

for file in "$key" "$pub"; do
  if [ ! -f "$file" ] || [ -L "$file" ] ||
     [ "$(stat -c '%U' "$file")" != 'gani' ]; then
    echo 'STOP: missing, linked or wrong-owner temporary key'; exit 1
  fi
done

if [ "$(stat -c '%a' "$key")" != '600' ] ||
   [ "$(stat -c '%a' "$pub")" != '644' ]; then
  echo 'STOP: unexpected temporary-key permissions'; exit 1
fi

public_fp="$(ssh-keygen -lf "$pub" | awk '{print $2}')"
private_fp="$(ssh-keygen -y -P '' -f "$key" | ssh-keygen -lf - | awk '{print $2}')"

if [ "$public_fp" != "$expected" ] || [ "$private_fp" != "$expected" ]; then
  echo 'STOP: temporary-key fingerprint mismatch'; exit 1
fi

rm -- "$key" "$pub"

if [ ! -e "$key" ] && [ ! -e "$pub" ]; then
  echo 'NOV05_OLD_TEMP_TRANSFER_KEY_PAIR_RETIRED'
  echo 'EXISTING_BACKUP_KEY_UNTOUCHED'
fi
EOF
```

**Expected:** `NOV05_OLD_TEMP_TRANSFER_KEY_PAIR_RETIRED` and `EXISTING_BACKUP_KEY_UNTOUCHED`. Stop on any mismatch or error; do not rerun blindly. Deletion is normal unlink, not guaranteed secure overwrite. No new approval needed for this exact retirement step because owner expressly approved the short-lived key's revocation and removal after verified transfer. Further Docker stack, MariaDB/Redis images, Compose configuration, site restoration and final cutover remain separate, explicitly gated operations. Nov 5 02:00 is the owner-confirmed most recent *backup*, not automatically the final transaction/write cutoff.

## NOV 5 TEMPORARY SSH AUTHORIZATION REMOVAL REPORTED SUCCESS — 2026-11-06

**Owner executed the previously authorized exact-line SSH `authorized_keys` revocation on NEW `ccpcadmin@ccpcerp-prod`.** The owner-provided terminal paste contained garbled command echo `data = auth.read_bytes()` and `PYint(...)` fragments, followed by all three expected success markers:

```text
NOV05_TEMP_TRANSFER_AUTH_REVOKED
OTHER_AUTHORIZED_KEYS_PRESERVED
VERIFIED_NOV05_BACKUPS_RETAINED
```

**Status:** Script-reported success removing only the temporary `ccpc-nov05-backup-transfer-20261106` public-key authorization from `~/.ssh/authorized_keys`, preserving other lines and retaining all four already independently checksum-verified November 5 02:00 backup artifacts in private NEW-host staging. The output alone does not independently establish absence of the line; verify via a **read-only count on NEW** before retiring the temporary OLD key pair. No backups or Docker images were deleted, no restore/run/cutover approved.

**NEXT single read-only command on NEW `ccpcadmin@ccpcerp-prod`:**

```bash
if [ "$(hostnamectl --static)" != "ccpcerp-prod" ] ||
   [ "$(id -un)" != "ccpcadmin" ]; then
  echo 'STOP: wrong server or user'
elif [ ! -f "$HOME/.ssh/authorized_keys" ]; then
  echo 'STOP: authorized_keys missing'
else
  count="$(grep -Fc 'ccpc-nov05-backup-transfer-20261106' "$HOME/.ssh/authorized_keys" || true)"
  printf 'NOV05_TEMP_TRANSFER_KEY_ENTRIES=%s\n' "$count"
fi
```

Expected `NOV05_TEMP_TRANSFER_KEY_ENTRIES=0`. This neither prints other SSH keys nor alters data. If nonzero or STOP, investigate only; **do not remove the OLD key yet**. Upon zero confirmation, retire exactly the new temporary key pair on OLD via guarded fingerprint-checked file unlink, not the existing `id_ed25519_ccpc_backup`. Never delete the backup copies on OLD or NEW. Rehearsal restore and any production cutover require separate approval, and later-than-backup changes must be reviewed before live cutover.

## NOV 5 FOUR NEW-HOST BACKUP FILES INDEPENDENTLY VERIFIED — 2026-11-06

**Owner-run read-only verification directly on NEW `ccpcadmin@ccpcerp-prod`**, after source and receiver both reported successful checksums for all four owner-selected 2026-11-05 02:00 backup artifacts. The local verification checked correct NEW hostname and account, private backup-staging directory ownership/mode `ccpcadmin:700`, each file's ownership/mode/size `ccpcadmin:600:<expected bytes>`, and exact independent SHA-256 hash of each file. Actual owner output:

```text
NOV05_DESTINATION_SHA256_OK 20261105_020001-ccpcerp_local-database.sql.gz
NOV05_DESTINATION_SHA256_OK 20261105_020001-ccpcerp_local-files.tar
NOV05_DESTINATION_SHA256_OK 20261105_020001-ccpcerp_local-private-files.tar
NOV05_DESTINATION_SHA256_OK 20261105_020001-ccpcerp_local-site_config_backup.json
NOV05_DESTINATION_ALL_FOUR_VERIFIED
```

**PASS:** All four files are present and independently SHA-256-verified, owned by `ccpcadmin` with restricted `0600` file and `0700` staging permissions, on NEW at `/home/ccpcadmin/.ccpc-nov05-backup-transfer-20261106`. Baseline exact SHA-256:
- database `8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87` (1,198,839 bytes)
- public files `200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6` (10,240 bytes)
- private files `60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf` (20,480 bytes)
- site config `b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b` (280 bytes; **never print the payload**)

An irrelevant, garbled shell echo `EOFo 'NOV05_DESTINATION_ALL_FOUR_VERIFIED'` preceded the expected marker output. There is no contrary failure marker in the supplied actual result.

**Next already approved security step:** Revoke the dedicated NEW `ccpc-nov05-backup-transfer-20261106` public key entry from `ccpcadmin` `~/.ssh/authorized_keys`, preserving all other existing SSH authorization lines *byte-for-byte*, keeping transferred files and receiver stage untouched. The owner explicitly approved temporary key creation, restricted authorization, then removal after verification. Do not treat key revocation as permission to delete backups, backup stage, existing NAS backup SSH key, or any Docker/ERPNext files. Do not reboot, migrate, restore, run Compose, or cut over.

**ONE guarded local action on NEW `ccpcadmin@ccpcerp-prod`:**

```bash
python3 - <<'PY'
import os
import socket
import stat
import tempfile
from pathlib import Path

def stop(reason):
    print(f'STOP: {reason}; no authorized_keys change')
    raise SystemExit(1)

if socket.gethostname() != 'ccpcerp-prod' or os.getuid() == 0:
    stop('wrong hostname or root execution')
if os.environ.get('USER') != 'ccpcadmin' or Path.home() != Path('/home/ccpcadmin'):
    stop('unexpected account')

sshdir = Path.home() / '.ssh'
auth = sshdir / 'authorized_keys'
stage = Path.home() / '.ccpc-nov05-backup-transfer-20261106'
expected = (
    'from="192.168.50.166",restrict,'
    'command="/home/ccpcadmin/.ccpc-nov05-backup-transfer-20261106/receive-backup.sh" '
    'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH2RioVBTIvEhayHxbVeFNBQaUVq8iDmnDjixt9tXnL5 '
    'ccpc-nov05-backup-transfer-20261106'
).encode('ascii')
try:
    sd, ak, st = os.lstat(sshdir), os.lstat(auth), os.lstat(stage)
except OSError as e:
    stop(f'required file missing: {e}')
if not (stat.S_ISDIR(sd.st_mode) and stat.S_ISREG(ak.st_mode) and stat.S_ISDIR(st.st_mode) and
        sd.st_uid == ak.st_uid == st.st_uid == os.getuid() and
        stat.S_IMODE(sd.st_mode) == 0o700 and stat.S_IMODE(ak.st_mode) == 0o600 and
        stat.S_IMODE(st.st_mode) == 0o700 and ak.st_nlink == 1):
    stop('unexpected SSH file type, owner, permissions or link count')

data = auth.read_bytes()
lines = data.splitlines(keepends=True)
matching = [line for line in lines if line.rstrip(b'\r\n') == expected]
marker = b'ccpc-nov05-backup-transfer-20261106'
if len(matching) != 1 or sum(marker in line for line in lines) != 1:
    stop('expected exactly one matching backup-transfer authorization')

remaining = b''.join(line for line in lines if line.rstrip(b'\r\n') != expected)
temp = None
try:
    fd, temp = tempfile.mkstemp(prefix='.ccpc-nov05-auth-revoke-', dir=sshdir)
    with os.fdopen(fd, 'wb') as out:
        out.write(remaining)
        out.flush()
        os.fsync(out.fileno())
    os.chmod(temp, 0o600)
    os.replace(temp, auth)
    temp = None
finally:
    if temp is not None:
        os.unlink(temp)

if auth.read_bytes() != remaining:
    print('STOP: post-write authorization verification failed; investigate')
    raise SystemExit(1)

print('NOV05_TEMP_TRANSFER_AUTH_REVOKED')
print('OTHER_AUTHORIZED_KEYS_PRESERVED')
print('VERIFIED_NOV05_BACKUPS_RETAINED')
PY
```

Avoid printing contents of `authorized_keys` or site config. A strictly read-only independent marker-count check should follow any successful revocation before OLD private/public key retirement. Never assume authentication has been fully revoked by output markers alone.

**Current outstanding operations:** NEW PRODUCTION app image is already loaded and image-ID-matched; four historical backups now independently verified; **no restored site or live services on NEW**. A separately approved isolated restoration rehearsal still requires a controlled plan and explicit authorization. Owner says this is the most recent backup; that does not yet establish the absence of changes after 02:00 on Nov 5.

## NOV 5 FOUR BACKUP FILES TRANSFERRED WITH RECEIVER CHECKSUM PASS — 2026-11-06

**Owner-run authorized OLD-to-NEW encrypted four-file backup transfer completed**. The guarded source command performed a read-only validation of the OLD NAS CIFS mount, all four source file sizes and SHA-256s, the dedicated temporary key, and the NEW SSH server fingerprint, then streamed each file to NEW restricted receiver from OLD `gani@ccpcerpserver` to NEW `ccpcadmin@ccpcerp-prod`. The owner reported full successful output:

```text
VERIFYING_ALL_FOUR_SOURCE_FILES
SOURCE_SHA256_OK 20261105_020001-ccpcerp_local-database.sql.gz
SOURCE_SHA256_OK 20261105_020001-ccpcerp_local-files.tar
SOURCE_SHA256_OK 20261105_020001-ccpcerp_local-private-files.tar
SOURCE_SHA256_OK 20261105_020001-ccpcerp_local-site_config_backup.json
BEGIN_APPROVED_NOV05_FOUR_FILE_TRANSFER
TRANSFERRING 20261105_020001-ccpcerp_local-database.sql.gz
NOV05_BACKUP_SHA256_OK 20261105_020001-ccpcerp_local-database.sql.gz
TRANSFERRING 20261105_020001-ccpcerp_local-files.tar
NOV05_BACKUP_SHA256_OK 20261105_020001-ccpcerp_local-files.tar
TRANSFERRING 20261105_020001-ccpcerp_local-private-files.tar
NOV05_BACKUP_SHA256_OK 20261105_020001-ccpcerp_local-private-files.tar
TRANSFERRING 20261105_020001-ccpcerp_local-site_config_backup.json
NOV05_BACKUP_SHA256_OK 20261105_020001-ccpcerp_local-site_config_backup.json
NOV05_FOUR_BACKUP_FILES_TRANSFERRED
```

**PASS — source and receiver in-band verification:** Four source checksum passes and four NEW receiver checksum passes. This supports successful transfer to NEW private staging `/home/ccpcadmin/.ccpc-nov05-backup-transfer-20261106`. **Independent local NEW-host verification is still pending**, as is subsequent key revocation. No site config or DB secrets should be printed. No Docker/ERPNext service starts, database restore, migration, cutover, or OLD PROD/DEV modifications were authorized/performed.

**NEXT read-only destination verification on NEW `ccpcadmin@ccpcerp-prod` only:**

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != 'ccpcerp-prod' ] ||
   [ "$(id -un)" != 'ccpcadmin' ]; then
  echo 'STOP: wrong destination host or account'
  exit 1
fi

stage="$HOME/.ccpc-nov05-backup-transfer-20261106"
names=(
  '20261105_020001-ccpcerp_local-database.sql.gz'
  '20261105_020001-ccpcerp_local-files.tar'
  '20261105_020001-ccpcerp_local-private-files.tar'
  '20261105_020001-ccpcerp_local-site_config_backup.json'
)
sizes=(1198839 10240 20480 280)
hashes=(
  '8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87'
  '200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6'
  '60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf'
  'b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b'
)

if [ ! -d "$stage" ] || [ -L "$stage" ] ||
   [ "$(stat -c '%U:%a' "$stage")" != 'ccpcadmin:700' ]; then
  echo 'STOP: unexpected private destination directory'; exit 1
fi

for i in "${!names[@]}"; do
  name="${names[$i]}"
  file="$stage/$name"
  if [ ! -f "$file" ] || [ -L "$file" ] ||
     [ "$(stat -c '%U:%a:%s' "$file")" != "ccpcadmin:600:${sizes[$i]}" ]; then
    echo "STOP: unexpected destination file metadata: $name"
    exit 1
  fi
  actual="$(sha256sum "$file" | awk '{print $1}')"
  if [ "$actual" != "${hashes[$i]}" ]; then
    echo "STOP: destination checksum mismatch: $name"
    exit 1
  fi
  echo "NOV05_DESTINATION_SHA256_OK $name"
done
echo 'NOV05_DESTINATION_ALL_FOUR_VERIFIED'
EOF
```

Expected four `NOV05_DESTINATION_SHA256_OK` lines plus `NOV05_DESTINATION_ALL_FOUR_VERIFIED`. Do not proceed with key retirement until this result is supplied. The script is read-only; it never prints the configuration JSON or database payload. On any error STOP without deletion/retry. After independent verification, the temporary `ccpc-nov05-backup-transfer-20261106` authorization can be precisely revoked (already explicitly approved), then OLD temporary public/private key pair retired, preserving existing backup-specific SSH identity. Do not remove either backup copy during security cleanup.

**Final cutover remains separately gated**: No backup newer than 2026-11-05 02:00 per owner; this does not prove whether any user/background writes happened later on Nov 5. Reconcile before committing live data.

## NOV 5 BACKUP RECEIVER SSH PROBE VERIFIED — 2026-11-06

**Owner-run probe-only command on OLD `gani@ccpcerpserver`, with dedicated temporary key, trusted NEW ED25519 host fingerprint and restricted receiver** returned:

```text
NOV05_TRANSFER_SSH_AUTH_OK
NOV05_TRANSFER_SSH_PROBE_PASS
```

**PASS:** Restricted NEW receiver accepted the temporary key from OLD and allowed only its `probe` action. No backup bytes have been sent. Temporary key: `/home/gani/.ssh/id_ed25519_ccpc_nov05_backup_transfer_20261106` public fingerprint `SHA256:f/ZQCIfeauyPQ7RpP1rQlXs4/Ej50pvxuGCTAF0wIeA`. NEW host IP `192.168.50.186`, trusted ED25519 SSH server fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`. OLD IP `192.168.50.166`, existing NAS mount `//192.168.50.132/erpnext_backups` (CIFS) at `/mnt/erpnext_backups`.

**NEXT OWNER-APPROVED STEP — encrypted four-file-only transfer, not yet executed:** Execute one bounded Bash child-shell command on OLD `ccpcerpserver`. Require expected source host/account; original CIFS NAS mount; exactly four correct files in `/mnt/erpnext_backups/2026-11-05_02-00`, each regular/non-symlink, readable, exact size and SHA-256. Confirm dedicated SSH key mode and public-key fingerprint, revalidate destination ED25519 SSH host fingerprint, pin a temporary user-owned `0600` known_hosts file with strict host checking. For each file, stream bytes via `cat "$file" | ssh -T ... ccpcadmin@192.168.50.186 "receive:$filename"`, using `pipefail`, `IdentitiesOnly=yes`, `BatchMode=yes`, no password or keyboard-interactive auth, and validate receiver's exact line `NOV05_BACKUP_SHA256_OK $filename` before advancing. On any failure STOP; do **not** retry blindly since the NEW receiver intentionally rejects `.partial` or an already finalized file. NO automatic deletion, modification, restoration or reauthorization. Preserve the four original NAS backup files and OLD running PROD+DEV. The receiver creates only protected finalized copies in NEW `~/.ccpc-nov05-backup-transfer-20261106`.

**Exact approved source baseline:**

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `20261105_020001-ccpcerp_local-database.sql.gz` | 1198839 | `8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87` |
| `20261105_020001-ccpcerp_local-files.tar` | 10240 | `200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6` |
| `20261105_020001-ccpcerp_local-private-files.tar` | 20480 | `60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf` |
| `20261105_020001-ccpcerp_local-site_config_backup.json` | 280 | `b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b` |

**Caution:** The site config may contain database credentials and encryption material: do not print its contents, only fixed file names and hashes. Even if all four receiver validations succeed, perform **independent NEW-host SHA-256 verification** before retiring temporary access. Transfer approval does not authorize restore, service startup, scheduler/mail/integration activation or final cutover. The owner describes Nov 5 02:00 as latest backup; determine whether later Nov 5 writes occurred separately before treating it as final live source.

## NOV 5 NEW-HOST RESTRICTED BACKUP RECEIVER SETUP REPORTED — 2026-11-06

**Owner-run approved setup on NEW `ccpcadmin@ccpcerp-prod`**, adding a dedicated temporary source-IP-restricted public key entry with forced command and creating private staging/receiver for exactly the four previously verified November 5, 2026 02:00 backup files. Owner's pasted terminal output showed **garbled paste echo** intermixed with command text but finished with the two expected markers:

```text
NOV05_RECEIVER_STAGING_READY
NOV05_TEMP_TRANSFER_KEY_AUTHORIZED
```

**Status:** Owner's two success markers indicate the new receiver setup script reached its normal completion. However, its independent SSH forced-command behavior is **not yet verified**. No backup files have been streamed or restored; no ERPNext or Docker configuration changed. Proceed with a **probe-only**, previously authorized, no-content SSH test from OLD host before any data transfer.

**NEXT one operator step on OLD `gani@ccpcerpserver`:** Child-shell probe validates source host/account, dedicated temporary key mode and public fingerprint, independently matches the NEW SSH ED25519 host key fingerprint, and invokes only `probe` on NEW restricted receiver.

```bash
bash <<'EOF'
set -euo pipefail
if [ "$(hostnamectl --static)" != 'ccpcerpserver' ] ||
   [ "$(id -un)" != 'gani' ]; then
  echo 'STOP: wrong source host or user'; exit 1
fi

key="$HOME/.ssh/id_ed25519_ccpc_nov05_backup_transfer_20261106"
pub="$key.pub"
expected_pub_fp='SHA256:f/ZQCIfeauyPQ7RpP1rQlXs4/Ej50pvxuGCTAF0wIeA'
expected_host_fp='SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c'

if [ ! -f "$key" ] || [ -L "$key" ] ||
   [ ! -f "$pub" ] || [ -L "$pub" ] ||
   [ "$(stat -c '%U:%a' "$key")" != 'gani:600' ]; then
  echo 'STOP: temporary transfer key invalid'; exit 1
fi

actual_pub_fp="$(ssh-keygen -lf "$pub" | awk '{print $2}')"
if [ "$actual_pub_fp" != "$expected_pub_fp" ]; then
  echo 'STOP: public key fingerprint mismatch'; exit 1
fi

scanned="$(ssh-keyscan -T 5 -t ed25519 192.168.50.186 2>/dev/null)"
actual_host_fp="$(printf '%s\n' "$scanned" | ssh-keygen -lf - | awk '{print $2}')"
if [ "$actual_host_fp" != "$expected_host_fp" ]; then
  echo 'STOP: NEW host SSH fingerprint mismatch'; exit 1
fi

kh="$(mktemp)"
trap 'rm -f -- "$kh"' EXIT
chmod 600 "$kh"
printf '%s\n' "$scanned" > "$kh"

if ssh -T -i "$key" \
  -o IdentitiesOnly=yes -o BatchMode=yes \
  -o PreferredAuthentications=publickey -o PasswordAuthentication=no \
  -o KbdInteractiveAuthentication=no -o StrictHostKeyChecking=yes \
  -o HostKeyAlgorithms=ssh-ed25519 -o UserKnownHostsFile="$kh" \
  -o ConnectTimeout=8 \
  ccpcadmin@192.168.50.186 probe; then
  echo 'NOV05_TRANSFER_SSH_PROBE_PASS'
else
  echo 'STOP: NOV05_TRANSFER_SSH_PROBE_FAILED'
  exit 1
fi
EOF
```

Expected exactly `NOV05_TRANSFER_SSH_AUTH_OK` from forced receiver and `NOV05_TRANSFER_SSH_PROBE_PASS` from OLD script. STOP, do not attempt to copy anything, if probe fails. Temporary known-host file created/deleted locally only. Leave existing backup-specific key, files, imported Docker image and running PROD/DEV unchanged. Only after probe PASS should a distinct guarded source checksum and encrypted four-file stream be offered.

## NOV 5 BACKUP TRANSFER PUBLIC KEY VERIFIED — 2026-11-06

**Owner's read-only OLD-host inspection output**:

```text
NOV05_PUBLIC_KEY_FINGERPRINT_OK
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH2RioVBTIvEhayHxbVeFNBQaUVq8iDmnDjixt9tXnL5 ccpc-nov05-backup-transfer-20261106
```

This is the **public** half of the dedicated key, with verified fingerprint `SHA256:f/ZQCIfeauyPQ7RpP1rQlXs4/Ej50pvxuGCTAF0wIeA`; OLD private key may not be printed or copied to NEW. **No NEW authorization or backup transfer has yet been completed.**

**Next approved step:** On NEW `ccpcadmin@ccpcerp-prod`, create new private `0700` staging `/home/ccpcadmin/.ccpc-nov05-backup-transfer-20261106` with an executable forced-command receiver. Authorize *only* the public key above in the existing `~/.ssh/authorized_keys`, with `from="192.168.50.166",restrict,command="/home/ccpcadmin/.ccpc-nov05-backup-transfer-20261106/receive-backup.sh"`. Verify exact key fingerprint locally before install; reject existing stage or previous matching key, and preserve all other authorizations and files.

The receiver must allow `probe` and precisely the four `receive:<filename>` operations, require a fresh non-existing destination and `.partial`, enforce fixed source sizes and SHA-256 and atomic no-overwrite finalization, without permitting an interactive shell, arbitrary commands, paths or restores. Pinned reference host ED25519 fingerprint for later OLD-to-NEW SSH probe is `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`.

Expected file constraints from earlier OLD verification:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `20261105_020001-ccpcerp_local-database.sql.gz` | 1198839 | `8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87` |
| `20261105_020001-ccpcerp_local-files.tar` | 10240 | `200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6` |
| `20261105_020001-ccpcerp_local-private-files.tar` | 20480 | `60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf` |
| `20261105_020001-ccpcerp_local-site_config_backup.json` | 280 | `b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b` |

**Guardrail:** This setup step installs restricted SSH authentication but transfers **no backup content**. Don't reveal the 280-byte site config's contents, reuse the older image-transfer key or backup-specific key, touch Docker/ERPNext/OLD PROD/DEV, start containers, restore data, or cut over. After user reports setup result, verify with read-only pinned SSH probe before streaming any files. Remove temporary authorization and retire key after four independently verified files.

## NOV 5 BACKUP TRANSFER TEMPORARY PUBLIC KEY CREATED — 2026-11-06

**Owner-executed dedicated temporary OLD-host SSH key generation**, after explicit permission to create a source-IP-restricted, forced-command, receive-only backup transfer on NEW. Reported terminal output:

```text
NOV05_TRANSFER_KEY_CREATED
256 SHA256:f/ZQCIfeauyPQ7RpP1rQlXs4/Ej50pvxuGCTAF0wIeA ccpc-nov05-backup-transfer-20261106 (ED25519)
```

**PASS:** The newly generated temporary ED25519 key at `/home/gani/.ssh/id_ed25519_ccpc_nov05_backup_transfer_20261106` has public fingerprint `SHA256:f/ZQCIfeauyPQ7RpP1rQlXs4/Ej50pvxuGCTAF0wIeA`. The private half is confidential, `0600`, not to be printed, pasted, copied to NEW or committed to GitHub. Owner's separately existing `id_ed25519_ccpc_backup` remains excluded. Temporary NEW `authorized_keys` access has **not** been installed; no NAS backup bytes sent.

**NEXT one read-only OLD-host step — print only the validated PUBLIC key line** for establishing the exact NEW-host restricted authorization, without accessing/displaying the private key:

```bash
bash <<'EOF'
set -euo pipefail
if [ "$(hostnamectl --static)" != 'ccpcerpserver' ] ||
   [ "$(id -un)" != 'gani' ]; then
  echo 'STOP: wrong host/account'; exit 1
fi

pub="$HOME/.ssh/id_ed25519_ccpc_nov05_backup_transfer_20261106.pub"
expected='SHA256:f/ZQCIfeauyPQ7RpP1rQlXs4/Ej50pvxuGCTAF0wIeA'
if [ ! -f "$pub" ] || [ -L "$pub" ] ||
   [ "$(stat -c %U "$pub")" != 'gani' ]; then
  echo 'STOP: public key missing, linked or wrong owner'; exit 1
fi

actual="$(ssh-keygen -lf "$pub" | awk '{print $2}')"
if [ "$actual" != "$expected" ]; then
  echo 'STOP: unexpected public key fingerprint'; exit 1
fi

echo 'NOV05_PUBLIC_KEY_FINGERPRINT_OK'
cat -- "$pub"
EOF
```

Output must contain exactly one `ssh-ed25519` **public** key line matching the expected fingerprint; never request or share the private key. After obtaining it, a separate bounded NEW-host step may create a private receive-only directory and forced-command SSH receiver restricted to this key and to OLD source IP `192.168.50.166`, with checksum checks for exactly the four approved Nov 5 artifacts. Stop if input differs; do not assume old image-transfer credentials can be reused.

## OWNER APPROVED TEMPORARY NOV 5 BACKUP TRANSFER SSH ACCESS — 2026-11-06

**Explicit owner response:** "Approved, the Nov. 05 2:00 AM is the latest there are no latest than that". This approves the previously requested **separate, dedicated, temporary SSH authentication key and restricted NEW-host public-key authorization** for encrypted transfer of only the four owner-selected November 5, 2026 02:00 OLD-PRODUCTION NAS artifacts. The source old host IP remains `192.168.50.166`, new host IP `192.168.50.186` and trusted NEW ED25519 SSH server host-key fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`. Remove temporary NEW authorization and retire dedicated OLD key after independently verifying all destination files. This is **not** authorization for unbounded SSH access, for reuse of the old `id_ed25519_ccpc_backup` key, or for Docker/container creation, restoring business data, schema migration, scheduler/email/integration activation or cutover.

**Freshness clarification:** Owner explicitly confirms **no backup later than 2026-11-05 02:00** is available. This statement does not itself prove no transactions, edits, uploads or asynchronous writes occurred after that timestamp. The 02:00 backup remains the selected **isolated rehearsal** source until reconciled, and no newer source is to be presumed or fabricated.

**Next ONE operator step on OLD `gani@ccpcerpserver`:** Create a uniquely named, user-owned temporary ED25519 key pair; do not touch existing backup key or present its private contents.

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != 'ccpcerpserver' ] ||
   [ "$(id -un)" != 'gani' ]; then
  echo 'STOP: wrong server or account'; exit 1
fi

key="$HOME/.ssh/id_ed25519_ccpc_nov05_backup_transfer_20261106"
if [ -e "$key" ] || [ -L "$key" ] ||
   [ -e "$key.pub" ] || [ -L "$key.pub" ]; then
  echo 'STOP: transfer-key path already exists; unchanged'; exit 1
fi

if [ ! -d "$HOME/.ssh" ] || [ -L "$HOME/.ssh" ]; then
  echo 'STOP: SSH directory missing or linked'; exit 1
fi

umask 077
ssh-keygen -q -t ed25519 -N '' -C 'ccpc-nov05-backup-transfer-20261106' -f "$key"
chmod 600 "$key"
chmod 644 "$key.pub"
echo 'NOV05_TRANSFER_KEY_CREATED'
ssh-keygen -lf "$key.pub"
EOF
```

`set -euo pipefail` is **inside the child shell**, not in user's interactive terminal. The no-passphrase private key is sensitive, temporary, and must never be pasted, logged or committed. Print/share the **public key only** in a later bounded step. Build a source-IP-restricted `authorized_keys` forced receiver on NEW that permits only the expected four fixed backup filenames and SHA-256s, stores each in private staging and refuses overwrite. Do not create NEW authorization in this first step. Any error must STOP for review and **not** trigger another `ssh-keygen` or overwrite.

**Existing source checksum baseline:** Database `8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87`; public tar `200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6`; private tar `60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf`; site config `b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b`. Never display JSON contents as it can contain encryption/authentication secrets.

**Status as of this entry:** User approved access setup and transfer. No new key or authorization has yet been executed/reported for this backup transfer; original exact app image is already safely loaded on NEW.

## OWNER APPROVED NOV 5 FOUR-ARTIFACT BACKUP TRANSFER — 2026-11-06

**Explicit owner response**: "Approved, The November 5, 2026 is the latest and there are no transaction after that day" to the separate request for **protected, encrypted, four-artifact-only transfer** from OLD live `ccpcerpserver`'s Synology NAS `/mnt/erpnext_backups/2026-11-05_02-00` to NEW `ccpcerp-prod` private staging. Approval covers moving **only** the previously fixed November 5 backup and verifying four source/destination hashes. It does **not** authorize restoring any database, launching a Compose stack, starting scheduler/email/integrations, changing existing OLD PROD/DEV, modifying production data, or cutting over traffic.

**Owner data-freshness statement:** Owner says Nov 5 is the latest backup and no transactions occurred **after that day**. The documented source was captured **2026-11-05 02:00:01 Asia/Manila**. The statement does **not by itself confirm** there were zero transactions **later on November 5 after 02:00**, nor that there were zero background/configuration/file updates after the backup. Before any final cutover, verify ERPNext write/activity cutoffs, database/doc timestamps, site/attachment consistency and reconcile with the intended source. Do not force a new backup absent need or silently accept loss of newer changes; the chosen snapshot is approved for an **isolated restoration rehearsal** now.

**Four source artifacts and source SHA-256 values (already independently obtained by OLD owner):**

| File | Bytes | Source SHA-256 |
| --- | ---: | --- |
| `20261105_020001-ccpcerp_local-database.sql.gz` | 1198839 | `8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87` |
| `20261105_020001-ccpcerp_local-files.tar` | 10240 | `200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6` |
| `20261105_020001-ccpcerp_local-private-files.tar` | 20480 | `60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf` |
| `20261105_020001-ccpcerp_local-site_config_backup.json` | 280 | `b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b` |

All four files earlier passed read-only gzip/tar/JSON format checks. The small site config may contain credentials/encryption material; **never print or paste file contents**. Protect DB and attachments as confidential business data. Source backup files must remain unchanged and no old NAS retention policy may be changed by this transfer.

**SSH transport constraint:** Prior temporary SSH image-transfer key `id_ed25519_ccpc_prod_image_transfer_20261106` was explicitly revoked and retired after exact-image transfer. Existing `id_ed25519_ccpc_backup` must not be repurposed or changed. OLD-to-NEW default SSH public-key login previously failed. Plan a **new dedicated short-lived, receive-only backup-transfer SSH key** with trusted NEW host-key fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c` and verified source IP `192.168.50.166` for destination `192.168.50.186`. Restrict to the four exact backup objects and verify independent destination checksums, then revoke access and retire temporary key. **The owner has approved the backup transfer but has not separately authorized changing SSH account access** for this second transfer; ask for that narrow approval rather than assuming the prior image-only SSH key approval extends to a new key. Avoid loosening archive permissions, copying public credentials, adding unrestricted keys, or altering live scheduled-backup credentials.

**Immediate next action:** Request consent to create and temporarily authorize a separate, source-IP-restricted, receive-only SSH backup-transfer key (and revoke/remove it after successful independent verification). After consent, guide one checked step at a time; do not execute auth changes without it. The exact original PRODUCTION Docker image is already loaded on NEW and verified at `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`; don't repeat image transfer.

## VERIFIED NEW-HOST DOCKER IMAGE LOAD — 2026-11-06

**Owner-run approved operation on NEW `ccpcadmin@ccpcerp-prod`:** The guarded import script checked the correct NEW host and account, private staging/archive metadata and SHA-256, required an unused destination image tag, then ran `sudo docker image load --input "$archive"`. Actual operator output:

```text
[sudo] password for ccpcadmin:
BEGIN_APPROVED_NEW_HOST_DOCKER_IMAGE_LOAD
Loaded image: ccpcerp:v16.50.0
NEW_IMAGE_ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8
NEW_IMAGE_ID_MATCH_OK
```

There was a visibly garbled shell paste echo (`EOFo 'NEW_IMAGE_ID_MATCH_OK'`) before the command output, but the expected `docker load` result and SHA check completed. **PASS: `ccpcerp:v16.50.0` is loaded into NEW Docker with exactly the same image ID as the six running OLD PROD application containers**, `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`.

**Scope achieved:** NEW Docker image-store import and post-import image-ID verification only. The original archive remains preserved NEW at `/home/ccpcadmin/.ccpc-prod-image-transfer-20261106/ccpcerp-v16.50.0.tar`, with independently matched SHA-256 `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`; OLD exported archive and live image preserved as well. The one-purpose SSH transfer key was revoked on NEW, independently confirmed `TEMP_TRANSFER_KEY_ENTRIES=0`, and temporary OLD key pair retired with owner-reported success. Existing backup key not touched.

**NOT done / not authorized:** No new-host Compose stack, container creation/start, ERPNext site/database restore, secret provisioning, schema migration, scheduler/email/integration activation, DNS/cutover, or modifications to OLD PRODUCTION and DEVELOPMENT. The separate `mariadb:11.8` and `redis:8.6-alpine` images, service configuration, volumes, and database/site data have **not** yet been migrated.

**NEXT OWNER APPROVAL GATE:** Ask separately whether owner approves a protected, encrypted **four-artifact-only** transfer of the specifically selected **November 5, 2026 02:00** OLD live-PRODUCTION NAS backup `/mnt/erpnext_backups/2026-11-05_02-00` to isolated private staging on NEW `ccpcerp-prod`. The source checksums were captured and passed DB gzip, public/private tar, and JSON syntax checks. After any separately authorized transfer, verify four exact destination SHA-256 values before attempting an isolated non-live restoration rehearsal. The Nov 5 data is **historical rehearsal only**: cannot replace more recent live transactions at final cutover without a separate consistent final backup and reconciliation or explicit signed risk acceptance. Transfer approval would not authorize the restore, container startup, or use of production secrets. Plan a distinct short-lived secure transfer path; do not reuse retired SSH credentials or alter the existing scheduled backup key.

## OWNER APPROVED NEW-HOST EXACT IMAGE LOAD — 2026-11-06

**Explicit owner response: "aPPROVED"** to the separately scoped operation of loading the already transferred and independently SHA-256-verified `ccpcerp:v16.50.0` archive into Docker's image store on the NEW `ccpcerp-prod` host, then inspecting the loaded image ID. This allows a NEW-host Docker image-store write only. **It does not authorize** starting any containers/services, pulling or building newer app code, copying/restoring MariaDB or site files, switching DNS/users, editing OLD PRODUCTION/DEVELOPMENT, or any database migration. **Execution and loaded result still pending**.

**Input archive:** `/home/ccpcadmin/.ccpc-prod-image-transfer-20261106/ccpcerp-v16.50.0.tar` — expected exactly **907840000** bytes, file mode `0600`, directory mode `0700`, owner `ccpcadmin`. SHA-256 `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`; source running immutable image ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`. Earlier NEW filesystem free space was ~740G; actual import size/used space not yet measured.

**ONE operator step on NEW `ccpcadmin@ccpcerp-prod` ONLY — guarded child-shell import:**

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != "ccpcerp-prod" ] || [ "$(id -un)" != "ccpcadmin" ]; then
  echo 'STOP: wrong host or account'; exit 1
fi

stage="$HOME/.ccpc-prod-image-transfer-20261106"
archive="$stage/ccpcerp-v16.50.0.tar"
expected_sha='8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009'
expected_image='sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8'

if [ -L "$stage" ] || [ -L "$archive" ] ||
   [ ! -d "$stage" ] || [ ! -f "$archive" ] ||
   [ "$(stat -c '%U:%a' "$stage")" != "ccpcadmin:700" ] ||
   [ "$(stat -c '%U:%a:%s' "$archive")" != "ccpcadmin:600:907840000" ]; then
  echo 'STOP: archive path, size, ownership or permissions unexpected'; exit 1
fi

actual_sha="$(sha256sum "$archive" | awk '{print $1}')"
if [ "$actual_sha" != "$expected_sha" ]; then
  echo 'STOP: archive hash mismatch'; exit 1
fi

sudo -v
sudo -n docker info >/dev/null

if sudo -n docker image inspect ccpcerp:v16.50.0 >/dev/null 2>&1; then
  echo 'STOP: destination image tag already exists; nothing loaded'; exit 1
fi

echo 'BEGIN_APPROVED_NEW_HOST_DOCKER_IMAGE_LOAD'
sudo -n docker image load --input "$archive"

actual_image="$(sudo -n docker image inspect --format '{{.Id}}' ccpcerp:v16.50.0)"
printf 'NEW_IMAGE_ID=%s\n' "$actual_image"
if [ "$actual_image" != "$expected_image" ]; then
  echo 'STOP: loaded image ID does not match original; do not run it'; exit 1
fi

echo 'NEW_IMAGE_ID_MATCH_OK'
EOF
```

The `set -euo pipefail` applies **inside a child Bash**, so any failure will not exit the operator's interactive shell. `sudo -v` is deliberately completed before image operations. The script reads archive and Docker metadata, checks the destination tag is not already present, writes only the new image into Docker via `docker image load`, and compares the resulting image ID. Successful `docker load` has not yet happened. Stop on any `STOP`/error, do not retry or remove image/archive without review. The temporary transfer key has already been retired and NEW authorized-keys entry revoked; preserve image archive for recovery.

**Following step:** Owner shares actual load output. Only then can we record successful immutable source-to-destination image match and separately scope next work on the Nov 5 four-part data **for isolated rehearsal only**, with no silent loss of post-snapshot business transactions.

## OLD TEMPORARY TRANSFER SSH KEY PAIR RETIRED — 2026-11-06

**Owner-executed the previously approved guarded key retirement on OLD `gani@ccpcerpserver`**, after independently verifying the NEW host no longer contained the dedicated `ccpc-prod-image-transfer-20261106` authorized-keys entry (`TEMP_TRANSFER_KEY_ENTRIES=0`). The child-shell script validated OLD host and user identity; checked that exactly the two specifically named OLD transfer key files existed as regular, non-symlink, user-owned files; confirmed private-key mode `0600`; derived public and private fingerprints and compared each to `SHA256:DQoxNuufbGbgD1KfvlmeZOYk40DaMXgUsI3MnzDBgf8`; then unlinked only those two files. Owner supplied actual output:

```text
OLD_TEMP_TRANSFER_KEY_PAIR_RETIRED
EXISTING_BACKUP_KEY_UNTOUCHED
```

**PASS — reported by guarded operator script:** OLD dedicated transfer private/public key pair was retired, and existing backup-specific SSH key was not a target of the deletion. Normal unlink does not prove physical secure-erasure, nor was secure-erasure authorized. NEW temporary authorization removal was separately checked to yield zero matching entries. The OLD and NEW Docker archive files remain retained; no Docker image load, Compose startup, database/file restore, or migration cutover has happened.

**Transferred image archive independently verified on NEW `ccpcadmin@ccpcerp-prod`:** `/home/ccpcadmin/.ccpc-prod-image-transfer-20261106/ccpcerp-v16.50.0.tar`, **907840000 bytes**, `0600` owned by `ccpcadmin`, in `0700` staging, SHA-256 **`8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`**. The original OLD live image `ccpcerp:v16.50.0` was previously verified in all six PRODUCTION application containers with image ID **`sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`**.

**NEXT APPROVAL GATE — not yet approved:** Request owner authorization to **load only the already verified archived image into the Docker image store of the empty NEW `ccpcerp-prod` host**, then inspect/tag-identity verify that Docker reports the exact expected image ID. Loading the image changes the new host's Docker image store and filesystem and incurs CPU/I/O/storage, but does not itself create/start containers, change services, restore databases/files, or cut over traffic. Do not run `docker load`, `docker compose`, `bench migrate`, restore or touch OLD PROD/DEV without separate authorization. After owner approval, provide one bounded child-shell command on NEW host that gates hostname, `0600` archive and `0700` stage, checks SHA-256, detects any preexisting conflicting local `ccpcerp:v16.50.0` tag, uses `sudo docker load -i` only for this archive, and verifies local image ID matches pinned source. Report Docker load outcome before any further operations.

**Caution on owner-selected November 5, 2026 backup:** The four backup files have format checks and recorded source SHA-256s but are still only designated for an isolated non-live rehearsal; they have not been copied or restored. Do not use the Nov 5 snapshot for final live cutover without addressing newer financial/business transactions via a separately approved consistent final backup/reconciliation or explicit signed data-loss disposition.

## TEMPORARY NEW-HOST SSH AUTHORIZATION ABSENCE CONFIRMED — 2026-11-06

**Owner-run independent read-only check directly on NEW `ccpcadmin@ccpcerp-prod`:**

```text
TEMP_TRANSFER_KEY_ENTRIES=0
```

This result was produced by an exact marker count in `~/.ssh/authorized_keys`, after the earlier guarded authorization removal. **PASS — no entry with `ccpc-prod-image-transfer-20261106` remains in the checked NEW authorized-keys file.** This is consistent with successful revocation of the one dedicated temporary key and preservation of other existing SSH account entries. Do not assume every alternative SSH authorization mechanism is absent; the check is scoped to this known temporary authorized-keys entry.

**NEXT one guarded OLD-host step — retire only the temporary transfer key pair** created expressly for this operation (the user approved a temporary key and previously agreed to its retirement after verified transfer):

```bash
bash <<'EOF'
set -euo pipefail

if [ "$(hostnamectl --static)" != "ccpcerpserver" ] || [ "$(id -un)" != "gani" ]; then
  echo 'STOP: wrong host or account'; exit 1
fi

key="$HOME/.ssh/id_ed25519_ccpc_prod_image_transfer_20261106"
pub="$key.pub"
expected='SHA256:DQoxNuufbGbgD1KfvlmeZOYk40DaMXgUsI3MnzDBgf8'

for file in "$key" "$pub"; do
  if [ ! -f "$file" ] || [ -L "$file" ] ||
     [ "$(stat -c %u "$file")" != "$(id -u)" ]; then
    echo 'STOP: missing, linked or unexpected owner for temporary key'; exit 1
  fi
done

if [ "$(stat -c %a "$key")" != '600' ]; then
  echo 'STOP: temporary private-key permissions unexpected'; exit 1
fi

public_fp="$(ssh-keygen -lf "$pub" | awk '{print $2}')"
private_fp="$(ssh-keygen -y -P '' -f "$key" | ssh-keygen -lf - | awk '{print $2}')"
if [ "$public_fp" != "$expected" ] || [ "$private_fp" != "$expected" ]; then
  echo 'STOP: temporary key fingerprint mismatch; nothing removed'; exit 1
fi

rm -- "$key" "$pub"
if [ ! -e "$key" ] && [ ! -e "$pub" ]; then
  echo 'OLD_TEMP_TRANSFER_KEY_PAIR_RETIRED'
  echo 'EXISTING_BACKUP_KEY_UNTOUCHED'
fi
EOF
```

**Guardrails:** This only deletes **two exactly named, validated source-side temporary transfer-key files**, not the pre-existing backup key `id_ed25519_ccpc_backup`, root-private original image tar, NEW verified archive, or any site/database backup; it changes no ERPNext or Docker runtime. `set -euo pipefail` is inside a bounded child shell, avoiding the previously observed interactive-terminal exit. `ssh-keygen -y` internally reads the private key but its contents are piped into fingerprint calculation; do not print or paste private bytes. Stop and inspect on any unexpected output rather than deleting anything else. This is a normal file unlink, **not** guaranteed secure media wiping; no secure-erasure operation is intended.

**Current scope:** The independent NEW archive checksum matched the OLD archive; NEW archive path remains `/home/ccpcadmin/.ccpc-prod-image-transfer-20261106/ccpcerp-v16.50.0.tar`, SHA-256 `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`. Original OLD source image and archive are still intact. No `docker load`, Compose startup, site database/file restore, or PROD cutover approved.

## TEMPORARY NEW-HOST SSH AUTHORIZATION REVOCATION REPORTED SUCCESS — 2026-11-06

**Owner-run on NEW `ccpcadmin@ccpcerp-prod`:** Executed previously approved exact-line removal of temporary OLD-to-NEW transfer key from NEW `~/.ssh/authorized_keys`, via guarded local Python that checked owner, file types, staging permissions and size, exact one-line match, wrote remaining lines to a fresh `0600` temporary file, then atomically replaced `authorized_keys` and checked resulting file bytes.

Owner's terminal paste showed some **garbled echo/paste fragments**, followed by all three expected success markers:

```text
TEMP_TRANSFER_SSH_AUTH_REVOKED
OTHER_AUTHORIZED_KEYS_PRESERVED
VERIFIED_IMAGE_ARCHIVE_RETAINED
```

**Status:** Script-reported successful revocation of only the dedicated `ccpc-prod-image-transfer-20261106` entry, preservation of other authorization lines, and retention of the independently checksum-matched image archive on NEW. Because the paste includes garbled text, perform a separate **read-only** confirmation before removing OLD temporary private-key files. Do not print any remaining `authorized_keys` lines or alter SSH configuration. No Docker load, Compose start, DB restore or cutover performed.

**NEXT read-only check on NEW host:**

```bash
if [ "$(hostnamectl --static)" != 'ccpcerp-prod' ]; then
  echo 'STOP: wrong host'
elif [ ! -f "$HOME/.ssh/authorized_keys" ]; then
  echo 'STOP: authorized_keys missing'
else
  count="$(grep -Fc 'ccpc-prod-image-transfer-20261106' "$HOME/.ssh/authorized_keys" || true)"
  printf 'TEMP_TRANSFER_KEY_ENTRIES=%s\n' "$count"
fi
```

Expected `TEMP_TRANSFER_KEY_ENTRIES=0`. On nonzero or STOP, investigate before touching the OLD transfer key. The NEW archive must remain `/home/ccpcadmin/.ccpc-prod-image-transfer-20261106/ccpcerp-v16.50.0.tar`, `907840000` bytes, archive SHA-256 `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`. Source image remains live on OLD and development untouched. Old backup key `id_ed25519_ccpc_backup` must remain intact. OLD temporary transfer private/public key pair retirement is a later distinct step once revocation is confirmed; image import, NAS backup copy and go-live require separate approvals.

## INDEPENDENT NEW-HOST IMAGE ARCHIVE INTEGRITY VERIFIED — 2026-11-06

**Owner-run read-only directly on NEW `ccpcadmin@ccpcerp-prod`**, independently of the restricted SSH receiver's in-band validation:

```text
ccpcerp-prod
STAGING_MODE=700 STAGING_OWNER=ccpcadmin
ARCHIVE_BYTES=907840000 ARCHIVE_MODE=600 ARCHIVE_OWNER=ccpcadmin
8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009  /home/ccpcadmin/.ccpc-prod-image-transfer-20261106/ccpcerp-v16.50.0.tar
```

**PASS — independently verified destination archive:** Source and destination SHA-256 **match exactly**, size is exactly **907840000 bytes**, staging `0700`, archive `0600`, both owned by `ccpcadmin`, correct target hostname. The original OLD-host tar and running PROD remain unchanged. **No `docker load`, restored database/files, ERPNext start, traffic cutover, or DEV modification yet**.

**Security next step (already owner-authorized as part of temporary-key lifecycle):** Revoke exactly the one temporary image-transfer key authorization for source `192.168.50.166` and public key fingerprint `SHA256:DQoxNuufbGbgD1KfvlmeZOYk40DaMXgUsI3MnzDBgf8` from NEW `ccpcadmin` `~/.ssh/authorized_keys`. Preserve all other authorization lines byte-for-byte; do not delete `authorized_keys`, the receiver staging directory, or its verified image tar. Do not modify existing backup key or other SSH users. Use a guarded, atomic local `authorized_keys` edit that rejects missing/multiple exact target lines, symlinks, unexpected owner/host/account; execute through a child process to avoid the previous interactive-shell exit. After confirmation, safely retire the OLD temporary key files (separate operation), preserving original OLD image archive. No new owner approval is needed for this *specifically agreed revocation after transfer verification*; a separate owner approval **is needed for `sudo docker load`**.

**Next operator command on NEW host only (guarded exact-line revocation, no archive deletion):**

```bash
python3 - <<'PY'
import os
import socket
import stat
import tempfile
from pathlib import Path

if socket.gethostname() != "ccpcerp-prod" or os.getuid() == 0 or os.environ.get("USER") != "ccpcadmin":
    print("STOP: wrong host or user; authorization unchanged")
    raise SystemExit(0)

sshdir = Path.home() / ".ssh"
auth = sshdir / "authorized_keys"
stage = Path.home() / ".ccpc-prod-image-transfer-20261106"
archive = stage / "ccpcerp-v16.50.0.tar"
expected = ('from="192.168.50.166",restrict,command="/home/ccpcadmin/.ccpc-prod-image-transfer-20261106/receive-image.sh" '
            'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJYzObYx7p4c4wOs2zXaikEYu6RCZijmuvsOndUf+mXO '
            'ccpc-prod-image-transfer-20261106').encode("ascii")
try:
    sd = os.lstat(sshdir)
    af = os.lstat(auth)
    st = os.lstat(stage)
    ar = os.lstat(archive)
except OSError as e:
    print(f"STOP: required file missing: {e}; authorization unchanged")
    raise SystemExit(0)
if not (stat.S_ISDIR(sd.st_mode) and stat.S_ISREG(af.st_mode) and
        stat.S_ISDIR(st.st_mode) and stat.S_ISREG(ar.st_mode) and
        all(s.st_uid == os.getuid() for s in (sd, af, st, ar)) and
        stat.S_IMODE(st.st_mode) == 0o700 and
        stat.S_IMODE(ar.st_mode) == 0o600 and ar.st_size == 907840000):
    print("STOP: owner, type, permissions or archive size unexpected; authorization unchanged")
    raise SystemExit(0)
lines = auth.read_bytes().splitlines(keepends=True)
matches = [line for line in lines if line.rstrip(b"\r\n") == expected]
if len(matches) != 1:
    print(f"STOP: expected exactly one temporary authorization, found {len(matches)}; unchanged")
    raise SystemExit(0)
remaining = b"".join(line for line in lines if line.rstrip(b"\r\n") != expected)
tmp = None
try:
    fd, tmp = tempfile.mkstemp(prefix=".ccpc-authorized-keys-revoke-", dir=sshdir)
    with os.fdopen(fd, "wb") as out:
        out.write(remaining)
        out.flush()
        os.fsync(out.fileno())
    os.chmod(tmp, 0o600)
    os.replace(tmp, auth)
    tmp = None
finally:
    if tmp is not None and os.path.exists(tmp):
        os.unlink(tmp)
if auth.read_bytes() != remaining:
    print("STOP: post-write content mismatch; investigate")
else:
    print("TEMP_TRANSFER_SSH_AUTH_REVOKED")
    print("OTHER_AUTHORIZED_KEYS_PRESERVED")
    print("VERIFIED_IMAGE_ARCHIVE_RETAINED")
PY
```

**Stop on anything other than the three success markers; do not rerun or edit manually on error.** The independent SHA-256 evidence is already recorded; this script checks archive file presence, size and private permissions but does not recalculate the archive's checksum. If it finds an unexpected `authorized_keys` entry, it makes **no changes**.

## EXACT LIVE PRODUCTION IMAGE ARCHIVE TRANSFER REPORTED SUCCESS — 2026-11-06

**Owner reported completed, previously explicitly approved OLD-to-NEW restricted SSH stream**, executed from `gani@ccpcerpserver` to `ccpcadmin@ccpcerp-prod`, after authenticated receiver probe. Actual output:

```text
[sudo: authenticate] Password:
BEGIN_APPROVED_IMAGE_ONLY_TRANSFER
TRANSFER_ARCHIVE_SHA256_OK
IMAGE_TRANSFER_AND_RECEIVER_CHECKS_OK
```

**PASS — restricted receiver transfer and in-band validation:** This indicates source archive re-checked for exact size and SHA-256 and the receiving forced-command script accepted the streamed bytes, checked its own expected length (`907840000`) and SHA-256 (`8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`), then finalized the archive in private staging. The source archive remains on OLD host at `/var/tmp/ccpc-prod-image-export.7blpZWnf/ccpcerp-v16.50.0.tar`. **Independent NEW-host filesystem verification is still pending.** The transfer operation did NOT include `docker load`, Compose startup, MariaDB/site backup transfer, backup restore, active traffic cutover, or unrelated DEVELOPMENT changes.

**NEXT one bounded read-only operator check directly on NEW `ccpcadmin@ccpcerp-prod`:**

```bash
hostnamectl --static
stat -c 'STAGING_MODE=%a STAGING_OWNER=%U' "$HOME/.ccpc-prod-image-transfer-20261106"
stat -c 'ARCHIVE_BYTES=%s ARCHIVE_MODE=%a ARCHIVE_OWNER=%U' "$HOME/.ccpc-prod-image-transfer-20261106/ccpcerp-v16.50.0.tar"
sha256sum "$HOME/.ccpc-prod-image-transfer-20261106/ccpcerp-v16.50.0.tar"
```

Expected NEW host `ccpcerp-prod`, staging mode `700`, archive `907840000` bytes, mode `600`, owner `ccpcadmin` and exact SHA-256 `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`. If anything differs, STOP and investigate without deletion/retransfer. Retire temporary SSH `authorized_keys` permission only after independent verification and safe cleanup planning. The prior temporary access approval covered its revocation after verified transfer, **not** image import.

**Next significant gate after independent verification:** A separate explicit owner approval is required before `sudo docker load` on NEW host, and before separately handling the Nov 5 four-part rehearsal backup. The Nov 5 backup remains an earlier snapshot; never cut over using it in place of unaccounted later financial transactions without a separately reviewed consistent final migration/reconciliation plan.

## OLD-TO-NEW RESTRICTED SSH RECEIVER PROBE PASSED — 2026-11-06

**Owner-run from OLD `gani@ccpcerpserver` after installing dedicated restricted NEW-host key:** The guarded child-shell probe using the private key `/home/gani/.ssh/id_ed25519_ccpc_prod_image_transfer_20261106`, independently matched ED25519 host key `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`, SSH `StrictHostKeyChecking=yes`, `IdentitiesOnly=yes` and `BatchMode=yes` returned exactly:

```text
TRANSFER_SSH_AUTH_OK
SSH_TRANSFER_PROBE_PASS
```

**PASS — restricted transfer login probe:** NEW forced receiver accepted the authorized OLD transfer identity and returned its expected `probe` marker. This is **not** an image-transfer success or proof of destination archive integrity. OLD root-private source archive still resides at `/var/tmp/ccpc-prod-image-export.7blpZWnf/ccpcerp-v16.50.0.tar`; **907840000 bytes**, SHA-256 `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`. Owner's earlier scope approves one image-only SSH transfer.

**NEXT single guarded image-only transfer command on OLD `ccpcerpserver`:**

```bash
bash <<'EOF'
set -euo pipefail
umask 077

if [ "$(hostnamectl --static)" != "ccpcerpserver" ]; then
  echo 'STOP: wrong source host'; exit 1
fi

archive='/var/tmp/ccpc-prod-image-export.7blpZWnf/ccpcerp-v16.50.0.tar'
key="$HOME/.ssh/id_ed25519_ccpc_prod_image_transfer_20261106"
expected_host_fp='SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c'
expected_archive_sha='8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009'

if [ ! -f "$key" ]; then
  echo 'STOP: temporary transfer key missing'; exit 1
fi

sudo -v
size="$(sudo -n stat -c '%s' "$archive")"
sha="$(sudo -n sha256sum "$archive" | awk '{print $1}')"
if [ "$size" != '907840000' ] || [ "$sha" != "$expected_archive_sha" ]; then
  echo 'STOP: source archive changed; no transfer'; exit 1
fi

scanned="$(ssh-keyscan -T 5 -t ed25519 192.168.50.186 2>/dev/null)"
host_fp="$(printf '%s\n' "$scanned" | ssh-keygen -lf - | awk '{print $2}')"
if [ "$host_fp" != "$expected_host_fp" ]; then
  echo 'STOP: destination host fingerprint mismatch'; exit 1
fi

kh="$(mktemp)"
trap 'rm -f -- "$kh"' EXIT
printf '%s\n' "$scanned" > "$kh"
chmod 600 "$kh"

echo 'BEGIN_APPROVED_IMAGE_ONLY_TRANSFER'
if sudo -n cat -- "$archive" | ssh -T -i "$key" \
  -o IdentitiesOnly=yes -o BatchMode=yes \
  -o PreferredAuthentications=publickey -o PasswordAuthentication=no \
  -o KbdInteractiveAuthentication=no -o StrictHostKeyChecking=yes \
  -o HostKeyAlgorithms=ssh-ed25519 -o UserKnownHostsFile="$kh" \
  -o ConnectTimeout=8 -o ServerAliveInterval=15 -o ServerAliveCountMax=4 \
  ccpcadmin@192.168.50.186 receive-image; then
  echo 'IMAGE_TRANSFER_AND_RECEIVER_CHECKS_OK'
else
  echo 'STOP: image stream failed or receiver rejected archive; do not retry blindly'
  exit 1
fi
EOF
```

This script's `set -euo pipefail` is **inside a child Bash**, not in the operator's interactive terminal. It verifies source host, root-private source file size and SHA-256, authenticates target SSH host key out-of-band, and streams the exact archive into a NEW receive-only forced command. The receiver independently checks exact 907840000-byte size and SHA-256 and prints `TRANSFER_ARCHIVE_SHA256_OK` only upon success. **Never assume successful transfer without both receiver marker and local completion marker.** A failed/partial copy is to be preserved for investigation; do not re-run automatically (destination refuses existing `.partial` or final path). No `docker load`, Compose run, DB import, secret handling, or cutover; source archive preserved. Next verify destination archive independently on NEW host before considering temporary access revocation and any separately approved image import.

## NEW-HOST TEMPORARY RECEIVER SETUP REPORTED SUCCESS — 2026-11-06

**Owner-run authorized operation on NEW `ccpcadmin@ccpcerp-prod`:** The bounded `bash <<'INNER'` setup command created the dedicated `~/.ccpc-prod-image-transfer-20261106` protected receiver location/helper, and appended one restricted `authorized_keys` entry for the newly created OLD source public key. Owner reported:

```text
INNER'RECEIVER_STAGING_READY'RIZED'trict,command="/home/ccpcadmin/.ccpc-prod-image-transfer-20261106/receive-image.sh" %s\n' "$pub" >> "$auth"
TEMP_TRANSFER_KEY_AUTHORIZED
RECEIVER_STAGING_READY
```

**Status:** The two expected success markers appeared, indicating the setup script reached its completion. The **preceding terminal echo was visibly garbled**, so do not yet independently claim the forced-command implementation, file content, owner-only access or login authorization is verified. No image bytes have been transferred, and no `docker load`, Compose startup, DB/site restore or cutover has occurred. The receiver should allow `probe` without sending bytes, and `receive-image` only after verifying the fixed 907,840,000-byte archive and its SHA-256.

**NEXT operator step — safe authenticated probe only from OLD `gani@ccpcerpserver`**, in a bounded child shell. The script re-checks the independently measured NEW ED25519 SSH host fingerprint before pinning the presented public key in a temporary `0600` known-hosts file; explicitly selects only the new transfer private key, disables interactive login prompting and requests only `probe` on the restricted key:

```bash
bash <<'EOF'
expected='SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c'
key="$HOME/.ssh/id_ed25519_ccpc_prod_image_transfer_20261106"
if [ ! -f "$key" ]; then
  echo 'STOP: temporary transfer key missing'
else
  scanned="$(ssh-keyscan -T 5 -t ed25519 192.168.50.186 2>/dev/null)"
  fingerprint="$(printf '%s\n' "$scanned" | ssh-keygen -lf - 2>/dev/null | awk '{print $2}')"
  if [ "$fingerprint" != "$expected" ]; then
    echo 'STOP: destination SSH host fingerprint mismatch'
  else
    kh="$(mktemp)"
    chmod 600 "$kh"
    printf '%s\n' "$scanned" > "$kh"
    if ssh -T -i "$key" -o IdentitiesOnly=yes -o BatchMode=yes \
      -o PreferredAuthentications=publickey -o PasswordAuthentication=no \
      -o KbdInteractiveAuthentication=no -o StrictHostKeyChecking=yes \
      -o HostKeyAlgorithms=ssh-ed25519 -o UserKnownHostsFile="$kh" \
      -o ConnectTimeout=8 ccpcadmin@192.168.50.186 probe; then
      echo SSH_TRANSFER_PROBE_PASS
    else
      echo SSH_TRANSFER_PROBE_FAILED
    fi
    rm -f -- "$kh"
  fi
fi
EOF
```

Expected two results: `TRANSFER_SSH_AUTH_OK` (forced command printed by NEW receiver) and `SSH_TRANSFER_PROBE_PASS` (OLD client). On anything else, **STOP and inspect** without pasting private key. Child-shell errors must **not** terminate the interactive SSH terminal. This step may create/delete only its own temporary known_hosts pin, and does not touch Docker or transmit the image. Existing backup SSH key remains untouched.

## OLD SOURCE ADDRESS AND PUBLIC KEY VERIFIED — 2026-11-06

**Owner-run read-only OLD `gani@ccpcerpserver`:** `ip -4 route get 192.168.50.186` resolved `192.168.50.186 dev enp7s0 src 192.168.50.166 uid 1000`. Thus the network path OLD `192.168.50.166` → NEW `192.168.50.186` is the observed source for this transfer. The public half of the newly created temporary key was read from `/home/gani/.ssh/id_ed25519_ccpc_prod_image_transfer_20261106.pub`; its exact key text is:

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJYzObYx7p4c4wOs2zXaikEYu6RCZijmuvsOndUf+mXO ccpc-prod-image-transfer-20261106
```

**Verified:** independently recomputing SHA-256 over its decoded SSH public-key blob yields the same key fingerprint as user-reported `ssh-keygen`: `SHA256:DQoxNuufbGbgD1KfvlmeZOYk40DaMXgUsI3MnzDBgf8`. This is a **public** key, not a credential or private key. The source's scheduled-backup key remains untouched. No NEW authorized-keys change or image transfer yet.

**NEXT one separately approved NEW-host step** (the owner already explicitly approved creating/installing a restricted dedicated transfer key): On `ccpcadmin@ccpcerp-prod` (guard hostname and user), create a unique `0700` private staging directory `/home/ccpcadmin/.ccpc-prod-image-transfer-20261106` and a `0700` receive-only helper script there; append exactly one new `authorized_keys` entry for **this** ED25519 public key, with `from="192.168.50.166",restrict,command="/home/ccpcadmin/.ccpc-prod-image-transfer-20261106/receive-image.sh"`. Do not overwrite existing authorized keys or enable shell/forwarding. Enforce no-clobber transfer and only accept a `receive-image` SSH command that streams at most `907840001` bytes, requires exact `907840000` bytes and SHA-256 `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009` before moving the private `.partial` file to `ccpcerp-v16.50.0.tar`; additionally allow a `probe` command that prints `TRANSFER_SSH_AUTH_OK` without modifying files. Reject all other SSH commands. The helper limits the one approved transfer and its temporary authentication to this exact object.

**Security and scope:** New-host authorization is an expressly approved access-control change, while image upload itself is separately approved. Existing `authorized_keys` entries and OLD backup key must not be removed/changed. The destination NEW `ccpcerp-prod` ED25519 host key remains pinned to `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`. Initial setup command must run in a bounded child shell, not `set -e` in an interactive login. No copy, Docker load, Compose run, DB/site restoration, cutover, or production data modifications under this specific setup step. Verify actual setup output before attempting the OLD-host SSH probe and file transfer.

## TEMPORARY IMAGE TRANSFER PUBLIC KEY CREATED — 2026-11-06

**Owner's actual OLD `gani@ccpcerpserver` output from approved child-shell `ssh-keygen` operation:**

```text
TEMP_TRANSFER_KEY_CREATED
PUBLIC_KEY_FILE=/home/gani/.ssh/id_ed25519_ccpc_prod_image_transfer_20261106.pub
256 SHA256:DQoxNuufbGbgD1KfvlmeZOYk40DaMXgUsI3MnzDBgf8 ccpc-prod-image-transfer-20261106 (ED25519)
```

**PASS — source-side temporary key created.** The `ssh-keygen` output is consistent with the uniquely named temporary key; the matching public key's fingerprint was displayed. No private key contents were shared. The existing `id_ed25519_ccpc_backup` key is intentionally untouched. **NEW host has not yet authorized this new key**, and no image transfer, `docker load`, ERPNext restore, PROD/DEV change or cutover has occurred.

**NEXT one read-only OLD-host step — capture public half and source IPv4 route:** 

```bash
ip -4 route get 192.168.50.186
cat "$HOME/.ssh/id_ed25519_ccpc_prod_image_transfer_20261106.pub"
```

The first command reveals the actual old-host source address chosen by routing to new host. The second prints **only the public key**; it is safe to provide this one-line public half for restricted `authorized_keys` provisioning. **Never print the matching file without `.pub`**. Before installing authorization on NEW `ccpcadmin`, confirm public key fingerprint matches `SHA256:DQoxNuufbGbgD1KfvlmeZOYk40DaMXgUsI3MnzDBgf8`, restrict to the observed source IP with `from="..."` plus `restrict` where supported, do not overwrite existing `authorized_keys`, and preserve strict NEW host fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`. This is the separately authorized temporary transfer-access setup; retire after checksum-matched transfer.

## OWNER AUTHORIZED DEDICATED TEMPORARY TRANSFER SSH KEY — 2026-11-06

**Owner explicitly said "Approved"** after review of the failed default SSH public-key authentication from OLD `gani@ccpcerpserver` to NEW `ccpcadmin@ccpcerp-prod`. Approval covers (1) creating a **dedicated, temporary** ED25519 SSH transfer key on OLD `ccpcerpserver`, (2) installing **only the public half** as a restricted authorized key for `ccpcadmin` on the NEW dedicated host, and (3) revoking the temporary authorization after the image-only transfer has been verified. The existing `id_ed25519_ccpc_backup` key and scheduled backups remain untouched. No permanent unrestricted login, production Docker/service changes, image import, database restore or cutover is authorized.

**First approved operator step only, on OLD `gani@ccpcerpserver`:** Create a new uniquely named key without overwriting anything; do not print or submit its private contents.

```bash
bash <<'EOF'
key="$HOME/.ssh/id_ed25519_ccpc_prod_image_transfer_20261106"
if [ -e "$key" ] || [ -e "$key.pub" ]; then
  echo "STOP: transfer key path already exists; no key created"
elif [ ! -d "$HOME/.ssh" ]; then
  echo "STOP: ~/.ssh directory missing; no key created"
else
  umask 077
  if ssh-keygen -q -t ed25519 -N '' -C 'ccpc-prod-image-transfer-20261106' -f "$key"; then
    chmod 600 "$key"
    chmod 644 "$key.pub"
    echo "TEMP_TRANSFER_KEY_CREATED"
    echo "PUBLIC_KEY_FILE=$key.pub"
    ssh-keygen -lf "$key.pub"
  else
    echo "STOP: key generation failed; check paths before retrying"
  fi
fi
EOF
```

**Security scope:** Passwordless **temporary** private key permits scripted SSH transfer without exposing a passphrase; it is sensitive and must remain `0600`, never be pasted into ChatGPT, logged or committed. This key will not be auto-selected by normal SSH defaults; explicitly target it with `-i` and `IdentitiesOnly=yes` only for the approved transfer. A later operator-controlled NEW-host `authorized_keys` edit must use at least no-agent/no-X11/no-port-forward/no-PTY restrictions and preferably a confirmed OLD-host source-IP or forced command. Confirm the key fingerprint, exact public key, source IP and the trusted NEW host-key fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c` before installing authorization. **Do not install access or copy the image in this first step.** The 907840000-byte protected Docker image archive remains only on OLD source.

**Execution still pending:** Owner approval has been recorded; no new SSH key or `authorized_keys` change has been verified in chat.

## EFFECTIVE OLD-TO-NEW SSH IDENTITIES — 2026-11-06

**Owner-run read-only on OLD `gani@ccpcerpserver`:**

```text
ssh -G -o BatchMode=yes ccpcadmin@192.168.50.186 | awk '$1=="identityfile" || $1=="identitiesonly" {print}'
identitiesonly no
identityfile ~/.ssh/id_rsa
identityfile ~/.ssh/id_ecdsa
identityfile ~/.ssh/id_ecdsa_sk
identityfile ~/.ssh/id_ed25519
identityfile ~/.ssh/id_ed25519_sk
```

**Interpretation:** Configured/default SSH identities for this connection **do not include** the one owner-reported named backup public key `id_ed25519_ccpc_backup.pub`. `identitiesonly no` also allows identities offered by an SSH agent; this output does **not** establish which private keys exist or precisely which one was offered. The observed `Permission denied (publickey)` remains the only actual authenticated-login test result. Keep backup authentication entirely unchanged.

**Recommended owner decision — separate authorization for SSH key/access-control change:** Provision a dedicated temporary ED25519 transfer key on OLD host with restrictive file permissions, install only its public half into NEW `ccpcadmin`'s `authorized_keys` with restrictive options (no agent/X11/port forwarding, no PTY, and source-IP restriction if confirmed) and remove that new authorization after verifying the already approved image-only transfer. This changes new-host SSH account authorization and should be **explicitly approved** before creating keys or editing `authorized_keys`. Any temporary private key must never be pasted, printed or committed. Use the independently observed NEW-server ED25519 host fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c` and keep host-key checks strict. Select file-copy direction and privileges carefully because existing exported OLD archive is root-only `0600` in root-only `0700` staging; do not weaken its permissions or copy onto a public intermediate location. A forced-command restriction or dedicated receive-only account can be considered when authoring the exact controlled transfer sequence.

**Approval status:** User has approved **secure image-only transfer**, but has **not yet explicitly authorized new cross-host SSH key creation/authorization changes**. Next conversational step is to request this scoped approval. No image bytes have been sent, loaded, restored, or started; no production cutover authorized.

## EXISTING OLD-HOST SSH PUBLIC KEY INVENTORY — 2026-11-06

**Owner ran read-only filenames-only key inventory** under `gani@ccpcerpserver` using `find "$HOME/.ssh" -maxdepth 1 -type f -name '*.pub' -printf '%f\\n' 2>/dev/null`. Output was exactly:

```text
id_ed25519_ccpc_backup.pub
```

This is **not** evidence that the backup key should be reused for the dedicated-production transfer, that the corresponding private key exists, or that the NEW `ccpcadmin` account authorizes it. The custom filename suggests backup-specific purpose, and SSH may not auto-offer it absent matching configuration. Do **not** read/publish the private key, automatically copy the public key into `authorized_keys`, replace the backup key or change existing backup authentication.

**Next ONE read-only command on OLD host `gani@ccpcerpserver`** to display only effective authentication key filename choices (no private key content or SSH login attempts):

```bash
ssh -G -o BatchMode=yes ccpcadmin@192.168.50.186 | awk '$1=="identityfile" || $1=="identitiesonly" {print}'
```

Interpret carefully: `ssh -G` shows configuration, **not** proof that files exist, keys are offered or a login will succeed. If only default keys show, the backup-named key was not selected by default. Choose a minimally scoped, dedicated transfer authentication path after reviewing results; adding a key to the NEW host changes SSH access policy and needs separate explicit approval. The user has already approved transfer of the **image archive only**, not unrestricted SSH account access changes or loading/running Docker on the NEW host. The source archive remains protected at `/var/tmp/ccpc-prod-image-export.7blpZWnf/ccpcerp-v16.50.0.tar`, with source SHA-256 `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`. No transfer has occurred.

## SAFE RECHECK AFTER TERMINAL EXIT — SSH AUTH REJECTED, 2026-11-06

**Owner successfully reconnected to OLD `gani@ccpcerpserver`** and ran `hostnamectl --static` → `ccpcerpserver`. A subsequent SSH login test was correctly run inside a child `bash <<'EOF'` shell, preserving their interactive terminal, with host fingerprint checked against independently verified NEW-host key `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`, `StrictHostKeyChecking=yes`, `BatchMode=yes`, ED25519-only server algorithm and `PreferredAuthentications=publickey`.

**Actual owner output:**

```text
ccpcadmin@192.168.50.186: Permission denied (publickey).
SSH_AUTH_NOT_AVAILABLE
```

**Result:** Network and previously matched host fingerprint were sufficient to reach the expected SSH service; **authentication from OLD user `gani` to NEW user `ccpcadmin` is not currently authorized/working.** No tar file sent; original archive remains on OLD and no destination archive known. The test had no Docker, app, database or container operation. This is **not** a reason to lower host-key checking, use SSH passwords, or change services.

**NEXT single read-only OLD-host step:** inventory **filenames only** for existing SSH public key files (no private keys or key contents):

```bash
find "$HOME/.ssh" -maxdepth 1 -type f -name '*.pub' -printf '%f\n' 2>/dev/null
```

If no keys are present, report no output and stop; an **explicitly authorized dedicated transfer key** can be planned with minimal permissions. If keys are present, assess whether an existing key is suitable for this one-way transfer rather than exposing private credentials or automatically adding long-lived trust. Provisioning destination `authorized_keys` changes access control and needs a clear, scoped approval; it is not implied by a failed login. Preserve the SSH fingerprint, no `StrictHostKeyChecking=no` and no public/writable archive copies. The previously approved image-only transfer is pending, not failed or completed.

## TERMINAL SESSION EXITED DURING SSH AUTHENTICATION PREFLIGHT — 2026-11-06

**Owner reported:** "The Terminal exited after runnibg the last code", immediately after running the assistant-supplied OLD-host SSH-auth test. No stdout/stderr of that test was shared, so **we do not know if the attempted SSH authentication succeeded, failed, or timed out**.

**Operator safety correction:** The previous instruction placed `set -euo pipefail` and an explicit `exit 1` directly into an **interactive** shell, where a failed `ssh-keyscan`, mismatched fingerprint, or unsuccessful `ssh` can terminate that interactive shell and close the SSH terminal. This was an unsafe presentation error in the guidance, **not evidence of ERPNext/Docker service shutdown**. The script did not include image transfer or Docker modification. It may have created a temporary host-key file which, if the trap ran, was removed on exit; do not assume the exact side effects without output.

**IMMEDIATE NEXT STEP (one read-only command, OLD host):** Reconnect normally to `gani@ccpcerpserver` and run **only** `hostnamectl --static`. Expected output `ccpcerpserver`. Do not repeat the earlier interactive `set -e` block. Continue only after OLD-host identity is reconfirmed.

**For any later repeat of this authentication test:** Enclose all error-handling steps in a **separate child** `bash <<'EOF' ... EOF` process so errors exit only the child shell, never the operator's interactive terminal. Print an explicit verdict and preserve the trusted destination ED25519 fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`; stop on mismatch. Do not auto-accept unknown host keys, lower strict checking, run unapproved transfers, reveal secrets, or configure cross-host keys without reviewed need.

**Transfer state:** Previously approved secure **image-only** SSH transfer is still **not confirmed executed**. Original root-private OLD-host archive remains the planned source and has full verified creation output; nothing has been shown to prove destination bytes exist. No approval for image import/restore/cutover.

## OLD-TO-NEW SSH NETWORK FINGERPRINT MATCH — 2026-11-06

**Owner-run read-only on OLD `gani@ccpcerpserver`:**

```text
set -o pipefail
ssh-keyscan -T 5 -t ed25519 192.168.50.186 2>/dev/null | ssh-keygen -lf -
256 SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c 192.168.50.186 (ED25519)
```

**PASS**: Network-presented destination ED25519 SSH fingerprint exactly matches the fingerprint independently obtained directly from NEW `ccpcerp-prod`: `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`. The scan does not by itself prove OLD `gani` has authorized login access on NEW `ccpcadmin`; **no authenticated login, source export transfer or destination file creation has yet been confirmed**. SSH transfer was separately approved by owner, but other operations remain excluded.

**HISTORICAL TEST INVALIDATED FOR INTERACTIVE USE (2026-11-06):** The earlier `set -euo pipefail` / `exit 1` snippet that was run directly in the user's interactive shell caused an unexpected terminal exit or coincided with it. **Do not reuse that syntax at the interactive prompt.** The operator must first reconnect to OLD `ccpcerpserver` and confirm `hostnamectl --static`, as stated in the incident section above. Any retry must run inside a bounded child `bash` process with explicit output and verified host key. No SSH success yet reported.

## DESTINATION SSH PUBLIC HOST KEY DIRECTLY VERIFIED — 2026-11-06

**Owner-run read-only directly on NEW `ccpcadmin@ccpcerp-prod`:**

```text
hostnamectl --static
ccpcerp-prod
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
256 SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c root@ccpcerp-prod (ED25519)
```

**PASS (direct-host identity observation):** New host name matches expected `ccpcerp-prod` and a server ED25519 **public** host-key fingerprint was measured locally. This fingerprints the specific currently configured host key, not the network presentation yet. Host-key trust is **not** installed and OLD-to-NEW authentication is **not** established. No transfer made.

**NEXT one OLD-host read-only command** to obtain the key presented by NEW host's SSH listener over the LAN and compare it to the independently measured local fingerprint, without automatically accepting it:

```bash
set -o pipefail
ssh-keyscan -T 5 -t ed25519 192.168.50.186 2>/dev/null | ssh-keygen -lf -
```

Expected fingerprint for `192.168.50.186`: `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`. **STOP on mismatch or scan failure.** `ssh-keyscan` alone is not an authenticated trust source; its use here is only comparison against the independently verified out-of-band public key. Do not use `StrictHostKeyChecking=no`, unauthenticated `ssh-keyscan >> ~/.ssh/known_hosts`, loose source permissions or plaintext transfers. After matching, determine an approved secure SSH authentication and root-restricted destination staging procedure, without transferring yet. Prior approval covers image-only SSH transfer; no image import, restore, Compose or cutover.

## OWNER APPROVED SECURE IMAGE-ONLY TRANSFER — 2026-11-06

**Owner explicitly replied "aPPROVED"** to the separately scoped request for a secure, authenticated SSH transfer of **only** the exported existing live PRODUCTION image archive from OLD `ccpcerpserver` to NEW `ccpcerp-prod`, into restricted destination staging, with a destination SHA-256 verification. This is approval for that bounded transfer, **not** for any `docker load`, container startup, Compose deployment, production/site restore, database/config changes, DNS switch, user traffic cutover, deletion or DEV operation.

**Pinned source artifact (already locally exported, not yet transferred):**

- OLD host root-private: `/var/tmp/ccpc-prod-image-export.7blpZWnf/ccpcerp-v16.50.0.tar`
- Bytes: `907840000`
- Archive SHA-256: `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`
- Embedded current live image ID: `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`

**Preflight before any bytes leave OLD host:** Verify SSH host identity and fingerprint of NEW dedicated host; confirm a trusted working SSH authentication path between source and destination. Do not disable StrictHostKeyChecking, automatically trust an unauthenticated `ssh-keyscan` result or expose the archive with world/group-readable permissions. Old admin `gani` and new admin `ccpcadmin` are distinct accounts; do not assume keys or cross-host sudo grants are already configured. Prefer minimal private staging on both sides, no sensitive content to terminal/GitHub, and fail safely on existing targets or interrupted streams. Record source/destination host identities and check the exact destination hash before accepting success. Avoid accidental overwrites and never remove the source archive without a separate retention decision.

**Next single read-only operator step on NEW `ccpcerp-prod`:**

```bash
hostnamectl --static
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Expected hostname `ccpcerp-prod`. The second command displays the new host's **public** ED25519 server-key fingerprint (not a private key). Record it to authenticate the host key seen from OLD before SSH trust or copying. If the public key is missing or unexpected, stop and inspect safely. No transfer, file change or services have yet been run under this fresh approval.

## ACTUAL OLD-HOST LIVE IMAGE EXPORT COMPLETED — 2026-11-06

**Owner-run output from the previously authorized `docker save` on OLD live `gani@ccpcerpserver`:**

```text
Exporting verified production image to protected location: /var/tmp/ccpc-prod-image-export.7blpZWnf
SOURCE_IMAGE_ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8
ARCHIVE_PATH=/var/tmp/ccpc-prod-image-export.7blpZWnf/ccpcerp-v16.50.0.tar
ARCHIVE_BYTES=907840000
8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009  /var/tmp/ccpc-prod-image-export.7blpZWnf/ccpcerp-v16.50.0.tar
```

**PASS — source export checkpoint:** The guarded script completed and printed the expected source image identity, a nonempty final archive (~866 MiB) and full SHA-256 digest. The script used root's `umask 077`, a unique `mktemp -d` private directory, `.partial` staging and a final archive `chmod 600`. This is evidence of the command's reported successful completion; **do not infer destination integrity or independent on-disk permissions verification** yet. No transfer, import, Compose startup, database/site restoration, scheduler/email activation or cutover has occurred in this work.

**Next separate approval gate — encrypted transfer of this archive ONLY:** Propose copying the exact protected tar through authenticated SSH to a new root/private staging location on dedicated `ccpcerp-prod` (LAN address previously recorded `192.168.50.186`), with strict host-key verification and no weak/disabled checking. Avoid exposing the protected source via world-readable temporary files, `chmod 777`, public shares, GitHub, or chat uploads. Stage only under root-owned `0700` directory with `0600` output and perform SHA-256 comparison against `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009` before accepting success. Check actual old->new or new->old SSH reachability, key availability and known-host fingerprint without weakening SSH security; do not guess successful connectivity. An authenticated encrypted stream via SSH from OLD root-readable image archive is permissible *only if separately authorized*, and no `docker load` or Docker daemon write should accompany this transfer. Avoid overwriting any pre-existing destination file, stop on checksum mismatch and retain source archive unchanged.

**Current approval state:** User's prior "aPPROVED" authorized the **old-host local export only**. **It did not approve copying the archive to another machine**. The user should be asked separately for consent to a secure, image-only transfer. Independently, the Nov 5 backup is for non-live rehearsal; financial transactions after that backup remain protected on old live PRODUCTION.

## OWNER APPROVED ONE OLD-HOST LOCAL IMAGE EXPORT — 2026-11-06

**Explicit owner approval received** after all six PRODUCTION containers matched the image ID, via message: **"aPPROVED"**, in direct response to scoped request for **one protected local `docker save` archive of existing `ccpcerp:v16.50.0` on OLD `ccpcerpserver` only**. Approval covers local staging writes, image export and source archive checksum/size; **not** secure transfer, image import, new-host stack startup, database/site restore, PRODUCTION or DEVELOPMENT runtime changes, or cutover. Owner must execute commands through SSH (ChatGPT has no host-SSH access). **Approval recorded; execution/output not yet verified.**

**Single guarded OLD-host operator step, after owner approval:**

```bash
sudo bash <<'EOF'
set -euo pipefail
umask 077

expected='sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8'
actual="$(docker image inspect --format '{{.Id}}' ccpcerp:v16.50.0)"
if [ "$actual" != "$expected" ]; then
  echo "STOP: production image ID changed; no export performed" >&2
  exit 1
fi

stage="$(mktemp -d /var/tmp/ccpc-prod-image-export.XXXXXXXX)"
archive="$stage/ccpcerp-v16.50.0.tar"
echo "Exporting verified production image to protected location: $stage"
docker image save --output "$archive.partial" ccpcerp:v16.50.0
test -s "$archive.partial"
mv -- "$archive.partial" "$archive"
chmod 600 "$archive"

printf 'SOURCE_IMAGE_ID=%s\n' "$actual"
printf 'ARCHIVE_PATH=%s\n' "$archive"
printf 'ARCHIVE_BYTES=%s\n' "$(stat -c %s "$archive")"
sha256sum "$archive"
EOF
```

**Expected safeguards:** `mktemp -d` unique directory is created by root with `0700` in local `/var/tmp`, `umask 077` limits file permissions, only the immutable-ID matched tag is exported, `.partial` is not promoted to final archive on failed save, final image archive is chmod `0600`, source and exported artifact sizes/hash printed for review. If any operation errors, **STOP**, preserve output and any partial archive; do not retry blindly or delete source data. `docker save` reads image layers and causes disk/CPU I/O and a local write, but should not touch running containers. The archive may embed sensitive deployment content; never attach it publicly, push to GitHub, share checksum together with secrets, or put it in the automatic NAS-retention tree.

**Following gate:** Wait for operator's actual archive path, byte count and SHA-256 checksum, then validate status and prepare a separate approval for secure transfer to the isolated new host. Preserve Nov 5 four-artifact backup checksums separately and do not substitute the Nov 5 rehearsal snapshot for later live transactions without a separately approved final reconciliation/cutover plan.

## ALL SIX RUNNING LIVE PROD APP IMAGE IDS MATCH — 2026-11-06

**Owner-run read-only `docker inspect` on OLD live `ccpcerpserver`:** All six running PRODUCTION app containers, `frappe_docker-frontend-1`, `frappe_docker-backend-1`, `frappe_docker-queue-short-1`, `frappe_docker-queue-long-1`, `frappe_docker-websocket-1`, and `frappe_docker-scheduler-1`, returned **exactly** `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`. **PASS:** a single existing `ccpcerp:v16.50.0` Docker image covers every application service, not just the backend; separate MariaDB and Redis are independent standard images, and their live data/config remain separately required.

**Ready for the next consent gate — not yet authorized:** Ask owner for **explicit, narrowly scoped approval** to create **one protected local `docker save` image archive on OLD `ccpcerpserver` only**. Intended safe procedure, after approval: re-check the tag still resolves to the verified immutable image ID; allocate a unique root-owned `0700` scratch directory on the OLD local filesystem outside NAS/backup retention, using restrictive umask and rejecting collisions; `docker save` only `ccpcerp:v16.50.0`; calculate/archive SHA-256 and actual bytes; leave source image, all running containers, DB, site and backup files untouched; report archive path and checksum without displaying secrets. The operation has bounded local write/storage/CPU/I/O effects and is not a zero-impact read-only check, so it requires owner approval. **Do not perform archive creation, SCP/rsync transfer, image import, Docker Compose startup, restore or go-live merely on this checkpoint.**

**Separation:** The selected November 5, 2026 four-artifact backup was checksum-checked/format-checked and is for **isolated non-live restoration rehearsal** only; post-snapshot transactions must be reconciled and a fresh final consistent backup or an explicit business decision required before any go-live. Never modify old production or DEVELOPMENT while preparing the dedicated server.

## OLD HOST STAGING CAPACITY VERIFIED — 2026-11-06

**Owner-run read-only on OLD `ccpcerpserver`:** `df -h /var/lib/docker /home/gani` reported the same root filesystem `/dev/nvme0n1p2` for both paths: **915G total, 182G used, 687G available, 21% utilization**. These are two views of **one** filesystem, not 1,374G of free space. The NEW `ccpcerp-prod` host separately reported **740G free** on its root logical volume. Both appear to have ample headroom for the approximately 866 MiB source application image, but the actual `docker save` archive, temporary copies, loaded layers and restore footprint remain unmeasured.

**NEXT single OLD-host read-only identity check, all six PRODUCTION application containers:** Confirm their immutable image IDs before proposing an image archive export:

```bash
sudo docker inspect --format '{{.Name}} {{.Image}}' \
  frappe_docker-frontend-1 \
  frappe_docker-backend-1 \
  frappe_docker-queue-short-1 \
  frappe_docker-queue-long-1 \
  frappe_docker-websocket-1 \
  frappe_docker-scheduler-1
```

All six outputs **should match** the already verified backend/container-and-tag image ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`. If not, STOP; do not export a single image assuming uniform source. Only after this read-only step should the operator be asked for **separate approval** of a bounded archive export. No file transfers, image writes, Docker restarts, database changes, or new-host deployment authorized or performed. The Nov 5 four-file source backup is selected for isolated rehearsal only; post-snapshot live transactions remain protected.

## OLD PRODUCTION IMAGE SIZE VERIFIED — 2026-11-06

**Owner-run read-only on OLD `gani@ccpcerpserver`:** `sudo docker image inspect ccpcerp:v16.50.0 --format 'source_image_bytes={{.Size}}'` returned `source_image_bytes=907815909`, about **866 MiB** (0.908 GB decimal). This is the image identified by the previously verified live backend image ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`. The new dedicated host has `740G` free on its single shared root filesystem as last reported.

**Scope:** Image inspection did not write or restart any container. Docker's image `.Size` is **not** a measured `docker save` archive size, and it does not cover the site/database restore, free space on OLD host or any staging overhead. The exact original image is still to be preserved, without a new build from DEVELOPMENT.

**NEXT single read-only operator step, OLD host `ccpcerpserver`:**

```bash
df -h /var/lib/docker /home/gani
```

This confirms actual filesystem headroom for a protected, separately approved *local image export*, without placing export files in the old NAS backup-retention tree or touching active Docker objects. After old-host capacity and the remaining application-container image IDs are verified, propose one bounded export/staging operation for explicit approval; create no archive or transfer yet. The selected Nov 5 backup remains a rehearsal snapshot, not final cutover data.

## DEDICATED HOST DISK SPACE VERIFIED — 2026-11-06

**Owner-run read-only on NEW `ccpcadmin@ccpcerp-prod`:** `df -h / /var/lib/docker /home/ccpcadmin` showed each path on the **same** device `/dev/mapper/ubuntu--vg-ubuntu--lv`, filesystem size `787G`, used `7.1G`, available `740G`, utilization `1%`. **PASS — substantial free space currently available**. These three rows report one shared filesystem, **not three separate 740G reserves**. No allocation or transfer was performed.

This observation alone does **not** prove final capacity for a Docker image archive and loaded layers, database and file staging, restored volumes, logs, temporary duplication, backup and rollback. Do not touch either host's existing Docker/project resources or storage permissions.

**NEXT one read-only OLD-host command** to size the exact already verified `ccpcerp:v16.50.0` image before specifying safe transfer paths:

```bash
sudo docker image inspect ccpcerp:v16.50.0 --format 'source_image_bytes={{.Size}}'
```

Docker's reported image size is **not necessarily the size of a `docker save` archive**, but it provides a useful sizing baseline. Actual image export, transfer, import, restored stack and use of old production secrets remain separately approval-gated. November 5 source snapshot remains the owner-selected **rehearsal** backup, not a final-write-fenced cutover snapshot.

## NOV 5 SOURCE SHA-256 VALUES RECORDED — 2026-11-06

**Owner-run read-only checksums from OLD `ccpcerpserver`:** `sha256sum` completed on the exact four files selected for the isolated November 5 migration rehearsal. These are source-file baselines (not after-transfer verification, not a restore test), and the source NAS artifacts remain unchanged.

```text
8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87  20261105_020001-ccpcerp_local-database.sql.gz
200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6  20261105_020001-ccpcerp_local-files.tar
60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf  20261105_020001-ccpcerp_local-private-files.tar
b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b  20261105_020001-ccpcerp_local-site_config_backup.json
```

**Next migration preflight (read-only NEW host):** Confirm free capacity on intended new-host root/Docker/home filesystems before any image or backup staging:

```bash
df -h / /var/lib/docker /home/ccpcadmin
```

Do not assume enough capacity for the exact Docker image archive, loaded layers, database restoration and rollback until full image size and planned transfer staging are assessed. All actual file transfers, `docker save/load`, credentials provisioning, Compose deployment, database/file restoration, and live cutover remain separate explicit execution approvals. The November 5 backup is **rehearsal data only**; future business writes are preserved on old PRODUCTION and need a final reconciled migration plan.

## FOUR FORMAT CHECKS PASS — OWNER-SELECTED NOV 5 SNAPSHOT, 2026-11-06

**Owner-run exact Nov 5 file-format verification on OLD `ccpcerpserver`:** The previously supplied read-only script tested the compressed database with `gzip -t`, both public/private TAR archives with `tar -tf >/dev/null`, and the site-configuration file with `python3 -m json.tool >/dev/null`. Owner reported four success markers, in order:

```text
DATABASE_GZIP_OK
PUBLIC_FILES_TAR_OK
PRIVATE_FILES_TAR_OK
SITE_CONFIG_JSON_OK
```

**PASS — narrow:** The chosen `2026-11-05_02-00` set contains four nonempty files and these format-level checks succeeded. This is **not** evidence that all expected business records or attachments were captured, that the backup is self-consistent, or that a Frappe restore will succeed. Never print site-config JSON (it may contain secrets), extract to the active production server, or delete an existing restore point.

**NEXT one read-only operator check on OLD host only — capture exact source file SHA-256 digests prior to any approved transfer:**

```bash
sudo bash -c '
set -e
cd /mnt/erpnext_backups/2026-11-05_02-00
sha256sum -- \
  20261105_020001-ccpcerp_local-database.sql.gz \
  20261105_020001-ccpcerp_local-files.tar \
  20261105_020001-ccpcerp_local-private-files.tar \
  20261105_020001-ccpcerp_local-site_config_backup.json
'
```

The command only **reads** four named backup artifacts and prints hashes and filenames, not file contents. Keep the source backups unchanged and verify corresponding hashes after a separately approved protected transfer. Check disk capacity, secure archive-handling and preservation of old/current transactions before any `docker save`, file copy, isolated restore or cutover. **Nov 5 is a rehearsal source**; do not replace live current business records with a stale snapshot without a separate, explicit reconciliation/data-loss decision.

## OWNER-SELECTED NOVEMBER 5, 2026 PRODUCTION BACKUP — 2026-11-06

**Owner explicitly directed: "USE NOVEMBER 05, 2026".** The selected **existing live-PRODUCTION** recovery set for the **isolated, non-live migration rehearsal** is:

`/mnt/erpnext_backups/2026-11-05_02-00` on **OLD** `ccpcerpserver`, verified mounted from `//192.168.50.132/erpnext_backups` (`cifs`). This is a *source selection*, not a successful restore, host-copy approval, final cutover authorization, or acceptance of any lost transactions.

**Owner-run read-only inventory:**

| Artifact | Verified filename | Bytes |
| --- | --- | ---: |
| Database | `20261105_020001-ccpcerp_local-database.sql.gz` | 1198839 |
| Public files | `20261105_020001-ccpcerp_local-files.tar` | 10240 |
| Private files | `20261105_020001-ccpcerp_local-private-files.tar` | 20480 |
| Site configuration | `20261105_020001-ccpcerp_local-site_config_backup.json` | 280 |

**Verification status:** Four expected *names* present as nonempty regular files. File integrity, contents, application compatibility, restorability and completeness remain unverified. Small tar archives could be legitimate or contain little/no data; inspect safely rather than assuming completeness. Site configuration may contain passwords/encryption keys; **never display or paste its contents**.

**Freshness/RPO boundary:** A snapshot created 2026-11-05 02:00:01 +08 predates the current 2026-11-06 conversation. Transactions, attachments, user changes and other writes **after** the snapshot will not exist in that restored snapshot. Owner's choice authorizes **using it for preparation/rehearsal**; **do not infer** approval to go live with that older dataset while there may be subsequent transactions. Before cutover, either perform a separately approved final consistent synchronized copy with old writes fenced and reconciliation, or obtain an explicit business-signed data-loss/recovery decision—do not silently drop later entries. Keep old production live and untouched.

**Next bounded read-only step on OLD host:** Test this exact source set's gzip/tar archive structures and site-config JSON syntax without extracting or printing sensitive contents, before any transfer. Preserve the original files; no archive rewriting, database restore, service operation or cleanup.

## OLD PROD NAS DIRECTORY RECENCY CHECK — 2026-11-06

**Owner-provided read-only directory name inventory from OLD live `ccpcerpserver`:** `sudo find /mnt/erpnext_backups -mindepth 1 -maxdepth 1 -type d -name '20??-??-??_??-??' -printf '%f\\n' | LC_ALL=C sort -r | head -n 10` returned:

```text
2026-11-05_02-00
2026-11-04_02-00
2026-11-03_02-00
2026-11-02_02-00
2026-11-01_02-00
2026-10-31_02-00
2026-10-30_02-00
2026-10-29_02-00
2026-10-28_02-00
2026-10-27_02-00
```

**Observation:** Ten consecutive **directory names** indicate periodic NAS publication activity through November 5, 2026. A November 6 02:00 directory is **not present among these ten newest matching directories** despite historical 02:00 daily root cron; this is an **unresolved freshness discrepancy** (may be missed job, changed naming, alternate location, schedule or error). Do not assert a Nov 6 backup failed without cron/log evidence. Directory names alone do **not** prove a complete backup or successful restore.

**NEXT one read-only OLD-host check:** Inspect **file names and sizes only** for the latest shown candidate directory, without opening or copying sensitive contents:

```bash
sudo find /mnt/erpnext_backups/2026-11-05_02-00 -mindepth 1 -maxdepth 1 -type f -printf '%f\t%s bytes\n' | LC_ALL=C sort
```

Look for non-empty compressed SQL database, public file archive, private file archive and site-config backup. After this, investigate missing November 6 backup via sanitized scheduler status/log checks before authorizing a fresh production recovery set, image archive or any restore. Do not run backup script, edit cron, delete backups or change production under this read-only approval.

## LIVE LEGACY NAS MOUNT — VERIFIED 2026-11-06, BACKUP CONTENT PENDING

**Owner-run read-only on OLD `gani@ccpcerpserver`:**

```bash
findmnt --mountpoint /mnt/erpnext_backups --output TARGET,SOURCE,FSTYPE --noheadings || echo NOT_MOUNTED
```

Output: `/mnt/erpnext_backups //192.168.50.132/erpnext_backups cifs`.

**PASS (narrow):** The expected Synology filesystem is actually mounted at the correct host location; it is not merely an empty local directory. This does **not** yet prove share writability, scheduled backups running, recent complete four-artifact backup, immutability, archive integrity or restore success. No backup job or Docker operation performed.

The historical GitHub `recovery.md` documents one completed manual four-artifact backup from September 2, 2026, and a proposed 02:00 daily cron/30-day NAS retention; those are historical records and not proof of present scheduled operation.

**NEXT one read-only operator step on OLD host:** list *names only* of the 10 newest-looking timestamp-formatted backup directories without opening files, changing retention or exposing site data:

```bash
sudo find /mnt/erpnext_backups -mindepth 1 -maxdepth 1 -type d -name '20??-??-??_??-??' -printf '%f\n' | LC_ALL=C sort -r | head -n 10
```

If none appear or dates are stale, stop to diagnose the backup schedule before any migration. If recent directories appear, inspect **exactly one selected run's** file names/sizes and verify four mandatory artifacts in a following controlled read-only step, then plan an explicitly approved fresh consistent migration backup and isolated restore. Do not delete/move/rename existing backups or run the backup script merely to test it.

## LIVE IMAGE BUILD LABELS ABSENT — EXACT-IMAGE MIGRATION PATH, 2026-11-06

**Owner read-only result on old `ccpcerpserver`:** `sudo docker image inspect ccpcerp:v16.50.0 --format 'frappe={{index .Config.Labels "org.ccpc.frappe.sha"}} erpnext={{index .Config.Labels "org.ccpc.erpnext.sha"}} ccpcerp={{index .Config.Labels "org.ccpc.ccpcerp.sha"}} patch={{index .Config.Labels "org.ccpc.erpnext.patch.sha256"}} overlay={{index .Config.Labels "org.ccpc.erpnext.overlay.sha256"}}'` printed `frappe= erpnext= ccpcerp= patch= overlay=`. This specific existing image does **not** expose the queried build-input labels. Their absence is **not** an application failure and does **not** undo the verified container/image ID match.

**Chosen approach:** Do **not** waste migration time guessing Git SHAs or rebuilding `ccpcerp:v16.50.0` from later GitHub source. Treat the already verified running image `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8` as the immutable migration baseline. During a **later separately approved** image-transfer stage, make a protected `docker save` archive of the **existing old-host image**, securely transfer, `docker load` only on the new isolated host, and verify the resulting image ID matches exactly before use. Review archive size/destination/free space, checksums, permissions, secure transfer and recovery. Image export/import is not yet authorized. The application image alone does **not** carry the live MariaDB DB or site volumes/files.

**Move to recovery readiness now:** Old legacy recovery guide `recovery.md` names host path `/mnt/erpnext_backups` and a past NAS source `//192.168.50.132/erpnext_backups`. Older manual backup evidence is historical and cannot certify present backups. Next *single read-only old-host step* checks **exact active mount** without reading backup contents or credentials:

```bash
findmnt --mountpoint /mnt/erpnext_backups --output TARGET,SOURCE,FSTYPE --noheadings || echo NOT_MOUNTED
```

Expected if unchanged is filesystem `cifs` and **exact source** `//192.168.50.132/erpnext_backups`; anything else (including `NOT_MOUNTED`) is a **STOP**, not permission to write backups to a local fallback directory. After mount identification, separately verify recent *complete* four-artifact backup and recovery readiness, then seek explicit approval for a fresh consistent production backup and isolated new-host restore. No current PROD or DEV write has been authorized or performed.

## NO .git IN LIVE IMAGE — EXPECTED BUILD PACKAGING, 2026-11-06

**Observed old live `ccpcerpserver`**: operator executed `sudo docker exec frappe_docker-backend-1 bash -lc 'for app in frappe erpnext ccpcerp; do printf "%s " "$app"; git -C "/home/frappe/frappe-bench/apps/$app" rev-parse HEAD; done'`. Each returned `fatal: not a git repository`; this means that **this in-container Git lookup is unavailable**. It is **not** evidence that installed applications are missing or damaged, and no install/migration/restore should be attempted in response.

**Verified GitHub source explanation (2026-11-06):** The reviewed deployment `images/custom/Containerfile` on `review/dedicated-host-readonly-inventory-2026-10-25` deliberately removes `apps/*/.git` after verifying the builder's expected commits (`find apps -mindepth 1 -path "*/.git" | xargs rm -fr`), then writes build-input OCI image labels `org.ccpc.frappe.sha`, `org.ccpc.erpnext.sha`, `org.ccpc.ccpcerp.sha`, `org.ccpc.erpnext.patch.sha256`, `org.ccpc.erpnext.overlay.sha256`. We **have not yet proven** the old running image was built from this exact reviewed Containerfile; inspect actual immutable image labels to find out. These are **build-time claims** and not a cryptographic signature or independent attestation.

**New next operator step — OLD host read-only image labels only** (safe fixed keys, no environment/secrets dump):

```bash
sudo docker image inspect ccpcerp:v16.50.0 --format 'frappe={{index .Config.Labels "org.ccpc.frappe.sha"}} erpnext={{index .Config.Labels "org.ccpc.erpnext.sha"}} ccpcerp={{index .Config.Labels "org.ccpc.ccpcerp.sha"}} patch={{index .Config.Labels "org.ccpc.erpnext.patch.sha256"}} overlay={{index .Config.Labels "org.ccpc.erpnext.overlay.sha256"}}'
```

If labels are absent (e.g. `<no value>`), stop; use `bench version` or package metadata with a separate reviewed read-only step rather than guessing. Do not run `git init`, `git pull`, build, migrate, or change containers. The already verified running backend image SHA-256 remains the primary source identity.

## VERIFIED RUNNING PROD BACKEND IMAGE SHA-256 — 2026-11-06

**Owner-reported from OLD live `gani@ccpcerpserver`, read-only Docker metadata only.** Commands:

```bash
sudo docker inspect --format 'running_backend_image_id={{.Image}}' frappe_docker-backend-1
sudo docker image inspect ccpcerp:v16.50.0 --format 'tag_image_id={{.Id}} created={{.Created}}'
```

Results:

- Backend container actual image ID: `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`
- Local `ccpcerp:v16.50.0` image ID: **the same** `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`
- Local image created: `2026-09-16T15:55:49.950715082+08:00`
- Outcome: **PASS for backend container/tag identity at observed time**. Does not yet prove other five app containers' immutable IDs, or the inner application Git SHAs/dirty patch state. No Docker files, application data, or containers modified.

**Next operator step (read-only, on OLD `ccpcerpserver` only):**

```bash
sudo docker exec frappe_docker-backend-1 bash -lc 'for app in frappe erpnext ccpcerp; do printf "%s " "$app"; git -C "/home/frappe/frappe-bench/apps/$app" rev-parse HEAD; done'
```

This reads the three application Git commit IDs from the running backend; do not run `bench migrate`, `git pull`, `git reset`, image build, or app installation. The next gate after commits is checking clean/modified source and compatibility, then separately approved complete four-part backup and a non-live restore rehearsal.

## VERIFIED OLD LIVE PRODUCTION CONTAINER INVENTORY — 2026-11-06

**Owner-run, read-only on old host `gani@ccpcerpserver`**: `hostnamectl --static` printed `ccpcerpserver`; `sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'` showed the active live PRODUCTION Compose project `frappe_docker` and separate DEV Compose project `frappe_docker_devcontainer`.

- **Six PRODUCTION app containers** `frappe_docker-frontend-1`, `frappe_docker-queue-short-1`, `frappe_docker-backend-1`, `frappe_docker-queue-long-1`, `frappe_docker-websocket-1`, `frappe_docker-scheduler-1` all use the same locally tagged application image **`ccpcerp:v16.50.0`** and reported `Up 3 weeks`. **Do not use the earlier `release-2026-09-16` or unmerged billing PR #33 instead.** The tag alone does *not* prove immutable image bytes, application Git SHA, exact Frappe/ERPNext revisions or installed patches.
- **PRODUCTION database** `frappe_docker-db-1` is `mariadb:11.8`, reported `Up 3 weeks (healthy)`; `frappe_docker-redis-cache-1` and `frappe_docker-redis-queue-1` use `redis:8.6-alpine`.
- **Separate DEVELOPMENT project** `frappe_docker_devcontainer`: a `vsc-frappe_docker-…-uid` Frappe container, `mariadb:11.8` database and two `redis:alpine` containers. All four reported `Up 3 weeks`; they are **not** migration sources and must not be copied/reconfigured.
- This was a metadata-only observation, not a full application health or backup validation. No container was restarted, copied, or changed. The source host's sudo password was entered locally; it was not supplied to chat.

**Next operator step (single bounded read-only inspection on OLD host):** Confirm the actual running backend container's image ID matches the local `ccpcerp:v16.50.0` tag before freezing image provenance:

```bash
sudo docker inspect --format 'running_backend_image_id={{.Image}}' frappe_docker-backend-1
sudo docker image inspect ccpcerp:v16.50.0 --format 'tag_image_id={{.Id}} created={{.Created}}'
```

Stop and investigate if the image IDs differ; do not `pull`, `build`, `save`, `commit`, or modify either environment yet. After identity alignment, read installed Frappe/ERPNext/CCPC versions and exact Git commits with a separately reviewed read-only procedure; then plan/authorize complete backup, new-host isolated restore and cutover.

## CURRENT DECISION — 2026-11-06: migrate **only existing live PRODUCTION**, unchanged in functionality

**Owner-directed scope change (supersedes the earlier candidate app PR #33 release path and this document's prior 'accounting acceptance first' recommendation):** Relocate the **already running live production** from the shared legacy Ubuntu host `ccpcerpserver` to the new physically dedicated `ccpcerp-prod`, without promoting unfinished DEVELOPMENT features. The application, version, database and business configuration source of truth is the **actual active legacy PRODUCTION deployment**, not DEVELOPMENT Git state and not a future release candidate. The old host's DEVELOPMENT installation remains untouched and continues independently.

**Decision is approved as migration direction and planning scope; production-impacting execution remains separately gated.** Do not interpret the owner's proposal as blanket approval for new-host container creation, exporting/copying the live database, taking new production backups, secrets handling, restoration, migrations, DNS cutover, stopping legacy services or retiring the old production instance. Obtain exact scoped approval for each consequential phase after presenting a verified plan.

**What must be included:** same live ERPNext/Frappe/installed CCPC application code and metadata (verify running image identity, app revisions, patches and versions), all existing PRODUCTION Companies, Chart of Accounts, inventory/Stock Ledger, GL, users/roles/User Permissions, business documents and configuration; **all four Frappe backup artifacts** — database, site configuration, public files and private files — plus independently handled environment secrets, integration config and recovery prerequisites. Keep the Frappe site identity `ccpcerp.local` unless a later separately approved compatibility plan requires otherwise.

**What must NOT be included:** any changes existing only in `development.localhost`, disposable CI/integration sites, unmerged review/feature branches, PR #33's unfinished billing roles/policies, DEV test records, DEV database or DEV credentials. The custom app Git `version-16` HEAD or `release-2026-09-16` pin alone is **not proof** of what currently runs on old production; exact live image/application version must be observed and preserved or reproducibly matched. Do not introduce a newer app release, unapproved DocTypes, database patches, workflows, role grants, or business rules as part of this infrastructure migration.

**Infrastructure compatibility is separate from changing business functionality:** The new host still requires independently protected credentials, Docker/Compose networking, appropriate image availability, volumes, NAS backup, TLS/firewall and restore testing. Those safe host-specific changes may be needed to run the same application, but must be reviewed for unwanted app or data/schema changes. An accidental version mismatch or automatic `bench migrate` could change schema/business behavior; exclude it until independently justified and approved.

### Migration sequence / safety gates

1. **Read-only old-host baseline first:** verify `ccpcerpserver` host identity; current legacy production containers, Compose project, image tags/IDs, installed app and Frappe/ERPNext versions and Git SHAs (including dirty changes), database/site identity, declared volumes, existing backup job and NAS path — without printing secrets or modifying any container. Separate production facts from development data. On the new host, already-verified empty Docker inventory and two clean historical checkouts need not be repeated unless changed.
2. **Freeze exact production-source identity:** choose an immutable, verifiable copy of the *live* app image or a byte-equivalent reproducible build from precisely matched commits and tracked overlays, supported by backups and checksums. Do not use the candidate `1bde04b` billing app or `c12d46f` dedicated review stack as a substitute for live-app identity; the latter may supply **reviewed infrastructure safeguards only** after checking for compatibility.
3. **Approved full recovery point:** produce a new, consistent legacy production four-artifact backup; independently verify files and off-host NAS, preserve an unaffected recovery point, and capture an approved operational settings/credential re-provisioning inventory. Confirm that backup creation alone is not restore proof.
4. **Isolated new-host rehearsal:** on a separately authorized non-live stack, restore old production data and verify documents/attachments, company books, stock/GL totals, permissions, version compatibility and migration behavior. During testing, prevent duplicate scheduled jobs, background workers, email, external integrations, payment/accounting writes and network access to employees; do not let a restored copy and old production both process business events. Do not make the new copy live before validation.
5. **Separate planned cutover:** approved downtime/maintenance window; quiesce/fence writes and background processing on old PRODUCTION; make a **fresh final consistent backup/sync** (not the earlier rehearsal copy); verify checksums, restore and reconciliation; separately approve and configure LAN DNS/TLS/endpoints and start only the new production instance. Ensure no split-brain/simultaneous write access.
6. **Post-cutover:** validate representative real production records, GL/SLE balances, attachments, login, workers, scheduler, integrations and new NAS scheduled backups; retain old production isolated and recoverable until explicit approval of retirement. Define rollback triggers and data reconciliation before any cutover.

**Immediate next operator step (read-only on OLD host only, not on new `ccpcerp-prod`):** Once in the trusted `gani@ccpcerpserver` session, execute:

```bash
hostnamectl --static
sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

If hostname differs from `ccpcerpserver`, stop. Output lists container metadata only; **no secrets, volume contents or Frappe data**. This establishes exactly which production image/tag and relevant containers currently run before requesting any backup or restoration actions. Record the date, source host and operator output. Do not stop/restart any container.

**Historical sections below remain as review evidence only:** Previous proposals to deploy PR #33 and resolve its incomplete Finance billing functionality **before** migrating are **superseded for this live-only move**, though still valid for a later independent DEVELOPMENT-to-PRODUCTION release after successful migration. Ignore old 'next step' wording where it conflicts with this current decision.

---

**Created:** 2026-11-06  
**Scope:** Dedicated Ubuntu server `ccpcerp-prod`, **not yet live**.  
**Status:** Preparation/documentation approved; no authorization for container creation, deployment, database restoration/migration, cutover, or old-host changes.  
**Purpose:** Preserve current verified facts and the shortest safe continuation path so subsequent conversations do not repeat completed read-only inventory.

## How to use this file

1. **Read this production record first** for dedicated-host facts, current decisions, checks, and deployment gates. Read [the GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) and [active app/development handoff](CURRENT-HANDOFF-3.md) for overall engineering state.
2. GitHub controls committed deployment code and documentation; **live host output controls actual running state**. Date every new host observation. Do not silently upgrade a historical observation into current proof.
3. Update this file after meaningful host verification, approved deployment/restore, or recovery milestones. Keep a concise **latest checkpoint at the top**; archive lengthy test transcripts separately. Never store passwords, private keys, complete `.env`, credentials, sensitive configuration, database content, or unredacted logs.
4. Preserve DEV/PROD physical separation and the **old** production server. GitHub merges or preparatory approval do not authorize production runtime changes.

## Latest checkpoint — 2026-11-06 (owner-reported read-only terminal output)

**Host:** New dedicated `ccpcerp-prod`, LAN `192.168.50.186`, account `ccpcadmin`. Historic host provisioning documented in [PRODUCTION-HOST-SETUP-HANDOFF.md](PRODUCTION-HOST-SETUP-HANDOFF.md). Windows SSH uses an owner-held Ed25519 key; do not request or copy private key material. Earlier reported `hostnamectl --static` = `ccpcerp-prod`, Docker context = `default`; this conversation's inspected Docker endpoint was `unix:///var/run/docker.sock` per prior guarded-run status, not independent proof of immutable daemon identity.

**Docker and permissions:** Docker Compose reports `5.6.1`; `sudo systemctl is-active docker` returned `active`. Socket `/var/run/docker.sock` was `root:docker` with mode `srw-rw----`; `ccpcadmin` is in `adm cdrom sudo dip plugdev lxd`, **not** `docker`. Unprivileged inventory failed with `permission denied`; later *explicit owner-performed* read-only `sudo docker ps`, `sudo docker ps -a`, and `sudo docker system df -v` succeeded and showed **zero running/stopped containers, zero Docker images, zero Docker local volumes, and 0 B build cache**. This is **consistent with the brand-new host**, not evidence of deleted ERPNext data. Docker network inventory, actual firewall behavior and effective Compose model have **not** been verified in this checkpoint. Do not change Docker socket mode/groups/ACLs merely for convenience; Docker access is effectively root-level.

**Host Git checkouts (owner-reported):**

| Location | Branch | HEAD (short) | Git state | Remote |
|---|---|---|---|---|
| `/home/ccpcadmin/ccpc-frappe-deployment` | `security/dedicated-production-pre-tls-2026-10-23` | `0bf8c6a` | clean (`git status --short` empty) | `git@github.com:ccpcerp/ccpc-frappe-deployment.git` |
| `/home/ccpcadmin/ccpc-pr29-review` | `security/dedicated-prod-external-env-2026-10-23` | `bd92ade` | clean (`git status --short` empty) | same |

Both checked-out commits matched the GitHub PR branch tips on 2026-11-06. The first checkout tracks `compose.yaml`, `overrides/compose.dedicated-pre-tls.yaml`, `images/production/Containerfile`, and the dedicated port-profile document. The second additionally tracks `docs/04-operations/dedicated-production-external-credentials.md`. **Preserve both checkouts; no blind pull, switch, clean, reset or overwrite.**

**Connected GitHub PR status (2026-11-06):** [PR #27](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/27) pre-TLS `0bf8c6a`, [PR #29](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/29) external credentials `bd92ade`, [PR #30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30) backup safety `fd751ab` are **OPEN/DRAFT/UNMERGED**, stacked in that order. These are **review candidates**, not approved deployed releases. Later dedicated Compose identity/environment reviews also exist; see [Step 144 inventory record](DEDICATED-PROD-STEP144-READONLY-HOST-INVENTORY-2026-10-25.md) and verify the right final reviewed source revision before use. The app's feature/review branches must also be reverified at release selection; never assume `version-16` includes all reviewed functionality.

## GitHub-only source review — 2026-11-06 (no host execution)

**Owner approval:** Continue non-live preparation and preserve a dedicated production record. Review executed through connected GitHub only; no PR merge, SSH session, credential provision, Compose execution, image build, container start, database operation or production modification.

**Verified review ancestry:** GitHub compare shows PR #29 is 10 commits ahead/0 behind PR #27; PR #30 is 27 ahead/0 behind PR #29; `review/dedicated-host-readonly-inventory-2026-10-25` (`c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e` at this review) is 20 ahead/0 behind PR #30. The latter contains later Compose project/credential-selector guards and the read-only host inventory helper, **but is still a review branch and not a final approved production release**. The existing on-host directories are behind these later draft protections; preserve them rather than pulling automatically.

**Candidate source inspection:** On the later review branch, `scripts/config.sh` blob `32614da1044c768bd67dcb9b9491e7c48ff2653a` defines five Compose inputs for `dedicated-pre-tls`, adding `overrides/compose.dedicated-pre-tls.yaml` last. The override blob `14fd89a3c2371104f464964137483de9f4a35861` replaces frontend publication with `127.0.0.1:8080:8080/tcp`, requires nonempty `DB_PASSWORD`, and declares explicit backend sites/logs mounts. The revised Docker module blob `a99bcdb2077f55f5ded118159ad72a90d0a9fd7e` requires the dedicated env file (external, 0600, owner-only parent 0700, one `DB_PASSWORD` key), rejects ambient Compose project/file/profile selection, verifies local default Docker context/socket, and passes the **candidate-only** `--project-name ccpc_prod_erpnext`. These are **source-level findings, not a real `docker compose config` validation**.

**Material pinning gap:** `scripts/config.sh` still pins `CCPC_REF=release-2026-09-16` with `CCPC_SHA=cfcc19394a6646548f2b7050db040c8cf5ebafde`; later October/November business application review work exists. **Do not equate this pinned older app revision with the current proposed day-one financial/billing release** or automatically change it to the moving `version-16` tip. Independently select and approve exact app source, Frappe/ERPNext compatibility, image provenance, unresolved permissions/SoD issues, and migrations before any release build.

**No-runtime-render gap:** All five-file Compose inputs still need an exact-source, secret-safe `docker compose config --quiet` validation in an authorized environment, followed by sanitized verification of service/port/mount metadata, Compose project identity, expected volumes and unknown environment-selector behavior. Avoid full config dumps that interpolate credentials. Docker zero-resource inventory reduces name-collision uncertainty only at the time observed; it is not authorization to allocate volumes or start services.

**Next decisive action:** Review the specific app candidate release SHA and unresolved blockers alongside the stacked dedicated Compose review branch; produce a single pinned candidate and a safely executable, credential-free or synthetic Compose-validation plan. The on-host checkouts and old PRODUCTION remain untouched. Real secret provisioning, host checkout updates, image build, starting containers, backups/restores, migration and cutover each retain their respective explicit approval gates.

## Source-pinned candidate selection and Compose validation plan — 2026-11-06

**Outcome:** Identified a **provisional application candidate and provisional deployment-review baseline**, not a buildable/approved release pair. All findings are from connected GitHub; zero server or Compose execution.

### Candidate sources verified

| Part | Provisional source reference | Verified state | Disposition |
|---|---|---|---|
| Application baseline | `ccpcerp/ccpcerp` `version-16` @ `cfcc19394a6646548f2b7050db040c8cf5ebafde` | Older base; 585 commits behind the billing review head (GitHub compare) | **Not sufficient for latest day-one billing behavior** |
| Application candidate | `ccpcerp/ccpcerp` `review/billing-authorization-correction-2026-11-03` @ `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc` | PR #33 OPEN/DRAFT/unmerged; GitHub combined commit status SUCCESS with `python-syntax`, `billing-controls-manual-approval`, `billing-controls-isolated-integration` | **Pin for review only**; not live-accepted or production approved |
| Deployment baseline | `ccpcerp/ccpc-frappe-deployment` `review/dedicated-host-readonly-inventory-2026-10-25` @ `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e` | Descends from PRs #27/#29/#30; includes reviewed project-name and local Docker checks | **Pin for source review only**; not merged or production approved |
| Frappe / ERPNext | `FRAPPE_REF=v16.33.1` and `ERPNEXT_REF=v16.34.2` in deployment `scripts/config.sh` | Corresponding SHAs and ERPNext patch/overlay hashes are frozen in that file | **Compatibility and image build still unverified** |

**Critical alignment issue:** The pinned deployment `scripts/config.sh` and `apps.json` still reference `CCPC_REF=release-2026-09-16`, `CCPC_SHA=cfcc19394a6646548f2b7050db040c8cf5ebafde`, and `apps.json` branch `release-2026-09-16`. The image Containerfile explicitly checks the cloned application's actual `HEAD` against `EXPECTED_CCPC_SHA`; therefore **changing only the expected SHA fails unless the Git fetch ref also retrieves that exact revision**. An approved release must introduce an immutable reachable app ref (or deliberate supported exact-SHA checkout design), update `CCPC_REF`, `CCPC_SHA` and `apps.json` coherently on a **new reviewed deployment branch**, then validate private Git fetch, image build, framework/ERPNext version compatibility, and installed app behavior. Do **not** change the existing two server checkouts, copy draft code straight into live production, or substitute a moving branch/ref as an immutable release pin.

**Business and acceptance blockers:** The three GitHub CI statuses establish bounded automated results, **not** persistent DEVELOPMENT named-Checker acceptance, solved Purchase Invoice Submit separation of duties, full authenticated HTTP/concurrency regression coverage, signed image release, or disaster recovery. Consult `CURRENT-HANDOFF-3.md` before asserting these gaps have closed. PR #33 remains draft and requires business/security review before release approval.

### Source-pinned safe Compose validation — plan only

1. Start with an **isolated scratch/lab checkout** of the exact reviewed deployment commit `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e`; preserve existing production host checkouts. Check blob fingerprints and verify all five Compose files in this exact order: `compose.yaml`, `overrides/compose.mariadb.yaml`, `overrides/compose.redis.yaml`, `overrides/compose.lan-production.yaml`, `overrides/compose.dedicated-pre-tls.yaml`.
2. First use credential-free static/offline tests and Bash syntax checks. The final override must replace `frontend.ports` to `127.0.0.1:8080:8080/tcp`; there should be no published MariaDB/Redis host ports. Review YAML `!override` semantics with real Compose 5.6.1 or an approved known-compatible Compose v2 lab CLI, not a generic YAML parser alone.
3. For a later **explicitly authorized isolated Compose render**, supply **synthetic test-only** `DB_PASSWORD` via an ephemeral protected 0600 external file in an owner-controlled 0700 directory, **not** via checkout `.env` or real production secrets. Use `CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls` and reviewed explicit image name/tag. Run only non-deploying `docker compose ... config --quiet` with the pinned five-file configuration and project selector in the authorized lab. Do **not** print full `config` output, because it can expose interpolated secrets. Preserve the security wrapper's environment guards; do not misrepresent a raw `docker compose` invocation as equivalent to the protected wrapper.
4. Validate sanitized expected service set (`configurator`, `backend`, `frontend`, `websocket`, `queue-short`, `queue-long`, `scheduler`, `db`, `redis-cache`, `redis-queue`), candidate Compose project identity `ccpc_prod_erpnext`, loopback-only frontend port, named `sites`/`db-data`/`logs` volumes, and no unexpected external/bind mounts or ambient Compose selectors. Any mismatch is a **stop**.
5. Only after a successful isolated render, obtain separate approval for on-host checkout preparation and any real credential creation, then for image build/containers. Before a restore or employee cutover, separately verify old-production consistent backup, isolated restore, schema, security, ledger, TLS, and rollback.

**Next implementation decision:** Complete focused code and acceptance review for app PR #33 and the inherited deployment guards; specify the exact app immutable release ref and a coherent `apps.json` / `config.sh` change on a fresh **review branch**. Do not merge PRs, create host secrets or run `compose up` based on this plan. The user approved GitHub-only preparation; business-policy changes, merges, persistent DEV actions and any production-impacting operation still require separate scoped approval.

## Owner-delegated next-step selection — 2026-11-06

**Decision:** Prioritize the **existing app PR #33 accounting authorization acceptance gate** ahead of image-source alignment, production image build or Compose execution. This is not a new authorization to change Company permissions, role assignments, DEVELOPMENT records, or any production resources.

**GitHub verified again on 2026-11-06:** app PR #33 remains OPEN/DRAFT at `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc` against `feature/finance-mapping-lifecycle-2026-10-28`; current commit's combined status SUCCESS with `python-syntax`, `billing-controls-manual-approval` and `billing-controls-isolated-integration`. The reviewed `intercompany_billing_authority.py` explicitly denies Administrator/Guest, disabled users, Stockroom Personnel, absent literal role, and missing Company User Permission for either Company. It requires two different named Maker/Checker users. The controller also has row locking and protected billing state transitions, but no new live tests were executed here.

**Important unresolved distinction:** Application-level `require_billing_actor()` does not establish that ordinary **native Purchase Invoice Submit** permission is denied to every conflicted shared purchasing employee. GitHub's active handoff identifies this separation-of-duties overlap and persistent DEVELOPMENT named-Checker acceptance as unresolved. A CI pass is not proof that real site DocPerm/role memberships cannot bypass the workflow. Do not auto-assign the new roles, revoke other users, alter native PI DocPerm, or change business policy without a separate business/security decision.

**Chosen delivery sequence:** (1) Safely inspect protected DEVELOPMENT branch/status and obtain fresh post-Maker off-host backup under separate approval; (2) run targeted read-only role/Company scope/native PI Submit permission mapping and present the smallest effective policy choice; (3) perform explicitly authorized named Maker/Checker end-to-end acceptance on DEVELOPMENT, with rollback boundaries and test records documented; (4) only after resolution, create a coherent immutable app ref + `apps.json`/`config.sh` pin update on a fresh GitHub review branch, validate actual image and synthetic/isolated Compose render; (5) separately authorize non-live new-host instantiation, migration backup/restore, TLS, and finally cutover. Preserve existing old PRODUCTION unchanged throughout.

**Immediate external dependency:** A safeguarded DEVELOPMENT preflight and later actual acceptance require separate scoped authorization and operator-side access; the GitHub connector does not provide live SSH. No such host operation was performed by this documentation decision.

## Permanent data and release boundaries

- **Migration authority:** Owner approved the **existing old PRODUCTION site/database** on `ccpcerpserver` (internal site `ccpcerp.local`) as the starting source of business records. That approval selects a source; it does **not** permit live data export/transfer/restore or site migration.
- **No DEV substitution:** `development.localhost` and disposable integration sites are test environments, not business migration sources. Do not initialize new live business data independently and later overwrite or splice it into the old source.
- **Protect old operations:** Keep old production serving users unchanged until a separately authorized, backed-up, tested cutover. During final authorized cutover, fence old writes before final sync to prevent split-brain; verify transaction reconciliation and rollback plans.
- **Backup and recovery:** Future migration requires a complete, consistent **database, site configuration, public files, and private files** set; safe handling of secrets; verified integrity and isolated restore; version/schema compatibility; Company, COA, inventory, GL, users/roles, documents and attachments validation. The dedicated NAS share `ccpcerp-prod_backups` has historical SMB smoke-test evidence, **not** evidence of a successful four-artifact production backup or restore.
- **Production safety:** No restart, Compose `up/down`, database migration/restore, material changes, DNS/TLS cutover, backup deletion/retention change or Docker cleanup without separately scoped explicit approval. No accidental use of legacy deployment environment or secrets.

## Reviewed candidate design (not current running state)

- The pre-TLS profile is intended to publish frontend HTTP on **`127.0.0.1:8080` only**, with no MariaDB/Redis host ports; employee-facing `https://ccpcerp.com` on LAN TCP 443 requires a separate validated gateway, certificate trust, WebSocket/Host headers and firewall rules. Refer to [dedicated port profile](../04-operations/dedicated-production-port-profile.md) on the relevant branch.
- The external-credentials draft proposes a **0600**, user-owned, non-symlink env file outside Git checkout, in a **0700** owner-only directory, passed via `CCPC_DEDICATED_ENV_FILE`; never use checkout `.env` for dedicated database secrets. Do not print interpolated `docker compose config` in chat or logs.
- Candidate dedicated Compose project `ccpc_prod_erpnext` and volume names are **unapproved proposals**, not an observed deployed namespace; check selector/env guards and name collisions before any deployment.
- The dedicated backup-safety PR is still a draft. Signed release/source pin, backup identity, recovery, and approval controls require review and execution evidence rather than relying on offline mock tests alone.

## Approved work versus gated work

**Approved on 2026-11-06:** Prepare the dedicated **non-live release candidate**, including GitHub documentation, inspection/review of exact candidate source, and planning the separate credential provisioning and configuration validation. This approval **does not** cover provisioning actual passwords without a controlled procedure, changing SSH/Docker access rights, starting containers, old production backup execution, restoring or migrating any database, switching DNS/TLS traffic, merging draft PRs, or go-live.

**Immediate engineering next action:** Compare the stacked dedicated release candidate (PRs #27/#29/#30 plus later reviewed Compose/identity guards) against the available on-host checkout revisions, identify a single **source-pinned non-live configuration** and a no-secrets `docker compose config --quiet` validation plan. Do GitHub-only source review first; use a separately reviewed checkout or exact pinned commit rather than mutating the two existing checkouts. For any host-side change or real credential setup, present the exact command and seek the necessary scoped approval once.

**Release gates, in order:**

1. Freeze reviewed app + deployment source SHAs, Compose project/overrides, dependencies, and image provenance; resolve draft PR dependencies and unresolved security defects.
2. Independently validate effective Compose project/services/ports/volumes, no remote daemon and no namespace collision in a safe environment; keep 8080 loopback-only prior to HTTPS gateway.
3. Explicitly approve and provision segregated production credentials **outside Git**, with secret backup/rotation and failure recovery; never copy from DEVELOPMENT.
4. Approve and instantiate a **non-live** isolated stack only after volumes, image/version and rollback are reviewed. Validate service and data recovery behavior without live employee transactions.
5. Separately approve source production backup/export, transfer and isolated new-host restoration of the **old production** four-artifact backup. Prove files, data, schema, permissions and reconciled reports.
6. Verify independent NAS backup, restore rehearsal, TLS trust/redirect/WebSocket, LAN segmentation, role/SoD and accounting acceptance, maintenance-window and rollback/runbook.
7. Obtain explicit go-live/cutover approval; fence old writes, make final consistent copy, reconcile, switch access deliberately, observe and retain old recovery assets until separately approved retirement.

## Next-conversation quick start

**Do not repeat** Docker installation, empty-container diagnostics, home directory discovery, or Git checkout identification unless host state actually changed. Start by reading this record, the current workflow and the latest active handoff; compare GitHub draft PR heads/current reviews, then continue the immediate engineering next action above. If the host changes, record exact date, operator-run read-only evidence, affected host, result and new next action. Clearly label historical facts, new observations and unverified assumptions.

**No production deployment or migration occurred in this documentation milestone.**
