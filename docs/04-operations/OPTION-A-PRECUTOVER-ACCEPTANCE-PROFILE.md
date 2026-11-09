# Option A — like-for-like NEW-host pre-cutover application acceptance profile

## November 9 — A3 logs root correction PASSED; isolated app start reviewed, NOT RUN

Owner's exact NEW-host output:

```text
A3_LOGS_ROOT_PREFLIGHT_PASS
A3_CANDIDATE_LOGS_ROOT_OWNER_1000_PASS
A3_NO_APP_SERVICE_STARTED
```

Both candidate sites and logs named-volume roots now have UID/GID 1000 with 0755 permissions, reported by two separately guarded commands. **Do not rerun** either volume-root ownership script, any earlier A2 recovery script, or candidate SQL import. NEW has only 9 running DB/Redis support containers, 12 named volumes and 3 project bridges; protected rehearsal containers and OLD PROD/DEV remain untouched according to the passed operator guards. The backend/websocket/frontend are **not yet started**.

A NEW one-use reviewed A3 candidate-only startup source has been committed on `review/option-a-existing-release-precutover-2026-11-09`: [`scripts/option_a_a3_start_internal_app.py`](../../scripts/option_a_a3_start_internal_app.py), commit `646c384db1e0c884200c652fea85734930e8a414`, Git blob `443ef2e98e3570d478c2ebda43f662fe565fa860`, **SHA256 `de207481685b0ae4b950edd7af0f5001fe1fa7e9b43df8d2c4aed614bb025504`**, UTF-8 11,646 bytes. GitHub source bytes verified and match the locally compiled, offline-tested file. The local synthetic read-only guard was tested for exact state PASS and rejection of wrong site-file mode and an unexpected assets symlink. **No live NEW app startup, Docker service, HTTP endpoint, or authenticated login test has yet been performed**.

A3 startup script guards NEW hostname/operator/default local Docker context, exact 9 support containers (all running), 12 named volumes, expected 6 Docker networks including three protected project bridges, image IDs, candidate DB health, internal nonattachable candidate bridge with only 3 expected peers, candidate volume labels/mountpoints, strict exact site/logs ownership and contents, correct scheduler/mail-disabled site config, and no preexisting `sites/assets` link. It then runs only candidate `backend`, `websocket`, `frontend` from immutable image `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`, with `--pull=never --restart=no --user=1000:1000 --cap-drop=ALL`, no host ports, attached **only** to `ccpc_prod_erpnext_default`, mounting **only** candidate sites+logs volumes. The original image entrypoint creates `sites/assets` symlink; no configurator, worker, scheduler, migration, SMTP, DNS, public listener or production/rehearsal action is included. After resource checks, it makes an HTTP GET to `/login` **inside the candidate frontend** with Host `ccpcerp.local`, discarding response body and exposing only sanitized HTTP status markers. HTTP 200 is a connectivity/login-page milestone **not proof of authenticated application login** or financial correctness.

**Operator next:** Download the exact pinned GitHub source through "Download raw file" to Windows Downloads; SHA256 check in PowerShell; strict-host-checking SCP through existing key to `ccpcadmin@192.168.50.186:/home/ccpcadmin/`; independently verify SHA256 and `python3 -m py_compile` on NEW, then execute **once** as normal `ccpcadmin` under the existing separately approved isolated NEW candidate application acceptance. On any `STOP:A3_APP_...`, preserve all partial candidate containers/volumes; **do not rerun**. If successful, proceed to separate supervised authenticated login and read-only Company/Work Request/finance acceptance before any gateway/TLS/final cutover; source remains Nov05 02:00 subject to post-backup write reconciliation.

## November 9 — A3 sites root fixed, logs root ownership gate

Owner's exact NEW Ubuntu output from the guarded one-use sites-volume root ownership correction:

```text
A3_CANDIDATE_ROOT_PREFLIGHT_PASS
A3_CANDIDATE_SITES_ROOT_OWNER_1000_PASS
A3_CANDIDATE_LOGS_ROOT_UID=0 MODE=755
A3_NO_APP_SERVICE_STARTED
```

