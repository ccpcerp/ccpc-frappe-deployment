# Step 124 — Frappe v16 capture wrapper and offline safety review

**2026-10-23 — GitHub-only draft feature / not executable on DEVELOPMENT or PRODUCTION.** This document supplements [Step 123's publication-core review](DEDICATED-BACKUP-STEP123-IMPLEMENTATION.md) and the [full design](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/docs/ccpc-checkpoint-2026-10-10/docs/ccpc-project/DEDICATED-PRODUCTION-BACKUP-RECOVERY-DESIGN-2026-10-23.md). The owner separately approved **PR #30 review and an offline-tested v16 backup execution wrapper**, not host installation, mounting NAS, running Frappe, migrating, deploying, enabling backups or scheduling.

## Source examination — actual pinned Frappe v16

Using connected GitHub read tools, reviewed `frappe/frappe` tag **`v16.33.1`**, the pinned release in `scripts/config.sh` (`FRAPPE_SHA=988e54f3c4c291e2077a83809663f123731abe76`):

- [Frappe site backup CLI](https://github.com/frappe/frappe/blob/v16.33.1/frappe/commands/site.py#L836-L925) declares `--backup-path`, `--with-files`, `--ignore-backup-conf` and optional `--compress`; passes those to `scheduled_backup`, requests `force=True`, and sets a nonzero exit code when a site's backup raises an error.
- [Frappe backup naming/format](https://github.com/frappe/frappe/blob/v16.33.1/frappe/utils/backups.py#L207-L225) uses one `YYYYMMDD_HHMMSS` prefix and a slugged site identifier for database `.sql.gz`, site configuration `.json`, public/private `.tar` (or compressed `.tgz` under `--compress`). Backup path is created if supplied. The backup code calls `delete_temp_backups()` before creating its backup; a future executor must check its actual effects and avoid modifying other users' preexisting backup files. Site-level encryption produces `-enc` filenames; the draft adapter **rejects encrypted output** until an encryption/key-recovery plan is separately reviewed.
- [Frappe backup configuration](https://github.com/frappe/frappe/blob/v16.33.1/frappe/utils/backups.py#L124-L148) can include or exclude DocTypes from the database backup. Therefore the wrapper requests `--ignore-backup-conf` and also requires a separately verified attestation that no partial filters or encryption apply.

**Important:** Upstream source review confirms options and naming in that pinned source, **not** the installed version, actual site configuration or a real successful v16 backup on the new server.

## Added files to draft PR #30

- `scripts/dedicated_backup_capture.py`: inert importable Python module, **not** an executable backup job. Requires caller-supplied `attest` and `runner` callbacks (neither provided or wired to Docker/bench). Attestation schema requires `ccpcerp-prod`, site `ccpcerp.local`, profile `dedicated-pre-tls`, pinned Frappe SHA, valid immutable image SHA-256, named `backend` and `db` services, preverified volumes, quiesced writes, full backup policy and encryption disabled. Refuses false, missing and truthy-string attestations. A real trusted attestor checking these facts still needs **separate implementation and approval**.
- Fixes executable argv to `bench --site ccpcerp.local backup --with-files --ignore-backup-conf --backup-path <dedicated-new-capture-directory>` (array of arguments; **never** shell constructed). The expected capture root must already be an absolute private 0700 executor-owned canonical directory outside the NAS mount path; no parent symlink and no preexisting capture-run directory. Unique 0700 staging directory uses fixed run ID syntax; preexisting content is never overwritten.
- On injected runner exit code zero, requires **exactly four** regular single-link filenames in the new directory, all with the **same** timestamp and exact `ccpcerp_local` name/suffix pattern. Calls Step 123 core's gzip, JSON, TAR and SHA-256 checks. Rejects extra/stale files, mixing backup generations, invalid formats, missing private/public files and symlinks. On any failure preserves incomplete local capture for explicit reconciliation; never chooses files from prior Frappe backup directories.
- `tests/test_dedicated_backup_capture.py`: **20 offline unittest cases** with injected fake runner and synthetic files; expected command, correct capture, wrong host/site/profile/release, wrong image/project/service/volume flags, truthy attestations, empty/unsafe/symlinked roots, duplicate capture, missing/extra/mixed timestamps, malformed gzip, symlinks, unsuccessful/throwing runner, unexpected non-integer status. Existing **13** Step 123 tests also remain.
- Direct script invocation exits with `NOT ENABLED`. No subprocess runner, CIFS mount/unmount, site migration, image action, environment credential source, NAS write, retention, cron or systemd timer is supplied.

## Offline verification and limits

Local disposable Python **3.13.5** container session, not CCPC DEVELOPMENT/PRODUCTION:

```text
PYTHONPATH=/mnt/data/step124 python -m unittest discover -s /mnt/data/step124/tests -p 'test_dedicated_backup_*.py' -q
Ran 33 tests
OK

python -m compileall -q /mnt/data/step124/scripts /mnt/data/step124/tests
# no errors
```

The exact local-tested source bytes were compared with GitHub fetch-file **blob hashes** after commit, confirming `scripts/dedicated_backup_capture.py` SHA `710eb63531a8521af62d708a8e12267f4d968a24` and `tests/test_dedicated_backup_capture.py` SHA `4453a7d237fcb6577e93b0c396d049e157b2f8fd`.

**No real Frappe/MariaDB integration tests, NAS remote publication, isolated restore, persistent DEVELOPMENT acceptance, CI, or production deployment have passed.** The entire runtime attestation is deliberately **only a caller-provided interface**; the actual trusted inventory adapter, service/container verification, site volume path mapping, backup size/resource limits, consistency quiescence and alternate encryption strategy are absent. A `True` attestation supplied by a careless future caller is **not evidence** of a real check.

## Review findings / unresolved safety and functionality gates

1. **Frappe capture not atomic with attachments:** a DB dump and files archive may reflect different transaction times unless an approved consistency/maintenance procedure is implemented and verified. No such procedure exists yet.
2. **Source immutability and runtime validation:** the wrapper verifies declared values, not the real Docker image digest, Git SHA, Compose project or site volumes. Runtime adapter must attest by independent calls using a restricted service identity and avoid the Docker-socket cron overlay.
3. **Source/destination boundary and TOCTOU:** root-path and symlink checks are not atomic against a malicious or compromised writer. A production adapter must pin trusted dirfds or enforce filesystem isolation and narrow permissions; identity checks must hold from capture through publication.
4. **Frappe internal behaviors:** `delete_temp_backups()`, possible partial backup rules, encryption flag and out-of-disk recovery must be exercised in disposable actual Frappe v16, not inferred from fake runner tests.
5. **Publication core limitations from PR #30:** `renameat2(RENAME_NOREPLACE)` support on actual SMB3.1.1/CIFS is unproven; failure after rename but before `COMPLETED` leaves a final directory that needs separate reconciliation; repeat `findmnt` checks cannot fully eliminate mount replacement races.
6. **Failure/security:** preserve incomplete backup captures and NAS partials without wildcard deletion; secrets must never appear in logs or exception tracebacks. Implement fixed audit statuses, redacted diagnostics, alerts and an off-host encrypted key recovery plan only after review.
7. **Retention and operational execution:** NO scheduling or deletion rules approved. The old host's 7/30-day policy is historical, not an adopted new-host policy. No live backup, restore drill or PRODUCTION changes authorized.

**Next gate:** Independent review of PR #30 and a separately approved, isolated DEVELOPMENT test plan that explicitly preserves local uncommitted work. Do **not** merge stacked PR #27/#29/#30, sync to either environment, mount NAS, start ERPNext, create cron or touch production database/backup records under this authorization.
