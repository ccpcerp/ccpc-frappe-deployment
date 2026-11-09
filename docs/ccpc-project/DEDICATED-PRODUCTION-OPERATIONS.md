# CCPC ERPNext — Dedicated PRODUCTION Operations and Deployment Record

## NEW REHEARSAL STAGE 17V-H2C PINNED IMAGE / RESTORED CLONE DOCTYPE ALIGNMENT — 2026-11-09

**OWNER-REPORTED ONE-USE IMAGE-ONLY INSPECTION PASS:** Operator on NEW ran `docker run --rm --pull never --network none --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges --pids-limit 32 --memory 128m --tmpfs /home/frappe/frappe-bench/sites:rw,nosuid,nodev,noexec,size=1m --tmpfs /home/frappe/frappe-bench/logs:rw,nosuid,nodev,noexec,size=1m --entrypoint /bin/sh sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8` with a shell loop checking only three installed CCPC DocType JSON paths. No network, host binds, DB credentials, app daemon, site mount or SQL access. Output: `IMAGE_work_request=PRESENT`, `IMAGE_withdrawal_slip=MISSING`, `IMAGE_intercompany_material_billing_batch=MISSING`, normal return. Earlier H2C clone MariaDB SELECT results: Work Request `DOCTYPE=PRESENT ISTABLE=0 TABLE=PRESENT`; Withdrawal Slip + Intercompany Material Billing Batch both missing DocType registration and base table. **These three presence checks align between preserved Sept16 pinned app image and historical Nov5 cloned database.** The H2B probe expected two features not shipped with the historical image. This is not a database corruption signal and does not justify auto-migration, nor does it prove Frappe Work Request ORM execution succeeded (the original H2B child first-error detail remained unavailable). Container `--rm` completed; no claims about other host file/volume/network hashes from this specific test. The newer reviewed GitHub source branch has these features, but is not the frozen original deployed image. **Next:** new separately reviewed SELECT-only Company+Work Request historical baseline application read acceptance with H2A credential and H2B isolation/after-state guards, no H2B rerun; then distinct tested/recoverable upgrade path for newer custom DocTypes if chosen. Do not mutate OLD PROD/DEV, original restored baseline, H1B protected checkpoint, clone DB schema, existing six containers or deploy production. H1B same-host checkpoint off-host=false restore_tested=false, final go-live approval separate.

## NEW REHEARSAL STAGE 17V-H2C IMAGE SOURCE-BOUNDARY OBSERVATION — 2026-11-09

Owner reported `sudo docker image inspect ccpcerp:v16.50.0` on NEW: `IMAGE_ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`, `CREATED=2026-09-16T15:55:49.950715082+08:00`, `REVISION=NOT_SET` using nil-safe OCI label lookup. An earlier `.Config.Labels` direct-access template failed only because labels map was absent. NEW identity and creation match separately reported OLD live backend's local image ID in existing 2026-11-06 record; the custom app's embedded Git SHA remains unproven because the original image has no `.git` and revision label is absent. Existing candidate source pin `release-2026-09-16` / `cfcc193` is corroborating context but not an attestation for the image. GitHub `version-16` at `cfcc193` contains only Work Request among the H2B three custom DocTypes; newer review `f665cf3` contains all three. This aligns with Stage17V-H2C SQL proof: Work Request present, Withdrawal Slip and Intercompany Material Billing Batch absent from Nov5 restored clone. Therefore do not migrate historical clone automatically to force an over-scoped modern-feature test to pass. First compare **actual pinned image file presence** in a separately bounded image-only, read-only, no-network, no-host-mount, no-DB container if explicitly executed. After that design historical baseline acceptance and a separate newly reviewed upgrade-migration rehearsal. No H2B/H2C rerun, clone/original DB writes, existing container restart/removal, OLD PROD/DEV changes or cutover; H1B backup still same-host/no independent restore test.

## NEW REHEARSAL STAGE 17V-H2C READ-ONLY DOCTYPE DIFFERENTIAL — 2026-11-09

**OWNER-REPORTED H2C PASS:** On NEW, a separately run SELECT-only clone MariaDB diagnostic using the existing `/run/secrets/db-client.cnf` inside `ccpc_full_acceptance_20261107-db-1` reported `WORK_REQUEST: DOCTYPE=PRESENT ISTABLE=0 TABLE=PRESENT`; `WITHDRAWAL_SLIP: DOCTYPE=MISSING ISTABLE=UNKNOWN TABLE=MISSING`; `INTERCOMPANY_BILLING: DOCTYPE=MISSING ISTABLE=UNKNOWN TABLE=MISSING`; `STAGE17V_H2C_READ_ONLY_DIAGNOSTIC_COMPLETE`. This is sufficient to show the restored Nov5 clone database cannot satisfy the H2B probe's required three-DocType check. It does not prove the first H2B child exception was the missing Withdrawal Slip (a prior Work Request Frappe ORM check could also fail) and does not diagnose installed app image `ccpcerp:v16.50.0`. GitHub review checkpoint `f665cf3` does include definitions for both missing DocTypes, but pushed source is not equivalent to migrated historical schema or the pinned Docker image. **No database migration or write was authorized or performed in H2C; original baseline and all six support containers remain untouched by the diagnostic as described.** No corruption demonstrated. Next review actual version/image provenance and independently recoverable current-feature acceptance path. Do not replay one-use scripts, start persistent app services, run SQL/bench migration, restart or clean containers, touch OLD PROD/DEV, or approve production cutover. H1B checkpoint is only local on same host and not off-host/restore-tested.

## NEW REHEARSAL STAGE 17V-H2B SIX SUPPORT CONTAINERS PRESENT — 2026-11-09

**OWNER-REPORTED READ-ONLY DOCKER INVENTORY PASS:** NEW `sudo docker ps -a --format 'NAME={{.Names}} STATUS={{.Status}} IMAGE={{.Image}}'` returned exactly six named running support containers: the clone's MariaDB `mariadb:11.8` and both `redis:8.6-alpine`; the original baseline's `mariadb:11.8` (Docker reports healthy) and both Redis 8.6. No extra or H2B helper container listed at inspection. This is container inventory only; Docker volume/network invariants, H1B file hashes after H2B, actual clone SQL DocType metadata, and image compatibility still need validation. H2B custom DocTypes phase STOP remains unexplained, NOT corruption established. Next minimal read-only step is to examine the existing one-use script's bounded custom DocType probe predicates (never run it again), then design a separate sanitized SELECT-only clone/image metadata check. Do not recreate helper or modify any DB, original baseline, old PROD/DEV or production rollout; H1B remains same-host/non-restore-tested.

## NEW REHEARSAL STAGE 17V-H2B HELPER ABSENCE VERIFIED — 2026-11-09

Owner reported zero lines from read-only `sudo docker ps -a --filter "name=ccpc_stage17v_h2b_probe_20261109" --format 'NAME={{.Names}} STATUS={{.Status}} IMAGE={{.Image}}'` on NEW. Thus the named disposable helper was not listed by Docker at the time of inspection. This does **not** establish full post-run six-service/volume/network/checkpoint invariants and it does **not** explain the custom-DocType phase STOP. Next operator action is one read-only NEW-only complete container inventory: `sudo docker ps -a --format 'NAME={{.Names}} STATUS={{.Status}} IMAGE={{.Image}}'`, followed by a separately scoped row-free SELECT-only custom DocType image/schema comparison. No H2B rerun, cleanup, restart, DB writes/migrations, baseline/OLD PROD/DEV change, or cutover; H1B checkpoint stays protected, off-host restore validation remains pending.

## NEW REHEARSAL STAGE 17V-H2B CUSTOM DOCTYPE STOP — 2026-11-09

**OWNER-REPORTED CONTROLLED STOP, NOT PASS.** Following previously SHA-verified one-use H2B, received exact markers: `STAGE17V_H2B_PRECHECK_VERIFIED`, `STAGE17V_H2B_RECOVERY_SITE_AND_RO_PERMISSIONS_VERIFIED`, `STAGE17V_H2B_ORIGINAL_BASELINE_AND_CHECKPOINT_PRESERVED`, `STOP:STAGE17V_H2B_CHILD_CUSTOM_DOCTYPES`, `STOP:STAGE17V_H2B_APP_READ_PROBE_NOT_ALL_PASSED`, `STAGE17V_H2B_REVIEW_EPHEMERAL_HELPER_STATE_NO_BLIND_RETRY`. This is failure at custom DocType probe, not evidence of clone corruption, nor full application acceptance. H2B helper container state and complete postflight preservation are **unverified**; do not infer these from earlier precheck markers. GitHub review checkpoint `f665cf3` includes source definitions for Work Request, Withdrawal Slip, Intercompany Material Billing Batch, but presence and compatibility within pinned runtime image or historical Nov5 clone are unproven.

**Next safe one-step operator diagnostic, on NEW only:** `sudo docker ps -a --filter "name=ccpc_stage17v_h2b_probe_20261109" --format 'NAME={{.Names}} STATUS={{.Status}} IMAGE={{.Image}}'` and return its sanitized output. No H2B/H2A/H1B/G replay, container deletion/restart, DB change/migration, baseline/old PROD/DEV modification, or cutover. Once helper absence/status is established, review a separately bounded SELECT-only metadata/image differential check if needed. Keep H1B same-host checkpoint protected; off-host/restored rollback and current-source cutover remain pending.

## NEW REHEARSAL STAGE 17V-H2B SELECT-ONLY ADAPTED CLONE FRAPPE PROBE PREPARED — 2026-11-09

**PREPARED / NOT EXECUTED on NEW.** Following owner-reported Stage17V-H2A PASS and H1B consistent local checkpoint PASS, a one-use H2B application test script was created locally as `stage17v_h2b_app_probe.py`, **28,194 UTF-8 bytes**, `py_compile` PASS, child Python source separately AST parsed, static safety checks for stdin/no credential-in-argv, exact Docker nonroot/readonly helper arguments PASS, **SHA-256 `2faf00f723637d31229e9d96689d2662133421be6ce16dbde1b3200c816328ac`**. Source is a conversation attachment only, not a GitHub code commit; GitHub stores scoped plan/hash. User should transfer via already established public-key SSH to NEW `ccpcadmin@192.168.50.186`, independently verify SHA256, then receive a separate exact run instruction. **No container test has yet been run.**

**Target and guards:** Strict NEW `ccpcerp-prod`, sudo `ccpcadmin`, local default Unix Docker context, pinned `ccpcerp:v16.50.0` app image and MariaDB11.8/Redis8.6 immutable IDs, exactly the 3 original-baseline plus 3 clone MariaDB/Redis persistent containers, separate two internal nonattachable IPv4 bridges (no office LAN overlap), eight named volumes, original baseline/clone service mount identities, zero extra containers, no published port. Verify root-only H1B checkpoint (exact four files with unchanged SHA256/size in root 0700 directory), owner-only fresh H2A credential `readonly-h2a.env` format, pinned Nov5 original source config, unchanged real clone `sites` tree and exact site/common/apps safety flags and private attachment digest. Confirm clone DB 741 base tables (738 InnoDB/3 MyISAM), six sequences, four Company rows and DocType/User/Singles counts, exact H2A account restricted to free clone bridge network IP +250 with **SELECT only** schema privileges and no other role/global/table/proxy privileges; check clone Redis queues empty. **No new database account, backup or volume is created by H2B.**

**One-time test runtime:** Disposable `docker run -i --rm --pull never` helper named `ccpc_stage17v_h2b_probe_20261109`, fixed `--ip` matched to H2A grant on clone internal bridge, UID/GID1000, **read-only rootfs**, drop all Linux capabilities, no-new-privileges, bounded pids/memory/cpu and subprocess timeout, *only* small writable scratch sites/tmp tmpfs, no external mounts, host ports, production credentials or historical encryption key. Scratch `site_config.json`/common/apps are synthesized inside helper with clone DB schema, H2A SELECT-only user/password delivered through **stdin** (not environment, CLI args, Docker inspect, or a persistent file), remote Redis endpoints pointed to unavailable loopback, maintenance/scheduler/mail OFF. Execute pinned Bench virtualenv Python with `FRAPPE_STREAM_LOGGING=1`: adapted clone `frappe.init` + `frappe.connect`, verify server `CURRENT_USER()` matches exact grant-bound H2A identity, 4-Company SQL/DocType/ORM reads, and metadata/limited read on three custom GitHub-review-branch DocTypes **Work Request**, **Withdrawal Slip**, **Intercompany Material Billing Batch**. Child stdout/stderr suppressed except predeclared phase markers; do not print business record values, actual usernames, private filenames, errors/tracebacks, passwords or encryption keys. Host postchecks ensure ephemeral helper is removed, six original containers/two networks/eight named volumes and H1B/clone site hashes remain unchanged, clone Redis still idle. No persistent backend/frontend/worker/scheduler/mailer/webhook, migrations, SQL DDL/DML, owner business writes, OLD PROD/DEV, baseline modification, or final release.

**Boundary and failure protocol:** This tests **application behavior with synthetic SELECT-only configuration against the REAL cloned Nov5 DB**; it does NOT initialize the actual restored site config, test login/HTTP/authorization, custom business posting, migrated schema, emails/Redis/queue behavior, or production readiness. `internal=true` alone is not conclusive absolute network egress protection; no arbitrary user/plugin action is invoked, but known pinned app startup hooks may run. If missing custom DocType or version mismatches, report sanitized child phase STOP and inspect; do not infer corruption. If helper times out or remains attached, **do not blind rerun/force-clean**; inspect helper state first. The H1B checkpoint is same-host and not restore-tested/offsite; real release requires independent rollback validation/current source snapshot/separate user approval.

## NEW REHEARSAL STAGE 17V-H2A SELECT-ONLY CLONE ACCOUNT PASS — 2026-11-09

**PASS — owner-reported NEW-only execution of hash-verified `stage17v_h2a_readonly_account.py`:**

```text
STAGE17V_H2A_PRECHECK_VERIFIED
STAGE17V_H2A_RECOVERY_CHECKPOINT_VERIFIED
STAGE17V_H2A_FIXED_PRIVATE_HELPER_IDENTITY_AVAILABLE
STAGE17V_H2A_NEW_SELECT_ONLY_SECRET_CREATED
STAGE17V_H2A_SELECT_ONLY_ACCOUNT_AND_GRANT_CREATED
STAGE17V_H2A_SELECT_ONLY_PERMISSIONS_VERIFIED
STAGE17V_H2A_ORIGINAL_BASELINE_PRESERVED
STAGE17V_H2A_NO_APPLICATION_STARTED
STAGE17V_H2A_READONLY_ACCOUNT_READY
```

H2A owner-run prechecks reported clone DB/schema and H1B root-private logical checkpoint intact; **new SELECT-only identity `ccpc_h2_ro_20261109` restricted to the fixed isolated clone bridge IP** was created only in cloned MariaDB, with one schema-level SELECT grant and no global/table/column/routine/role/proxy/other privileges; its fresh 64-hex secret is held privately in `/home/ccpcadmin/.ccpc-full-acceptance-secrets-20261107/readonly-h2a.env` (0600, private 0700 parent). Original restored baseline reportedly unchanged; no app/runtime services, OLD PROD/DEV, migrations or production release actions. Evidence is owner terminal sanitized markers, not direct NEW-host readback. **Do not rerun H2A**; account already exists and exclusive secret file is created. Existing same-host H1B checkpoint is still not off-host or independently restore-tested.

**Next Stage17V-H2B:** Use a new one-time nonprivileged read-only-rootfs app-container probe pinned to exact `ccpcerp:v16.50.0` image, on clone-only private bridge at the fixed grant-bound IP. Obtain *only* the new SELECT-only diagnostic secret (never transfer full-write clone password/historical encryption key); create an ephemeral synthetic site config on tmpfs with DB host fixed clone DB and safe flags, disable external Redis/mail/queue/scheduler, and test selected Frappe/ERPNext/ccpcerp DocType/ORM reads. Guard all six baseline+clone DB/Redis service containers, two internal networks, eight volumes and original checkpoint before/after; redact table rows/secret values/tracebacks in owner terminal. No persistent app, worker, scheduler, HTTP, SMTP/webhook, SQL writes, migrations or OLD PROD/DEV. **H2B not yet created or run.** Later test full site access/recovery/real workflows only after separate constrained plan; current Nov5 data remains historical rehearsal snapshot.

## NEW REHEARSAL STAGE 17V-H2A SELECT-ONLY CLONE ACCOUNT SCRIPT PREPARED — 2026-11-09

**PREPARED, NOT EXECUTED ON NEW.** One-use `stage17v_h2a_readonly_account.py` artifact, **18,469 UTF-8 bytes**, local Python `py_compile` and static no-`shell=True`/no-`docker run` check passed, **SHA-256 `3f660844af54c06508908f67409b1619dbd265e47905a261b3bfd5ea8c01df24`**. Executable is a conversation file download, not committed in GitHub. Operator must transfer with the known Windows SSH identity to NEW `ccpcadmin@192.168.50.186` and verify SHA256 on NEW, then separately execute only after hash match. Never auto-run a downloaded script. Current Stage17V-H1B private local clone checkpoint is COMPLETE as reported, remains off-host=false and restore_tested=false; original baseline intact.

**Intended narrowly bounded mutations:** New diagnostic account `ccpc_h2_ro_20261109` in **CLONE MariaDB only** with host restricted to one free fixed private IP derived from `ccpc_full_acceptance_20261107_default` IPv4 internal network (network address +250, verified in subnet, unused and not gateway). **Only** `GRANT SELECT ON <validated restored clone schema>.*`, zero global grants, zero separate table/column/routine/role/proxy privilege and every other MariaDB `mysql.db` privilege flag `N`. Generates a fresh cryptographically random 64-hex password and exclusive `0600` `/home/ccpcadmin/.ccpc-full-acceptance-secrets-20261107/readonly-h2a.env` owned by ccpcadmin within preexisting `0700` directory. Sends SQL over Docker-exec **stdin**, never putting password on host argv, Docker env, stdout or GitHub; no shared/historical/application DB password reuse. No persistent application/frontend/worker/scheduler, no SMTP/webhooks/external integrations, no SQL business rows or table DDL, no site config/archives edits, no new containers/networks/volumes and no OLD PRODUCTION/DEV/baseline changes.

**Guards:** Exact NEW sudo operator/local Docker socket and pinned app/MariaDB/Redis image IDs, six expected 3+3 support containers on two separate internal nonattachable IPv4 bridges with eight original+clone named volumes, no published ports/restarts and expected cloned support mounts. Requires root-owned 0700 H1B checkpoint with exactly four 0600 files whose SHA256/size match its private manifest, correct previously imported Nov5 restored schema (741 BASE TABLE: 738 InnoDB, 3 MyISAM; 6 SEQUENCE; 4 companies, 814 DocType, 7 User and 1000 Singles), preserved 280-byte SHA-pinned original site config and clone-only credential bounds, empty clone Redis, unused candidate username across MariaDB privilege metadata, and unoccupied fixed helper IP. Before first mutation prints scoped precheck markers; postchecks exact one account/one schema-SELECT grant/no other privileges and original six services/eight volumes/two networks unchanged. On any STOP after exclusive secret creation preserve partial user/file and DO NOT rerun/cleanup without new inventory; no automated retry.

**Next after H2A PASS:** One-use, nonroot, no-capability, read-only-rootfs ephemeral `ccpcerp:v16.50.0` helper on **clone network only** at the matching fixed IP, with **synthetic disposable site config** substituting the SELECT-only account, no mount or exposure of full-write restored clone site credentials/encryption key, and remote Redis/side-effect calls disabled, to verify Frappe/ERPNext/CCPCERP DocType/ORM queries against clone. Verify no write access and runtime network isolation before running. This will not by itself establish full HTTP/UI authorization, business posting, intercompany or production readiness; later separate staged full-site acceptance requires rollback/off-host recovery and explicit scope. Final PROD cutover separately approved after current-source backup and rollback testing.

## NEW REHEARSAL STAGE 17V-H1B PRIVATE CLONE CHECKPOINT PASS — 2026-11-09

**PASS — owner-reported successful one-use H1B execution on NEW `ccpcadmin@ccpcerp-prod`, after prior SHA256 verification:**

```text
STAGE17V_H1B_PRECHECK_VERIFIED
STAGE17V_H1B_CLONE_SITE_DB_AND_FILES_VERIFIED
STAGE17V_H1B_CLONE_SQL_CHECKPOINT_VERIFIED
STAGE17V_H1B_CLONE_SITES_AND_PRIVATE_FILE_CHECKPOINT_VERIFIED
STAGE17V_H1B_CLONE_CREDENTIALS_CHECKPOINT_PRIVATE
STAGE17V_H1B_BASELINE_UNCHANGED
STAGE17V_H1B_NO_APPLICATION_OR_SCHEMA_MUTATION
STAGE17V_H1B_LOCAL_CHECKPOINT_CREATED_RESTORE_NOT_TESTED
```

**Result/evidence:** The previously SHA256-pinned `stage17v_h1b_checkpoint.py` (hash `76cfab138cb4c4ce359271e183b397f1dcf0665c102978acf40df4d6621c0488`) successfully completed all Stage17V-H1B markers. Exact NEW-only cloned MariaDB 738 InnoDB / 3 MyISAM base-table distribution and 6 sequences, historical Nov5 four-company schema, site config and single private attachment were guarded. Independent root-private checkpoint directory `/home/ccpcadmin/.ccpc-full-acceptance-checkpoint-20261109-h1b/` (0700) now holds four 0600 artifacts: `clone-db.sql.gz` (consistent logical dump using `mariadb-dump --skip-single-transaction --lock-all-tables --quick` for both InnoDB and MyISAM; global read lock during dump), `clone-sites.tar.gz` (exact site tree and attachment), `clone-secrets.tar.gz` (clone-only credentials), `manifest.json` (sizes, digests, expected identity and `restore_tested=false`, `off_host=false`). Script reports digest/readback and unchanged original restore baseline, no application/schema mutation, and no app or scheduler startup. User supplied sanitized terminal output; this does not provide independent NEW-host access. **Do not rerun H1B; it is exclusive/one-use.** Keep private checkpoint intact; never share secret tar, SQL data, or raw manifest contents in chat/GitHub.

**Major limitations:** This is a **same-host backup**, not an off-host disaster recovery copy or a restore test. The original Nov5 source remains historical and is not a current source-consistent final migration snapshot. No persistent Frappe backend/HTTP/authentication/custom workflow tests have been executed against the full independent clone yet. OLD PRODUCTION, DEVELOPMENT, and baseline restore remain protected. Live cutover, live-data backup, rollout, rollback and go-live require independent explicit owner approval.

**NEXT Stage17V-H2:** Move to a clone-only SELECT-restricted application-layer test using the pinned `ccpcerp:v16.50.0` image, with DB writes impossible from the diagnostic identity and no persistent app, worker, scheduler, mail, webhook, frontend or proxy services. The new clone database has a write-capable application user, so **do not** launch a generic Frappe process with its real `site_config.json` before establishing an isolated read-only DB identity/secret and an egress/side-effect barrier. Check current GitHub current custom-app branch/features before picking representative custom DocTypes/queries; use controlled one-use diagnostic helper with fixed clone-network source identity, isolated tmpfs and nonroot/no-capability settings. Later verify a real login/HTTP path and actual transaction workflows only after isolating rollbacks and separate bounded approval. No further SQL import, table engine conversion or automatic migration.

## NEW REHEARSAL STAGE 17V-H1A ENGINE CLASSIFICATION PASS; H1B CORRECTED CHECKPOINT PREPARED — 2026-11-09

**H1A PASS — owner-run READ-ONLY NEW-only SQL metadata diagnostic:**

```text
STAGE17V_H1A_READ_ONLY_PREFLIGHT_PASS
BASE_ENGINE_INNODB=738
BASE_ENGINE_MYISAM=3
NON_INNODB_BASE_TABLES=3
NON_INNODB_STANDARD_SEARCH_INDEX=0
NON_INNODB_OTHER_TABLES=3
STAGE17V_H1A_READ_ONLY_DIAGNOSTIC_COMPLETE
```

Exactly 741 base tables: **738 InnoDB, three MyISAM**, with zero non-InnoDB `tabSearch Index` tables. The existing H1 safety STOP was expected for three MyISAM tables and occurred before its first host checkpoint write. This does not indicate a damaged restore and **does not warrant ALTER TABLE, engine conversion, schema migration, SQL reimport, or deletion**. H1A was SELECT-only and performed no DB writes. Do not rerun original H1.

**H1B one-use revised checkpoint prepared / NOT executed:** Reviewed local artifact `stage17v_h1b_checkpoint.py`, **24,706 UTF-8 bytes**, Python compilation and static review passed; **SHA256 `76cfab138cb4c4ce359271e183b397f1dcf0665c102978acf40df4d6621c0488`**. Executable file is provided as a conversation attachment, not committed to GitHub; this entry records its hash/constraints. Transmit via existing Windows private-key SSH to NEW `ccpcadmin@192.168.50.186`; independently verify SHA on NEW before separately running. Never rerun failed `stage17v_h1_checkpoint.py` or overwrite any partially created H1/H1B directory. H1B rejects an occupied old H1 directory and uses a distinct root-only `/home/ccpcadmin/.ccpc-full-acceptance-checkpoint-20261109-h1b/` (0700, private 0600 archives).

**Correction and consistency:** H1B retains original six pinned clone/baseline containers, 8 volumes, two isolated internal bridges, clone DB/schema/file/config/credentials/side-effect-off guards and read-only source backup hash. It checks exactly **738 InnoDB and 3 MyISAM** tables and no other base-table engines. Original `mariadb-dump --single-transaction --skip-lock-tables` is replaced by `mariadb-dump --skip-single-transaction --lock-all-tables --quick`. Per official MariaDB `mariadb-dump` documentation, `--lock-all-tables` acquires a global read lock (`FLUSH TABLES WITH READ LOCK`) for the entire dump, preventing concurrent modifications of MyISAM and InnoDB while dumping; `--single-transaction` is not guaranteed consistent for MyISAM. Reference: https://mariadb.com/docs/server/clients-and-utilities/backup-restore-and-import-clients/mariadb-dump . Before any output files, H1B checks the container has `timeout` and the dump lock option. A child process timeout (125s + 5s kill grace) bounds the global lock duration; the host Docker exec has a longer 160s timeout. No app server/workers/scheduler/mail/integration/HTTP processes or SQL DML/DDL are requested. The global read lock temporarily blocks writes **inside the clone DB** while snapshot is taken; it should not reach OLD PROD/DEV or original baseline. Creates root-private clone SQL dump, sites/attachment tar, clone-only secret tar and manifest, with SHA digests/readback and postchecks. **Local host checkpoint is not an offsite backup; recovery remains untested.** On any STOP after write, preserve partial checkpoint without rerun/delete/auto-clean. The checkpoint is not created until operator reports successful run.

