# CCPC dedicated PRODUCTION — backup and recovery design (Step 122)

**Status:** DESIGN / REVIEW ONLY, 2026-10-23. **Not implemented, enabled, tested end-to-end, or approved for production operation.** This document applies exclusively to the **new dedicated** `ccpcerp-prod` host and new Synology `ccpcerp-prod_backups` share. It is not an instruction to change the active production/DEVELOPMENT host `ccpcerpserver` or old `erpnext_backups` share. Read this alongside [PRODUCTION-HOST-SETUP-HANDOFF.md](PRODUCTION-HOST-SETUP-HANDOFF.md), [recovery.md](recovery.md) and [GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md).

## 1. Verified source baseline and scope

### Verified / operator-reported as of Step 121

| Area | Actual evidence / limitation |
| --- | --- |
| GitHub deployment preparation | PR #27 `security/dedicated-production-pre-tls-2026-10-23` at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f` and stacked PR #29 `security/dedicated-prod-external-env-2026-10-23` at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`; both OPEN/DRAFT/UNMERGED at this review. New host checkouts were reported clean/pinned during Steps 119–121. |
| New NAS storage and account | `//192.168.50.132/ccpcerp-prod_backups`; account `ccpcerp_prod_backup` with DSM SMB Allow / ten other displayed applications Deny; user-only access to the intended share, explicit No Access to `docker` and legacy `erpnext_backups`. Some `homes` permission was displayed as Default and was not validated as explicit No Access. |
| New host credential / mountpoint | Root-only `/etc/ccpc-prod-nas/credentials` (0600), parent directory 0700; root-only `/mnt/ccpcerp-prod_backups` (0700), credentials outside Git. |
| Connection tests | Step 120 temporary SMB 3.1.1 read-only CIFS mount, verified source/type/ro, clean unmount; Step 121 temporary read/write CIFS mount, exact source/type/rw, uniquely created and read-back/flush test file, exact file and test directory removed, clean unmount. All are operator-provided PASS outputs, not persistent monitoring. |
| ERPNext application | The new dedicated host is **not running/live-serving ERPNext**. The reviewed Compose stack uses named `sites` and `db-data` volumes, with MariaDB and Redis overrides. Site name is configured as `ccpcerp.local` in `scripts/config.sh`, but runtime site existence must be checked after a separately approved deployment. |
| Old active production | [recovery.md](recovery.md) documents a manually verified four-artifact backup on **2026-09-02** on old `ccpcerpserver`; daily 02:00 Asia/Manila root cron was configured, but unattended successful execution was **pending** in that recorded checkpoint. Old retention was 7 days local and 30 days NAS. These are **legacy baselines, not new-host completed tests or automatically adopted new policy**. |

### Requirements that are NOT yet validated

A complete/recoverable four-artifact backup, a production workload under the new profile, automated scheduler, failure notification, external secret recovery, disaster restore, and isolation-tested NAS access are all **pending**. Successful mount/read/write smoke tests are not equivalent to an application backup or restore.

## 2. Explicitly excluded designs and execution boundaries

- **Do not adopt `overrides/compose.backup-cron.yaml` as-is.** On the inspected PR #29 branch it uses `mcuadros/ofelia:latest`, mounts `/var/run/docker.sock` even with `:ro`, and invokes `bench --site all backup` without the documented `--with-files` requirement or the host's four-artifact/mount/publication validation. Docker socket `:ro` does not make the Docker API read-only. The overlay is not included in this design or approved for deployment.
- Do not reuse `/usr/local/bin/erpnext_backup.sh`, root cron, credentials, mountpoint or NAS account from the old production host. The older script is documented by [recovery.md](recovery.md), **not** verified by fresh source inspection; it may provide design lessons but is not a drop-in new-host implementation.
- Do not treat the old environment's `compose.yaml.backup`, `.env`, database or files as safe inputs for the new system without independent review and migration approval. Never move secrets into checkout `.env`, GitHub, logs, arguments, or Docker image layers.
- No permissions to modify existing PROD, shared DEVELOPMENT, Synology old `erpnext_backups`, `docker`, any existing backup retention, `/etc/fstab`, live database contents, Docker containers, network settings or service schedules are conferred by Step 122 documentation approval.

