# Option A — like-for-like NEW-host pre-cutover application acceptance profile

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