**Current delivery gate:** Owner has approved Stage17V-H restricted acceptance, not final go-live. **NEXT** owner transfers H1B script, reports NEW-host SHA256 verification; only then execute bounded one-use H1B. Once successful, test recovery/off-host copy as a separate gate, then real app read-only/functional acceptance without live external side effects; no old PROD/DEV modifications, migrations or production cutover.

## NEW REHEARSAL STAGE 17V-H1 NONTRANSACTIONAL ENGINE PREFLIGHT STOP — 2026-11-09

**STOP BEFORE ANY WRITES — operator-run NEW `ccpcadmin@ccpcerp-prod`:** Owner ran SHA256-verified one-use `stage17v_h1_checkpoint.py` and reported solely `STOP:STAGE17V_H1_NONTRANSACTIONAL_TABLE_REVIEW_REQUIRED`. Inspected exact locally archived script SHA256 `28cef42ea98fed81d9f7090bcbfbc1c13a868f83bb9d298a8aaa8b841246442a`: the guard checks `information_schema.tables` for any `BASE TABLE` in the cloned Nov5 schema whose `ENGINE IS NULL OR ENGINE <> 'InnoDB'`, and this check occurs **before** `WRITES_STARTED=True` and `os.mkdir(CHECKPOINT,...)`. The script's preflight passed earlier host/Docker/schema/count/credential checks (some do not emit markers until later); SQL operations through the STOP are SELECT-only. **No local H1 checkpoint directory, SQL dump, credential tar, site tar or Docker/database/site mutation is created by this halted script.** This is a consistency-method guard, **not** proof of database corruption, restored data loss or app incompatibility. Operator console is evidence, not remote host inspection.

**Do not rerun H1**: it will repeat the same STOP until the checkpoint design is revised for actual storage engines. **Next single safe Stage17V-H1A read-only diagnostic:** NEW-only guarded `docker exec` clone MariaDB **SELECT** of `information_schema.tables` for the one restored non-system schema, grouped by `table_type` and `ENGINE`; output only aggregate counts and whether a non-InnoDB table is the known Frappe `tabSearch Index` plus count of others, with no schema/table names, business rows, secrets or raw SQL output. Confirm exact clone pinned MariaDB running and on clone internal network, no extra Docker containers/volumes. **No SQL DDL/DML, no checkpoint directory, no app startup, no writes.** Based on exact reported engine distribution and whether the clone is quiescent, review a revised consistent backup method (e.g. MariaDB dump with table locks for nontransactional engines; do not silently remove `--single-transaction` or claim transactional consistency for MyISAM). The on-host checkpoint remains **not created**, and separate off-host/recovery test, actual app acceptance and production go-live remain pending. Original restored baseline, OLD PROD/DEV must remain untouched.

## NEW REHEARSAL STAGE 17V-H1 CLONE RECOVERY CHECKPOINT SCRIPT PREPARED — 2026-11-09

**Owner approved proceeding with Stage17V-H restricted application acceptance.** Before any write-capable Frappe runtime, first create an **isolated local logical checkpoint** of the already prepared historical Nov5 clone. This is **not** a deployment/cutover authorization, not an off-host backup, and not a restore-tested recovery. No NEW-server action has yet been reported for H1.

**Reviewed operator artifact:** `stage17v_h1_checkpoint.py`, 23,051 UTF-8 bytes; local Python `py_compile` passed; **SHA256 `28cef42ea98fed81d9f7090bcbfbc1c13a868f83bb9d298a8aaa8b841246442a`**. Script created in chat artifact runtime and provided separately as a file download, **not committed as executable GitHub source**; only its scope/checksum are documented. Operator must securely SCP through existing NEW server public-key SSH access to `ccpcadmin@192.168.50.186`, then SHA256-verify the exact file on NEW before any execution. One-use script; do not execute if precheck/hash mismatch or repeat after a partial attempt.

**H1 safety and output design:** Host/operator/default-local-Docker checks; exact pinned app/MariaDB/Redis images; current baseline and clone each 3 running DB/Redis containers, exact 8 total named volumes and 2 independent private internal IPv4 networks, no host port binding/restart. Clone DB schema remains the exact expected 741 BASE TABLE + 6 SEQUENCE (zero views), 814 DocType, 7 User, 1000 Singles, 4 Company; all baseline-table engines must be InnoDB for consistent `mariadb-dump --single-transaction`. Clone-only DB app user/grant, root client secret, site env secret protected; clone Redis cache/queue `DBSIZE=0`. Only clone `sites` Docker volume is read; exact Stage17V-G site tree and uid1000 owner/modes, expected app list, internal hosts and maintenance/scheduler/email OFF configuration are compared with SHA-pinned historical encryption key and fresh clone app password (never printed). The NEW-only source backup and restored baseline are not modified.