## 3. Proposed architecture — fail closed

The new backup workflow should be independently implemented and reviewed in GitHub before delivery to a non-production test environment. Conceptual stages only:

1. **Acquire exclusive lock** (e.g., host-root run lock under `/run` with `flock`); reject concurrent invocations, stale ambiguous runs and duplicate scheduler paths. Record one immutable run ID and a limited state transition trail without secrets.
2. **Verify environment and source**. Require the dedicated host identity, expected released Git commit and Docker image digest, explicit Compose project/profile, expected Frappe site `ccpcerp.local`, running/healthy DB and app, correct sites and database volumes. Discover actual live container name and bench access method only **after** deployment verification. Reject missing/ambiguous sites or any fallback to another host/site. An operator-approved maintenance/cutover consistency policy must cover concurrent uploads, database writes, queues and restored attachment references. Frappe DB + filesystem backup is **not presumed atomic** merely because `bench backup` exits zero.
3. **Protect local scratch work**. Allocate a unique root-only local working directory on an approved local filesystem with bounded disk space; never put provisional data inside Git checkouts or a path whose parent could unintentionally become the NAS mountpoint. Avoid shell glob selection of an old backup set. Track the exact four artifacts created by the current run using a before/after manifest or the supported tool's explicit output; reject ambiguous names, stale results and partial writes. No uncontrolled cleanup of Frappe-managed backups.
4. **Create exactly one logical backup set** using a version-verified supported Frappe command (the legacy reference is `bench --site ccpcerp.local backup --with-files`; **confirm current v16 behavior in DEVELOPMENT**, including expected compressed SQL, site-config backup, public files archive and private files archive). Require all four nonempty, readable regular files with expected naming, bounded sizes and correct source site. Treat site-config JSON and archives as **sensitive**, as they may contain credentials, PII, business documents and private attachments.
5. **Integrity before copy**. Compute SHA-256 and byte size for each artifact, record UTC completion time, site identifier, Frappe/ERPNext/custom app version and immutable Git/image identifiers in a **non-secret manifest**. Restrict metadata exposure; the backup files themselves remain sensitive. Require nonzero lengths and archive/header/decompression checks compatible with actual file format, without extracting into production.
6. **Mount NAS only when needed** using a separately approved root-operated CIFS connector that uses the existing `/etc/ccpc-prod-nas/credentials`; prefer temporary mount over a persistently auto-recovering mount unless reliability testing justifies otherwise. Confirm existing mountpoint is absent, directory is not symlink, credentials ownership/mode, then CIFS `vers=3.1.1,sec=ntlmssp,rw,nosuid,nodev,noexec`. **Before any NAS write, and again before publish or retention, require** `findmnt` with the **exact** source `//192.168.50.132/ccpcerp-prod_backups`, filesystem `cifs`, VFS `rw`, and only one expected mount. If unavailable, **FAIL WITHOUT WRITING TO THE UNMOUNTED LOCAL PATH**. A path that exists is insufficient evidence. Stop on replacement/unmount, network error, or unexpected mount.
7. **Stage, verify, publish**. Under the verified new NAS mount create one uniquely allocated restricted `.partial-<run-id>` directory (must not pre-exist). Copy only the four files and manifest; sync/flush as appropriate; re-read from NAS and independently compare hashes and sizes against the local manifest. Optionally verify filesystem space and SMB fault behavior. Only after a complete match, rename the staging directory to an unused immutable final run directory **on the same share**; write a final completion marker containing no secrets last. A local rename on a CIFS share is an expected publication primitive, **not proof of power-loss durability**; cross-check published content/marker in an independent later run.
8. **Success criteria**. Treat a run as successful only if source backup completed, all four source artifacts verified, destination hash check passed, completed marker and final directory were observed, no unexpected writes/errors occurred, and the mount was cleanly unmounted or its safe residual state was reported. Alerts must indicate *failure or unknown* rather than print a misleading success on copy-only completion. If unmount fails, do not proceed to a new run or conceal active mount.
9. **Failure handling**. Keep identifiable, bounded failed local/NAS partials for a **separately approved** reconciliation/cleanup policy; never generic `rm -rf`, wildcard deletion, or unmount of a pre-existing shared filesystem. No automatic retries of uncertain success that could produce duplicate run IDs or duplicate publishes. Use deterministic run IDs with exclusive allocation and an audit trail; failure and recovery procedures must be tested for power loss, low space, interrupted transfer, wrong credentials, and network outage.

