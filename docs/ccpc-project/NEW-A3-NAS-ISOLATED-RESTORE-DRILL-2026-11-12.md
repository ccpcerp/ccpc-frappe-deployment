# NEW A3 — independent isolated Synology restore drill (2026-11-12)

**Status: OWNER APPROVED RESTORE-TEST SCOPE; STAGE 0 READ-ONLY PREFLIGHT PREPARED; NO RESTORE EXECUTED.** This dedicated review branch is stacked on deployment draft PR #33's owner-verified full NEW A3 backup. Nothing in GitHub has altered the running server.

## Authorization and safety boundary

Owner replied **"aPPROVED"** to the proposed independent test of the Nov12 Synology backup in a new, disposable environment. The authorized scope is to restore database, site config, public and private files to **NEW test-only Docker resources** with separate database/sites volumes, independent DB credentials, new internal-only network, no published ports, workers, scheduler, mail, webhooks or external integrations; verify ERPNext business records and attachments read-only. Preserve the six running `ccpc_prod_erpnext` candidate containers/volumes/network and the six Nov7 protected rehearsal containers/volumes/networks. Never modify OLD PROD or its shared DEV, router, Caddy/relay, source Nov05 backup, existing A3 backup or original NAS publication.

Unique proposed test namespace: `ccpc_a3_restore_drill_20261112`. New network `ccpc_a3_restore_drill_20261112_internal` MUST have Docker `internal:true` and no connections to the candidate or rehearsal networks. New DB/sites volumes use this namespace prefix. Do not use a generic Compose `up` or migration, and do not enable background services. No automatic retry or teardown/cleanup of test or existing data without separate reviewed authority.

## Source provenance

- Owner-verified backup run ID: **`20261112T090214Z-0148d36b2cb678b3`** (UTC). One-use capture script Git SHA256 `daa3f1d2ad906b0d3be1dc331bee9724d0d868ec386f3ab5fc13a7ee53f9101b`.
- Owner reported `CCPC_A3_GENERATOR_CAPTURE_PASS`, four individual local SHA256 passes, `CCPC_A3_FOUR_LOCAL_ARTIFACTS_PASS`, four NAS SHA256 passes, `CCPC_A3_NAS_FOUR_ARTIFACT_PUBLICATION_PASS`, `CCPC_A3_NAS_CLEAN_UNMOUNT_PASS`, and final `CCPC_NEW_A3_ONE_TIME_BACKUP_COMPLETE_RESTORE_TEST_PENDING`.
- Local run path from reviewed backup script: `/var/lib/ccpc-a3-one-time-backup/20261112T090214Z-0148d36b2cb678b3`, containing four artifacts and nonsecret `manifest.json`. NAS folder derived from script: `ccpc-new-a3-20261112T090214Z-0148d36b2cb678b3` under `//192.168.50.132/ccpcerp-prod_backups`; should contain four files, manifest, COMPLETED marker. These paths are script-derived, not yet independently re-read after NAS unmount.
- NEW A3 app image digest: `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`. Installed Frappe v16.33.1; root-only existing NAS credentials; encrypted backup feature disabled at creation. **Backup contains sensitive unencrypted site config/private business data**; never expose contents, passwords, company records, private attachment filenames, SQL or unredacted logs.

## Ordered recovery stages

**Stage 0 — next, read-only:** inspect exactly the four local manifest-named files by size and hash; verify manifest run/site/project/image IDs; inspect NEW Docker container, volume and network names to prove the requested test namespace is vacant; inspect local disk free. No mounts, file creation, container/service changes or backup output displayed. Run via an operator-reviewed root-only read-only command, with sanitized PASS/STOP markers.

**Stage 1 — later, independent NAS re-read:** temporarily mount only the exact dedicated Synology share `//192.168.50.132/ccpcerp-prod_backups` with **read-only** SMB 3.1.1 on a separate private, verified mountpoint. Enforce exact `findmnt` source, `cifs`, `ro` and source identity, no local fallback writes, no copying to existing backup directories. Check exact NAS run folder, COMPLETED marker, manifest agreement and all four NAS SHA256s. Copy to a **new root-only isolated local restore scratch**, verify again, cleanly unmount only drill-created mount. No NAS write or deletion.

**Stage 2 — later, isolated restore:** Create new dedicated `internal:true` network and new-only volumes after exact Docker diff/identity guards. Reuse pinned local Frappe/MariaDB image IDs, with no new pull/build. Generate independent test DB credentials locally (never GitHub/terminal output) and protect new-only site config. Import verified compressed SQL into only new empty DB and separately restore public/private files into only new test volume. Preserve backed-up encryption key as needed for historical record interpretation, without reusing live DB password. No worker/scheduler/migrations/notification or app internet connection. On any partial creation STOP and preserve for diagnosis; do not automatically replay or clean.

**Stage 3 — later, isolated Frappe acceptance:** Confirm only the test DB/Redis/app share the private network and zero published host ports. Read-only verify Frappe site, four company master records, Work Request/GL/inventory document counts where present, consistency of file references and public/private attachment availability. Do not invent positive ledger entries when the original data contains none.

**Stage 4 — evidence/handoff:** Distinguish checksum/manifest validation from actual MariaDB and application restoration. Record exact pass/fail, test duration, remaining gaps and verified GitHub commits. Retain test state pending separately approved cleanup; do not represent recovery as production-ready until successful isolated restore and remaining cutover gates.

## First operator step

Run a NEW-only read-only Stage 0 inspection of the stored local backup and target namespace (provided in the ChatGPT operator step). If any check STOP, do not create the test network/volumes or mount Synology; investigate source evidence instead. **The restore approval is already granted**; do not re-request it for steps within these exact boundaries.

## November 12, 2026 — OWNER_APPROVED_ISOLATED_RESTORE_PR34_STAGE0_READY

- Separate owner approval for the **independent isolated recovery test** recorded. Created draft deployment [PR #34](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/34) on `review/new-a3-isolated-restore-2026-11-12` stacked on backup PR #33. The plan is in this file, and read-only Stage0 audit source is `scripts/ccpc_new_a3_restore_stage0_readonly.py` at Git blob `6b6d04c80dfc7a4a33bab51b85864794ecdaa738` (commit `34fa261ac4cd6979ae2aeeae5e785645ff4e4f1f`).
- Stage0 source inspects exact preserved local run, manifest source identity, four unique correctly labelled artifact filenames, SHA256 and size, 12 protected running container names, absence of any resources under new test namespace prefix, and scratch disk headroom. It does **not** mount NAS, create any container/volume/network, write backup files, or restore DB. Source has been reviewed and committed to GitHub; **no runtime execution or local offline unit-test results recorded for this script**, so do not call it tested.
- For operator convenience, the assistant may first issue a shorter read-only one-shot inline inspection checking the existing run manifest hashes and test namespace collision without transferring the full Stage0 source. If so, document exactly which checks passed, and do not claim to have executed untransferred GitHub script. Stage1 NAS re-read and Stage2 new isolated restore remain separately unexecuted within approved scope.
- Do not overwrite/modify any existing A3 or the six Nov7 rehearsal containers, volumes/networks; no new namespace resources created yet. After operator Stage0 evidence, prepare Stage1 guarded **read-only NAS mount and independent scratch reread**, then Stage2 test-only restoration code. Preserve backup run and all secret-bearing site configs. No public endpoint, worker/scheduler/mail or cutover.