**Verified milestone as operator-reported:** NEW candidate sites volume root was changed from UID 0 / 0755 to UID/GID 1000/1000, without recursively changing site files; no application service was started. This command is consumed; **never rerun it.** Separate candidate logs volume `ccpc_prod_erpnext_logs` remains UID 0 / 0755. The pinned image's Frappe backend runs as UID 1000 and requires a writable volume for application logs. Before app startup, carry out one more precisely guarded candidate-only, nonrecursive root-owner change, using an already-opened no-follow directory FD and `os.fchown(fd,1000,1000)`. Guard NEW hostname/operator, exact Docker socket/context, volume mountpoint/project+stage labels, root currently UID/GID 0/0755 and EMPTY, sites volume root UID/GID 1000/0755, nine expected running DB/Redis support containers, candidate bridge internal/nonattachable, and no unexpected Docker resources. Never inspect or print any business/secret file contents. On unexpected state, STOP without changes. After exact PASS, prepare separate fail-closed A3 script to launch backend/websocket/frontend only on existing NEW internal bridge and perform sanitized internal HTTP /login check; no queues, scheduler, configurator, migrations, public ports, old production or rehearsal impact. **The logs-root fix and application startup have not yet been executed.**

## November 9 — A3 volume-root ownership guard (pending operator run)

Owner's direct NEW-host `sudo stat` reported `A3_CANDIDATE_SITES_ROOT_UID=0 MODE=755` for exact candidate-only volume root `/var/lib/docker/volumes/ccpc_prod_erpnext_sites/_data`. The pinned custom image's `resources/core/main-entrypoint.sh` removes and re-creates `sites/assets` using the Frappe image process (UID 1000). Directory UID 0, mode 0755 will deny UID 1000 the link write. This is a verified filesystem ownership discrepancy, not evidence of an attempted app startup. The original A2 scripts are consumed and must not be rerun.

**Next single operator command:** A NEW-only, one-use, root-privileged guarded inline Bash procedure (syntax checked with `bash -n` outside NEW). Before the write, verify hostname/operator, exact volume name/mountpoint and Compose/project+stage labels, exactly the nine expected candidate/rehearsal support containers, the restored candidate site-files structure, UID/mode of the files and single private attachment without printing secret or attachment filename, and `sites` root currently UID 0/mode 0755. Then execute `chown --no-dereference 1000:1000` on **only the verified candidate sites-volume root directory**, to UID/GID 1000. The guarded inline Bash command is 26 lines, exits on a failed check, and does not use `-R`. No recursion, chmod, file overwrite, SQL, services, Docker network, volume deletion, scheduler/migration, OLD PROD/DEV or rehearsal modification. Confirm new ownership and emit `A3_CANDIDATE_SITES_ROOT_OWNER_1000_PASS`. The operation is not yet executed; any STOP requires inspection and no blind rerun. Observe the separate candidate logs-volume root UID/mode read-only to plan later app startup; do **not** change logs ownership without its own preflight.

The later backend/websocket/frontend startup must remain limited to the original image `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`, internal bridge `ccpc_prod_erpnext_default`, zero published ports, no worker/scheduler/configurator/migration. The owner-reported A2 PASS is not app login proof; actual runtime startup/HTTP/authentication/cutover remain pending.

## November 9 — Candidate A2 site/attachment recovery SUCCESS (owner-reported)

Operator ran the verified one-use recovery script `option_a_a2_complete_partial_site.py` on NEW and reported **all seven complete success markers**:

```text
A2_PARTIAL_PREFLIGHT_DB_NETWORK_BACKUP_AND_ARCHIVES_PASS
A2_PARTIAL_CANDIDATE_SECRET_AND_DB_ACCOUNT_REUSED
A2_PARTIAL_SCHEMA_SCOPED_APP_ACCOUNT_RECONFIRMED_PASS
A2_PARTIAL_SITE_CONFIG_AND_PRIVATE_ATTACHMENT_RESTORED_PASS
A2_PARTIAL_SIX_REHEARSAL_SERVICES_PRESERVED
A2_PARTIAL_NO_APP_WORKERS_MIGRATION_OR_PUBLIC_PORTS
A2_PARTIAL_CANDIDATE_SITE_READY_FOR_APP_TEST
```

