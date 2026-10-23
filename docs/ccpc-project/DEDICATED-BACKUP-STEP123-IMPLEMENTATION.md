# Dedicated production backup — Step 123 GitHub-only implementation checkpoint

**2026-10-23; status: DRAFT CODE / OFFLINE TESTS ONLY. NOT INSTALLED OR APPROVED TO EXECUTE ON ANY ERPNext HOST.**

## Parent review context

This feature branch starts exactly from the unmerged dependent dedicated host security PR #29 (`security/dedicated-prod-external-env-2026-10-23` at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`), which itself is stacked on unmerged PR #27. It does **not** modify either parent review branch, the documentation handoff branch, running DEVELOPMENT, either production environment, Synology NAS, or /etc/fstab. The authoritative full design is on the separate documentation branch: [DEDICATED-PRODUCTION-BACKUP-RECOVERY-DESIGN-2026-10-23.md](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/docs/ccpc-checkpoint-2026-10-10/docs/ccpc-project/DEDICATED-PRODUCTION-BACKUP-RECOVERY-DESIGN-2026-10-23.md).

## Files and implemented boundaries

- `scripts/dedicated_backup_core.py`: **inert Python standard-library code**. It has NO production command entry point; executing the file directly terminates with a `NOT ENABLED` message. It does NOT run Frappe `bench`, mount/unmount CIFS, inspect Docker, delete old data, set retention, or create a cron/systemd job.
- `tests/test_dedicated_backup_core.py`: standard-library unittest regression suite using synthetic SQLite-free/GitHub-free samples. It uses a **mock** mount probe and disposable local scratch directories; no real NAS/auth, Docker or production data access is attempted.

Implemented reusable functions (to be integrated **only after separately approved DEVELOPMENT review**):
1. `inspect_artifacts` requires exactly four explicit **distinct** role-to-filename entries for `ccpcerp.local`: gzip-compressed SQL, site_config JSON, public files tar and private files tar; rejects wrong-site names, missing/empty, symlinked or multiply linked files, malformed contents, unsafe tar entries and wrong extensions. Gzip and tar are inspected without extraction.
2. `verify_cifs_mount` checks a real mountpoint and exact CIFS source `//192.168.50.132/ccpcerp-prod_backups` through `findmnt`, requiring `rw,nosuid,nodev,noexec`. A normal local directory, wrong share, ro mount, wrong type and unsafe flags are rejected.
3. `exclusive_lock` protects against competing jobs via nonblocking Linux `flock` and no-symlink file open. A future root-operated wrapper must verify the host, lock directory ownership/mode, runtime identity, exact site and immutable code/image, and the DB/file consistency procedure.
4. `publish_verified_set` accepts **only previously created, reviewed/consistent** four artifacts and a strictly shaped run ID. After mount verification it creates a unique mode-0700 `.partial-<run-id>` destination, copies four artifacts with O_EXCL, flushes each destination file, checks SHA-256 sizes/digests, writes a JSON manifest, validates copies again, performs Linux `renameat2(RENAME_NOREPLACE)` for fail-closed non-overwriting publication, and writes a `COMPLETED` marker last. It rechecks mount source between stages; it never deletes existing paths or partial results after failures.
5. **Known limitation**: Rechecking a mount is not a fully atomic defense against mount replacement/disconnect between system calls. A future integration wrapper must hold a verified mount/file descriptor and test network failure and CIFS rename semantics before any production usage. Linux local-filesystem `renameat2` success does not prove support by Synology CIFS. No NAS crash-durability guarantee is made.

## Test evidence

Offline test run **outside** CCPC hosts (disposable container, Python 3.13):

```text
PYTHONPATH=/mnt/data/step123 python -m unittest discover -s /mnt/data/step123/tests -p test_dedicated_backup_core.py -v

Ran 13 tests in 0.041s
OK
```

The 13 tests cover: successful four-artifact publication and manifest, incomplete/duplicate files and roles, invalid gzip/JSON/site, path traversal/symlinks, preexisting run/partial no clobber, mount probe pre-write refusal, interrupted transfer partial retention, checksum mismatch, concurrent lock rejection, unsafe run ID, Linux no-clobber atomic rename, wrong source/fstype/ro/flags/duplicate mount rows, and symlink lock refusal. `python -m compileall -q` also succeeded. The exact committed source and test blobs were compared against the offline-tested local files by Git blob SHA-1; the bytes match.

**Mocked tests do not establish actual Frappe/MariaDB v16 integration, consistency of concurrent DB/uploads, live NAS connectivity, CIFS `renameat2` support, restore success, backup age monitoring, encryption/key recovery, alerting or production readiness.** No pre-commit, GitHub Actions or real DB integration results are claimed.

## Known remaining work — not authorized in Step 123

- Bind to an actual reviewed **Frappe v16 bench backup --with-files** execution with exact source-run identification; verify current artifact names, backup permissions, concurrent DB/file consistency and live Docker/Compose profile/site/volume isolation before coding a root-operated wrapper. Do not use `bench --site all backup` as a substitute.
- Design and test the **root-only temporary mount lifecycle** and explicit backup run provenance, then exercise read/write integration on a **new share test namespace only with separate consent**. No persistent mounts; no writes to `erpnext_backups`.
- Test error behavior and **renameat2 support on SMB3.1.1/CIFS** without assuming the local offline test proves remote compatibility. Verify safe handling of orphaned final directories missing `COMPLETED` and failure to unmount.
- Add secure log/alert interface, idempotency rules for an interrupted run, backup retention **dry-run** and explicit owner-approved deletion policy. No automatic `.partial-*` removal or wildcard deletions.
- Plan isolated restore with four real artifacts, full app/data validation and measured RTO/RPO, protected secrets and external key recovery.
- Do not deliver/pull to DEVELOPMENT until Git working status and pending uncommitted work are verified; no new PRODUCTION host script installation, Docker start, cron/systemd timer, database migration, restore or production deployment without **new explicit approval**.

## Review instructions

Review this stacked feature branch against base `security/dedicated-prod-external-env-2026-10-23`. Run only the offline unittest suite; **do not execute the core against any live host**. Keep the PR draft until the above missing gates are separately resolved. GitHub-only completion is a **partial implementation milestone** (validated publication core), not a complete deployable backup system.