### Proposed new NAS layout — not created

```text
//192.168.50.132/ccpcerp-prod_backups/
  .partial-<unique-run-id>/       # incomplete, never counted as a backup
  <unique-run-id>/                # final, published only when validated
    database.sql.gz               # actual Frappe-generated filename may differ
    site_config_backup.json
    files.tar                     # example artifact types only
    private-files.tar
    manifest.sha256
    COMPLETED                     # final marker; implementation to define format
```

This is illustrative, **not** a claim that Frappe will output these exact filenames. Preserve real filenames in the manifest; avoid renaming in ways that break supported restore tooling. A valid final set must have exactly the four tracked Frappe artifacts **plus** approved metadata/marker; extra unexpected files must be investigated.

## 4. Retention, confidentiality and recoverability controls

**Proposed baseline for owner decision, NOT a live deletion rule:** assess whether to carry forward the old policy (seven days local; 30 days NAS). Determine number of restore points and time/space requirements, longer month-end/year-end holds, audit/legal retention and offsite resilience before adoption. Never implement retention until one complete and independently verified backup set exists **and** a successful isolated restore has been demonstrated; even then require explicit operational approval.

- Retention must only ever evaluate **completed, manifest-verified directories** created by the new backup job on the **new** share; never delete `.partial-*` automatically without reconciliation, unknown paths, Synology `#recycle`, older NAS share data or files beyond an exact prefix. Guard the root mount source/identity before every proposed deletion; perform a full dry-run report first and require a separate owner approval for the initial destructive policy.
- Protect private backup contents with strict SMB/NAS ACLs, restricted local scratch and temporary paths, audit-only non-secret logs. Verify NAS snapshot/immutable or offsite protections **if available and separately approved**; ordinary write-enabled CIFS credentials alone do not protect backups from ransomware or compromised root.
- Document separate encrypted/offline recovery for **dedicated deployment environment file**, encryption keys, MariaDB and Frappe secrets, NAS credentials, application image/source and host recovery instructions. Keep decryption keys independent of the copies they protect; never check plaintext credentials into GitHub. The staged `credentials` file is currently on the new host only.
- Design capacity and health alerts for source backup age, timeouts, nonzero exit, hash mismatch, permission/mount errors, partial directories, less-than-required free space, unexpected existing run directories and missed scheduler executions. Alert on absence of a new valid marker rather than only job exit code. Avoid sensitive log contents.

## 5. Independent isolated restore drill (before release readiness)

This is a separately approved future test **only in a controlled disposable non-production environment with confirmed isolation**. Do not assume ordinary DEVELOPMENT is physically isolated from production; it may share NAS/network infrastructure and contains independent work to preserve.