**Status:** Candidate November 5 SQL backup, original source encryption key, candidate-only application DB account and private secret, site common/app/site config, public directory and single private attachment are reported restored on NEW. Both rehearsal environments remain protected and the output reports no app, workers, migrations or host-published application port. Treat these as operator-observed/script-reported assertions, not an independent ChatGPT connection to NEW. **No A2 script must ever be rerun**; preserve the exact candidate state. No actual HTTP, authenticated login, ERPNext record validation, employee HTTPS, or cutover has yet passed.

**Next bounded A3 step:** Start only `backend`, `websocket`, and `frontend` from the pinned `ccpcerp:v16.50.0` immutable image in the already-created `ccpc_prod_erpnext_default` internal-only Docker network. No `docker compose up`, configurator, scheduler, queue workers, mail/integrations, migrations, published host ports, DNS, old server or rehearsal changes. First verify the site volume root's UID/mode: the pinned `resources/core/main-entrypoint.sh` unlinks/relinks `sites/assets` as runtime UID 1000, and the A2 writer changed *file/subdirectory* ownership but did not explicitly change the **sites volume root** ownership. If the root is UID 0/0755, a narrowly bounded NEW-only root-ownership adjustment is needed before starting the image. A missing permission guard would reproduce another startup failure. Read-only candidate site inspection and fixed-volume single-use startup should fail closed on changed inventory; preserve partial state on STOP and never repeat one-use scripts. HTTP probe can occur **inside** isolated frontend, with only sanitized status output; authenticated login and employee-facing gateway are later separate milestones. Nov05 is the owner-selected source, subject to final post-backup write reconciliation.

## November 9 — A2 partial site writer diagnostic and guarded continuation (NOT RUN)

Operator's exact read-only NEW candidate-volume diagnostic: `COMMON_CONFIG=FILE UID=1000 MODE=600`, `APPS_TXT=FILE UID=1000 MODE=644`, `SITE_DIRECTORY=DIR UID=1000 MODE=755`, `SITE_CONFIG=MISSING`, `PUBLIC_FILES_DIR=MISSING`, `PRIVATE_FILES_DIR=MISSING`, `PRIVATE_ATTACHMENT_COUNT=UNAVAILABLE`, `SITE_ROOT_ENTRY_COUNT=3`, `ONEOFF_WRITER_CONTAINER=ABSENT`; markers `A2_DIAGNOSTIC_CANDIDATE_VOLUME_VERIFIED` and `A2_READ_ONLY_DIAGNOSTIC_COMPLETE`. No password, encryption key, private filename or attachment contents were printed.

Likely root cause: the original ephemeral writer created and chowned the site directory to UID 1000 (0755), then the same process ran as root with `CAP_DAC_OVERRIDE` dropped, causing failure when attempting to create the next file inside the UID-1000 directory. Error stderr was suppressed, so the diagnosis remains a strong inference, not a captured exception. Existing root-level site config files and candidate database secret/account **must be preserved**.

A **NEW review-only** one-use continuation script is now at [scripts/option_a_a2_complete_partial_site.py](../../scripts/option_a_a2_complete_partial_site.py), first committed as `37bb05d2aacb83683db2e5de6055dfafba87d389`, SHA-256 `9799bb8d34e012dddd55f57bac60959ccdf16e7b30de4c09aeeb6b14eea902d9` (17,124 bytes). It requires the **exact** three-entry candidate-only partial state, preserved Nov05 archive digests, private existing site password, schema-scoped existing database account/grants, unchanged inventory, image IDs and internal network. It reuses credentials and writes **only missing** `ccpcerp.local/site_config.json`, public/private file directories, and the single private attachment, using a temporary `--network none`, `--user 1000:1000`, `--cap-drop ALL`, no-new-privileges, read-only-rootfs writer mounted only to the candidate sites volume. Every file uses exclusive create; no SQL mutation, DB restore, migrations, application or worker start, published port or rehearsal operation. On STOP, preserve partial state and never replay. Original A2 script must **never** be rerun.

