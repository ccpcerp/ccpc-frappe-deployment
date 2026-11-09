# Option A — Fast-track like-for-like NEW production migration (2026-11-09)

**Status:** Owner explicitly selected **Option A**, the fastest safe migration of the existing OLD production ERPNext release to the dedicated NEW server, **with newer unfinished Withdrawal Slip/intercompany billing/day-one-report enhancements deferred**. This authorizes planning, GitHub review/documentation and read-only NEW-host checks; it is **not** standing approval to modify OLD production, restore/migrate databases, create production application services, switch DNS or open public access. Those need the final operator-reviewed scope and separate explicit cutover approval.

## Concrete known-good release boundary

- OLD production host: `ccpcerpserver`; NEW independent server: `ccpcerp-prod` (`ccpcadmin@192.168.50.186`). Keep OLD PRODUCTION **and** shared-host DEVELOPMENT untouched until individually authorized.
- Existing production image frozen across OLD/NEW: `ccpcerp:v16.50.0`, immutable `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`, created September 16, 2026. This is a byte-identical image observation, **not** an attested source Git SHA; revision OCI label absent.
- Supporting images pinned: MariaDB 11.8 `sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4`; Redis 8.6-alpine `sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763`.
- On NEW, six running support containers only: 3 in preserved original `ccpc_restore_rehearsal_20261107` and 3 in separately isolated `ccpc_full_acceptance_20261107` clone; no backend, frontend, websocket or workers/scheduler live. Neither namespace is an approved final production service or eligible for destructive reuse.
- November 5 four-artifact source backup transferred and verified; clone restored 741 base tables+6 sequences, 4 Companies and file attachment; H1B consistent local checkpoint protects clone. **H1B not off-host and not independently restored.** The November 5 dataset is historical and cannot be promoted to go-live data if OLD accepted writes afterward.
- Stage17U **actual adapted-site Company SQL/meta/ORM** SELECT-only PASS on historical restored DB. Stage17V-H2B required three DocTypes and stopped; independent H2C SQL and pinned-image file checks agree: Work Request present, Withdrawal Slip and Intercompany Material Billing Batch absent. **No evidence of corruption from that absence.** Work Request ORM, authenticated HTTP/session, stock/GL, attachments served, end-to-end restores, user permissions and final cutover remain pending.
- GitHub deployment candidate PR #27 (loopback-only pre-TLS Compose), #28 (HTTPS design only), #29 (external env/guard), #30 (advanced backup design) were still OPEN/DRAFT as of rechecked 2026-11-09. **Do not merge or launch these scripts wholesale:** current `deploy_release` uses full `compose up -d`, starts scheduler/workers, and runs migrations. This is inappropriate for a protected rehearsal or release without explicit stage-specific controls. Current generic Compose files also contain dangerous broad-port and unsafe-credential defaults unless the reviewed profile and protected env are precisely applied. An executable, accepted TLS gateway is not established.

## Shortest safe critical path — avoid extra historical H2 probes

1. **NEW operator preflight, read-only, one batch:** ensure Compose CLI supports `!override` (v2.24.4+), identify listeners on 80/443/8080 and whether an HTTPS gateway already exists, confirm local Docker context and exact namespace identity. Do not start or modify anything. Request output only from the NEW host. If ports are occupied, identify owner before planning binding; no kill, reconfigure or prune.
2. **NEW isolated application start acceptance using historical data:** develop/review a **separate locked-down maintenance acceptance profile** sourced from the pinned currently reviewed deployment stack, never the generic `deploy_release` routine. Keep existing baseline and acceptance clone names/volumes/networks unchanged; use a distinct candidate namespace only if host capacity and resource identity are reverified. For a first browser test, use an isolated non-public frontend via loopback/SSH tunnel; no 80/443 public/LAN binding until gateway, certificate and trusted access are verified. No schedulers, queues/workers, outbound email/webhooks, migrations, install-site or automatic new-site creation; `configurator` writes must be controlled and reviewed. FIRST full-write start must occur on a separately recoverable clone with the exact original image. Validate login/session, Work Request, access controls, Company, representative historical accounting/inventory documents (read-only), and allowed public/private attachment access, without creating live financial postings or external notifications. Record sanitized pass/fail.
3. **Recoverable fresh source capture and cutover rehearsal:** independently verify OLD current four-artifact **consistent** backup (DB, public files, private files, site config, correct encryption key) and restore it onto a designated NEW candidate, not a protected pre-existing rehearsal volume. Before any final cutover, demonstrate isolated restoration and verify DB/site/apps/files compatibility and rollback from an independently held backup. Full write-capable restore/production freeze needs an explicit scoped approval and owner-observed current OLD status. A newer fresh backup must supersede Nov5; do not call Nov5 current.
4. **LAN HTTPS and controlled cutover:** select validated cert/trust for office clients and a secure 443 gateway to loopback application frontend, keep DB/Redis non-public and management access restricted. Confirm login and permissions from an authorized office workstation. Plan a maintenance window; stop OLD writes only when explicitly approved; take final consistent backup, verify/import into NEW, smoke check and reconcile critical data, then explicitly approve DNS/employee access switch. **Never allow both OLD and NEW to accept production writes simultaneously.** Keep OLD recoverable, rollback decision tree and audit trail. Stop rather than blind restart/restore if any invariant or final smoke check fails.