1. Authorize a target with its own database and sites volumes, credentials, network identity and immutable image/application revision. Prohibit connections to production DB or use of production site identity on a shared network until isolation is verified.
2. Select a completed NAS run ID and verify manifest, all four files, hashes, format, timestamp and exact source. Copy a test set to private local scratch using a **read-only** verified mount. Never restore directly from a mutable NAS path.
3. Create a pre-test snapshot of the isolated target. Restore the database and public/private files with the **version-specific supported** Frappe procedures; reconcile site configuration secrets without reusing live credentials or exposing the recovered site externally. Migrations need independent approval if they change schema.
4. Verify restored Frappe recognizes the site, representative general ledger/inventory and other ERPNext documents are present and internally consistent, attachments resolve with authorized private/public access, and intended applications load. Check referential consistency across DB records and attachment files; capture sanitized test evidence and measured RTO/RPO (not a guarantee).
5. Teardown/sanitize isolated test data only under reviewed retention and approval; record test verdict and any reproducible failures. A `gzip -t` or hash PASS **alone does not constitute a restore drill**.

## 6. Validation plan for a future implementation (not run)

| Layer | Required evidence before scheduling |
| --- | --- |
| Offline script tests | Lint/syntax; mocked fake CIFS/mount/rename/file failure; wrong host/site, missing mount, wrong source, ro mount, symlinks, empty/duplicate artifacts, hash mismatch, partial transfer, disk full, concurrent run, timezone/run-ID collision, cleanup safety; show `PASS/FAIL` and no leaked credentials. Mocked tests **do not prove MariaDB/Frappe behavior**. |
| DEVELOPMENT functional test | An explicitly approved disposable actual Frappe v16 site, real MariaDB and files; execute backup, verify all four, hashes and published result. Preserve all existing DEVELOPMENT work and data; do not import production data without separate privacy/isolation approval. |
| NAS integration | Bound to **new dedicated share** with reviewed test namespace only: mount guards, failure injection, clean unmount and partial reconciliation. Step 121's one-file smoke test is **not** a substitute. |
| Restore drill | Independently approved isolated DB/files restoration with application/attachment/business-record verification. |
| Operations | Separately approve owner, runtime identity, scheduler mechanism, run window, one-job concurrency control, alert transport, retention policy, recovery secrets/escrow, off-host retention and rollback plan. Observe a manually approved complete run and then one unattended run before claiming scheduler reliability. |

## 7. Required approvals / gates

| Gate | Current status |
| --- | --- |
| Synology account, dedicated root-only credentials and temporary SMB read/write smoke test | **Passed by operator status, Steps 118–121** |
| Step 122: GitHub read-only review and written design | **Authorized; this document records the design, no runtime action** |
| Write actual backup scripts or Compose changes on a separately reviewed GitHub development branch | **NOT authorized by Step 122** |
| Deliver or run scripts on DEVELOPMENT | **Not authorized; protect uncommitted DEV work** |
| Deploy/launch ERPNext on new PRODUCTION host, migrate data, restore or start containers | **Not authorized** |
| Persist NAS mount or modify `/etc/fstab`; create cron/systemd timer; enable production backup runs | **Not authorized** |
| Delete data / activate retention; run actual isolated restore with business data | **Not authorized** |

**Next recommended decision:** review this design with the owner; seek separate approval to implement a *non-executing, testable* backup module on a dedicated GitHub feature branch, with a reviewable test plan. No runtime or production action follows from this document.

## 8. GitHub sources reviewed

- [Authoritative legacy recovery guide](recovery.md) — the four mandatory artifacts, old-host 2026-09-02 manual backup, 7/30-day old retention, mount fallback incident, restore and approval rules.
- [Dedicated production host checkpoint](PRODUCTION-HOST-SETUP-HANDOFF.md) — exact new NAS account/share/mount paths and Step 119–121 owner-supplied test results.
- [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) — review code, branch, test, deliver through DEVELOPMENT before separate PROD approval.
- PR #27 and stacked PR #29; specifically reviewed `compose.yaml`, `overrides/compose.mariadb.yaml`, `overrides/compose.dedicated-pre-tls.yaml`, `overrides/compose.backup-cron.yaml`, `scripts/config.sh`, `scripts/modules/env.sh` and `scripts/modules/docker.sh`. The optional `compose.backup-cron.yaml` is **not** part of the approved new-host path.