**Pending:** NEW operator must transfer the exact reviewed file with pinned commit and SHA256, pass Python compile and then separately perform the one-use continuation under the existing specifically scoped A2 approval. A similar local synthetic non-root writer test succeeded; actual GitHub-script execution and NEW-host file restore remain **unverified**. After successful actual output, independently diagnose/approve the isolated NEW backend/frontend/websocket application login stage. OLD production, both rehearsal environments, employee HTTPS, and final cutover remain protected and outside this step.

**2026-11-09. PREPARATION ONLY. NOT DEPLOYED. NOT PRODUCTION READY.**

Owner selected the fastest *safe* like-for-like release move: preserve the currently live OLD `ccpcerp:v16.50.0` image, and defer newer draft Withdrawal Slip, intercompany billing and report changes to a later separately approved application release.

This review branch starts from `review/dedicated-host-readonly-inventory-2026-10-25` at `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e`, **not `main`**. The new sixth file `overrides/compose.option-a-precutover.yaml` is a **temporary, locked-down staging profile**; it is not a replacement for the dedicated runtime release or the later full production services.

## NEW host evidence already available

Owner reported after Stage17V-H2C:
- 6 expected support containers and 8 named volumes split between protected `ccpc_restore_rehearsal_20261107` and `ccpc_full_acceptance_20261107`; 2 isolated project networks; no `ccpc_prod_erpnext` container, volume or network namespace collision.
- 734 GB available filesystem capacity as reported by `df -h /var/lib/docker`.
- Docker Compose 5.6.1 and no TCP listeners on 80, 443 or 8080 at inspection.
- The original full-production application image on OLD and NEW matches immutable ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`. The historical Nov5 restored clone has four Companies and matches that image for three checked custom DocType *presence* predicates: Work Request present; two newer features not installed.
- The NEW host previously accepted the **five original dedicated Compose files** using actual Docker Compose CLI with synthetic credentials in a private scratch source copy. Separate six-file *rehearsal-only* override was previously parsed on NEW; do not delete, overwrite, blindly replay, or confuse that scratch override with this new GitHub review file.

This evidence narrows the problem but **does not prove** Frappe login, employee HTTPS, image source SHA, current source backup, production rollback, live financial integrity or safe multi-container startup.

## Why sixth file is needed

The five-file dedicated pre-TLS Compose model, used alone, defines a configurator that modifies site files, frontend loopback port, and scheduler/queue workers. A generic `docker compose up` or existing `deploy_release` is NOT a safe acceptance step: it can create volumes, launch jobs, alter site config and run migrations.

The sixth reviewed file is intended to be layered **last**:
```
compose.yaml
overrides/compose.mariadb.yaml
overrides/compose.redis.yaml
overrides/compose.lan-production.yaml
overrides/compose.dedicated-pre-tls.yaml
overrides/compose.option-a-precutover.yaml
```

It assigns the six app/data acceptance services `backend`, `websocket`, `frontend`, `db`, `redis-cache`, `redis-queue` to the explicit `ccpc-acceptance` profile; stock `configurator`, `scheduler`, `queue-short`, `queue-long` are excluded behind separate `ccpc-disabled-*` profiles. The backend/websocket dependency on the stock configurator is replaced with prerequisites on existing DB/Redis services. All services have `restart: no` and `pull_policy: never`; all published frontend ports are removed; the default Compose bridge is declared `internal: true`. This is a **source-level intent**, not runtime proof. **Profiles alone are not a security boundary**; a privileged operator could explicitly enable excluded profiles or attach additional networks. No app service may be started before tested DB/backup/rollback and egress guard.

## Stage A1 — synthetic Compose parser only, no containers

Next, copy this exact **sixth review file** to an independent, owner-private NEW scratch location **without overwriting the old five pinned sources or either checkout**. Verify its GitHub file SHA/blob digest and existing source hashes. Run the real `docker compose ... config --quiet` using only a synthetic `DB_PASSWORD`, exact `CUSTOM_IMAGE=ccpcerp`, `CUSTOM_TAG=v16.50.0`, `PULL_POLICY=never`, explicit candidate project `ccpc_prod_erpnext`, and this exact six-file order. Run `config --format json` only through a bounded Python parser that outputs **sanitized PASS/STOP markers**, not the expanded environment/secret. Check expected service names/profiles, 0 published ports, internal default network, named volumes, restart=no, pull_policy=never, no host mounts, privileged flags, external bridges or secret values in printed output.

**Do not run `up`, `run`, `start`, `pull`, `build`, `exec`, `down`, `volume rm`, `bench migrate` or any OLD PROD/DEV operation from this source-only step.** Do not turn on an arbitrary profile or use real credentials for config-only validation.

## Stage A2 — separate scoped approval, then NEW application startup

Before any mutating Docker call, review and obtain exact approval for:
- Safe **new-only** candidate namespace, isolation from both preserved rehearsal datasets, distinct named volumes/bridge, immutable image IDs, and capacity.
- A **recoverable** candidate restoring historical source artifacts, not live OLD data, or another independently disposable clone; never overwrite either protected baseline or acceptance clone without separate approval.
- Fresh private credentials and config, Frappe scheduler/mail/webhooks/integrations OFF, queue workers OFF, no public ports, no auto-site creation, no schema migration, and exact side-effect-blocking network behavior.
- Explicit allowlisted service start procedure; no default `docker compose up -d`, and no `deploy_release`. Verified resource inventories and bounded STOP handling.
- App login, Company, Work Request, attachments and read-only financial/inventory acceptance; do not enter real transactions on an unapproved clone.
- Current **fresh and consistent** OLD production four-artifact backup, restored into the final NEW candidate **only after separate authorization**, independently tested recovery/rollback, final freeze, no dual writers, office TLS client trust and later explicit live cutover signoff.

NEW host's actual production app/http services have **not** yet been started or approved. OLD production continues serving users. A November 5 backup is only a historical rehearsal source, not safe final cutover data.

## Gate summary

The fastest safe plan is: **verify the one extra overlay by real Compose parser, approve one bounded isolated candidate start, perform one consolidated login/app acceptance, then fresh current backup + independent restore/rollback + TLS + final owner-approved cutover.** No extra H2B/H2C DocType mismatch tests or draft-feature release are necessary.

## Stage A1 no-profile validator mismatch — owner report 2026-11-09

The NEW sixth-file checksum matches GitHub. Operator ran the synthetic read-only Compose validator and received `STOP:OPTION_A_SYNTHETIC_COMPOSE_VALIDATION_FAILED`. A separately instrumented read-only diagnostic reported:

```text
A1_FILE_CHECK_PASS
A1_COMPOSE_PARSER_PASS
A1_SERVICE_SET=FAIL
A1_ACTIVE_PROFILES=FAIL
A1_DISABLED_PROFILES=FAIL
A1_NO_PORTS=PASS
A1_NO_RESTART=PASS
A1_NO_PULL=PASS
A1_INTERNAL_NETWORK=FAIL
A1_NAMED_VOLUMES=FAIL
A1_DIAGNOSTIC_COMPLETE
```

**Root-cause hypothesis, not yet proven with the corrected NEW-host run:** Original validator called `docker compose ... config --format json` with **no active profiles** and incorrectly expected all ten profile-gated services, default-network and named-volume declarations to appear. Compose normally omits inactive-profile services from the effective model; the empty/no-profile model can also omit unused network/volume definitions. These outputs do **not** prove the six-file config broken; parser itself passed. No service was started by this read-only check.

A new **review-branch-only** test file `scripts/review_option_a_compose_profiles.py` corrects the test: it verifies the five exact Git blob IDs and sixth SHA-256 first; renders the model three times with synthetic password only—`--profile "*"` for all ten service definitions and all networks/volumes; `--profile ccpc-acceptance` for precisely six allowed acceptance services; and no profile for zero default services. Checks no privileged services, unapproved mounts, exposed ports, restarts, pulls, disabled-service dependencies and non-internal networks. It suppresses raw Compose JSON and environment. **Source prepared, not yet run on NEW; do not claim PASS.** Never use `--profile "*"` with `up`; it is safe here only with `config`.

The source/configuration overlay itself was **not modified** to address this validation mistake. Continue with corrected synthetic parser check only; NEW actual application startup, restore, migrations, DNS or OLD production remains separately gated.

## Owner-approved Stage A2 empty candidate foundation — source prepared 2026-11-09

The owner explicitly approved NEW-only Stage A2 actual isolated app acceptance and selected **November 5 2026 02:00:01** as the latest and final approved four-artifact migration input, asserting OLD production remains live but is no longer being used. Do not require a later backup by default; nonetheless **verify no human or automated writes occurred after the 02:00 backup** before final cutover. No cutover/DNS/employee access/OLD host change is approved.

Added one-use operator script `scripts/option_a_a2_candidate_foundation.sh` in draft PR #32 (blob `025d02ad7ffe67204097bed89de00481f46e437b`, SHA256 `131fc1a6fc28323d5547b3187aa5be46475668a0ea8176aac5f06b2e15ab4631`, 5195 bytes). Identical downloadable copy was checked with Git blob ID and `bash -n` syntax PASS in ChatGPT's scratch environment. Script has **NOT** run on NEW yet.

Operator must transfer file via already established strict-host-checking SCP identity, check the exact SHA256 on NEW, and execute once as user `ccpcadmin` via `bash`. It verifies NEW hostname/user/default local Docker socket, exactly the six existing running DB/Redis containers, eight protected existing volumes and two original internal bridges, immutable app/MariaDB/Redis image IDs, exact four Nov5 artifact hashes and >=20 GiB Docker filesystem free. After PASS it creates **only** the new internal non-attachable `ccpc_prod_erpnext_default` bridge and four empty labeled candidate volumes `ccpc_prod_erpnext_{db-data,logs,redis-queue-data,sites}`. It verifies network isolation/volume label and preserved old support container inventory, then prints sanitized pass markers. It does not start containers, initialize a database, modify site config, connect OLD, import data, publish ports, run migrations, or access business records. Script is fail-closed and **non-idempotent**; after any failure/partial write, do not rerun, delete or reconcile automatically—report STOP and inspect state first.

The next approved step after an actual PASS is guarded isolated MariaDB/Redis candidate support start with NEW-only 0600 secrets passed using `*_PASSWORD_FILE`—**never environment-variable plaintext or `DB_PASSWORD=CCPC_SYNTHETIC_TEST_ONLY` from earlier parser test**—then use copies of four verified Nov5 artifacts to restore candidate data and files. Keep all automatic Frappe background workers/integrations disabled and no externally published ports until proper authenticated HTTP acceptance. OLD PRODUCTION/DEVELOPMENT and two rehearsal systems remain untouched throughout. No source script source-read or `bash -n` PASS should be misreported as actual Docker startup/restore.

## NEW A2 owner-reported candidate foundation PASS; guarded support startup prepared — 2026-11-09

**Owner-reported exact A2 foundation success markers:** `A2_NEW_HOST_AND_SOURCE_PREFLIGHT_PASS`, `A2_SEPARATE_INTERNAL_NETWORK_CREATED_PASS`, `A2_FOUR_EMPTY_CANDIDATE_VOLUMES_CREATED_PASS`, `A2_SIX_EXISTING_REHEARSAL_CONTAINERS_PRESERVED`, `A2_NO_APP_DATABASE_OR_WORKERS_STARTED`. Thus the independent `ccpc_prod_erpnext_default` network and four candidate volumes are reported present; no candidate DB/Redis/app runtime started by the foundation script. **Never replay the one-use foundation script.**

Prepared `scripts/option_a_a2_support_start.py` on this draft branch, confirmed Git blob `c7bc7eeee0929eadf74bd8f834e070ee8de987c3` matches the byte-for-byte local tested artifact, 10537 bytes, SHA256 `888724593cd0f006d5e603965568dedc2db602a86e33b94f8cdeedd378884115`. `py_compile` and static no-destructive-command/source guards PASS; **it has NOT run on NEW; no support-runtime PASS claimed.** One-use NEW-host operator command requires owner transfer of exact script, SHA verification, then `python3` as `ccpcadmin` (not root). Existing A2 approval covers this next isolated NEW-only application acceptance phase.

**Operator script scope:** checks exact host/account/default local Docker, 6 preexisting running support containers and 2 old networks/8 old volumes plus **new empty** `ccpc_prod_erpnext_default` bridge and 4 labeled candidate volumes, immutable three image IDs, intact exact four Nov5 backup checksums and no candidate network members. If all guard checks pass, creates owner-only 0700 `/home/ccpcadmin/.ccpc-option-a-secrets-20261109` and two exclusive 0600 files (random 64-character MariaDB root password, private MariaDB local-socket client option file) without displaying credentials or placing password in Docker environment/argv. Starts exactly 3 candidate containers with `docker run --pull=never --restart=no` using immutable image IDs, internal network and network aliases: `ccpc_prod_erpnext-db-1` (private root password via `MARIADB_ROOT_PASSWORD_FILE`; root host localhost, volume `ccpc_prod_erpnext_db-data`, internal-only healthcheck), `ccpc_prod_erpnext-redis-cache-1` (ephemeral tmpfs) and `ccpc_prod_erpnext-redis-queue-1` (only candidate Redis volume). Checks DB health/localhost socket SELECT 1 without password-in-argv, both Redis PING, exactly 9 total containers/12 expected named volumes/3 isolated project networks plus Docker default, all six rehearsal containers still running, no published host ports. Redis has `--protected-mode no` strictly inside the internal-only bridge; network participants are trusted candidate containers and no host forwarding is allowed. Later acceptance must assess side effects and auth carefully before accessing business records.

The A2 script **does not** run Compose `up`, import SQL, create ERPNext schema/user/site, enable worker/scheduler/mail integrations, start backend/frontend, touch OLD PROD/DEV, or publish HTTP/HTTPS. It intentionally uses direct, pinned `docker run` for the support-only acceptance phase; do **not** later run a generic Compose `up` against those names or try to adopt them into an unrelated Compose stack. All operations are non-idempotent after first write; on any `STOP:A2_SUPPORT_*`, preserve secrets and partial containers/volumes for inspection; no blind rerun/stop/cleanup. Then, after observed support PASS, restore approved Nov5 SQL and files into the **new candidate only** using separate guarded restore logic and new candidate-only app DB credential, followed by genuine Frappe login/HTTP and reconciliation. Final go-live still requires trusted LAN HTTPS and separate explicit controlled cutover approval; OLD stays live meanwhile.

## Stage A2 candidate support PASS; SQL-only Nov05 restore ready (not run)

On 2026-11-09 owner reported complete one-use A2 support startup markers:
```text
A2_SUPPORT_PREFLIGHT_ALL_PROTECTED_RESOURCES_AND_NOV05_VERIFIED
A2_SUPPORT_NEW_PRIVATE_DB_SECRET_CREATED
A2_SUPPORT_DB_RUNNING_HEALTHY_ROOT_SOCKET_AUTH_PASS
A2_SUPPORT_BOTH_REDIS_PING_PASS
A2_SUPPORT_THREE_CANDIDATE_SERVICES_ISOLATED_PASS
A2_SUPPORT_SIX_REHEARSAL_SERVICES_PRESERVED
A2_SUPPORT_NO_APP_SQL_IMPORT_WORKERS_OR_CUTOVER
```
NEW now has 3 additional candidate running MariaDB/Redis containers (nine total including 6 protected restored rehearsal support services), 12 total named volumes and the candidate-only internal network. OLD PROD/DEV unchanged. **Do not rerun** the candidate support startup or empty-volume foundation scripts.

Next one-use operator script: `scripts/option_a_a2_restore_nov05_sql.py`, GitHub review commit `59fdce753df0b3f1fa4ff85ff364352a5598579c`, blob `0aaf5e7a0fcff147f04ac138c5711e54aea6861e`, UTF-8 size **9452 bytes**, **SHA256 `2725c8502e1338f3075a2e292f306fb363e3621582c244020aa79ba00f60de5c`**, computed against exact GitHub source content. It is **not yet transferred, syntax-tested on NEW, or executed**. Operator should download through authenticated GitHub file page, hash-check locally, SCP via known SSH key, hash-check and run `python3 -m py_compile` on NEW, then execute once (only if all PASS). It checks isolated candidate 3+6 running containers, image IDs, exact 12 volumes/3 project bridges, source Nov5 four hashes and private candidate DB-client config; verifies candidate is free of non-system schemas and source gzip integrity *before* first write. Creates only the candidate target schema, streams approved compressed Nov5 SQL through the NEW candidate DB local root client (no password in argv/env), checks 741 base tables, 6 sequences, 4 Companies, DocType=814, Users=7, Singles=1000; verifies old six rehearsal containers preserved. No app worker, scheduler, HTTP, site file restore, migrations, mail, public port or OLD PROD/DEV change. After any `STOP` after schema creation **never rerun or delete**; preserve exact candidate state for inspection. On PASS, proceed immediately with candidate-only site DB identity, restored encryption-key site_config and attachments, then app login/functional acceptance. Production cutover still requires post-Nov05 backup activity reconciliation and a separately controlled employee-access switch.

## Stage A2 — candidate Nov05 SQL restore PASS; app-user/site/file restoration prepared (2026-11-09)

**Owner-reported exact SQL-only import PASS, on NEW:** `A2_SQL_PREFLIGHT_PROTECTED_CONTAINERS_ARCHIVE_AND_EMPTY_DB_PASS`, `A2_SQL_CANDIDATE_SCHEMA_CREATED`, `A2_SQL_IMPORT_CLIENT_EXIT_ZERO`, `A2_SQL_RESTORED_741_TABLES_6_SEQUENCES_4_COMPANIES_PASS`, `A2_SQL_RESTORED_814_DOCTYPES_7_USERS_1000_SINGLES_PASS`, `A2_SQL_SIX_REHEARSAL_SERVICES_PRESERVED`, `A2_SQL_NO_APP_FILES_MIGRATION_OR_WORKERS_STARTED`, `A2_SQL_NOV05_CANDIDATE_RESTORE_COMPLETE`. The approved Nov05 SQL is restored into **only** the candidate `ccpc_prod_erpnext` MariaDB, with schema 741 base tables/6 sequences/4 Companies. App/HTTP/worker/scheduler not started. **Never rerun the SQL restore.** No independently observed NEW data state apart from owner markers.

**Next one-use A2 operator task prepared and review-committed:** `scripts/option_a_a2_site_and_files.py` blob `40cc4206cfd30a7d93ee17f98e882c1bd6bb153e`, SHA256 `e5ae5b3a7fb3ed671079b9806100059450ec902b7fc243b4d32181e965c1d9dc`, UTF-8 15,480 bytes. This exists in DRAFT PR #32 **only; not transferred to NEW and not executed**. It verifies exactly 9 expected DB/Redis support containers, 12 labeled volumes/3 private Docker bridges, immutable images, approved four November 5 SHA256s, candidate SQL structural counts, schema-only absence of an application user and completely empty candidate sites volume, plus strict tar members (public files empty, one direct private file). It generates private owner-only 0600 app DB password file; creates MariaDB login `<historical_schema>@<candidate_bridge_IPv4_subnet/netmask>` with **only** that candidate schema's grants; verifies grants; writes candidate-only `common_site_config.json`, `apps.txt`, restored site config retaining historical encryption key and using the new app DB password, and extracted private attachment through an ephemeral no-network, read-only-rootfs, capabilities-reduced `--rm` image writer with only `ccpc_prod_erpnext_sites` volume mounted. App acceptance config sets `maintenance_mode=0` for eventual login, `pause_scheduler=1`, `disable_scheduler=1`, `mute_emails=1`; no persistent app or public port starts. Stops if any unexpected tar object, volume content, DB user, network/port, backup mismatch or partial write. **Do not rerun** after any `STOP:A2_SITE_` or failed post-write result; preserve and inspect. Source Python compilation is required on NEW before execution. The untrusted image's `VOLUME` declared logs path is explicitly replaced with tmpfs for the ephemeral writer and sites volume is `volume-nocopy` to avoid unintended population. Compiled image assets are linked by the real image entrypoint during later app startup; no build/migration now.

After successful one-use site/files task, next meaningful milestone is launch ONLY backend, websocket and frontend on a bounded internal network with no background queues, host-port exposure or outbound integrations, then perform login/session and Company/Work Request/finance read-only acceptance. A later supervised secure 443 office gateway and separately approved OLD freeze/cutover remain pending. Final source remains the owner-approved November 5 02:00 snapshot, subject to post-snapshot write reconciliation; do not demand a newer backup just for age.