## Stage A0 — NEW Compose and listener preflight PASS (owner report, 2026-11-09)

On `ccpcerp-prod` the owner ran `sudo docker compose version --short` and `sudo ss -ltn '( sport = :80 or sport = :443 or sport = :8080 )'`. Exact Compose output: `5.6.1`; `ss` produced only its header, with **no listeners on TCP ports 80, 443 or 8080 at check time**. Docker Compose version exceeds the documented v2.24.4 minimum for `!override`; actual candidate five-file Compose configuration has **not yet been rendered/accepted**. Open port availability does **not** prove firewall policy, trust/certificates, DNS, backend health or safe ability to start containers. No NEW or OLD service was changed through these read-only checks.

**Next single NEW-only operator batch (read-only, no secrets):** inspect existing container/volume/network names and free Docker filesystem capacity before selecting distinct `Option A` candidate namespace; compare specifically against proposed `ccpc_prod_erpnext` and preserved rehearsal projects. No `docker compose up`, deploy script, new site, image pull, migration or release action until namespace/source/config/invariants and approved rollback are independently verified.

```bash
sudo docker ps -a --format 'CONTAINER={{.Names}}' | sort
sudo docker volume ls --format 'VOLUME={{.Name}}' | sort
sudo docker network ls --format 'NETWORK={{.Name}}' | sort
df -h /var/lib/docker
```

## Stage A1 — NEW candidate namespace and capacity PASS; bounded pre-cutover review prepared (2026-11-09)

**Owner-reported read-only NEW inventory:**
- Exactly six containers (`ccpc_restore_rehearsal_20261107` and `ccpc_full_acceptance_20261107`, 3 DB/Redis each), eight expected project volumes, two distinct rehearsal project Docker networks plus Docker default bridge/host/none.
- **No** `ccpc_prod_erpnext` container, named volume or network present in the complete inventory reported at inspection; this is a non-collision observation, not authorization to deploy/create.
- `df -h /var/lib/docker`: root filesystem 787G, used 13G, **734G available**, 2% used. Avoid treating free disk capacity as proof that backup/restore has been validated.
- Earlier owner checks: Docker Compose 5.6.1; TCP 80/443/8080 had no listeners.