**One-use local host backup operation:** Fail if output directory exists; create exactly `/home/ccpcadmin/.ccpc-full-acceptance-checkpoint-20261109-h1/` root-owned mode 0700, with root-only 0600 `clone-db.sql.gz` (MariaDB 11.8 container's `mariadb-dump` from clone socket using secret-file credential, consistent InnoDB snapshot, routines/events/triggers), `clone-sites.tar.gz` (allowlisted restored site config and one private attachment), `clone-secrets.tar.gz` (three fresh clone-only credential files), and `manifest.json` (artifact digests/size, no secret values). No Docker container/volume creation/restart, DB/schema/row writes, site edits, application startup, external port/DNS/net changes, OLD PROD/DEV changes, or historical source change. Readback verifies gzip/tar shapes, file digests/private permissions and identical baseline/clone resource inventories. STOP after any attempted directory/file creation means preserve partial contents and **do not rerun, delete or auto-clean**. The logical checkpoint is **on the same NEW host disk**, and **no restore has been tested**; separate off-host copy and actual rollback restoration test remain later gates.

**After successful H1:** Plan Stage17V-H2 app-level **SELECT-only** clone diagnostic, with app DB write credentials fenced off, no persistent backend/frontend/websocket/worker/scheduler/mail/integrations, then practical acceptance of actual custom workflows. Existing Nov5 backup remains historical rather than final source-consistent cutover data. User must separately approve any actual PRODUCTION release, live source backup/migration and DNS switch.

## NEW REHEARSAL STAGE 17V-G CLONE ATTACHMENTS RESTORED AND VERIFIED — 2026-11-09

**PASS — owner-reported NEW-only one-use restore from Nov5 protected public/private archives to independent full-application clone.** The owner previously transferred `stage17v_g.py` (pinned SHA-256 `2c850375ec01cddb0d84bdde7b7c43dd814a23d19d9074fae1729647f5c17827`) to NEW `ccpcadmin@ccpcerp-prod` and reported hash verification. The executed command's output contains the exact nine success markers:

```text
STAGE17V_G_PRECHECK_VERIFIED
STAGE17V_G_PINNED_ARCHIVES_AND_STRICT_LAYOUT_VERIFIED
STAGE17V_G_CLONE_STAGE_F_SITE_CONFIG_UNCHANGED
STAGE17V_G_PUBLIC_FILES_DIRECTORY_RESTORED
STAGE17V_G_PRIVATE_FILE_RESTORED_AND_VERIFIED
STAGE17V_G_EXISTING_CLONE_CONFIG_UNCHANGED
STAGE17V_G_BASELINE_PRESERVED
STAGE17V_G_NO_APPLICATION_OR_SQL_MUTATION_STARTED
STAGE17V_G_ATTACHMENT_RESTORE_COMPLETE
```

**Result:** The separate `ccpc_full_acceptance_20261107` clone has a historically restored MariaDB schema (**741 BASE TABLE**, **6 SEQUENCE**, four Company records), separate cloned MariaDB/Redis support services, separately generated schema-scoped clone-only application DB credential, prepared `ccpcerp.local` site config retaining Nov5 encryption key and disabling maintenance-sensitive side effects, and now the exact archive public/files directory (empty) plus single private file under `private/files`, with source member type/hash/layout and target content digest verified. Stage17V-G postchecks report previous site/common/apps file bytes unchanged, original baseline six-vs-three support service separation preserved, no Frappe app/HTTP/worker/scheduler startup, SQL rewrite, migration, or OLD PRODUCTION/DEVELOPMENT operation. **This is operator console evidence, not independent live host access.** Do **not** rerun Stage17V-G because files now exist, and do not rerun Stages V-C through V-F or prior SQL import.

**NEXT Stage17V-H (bounded readiness/acceptance gate):** Before any Frappe app runtime with a full-write clone account, perform a **read-only** clone-specific host/volume/site/DB/network security and compatible-image inspection. Confirm expected clone site and attachment state; check pinned app image contains the intended Frappe/ERPNext/ccpcerp apps and that UID1000 can read the clone's files without publishing ports. Assess remaining runtime side effects, Redis/mail/webhooks and clone network host-gateway/egress exposure. Prefer a one-shot, nonprivileged read-only-rootfs app diagnostic with SELECT-only clone DB access (or otherwise safely constrained) *after* the runtime safety review; avoid starting persistent backend/frontend/workers/scheduler before this gate. Distinguish observed process-level Frappe/HTTP/functionality tests from present offline checks. No automatic migrate, submit, posting, email, integrations, or approval of actual PROD cutover. Final current source-consistent backup, independent rollback and separate explicit go-live approval remain prerequisites.

## NEW REHEARSAL STAGE 17V-G CLONE ATTACHMENT SCRIPT PREPARED — 2026-11-09

**PREPARED / NOT EXECUTED on NEW.** One-use `stage17v_g.py` prepared in conversation artifact runtime, **24,001 UTF-8 bytes**, syntax compiled and AST-checked (no `tar.extract`/`extractall`, no network call or `shell=True`); **SHA-256 `2c850375ec01cddb0d84bdde7b7c43dd814a23d19d9074fae1729647f5c17827`**. Executable bytes are in the conversation attachment, **not GitHub**; GitHub records the scope/hash. Operator should SCP through existing Windows public-key SSH path to NEW `192.168.50.186`, then compare this exact SHA-256 on NEW before a separate execution step. No automatic download/execution.

**Planned Stage17V-G source/target and preflight:** Exact NEW host/operator/default Unix Docker socket; pinned immutable app/DB/Redis images; baseline and clone support services remain exactly six containers, eight named volumes and two separate private non-attachable internal IPv4 bridges; cloned MariaDB retains 741 BASE TABLE+6 SEQUENCE, 814 DocType, 7 User, 1000 Singles, 4 Company; clone-only app-user grant on exactly that schema. Read SHA-pinned 280-byte Nov5 backup site config only in-memory (no historical password output); verify new clone-only site password, historical encryption key, `maintenance_mode=1`, scheduler disabled/paused, mute-emails, internal Redis/DB names. Verify exact `ccpc_full_acceptance_20261107_sites` Docker-local mountpoint identity, Frappe UID1000/modes and **exact Stage17V-F site tree** with no `public` or `private` yet; record site/common/apps in-memory SHA-256 fingerprints. Source public/private archives use previously verified Nov5 SHA256 `200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6` and `60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf`, fixed sizes 10,240 and 20,480 bytes, 0600 source owner-only files. Require **exact** original member path strings `./ccpcerp.local/public/files` (one directory) and `./ccpcerp.local/private/files` (one directory plus one direct regular private file with single safe filename). Reject other tar members, types, symlink/hardlink/traversal/directory mismatches; private name/data never printed. No general tar extraction.

**Intended write:** After all preflights, create **only** `ccpcerp.local/public/files` (empty) and `ccpcerp.local/private/files/<single-safe-basename>` inside clone sites. Use root operator with Docker-confirmed exclusive clone-only volume, `dir_fd` + `O_NOFOLLOW` directory walking and `O_EXCL` for private file, Frappe UID1000 ownership and modes, fsync/file-digest verification. Reverify original site/common/apps fingerprints, six support containers/eight volumes, baseline/clone network identities and no application startup. **No Frappe service, SQL/backup mutation, second schema import, mail, integrations, workers, migrations, bridge/port changes, OLD PROD/DEV activity or final cutover.** If STOP after first write, **preserve partial site tree, do not rerun or clean automatically**. Static syntax check does not prove success on NEW. After a verified attachment restore, move to independently isolated app read/HTTP/functional acceptance; actual go-live still needs separately approved fresh backup/rollback and current-source cutover.

## NEW REHEARSAL STAGE 17V-F CLONE SITE-CONFIG PASS — 2026-11-09

**PASS — owner-reported execution on NEW `ccpcadmin@ccpcerp-prod` after SHA256 verification of one-use `stage17v_f.py`:**

```text
STAGE17V_F_PRECHECK_VERIFIED
STAGE17V_F_CLONE_EMPTY_SITES_VOLUME_VERIFIED
STAGE17V_F_NEW_CLONE_APP_SECRET_AND_HISTORICAL_KEY_VERIFIED
STAGE17V_F_CLONE_SITE_CONFIG_CREATED
STAGE17V_F_CLONE_COMMON_CONFIG_AND_APPS_CREATED
STAGE17V_F_SITE_UID1000_PERMISSIONS_AND_READBACK_VERIFIED
STAGE17V_F_BASELINE_PRESERVED
STAGE17V_F_NO_APPLICATION_OR_FILE_ARCHIVE_RESTORE_STARTED
STAGE17V_F_SITE_CONFIG_PREPARED
```

Clone `ccpc_full_acceptance_20261107_sites` now contains `ccpcerp.local/site_config.json`, `common_site_config.json`, `apps.txt`. Stage17V-F owner-run guards verified independently restored Nov5 741+6 DB and four Company records, NEW-only clone application password distinct from historical/clone-root credentials, and original historical encryption key retained without printing. Site tree permissions and config read-back verified for UID1000; internal DB/Redis aliases, maintenance=1, scheduler disabled/paused, mail muted, developer off. **Original protected baseline preserved.** No file archive restoration, Frappe backend/frontend/worker/scheduler startup, SQL import, migrations, OLD PROD/DEV or go-live actions reported. Evidence is sanitized operator output; GitHub has no live server read. **Do not rerun F** because the sites tree is no longer empty.

**Next owner-approved Stage17V-G:** Restore only historical Nov5 `./ccpcerp.local/public/files` (empty directory) and `./ccpcerp.local/private/files` (one direct file) from SHA-pinned, previously inspected tar archives into already initialized **clone-only** `sites` volume. Guard unique clone volume mapping, exact existing site-config tree, source hash+layout/type without printing private filename, reject traversal/symlinks/overwrites, use exclusive nofollow creation, verify digest and unchanged config/old baseline, stop without retry or cleanup on partial failure. **No app startup, worker/scheduler, email, integrations, migrations, external network or old host changes.** Then separate app/functional acceptance; Nov5 remains historical, final fresh backup/rollback and separately approved go-live required.

## NEW REHEARSAL STAGE 17V-F CLONE SITE CONFIG SCRIPT PREPARED — 2026-11-09

**PREPARED / NOT EXECUTED on NEW:** One-use Python script `stage17v_f.py` created locally, **19,356 UTF-8 bytes**, syntax checked with `py_compile`, **SHA-256 `d6480be3174071c0b0f898980eabdc28913c2a49025124e7daa0ba7097351bb4`**. Offered as a conversation file transfer; the executable artifact is **not committed to GitHub**. Operator is to transfer with existing private-key SCP to NEW `192.168.50.186`, then independently hash-check on NEW before execution. Do not run on hash mismatch or automatically retry any partially written site volume.

**Reviewed bounded scope:** Exact NEW hostname, sudo operator, local Docker daemon, pinned `ccpcerp:v16.50.0`, MariaDB11.8 and Redis8.6 immutable IDs, **six containers, eight volumes, two distinct internal IPv4-only bridges**, no public port/restarts, strictly independent clone DB/cache/queue mount contracts. Existing clone schema must have **741 BASE TABLE, 6 SEQUENCE, 0 VIEW, 814 DocType, 7 User, 1000 Singles and 4 Company**, and the single schema-scoped clone-only app account/grant must exist. Checks pre-existing clone `site-db.env` and DB root secret are mode 0600, owner-only secret directory 0700; new application password differs from historical DB password and clone root. Reads the SHA256-pinned 280-byte Nov5 source site config **in memory**, retaining only schema name and historical `encryption_key`. Source backup directory/metadata and schema identity checked. Before first write, verifies clone-only `ccpc_full_acceptance_20261107_sites` Docker mountpoint is **exactly** `<verified Docker root>/volumes/<clone-sites>/_data`, distinct from original baseline, and empty. Then with host-root permissions creates only the clone Frappe sites tree owned UID:GID 1000:1000: sites root and `ccpcerp.local` mode 0750, `site_config.json` mode 0600, `common_site_config.json` and `apps.txt` mode 0640; **exclusive create / no overwrite**. Site config carries new clone-only `db_password`, original `encryption_key`, internal `db` host/port, and `maintenance_mode=1`, `disable_scheduler=1`, `pause_scheduler=1`, `mute_emails=1`, `developer_mode=0`. Common config uses only internal Redis service aliases and same safety flags. Apps list `frappe, erpnext, ccpcerp` from pinned known image. Verifies exact byte-for-byte in-memory readback (no secret output) and original six-container/two-network/eight-volume scope unchanged. It **does not** start any Docker helper or application, touch backup/SQL/other Docker volumes, enable jobs/email/integrations, restore file archives, migrate or affect OLD PRODUCTION/DEVELOPMENT.

**STOP/partial handling:** Once volume ownership/content writes start, any error leaves clone sites unchanged as far as possible, reports possible partial state, and **must not be rerun or deleted blindly**. This is static local syntax and scope review only; not an integration test on NEW. After successful Stage17V-F, the next separate phase restores only the already verified Nov5 public/private tar member paths using strict file-by-file semantics, then controlled app validation. No final production go-live authorization.

## NEW REHEARSAL STAGE 17V-E CLONE APP-DB ACCOUNT PASS — 2026-11-09

**PASS — owner-reported NEW-only run of SHA256-verified one-use `stage17v_e.py`:** `STAGE17V_E_PRECHECK_VERIFIED`, `STAGE17V_E_EXISTING_CLONE_SCHEMA_VERIFIED`, `STAGE17V_E_APP_DB_IDENTITY_UNUSED`, `STAGE17V_E_CLONE_APP_SECRET_CREATED_PRIVATELY`, `STAGE17V_E_CLONE_APP_USER_AND_SCHEMA_GRANT_CREATED`, `STAGE17V_E_CLONE_SCHEMA_SCOPED_GRANTS_VERIFIED`, `STAGE17V_E_BASELINE_PRESERVED`, `STAGE17V_E_NO_APPLICATION_STARTED`, `STAGE17V_E_APP_DB_ACCOUNT_READY`. The independent clone's app DB login name now matches its Nov5 historical schema name, but the **password is newly generated and unique to this clone**, owner-only `0600` `/home/ccpcadmin/.ccpc-full-acceptance-secrets-20261107/site-db.env` in `0700` secret directory. Grants verified only on exact restored clone schema, no global access or extra table/routine/role/proxy grants. This creates no actual ERPNext app/site runtime. Original `ccpc_restore_rehearsal_20261107` baseline reportedly preserved; no OLD production/DEV operation. Do **not** rerun Stage17V-E or re-create the account.

**NEXT Stage17V-F — cloned site-config preparation, no services:** Clone-only `sites` volume is expected empty from Stage17V-C/D/E. Build private `ccpcerp.local/site_config.json` with exact SHA-pinned Nov5 historical `encryption_key` and schema ID but the new clone-only `APP_DB_PASSWORD`; set `db_host=db`, `db_port=3306`, internal-only Redis endpoints, maintenance=1, disable/pause_scheduler=1, mute_emails=1, developer_mode=0. Prepare the clone-only common_site_config and apps.txt for pinned frappe/erpnext/ccpcerp app image using strict owner UID1000/GID1000 and file modes; never run stock configurator, create-site, bench migrate, app/backend/frontend/worker/scheduler, email or external integration. Before writing, assert exact NEW host/operator/local Docker, six pinned containers/two internal networks/eight distinct volumes, unchanged original baseline, protected source config SHA256 and clone credential metadata, and exact empty sites volume mountpoint. Writes must be **exclusive** to clone sites volume and verified afterwards; partial failure stops without retry/delete. Later restore public/private Nov5 file archives using strict member validation, then guarded app tests with side effects off. Historical snapshot only; new current backup+rollback and separate go-live consent remain outstanding.

## NEW REHEARSAL STAGE 17V-E CLONE APP-DB ACCOUNT SCRIPT PREPARED — 2026-11-09

**PREPARED / NOT EXECUTED.** After Stage17V-D pass, one-use NEW-only `stage17v_e.py` (17,620 UTF-8 bytes) was created and Python syntax checked locally. **Exact file SHA-256:** `789fe7b92503e7c2348dda58629fa50f90270e37e65f9b8eb2396942eef2484b`. File itself is a separately provided conversation download, not a GitHub-committed operator artifact; this GitHub record pins the reviewed intent and checksum, not script bytes. Operator must transfer securely, verify this exact SHA-256 on NEW before execution, and stop on mismatch.

**Scope / safety checks:** Script verifies NEW `ccpcadmin@ccpcerp-prod` root-through-sudo/local default Docker socket; exact existing baseline and clone 3+3 pinned MariaDB/Redis container scope, eight volumes, two internal non-attachable IPv4 bridges, isolated service mounts; owner-restricted clone DB root-client files and four Nov5 archive metadata; original config SHA-256, original `db_name`, original secret/key presence, and expected restored clone catalog (741 base tables, 6 sequences, 814 DocTypes, 7 Users, 1000 Singles, 4 companies). It confirms that the candidate account has no prior global/schema/table/column/routine/role/proxy grants. Generates a fresh 64-hex **clone-only app DB password**, distinct from historical and clone-root passwords, writes owner-only `site-db.env` with `APP_DB_PASSWORD=` under existing private clone secret directory, and uses clone MariaDB root socket with SQL sent on process **stdin** (password never in process argv/terminal/chat): `CREATE USER '<validated backup db_name>'@'%' IDENTIFIED BY <new>`, `GRANT ALL PRIVILEGES ON <exact cloned schema>.*` to only that new user. **Caveat:** grant is broad within the one clone schema for eventual Frappe functionality, with no server-global privileges; `@'%'` accepts reachable sources inside the already fenced clone internal network. Verifies root account metadata shows zero global access, exactly one target-schema grant with core DML/DDL privileges, no extra grants; postchecks unchanged baseline and clone scope. The script does **not** perform a TCP login as the new app account (a later separate controlled test), start Frappe/web/jobs/worker, restore files, migrate, modify OLD PROD or DEV or cut over. If any STOP occurs after secret-file creation, preserve new file/account/grants and do not rerun, delete or clean automatically; diagnose state. Do not assume an account grant proves functional ERPNext access.

## NEW REHEARSAL STAGE 17V-D CLONE SQL RESTORE PASS — 2026-11-09

**PASS — operator-run on NEW `ccpcadmin@ccpcerp-prod`:** One-use script `/home/ccpcadmin/stage17v_d.py` previously SHA-256 verified by operator against pinned `10d1dfadd3bdae9f5d47066e7e2ae268b328737c1d24dad5bf0eefc8dbc701dc`. On execution the operator reported exactly: `STAGE17V_D_PRECHECK_VERIFIED`, `STAGE17V_D_PINNED_SQL_AND_CONFIG_VERIFIED`, `STAGE17V_D_CLONE_TARGET_EMPTY`, `STAGE17V_D_CLONE_SCHEMA_CREATED`, `STAGE17V_D_CLONE_SQL_IMPORT_CLIENT_EXIT_ZERO`, `STAGE17V_D_RESTORED_BASE_TABLES=741`, `STAGE17V_D_RESTORED_SEQUENCES=6`, `STAGE17V_D_RESTORED_COMPANIES=4`, `STAGE17V_D_BASELINE_PRESERVED`, `STAGE17V_D_NO_APPLICATION_STARTED`, `STAGE17V_D_SQL_RESTORE_COMPLETE`. Reviewed script also validates `tabDocType=814`, `tabUser=7`, `tabSingles=1000` and zero views before final success. The exact historical Nov5 backup source SQL/config SHA256/size were checked; full gzip import used only the new clone MariaDB local root-client secret; original saved Nov5 site DB password was not used. A new schema was created **only within clone project** `ccpc_full_acceptance_20261107`. The original `ccpc_restore_rehearsal_20261107` 3-container/4-volume baseline was verified preserved after import. No new Frappe/web/worker/scheduler, mail/integration activity, file archives or OLD PROD/DEV changes are reported. Result is owner-provided console evidence, not ChatGPT's direct server inspection.

**Do not re-run Stage17V-D**: the clone schema now exists and contains imported data. No drop, truncate, replace, schema migration, container recreation or rollback/cleanup without explicit scoped review. **Next Stage17V-E:** independently create NEW-only least-privileged application DB identity for exactly the restored clone schema with a fresh distinct `0600` secret and tightly scoped schema-only grants, then validate TCP login and catalog count, preserving cloned records and originals. First review the proven prior Stage9/17B account boundary and Stage17V-C credential-file mount shape, preserve encrypted historical key for a later stage, and guard exact six containers/eight volumes/two isolated networks. No reuse of historical DB password or baseline's secret; no scheduler/jobs/email/HTTP/startup or cutover. Site config and public/private archive restoration remain separate later stages. Nov5 database is historical, **not** a current source-consistent production cutover snapshot. Final go-live requires separate owner consent, fresh backup, rollback and migration plan.

## NEW REHEARSAL STAGE 17V-C CLONE SUPPORT SERVICES PASS — 2026-11-07

**PASS — operator-reported execution on NEW `ccpcadmin@ccpcerp-prod`:** `STAGE17V_C_PRECHECK_VERIFIED`, `STAGE17V_C_CLONE_ROOT_SECRET_CREATED_PRIVATELY`, `STAGE17V_C_CLONE_DB_LOGIN_VERIFIED`, `STAGE17V_C_CLONE_REDIS_PING_BOTH_PASS`, `STAGE17V_C_CLONE_SUPPORT_SERVICES=3`, `STAGE17V_C_BASELINE_UNCHANGED`, `STAGE17V_C_NO_APP_OR_SQL_RESTORE_STARTED`, `STAGE17V_C_SUPPORT_LAYER_COMPLETE`. The Stage17V-C one-use Python script, after SHA256 verification on NEW, created NEW-only random MariaDB root secret files under owner-private `/home/ccpcadmin/.ccpc-full-acceptance-secrets-20261107/`, started the clone's `db`, `redis-cache`, `redis-queue` containers with pinned `mariadb:11.8` and `redis:8.6-alpine` image IDs, network `ccpc_full_acceptance_20261107_default`, no host-published ports or auto-restarts, DB volume and Redis queue volume independent, cache on tmpfs, and reported successful clone-local database login / both Redis PING. Source restored baseline remains original 3 containers / 4 volumes; clone now has 3 support containers / 4 volumes. No SQL restore, site config, Frappe backend/worker/scheduler/frontend or OLD PROD/DEV changes were reported. Evidence is the owner's filtered output, not direct host inspection; do not rerun Stage17V-C.

**NEXT Stage17V-D — owner-approved, one-use guarded Nov5 SQL import into independent clone only:** Prepared operator-transfer artifact `stage17v_d.py`, SHA-256 `10d1dfadd3bdae9f5d47066e7e2ae268b328737c1d24dad5bf0eefc8dbc701dc` (15,523 bytes, Python compilation pass; NOT YET RUN on NEW). Before any write it checks exact operator/host/local Docker, original and clone 3+3 container/4+4 volume/network scope, clone DB/Redis identity and mount contracts, private existing clone root-client file, exact protected source backup metadata and pinned Nov5 SQL/config SHA-256 and sizes, valid single schema from source config and intact gzip, clone DB containing system schemas only, capacity reserve. It then creates **only that schema in clone MariaDB**, imports exact trusted historical compressed SQL via a local socket using the clone-only secret file (never historical DB password or site config on process argv), and checks expected Nov5 structural counts: 741 BASE TABLE + 6 SEQUENCE + 0 VIEW; tabDocType=814, tabUser=7, tabSingles=1000, tabCompany=4, without printing business data. No app user/schema privilege creation yet, files tar extraction, Frappe services, external connection, migration, OLD production/DEV changes, or final cutover. **On STOP after any attempted write preserve partial schema/data and do not rerun or drop**; diagnose independently. Script syntax compiled locally but no live run claimed. Operator will transfer and SHA-verify before execution.

## NEW REHEARSAL STAGE 17V-B EMPTY CLONE FOUNDATION PASS — 2026-11-07

**PASS — owner-reported NEW-only manual execution:** `STAGE17V_B_PRECHECK_VERIFIED`, `STAGE17V_B_CLONE_INTERNAL_NETWORK_CREATED`, `STAGE17V_B_CLONE_EMPTY_VOLUMES=4`, `STAGE17V_B_BASELINE_PRESERVED`, `STAGE17V_B_NO_CONTAINERS_OR_RESTORE_STARTED`, `STAGE17V_B_FOUNDATION_COMPLETE`. The terminal paste began with garbled echoed command characters but contains all six exact success markers, including final shell prompt. Guarded Stage17V-B validated exact NEW operator/local Docker, baseline three pinned DB/Redis containers and original 4 volumes/internal network, pinned images and four Nov5 historical source artifacts; created a separate `ccpc_full_acceptance_20261107_default` internal, IPv4-only, non-attachable Docker bridge and exactly four newly named and project-labeled clone volumes `ccpc_full_acceptance_20261107_{db-data,redis-queue-data,sites,logs}`. Its postcheck reports original baseline preserved. No containers, backup extraction, DB import, application startup, DNS/firewall adjustment, OLD PRODUCTION or DEVELOPMENT modification was reported. This is operator-output evidence; ChatGPT cannot independently inspect the NEW host.

**NEXT Stage17V-C — guarded clone-only credential and support service activation under existing isolated NEW-only Stage17V owner approval:** Immediately recheck original baseline and new clone network/volumes, zero clone containers, immutable locally pinned MariaDB/Redis images and no foreign Docker resources. Generate a strong *new* clone database root password only in a unique owner-private `0700` directory, stored in separately protected `0600` files and passed into the database container through a read-only secret bind and `MARIADB_ROOT_PASSWORD_FILE` (never command arguments, Docker env values, terminal output, Git or chat). Launch **only** clone DB, redis-cache and redis-queue with unique service container names, clone-only mounts, no ports/external bridges/restarts. Redis cache on tmpfs; Redis queue persistent clone volume. Verify MariaDB local client authentication and Redis PING, exact six total containers (original three plus clone three), exactly eight intended volumes, no other mounts and unchanged original network identities; fail closed and preserve partial state on errors with **no retry/cleanup**. Do not create the app/schema user, import SQL, create site configs, enable Frappe/HTTP/workers/scheduler or open network ports yet; original Nov5 backup remains untouched. Restore into clone only after next checkpoint; old PROD/DEV unchanged and final cutover separately approved.

## NEW REHEARSAL STAGE 17V-A CAPACITY AND PROTECTED BASELINE PASS — 2026-11-07

**PASS — owner-reported NEW-only read-only preflight output:** `STAGE17V_A_NEW_HOST_VERIFIED`, `STAGE17V_A_BASELINE_REHEARSAL_VERIFIED`, `STAGE17V_A_ALL_PINNED_IMAGES_PRESENT`, `STAGE17V_A_PROTECTED_BACKUP_FILES=4`, `STAGE17V_A_CLONE_NAMESPACE_UNUSED=True`, `STAGE17V_A_CAPACITY_PASS`, `STAGE17V_A_READ_ONLY_COMPLETE_NO_RESOURCES_CREATED`. Available Docker-root storage **733.6 GiB**, baseline volumes **0.26 GiB**, planning reserve **20.0 GiB**, source archives **0.00 GiB rounded** (all four individually verified nonempty; rounded display is not a zero-size finding). The operator-run guard checked exact NEW hostname/operator/local Docker context, pinned app/MariaDB/Redis image IDs, original internal-network 3-running-service/4-volume baseline and no clone network/volume namespace collision, four protected Nov5 archives owner/mode/nonzero size. No new Docker resource, database work, app startup, backup copy or production change is evidenced by this preflight. GitHub records operator-provided markers, not independent live server access.

**NEXT Stage17V-B — owner-approved clone foundation, one bounded NEW-only write step:** Reverify local Docker host and unchanged exact three-service/four-volume restored baseline, pinned local images, backup presence and unused clone namespace immediately before writes. Create **only** a new internal, non-attachable, IPv4-only bridge named `ccpc_full_acceptance_20261107_default` and four *empty*, distinctly named volumes `ccpc_full_acceptance_20261107_{db-data,redis-queue-data,sites,logs}` with unique rehearsal labels. Do **not** start containers, attach the old baseline, restore SQL, access site config/secrets, publish ports, change firewall manually, activate Frappe jobs/integrations, mutate the baseline, run migrations, touch OLD PROD or DEV, or delete resources. Verify all five new resources exist with expected isolation and the pre-existing original 3 containers/4 volumes/network remain unchanged; fail closed and inventory partial creation without automatic cleanup/retry. Later steps will restore the isolated clone with newly generated clone-only credentials, not reuse historical full-write site credentials, then test the app with egress and side effects disabled. No final cutover approval.

## NEW REHEARSAL STAGE 17V INDEPENDENT FULL APPLICATION REHEARSAL APPROVED — CAPACITY/SOURCE PREFLIGHT PENDING (2026-11-07)

**Owner replied `Approved, I hope were almost there` to Stage17V independent protected full-application rehearsal**, after Stage17U successfully initialized a synthetic, safely adapted real-site config and read ERPNext Company DocType/ORM from the Nov5 historical restored NEW-only schema using a SELECT-only account. Owner earlier delegated bounded, nondestructive NEW pre-production preparations without repeated approval loops. This is approval **only for the isolated NEW rehearsal**; **no actual Stage17V clone, container startup, backup, DB write or browser/login test has yet been executed**. Do not interpret owner approval as blanket final go-live permission. Preserve OLD PRODUCTION and DEVELOPMENT and the existing verified `ccpc_restore_rehearsal_20261107` baseline (3 running pinned MariaDB/Redis services, internal isolated network, 4 volumes) unchanged.

**Fastest credible architecture:** Build a **separate, independently recoverable rehearsal copy** from the four already independently verified Nov5 02:00 historical source archives held NEW-only at `/home/ccpcadmin/.ccpc-nov05-backup-transfer-20261106/` (database .sql.gz; public-files tar; private-files tar; original site config JSON). This is safer than byte-copying a live MariaDB Docker volume or running an unconstrained full-write Frappe process against the existing Stage17P–U baseline. Give the clone its own unique Compose project, separate internal network, isolated DB + Redis instances, separate named volumes, separately generated clone-only DB credentials and a completely private site config with restored encryption key from approved archive but scheduler/worker/queue/email/integrations disabled and maintenance on until controlled tests. Keep the pinned images `ccpcerp:v16.50.0` (ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`), MariaDB 11.8 (`sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4`), Redis 8.6-alpine (`sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763`). No pulls, rebuilds or migrations without a separate compatibility check. No public ports, reverse proxy, PROD hostname/DNS, external network, schedulers/workers, outbound mail or webhooks; if UI is later needed, use an expressly approved secured local-only interface/tunnel with tight origin and credentials controls. Do not run stock Frappe `configurator` or `create-site` blindly because Compose defaults can mutate site config, force restarts or create a new site. Do not treat this as production cutover. Recovery: preserve originals, verify independent clone backup and app/data after each meaningful write, fail closed on partial creation with inventory; no force cleanup or auto-retry.

**Immediate single safe Stage17V-A operator step:** NEW-only read-only Docker/host/storage/archive capacity inventory: exact host/operator/local Docker context, three baseline pinned running services, four baseline volumes, internal bridge, existing app/support images, no clone-name collisions, original four protected Nov5 archives present with expected owner/mode, current disk free bytes vs source volume and archive sizes. Emit **only** sanitized counts/capacity booleans and phase markers (no secret paths, raw site settings, business data, IP inventories). No new Docker resources, no backup copy, no DB transactions/services or filesystem writes. Archive content/hashes were already verified in Stage5; do not burn time repeating whole-archive checksum unless a source change is suspected. If insufficient space, STOP and review; do not prune or delete automatically. Following passing feasibility, prepare and execute *independent clone creation* under owner's Stage17V NEW-only approval one verified step at a time, with fresh strict plan and rollback checks.

**Current delivery status:** Stage17U Company ORM pass; Stage17V independent full-site clone and operational HTTP/Redis/custom workflow acceptance remain **pending**; current/live source-consistent final backup, production release plan, independent rollback and explicit go-live approval remain later gates. Current OLD PROD was checked at Stage17R (4 companies, no GL/SLE/7 standard document rows), but that limited parity is not proof every table or subsequent write is unchanged.

## NEW REHEARSAL STAGE 17U ADAPTED RESTORED-SITE CONFIG + FRAPPE COMPANY ORM PASS — 2026-11-07

**PASS — owner-run NEW-only isolated one-off app-level read from restored Nov5 rehearsal database; exact sanitized markers:**

```text
STAGE17U_PRECHECK_VERIFIED
STAGE17U_POSTCHECK_VERIFIED
STAGE17U_ADAPTED_SITE_INIT_OK
STAGE17U_COMPANY_SQL_READ_OK
STAGE17U_COMPANY_DOCTYPE_META_OK
STAGE17U_COMPANY_ORM_READ_OK
STAGE17U_ADAPTED_SITE_SELECT_ONLY_SUCCESS
STAGE17U_RESULT=ADAPTED_SITE_ORM_PASS
STAGE17U_ONE_USE_TEST_COMPLETE
```

**Evidence:** Guarded NEW `ccpcadmin@ccpcerp-prod` preflight asserted pinned `ccpcerp:v16.50.0` immutable app ID, exact 3 DB/Redis running pinned service containers, four named rehearsal volumes, isolated non-attachable internal bridge `ccpc_restore_rehearsal_20261107_default` and available helper IP `172.18.0.250`. Host inspected only the **real restored site config** SHA256/fingerprint and safe scheduler/mail/maintenance flags and ensured the protected `DB_READONLY_*` diagnostic identity matched the restored schema; the actual old full-write site DB password and `encryption_key` were **not sent to the networked container**. One disposable nonroot, no-capabilities, no-new-privileges, read-only-rootfs `docker run --rm --pull never` helper joined only the internal bridge at source IP `172.18.0.250`, with no published port, site/DB/log volume mounts, web/worker/scheduler/email/integration startup or Bench migration. It wrote a synthetic throwaway site config on tmpfs preserving only real site's allowlisted safety flags and **substituting SELECT-only DB credentials**, and disabled remote Redis use by loopback. Frappe `init`, the Company `SELECT COUNT(*)` (four companies), Company `frappe.get_meta('Company',cached=False)` and a `frappe.get_all('Company', fields=['name'])` ORM read all passed. Child suppressed raw records/logs; only sanitized markers printed. Postcheck verified the original three persistent services/network/four volumes and the three real site config/app-file fingerprints unchanged. **One-use Stage17U test complete**; do not rerun as routine.

**Limitations:** This is a substantial **real application/DocType/ORM compatibility milestone** against an adapted site configuration and historical schema, **not an initialization of the original restored site with its full runtime config**. Does not verify actual web access/login, installed application custom DocType behavior and intercompany, emails, workers, Redis integration, file/attachment retrieval, financial/inventory posting, business authorization, schema migrations, fresh production dataset or a cutover. The Stage17S `--network none` original-site init STOP has not been explicitly diagnosed, though successful `init` with DB connectivity supports networking as the cause rather than file permission. Avoid enabling real site full-write credentials in an unconstrained app process.

**Next most productive work:** Stop repeated environment/network/DB account smoke checks. Review authoritative `ccpcerp` application review branch and current deployment acceptance/release docs to choose a narrow set of representative **custom CCPC ERPNext workflow** read-only integration checks, and design one **isolated, reversible, production-like full-site app rehearsal** using safe restored source/side-effect fences (scheduler/worker/mail/queue/external integrations OFF, no public service ports, staged credentials, careful rollback). Compare against currently live OLD source and plan a fresh consistent backup before final cutover. Original PRODUCTION must not be modified or automatically switched without separate concrete plan and approval.

## NEW REHEARSAL STAGE 17T REAL SITE UID1000 FILE ACCESS PASS — 2026-11-07

**PASS — owner-run NEW-only read-only host/dedicated-volume permission diagnostic reported:**

```text
STAGE17T_NEW_HOST_VERIFIED
SITE_ROOT_UID1000_ACCESSIBLE=True
SITE_DIRECTORY_UID1000_ACCESSIBLE=True
SITE_CONFIG_UID1000_ACCESSIBLE=True
COMMON_CONFIG_UID1000_ACCESSIBLE=True
APPS_FILE_UID1000_ACCESSIBLE=True
STAGE17T_SITE_FILE_PERMISSIONS_PASS
STAGE17T_READ_ONLY_DIAGNOSTIC_COMPLETE
```

The diagnostic was run on NEW `ccpcadmin@ccpcerp-prod`, checked the local default Docker socket and expected isolated 3-container network, obtained the exact named `sites` volume location under the verified Docker data root and inspected the mode/user/group bits on each **real** restored file/parent. Frappe UID1000's read/search access was found for all five paths; no file contents, secrets, business rows or permission changes were output. This narrows the previous Stage17S `frappe.init` STOP: simple UNIX owner/group/mode access to these paths is **not** the likely explanation. However it is a static permission check; cannot confirm actual container mount propagation, SELinux/AppArmor issues or the exact suppressed exception.

**Stage17S root cause remains unresolved, likely network-mode incompatibility:** Upstream Frappe v16 `frappe.init(is_request=True)` can resolve installed apps via a database connection and/or Redis; Stage17S was `--network none` and used original site's existing full-write credentials. Do not rerun that command with network attached and original credentials. Separate Stage17P already confirmed Frappe `init` and SELECT-only DB connect with a synthetic config over the isolated bridge.

**Next efficient, bounded Stage17U on NEW ONLY (routine safe non-destructive pre-production test under owner's standing delegation):** A single ephemeral pinned app-image `docker run --rm --pull never` on the **existing internal** rehearsal network at unused `172.18.0.250`. Strict host/user/default Docker context and exact 3 pinned DB/Redis services + 4 rehearsal volumes pre/post; UID1000, read-only rootfs, cap-drop, no ports, no mounts/no original restored site secret inside container. Host read only the real site configuration (verify off switches and required encryption-key presence, never output secrets), derive a *whitelisted subset* of site flags and `db_name`, replace `db_user` and `db_password` exclusively with protected SELECT-only `DB_READONLY_*` values, suppress Redis (point to unreachable loopback), serialize child scratch config **via stdin only**, keep scratch inside tmpfs, and run `frappe.init` / `frappe.connect(set_admin_as_user=False)`, one simple `frappe.db.sql` SELECT, then optionally a targeted read-only `frappe.get_meta("Company",cached=False)` + sanitized Company row count if cache does not force network. Suppress stdout/stderr, print only pass/stop phase markers, no raw Company names/rows/credentials/DB strings. Use SELECT-only account, no full-write original site password inside helper, no scheduler/mail/workers/bench migrate, no production change. Observe that the **real site itself still has not been initialized with its own site config**, so this establishes adapted real-site metadata compatibility only. Existing full-write real site configuration and Nov5 DB remain untouched, separate final cutover gate persists.

## NEW REHEARSAL STAGE 17S REAL RESTORED SITE OFFLINE INIT STOP — 2026-11-07

**STOP, not a PASS — owner-run bounded offline NEW `ccpcadmin@ccpcerp-prod` app-image diagnostic reported:**

```text
STAGE17S_NEW_REHEARSAL_PRECHECK_VERIFIED
STAGE17S_POSTCHECK_VERIFIED
STAGE17S_RUNTIME_STOP_INIT
STAGE17S_RESULT=STOP_NO_AUTOMATIC_RETRY
```

Stage17S used the pinned `ccpcerp:v16.50.0` image, `--network none`, root filesystem read-only, `sites` volume mounted **readonly** at its real bench path, nonroot/capability-dropped, with stream logging and bounded lifetime. The operator pre/post verified three persistent DB/Redis rehearsal service containers, four volumes, isolated network and SHA256 of real site's `site_config.json`, common config and `apps.txt` unchanged; no persistent services/migrations/DB activity intentionally triggered. The child reported a caught error at `frappe.init(site="ccpcerp.local", sites_path=..., is_request=True)`; exception type and call site were **suppressed**, so this result cannot establish corruption, credential failure, permission problem or application incompatibility. No stage17S rerun should occur unchanged.

**Source-level hypothesis (not proven image-trace):** Inspection of upstream Frappe `version-16` `frappe/__init__.py` shows that `init` calls `setup_module_map(include_all_apps=False)` for `is_request=True`; `setup_module_map` can call `get_installed_apps(_ensure_on_bench=True)`, and `get_installed_apps` calls `connect()` if no db connection is present. It also may access Redis cache. With `--network none`, this is a plausible normal STOP on internal DB/Redis access even when site files are valid. However the actual immutable custom image implementation/its exact exception has **not** been independently traced. Do not enable network while loading original site config/full-write DB password for diagnosis, and do not create privileged write access.

**NEXT efficient, safe targeted diagnostic:** Either (1) NEW-only no-container, read-only site-directory UID1000 access/permission and `apps.txt`/config consistency assessment plus an independent **static source audit of the pinned image** for `setup_module_map` and installed-app DB connection paths; or (2) a separately scoped **instrumented, networkless, read-only** helper that prints only exception class/module and a whitelist of Frappe init phase tags, suppressing raw exception messages/tracebacks because they may contain site path/business/secret information. This is a **new root-cause diagnostic**, not a blind retry of Stage17S. With evidence in hand, plan **SELECT-only scratch site config** from protected credentials with retained non-secret restored flags and optionally restored encryption key, on the existing isolated NEW bridge with no original `sites` volume mounted; test actual Frappe DocType/Company metadata in a single transaction after controlling side effects and rollback. Preserve all original site files/DB and OLD PROD/DEV; no production changes/cutover.

## OLD LIVE PROD STAGE 17R READ-ONLY AGGREGATE COMPARISON MATCHES NEW NOV5 REHEARSAL — 2026-11-07

**PASS — owner-run OLD `gani@ccpcerpserver` read-only summary, no PROD changes reported:**

```text
STAGE17R_OLD_PROD_SCOPE_VERIFIED
SOURCE_COMPANIES=4
SOURCE_GL_ENTRIES=0
SOURCE_STOCK_LEDGER_ENTRIES=0
SOURCE_STANDARD_DOCUMENT_TOTAL=0
SOURCE_READONLY_COUNTS_COMPLETE
STAGE17R_LIVE_SOURCE_READONLY_CHECK_COMPLETE
```

**Interpretation against Stage17Q (NEW):** Four Companies in both OLD live PRODUCTION and restored November 5 snapshot; both report **0 GL entries**, **0 Stock Ledger entries**, and **0 total rows in the same seven standard transaction document tables**. The OLD-only preflight verified OLD host/operator/local Docker context, exact pinned `frappe_docker-backend-1` and `frappe_docker-db-1` project/service/image/running identity. One `docker exec -i` in the *already-running* OLD backend read only the live site's current DB connection config, opened a MariaDB `REPEATABLE READ` `START TRANSACTION READ ONLY` using existing full-write app account, queried only aggregate counts with per-query time limit and then rolled back. No site/data mutation, restart, migration, new container, application runtime startup, DEV or cutover was part of that command. **This confirms the empty transaction tables are presently common to OLD and NEW**, not necessarily an omitted Nov5 backup of those categories. It does **not** establish all other source tables, app settings, attachments or Company details are identical; nor prove future live transactions won't occur before cutover. The GL balanced flag from 17Q is vacuous (0=0), so financial transaction integrity cannot yet be tested on real GL/SLE rows.

**Owner standing delegation remains**: continue safe, nondestructive NEW-only rehearsal tests without repetitive individual approvals; still require explicit operator authorization for live deployment/traffic switch, destructive cleanup, DB migrations, live-data writes/restarts, changes on OLD PROD or changes that may impact shared infrastructure.

**Next fastest meaningful NEW-only action:** Prepare *real restored-site* application acceptance without using the full-write historical DB credentials: check site artifacts from the already restored `sites` volume with sanitized static metadata and verify a safe scratch overlay that preserves the original encryption key and app identities but substitutes the IP-limited SELECT-only DB identity. Avoid restarting/launching services, modifying original site volumes or running migration. Subsequent limited app-level actual DocType/Company read can then be tested with the pinned legacy image under no-web/no-jobs/no-mail/no-integrations controls; reporting only booleans/counts and respecting that a write attempt under SELECT-only must fail. Actual full HTTP/user login/stock/GL tests, current source backup+reconciliation, production rollback readiness and final separate cutover authorization remain future gates. Stop endless network/client-only preflight loops.

## NEW REHEARSAL STAGE 17Q SELECT-ONLY BUSINESS AGGREGATES COMPLETE; TRANSACTION SET EMPTY — 2026-11-07

**PASS for execution/scope, transaction integrity **NOT TESTED** because applicable ledger/document sets are empty.** Owner reported the following exact sanitized output from the single NEW-only authorized check:

```text
STAGE17Q_PRECHECK_VERIFIED
STAGE17Q_POSTCHECK_VERIFIED
STAGE17Q_SCHEMA_ALLOWLIST_VERIFIED
STAGE17Q_COMPANY_COUNT=4
STAGE17Q_GL_ENTRY_COUNT=0
STAGE17Q_STOCK_LEDGER_ENTRY_COUNT=0
STAGE17Q_STANDARD_DOCUMENT_TOTAL=0
STAGE17Q_INVALID_COMPANY_LINKS=0
STAGE17Q_GL_STANDARD_VOUCHER_MISSING=0
STAGE17Q_SLE_STANDARD_VOUCHER_MISSING=0
STAGE17Q_GL_DEBIT_CREDIT_BALANCED_WITHIN_001=True
STAGE17Q_READONLY_AGGREGATES_COMPLETE
STAGE17Q_DATA_CHECK=PASS_LIMITED_SCOPE
STAGE17Q_RESULT=SELECT_ONLY_AGGREGATE_DIAGNOSTIC_COMPLETE
STAGE17Q_ONE_USE_APPROVAL_CONSUMED
```

**Interpretation:** Strict NEW rehearsal pre/post scope verified three persistent DB/Redis services, four volumes, internal bridge, fixed helper IP availability and immutability; the one-shot restricted app-image Python client authenticated using the existing SELECT-only schema account and ran allowlisted aggregate reads only, no business rows/amounts shown. Exactly **four Companies** exist in the 2026-11-05 historical rehearsal snapshot, but **zero** `tabGL Entry`, **zero** `tabStock Ledger Entry`, and **zero** rows aggregated across seven standard Sales/Purchase Invoice, Payment Entry, Journal Entry, Stock Entry, Delivery Note, Purchase Receipt tables. The zero invalid Company/voucher links are **vacuous** with no transactions. GL debit/credit `True` is **0 equals 0**, not evidence of meaningful accounting/stock integrity. `PASS_LIMITED_SCOPE` only means the selected checks found no inconsistencies in those empty sets; do not label the financial/inventory business data validated, and do not assume a current live PROD copy also has zero transactions. SQL metadata and application DB connectivity have passed separate previous milestones.

**Owner's next-stage delegation:** Following this result owner explicitly said, `You can approved it yourself up to production run to speed up our progress`. Interpret as standing approval to **continue routine safe, nondestructive, isolated NEW rehearsal planning/inspections and bounded tests without repetitive yes/no gates**, with GitHub checkpoints and one safe host operator step at a time. This does not give ChatGPT physical server access or waive the requirement to review significant changes; no autonomous background changes. **PRODUCTION deployment, write-bearing live migration/restoration, service traffic cutover, destructive cleanup, DATABASE migrations/restarts on live services, old PROD modifications, or shared-infrastructure-impacting operations require distinct explicit plan/scope and owner approval.** Do not self-approve the final go-live or move untested DEV code into PROD.

**Fastest next steps:** Determine whether zero GL/SLE/standard transactions is expected by comparing **sanitized counts** to the current OLD live PROD database using guarded **read-only** access, or clearly confirm setup-only status if the old host cannot be safely queried. Do not leak host DB secrets or raw business data; avoid production schema writes, Docker exec app startup, or invasive backup operations. Then progress to a reversible isolated full restored-site Frappe operational smoke, with preserved rehearsal snapshot and disabled scheduler/jobs/email/integrations, no outside access and no live traffic. Before actual cutover, capture and reconcile a new **current consistent** production backup, validate restore and rollback, and obtain explicit owner approval.

## NEW REHEARSAL STAGE 17Q BUSINESS-DATA AGGREGATE DIAGNOSTIC APPROVED — EXECUTION PENDING (2026-11-07)

**Explicit owner authorization:** After successful Stage17P-2 one-use Frappe initialization and SELECT-only metadata query, owner replied **`Approved`** for **one** bounded, NEW-only historical rehearsal business-data diagnostic. **Not executed yet.** Scope: use existing pinned `ccpcerp:v16.50.0` image (`sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`) to run **one ephemeral** no-mount/nonroot/no-port/read-only-rootfs/no-capabilities container on existing internal rehearsal bridge at unused `172.18.0.250`, with only protected `DB_READONLY_HOST`, `DB_READONLY_PASSWORD`, `DB_READONLY_SCHEMA`, `DB_READONLY_USER` owner-file values passed via stdin into an in-container Python/PyMySQL client (not Docker args/env). No Frappe web/process/worker/scheduler, Redis/cache use, ERPNext hooks, email/integrations or actual site config mount. SQL is restricted to server-reported identity, information_schema table/column metadata, and fixed aggregation-only `SELECT` from Company, General Ledger, Stock Ledger and common invoice/payment/journal/stock voucher tables in the restored November 5 rehearsal DB, using transaction READ ONLY; no row-level data, names, amounts, business records or secrets emitted. Report sanitized counts/boolean linkage checks and whether GL total debits equal credits within a clearly stated rounding tolerance, without interpreting nonzero counts as proof of corruption. Validate pre/post exact three persistent DB/Redis containers/network/four volumes/immutable image and protected diagnostic credential owner/mode. One authorized execution, bounded timeout, no auto-retry on partial failure.

**Evidence limits:** This is **internal consistency of a historical rehearsal snapshot**, not exact hash verification of each business row, inventory balance proof, permissions audit, reconciliation with OLD live PRODUCTION, or final production readiness. GL/SLE voucher-link joins cover only an explicitly named list of standard document types; custom voucher types remain untested. All system access must be restricted to NEW `ccpcadmin@ccpcerp-prod` local Docker daemon. The preceding Stage17P approval is consumed; owner approved this **separate** diagnostic, not production deployments, database writes, migrations, full-write account, restore, network changes, OLD PROD/DEV activity or cutover.

**Next:** Give owner the one-use Stage17Q command; wait for actual sanitized output before calling the operation complete.

## NEW REHEARSAL STAGE 17P-2 SELECT-ONLY FRAPPE/MARIADB DIAGNOSTIC SUCCESS — 2026-11-07

**PASS — single authorized operator-run diagnostic on NEW `ccpcadmin@ccpcerp-prod`.** Exact sanitized result:

```text
STAGE17P_PRECHECK_VERIFIED
STAGE17P_POSTCHECK_VERIFIED
STAGE17P_FRAPPE_INIT_OK
STAGE17P_FRAPPE_READONLY_CONNECT_OK
STAGE17P_FRAPPE_DB_METADATA_SELECT_OK
STAGE17P_ONE_SHOT_READONLY_SUCCESS
STAGE17P_RESULT=SELECT_ONLY_SITE_CONNECTION_VERIFIED
STAGE17P_SINGLE_USE_APPROVAL_CONSUMED
```

**Scope/evidence:** The exact legacy PRODUCTION application image `ccpcerp:v16.50.0` at immutable ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8` ran as **one ephemeral, nonprivileged, read-only-rootfs, no-capabilities/no-new-privileges container** with only the NEW rehearsal internal bridge (`ccpc_restore_rehearsal_20261107_default`) and fixed source IP `172.18.0.250`; no host/site/db/log volumes, no published ports or production service containers were started by this probe. Guarded preflight verified three existing pinned MariaDB/Redis service containers, named volumes and scope; postcheck passed. The diagnostic received `DB_READONLY_*` secret values via stdin from the restricted protected file, built a disposable **synthetic** site config on tmpfs with scheduler/maintenance/email off, and did **not** mount or read the real restored site config or full-write app credentials. Frappe `init`, `connect`, and two database `SELECT` metadata checks completed. The database connection identified the exact schema-restricted `ccpc_ro_probe_20261107@172.18.0.250` account, and information_schema returned **741 BASE TABLE + six SEQUENCE** as expected for the separately restored Nov 5 historical SQL. Stream output/traces were suppressed by the probe; user reported only approved success markers.

**What PASSED:** Functional Python/Frappe initialization and real MariaDB authentication/query against the isolated restored data layer with an IP-limited SELECT-only account. Importantly this is *beyond* offline app imports (Stage16) and DB-only client login (Stage17F). **One-run authorization consumed: do not rerun it or escalate DB credentials.**

**What did NOT pass / was not attempted:** Frappe initialization using the actual restored `ccpcerp.local` site configuration, full app workflows/HTTP, Stock Ledger/GL and Company reconciliation, permissions, Redis/cache end-to-end behavior, integrations, attached-file resolution, background jobs, migrations, actual accounting data row checks, persistent PRODUCTION startup, new-host production DNS/cutover, rollback or current as-of-cutover source consistency. Using historical Nov 5 snapshot cannot establish preservation of later live transactions; the OLD live PRODUCTION remains authoritative. Pre/post checks confirmed container/network/volume scope, not byte-for-byte proof of DB contents or all file data; no changes were intended or reported.

**Next fastest safe step / separate authorization boundary:** Stop repeating network/firewall/client-credential probes. Prepare **one deliberately bounded NEW-only rehearsal business-data acceptance** using existing SELECT-only DB credential and image to read **sanitized aggregates** (e.g. schema/Company/Stock Ledger/GL/document counts and references), with a strict query allowlist, zero user/business rows in output, no Frappe services/migrations/workers, no integrations/emails, pre/post scope validation, and a safe historical baseline for comparison. That test would be a NEW database-connected operation requiring explicit new authorization because Stage17P approval is consumed. Then address full restored-site behavior under isolated safeguards and separately review an approved **current consistent** OLD production cutover backup, protected actual data reconciliation, rollback and final authorization; do not promote Nov 5 rehearsal data as current live production. No OLD PRODUCTION/DEV host action is authorized by this milestone.

## NEW REHEARSAL STAGE 17P-1 GUARDED SECRET/SITE/IMAGE PREFLIGHT PASS — 2026-11-07

**Owner-run NEW-only read-only preflight markers:**

```text
STAGE17P_NEW_REHEARSAL_SCOPE_VERIFIED
STAGE17P_APP_IMAGE_PIN_VERIFIED
STAGE17P_FIXED_DIAGNOSTIC_IP_AVAILABLE
STAGE17P_PROTECTED_SECRET_FILE_VERIFIED
STAGE17P_SECRET_FIELD_NAMES=DB_READONLY_HOST,DB_READONLY_PASSWORD,DB_READONLY_SCHEMA,DB_READONLY_USER
STAGE17P_RESTORED_SITE_CONFIG_VERIFIED
STAGE17P_SCHEDULER_EMAIL_MAINTENANCE_FLAGS_VERIFIED
STAGE17P_APP_NAMES_VERIFIED
STAGE17P_PREFLIGHT_COMPLETE_NO_FRAPPE_STARTED
```

**Meaning:** Existing NEW isolated rehearsal network with 3 pinned DB/Redis containers and 4 volume names, exact PRODUCTION app image ID, available fixed source IP `172.18.0.250`, protected diagnostic secret owner/mode and four **field names only**, restored site's DB host/type, maintenance/scheduler/email safety flags and apps.txt `frappe`, `erpnext`, `ccpcerp` passed. **No credential values, business records, SQL, app process or persistent service were output/executed.**

**Implementation design checked against Frappe v16 source (not a guarantee of exact immutable image fork):** Frappe v16's `frappe.init(site, sites_path=..., is_request=True)` reads site configuration; `frappe.connect(set_admin_as_user=False)` uses `db_name`, `db_user`, `db_password` from that config; module/cache initialization may occur before SQL. To prevent full-write site credentials being loaded, never mount the restored sites volume in the probe. Instead, the one-shot **preapproved** app-image helper receives `DB_READONLY_*` secret values via **stdin only** from the protected NEW host file and creates a synthetic site configuration + apps.txt entirely on container tmpfs. Use nonroot 1000:1000, `--read-only`, no mounts, `--cap-drop ALL`, no new privileges, single existing internal Docker network/fixed IP, no published ports, `--pull never` immutable image, no web/worker/queue/scheduler/email/Bench commands. Configure Redis to loopback unused port to prevent contacting the existing queue/cache, and permit a single Frappe init/DB SELECT metadata query (current user + database identity and schema object counts) with automatic stdout/stderr suppression and sanitized phase/status markers; avoid printing source names/secrets. The exact SELECT-only account cannot mutate restored financial tables; Frappe may still try an unsupported write during initialization and must then fail without privilege escalation. One execution only, pre/post scope checks; no reruns without a new decision. No OLD PROD/DEV, migrations, restore or cutover.

**Current status:** Stage 17P-1 completed; one-off `docker run` Stage 17P-2 **not yet reported executed**.

## NEW REHEARSAL STAGE 17P ONE-OFF READ-ONLY FRAPPE DB DIAGNOSTIC OWNER-APPROVED — EXECUTION PENDING (2026-11-07)

**Owner explicit authorization:** After Stage 17O read-only host listener/UFW classification passed, the owner replied `aPPROVED` to preparing and executing **one** bounded Frappe site/database diagnostic on the **NEW** `ccpcadmin@ccpcerp-prod` rehearsal only. The earlier Stage17M authorization has been consumed. This is **not proof of execution** nor permission for live app deployment, ERPNext service startup, any OLD PROD/DEV change, database writes/migrations, privileged full app credentials, network/firewall edits, backup/restore, or final cutover.

**Confirmed prerequisites:** Local immutable image `ccpcerp:v16.50.0` ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`; NEW-only internal non-attachable IPv4 Docker bridge `ccpc_restore_rehearsal_20261107_default`, only 3 persistent pinned MariaDB/Redis DB/cache/queue containers and 4 named volumes; completed Nov5 database/schema and site/attachment restoration; existing exact host-IP-restricted SELECT-only MariaDB identity `ccpc_ro_probe_20261107@172.18.0.250`; protected `readonly-db-probe.env`; all offline Frappe/ERPNext/CCPC imports passed Stage16. Stage17L static isolation rules passed, Stage17M test found no default route and rejected nonlocal egress, Stage17O showed only SSH-port wildcard host listeners with active UFW default deny and one LAN SSH allowance; host-gateway access is not independently disproved.

**Next single action is a NEW-only READ-ONLY preflight (within approved Stage17P):** Verify actual secret file **key names and permissions only**, actual image Entrypoint/User/WorkDir metadata, existing rehearsal site config file/mode and isolation off switches **without printing values**, pinned exact container/network/volume identities and available fixed source IP. This avoids fabricating env variable names or inadvertently running Frappe against the full-write app credentials. Only after a clean preflight should ONE `docker run --rm --pull never` restricted non-web/no-worker/no-scheduler Frappe diagnostic be constructed and executed, with stdin-only credential handoff (not Docker env or argv), ephemeral synthetic/scratch site config, root filesystem read-only, no site/DB/logs volume writes, exact source IP, no network attachments beyond isolated bridge, no publish, no privileges/caps, bounded timeout, sanitized output, before/after invariants and no automatic retry. If Frappe tries prohibited writes, preserve that error classification without exposing business records, and STOP. The SELECT-only account prevents data mutation but does not guarantee init succeeds without write attempts. No app service or production change authorized.

## NEW REHEARSAL STAGE 17O HOST LISTENER + UFW CLASSIFICATION PASS — 2026-11-07

**Owner-run read-only NEW `ccpcadmin@ccpcerp-prod` output:**

```text
STAGE17O_NEW_HOST_VERIFIED
HOST_LISTENERS_IPV4_SSH_PORT=1
HOST_LISTENERS_IPV6_SSH_PORT=1
HOST_LISTENERS_IPV4_OTHER_PORT=0
HOST_LISTENERS_IPV6_OTHER_PORT=0
HOST_LISTENERS_UNKNOWN_WILDCARD=0
UFW_ACTIVE=True
UFW_DEFAULT_INCOMING_DENY=True
UFW_LAN_RESTRICTED_SSH_RULES=1
UFW_OTHER_INBOUND_ALLOW_RULES=0
STAGE17O_READ_ONLY_CLASSIFICATION_COMPLETE
HOST_GATEWAY_REACHABILITY_NOT_DIRECTLY_TESTED
```

**Verified interpretation:** The bounded diagnostic reports one TCP/22 wildcard listener for each IPv4/IPv6 family, zero wildcard listeners on other ports, UFW active with default incoming DENY, and a sole displayed SSH allow from the dedicated LAN `192.168.50.0/24`; no other shown inbound allow rule. This is an *SSH-port* classification, not an independent process identity proof, and does not verify every possible nft/iptables INPUT bypass or actual bridge-to-host gateway reachability. Prior 17N had zero listeners specifically bound to the rehearsal bridge. The earlier Stage 17M one-use UDP test showed no default route and rejected socket toward nonlocal `192.0.2.1:9`; it did not test host gateway access. On the evidence seen, no unexpected host listening service or UFW rule warrants expanding static network inventory. The owner did not report any writes or changes to NEW host, OLD PRODUCTION or DEVELOPMENT.

**Engineering continuation — separate authorization required:** Prefer a **single bounded, no-web/no-worker/no-scheduler, one-shot Frappe site/DB initialization diagnostic** on NEW rehearsal only, using pinned live legacy app image `ccpcerp:v16.50.0` (immutable image ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`), restored Nov 5 isolated rehearsal DB, existing exact-source-IP-restricted SELECT-only `ccpc_ro_probe_20261107` diagnostic identity, and controlled scratch site config. Before execution review image's actual entrypoint/permissions, synthetic scratch wiring, source-IP reservation, app initialization's possible DB/cache/file side effects, secure credential injection with no stdout/log exposure, client-image mounts, and pre/post unchanged DB/site/service checks. Use one bounded `docker run --rm --pull never`, read-only filesystem, tmpfs only where necessary, no privileged/capabilities, no published ports, disabled Frappe jobs, scheduler, web, mail, integration and external egress; fail closed on any mismatch and no automatic reruns. **SELECT-only DB privilege blocks writes but cannot guarantee that Frappe's code never attempts them**; distinguish an expected readonly failure from schema/auth incompatibility. No user/Company/GL data displayed, no full business queries; no app service startup or migrations. Owner approval for 17M does **not** authorize this 17P app-connected attempt. The next decision is a **single explicit authorization** for that narrow guarded diagnostic, not another general host-firewall inspection.

## NEW REHEARSAL STAGE 17N READ-ONLY HOST LISTENER INVENTORY PASS — 2026-11-07

**Owner-run NEW-only read-only scope/listener check reported:**

```text
STAGE17N_NEW_REHEARSAL_SCOPE_VERIFIED
HOST_LISTENERS_IPV4_WILDCARD=1
HOST_LISTENERS_BRIDGE_ADDRESS=0
HOST_LISTENERS_IPV6_WILDCARD=1
STAGE17N_READ_ONLY_INVENTORY_COMPLETE
HOST_GATEWAY_REACHABILITY_NOT_YET_PROVEN
```

**Interpretation:** Fresh verification of exact NEW local Docker context, internal IPv4 rehearsal bridge with correct project, three persistent pinned DB/Redis containers, and four named rehearsal volumes passed. Host socket inventory found **one IPv4 wildcard socket**, **one IPv6 wildcard socket**, and **zero sockets bound specifically to the rehearsal bridge's gateway address**. The wildcard listener counts may represent the same dual-stack service or distinct services; no ports/process identities were printed. Importantly, a wildcard listener can accept traffic via the bridge as well as other interfaces if firewall INPUT rules allow, so zero bridge-specific binds **does not prove host gateway inaccessibility**. The IPv6 wildcard is on the HOST and does not negate earlier `EnableIPv6=False` for the rehearsal bridge. No host-gateway connection or Frappe runtime test occurred. Do not claim host gateway blocked, or re-run the consumed Stage 17M authorization.

**Next efficient safe step:** One bounded **read-only** identification of whether wildcard host listener(s) are only restricted management SSH or other services, together with UFW IPv4/IPv6 incoming policy and presence of any Docker-bridge input allow. Emit only sanitized category/count/status; never dump live interface names, host addresses, raw firewall rules or process command lines. If only existing SSH is listening and host firewall applies LAN-only ingress, proceed to risk review and request explicitly scoped bounded non-web/non-worker Frappe diagnostic rather than repeating general network inventory. No new container/probe or host/service/Docker/DB changes authorized by this step.

## NEW REHEARSAL STAGE 17M SINGLE NEGATIVE-EGRESS PROBE COMPLETED — 2026-11-07

**PASS for the one authorized test only — owner-run NEW `ccpcadmin@ccpcerp-prod` with exact restricted rehearsal guards:**

```text
STAGE17M_PRECHECK_VERIFIED
STAGE17M_POSTCHECK_VERIFIED
PROBE_DEFAULT_ROUTE=ABSENT
PROBE_SOCKET=REJECTED
OUTBOUND_DROP_COUNTER_INCREASED=False
STAGE17M_RESULT=NO_DEFAULT_ROUTE_TO_TEST_TARGET
STAGE17M_SINGLE_PROBE_COMPLETE
HOST_GATEWAY_AND_APP_EGRESS_STILL_REQUIRE_SEPARATE_REVIEW
```

One `docker run --rm --pull never` from pinned `mariadb:11.8` image, using a nonprivileged read-only no-capability no-new-privilege no-mount/no-secret client on existing NEW-only internal Docker rehearsal network, attempted a single UDP send of a nonsecret marker to documentation-only `192.0.2.1:9` (numeric; no DNS). The temporary client reported **no default IPv4 route** and **socket send rejected**. No increment in the network's outbound DROP counter is **expected/compatible** when the kernel rejects a send before it traverses FORWARD. The script reported passing precheck and postcheck: exact original three pinned DB/Redis service containers and endpoints, four named volumes, unchanged network ID and firewall policy checks. No app/DB/legacy-production or DEVELOPMENT writes were part of the command. This test does **not** prove a packet was dropped by firewall because the socket was rejected locally. The one-run approval is now consumed; **do not repeat** without new scope/authorization.

**Interpretation:** Concrete one-destination negative test supports that ordinary new routed IPv4 egress toward a nonlocal address from the isolated rehearsal client was unavailable. Prior 17L static `DOCKER-INTERNAL` negated-subnet DROP rules add a separate safety layer. Neither shows comprehensive host-gateway isolation, non-routed host access, IPv6 in other namespaces, nft hook scope, or actual application side effects. No DB-connected Frappe startup, scheduler, worker, web, email, migrations, live cutover or production operation was authorized or executed.

**Next fastest safe continuation:** A brief **read-only, no-new-container** inventory of NEW isolated network gateway and host-local listening/socket/INPUT rules *using sanitized metadata*, to assess host-gateway and Docker host services. Then design the **single bounded read-only-Frappe diagnostic** using existing SELECT-only account and isolated scratch/config with no workers/web/scheduler/jobs/emails, no external access and protected data; obtain **separate explicit approval** before starting a Frappe-capable process. No additional external probes or firewall edits to make this test pass. Retain existing rehearsal resources and OLD PROD/DEV unchanged.

## NEW REHEARSAL STAGE 17M ONE-OFF NEGATIVE-EGRESS PROBE APPROVED — EXECUTION NOT YET REPORTED (2026-11-07)

**Approval only, not an executed test:** Following Stage 17L static guard success, owner explicitly replied **`aPPROVED`** to the proposed one-time **NEW `ccpcadmin@ccpcerp-prod` isolated-rehearsal negative-egress probe**. Scope is **one** temporary, unprivileged `docker run --rm` client-only container on existing `ccpc_restore_rehearsal_20261107_default`, *no business-data or credential mounts*, no published ports, no DB or Frappe/Bench use, and one outbound IPv4 UDP send attempt carrying a fixed nonsecret marker to IANA RFC5737 documentation-only TEST-NET-1 address `192.0.2.1` port 9 (no DNS and no real service expected). Use the already verified MariaDB image by immutable ID with entrypoint replaced by Bash, capability drop, read-only rootfs, no new privileges, fixed unused rehearsal bridge client IP, tight resource limits, and `--pull never`. No other destinations, retries or services permitted. Auto-remove and post-check original three services/network/four persistent volumes; on partial failure STOP, inspect, do not silently rerun or aggressively clean existing containers.

**Required before execution:** Fresh host/user/local Docker endpoint, exact 3 pinned existing DB/Redis rehearsal containers, 4 volumes, internal IPv4-only bridge, unused probe IP, immutable image and `DOCKER-INTERNAL` negated-subnet DROP structure/conntrack state. Capture pre/post outbound DROP packet counters without printing raw firewall details. Probe itself reads `/proc/net/route` for default-route presence, makes exactly one numeric-IP UDP socket write attempt, and prints only `ACCEPTED`/`REJECTED` markers. If missing default route + socket rejected, evidence supports blocked routing to tested destination. If a matching DROP counter increases, that is consistent with filtering, but a counter may also include concurrent traffic. A socket write succeeding does NOT establish delivery; absence of reply/timeout alone is not proof. Mark ambiguous outcomes INCONCLUSIVE.

**Hard boundaries:** Approval does NOT cover Frappe/Bench runtime, worker/scheduler/web/email/integration startup, new site restore, Docker firewall/routing edits, exposure of host or business data, OLD live PRODUCTION/DEVELOPMENT changes, production cutover or any repeated/expanded probe. Docker internal isolation allows possible host-gateway traffic, so even a passing test is not blanket proof of application-level network isolation. Operator execution/output pending.

## NEW REHEARSAL STAGE 17L SUBNET-NEGATION AND CONNTRACK CHECK PASS — 2026-11-07

**PASS — owner-run NEW-only static firewall check (no writes, no container startup):** The exact reported sanitized results were:

```text
STAGE17L_REHEARSAL_SCOPE_VERIFIED
INBOUND_SOURCE_SUBNET_MATCH=True
INBOUND_SOURCE_NEGATED=True
OUTBOUND_DEST_SUBNET_MATCH=True
OUTBOUND_DEST_NEGATED=True
CONNTRACK_ESTABLISHED_RELATED_ONLY=True
STAGE17L_READ_ONLY_CHECK_COMPLETE
DYNAMIC_EGRESS_ISOLATION_NOT_YET_PROVEN
```

The script's early NEW hostname/operator/default local-Docker endpoint, exact 3 running pinned DB/Redis-only rehearsal containers, no published ports/restarts, internal non-attachable IPv4 bridge, 4 named volumes, host `FORWARD DROP`, `DOCKER-FORWARD` ordering and `DOCKER-INTERNAL` two DROP-rule structure guards all passed. The inbound-to-bridge DROP rule applies to **source addresses outside the exact rehearsal subnet**, and the outbound-from-bridge DROP rule applies to **destination addresses outside the exact rehearsal subnet**. The preceding `DOCKER-CT` ACCEPT was confirmed limited by conntrack to `ESTABLISHED,RELATED` (not generic NEW traffic). Together with stages 17H–17K, this provides coherent **static evidence** that ordinary *new forwarded IPv4 flows* from the isolated rehearsal bridge to external destinations should be blocked while same-bridge traffic is allowed.

**Safety/limits:** This is **not** a packet-level negative-egress test and does not exclude host gateway/INPUT/OUTPUT paths, native nftables hooks, host networking, privilege escalation, or side effects of an app-capable process. Previous 17K STOP was caused by an over-specific script assertion, resolved by the additional subnet predicate check; do not 'fix' Docker rules. The user has **not** authorized a new outbound test container, active external probes, Frappe/Bench startup, mail/worker/scheduler, DB writes or production cutover by merely sharing Stage 17L output. OLD live PROD and DEV remain preserved.

**Next decisive action:** Design **one** separately approved, tightly bounded NEW-only dynamic **negative-egress** probe, after fresh exact Docker/network/host scope and destination-safety review; use an ephemeral no-mount/no-secret, unprivileged, read-only, capability-dropped probe with no published ports, no DNS/service calls or business traffic, preselected safe destination(s), no automatic retries, and cleanup/re-count validation. Avoid testing random/public addresses and avoid treating a timeout alone as proof of filtering. If even this cannot safely prove host-path isolation, protect the eventual app-runtime test by stronger namespace/network restrictions. Only after explicit approval and verification should a DB-connected Frappe diagnostic be planned; do not launch application/web/jobs or migrate now.

## NEW REHEARSAL STAGE 17K SANITIZED FIREWALL RULE DIAGNOSTIC PASS — 2026-11-07

**PASS for bounded diagnostic, not yet egress isolation:** Owner ran the corrected read-only Stage 17K diagnostic on NEW `ccpcadmin@ccpcerp-prod` and reported:

```text
STAGE17K_REHEARSAL_SCOPE_VERIFIED
INTERNAL_RULE_01:IN=ABSENT,OUT=BRIDGE_POSITIVE,TARGET=DROP,EXTRA_FLAGS=-s
INTERNAL_RULE_02:IN=BRIDGE_POSITIVE,OUT=ABSENT,TARGET=DROP,EXTRA_FLAGS=-d
STAGE17K_SANITIZED_DIAGNOSTIC_COMPLETE
OUTBOUND_ISOLATION_NOT_YET_PROVEN
```

**Interpretation:** Exact NEW rehearsal scope checks passed, and DOCKER-INTERNAL contains two DROP rules: one matching traffic outgoing **to** the isolated bridge with a source address (`-s`) predicate, and the other matching traffic incoming **from** the isolated bridge with a destination address (`-d`) predicate. The earlier 17K assertion incorrectly expected *negated interface* selectors; the actual rules use positive bridge selectors plus address predicates. The diagnostic did not reveal the source/destination address networks or whether those `-s`/`-d` predicates themselves were negated. This explains the previous STOP as an overly specific guard rather than proof of a breach. No firewall/container/DB/service changes; OLD PROD and DEV untouched.

**Next bounded Stage 17L:** On NEW-only guarded read-only inspection, compare the `-s` and `-d` network predicates to the exact rehearsal Docker IPAM subnet, determine whether each is negated (including either `! -s` or `-s !` syntax), and confirm the DOCKER-CT rule is limited to established/related flow rather than a broad bypass. Print only boolean match classifications and safe status markers; never raw host firewall text, host interface names, addresses, secrets or business records. Stop on unknown predicate/changed scope. This is a static firewall check only; **dynamic egress/host namespace limits remain unproven**, and no app/Bench startup, Docker changes, external probe, site migration, OLD PROD/DEV operation or cutover is authorized.

## NEW REHEARSAL STAGE 17K STRICT FIREWALL MATCH CHECK STOPPED — 2026-11-07

**STOP — owner-run read-only NEW-host verification:** The Stage 17K Python/iptables diagnostic reached the internal-chain rule assertion and printed exactly `STOP: internal bridge negation mismatch` before returning to `ccpcadmin@ccpcerp-prod`. The script's earlier host identity, local Docker context, rehearsal internal bridge, exactly three pinned running DB/Redis containers with no ports, four volume names, FORWARD DROP and first-chain ordering guards had passed or else it would have stopped earlier. No Docker, firewall, database or service writes are in that script.

**Interpretation:** This is a mismatch between the script's **hardcoded expected match pattern** and the actual parsed `DOCKER-INTERNAL` rules, **not** evidence proving an outbound path or a firewall breach. Prior Stage 17J sanitized `OTHER_MATCH:True` did not disclose interface negation form or other non-interface predicates, so the check was deliberately inconclusive. Do not rerun Stage 17K unchanged and do not change firewall rules to make an assertion pass.

**Next single safe action:** Run a NEW-only, read-only diagnostic that rechecks the same exact Docker rehearsal scope and prints **only sanitized classifications** for `DOCKER-INTERNAL` match flags: presence of `-i` and `-o`, whether each matches the exact derived bridge, whether `!` applies, DROP target and safe names of any additional predicate flags. Never print raw rule text, interfaces/IPs, other host firewall infrastructure or secrets. Distinguish a script expectation error from a real rule-ordering or match problem before contemplating a separately approved negative-egress test. No Frappe process, new containers, external probes, firewall edits, DB changes, OLD PROD/DEV or cutover.

## NEW REHEARSAL STAGE 17J READ-ONLY DOCKER FILTER-CHAIN TRAVERSAL REPORTED — 2026-11-07

**Owner-provided Stage 17J output, read-only on NEW rehearsal scope** (no Docker/firewall mutation reported):

```text
STAGE17J_DOCKER_ISOLATION_VERIFIED
HOST_FORWARD_POLICY=DROP
CHAIN_FORWARD_RULES=8
FORWARD_RULE_01=TARGET:DOCKER-USER,IN:ANY,OUT:ANY,OTHER_MATCH:False
FORWARD_RULE_02=TARGET:DOCKER-FORWARD,IN:ANY,OUT:ANY,OTHER_MATCH:False
FORWARD_RULE_03..08=TARGET:OTHER
CHAIN_DOCKER-USER_RULES=0
CHAIN_DOCKER-FORWARD_RULES=5
DOCKER-FORWARD_RULE_01=TARGET:DOCKER-CT,IN:ANY,OUT:ANY,OTHER_MATCH:False
DOCKER-FORWARD_RULE_02=TARGET:DOCKER-INTERNAL,IN:ANY,OUT:ANY,OTHER_MATCH:False
DOCKER-FORWARD_RULE_03=TARGET:DOCKER-BRIDGE,IN:ANY,OUT:ANY,OTHER_MATCH:False
DOCKER-FORWARD_RULE_04=TARGET:ACCEPT,IN:OTHER,OUT:ANY,OTHER_MATCH:False
DOCKER-FORWARD_RULE_05=TARGET:ACCEPT,IN:BRIDGE,OUT:BRIDGE,OTHER_MATCH:False
CHAIN_DOCKER-INTERNAL_RULES=2
DOCKER-INTERNAL_RULE_01=TARGET:DROP,IN:ANY,OUT:BRIDGE,OTHER_MATCH:True
DOCKER-INTERNAL_RULE_02=TARGET:DROP,IN:BRIDGE,OUT:ANY,OTHER_MATCH:True
CHAIN_DOCKER-BRIDGE_RULES=1
DOCKER-BRIDGE_RULE_01=TARGET:DOCKER,IN:ANY,OUT:OTHER,OTHER_MATCH:False
CHAIN_DOCKER-CT_RULES=1
DOCKER-CT_RULE_01=TARGET:ACCEPT,IN:ANY,OUT:OTHER,OTHER_MATCH:True
STAGE17J_READ_ONLY_CHAIN_TRAVERSAL_COMPLETE
```

**Interpretation / limits:** The host FORWARD policy is DROP; first top-level jumps reach the empty DOCKER-USER chain and then Docker forwarding. DOCKER-FORWARD checks DOCKER-CT and DOCKER-INTERNAL before its broad ACCEPT rules. The dedicated internal chain includes two DROP rules referencing the isolated rehearsal bridge. This is **consistent with** intended bridge isolation, but the sanitized flags `OTHER` and `OTHER_MATCH:True` do not tell us whether interface predicates are *negated*, whether DOCKER-CT ACCEPT is limited to established/related flows, or whether other nftables/hook/host paths exist. The `STAGE17J_DOCKER_ISOLATION_VERIFIED` marker indicates script scope/preflight passed, **not** independently proven absence of outbound egress. No active egress test, DB-coupled Frappe startup or live migration was evidenced.

**Next bounded Stage 17K:** On **NEW** `ccpcadmin@ccpcerp-prod` only, perform a strict-scope **read-only, sanitized** check of *match semantics* for `DOCKER-INTERNAL` and `DOCKER-CT`: whether the rehearsal bridge `-i`/`-o` conditions are negated, exact conntrack state categories (without interface/IP names), and whether any earlier unexpected broad ACCEPT/jump can bypass the intended drops. Cross-check current Docker internal bridge, exact three isolated service endpoints, and four rehearsal volumes before interpretation. Stop on changed scope or unrecognized rule shapes. Do not print raw firewall rules, interface addresses, site configs or credentials. Still no new containers, external probes, Frappe/Bench, DB modifications, firewall edits, service restarts, OLD PRODUCTION or DEVELOPMENT operations. Even a passing static check is not a substitute for separately authorized bounded negative-egress verification before running an app-capable process.

## NEW REHEARSAL STAGE 17I FIREWALL RULE DIRECTIONS PASS; CHAIN TRAVERSAL PENDING — 2026-11-07

**PASS — owner-run Stage 17I strict NEW-only isolated Docker scope and read-only firewall rule-direction inspection completed.** Exact output:

```text
STAGE17I_DOCKER_ISOLATION_VERIFIED
HOST_FORWARD_POLICY=DROP
FORWARD_RULE_COUNT=8
FORWARD_TARGET_ORDER=DOCKER-USER,DOCKER-FORWARD,OTHER,OTHER,OTHER,OTHER,OTHER,OTHER
BRIDGE_RULE_01=CHAIN:DOCKER-FORWARD,IN:BRIDGE,OUT:BRIDGE,TARGET:ACCEPT,STATE_MATCH:False
BRIDGE_RULE_02=CHAIN:DOCKER-INTERNAL,IN:ANY,OUT:BRIDGE,TARGET:DROP,STATE_MATCH:False
BRIDGE_RULE_03=CHAIN:DOCKER-INTERNAL,IN:BRIDGE,OUT:ANY,TARGET:DROP,STATE_MATCH:False
NFT_BRIDGE_RULE_COUNT=3
STAGE17I_READ_ONLY_RULE_DIRECTION_COMPLETE
```

**Interpretation:** The three bridge-referencing filter rules are (1) same-rehearsal-bridge traffic ACCEPT in `DOCKER-FORWARD`, and (2)/(3) inbound to and outbound from the isolated rehearsal bridge DROP in `DOCKER-INTERNAL`; host FORWARD policy DROP. Eight top-level FORWARD chain rules jump first to `DOCKER-USER`, then `DOCKER-FORWARD`, followed by six targets the allowlist classified as OTHER (not automatically ACCEPT). IPv6 disabled; earlier 17H no matching bridge NAT/MASQUERADE. These are **consistent with isolation but not full proof**: ordering and targets *inside* `DOCKER-USER` and `DOCKER-FORWARD` could alter whether `DOCKER-INTERNAL` DROP rules are reached, and native nftables, OUTPUT/INPUT, host network namespaces and side-effect paths still require separate review.

**Next bounded Stage 17J:** Read-only inspect first-stage chains and jumps `FORWARD`, `DOCKER-USER`, `DOCKER-FORWARD`, `DOCKER-INTERNAL`, any referenced `DOCKER-BRIDGE`/`DOCKER-CT` rules. Report sanitized ordered targets, incoming/outgoing relation to rehearsal bridge, existence of broad ACCEPT, rule match predicates and state matches; do not print raw firewall rules, source/dest/IP strings, host interface names or unrelated infrastructure identifiers. Guard exact NEW host/user/local Docker endpoint and strict three pinned DB/Redis service identities, network full endpoint IDs and four rehearsal volumes. Static traversal alone does not authorize app network egress or outbound events. No new container, firewall edits, DB modifications, Frappe startup or PROD/DEV action.

## NEW REHEARSAL STAGE 17H FIREWALL RULE COUNT INSPECTION PASS — 2026-11-07

**PASS — owner-run NEW-only, read-only Docker bridge + firewall count inspection.** Operator-reported sanitized result:

```text
STAGE17H_DOCKER_AND_BRIDGE_VERIFIED
HOST_FORWARD_POLICY=DROP
IPTABLES_BRIDGE_FILTER_RULES=3
IPTABLES_BRIDGE_ACCEPT_RULES=1
IPTABLES_BRIDGE_DROP_REJECT_RULES=2
IPTABLES_BRIDGE_NAT_RULES=0
IPTABLES_BRIDGE_MASQUERADE_RULES=0
NFT_BRIDGE_REFERENCING_RULES=3
STAGE17H_READ_ONLY_FIREWALL_INSPECTION_COMPLETE
```

**Meaning:** Prior strict NEW-local Docker 3-container/4-volume/internal IPv4-only bridge and pinned DB/Redis checks passed. Bridge interface exists and has the Docker network IPAM gateway; host iptables FORWARD chain default policy is DROP. On bridge-referencing iptables filter rules, three entries: one ACCEPT and two DROP/REJECT; no bridge-referencing iptables NAT or MASQUERADE; nft reports three bridge-referencing rules. No firewall modification or app/DB connection occurred. This is **positive evidence consistent with network isolation but NOT proof** of outbound blocking: a broader preceeding ACCEPT/jump chain, return-path semantics, rules in other tables, nft hooks, or host-forward routing could matter. Only after examining rule ordering and direction plus independently controlled validation can a restricted Frappe runtime be considered. Stage 17F SELECT-only login remains verified; read-only diagnostic account is preserved; no Frappe startup authorized.

**Next bounded Stage 17I:** Under strict owner/host/local-Docker preflight and network full-ID checks, inspect `iptables-save -t filter` and `nft -j list ruleset` **read-only**, derive bridge from exact current Docker network ID, and summarize **only** rule order/chain category/direction (`-i` vs `-o` and negation), target category (ACCEPT/DROP/REJECT/RETURN/jump), and connection-state presence for bridge-referencing filter rules. Also report FORWARD chain target order (sanitized) to assess possible earlier bypass; never emit raw rules, source/dest IPs, unrelated host firewall details, interface names, secrets or business records. This remains an interpretation aid, not proof of no egress, and must STOP if firewall output is unrecognized or unexpectedly changed. No operational firewall changes, new containers, active external probes, Frappe/Bench runtime, DB write, PROD/DEV interaction, or deployment.

## NEW REHEARSAL STAGE 17G READ-ONLY NETWORK AND FIREWALL TOOL INVENTORY PASS — 2026-11-07

**PASS — owner-run isolated NEW-only network/firewall inventory, with no changes.** Operator output:

```text
STAGE17G_DOCKER_SCOPE_VERIFIED
NETWORK_INTERNAL=True
NETWORK_ATTACHABLE=False
NETWORK_IPV6_ENABLED=False
NETWORK_GATEWAY_MODE=default
NETWORK_BRIDGE_OPTION_PRESENT=False
HOST_IPV4_FORWARDING_ENABLED=True
IPTABLES_FIREWALL_INSPECTION=READABLE
NFT_FIREWALL_INSPECTION=READABLE
STAGE17G_READ_ONLY_NETWORK_INVENTORY_COMPLETE
```

**Interpretation:** The owner-run NEW-only local Docker scope verification still found exactly the three isolated rehearsal containers on an internal non-attachable IPv4-only bridge, with no published ports. No explicit bridge-name option or gateway-mode option was configured; Docker uses its defaults. The host's IPv4 forwarding is on, and iptables and nftables inspection commands are readable by sudo. **IPv4 forwarding alone neither proves a breach nor proves the Docker bridge can reach outside**, and the presence of firewall tooling says nothing about whether its rules deny egress. Do not claim internet isolation has been verified by Stage 17G; the last proven app-related operation remains Stage 16 *offline imports*, and the only DB-coupled client test is Stage 17F SELECT-only MariaDB client.

**Next safe Stage 17H:** Under same owner and local-Docker guards, run read-only enumeration of the actual isolated bridge interface derived from the current Docker network ID, compare assigned IP/gateway and endpoint IP addresses to the expected IPv4-only `172.18.0.0/16`, check that no new containers/volumes are present, and inspect `iptables-save -t filter`, `iptables-save -t nat`, and `nft -j list ruleset` without printing the raw firewall or route configuration. Report only sanitized total bridge-referencing rules, bridge-target ACCEPT/DROP/REJECT counts, FORWARD default policy and nft bridge-reference counts. Need further direction-of-flow and dynamic egress validation under safe, explicitly scoped controls before asserting outbound isolation; counts alone are not proof. No policy, routing or container changes, no TCP traffic to arbitrary destinations, no Frappe service, no DB writes/migrations, no OLD PROD/DEV or cutover.

## NEW REHEARSAL STAGE 17F SELECT-ONLY TCP LOGIN VERIFIED — 2026-11-07

**PASS — owner-run NEW `ccpcadmin@ccpcerp-prod` bounded one-off MariaDB diagnostic client authentication and SELECT metadata query, with temporary client removed.** Exact operator output:

```text
REHEARSAL_STAGE17F_ISOLATION_VERIFIED
REHEARSAL_READONLY_CREDENTIAL_VERIFIED
REHEARSAL_READONLY_TCP_LOGIN_VERIFIED
REHEARSAL_READONLY_EXACT_HOST_GRANT_VERIFIED
REHEARSAL_READONLY_SCHEMA_SELECT_VERIFIED
REHEARSAL_RESTORED_DATABASE_STRUCTURE_VERIFIED
REHEARSAL_STAGE17F_CLIENT_REMOVED
REHEARSAL_STAGE17F_SELECT_ONLY_LOGIN_COMPLETE
```

**Meaning:** Preflight verified local NEW Docker daemon, isolated three persistent rehearsal DB/Redis containers and four named volumes, pinned image IDs, internal bridge, exact IPAM scope and temporarily available `172.18.0.250`. The protected new mode 0600 diagnostic credential file `/home/ccpcadmin/.ccpc-rehearsal-secrets-20261107/readonly-db-probe.env` passed identity/ownership/mode checks; values were not printed. From a one-shot `--rm --pull never --network ccpc_restore_rehearsal_20261107_default --ip 172.18.0.250 --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges` MariaDB *client-only* container with no mounted DB/site/secret volume, a password sent via stdin allowed TCP authentication to service `db`. `CURRENT_USER()` matched the exact account `ccpc_ro_probe_20261107@172.18.0.250`, and a SELECT-only information_schema query returned exactly **741 BASE TABLE** and **6 SEQUENCE** objects. The ephemeral client was removed and persistent service/network/volume counts were rechecked unchanged. **This tests successful allowed reads; it did not issue a forbidden DML/DDL statement**. The separately verified Stage 17E grants and metadata scope demonstrate the SELECT-only restriction. No app, scheduler, web, worker, migrations, emails, integrations, original production, DEV, or cutover actions.

**Stage 17 status:** 17A read-only inspected existing app account (schema write permissions), 17B audited scope/no global roles, 17C confirmed new identity available, 17D corrected an ID truncation false-positive and confirmed Docker fixed IP, 17E explicitly approved and created account with exactly one schema SELECT grant/no detected other privileges, 17F authenticated via actual IP-limited TCP and verified restored schema structure. Keep the existing full-privilege app account and restored site configuration unchanged; preserve the separate diagnostic secret as protected, and do not move it into site config or expose it in logs/GitHub.

**Next safe boundary:** Do not infer Docker `Internal=true` provides independently proven outbound connectivity isolation for an **app-capable** Frappe process, and do not infer Frappe can initialize with a read-only account without trying any writes. First perform **read-only network/routing and enforcement inventory** on the NEW host: review exact dedicated network properties and relevant routing/firewall/nftables/iptables/forward policies, Docker host gateway and whether the ephemeral client namespace might reach destinations beyond DB; avoid printing host secrets/remote IP inventories or modifying firewall. Then design a bounded app runtime with read-only credentials, no internet/other network egress, site mount read-only or synthetic scratch config, no workers/web/queues/mail or scheduled jobs, and snapshot/rollback guard. Approval to create the DB user was **not** approval to run a DB-connected Frappe process. No PROD deployment approval.

## NEW REHEARSAL STAGE 17E SELECT-ONLY DIAGNOSTIC ACCOUNT CREATED AND VERIFIED — 2026-11-07

**PASS — explicitly owner-approved NEW-only account creation executed by owner on `ccpcadmin@ccpcerp-prod`.** Exact sanitized output:

```text
REHEARSAL_STAGE17E_ISOLATION_VERIFIED
DIAGNOSTIC_FIXED_IP_REVERIFIED_UNUSED
DIAGNOSTIC_ACCOUNT_IDENTITY_REVERIFIED_AVAILABLE
READONLY_SECRET_DIRECTORY_READY
READONLY_SECRET_FILE_CREATED_NO_SECRET_DISPLAYED
READONLY_DB_USER_CREATED
READONLY_DB_SELECT_GRANT_APPLIED
READONLY_DB_SCOPE_VERIFIED
READONLY_DB_NO_EXTRA_GRANTS_VERIFIED
REHEARSAL_STAGE17E_READONLY_ACCOUNT_CREATED
```

**Actions actually completed:** Strict NEW-only `ccpc_restore_rehearsal_20261107` Docker identity checks verified three expected pinned DB/Redis running services, internal network and four volumes; historical Nov 5 site backup config SHA verified. Stage 17D had separately verified a former false-positive caused by shortened vs full Docker container IDs; updated corrected network check passed on NEW before any DB write (`DOCKER_SHORT_IDS_TRUNCATED=True`, `NETWORK_MATCHES_SHORT_IDS=False`, `NETWORK_MATCHES_FULL_IDS=True`, `REHEARSAL_INTERNAL_NETWORK_VERIFIED`, expected Docker subnet and currently unused `172.18.0.250`). This is a Docker-internal IP, **not** the host's office `192.168.50.x` LAN.

Within exact approved scope, owner executed `CREATE USER 'ccpc_ro_probe_20261107'@'172.18.0.250' IDENTIFIED BY <fresh random>` and `GRANT SELECT ON <restored Nov 5 schema>.*` only, after rechecking that all candidate identity/grant metadata was absent. Fresh credential securely stored in owner-only `/home/ccpcadmin/.ccpc-rehearsal-secrets-20261107/readonly-db-probe.env` mode 0600 (directory 0700). No credential text, user business rows or raw secret material was printed or committed. The owner-run postcheck reported one exact account entry, one exact schema/host grant with SELECT, zero listed write grants and no individual table/column/routine/role/proxy grants. Existing application account and site config untouched; no site/DB restore, migration, Frappe service, email/integrations, PROD/DEV cutover or other write.

**Boundary:** Account creation and MariaDB metadata scope verified, but **a login from 172.18.0.250 has not been tested**; IP is not permanently reserved. The current grant audit checks SQL schema privileges but does not independently test client authentication, TCP source match, Frappe initialisation, or the possibility of unintended external egress from an app-capable container. Owner approval covers creating and verifying only this diagnostic account. Do not run Frappe/runtime/Bench, scheduler, web, jobs, mail, or integrations.

**Next bounded step:** A one-shot short-lived client-only container sourced from exact pinned MariaDB image ID, `--rm --pull never --network ccpc_restore_rehearsal_20261107_default --ip 172.18.0.250 --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges`, explicit `--entrypoint /bin/sh`, no secrets/site/DB/logs volume mounts and no published ports. Pass new credential only via host Python stdin pipe to container shell and set `MYSQL_PWD` internally (no password in Docker options/argv/image/inspect/output), execute only `mariadb` **TCP SELECT** against DB service, assert `CURRENT_USER()` matches exact `user@ip`, and count the expected 741 BASE TABLE and six SEQUENCE objects. Before invocation recheck host identity, Docker local endpoint, pinned images, three persistent service identities, exact four volumes, internal bridge, three endpoints/full IDs, fixed candidate IP unused and fresh secret owner/mode/known fields; after invocation confirm only three persistent containers/endpoints remain. On any mismatch STOP and preserve state, no reruns if partial. No intentional DML test or application process. After that, separately design and verify outbound fence before any DB-coupled Frappe runtime tests.

## NEW REHEARSAL STAGE 17D NETWORK CHECK STOP; SUSPECT DOCKER SHORT-VS-FULL IDS — 2026-11-07

**STOP — owner-run read-only fixed-IP preflight, no DB changes.** Owner reported:

```text
STOP: network isolation mismatch
```

Owner also clarified local LAN uses `192.168.50.xxx`, which is **not the same namespace as** the previously verified isolated NEW-only Docker bridge `172.18.0.0/16`. Do not replace the planned diagnostic helper IPv4 with a LAN IP, bind ports, or attach to a LAN/macvlan merely to work around a failed check. The Stage 17D script did not create any user/password/container, touch DB/site/volumes, or reserve an IP. The owner approval for creating a bounded SELECT-only diagnostic account remains valid but **not executed**. The proposed `172.18.0.250` is still an unverified/unreserved candidate.

**Strong test-harness cause, pending confirmation:** Stage 17D required `set(net['Containers']) == set(ids)`; `ids` was obtained with `docker ps -aq` (quiet output is normally **shortened container IDs**), whereas `docker network inspect ... Containers` uses full container IDs. An otherwise correct network therefore triggers `network isolation mismatch`. Previous Stage 17C checked the isolated project label, three endpoints and four volumes without the new ID-set comparison and passed. Docker CLI official docs `https://docs.docker.com/reference/cli/docker/container/ls` explain `--no-trunc`. This is **likely a false-positive guard**, not proof network changed.

**Next safe step:** Run a NEW-host/user/local-Docker read-only targeted diagnosis comparing `docker ps -aq` short IDs, `docker ps --no-trunc -aq` full IDs, `docker inspect` `Id`, and `docker network inspect` endpoint IDs **without displaying IDs**; verify network `Internal`, driver, exact project scope label, attached count, true image/container identities, no published ports, expected subnet/gateway, four named volumes and whether `172.18.0.250` is currently unallocated. Never call `CREATE USER` or `GRANT` until the guard is corrected and fresh preflight passes. If real isolation discrepancies exist, STOP and investigate; don't manually change Docker network or existing services. No OLD PROD/DEV, app runtime, migrations, email/integrations or cutover.

## OWNER APPROVAL: STAGE 17 SELECT-ONLY DIAGNOSTIC DB ACCOUNT — 2026-11-07

**Explicit owner approval recorded in active conversation:** After Stage 17C verified `ccpc_ro_probe_20261107` does not exist, the owner replied **“Approved”** to the narrowly scoped proposal: *create and verify a new SELECT-only diagnostic DB account in the isolated NEW rehearsal database*. This is **not** authorization for Frappe runtime, database migration, PROD/DEV access, cutting over, running workers, exposing ports, email, integrations, or altering the existing application account/site config. None of those actions have been performed by this approval, and as of this note **the new account has not yet been created**.

**Proposed exact grant:** `GRANT SELECT ON <restored-schema>.* TO 'ccpc_ro_probe_20261107'@'<exact-static-client-IPv4>'` after `CREATE USER ... IDENTIFIED BY <fresh random>`. No wildcard '%' host grant, no global/other-schema privilege, DML/DDL, GRANT OPTION, roles, or proxy. Store the new credential in a separate mode 0600 regular file within `/home/ccpcadmin/.ccpc-rehearsal-secrets-20261107/` (mode 0700), using exclusive creation, no passwords in argv/logs/GitHub. The old Nov 5 encryption key, historical artifacts, existing Stage 9 DB credential, app site config and SQL rows must remain unmodified. On partial failure STOP and inspect; never overwrite/recreate blindly.

**Safe phased implementation:** First run a read-only IPAM preflight to confirm exact NEW-only Docker endpoint, pinned DB/Redis service IDs, three containers, four labeled volumes, internal bridge CIDR/gateway/endpoint assignments, and a proposed fixed unique diagnostic IPv4 such as `172.18.0.250`. This IP is a **candidate future helper address**, not already an attached/verified container IP. A later CREATE USER step must recheck all guards and collisions immediately before the write. The fixed source address can only be used later by a distinct one-shot helper with explicit `--ip` and separate review. Any app-capable container needs independent outbound/side-effect restriction review; `Internal=true` alone is not proof of egress safety.

**After account creation:** Verify only exact per-schema SELECT privileges and a no-global, no-role, no-write grant scope before any client use; treat DB-account creation and a subsequent DB-coupled app test as separate milestones. A future cleanup should remove *only* the new diagnostic user after separate safety review, without touching the old site app account or database.

## NEW REHEARSAL STAGE 17C READ-ONLY DIAGNOSTIC DB IDENTITY AVAILABLE — 2026-11-07

**PASS — owner-run isolated NEW-only, read-only Stage 17C account-name and schema preflight.** Output reported:

```text
REHEARSAL_STAGE17C_ISOLATION_VERIFIED
REHEARSAL_DATABASE_STRUCTURE_UNCHANGED
DIAGNOSTIC_CANDIDATE_ACCOUNT_ROWS=0
DIAGNOSTIC_CANDIDATE_SCHEMA_ROWS=0
DIAGNOSTIC_CANDIDATE_TABLE_ROWS=0
DIAGNOSTIC_CANDIDATE_COLUMN_ROWS=0
DIAGNOSTIC_CANDIDATE_ROUTINE_ROWS=0
DIAGNOSTIC_CANDIDATE_ROLE_ROWS=0
DIAGNOSTIC_CANDIDATE_PROXY_ROWS=0
REHEARSAL_DIAGNOSTIC_ACCOUNT_IDENTITY_AVAILABLE
REHEARSAL_STAGE17C_READ_ONLY_PREFLIGHT_COMPLETE
```

**Interpretation:** Exact existing NEW rehearsal MariaDB/Redis three-container scope, internal bridge, four volumes and historical backup config SHA/ownership passed guards. Restored Nov 5 database still contains 741 BASE TABLE and six SEQUENCE objects. Candidate `ccpc_ro_probe_20261107` has **zero** existing rows in MariaDB global account, schema, table, column, routine, role and proxy metadata. The proposed diagnostic username is **available**, not yet created or privileged. No password was generated or stored; no CREATE USER/GRANT/ALTER, app/site config, migration or persistent Frappe service was touched.

**Next safe boundary:** Before creating this identity, specify the target single schema and fixed source-IP or appropriately restricted host part; identify the isolated temporary diagnostic client container networking and an independently evaluated egress/side-effect fence; choose a new independent random credential with owner-only 0600 file in the protected rehearsal secrets directory; only `SELECT` on the specific restored schema, no DML/DDL, GRANT OPTION, global or role privileges. Require explicit owner authorization for CREATE USER and GRANT. Verify conflict-free identity immediately before any write. Validate new grants and test using a deliberately write-denied SQL statement only in a tightly bounded safe proof (not against business rows); protect historical site config, original Stage 9 app credentials, and Nov 5 restore. Later DB-connected Frappe test may still not run if startup needs writes; never bypass restriction. Since Docker `internal=true` and absence of published ports do not by themselves prove no outbound reachability or side-effects, **do not run any DB-connected Frappe runtime process until independent containment review**. No OLD PRODUCTION, DEVELOPMENT, live app, outbound mail/integration, or cutover.

## NEW REHEARSAL STAGE 17B DB APP ACCOUNT PRIVILEGE SCOPE PASS — 2026-11-07

**PASS — owner-run NEW-only Stage 17B read-only DB privilege-scope audit on `ccpcadmin@ccpcerp-prod`.** Owner reported:

```text
REHEARSAL_STAGE17B_ISOLATION_VERIFIED
APP_GLOBAL_ACCOUNT_ROWS=1
APP_OTHER_HOST_ACCOUNT_ROWS=0
APP_NONZERO_GLOBAL_PRIVILEGE_ROWS=0
APP_SCHEMA_GRANT_ROWS=1
APP_OTHER_SCHEMA_GRANT_ROWS=0
APP_SCHEMA_SELECT_GRANT=True
APP_SCHEMA_WRITE_GRANT=True
APP_TABLE_GRANT_ROWS=0
APP_COLUMN_GRANT_ROWS=0
APP_ROUTINE_GRANT_ROWS=0
APP_ROLE_GRANT_ROWS=0
APP_PROXY_GRANT_ROWS=0
REHEARSAL_APP_ACCOUNT_DIRECT_SCOPE_EXPECTED
REHEARSAL_STAGE17B_READ_ONLY_SCOPE_AUDIT_COMPLETE
```

**Meaning:** The existing Stage 9 application's MariaDB account is present as one host-`%` account, with zero nonzero global privilege masks, one grant confined to the restored application schema, SELECT and write privileges at schema level, zero individual table/column/routine grants and no role/proxy mappings in the inspected metadata. Strict three-container NEW-only Docker/isolated bridge/four-volume preflight passed. Inspected `mysql.global_priv`, `mysql.db`, `mysql.tables_priv`, `mysql.columns_priv`, `mysql.procs_priv`, `mysql.roles_mapping`, `mysql.proxies_priv` with SQL SELECT only; no passwords or DB names displayed, no grants altered, no applications started. This corroborates earlier Stage 17A and Stage 9's least-scoped normal ERPNext application identity, but **not a read-only identity**. MySQL/MariaDB `% ` grants may allow connections from any reachable source; network fencing must still be independently evaluated.

**Next Stage 17C safest preparation:** New-only *read-only* preflight of candidate unique dedicated diagnostic account identifier, existing MariaDB account/global/schema/routine/role/proxy naming conflicts (report counts/booleans, never names or secrets), image/DB/volume scope and network exposure/host-published ports. Plan single-schema `SELECT` only, isolated credential, source-host restriction, no `GRANT OPTION` or role inheritance. For any later DB account creation, require separate explicit owner authorization and a recorded recovery/rollback plan. Do not modify the existing account, the historical restored site config or DB records. Before Frappe runtime connection, independently prove network egress restrictions; Docker's `Internal` flag alone is insufficient to claim complete isolation, and consider whether a strictly read-only database account permits Frappe initialization (some startup code can try writes and must fail cleanly). No development/old production/live service changes or cutover.

## NEW REHEARSAL STAGE 17A EXISTING APP DB ACCOUNT HAS WRITE PRIVILEGES — 2026-11-07

**PASS — owner-run Stage 17A NEW-only SQL read-only app-account schema privilege check.** Operator reported:

```text
REHEARSAL_STAGE17A_ISOLATION_VERIFIED
APP_SCHEMA_GRANT_ROWS=1
APP_SCHEMA_SELECT_GRANT=True
APP_SCHEMA_WRITE_GRANT=True
REHEARSAL_STAGE17A_READ_ONLY_PRIVILEGE_CHECK_COMPLETE
```

The strict NEW-host/local-Docker three-container database/Redis and network/volume preflight passed. Root SQL session was used **only for SELECT** from `mysql.db` to summarize direct schema grants for the restored application's schema account; exact database account and schema name were loaded from SHA-pinned November 5 backup config and **not printed**. One schema grant row existed; SELECT privilege and one or more DML/DDL write privileges were present. This is normal for ERPNext but **disqualifies that app account for a no-write Frappe runtime smoke**. Existing site password was neither revealed nor changed, no DB account was added, and no Frappe app started.

**Caveat:** `mysql.db` alone does not prove the account has no global grants, role inheritance, table-specific privileges, routine privileges or proxy grants. `APP_SCHEMA_WRITE_GRANT=True` also does not enumerate which writes it has; do not infer a minimal write set from it. The next bounded Stage 17B is a read-only privilege-scope inventory: inspect the MariaDB grant metadata `mysql.global_priv`, `mysql.db`, `mysql.tables_priv`, `mysql.columns_priv`, `mysql.procs_priv`, `mysql.roles_mapping` and `mysql.proxies_priv` as available; verify app-account host patterns, schema grant count and whether any global access or inherited role privileges may exist, and print only sanitized counts/boolean markers. No raw JSON grants, password hashes, DB/schema names, user/host strings, secrets, or business records in terminal output; no GRANT/CREATE/ALTER. Then plan a separately generated restricted SELECT-only diagnostic identity with exact schema, host restrictions and no global grants, **only after separate approval/backup/reversibility review**, and design independent egress fencing before any Frappe process uses the restored DB. No OLD PRODUCTION/DEV or live deployment.

## NEW REHEARSAL STAGE 16 ALL OFFLINE APPLICATION IMPORTS PASS — 2026-11-07

**PASS — Stage 16 offline image Python compatibility smoke completed by owner on NEW `ccpcadmin@ccpcerp-prod`.** Exact sanitized markers:

```text
REHEARSAL_STAGE16_STREAM_ISOLATION_VERIFIED
REHEARSAL_STREAM_LOGGING_ENABLED
REHEARSAL_MODULE_FRAPPE_IMPORT_OK
REHEARSAL_MODULE_FRAPPE_APP_IMPORT_OK
REHEARSAL_MODULE_FRAPPE_HOOKS_IMPORT_OK
REHEARSAL_MODULE_ERPNEXT_IMPORT_OK
REHEARSAL_MODULE_ERPNEXT_HOOKS_IMPORT_OK
REHEARSAL_MODULE_CCPCERP_IMPORT_OK
REHEARSAL_MODULE_CCPCERP_HOOKS_IMPORT_OK
REHEARSAL_STAGE16_ALL_IMPORTS_PASSED
REHEARSAL_STAGE16_COMPLETE_NO_APP_SERVICES_STARTED
```

**Meaning and boundary:** All seven application modules imported successfully using the explicit Bench virtualenv `/home/frappe/frappe-bench/env/bin/python` from the exact pinned local image `ccpcerp:v16.50.0`; import origins were checked to resolve under the corresponding app's immutable image directory. Environment-only `FRAPPE_STREAM_LOGGING=1` selected stream handlers, resolving the artificial `FileNotFoundError` from `frappe.utils.logger.create_handler` when file logging was attempted in a no-mount readonly filesystem. Also a real `/dev/null` stream was used, resolving earlier artificial `io.UnsupportedOperation` from `io.StringIO` lacking `fileno()`. The preflight passed NEW-only three running DB/Redis services, internal bridge and four rehearsal volumes. The transient helper used `--network none --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges`, no mounted site/DB/logs volumes, no site credentials, no DB connectivity. No persistent app services started, no imports of restored site config, no `frappe.init`, Bench, migrations, transactional writes, web, workers, scheduler, email, integrations, DEV, OLD PRODUCTION, or cutover.

**Verified November 5 historical rehearsal milestones through Stage 16:** SQL schema structure 741 BASE TABLE + six SEQUENCE objects; registered frappe, erpnext, ccpcerp; three image/DB version declarations match; 774 patch declarations = 774 distinct successful log entries with zero missing/skipped; offline image package import pass. **Do not infer** successful credentialed site/DB Frappe initialization, user authentication, GL/stock integrity, or production-readiness. No need to reimport the SQL archive, reinstall apps, or `bench migrate` on this evidence.

**Next safe Stage 17 planning:** Start with *read-only safety preflight* on NEW: inspect protected isolated Docker network and container scopes plus database app-account privilege/host grants, and determine if a separate dedicated SELECT-only user can be provisioned for later app runtime probing. A DB-connected Frappe process may attempt writes at initialization or shutdown; using site DB credentials with data modification privileges is **not safe** merely because an operation is described as read-only. Also verify the process cannot reach arbitrary outside hosts: `internal=true` Docker bridge is not sufficient evidence of egress fencing for all namespaces. Keep networkless helpers for offline checks, and do not start a site runtime process until a bounded and verified network/DB-access plan and optional snapshot/recovery boundary are agreed. Zero production deployment approval; OLD PROD/DEV unchanged.

## NEW REHEARSAL STAGE 16 FILE ERROR IS FRAPPE FILE LOGGER; STREAM-ONLY ENV FIX — 2026-11-07

**PASS — owner-run diagnostic, no restored-data writes.** Owner output:

```text
REHEARSAL_FILE_SCOPE_ISOLATION_VERIFIED
MISSING_PATH_SCOPE=FRAPPE_HOME_OTHER
MISSING_PATH_WAS_ABSOLUTE=True
MISSING_PATH_PARENT_EXISTS=False
LAST_FRAPPE_MODULE=frappe.utils.logger
LAST_FRAPPE_FUNCTION=create_handler
LAST_TRACEBACK_FRAME_CATEGORY=PYTHON_LIBRARY
REHEARSAL_MISSING_FILE_SCOPE_DIAG_COMPLETE
REHEARSAL_STAGE16_FILE_SCOPE_INSPECTION_FINISHED
```

The explicit Bench Python venv import of `frappe` succeeds. The `frappe.app` import fails with `FileNotFoundError` because `frappe.utils.logger.create_handler()` attempted to open a path under `/home/frappe` outside Bench and the parent directory is absent in the one-shot, read-only-rootfs, no-mount import environment. The output prints **category only**, not raw missing filename; this does not indicate corrupt app code or database. Check of upstream version-pinned Frappe source `frappe/frappe` at tag `v16.50.0`, file `frappe/utils/logger.py`, git blob SHA `66bac78656febd7ed022a0b63dce2ee064dd2594`: `create_handler(..., stream_only=False)` uses `RotatingFileHandler(os.path.join("..","logs",f"{module}.log"))` unless `stream_only` is truthy; `stream_logging = os.environ.get("FRAPPE_STREAM_LOGGING")`; `get_logger(...,stream_only=stream_logging)` allows the environment-only stream route. This directly explains why an image-only test with a readonly rootfs and no writable logs path can fail.

**Next bounded NEW-only Stage 16 recovery:** Run one-off Bench venv imports for `frappe`, `frappe.app`, `frappe.hooks`, `erpnext`, `erpnext.hooks`, `ccpcerp`, `ccpcerp.hooks` in exactly pinned image, using **`FRAPPE_STREAM_LOGGING=1`** and real file-descriptor stdout/stderr redirected to `/dev/null` during imports. Guard NEW host/user, default local Docker, 3 expected running isolated DB/Redis containers, 4 volumes, and image ID. `--network none --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges --rm`; **do not mount any site/logs/DB volume, create directories, or modify restored configuration**. Only allow sanitized per-module PASS markers and module/type on failure; check origins within pinned immutable image app directories. If more filesystem dependencies are discovered, STOP and inspect instead of adding arbitrary mounts. No `bench migrate`, `frappe.init`, `frappe.connect`, service start, mail, workers, OLD PROD, DEV, or cutover. Even a complete import PASS is not DB-connected Frappe integration or accounting/inventory verification.

## NEW REHEARSAL STAGE 16 MISSING FILE CATEGORY OTHER, _open — 2026-11-07

**PASS — diagnosis script completed, but application import remains STOPPED.** Owner-run NEW-only result:

```text
REHEARSAL_STAGE16_PATH_DIAGNOSTIC_ISOLATION_OK
FRAPPE_APP_EXCEPTION=FileNotFoundError
FRAPPE_APP_MISSING_PATH_CATEGORY=OTHER
FRAPPE_APP_FAILURE_SOURCE_CATEGORY=PYTHON_LIBRARY
FRAPPE_APP_FAILURE_FUNCTION=_open
REHEARSAL_STAGE16_MISSING_FILE_DIAGNOSTIC_COMPLETE
REHEARSAL_STAGE16_PATH_INSPECTION_FINISHED
```

`FileNotFoundError` reproduces during `frappe.app` import in Bench venv with rootfs read-only, `--network none`, UID1000, no capabilities and **no restored site/secret/DB mounts**. Previous classifier returned `OTHER`, outside bench `sites`, `logs`, `assets`, `apps`, `env` and `/tmp`; bottom traceback frame was a generic Python library `_open`. It **does not establish which file or parent directory is missing**: could be another bench-relative path or a user-home/system path. No app/DB changes, no persistent service and no release.

**Next safer diagnostic:** Under identical NEW-only, exact-image, local Docker and environment guards, run **one** more no-network/no-mount/readonly ephemeral Bench Python helper importing `frappe.app` with real `/dev/null` output redirection; classify `exc.filename` without exposing literal path, file contents or private names. Report whether raw path is absolute or relative; bucket resolved path into `BENCH_ROOT_OTHER`, `FRAPPE_HOME_OTHER`, `ETC`, `VAR`, `RUN`, `DEV`, `USR`, `OPT`, `PROC`, `SYS`, `TEMPORARY`, `OTHER`, plus separate known bench sites/logs/assets/apps/env categories. Report whether parent exists and identify the last Frappe-origin frame as sanitized module:function (or NONE), plus last two frame categories; no raw traceback/exception text. Probe remains metadata-only with no explicit file creation or bench commands. If path is a missing image/bench runtime config or logging target, consider **scratch tmpfs only** in a later approved helper; do not mutate restored sites, DB or original backups. Avoid adding arbitrary bind mounts to conceal a code incompatibility. No OLD PRODUCTION/DEV changes or cutover.

## NEW REHEARSAL STAGE 16 FULL OFFLINE IMPORT STOPS AT frappe.app FILE NOT FOUND — 2026-11-07

**PARTIAL/STOP — owner-run complete Stage 16 offline module smoke attempted on NEW `ccpcadmin@ccpcerp-prod`; Frappe root package PASSED, next module FAILED.** User output:

```text
REHEARSAL_STAGE16_FULL_IMPORT_ISOLATION_VERIFIED
REHEARSAL_STAGE16_BENCH_VENV_VERIFIED
REHEARSAL_MODULE_FRAPPE_IMPORT_OK
STOP: offline helper import failed: frappe.app | FileNotFoundError
STOP: offline import verification incomplete; preserve state
```

The pinned Docker image, three running DB/Redis containers, isolated network and four volumes were guarded; a disposable rootfs read-only, `--network none`, UID:GID1000, capability-free Bench venv Python helper imported `frappe` and checked image package origin. It then raised `FileNotFoundError` importing `frappe.app`. **No restored `sites`, secrets, DB, or Redis volumes were mounted or accessed by this test**, and no persistent application service or migration started. ERPNext/CCPC imports remain **UNTESTED**, not failed. This result does not establish application incompatibility or a damaged database.

**Possible origin:** `frappe.app` imports many modules with import-time initialization, which may assume bench `logs` or `sites` runtime directories/configuration. With image-only mountless helper and read-only container filesystem, these files may be unavailable. This remains hypothesis; first identify the sanitized missing-file **category** by catching `FileNotFoundError.filename` and classifying it as expected known bench logs/sites/assets/image paths vs other (no raw path or private filename), combined with a safe traceback module/function category. Do not print any raw exception message, traceback, DB identities, secret config or file content. Keep the same strict isolated one-shot helper, explicit Bench Python, `/dev/null` output suppression (supports fileno), *no mounted restored data*. Inspect before considering any read-only mount of `sites` or writable scratch `logs`; do not create/move any files in existing volumes, reimport DB, start Frappe app, or run migrations. OLD PRODUCTION and DEVELOPMENT untouched. Next checkpoint should record exact diagnosed missing path and only then propose corrected offline import smoke.

## NEW REHEARSAL STAGE 16 FRAPPE IMPORT PASSES WITH REAL FD OUTPUT STREAM — 2026-11-07

**PASS — NEW-only owner-run Frappe single-module import diagnostic after previous `io.UnsupportedOperation` in Stage 16.** Operator output:

```text
REHEARSAL_STAGE16_NULLSTREAM_ISOLATION_VERIFIED
REHEARSAL_BENCH_INTERPRETER_CONFIRMED
REHEARSAL_REAL_OUTPUT_FD_VERIFIED
REHEARSAL_FRAPPE_IMPORT_WITH_REAL_STREAMS_OK
REHEARSAL_STAGE16_FRAPPE_IMPORT_DIAGNOSTIC_COMPLETE
REHEARSAL_STAGE16_FRAPPE_DIAGNOSTIC_FINISHED
```

The guarded local Docker target, exact pinned `ccpcerp:v16.50.0` image ID, three healthy/isolated persistent MariaDB+Redis containers, internal bridge and four volumes passed. A one-shot helper used explicit `/home/frappe/frappe-bench/env/bin/python`, `--network none --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges` with no site/DB/Redis volume mounts and no restored secrets or network access. Output redirection changed from `io.StringIO()` to an opened `/dev/null` with a working `fileno()`; `importlib.import_module('frappe')` then succeeded and module origin was verified inside immutable image `apps/frappe/frappe`. This strongly confirms the prior `UnsupportedOperation` was an artificial output-stream compatibility issue, **not an observed Frappe code import failure**. No persistent application services, Bench, DB reads/writes, migrations, scheduler, frontend, mail, integrations or OLD PROD/DEV modifications.

**What remains open:** The Stage 16 *full* offline import smoke is not yet done: `frappe.app`, `frappe.hooks`, `erpnext`, `erpnext.hooks`, `ccpcerp` and `ccpcerp.hooks` still need tested. Use identical no-network, no-mount helper with explicit Bench venv and real file descriptor output redirection; print only allowlisted successful module markers or a sanitized failure name and exception class. No `frappe.init`, `frappe.connect`, DB-backed runtime, installs, migrations or services. Preserve historical Nov 5 restored rehearsal and all earlier checkpoints. If all module imports pass, Stage 16 static Python compatibility can be marked PASS, **not** final production readiness. Later DB-coupled Frappe validation needs independently verified egress/side-effect fencing and read-only DB credentials.

## NEW REHEARSAL STAGE 16 BENCH IMPORT UnsupportedOperation UNDER StringIO REDIRECTION — 2026-11-07

**STOP — operator-run corrected Stage 16 Python import using Bench venv, NEW `ccpcadmin@ccpcerp-prod`.** Output:

```text
REHEARSAL_STAGE16_CORRECTED_ISOLATION_VERIFIED
REHEARSAL_BENCH_VENV_ACTIVE
STOP: offline helper import failed: frappe | UnsupportedOperation
STOP: corrected offline import incomplete; preserve state
```

**What is confirmed:** Guarded NEW-local Docker scope, pinned custom Frappe image and isolated three-container/four-volume rehearsal passed. The actual Bench venv launched. `importlib.import_module('frappe')` returned `io.UnsupportedOperation` *inside the helper's output suppression context*; no module-import PASS markers followed, and no ERPNext or CCPC import was tested. This was no-network, read-only-rootfs, UID1000, no capabilities, zero site/DB/Redis volume mounts, no restored credentials, no BENCH or persistent app services. Existing SQL/site/attachments all retained.

**Strong test-harness hypothesis, not proven yet:** The helper used `contextlib.redirect_stdout(io.StringIO())` and `redirect_stderr(io.StringIO())`; a library performing `sys.stdout.fileno()` or `sys.stderr.fileno()` raises `io.UnsupportedOperation` because `StringIO` has no OS file descriptor. There is currently no sanitized traceback to locate the exact Frappe import operation. **Do not claim application code is incompatible** or regenerate/migrate any restored artifacts.

**Next safe diagnostic:** Keep the same NEW host, local Docker, pinned image, three-container internal network, expected four volumes preflight. Run a new *one-shot* no-network read-only-rootfs UID1000 no-capabilities helper with explicit Bench Python, **no mounts at all**, and use a real writable `/dev/null` stream for redirected stdout/stderr (supports `fileno()`), checking this locally in the ephemeral helper before importing. The caller must capture stdout/stderr and print only allowlisted test markers or sanitized module and exception type; no raw Frappe output or tracebacks; no site secrets available to helper. Validate imported origins under each image app package, report per-module success. If import still fails, stop at first failure with sanitized type for a separate traceback-origin diagnosis; do not rerun the old StringIO command or enable database-coupled Frappe CLI automatically. No OLD PRODUCTION, DEV or live cutover.

## NEW REHEARSAL STAGE 16 BENCH VIRTUALENV PACKAGE DISCOVERY PASS — 2026-11-07

**PASS — operator-run corrected Bench Python *discovery-only* test on NEW `ccpcadmin@ccpcerp-prod`.** Owner reported:

```text
REHEARSAL_BENCH_PYTHON_ISOLATION_VERIFIED
BENCH_VENV_ACTIVE=True
FRAPPE_SOURCE_EXISTS=True
FRAPPE_DISCOVERABLE=True
FRAPPE_ORIGIN_MATCHES_IMAGE=True
ERPNEXT_SOURCE_EXISTS=True
ERPNEXT_DISCOVERABLE=True
ERPNEXT_ORIGIN_MATCHES_IMAGE=True
CCPCERP_SOURCE_EXISTS=True
CCPCERP_DISCOVERABLE=True
CCPCERP_ORIGIN_MATCHES_IMAGE=True
REHEARSAL_BENCH_PYTHON_DISCOVERY_COMPLETE
REHEARSAL_BENCH_PYTHON_INSPECTION_FINISHED
```

The pinned image `ccpcerp:v16.50.0` Bench venv interpreter `/home/frappe/frappe-bench/env/bin/python` is active and resolves all three app packages to their source directories. This strongly explains why Stage 16's first offline import attempt using the system `python3` failed to discover modules. **Discovery does not import the modules or prove application runtime readiness.** The corrected probe was a temporary no-network, read-only-rootfs, UID1000 no-capabilities container with no mounted restored site; the preflight confirmed NEW-only three Docker services and four rehearsal volumes, no DB query or app start.

**Next owner-approved nonlive Stage 16 recovery:** Use the *explicit Bench venv interpreter* in a single no-network, read-only-rootfs, UID1000, no-capabilities temporary container. Import `frappe`, `frappe.app`, `frappe.hooks`, `erpnext`, `erpnext.hooks`, `ccpcerp` and `ccpcerp.hooks`; check that each imported module originated under the expected immutable image `apps/<app>/<app>` tree. Before import verify only safe flags on the restored config if sites are mounted, or omit site mount entirely to reduce exposure since Python imports do not require restored DB. Only emit allowlisted success markers or sanitized exception *type* and failing module name. Do not output traceback, secret data or private filenames; do not run `frappe.init`, Bench, DB queries, HTTP, workers, scheduler, migrations, backups, email, integrations or any live app service. No OLD PROD or DEV modification. Do not interpret a module import failure as permission to reinstall. Stage 8-15 historical restoration checkpoints remain intact.

## NEW REHEARSAL STAGE 16 PYTHON PATH DIAGNOSIS: DEFAULT INTERPRETER NOT BENCH ENV — 2026-11-07

**PASS — read-only offline path diagnosis completed on NEW `ccpcadmin@ccpcerp-prod`; Stage 16 import test is still UNVERIFIED.** Owner-supplied output:

```text
REHEARSAL_IMPORT_DIAGNOSTIC_ISOLATION_VERIFIED
PYTHON_USES_BENCH_ENV=False
BENCH_ENV_PYTHON_EXISTS=True
FRAPPE_SOURCE_PACKAGE_EXISTS=True
FRAPPE_APP_PATH_ON_SYS_PATH=False
FRAPPE_MODULE_DISCOVERABLE=False
FRAPPE_MODULE_ORIGIN_MATCHES_IMAGE=False
ERPNEXT_SOURCE_PACKAGE_EXISTS=True
ERPNEXT_APP_PATH_ON_SYS_PATH=False
ERPNEXT_MODULE_DISCOVERABLE=False
ERPNEXT_MODULE_ORIGIN_MATCHES_IMAGE=False
CCPCERP_SOURCE_PACKAGE_EXISTS=True
CCPCERP_APP_PATH_ON_SYS_PATH=False
CCPCERP_MODULE_DISCOVERABLE=False
CCPCERP_MODULE_ORIGIN_MATCHES_IMAGE=False
REHEARSAL_PYTHON_PATH_DIAGNOSTIC_COMPLETE
REHEARSAL_IMPORT_PATH_INSPECTION_FINISHED
```

The pinned image contains all three source packages and its `/home/frappe/frappe-bench/env/bin/python` exists. The **system `python3` used by Stage 16 and this diagnostic is not the Bench virtualenv interpreter**, and none of the three app package parents are in that interpreter's `sys.path`, so none was discoverable by `find_spec`. This **explains the apparent Stage 16 failure far more parsimoniously than bad app code**; the venv's own package discoverability is still unverified and must be checked. This was only a Python path check, no application imports, DB/site modifications or service starts.

**Next NEW-only bounded step:** Guard NEW host/user, default local Docker target, pinned image digest, exactly three expected running pinned MariaDB+Redis containers on internal bridge with no exposed ports, four rehearsal-labeled volumes. Run `/home/frappe/frappe-bench/env/bin/python` explicitly inside a one-shot `--network none --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges --rm` pinned image helper **with no volume mounts whatsoever**, and use `importlib.util.find_spec` to check top-level `frappe`, `erpnext`, `ccpcerp` discoverability and origin constrained to the image's expected app directory; report sanitized booleans only. `sys.prefix` should point to the bench virtualenv; don't rely on `sys.executable` resolving symlink to determine venv use. Do **not** run application imports yet; if packages can be discovered, design a corrected offline Stage 16 import smoke with the Bench interpreter and same isolation. If not, stop and inspect packaging. No `bench`, migrations, restored DB writes or connectivity, app services, PROD/DEV changes, or cutover.

## NEW REHEARSAL STAGE 16 OFFLINE PYTHON IMPORT TEST INCOMPLETE — 2026-11-07

**STOP, no installation or migration authorized.** Operator ran Stage 16 NEW-only offline application import test on `ccpcadmin@ccpcerp-prod` and pasted:

```text
REHEARSAL_STAGE16_ISOLATION_VERIFIED
REHEARSAL_OFFLINE_SITE_CONFIGURATION_VERIFIED
STOP: offline import test incomplete; preserve rehearsal state
```

The 3-container/4-volume/internal-network/pinned image checks and site safe-off switches passed. No `REHEARSAL_MODULE_*_IMPORT_OK` markers appeared and the final success marker was absent. The helper ran with `--network none --read-only --user 1000:1000 --cap-drop ALL --mount ...readonly` and no DB/Redis connectivity or persistent app service. Host wrapper discarded stderr and only forwarded allowlisted marker lines and `STOP: offline helper ...` stdout. Because none appeared, **actual failure reason is NOT KNOWN**: possible Python interpreter/site-packages mismatch, import exception, module origin/path check, error on stderr, or helper startup problem. Do not assert code incompatibility or that app would fail when started normally.

**Next safest NEW-only read-only diagnostic:** Without importing Frappe or executing app code, check the same pinned image under the same no-network/read-only/UID1000 envelope and restored sites volume mounted read-only. Report sanitized Python interpreter location as category, runtime version, cwd and app path presence, `sys.path` app-code parent membership, `importlib.util.find_spec('frappe'|'erpnext'|'ccpcerp')` module discoverability and whether each resolved package origin is inside its pinned image app directory. Optionally inspect `env/bin/python` presence and executable metadata. Do not expose absolute paths, secrets, private file names, exception text, or run `bench`, `frappe.init`, `frappe.connect`, workers, migrations, web, mail, or code-changing operations. Depending on results, make a separate tiny, safely sanitized import exception-type-only probe, not a blind Stage 16 rerun. Preserve SQL stage 8, new DB account stage 9, configs/attachments stages 10-11 and installed app/versions/patches stages 12-15. No OLD PRODUCTION, DEV, employee-facing services or live cutover.

## NEW REHEARSAL STAGE 15 ALL 774 PINNED PATCH DECLARATIONS SUCCESSFULLY LOGGED — 2026-11-07

**PASS — owner-run NEW-only Stage 15 read-only comparison of image patch declarations with restored DB `tabPatch Log`.** Output supplied:

```text
REHEARSAL_STAGE15_ISOLATION_VERIFIED
REHEARSAL_PATCH_LOG_ROWS=774
REHEARSAL_PATCH_LOG_SUCCESSFUL_DISTINCT=774
REHEARSAL_PATCH_LOG_SKIPPED_DISTINCT=0
REHEARSAL_FRAPPE_PATCH_DECLARATIONS=267
REHEARSAL_FRAPPE_PATCHES_WITHOUT_SUCCESS_LOG=0
REHEARSAL_ERPNEXT_PATCH_DECLARATIONS=504
REHEARSAL_ERPNEXT_PATCHES_WITHOUT_SUCCESS_LOG=0
REHEARSAL_CCPCERP_PATCH_DECLARATIONS=3
REHEARSAL_CCPCERP_PATCHES_WITHOUT_SUCCESS_LOG=0
REHEARSAL_TOTAL_DISTINCT_PATCH_DECLARATIONS=774
REHEARSAL_DECLARED_PATCHES_ALL_SUCCESSFULLY_LOGGED
REHEARSAL_STAGE15_READ_ONLY_PATCH_AUDIT_COMPLETE
```

**Validated meaning:** All 267 distinct Frappe, 504 ERPNext, and 3 CCPC custom application patch declarations from the pinned `ccpcerp:v16.50.0` image have a corresponding **successful** (skipped=0) Patch Log record in the restored November 5 SQL database. 774 total log records are distinct, with zero skipped, and all 774 declared patch strings matched. This corroborates the Stage 14 `MATCH` of all three app version declarations to `tabInstalled Application` records. Stage 15 did not run any patches, import code, execute bench commands, start application services, or write to the DB/volume. Three isolated DB/Redis containers, private bridge and labeled volumes remained the only persistent environment as reported by the operator. Do **not** migrate/install/reimport or reset the restored database on this evidence.

**Important boundary:** This is **patch registry completeness**, not actual execution replay, model-schema diff, decoded credentials test, GL/stock ledger audit, permissions test, employee-facing app operation or final cutover readiness. A migration can have other work outside patch log, so no `bench migrate` without a separately reviewed plan. Also, an internal Docker bridge by itself is not a demonstrated outbound network fence for arbitrary Frappe process execution; scheduler/email off switches are additional but not sufficient standalone safeguards.

**Next bounded Stage 16 without live app processes:** perform a no-network, no-write, UID1000 helper `--read-only --cap-drop ALL` import/compatibility smoke on the exact pinned image, with only the already restored `sites` named volume **read-only**, no DB or Redis network access. Validate that Frappe/ERPNext/CCPC Python application package imports and static hook loading do not fail in the current image; no `frappe.init`, `bench`, `frappe.connect`, jobs, web server, migrate, or event firing. Treat any import error as a diagnostic without modifying image/site/DB. Independently inspect Docker egress and side-effect constraints before any later live DB-coupled Frappe runtime test; use a dedicated read-only database account and restrictive runtime if that test is approved, rather than letting full-privileged site DB credentials mutate the restored copy. Keep OLD PRODUCTION, DEVELOPMENT and live services untouched. This historic backup is rehearsal only.

## NEW REHEARSAL STAGE 14 PINNED APP VERSIONS MATCH RESTORED DB — 2026-11-07

**PASS — owner-run read-only Stage 14 version checks on NEW `ccpcadmin@ccpcerp-prod`.** Owner reported:

```text
REHEARSAL_STAGE14_ISOLATION_VERIFIED
REHEARSAL_THREE_APP_VERSION_RECORDS_VERIFIED
REHEARSAL_RECORDED_PATCH_LOG_ROWS=774
REHEARSAL_CCPCERP_VERSION_COMPARISON=MATCH
REHEARSAL_ERPNEXT_VERSION_COMPARISON=MATCH
REHEARSAL_FRAPPE_VERSION_COMPARISON=MATCH
REHEARSAL_STAGE14_READ_ONLY_VERSION_CHECK_COMPLETE
```

**Meaning:** The NEW-only isolated rehearsal DB/Redis network, pinned image, named volumes and restored schema survived preflight; the `tabInstalled Application` records for all three required apps were complete. Each restored DB `app_version` (or `version`) agreed with static `__version__` (or supported `pyproject.toml` declaration) from the pinned local `ccpcerp:v16.50.0` image for frappe, erpnext and ccpcerp; `tabPatch Log` contains **774** existing records. This was a metadata-only SQL read plus offline AST/static file inspection in a no-network readonly helper, not `bench` execution or app bootstrap. **Version equality is not proof that all required patches/migrations ran** and patch log row count is not validation of individual patch status, schema compatibility or ledger correctness. Do not run `bench migrate` or start any backend, scheduler, queue workers, frontend, websocket or mail/integrations yet. No OLD PRODUCTION/DEV changes or cutover.

**Next fastest safe NEW-only guard:** Read-only audit of actual `patches.txt` declarations in the pinned image against restored `tabPatch Log.patch` records (without displaying raw patch names or business data), in combination with verifying that the current custom app and framework app packages are present in the site app registry. Treat missing historical/conditional patch declarations as **review candidates, not permission to run migration**; source declarations can change and logged patches can be older than current files. Preserve 741 BASE TABLE + six SEQUENCE inventory and current archive/site fingerprints. After static patch review, proceed toward a **bounded actual Frappe runtime read-only test** only with independently verified egress/side-effect fencing, no mail/queue/scheduler, and a separate read-only SQL account so a CLI cannot accidentally mutate restored database. The user-approved historical Nov 5 rehearsal is not a live cutover or release approval.

## NEW REHEARSAL STAGE 13 DATABASE INSTALLED-APP REGISTRY VERIFIED — 2026-11-07

**PASS — owner-run Stage 13 read-only Frappe installed-app metadata verification on NEW `ccpcadmin@ccpcerp-prod`.** Owner provided:

```text
REHEARSAL_STAGE13_ISOLATION_VERIFIED
REHEARSAL_DATABASE_STRUCTURE_UNCHANGED
REHEARSAL_DEFAULT_VALUES_SCHEMA_VERIFIED
RESTORED_GLOBAL_INSTALLED_APPS_ROWS=1
RESTORED_GLOBAL_INSTALLED_APPS_COUNT=3
RESTORED_APP_FRAPPE_PRESENT=True
RESTORED_APP_ERPNEXT_PRESENT=True
RESTORED_APP_CCPCERP_PRESENT=True
RESTORED_INSTALLED_APPLICATIONS_SINGLE_DOCTYPE=True
RESTORED_CHILD_APPLICATION_RECORDS=3
RESTORED_CHILD_APPS_SUBSET_OF_GLOBAL=True
REHEARSAL_THREE_REQUIRED_DATABASE_APPS_CONFIRMED
REHEARSAL_STAGE13_READ_ONLY_APP_METADATA_COMPLETE
```

**Conclusion:** Restored historical November 5 SQL database has the global `__global/installed_apps` JSON in `tabDefaultValue`, containing **exactly** `frappe`, `erpnext`, `ccpcerp`, all valid identifiers with no duplicate. `Installed Applications` is a **Single** DocType, and the child metadata table `tabInstalled Application` contains three application records whose names are contained in the global list. This resolves Stage 12's `tabInstalled Applications` missing-physical-table observation as an incorrect physical-table assumption, **not a missing app installation**. DB remains exactly 741 BASE TABLE and six SEQUENCE objects; identity, isolation, NEW only, verified. No ERPNext startup, bench, SQL write, migrations, scheduled jobs, mail or external access during Stage 13.

**Next guarded NEW-only read-only Stage 14 option:** Compare the three installed-app version values (where present) in `tabInstalled Application` and stored migration patch state against version declarations in the already-pinned image, using a no-network readonly-sites one-shot container only for app file inspection and read-only SQL in existing MariaDB. The image's code declarations may differ from installed-app metadata if patch state is behind, or the version field may be absent/empty; report safely without automatically installing apps or applying patches. Print only app names/versions or booleans and patch counts, **never** secrets, business data, private filenames or DB credentials. Avoid booting Frappe or trusting a general 'internal' network as sufficient to block external egress. Work only in NEW rehearsal; no OLD PRODUCTION, DEV or cutover.

## NEW REHEARSAL STAGE 12 OFFLINE IMAGE/SITE SAFETY PASS; APP METADATA FALLBACK REQUIRED — 2026-11-07

**PASS on the offline site/image safety and database object invariants; installed-app registry in restored DATABASE still pending verification.** Owner-run Stage 12 read-only diagnostic on NEW `ccpcadmin@ccpcerp-prod` returned:

```text
REHEARSAL_STAGE12_ISOLATION_VERIFIED
REHEARSAL_SITE_FILE_TREE_VERIFIED
REHEARSAL_SITE_KEY_AND_APP_DB_SECRET_MATCH_SOURCES
REHEARSAL_OFFLINE_SITE_SAFETY_FLAGS_VERIFIED
REHEARSAL_IMAGE_CODE_AND_SITE_APP_REGISTRY_MATCH
REHEARSAL_DATABASE_741_TABLES_6_SEQUENCES_UNCHANGED
REHEARSAL_DB_INSTALLED_APPS_METADATA_TABLE_ABSENT
REHEARSAL_STAGE12_READ_ONLY_COMPATIBILITY_DIAGNOSTIC_COMPLETE
```

**Verified meaning:** The NEW-only isolated three-container MariaDB+Redis set, internal bridge, four volumes and pinned `ccpcerp:v16.50.0` were checked. The ephemeral helper used no networking, a readonly `sites` volume, UID:GID1000 and no Linux capabilities; site and restored file tree/permissions passed. The **site config historical `encryption_key` digest** matched the protected 2026-11-05 backup, and its `db_password` matched the independently protected Stage 9 app secret. Both common and site settings used internal DB/Redis hosts, `maintenance_mode=1`, `disable_scheduler=1`, `pause_scheduler=1`, `mute_emails=1`, `developer_mode=0`. The image's installed directory and sites/apps.txt set match (including frappe, erpnext, ccpcerp). MariaDB still reports 741 BASE TABLE and six SEQUENCE objects. This is a **read-only structural/configuration PASS, not proof Frappe app or GL/stock behavior**.

**Important metadata interpretation:** The check looked specifically for a physical SQL table named `tabInstalled Applications` and found none. That does **not** by itself mean the apps are uninstalled. Frappe’s installed-app registration is maintained in a *global default* `installed_apps` (backed by `tabDefaultValue`), and the `Installed Applications` DocType is Single, with optional child rows in `tabInstalled Application` to track version metadata; `bench list-apps` can use global-default fallback. See upstream Frappe source and docs: https://github.com/frappe/frappe/blob/develop/frappe/installer.py ; https://github.com/frappe/frappe/blob/develop/frappe/apps.py ; https://docs.frappe.io/framework/user/en/bench/reference/list-apps . These upstream links are supporting reference, **not independently verified to match the exact pinned image code**. **Do not treat absent `tabInstalled Applications` SQL table as an app-compatibility failure** or create a table manually.

**Next bounded read-only Stage 13:** Check NEW Docker/local isolation and restored 741+6 object catalog; read the protected backup `db_name` without printing it. Query `tabDefaultValue` for `defkey='installed_apps'` (global parent `__global`) and parse stored JSON **in memory**. Print only entry counts and booleans for `frappe`, `erpnext`, `ccpcerp`; compare with a valid `tabInstalled Application` child-table app set if it exists, and inspect the Single DocType presence/issingle flag. Avoid printing raw `defvalue`, user/business rows, passwords, encryption keys, install-version data or app filenames. Do not mutate DB/site, run bench, start persistent backend/worker/scheduler/frontend, contact OLD PROD/DEV, or perform production cutover. If installed-app metadata incomplete, STOP for diagnosis rather than installing or migrating apps automatically.

## NEW REHEARSAL STAGE 11 PUBLIC/PRIVATE ARCHIVES RESTORED AND VERIFIED — 2026-11-07

**PASS — owner-run, corrected Stage 11 on NEW `ccpcadmin@ccpcerp-prod` under previously approved isolated historical restoration rehearsal.** Output reported:

```text
REHEARSAL_PUBLIC_ARCHIVE_VERIFIED
REHEARSAL_PRIVATE_ARCHIVE_VERIFIED
REHEARSAL_STAGE11_CORRECTED_PREFLIGHT_PASSED
REHEARSAL_SITE_TREE_PREFLIGHT_VERIFIED
REHEARSAL_PUBLIC_FILES_DIRECTORY_RESTORED
REHEARSAL_PRIVATE_FILE_RESTORED_AND_VERIFIED
REHEARSAL_ORIGINAL_SITE_CONFIG_UNCHANGED
REHEARSAL_NOV05_FILE_ARCHIVES_RESTORED_NO_APP_STARTED
```

**Verified restoration milestone:** Both untouched 2026-11-05 02:00 public and private archive inputs passed their pinned SHA-256 checks and exact `./ccpcerp.local/public/files`, `./ccpcerp.local/private/files` directory spelling checks. The source private archive's one direct file was validated with strict single-component filename, type, length, and checksum validation. A one-time, no-network, read-only-rootfs, UID/GID1000 non-capability helper mounted **only** the NEW rehearsal `sites` named volume and required the exact Stage 10 baseline site tree, proper Frappe UID/GID file modes, safety flags (maintenance, scheduler pause/disable, mute emails) and internal Docker DB/Redis addresses. The helper created `ccpcerp.local/public/files/` empty and `ccpcerp.local/private/files/` with exactly one private file using `O_EXCL|O_NOFOLLOW`, verified restored file digest, confirmed root and attachment directory tree and that site configuration, common config and `apps.txt` SHA-256 fingerprints were unchanged. The invoking script reverified only the three persistent isolated MariaDB/Redis containers, four named volumes and internal network with three attached containers after the one-shot helper exited. **No original backup changed, no SQL reimport, no permanent application/frontend/worker/scheduler container started and no OLD PRODUCTION/DEVELOPMENT operations.**

**Current complete historical data-layer rehearsal state:** SQL restored exactly 741 source BASE TABLE and six MariaDB SEQUENCE objects; essential DocType/User/Singles records inspected; independent application DB user verified; NEW-only site config retains historical `encryption_key`, independent app database secret, internal DB/Redis and off switches; public/private Nov 5 attachments restored and verified. This **does not yet confirm Frappe app code compatibility, DB migrations, decrypted secrets, data integrity/financial reconciliations or live production readiness**. Do not claim ERPNext application can be used before testing, and do not interpret the Nov 5 backup as a final cutoff snapshot.

**Recommended next bounded NEW-only read-only Stage 12:** Independently inspect app identities/metadata **from the pinned image** via an ephemeral `--network none --read-only --user 1000:1000 --cap-drop ALL --mount ...readonly` helper and compare with installed-app metadata stored in the restored database via *read-only SQL* on existing DB container; no SQL migration, `bench` execution, configurator, backend, workers, HTTP, mail or external integrations. Confirm existing guarded Docker scope, actual `sites/apps.txt`, original `site_config.json` safety flags without leaking password/key, app directories required frappe, erpnext, ccpcerp and image ID, and installed-app metadata/table availability. On mismatch STOP and inspect; no deletion or reimport. Only later consider a tightly constrained read-only Frappe site CLI verification on the isolated Docker bridge after independently reviewing outbound-egress/side-effect risks. Live cutover, current consistent backup, production rollback and approval remain separate steps.

## NEW REHEARSAL STAGE 11 SOURCE TAR LEADING DOT-SLASH CONFIRMED — 2026-11-07

**PASS — operator-run read-only RAW tar spelling diagnostic on NEW `ccpcadmin@ccpcerp-prod`.** Owner reported:

```text
PUBLIC_MEMBER_1_TYPE=DIR
PUBLIC_MEMBER_1_COMPONENTS_VALID=True
PUBLIC_MEMBER_1_RAW_CANONICAL=False
PUBLIC_MEMBER_1_LEADING_DOT_SLASH=True
PUBLIC_MEMBER_1_TRAILING_DOT=False
PUBLIC_MEMBER_1_DOUBLE_SLASH=False
PUBLIC_MEMBER_1_TRAILING_SLASH=False
PUBLIC_ARCHIVE_SAFE_COMPONENTS_VERIFIED
PRIVATE_MEMBER_1_TYPE=DIR
PRIVATE_MEMBER_1_COMPONENTS_VALID=True
PRIVATE_MEMBER_1_RAW_CANONICAL=False
PRIVATE_MEMBER_1_LEADING_DOT_SLASH=True
PRIVATE_MEMBER_1_TRAILING_DOT=False
PRIVATE_MEMBER_1_DOUBLE_SLASH=False
PRIVATE_MEMBER_1_TRAILING_SLASH=False
PRIVATE_MEMBER_2_TYPE=FILE
PRIVATE_MEMBER_2_COMPONENTS_VALID=True
PRIVATE_MEMBER_2_RAW_CANONICAL=False
PRIVATE_MEMBER_2_LEADING_DOT_SLASH=True
PRIVATE_MEMBER_2_TRAILING_DOT=False
PRIVATE_MEMBER_2_DOUBLE_SLASH=False
PRIVATE_MEMBER_2_TRAILING_SLASH=False
PRIVATE_ARCHIVE_SAFE_COMPONENTS_VERIFIED
REHEARSAL_TAR_SPELLING_DIAGNOSTIC_COMPLETE
```

**Root cause conclusively identified:** The public and private tar archives use the tar convention of prefixing each member path with a *leading* `./`, e.g. `./ccpcerp.local/public/files` and `./ccpcerp.local/private/files`, and one private direct file under `./ccpcerp.local/private/files/`. These are semantically valid components and were independently verified against original SHA-256, with no traversal, backslash, double slash, trailing dot or trailing slash. Stage 11's first preflight erroneously compared raw entry string to `ccpcerp.local/public/files` without the `./`, causing a **false-positive safety STOP before the helper ran or any files were written**. The prior Stage 10 site configuration remains intact; Stage 8 structural SQL and Stage 9 DB account also intact. **No need to reimport/restore database or regenerate credentials**.

**Recovery action within existing owner-approved NEW-only nonlive rehearsal:** Run a **corrected, strict** Stage 11 archive restore preflight that accepts exactly `./ccpcerp.local/public/files` as one directory and `./ccpcerp.local/private/files` as one directory plus exactly one direct regular private file `./ccpcerp.local/private/files/<sanitized single component>`. Recheck original backup SHA-256 and 0700/0600 file owner/modes; reject unsupported tar member type, link, device, unsafe names and overwrite. Recheck all NEW Docker container/image/network/volume labels, internal bridge, pinned exact custom Frappe image; start **only** a one-shot helper `--network none --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges --rm` with only rehearsal `sites` volume mounted. Require exactly the Stage 10 expected file tree `apps.txt`, `common_site_config.json`, `ccpcerp.local/site_config.json` and safety flags, verify file content fingerprints before/after and restore only empty public/private files directory trees plus one private file using exclusive, nofollow creation. Pass private payload via helper stdin (no host filenames, secrets or binary data in terminal). If partial failure, leave data intact and inspect; no blind rerun/deletion. No backend, configurator, frontend, WebSocket, workers, scheduler, mail, integrations, DEV/OLD PROD changes or cutover; backups remain historical Nov 5 rehearsal data, not final live cutoff.

## NEW REHEARSAL STAGE 11 TAR RAW DIRECTORY SPELLING STOP — 2026-11-07

**STOP before any writes — owner-run first attempt at Stage 11 archive restoration, NEW `ccpcadmin@ccpcerp-prod`.** Operator pasted:

```text
[sudo] password for ccpcadmin:
STOP: unexpected archive directory layout
```

This exception originated in the **host Python tar preflight**, before it printed `REHEARSAL_PUBLIC_ARCHIVE_HASH_AND_LAYOUT_VERIFIED` and **before launching the ephemeral Docker extraction helper**. Thus the command did **not** create `public/files` or `private/files`, did not restore the one private file, and did not mutate the completed site configuration/SQL database. The source tar was checksum checked before the exception. The test `member.name.rstrip("/") == "ccpcerp.local/public/files"` (or private variant) is **stricter** than the preceding successful Stage 7 safe `PurePosixPath(member.name).parts[:3] == ("ccpcerp.local", "public", "files")`. Tar member spellings that are semantically equivalent but not byte-for-byte identical, such as `./ccpcerp.local/public/files`, `ccpcerp.local/public/files/.`, or repeated slashes can satisfy the normalized parts test yet fail the exact string check. **The specific spelling is an unverified hypothesis pending inspection**, not yet determined. Do not rerun the failing Stage 11 script or relax type/path checks indiscriminately.

**Next safe read-only operator check:** Validate NEW hostname/user, `0700` backup directory and `0600` archive files, pinned SHA-256 of Nov 5 public/private archive; inspect the *exact original string spelling* of each tar member **without printing private names**, and compare normalized `PurePosixPath.parts` against the approved exact 3-part directory roots and 4-part direct private file path. Output booleans only: normalized root matches, exact raw root matches, optional leading dot slash, optional trailing dot, repeated slash, path component count, member file/dir type and count. Reject absolute/traversal/backslash/link/device members, and do not extract any files, start any containers or print secrets. If normalized shapes match the already-verified original member checks and no unsafe spelling, plan corrected Stage 11 that safely uses component-level validation, preserves original config, protects against overwrites and path traversal, and runs one no-network UID1000 helper only. The owner previously authorized NEW-only staged rehearsal; do not touch OLD PRODUCTION, DEVELOPMENT, live traffic or final cutover.

## NEW REHEARSAL STAGE 10 NONROOT SITE CONFIG RECOVERY VERIFIED — 2026-11-07

**PASS — operator-run Stage 10 recovery on NEW `ccpcadmin@ccpcerp-prod` after verified empty, UID1000/GID1000-owned sites volume.** User pasted:

```text
REHEARSAL_EMPTY_FRAPPE_OWNED_VOLUME_VERIFIED
REHEARSAL_SITE_RECOVERY_PREFLIGHT_PASSED
REHEARSAL_NONROOT_HELPER_VERIFIED
REHEARSAL_SITE_CONFIG_FILE_VERIFIED
REHEARSAL_COMMON_CONFIG_AND_APPS_VERIFIED
REHEARSAL_SITE_OWNERSHIP_AND_MODES_VERIFIED
NEW_REHEARSAL_SITE_CONFIG_PREPARED_NO_APP_STARTED
```

**Verified state:** Guarded script again confirmed NEW host `ccpcerp-prod`, account `ccpcadmin`, local default Docker socket, exact pinned `ccpcerp:v16.50.0` image, only existing three running isolated MariaDB/Redis containers, internal network and exactly four rehearsal-labeled volumes. The sites named volume was exactly empty and owned by Frappe UID:GID `1000:1000`, mode `0755`. A one-time temporary helper ran with `--network none --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges --rm`, mounted **only** `ccpc_restore_rehearsal_20261107_sites` with `volume-nocopy`, and prepared `ccpcerp.local/site_config.json`, `common_site_config.json`, and `apps.txt` as the Frappe user. It checked the new app-db password from private `site-db.env` differs from historical DB password and private root DB secret. It retained the original source-backup `encryption_key`, did **not** use historical DB password, and set `db_user=db_name`, `db_host=db`, `db_port=3306`, `db_type=mariadb`, `maintenance_mode=1`, `disable_scheduler=1`, `pause_scheduler=1`, `mute_emails=1`, `developer_mode=0`. Common Redis endpoints are isolated Docker service names. `apps.txt` was generated from actual local image app directories, checking frappe/erpnext/ccpcerp. Files' exact content, mode, UID/GID were verified **inside the helper without printing secrets**: site `site_config.json` mode 0600, common/apps 0640, owned by Frappe; site and sites dir 0750. Final invariant checks confirmed only three persistent containers, four named volumes and internal network three attachments. Recovery succeeded without deleting or rebuilding prior DB/Redis resources or rerunning any SQL import. **No ERPNext application service was launched; no file tar extracted yet.** The terminal showed a standard sudo password prompt for `ccpcadmin`; no password was pasted into chat.

**Next NEW-only stage within scoped owner approval:** Restore the two checksum-pinned historical Nov 5 file archive contents into the existing NEW-only sites volume with a tightly guarded `--network none` ephemeral helper as UID1000/GID1000. The public archive has exactly the sole directory `ccpcerp.local/public/files` and zero file entries; the private archive contains exactly `ccpcerp.local/private/files` plus one file beneath. Verify archive SHA-256 and member type/path shape before writes. No symlinks, hardlinks, absolute/traversal paths, links, device members, existing-file overwrite or use of `tar.extractall`; create only the expected `public/files`, `private/files` directories and one private file with `O_EXCL|O_NOFOLLOW` and Frappe UID 1000 permissions, preferably streaming data via Docker stdin to avoid bind-mounting private backup directories. Preserve already-created site config untouched; verify read-back file digest and unchanged site-config metadata (without exposing file contents). No app frontend/backend/configurator, schedulers, queue workers, integrations, employee access, backups from other dates, DNS or live cutover. Restore the historical backup only as a rehearsal. On failure preserve partial site volume and stop before rerunning.

## NEW REHEARSAL STAGE 10 READ-ONLY VOLUME STATE CONFIRMED EMPTY, OWNER FRAPPE — 2026-11-07

**PASS — owner-run READ-ONLY diagnosis after the Stage 10 ephemeral helper STOP.** Owner pasted:

```text
REHEARSAL_DOCKER_SCOPE_VERIFIED
SITES_VOLUME_ROOT=DIRECTORY|UID=1000|GID=1000|MODE=0755
SITES_ROOT_ENTRY_COUNT=0
SITES_UNEXPECTED_ROOT_ENTRY_COUNT=0
APPS_TXT=ABSENT
COMMON_SITE_CONFIG=ABSENT
SITE_DIRECTORY=ABSENT
REHEARSAL_SITE_VOLUME_READ_ONLY_DIAGNOSTIC_COMPLETE
```

The guarded inspection confirmed NEW `ccpcadmin@ccpcerp-prod`, default local Docker context, only the three existing rehearsal DB/Redis containers, internal three-attachment bridge and four named scoped volumes. It compared the named `ccpc_restore_rehearsal_20261107_sites` volume mountpoint to the actual Docker data-root's `volumes/<name>/_data`, rejected symlink/path mismatch, then inspected only lstat metadata and directory entry counts. The sites root is now **owned by 1000:1000 (Frappe account)** but still `0755`; **there are no files or subdirectories**. Therefore the helper stopped after ownership was changed but before creating `ccpcerp.local`, `apps.txt` or either JSON config. The strongest explanation is that the root helper, limited to `CAP_CHOWN`, could chown a root-owned volume to UID 1000 but could not subsequently `chmod` a directory it no longer owned without `CAP_FOWNER`; we did not capture its stderr so this remains a supported causal inference, not direct error trace.

**Next safe NEW-only bounded operation (existing phased rehearsal approval):** Recover without deleting/recreating/restarting anything by using a new one-shot `ccpcerp:v16.50.0` helper **as `1000:1000`**, not root; no Linux capabilities; `--network none`, `--read-only`, `--security-opt no-new-privileges`, exact `volume-nocopy` named rehearsal sites mount, `--rm`, pinned immutable image ID. First verify the volume is STILL exactly empty, owner `1000:1000`, mode `0755`, local Docker context, expected container/volume/network inventory; verify checksum-pinned `site_config_backup.json` and separate private `site-db.env` file, no secret output. The helper can then `chmod` the already-owned root to `0750`, create the site directory `ccpcerp.local` and two JSON config files plus `apps.txt` **as the Frappe user**, read back files and validate UID/GID/modes `site_config.json 0600`, common/apps `0640`. Preserve the historical `encryption_key`, but use only newly generated app DB password from `site-db.env`; force `disable_scheduler=1`, `pause_scheduler=1`, `maintenance_mode=1`, `mute_emails=1`, `developer_mode=0` and strictly internal DB/Redis hosts. Do not invoke any Frappe service, bench migrate, files tar extraction, HTTP/email, queue workers or frontend, and do not edit PRODUCTION/DEV. On partial creation failure, do not rerun, delete or overwrite—inspect volume metadata and contents again.

**Still not completed:** site config, attachment extraction, application validation, ERPNext accounting and inventory acceptance, any final cutover snapshot or production deployment. Stage 8 restored 741 BASE TABLE + 6 SEQUENCE, Stage 9 app DB account passed login; these remain preserved, not rerun.

## NEW REHEARSAL STAGE 10 SITE-VOLUME CONFIG HELPER PARTIAL FAILURE — 2026-11-07

**PARTIAL / STOP — owner-run Stage 10 attempted to prepare the NEW isolated rehearsal `sites` volume.** Operator output:

```text
REHEARSAL_SITE_PREPARATION_PREFLIGHT_OK
REHEARSAL_EMPTY_SITE_VOLUME_VERIFIED
STOP: site volume preparation incomplete; preserve contents and do not rerun
```

**Observed scope:** The extensive NEW-only preflight passed, and the temporary `ccpcerp:v16.50.0` helper, using `--network none --read-only --cap-drop ALL --cap-add CHOWN --security-opt no-new-privileges --rm`, verified that the rehearsal-only Docker named `sites` volume contained no files at helper entry. **None of the later markers** `REHEARSAL_SITE_CONFIG_FILE_VERIFIED`, `REHEARSAL_COMMON_CONFIG_AND_APPS_VERIFIED`, `REHEARSAL_SITE_FILE_MODES_AND_OWNERS_VERIFIED`, or `NEW_REHEARSAL_SITE_CONFIG_PREPARED_NO_APP_STARTED` appeared. The helper's stderr was discarded, so no exact failure reason was printed. The root-running helper used `os.chown(sites, frappe_uid, frappe_gid)` **then** `os.chmod(sites, 0750)` and attempted `os.mkdir(sites/ccpcerp.local)` after dropping all capabilities other than `CHOWN`. With neither `CAP_FOWNER` nor `CAP_DAC_OVERRIDE`, root may lack permission to chmod/mkdir the now-frappe-owned volume root: strong **hypothesis only**, not a confirmed trace. Some volume ownership/mode mutation may already have occurred and an unknown subset of site files may exist. The script deliberately fails closed and must **not** be rerun or followed by restore/extraction yet.

**Next safest step:** Read-only local Docker inventory and direct host-side inspect using `sudo -n stat`/Python `lstat` on the **exact Docker-confirmed mountpoint of `ccpc_restore_rehearsal_20261107_sites`**. First reverify expected NEW hostname/user and local Docker socket, exactly three existing rehearsal containers, internal network, expected four volumes and no foreign volumes. Before walking, confirm volume label project/volume/scope and the resolved mountpoint is actually beneath Docker's verified data root and matches a named volume `_data` path (not symlink); then report only ownership uid/gid, permission modes, file/dir/other counts, and presence/owner/mode of exactly allowed relative paths (`apps.txt`, `common_site_config.json`, `ccpcerp.local`, `ccpcerp.local/site_config.json`) without reading any secret JSON values. Do not start helper containers or perform writes for this diagnostic. On a nonstandard Docker root or unexpected structures, stop instead of guessing. Once partial state is known, repair with narrowly scoped operations, no deleting or overwriting existing private site files blindly. Leave SQL-restored database and Stage 9 app user intact; no backend/configurator/worker/scheduler/frontend or connections to OLD PROD/DEV, no cutover.

## NEW REHEARSAL STAGE 9 APPLICATION DB CREDENTIAL AND SCOPED USER VERIFIED — 2026-11-07

**PASS — owner-run Stage 9 NEW-only isolated application database user and secret.** Owner pasted:

```text
REHEARSAL_DATABASE_ISOLATION_REVERIFIED
REHEARSAL_APP_USER_PREFLIGHT_PASSED
REHEARSAL_NEW_APP_PASSWORD_STORED_PRIVATELY
REHEARSAL_APP_DATABASE_ACCOUNT_CREATED
REHEARSAL_APP_DATABASE_LOGIN_VERIFIED
REHEARSAL_APP_DATABASE_USER_READY
```

The guarded NEW-host script confirmed MariaDB/Redis three-container identity, single internal rehearsal bridge, exactly four scoped volumes, MariaDB healthy and the restored DB catalog unchanged at 741 BASE TABLE plus 6 SEQUENCE. It verified site-config backup SHA/permissions without revealing the historical `encryption_key` or old DB password. NEW-only `/home/ccpcadmin/.ccpc-rehearsal-secrets-20261107/site-db.env` (regular, owner ccpcadmin, 0600) contains a newly generated independent 64-hex password as `APP_DB_PASSWORD=<secret>`. The owner-run script checked there was no preexisting MariaDB user with the backup's `db_name`, then created exactly `'<db_name>'@'%'` and granted privileges scoped to `<db_name>.*`, not server/global scope. Its TCP login test to the newly created schema authenticated using the new password and counted 741 base tables. No credentials were printed or committed to GitHub. **Stage 9 complete**; DO NOT rerun.

**Next owner-approved isolated rehearsal Stage 10 proposal:** Prepare NEW Docker named `sites` volume with `ccpcerp.local/site_config.json`, `common_site_config.json` and `apps.txt` in a one-shot non-networked, nonprivileged helper container based on already-verified `ccpcerp:v16.50.0` image. The helper may need transient filesystem ownership changes inside the exclusive `sites` volume but no other volumes, DB writes or production paths. Verify empty target volume, exact image, local Docker context and three existing container labels/mounts; use `--network none`, `--read-only`, `--cap-drop ALL` except `CHOWN`, `--security-opt no-new-privileges`, `--pull never`, `volume-nocopy`, and `--rm`. Build site config in memory from checksum-pinned backup's `db_name` and historical `encryption_key` and new `site-db.env` credential, **do not** reuse original `db_password` or any external connection settings. Explicitly set `db_host=db`, `db_port=3306`, `db_type=mariadb`, `disable_scheduler=1`, `pause_scheduler=1`, `maintenance_mode=1`, `mute_emails=1`. Common config should use Redis network-local names, set off switches and no external endpoints; generate `apps.txt` from exact locally installed app directories (check frappe/erpnext/ccpcerp present). Verify ownership and restrictive permissions and exact read-back without printing secrets. Do not run configurator, backend, scheduler, workers, frontend, websocket, bench migrate or any restore command in this stage. On any partial error preserve volume contents, do not rerun without inventory. Later validate/restore the 2 pinned tar archives into this site under controlled extraction and inspect app compatibility before any app execution. Still no OLD PROD/DEV changes, final cutover or employee access.

## NEW REHEARSAL STAGE 8 SQL IMPORT FULL OBJECT CLASSIFICATION VERIFIED — 2026-11-07

**PASS — owner-run read-only Stage 8 post-import classification on NEW `ccpcadmin@ccpcerp-prod`.** Reported:

```text
REHEARSAL_ISOLATION_REVERIFIED
RESTORED_OBJECT_TYPE=BASE TABLE|741
RESTORED_OBJECT_TYPE=SEQUENCE|6
RESTORED_TOTAL_OBJECTS=747
BACKUP_CREATE_SEQUENCE_LINES=6
RESTORED_TABDOCTYPE_ROWS=814
RESTORED_TABUSER_ROWS=7
RESTORED_TABSINGLES_ROWS=1000
REHEARSAL_SIX_SEQUENCES_MATCH_BACKUP
REHEARSAL_DATABASE_OBJECT_DIAGNOSTIC_COMPLETE
```

**Confirmed outcome:** November 5 02:00 historical backup's 741 distinct `CREATE TABLE` statements yielded **exactly the corresponding 741 BASE TABLE objects**, with no missing or extra base tables (previous checkpoint), plus **exactly six MariaDB SEQUENCE objects**, matching six `CREATE SEQUENCE` source directives; hence the earlier hardcoded `information_schema.tables == 741` assertion was a false-positive because this catalog counts 747 objects including six sequences. Essential Frappe table record counts: `tabDocType=814`, `tabUser=7`, `tabSingles=1000`. Three NEW isolated MariaDB/Redis containers, no published host ports, network internal, preserved four volumes verified on NEW during the command. SQL imported **once**, MariaDB client returned success. DO NOT repeat the import, drop schema or restart services. This is a **structurally validated SQL restoration**; not yet tested app login, GL/stock/accounting integrity, encryption decryption, migrations or live operations.

**Next NEW-only owner-approved phased rehearsal step:** Generate an independent random *application* database password (`0600` under preexisting `0700` rehearsal-secret directory), then create only one `<backed_up_db_name>@%` MariaDB account with privileges scoped to the already restored single target schema (no global grants), avoiding historical `db_password`. Preserve the historical `encryption_key` only for later site config. Verify existing DB target and no conflicting DB account before writing. Use container-local MariaDB root auth from existing `MYSQL_ROOT_PASSWORD` environment, no root/app secrets in host argv, shell command line, output, Git or chat, and no `DROP`, `ALTER` of backup records or `GRANT ALL ON *.*`. On any partial failure preserve file/account and inspect without blind reruns. No Frappe/container startup, file archive extraction, mail, scheduler, background queue worker, integrations, DNS/cutover or OLD PRODUCTION/DEV changes. Historical backup remains only a rehearsal source.

## NEW REHEARSAL STAGE 8 ALL 741 SOURCE TABLES MATCH IMPORTED BASE TABLES — 2026-11-07

**PASS for base-table identity; supplementary database object classification PENDING.** Owner-run Stage 8 read-only diagnostic on NEW `ccpcadmin@ccpcerp-prod` reported:

```text
REHEARSAL_CONTAINERS_AND_NETWORK_REVERIFIED
RESTORED_DATABASE_OBJECTS=747
RESTORED_BASE_TABLES=741
RESTORED_VIEWS=0
BACKUP_CREATE_TABLE_STATEMENTS=741
BACKUP_DISTINCT_TABLE_NAMES=741
BACKUP_DUPLICATE_TABLE_DECLARATIONS=0
BACKUP_UNPARSED_CREATE_TABLE_LINES=0
TABLES_MISSING_FROM_RESTORE=0
TABLES_NOT_IN_BACKUP_DECLARATIONS=0
REQUIRED_FRAPPE_TABLES_PRESENT=True
BACKUP_AND_RESTORED_TABLE_NAMES_MATCH
REHEARSAL_READ_ONLY_IMPORT_DIAGNOSTIC_COMPLETE
```

**What this resolves:** The original Stage 8 hard stop was due to comparing the total `information_schema.tables` object count (747) against the source's **base-table** declaration count (741). In the new diagnostic, exactly all 741 distinct source `CREATE TABLE` identifiers match the exact 741 NEW `BASE TABLE` identifiers, with no missing or extra base tables, no source duplicates or unparsed declarations, and the `tabDocType`, `tabUser`, `tabSingles` structures present. No views were reported; the additional **six** table-catalog objects were **not yet classified** by the script and are not evidence of failed import. They might be MariaDB sequences but this must be checked from `information_schema.tables.table_type`, not assumed. The SQL client exited successfully in the first import and **must not be rerun**. We can treat base table import as structurally matching, not full Frappe/ERPNext functional validation or complete recovery.

**Next read-only single action:** On NEW only, guard hostname, account, local Docker context, exactly three pinned running rehearsal containers with internal network/no host-published ports, MariaDB healthy, and both checksum-pinned SQL/config input files. Using container-local MariaDB socket without exposing credentials, query `information_schema.tables` grouped by `table_type`, confirm 741 BASE TABLE and the six other entries' types, and query *counts only* for `tabDocType`, `tabUser`, `tabSingles` and optionally `tabCompany` (do not print records). For cross-check, count `CREATE SEQUENCE` source lines in gzip SQL archive if relevant and compare to catalog `SEQUENCE` count. Print only sanitized markers and counts. No DB writes, no import retry, no application services, file extraction, migration, email, integration, employees or cutover. Once verified, next authorized phased stage can prepare a new application database account/privileges and site configuration retaining historical encryption_key (but not historical DB password), then restore two pinned file archives safely. These steps have not occurred.

**Authoritative workflow:** GitHub-first; NEW-only isolated historical Nov 5 02:00 rehearsal after owner approval. OLD PRODUCTION and DEVELOPMENT unchanged; final production release/cutover requires separate approval.

## NEW REHEARSAL STAGE 8 SQL IMPORT FINISHED; TABLE COUNT VERIFICATION STOP — 2026-11-07

**PARTIAL PASS / STOP — operator-run NEW-only controlled MariaDB import, authorized by the owner-approved isolated rehearsal.** The owner pasted:

```text
REHEARSAL_TARGET_EMPTY_REVERIFIED
REHEARSAL_SQL_IMPORT_PREFLIGHT_PASSED
REHEARSAL_DATABASE_SCHEMA_CREATED
REHEARSAL_SQL_IMPORT_PROCESS_COMPLETE
STOP: unexpected imported table count; preserve database
```

**What is known:** Before the import, the NEW rehearsal MariaDB database server contained no non-system schema, the exact source SQL `20261105_020001-ccpcerp_local-database.sql.gz` and config hashes matched recorded originals, and the three MariaDB/Redis containers had vetted project/service labels and isolated network. The guarded script created exactly one new DB schema with the validated local backup site `db_name`, streamed compressed SQL to `mariadb` in the isolated DB container via its local Unix socket using the rehearsal root secret only in container environment, and the MariaDB client exited `0`. A post-import query then found the number of `information_schema.tables` entries **not equal** to the script's hardcoded expectation 741, stopping before checking the three required `tabDocType`, `tabUser`, `tabSingles` tables. The exact actual table count was not printed by this stage. 741 was taken from counting `CREATE TABLE`-prefixed lines in the SQL archive; this can overcount duplicate table declarations or differ from actual BASE TABLE plus VIEW catalog and is not independently proof of failed import. **Do not declare Stage 8 verified, attempt another import, drop the database, or alter data before diagnosis.** No site files, app user/permissions, public/private attachments, Frappe service, frontend, workers, scheduler or integrations were created/started by this step; OLD PRODUCTION and DEVELOPMENT untouched.

**Next operator-run read-only gate:** Verify current three NEW isolated rehearsal containers and healthy DB, backup SQL SHA-256 and site `db_name` without printing it; query `information_schema.tables` for exact actual count, BASE TABLE and VIEW totals, and the presence of critical Frappe tables. Independently parse source `CREATE TABLE` statements to count distinct table names, compare sets with actual catalog names locally, **print only counts and sanitized markers, never full table names or rows/credentials**. If the actual catalog matches the distinct backup table name set and essential Frappe tables exist, Stage 8 can be reclassified as a **false-positive expected-count check**; otherwise inspect differences further without destructive reruns. Maintain NEW-only isolated rehearsal and no app startup, restoration of attachments, schema migration or production cutover until verified.

## NEW REHEARSAL STAGE 7 ARCHIVE SITE ROOT CONFIRMED — 2026-11-07

**PASS — operator-run read-only tar site-root check on NEW `ccpcadmin@ccpcerp-prod`:**

```text
PUBLIC_ARCHIVE_SITE_ROOT_VERIFIED
PRIVATE_ARCHIVE_SITE_ROOT_VERIFIED
BOTH_ARCHIVES_MATCH_CCPERP_SITE
REHEARSAL_ARCHIVE_ROOT_PREFLIGHT_PASSED
```

The site-root diagnostic confirmed exact path-component equality to the selected rehearsal site `ccpcerp.local` for both checksum-pinned 2026-11-05 02:00 tar archives. Expected archive content structure is `ccpcerp.local/public/files/` (one directory only) and `ccpcerp.local/private/files/` (one directory, one direct private file). No absolute or traversal paths, symlinks or file writes; no database restore yet. The earlier Stage 7 `STOP: archive extraction layout needs review` was a too-narrow root allowance and is resolved. The archive source remains immutable; no need to move or re-transfer backups.

**NEW-only next Stage 8 within already approved phased isolated rehearsal:** Start isolated **database-only** import, leaving Frappe, frontend, configurator, WebSocket, workers and scheduler stopped. Because no Frappe site exists yet in the NEW `sites` volume, official `bench --site ccpcerp.local restore` is **not directly ready**; Frappe documentation describes Bench restore for an existing site with file archives (https://docs.frappe.io/framework/user/en/bench/reference/restore) and `bench new-site` bootstrap creates a database/user and initial framework tables (https://docs.frappe.io/framework/user/en/bench/reference/new-site). To avoid running an app bootstrap or supplying DB passwords as process CLI flags while only MariaDB/Redis exist, prefer a tightly guarded **single direct MariaDB import into a new EMPTY database** in the isolated NEW DB container; later build the Frappe site config with a **new, separate random app-DB credential** and the historical `encryption_key`, restore verified attachments safely, then validate site contents without starting employees/mail/queues/schedulers. This controlled import is **not a `bench restore` test** and must be documented as such, with schema/apps compatibility verification pending.

**Stage 8 command design constraints:** recheck NEW hostname/user/local Docker socket, exactly three vetted running rehearsal service containers and no published ports, isolated network and named volume inventory, MariaDB health, empty non-system database list, SQL + backup JSON SHA-256 and 0600/0700 protections, valid backup site `db_name` regex. Run root MariaDB through **container-local Unix socket** using `MYSQL_ROOT_PASSWORD` only inside the already-running isolated container and `MYSQL_PWD` there, never host argv/logs/chat. Issue `CREATE DATABASE` only for the valid destination backup DB name; stream **pinned** `database.sql.gz` directly into that one DB via `docker exec -i`. No host SQL file, shell password expansion, unfiltered table data, or external connections. Do not create users/grants, site files, app services or trigger migrations yet. Fail closed and preserve partial DB state for inspection on any failure: **never rerun blindly, drop/truncate or delete**. Report only markers and table count, not DB name. Once DB import succeeds, next stage prepares app DB user and Frappe config with the preserved encryption key. Final live cutover requires separate approval and fresh consistent backup; Nov 5 is rehearsal-only.

## NEW REHEARSAL STAGE 7 TAR ARCHIVE LAYOUT DIAGNOSED — 2026-11-07

**PASS — operator-run read-only sanitized tar diagnostic on NEW `ccpcadmin@ccpcerp-prod`.** The owner pasted:

```text
PUBLIC_ARCHIVE_SHA256_OK
PUBLIC_MEMBER_1=DIR|DEPTH=3|SHAPE=<redacted-directory>/public/files
PUBLIC_MEMBER_TOTAL=1
PRIVATE_ARCHIVE_SHA256_OK
PRIVATE_MEMBER_1=DIR|DEPTH=3|SHAPE=<redacted-directory>/private/files
PRIVATE_MEMBER_2=FILE|DEPTH=4|SHAPE=<redacted-directory>/private/files/<redacted-file>
PRIVATE_MEMBER_TOTAL=2
REHEARSAL_ARCHIVE_PATH_DIAGNOSTIC_COMPLETE
```

**Conclusion:** Both Nov 5 checksum-pinned file archives have a **single additional leading directory** relative to the overly narrow Stage 7 allowlist. The public archive contains just `<root>/public/files` directory (zero public files), while the private archive contains `<root>/private/files` directory and exactly one file beneath it. No symlink, hardlink, archive traversal/absolute path or other tar member type was detected by the guarded code. The root folder name was deliberately redacted and **has not yet been verified equal to** the site intended for NEW rehearsal. This layout is consistent with Frappe Cloud's documented backup tar structure, which puts the site name above `public/files` (https://docs.frappe.io/cloud/sites/migrate-an-existing-site). **No extraction, DB restore or app service startup occurred**.

**Next operator-run read-only gate:** Check whether the exact first path component in *both* checksum-verified original tar files equals expected site directory `ccpcerp.local` (known reviewed deployment site name), assert root equality across archives and exact member shapes/types/counts with no symlinks or traversal; print only booleans/markers, not private basenames or archive root on mismatch. Do not broaden extraction allowlist merely to accept unknown roots. If this passes, plan guarded Frappe-compatible attachment restore in the isolated `sites` volume, preserving the backup `encryption_key` without old database passwords, and selecting a safe database import method in a separate staged step. Current rehearsal DB/Redis are running on NEW isolated bridge only, no employee access, workers, scheduler or frontend; OLD PRODUCTION/DEVELOPMENT untouched. Snapshot remains 2026-11-05 02:00 rehearsal data only, not a reconciled cutover backup.

## NEW REHEARSAL STAGE 7 DB TARGET VERIFIED; ARCHIVE LAYOUT GATE STOP — 2026-11-07

**PARTIAL PASS / STOP — operator-run read-only Stage 7 on NEW `ccpcadmin@ccpcerp-prod`.** Owner pasted:

```text
REHEARSAL_TARGET_DATABASE_RUNNING
REHEARSAL_DATABASE_TARGET_EMPTY
BACKUP_DB_IDENTITY_FORMAT_VALID
BACKUP_ENCRYPTION_KEY_AVAILABLE
SQL_ELEVATED_DIRECTIVE_LINES=0
STOP: archive extraction layout needs review
```

**Meaning:** Guarded operator command found MariaDB healthy and target SQL catalog empty of non-system databases, valid portable backup site `db_name` identifier and available historical `encryption_key` (neither value printed), and zero *line-start* elevated SQL directives matching the limited precheck. It then rejected a public or private tar member path outside the initial narrow Frappe archive layout allowlist (which accepted only a root-level `files` tree or `public/files` / `private/files`). This could be a harmless parent directory member, different relative tar root, or genuinely nonstandard archive contents. Existing Stage 6 evidence already found one public directory and one private directory plus one private file, with no absolute/traversal paths, no link/other member types, and archive SHA-256 matches. **Cannot infer the precise archive layout without a further safe diagnostic.** The command stopped before any database DDL/import or archive extraction; NO business data was restored. NEW DB/Redis containers remain the last verified operational set; do not restart or rerun earlier writes.

**Next safe preparation step:** Read-only, SHA-256-pinned inspection of the two original tar archives on NEW. Print only the member's entry type, relative path component **classifications** (`files`, `public`, `private`, `.` or a fixed `<redacted>` placeholder), component depth, and archive member totals, not actual private file basenames, site config fields, records, or binary data. Recheck archive owner/mode and reject symlinks, hardlinks, absolute paths and `..` traversal. Diagnose the allowlist mismatch before selecting extraction path or a trusted Frappe `bench restore` route. This inspection does NOT approve relaxing path checks generally, and must not allow writing outside isolated NEW rehearsal site. No PRODUCTION/DEVELOPMENT changes or cutover.

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
