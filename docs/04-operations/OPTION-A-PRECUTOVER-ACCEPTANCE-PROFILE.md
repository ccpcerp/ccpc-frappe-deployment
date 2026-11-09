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