**GitHub-first engineering completed without host changes:** Created review-only branch `review/option-a-existing-release-precutover-2026-11-09` from exact original deployment review SHA `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e` and opened [DRAFT PR #32](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/32) to that review base (head `a57d8328f0a7e2f05d3378a10967101d1f4fe183`). This adds a sixth **pre-cutover acceptance-only** override `overrides/compose.option-a-precutover.yaml` and guarded operator document `docs/04-operations/OPTION-A-PRECUTOVER-ACCEPTANCE-PROFILE.md`. Overlay Git blob `38152038ea0de6d56b3b38ce9572785f95463d3a`, 2055 bytes, SHA-256 `bc283e1a48a314c0321f48f8636d30142f49edc2560ef24663efbe39408b5114`. Source-level PyYAML parse plus assertion verified 10 services, six acceptance-profile services, four separately excluded background/configurator services, disabled restarts/pulls, no frontend published port, declared internal default network. **Not yet validated by actual NEW Docker Compose six-file parser; not deployed.** Built direct matching downloadable file for owner transfer to private scratch, not into protected checkout.

**Next one NEW-only non-deploy action:** operator independently transfers the exact sixth YAML to NEW using previously established secure file-transfer workflow, checks its SHA256 against above and confirms private destination distinct from both earlier Git checkouts and original rehearsal overrides. Then one `docker compose ... config --quiet` with synthetic credential and a sanitized effective-model check; **no `up`, `run`, `start` or new persistent resource**. The preexisting five-file Compose parser/sanitized layout already passed on NEW November 7; do not rerun those unnecessarily. Releasing actual write-capable NEW app/start requires subsequent explicit scoped approval. OLD PRODUCTION/DEV, both NEW rehearsal databases/volumes and original H1B backup remain protected.

## Stage A1-file — NEW operator file-transfer SHA256 VERIFIED (2026-11-09)

Operator first verified the exact reviewed sixth overlay downloaded to Windows using `Get-FileHash`, then transferred it via existing production SSH key to `/home/ccpcadmin/.ccpc-compose-review-c12d46f/source-only/compose.option-a-precutover.yaml` on NEW. The NEW Ubuntu `sha256sum` returned `bc283e1a48a314c0321f48f8636d30142f49edc2560ef24663efbe39408b5114`, which matches previously reviewed GitHub blob `38152038ea0de6d56b3b38ce9572785f95463d3a`. **File transfer and checksum PASS only; no six-file actual Compose parser, app service startup, database operation, migration, backup/restore, TLS, OLD PROD/DEV or cutover is evidenced.** Next perform *one* sanitized synthetic six-file `docker compose config --format json` parser/guard (no service startup) from the existing private source-only directory. Never print the JSON environment containing the synthetic password. Then separately review whether guarded NEW-only runtime startup is authorized; do not use a generic deployment script.

## Stage A2 — owner-approved NEW isolated write-capable candidate; Nov 5 selected as final source (2026-11-09)

**New explicit owner authorization:** "Approved, and the Nov. 05, 2026 back-up still the latest and the approved back-up to be use, the live production is live but not being used anymore. and the waiting user rely on when this new production server gonna get live." This supersedes earlier **assumption** that a fresh backup is categorically required, while preserving the need for integrity/reconciliation. **Do not automatically demand a more recent backup**; use the four-owner-approved 2026-11-05 02:00:01 source artifacts already SHA-verified on NEW at `/home/ccpcadmin/.ccpc-nov05-backup-transfer-20261106/`. Their SHA-256s remain `8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87` (database), `200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6` (public), `60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf` (private), and `b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b` (site config). Existing independent Nov5 clone SQL/files restore was successful, with four Companies. No reason to transfer these same files again.

**Critical unchanged boundary:** "Live but not being used" is an operator assertion about human usage, not proof the OLD site's scheduler, integrations, database or filesystem stopped writing at exactly 2026-11-05 02:00:01 (especially later on Nov5). Before final cutover, require targeted evidence for post-backup transactional/master/config/attachment changes and automatic jobs; obtain separately scoped OLD write-freeze and final controlled switch approval. Do not ask for a new backup merely due to elapsed time. If post-backup writes are found, STOP to reconcile and obtain an owner decision; never silently discard records.

**Scope authorized now:** On NEW only, create an **independent** production-candidate namespace `ccpc_prod_erpnext` (distinct internal bridge and four new empty volumes) and initiate a controlled restore of a COPY of the approved Nov5 backup, new private credentials, database/Redis and pinned historical app services for authentication/Work Request/financial read-only acceptance. OLD live PROD and shared DEVELOPMENT, existing two protected NEW baseline/clone datasets, their H1B checkpoint, source backup originals and site/config secrets stay untouched. Start no scheduler/queue workers, automatic configurator, external-integrations, auto migrations, public port or user write access. Do not mistake A2 for authorization to **cut over** users, modify OLD, publish HTTPS/DNS or operate both systems as writers.

**Fastest actual next operation:** Create third candidate Docker namespace *foundation only* with strict identity/backup/image/inventory guards and guaranteed non-overwrite, then follow directly with protected NEW-only DB/Redis credentials and support startup, an isolated Nov5 SQL+file restore, and only then manual app/HTTP acceptance. Avoid repeating already passed A1/H2 tests. This is the first NEW persistent write under approved Stage A2, but creates only empty network and volumes (no DB/app yet). Stop on partial creation without blind retry/cleanup. The actual employee-facing go-live requires authenticated app test + backup reconciliation, recovery/rollback, trusted 443 LAN gateway and final cutover authorization.

## Current deliberately omitted scope## Stage A1 — CORRECTED SIX-FILE COMPOSE VALIDATION PASS — 2026-11-09

**OWNER-REPORTED NEW-ONLY REAL COMPOSE CONFIG PASS:** The operator reran only the corrected *synthetic*, no-start validator on `ccpcerp-prod`; no Compose `up`, app/DB start, secret use or other mutation. Exact sanitized markers:

```text
A1_TEN_SERVICES=PASS
A1_ACCEPTANCE_ONLY=PASS
A1_NO_DEFAULT_SERVICES=PASS
A1_PROFILE_SEPARATION=PASS
A1_NO_PUBLISHED_PORTS=PASS
A1_NO_RESTART_OR_PULL=PASS
A1_INTERNAL_NETWORK=PASS
A1_NAMED_VOLUMES=PASS
A1_NO_PRIVILEGED_OR_BIND_MOUNTS=PASS
OPTION_A_CORRECTED_VALIDATION_PASS
```

The previous synthetic STOP was caused by the *validator's assumptions about Compose inactive-profile filtering*, not evidence the sixth file was invalid. The default-profile model selects no services; enabling `ccpc-acceptance` in a **config-only** render reveals exactly six allowed app+DB/Redis services; `--profile "*"` **config-only** shows ten total definitions. The latter is NEVER an approved runtime `up` profile. The validated sixth file remains pinned to owner-confirmed NEW-side SHA256 `bc283e1a48a314c0321f48f8636d30142f49edc2560ef24663efbe39408b5114`, GitHub review [draft PR #32](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/32). This establishes only the synthetic effective Compose model; actual Docker network egress, site initialization, DB permissions, login/session, services, TLS, fresh-data restore and rollback are **not yet tested**.

**Immediate next decision is scoped Stage A2 NEW-only operational authorization, not another parser/preflight:** propose isolated **new `ccpc_prod_erpnext` candidate** separate from all six historical support containers and eight protected named volumes, with reviewed immutable image digests, separate protected credentials, independent historical **copy** of Nov5 archives, no workers/scheduler/configurator, mail/webhooks muted, `internal:true` networking, zero public ports and access only through a strictly reviewed local SSH test tunnel. A write-capable restored candidate/app login would create container/volume/database/session state, so require explicit owner approval of exact recoverable procedure **before** running it. Preserve OLD PROD/DEV and both existing NEW rehearsal environments. On successful authentic login plus read-only sample acceptance, advance to fresh current four-part backup, independently verified restore/rollback, LAN HTTPS and separately approved final write-freeze/cutover. A live system must never use the historical Nov5 data in place of a fresh current final capture.



- Do not make the newer draft finance/billing/Withdrawal Slip branches blockers for this **like-for-like migration**. Their production integration, reports, schemas, migrations, authorization and approvals are a **separate future release**, not hidden work added to the frozen historical image.
- Do not rerun successful Stage17U, 17V-H1B, H2A, H2B or H2C steps. H2B failure is explained at the expected-feature level; its precise first exception is unverified and historical Work Request ORM still needs a bounded production-like acceptance.
- Do not update arbitrary `version-16` Git heads, rebuild or pull newer images, change original baseline, erase clones, perform `bench migrate`, or expose full-write clone credentials in a generic app helper merely to hurry.
- Do not replace protected recovery with a same-host-only backup. Full production readiness still requires tested recovery, credential isolation and trustworthy LAN TLS.

## Next exact operator command (NEW host only, read-only)

```bash
sudo docker compose version --short
sudo ss -ltn '( sport = :80 or sport = :443 or sport = :8080 )'
```

**Why this command:** identifies whether current Compose can parse the dedicated `!override` profile and whether candidate loopback/HTTPS listener ports are already occupied. Does not inspect any secrets, change services or trigger pulls. Do not infer that an open listener is secure/healthy merely from `ss`. Return sanitized output.

## GitHub deployment work to prepare after preflight

- Verify exact source branch/commit for the existing dedicated env+Compose guards. Prefer an isolated **Option A release-candidate review branch** based on the latest reviewed deployment security selectors (not `main` and not automatically merged), and a small explicit stage-specific maintenance profile without workers/migrations/outbound side effects. Exact Docker Compose v2 render must be reviewed and tested on a trusted NEW shell before any `up`; do **not** use generic `deploy_release`.
- Reuse existing certificate/HTTPS design only after confirming actual gateway/cert implementation, office trust, UFW and DNS state. No invented certificate status or domain mapping.
- Design a bounded **one-time** NEW candidate start and rollback/restore operator runbook with exact namespace/volume/network/secret allowlists, pinned image IDs, and STOP behavior.
- Preserve original OLD PROD/DEV, NEW baseline+clone, protected H1B backups, and source archives throughout.

**Final go-live authority:** requires owner explicit approval of exact final backup/freeze/deploy/DNS action and verified recoverable rollback. This fast-track decision itself is not that approval.
