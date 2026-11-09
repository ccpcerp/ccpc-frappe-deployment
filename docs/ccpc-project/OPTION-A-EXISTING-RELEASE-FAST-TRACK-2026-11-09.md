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

## Current deliberately omitted scope

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
