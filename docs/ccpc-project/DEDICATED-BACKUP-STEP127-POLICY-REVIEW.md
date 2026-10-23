# Step 127 — GitHub-only release/mount/consistency policy implementation

**2026-10-23. DRAFT / OFFLINE ONLY. No live Docker, bench, NAS, DEVELOPMENT or PRODUCTION activity authorized or performed.**

Owner expressly approved GitHub-only implementation and offline testing of the Step 126 identified three controls: reviewed release-manifest schema, fail-closed Docker mount layout (including image-declared `logs`), and consistency-evidence policy interface. This is not an authorization to merge PRs, build/release an image, pull code to DEVELOPMENT, touch a production server, suspend any service, execute backups, mount NAS, restore data, or enable jobs/retention.

## Current commits and scope

Stacked, OPEN/DRAFT PR [#30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30) remains based on PR #29, which is based on PR #27.

- `scripts/dedicated_backup_policy.py` — GitHub verified commit `11899f05c7ea7bf4e434a559306838f2e9ca12fc`, content Git blob `9de6d269dcb90ba70302795a7dbb8149ebf5a2b4`. An inert, importable standard-library Python module: no Docker interaction, file changes, bench access, service stop/start, NAS action, schedule, or runnable backup job.
- `tests/test_dedicated_backup_policy.py` — GitHub verified commit `106f6cf7ca20828c2ca407e7965aefec3bf41e2d`, content Git blob `adf9e0e53ca875317a0316d78aa5845e0db200d9`. New mock/synthetic tests for schema/approval-digest tampering, extra/secret-like fields, wrong release/source, anonymous/extra Docker mounts, quiescence time coverage, missing writers, backup-side-effect/filter/encryption claims, and never granting backup-ready status.
- Prior Step 123–125 production backup core, capture adapter, runtime inventory module and their tests were NOT modified by this step. Current Step 125 runtime verifier continues to require one backend mount and **does not consume this new mount policy**; safe integration with explicitly named logs volume is separate outstanding work. Keep `VerifiedIdentity.backup_ready == False`.

## Release manifest design, not a release

`validate_reviewed_release(raw, independently_approved_sha256=...)` requires byte-for-byte SHA-256 equality to a **digest provided independently of the manifest and Docker**. It rejects oversized/non-UTF-8/ambiguous JSON, duplicate/unknown fields, non-string values, wrong frozen FRAPPE/ERPNEXT/CCPC commits, patch/overlay hashes, host/site/profile and mutable/non-ID image tags. Required deployment commit, backend/DB image IDs and Compose configuration hashes must be complete and syntactically correct. Required volumes are **exactly** `<project>_sites`, `<project>_db-data` and `<project>_logs`.

Only **synthetic values** exist in the offline tests. No production release manifest, approval signature, observed container image ID, Compose hash or real digest was generated; no trusted signer/verifier has been implemented. A careless caller **could** hash its own untrusted data and pass it, which is explicitly prohibited by this contract. Manifest validation is not source/build provenance or authorization; `ValidatedRelease.trusted_runtime` and `backup_ready` remain **False**.

## Exact mount inventory policy (separate from runtime collection)

`verify_exact_mount_layout` accepts caller-provided *synthetic* inspected data and requires backend **exactly two** named RW volumes, sites at `/home/frappe/frappe-bench/sites` and approved logs at `/home/frappe/frappe-bench/logs`, and DB **exactly one** named RW volume at `/var/lib/mysql`. Volume names, mount paths and Compose labels must match exactly. Extra/anonymous/bind, missing/duplicate, wrong project or unexpected mount metadata **fail closed**; result still has `backup_ready=False`.

**Important integration gap:** Current image `VOLUME logs` without explicit Compose logs mapping can lead Docker to create an anonymous log volume. This policy **does not accept** it. A separate reviewed Compose change to provision the named `<project>_logs` volume, plus a trusted Docker inventory adapter using this exact policy, is required later. This step made **no Compose change** and does not relax the existing Step 125 checks. Host paths must still undergo additional independent canonical/symlink/permissions/race validation.

## Consistency evidence interface

`evaluate_quiescence_observation` checks the **shape and completeness of untrusted claims only**:
- Freeze begins before backup capture and ends after all artifacts, with correctly ordered timezone-aware UTC instants.
- Explicit writer groups `http, api, integrations, scheduler, queues, uploads, custom_jobs, direct_db` each claim no activity.
- No in-flight DB transactions, no changed-file TAR warning, and true booleans for backup cleanup side effects, full backup filters, encryption state, and safe abort/recovery policy.

This module **does not observe actual writers, block work, hold a freeze, inspect encryption, test backup cleanup, parse secrets, run Frappe, or produce a usable Step 124 capture attestation**. `ConsistencyAssessment.writes_quiesced=False` and `backup_ready=False` are intentionally fixed despite syntactically complete synthetic claims.

## Offline test evidence and critical qualification

A more extensive locally authored **prototype** of the same policy passed **20 offline standard-library unittest cases** (in a disposable environment, using no live services or data) and Python `compileall`; these tested the same categories of release, mount and quiescence policy checks. Source was subsequently **reauthored when uploading to GitHub**. The two GitHub files were each **fetched and byte-for-byte compared to the content submitted in their GitHub writes**, with verified blob IDs above, but **the exact committed GitHub revision and the newly committed GitHub test file have not been independently executed in a Python test runner**. GitHub combined status for latest commit returned **no statuses**. Do not claim “15/15” for the committed suite or “60+” full-suite success. Next independent offline action is an exact-GitHub-checkout test plus full regression; no host execution approval implied.

## Remaining gates and review priorities

1. Independently review the new module/tests on draft PR #30; obtain exact committed Python code through a safe test runner and verify offline tests and legacy regression suite. Tests here are mocks; no integration is demonstrated.
2. Independently approved immutable image build, real source provenance (current Containerfile lacks the expected Frappe source label), real Compose hashes and trusted approval signatures/digest distribution. No placeholder values or manifest copied from the same host it checks.
3. Explicit **named logs volume** in independently reviewed Compose and compatible guarded Step 125 runtime verifier; confirm the actual image mount layout in a separately approved isolated environment, not PROD.
4. Controlled, observable **DB/attachments consistency** policy and real verified freeze/abort behavior. Frappe v16.33.1 `delete_temp_backups()` can remove older files from its default backup directory, even if `--backup-path` is separate; do not run against existing business backups until independently tested in a disposable environment.
5. Safe Docker socket capability, Frappe backend path/mapping, snapshot/restore consistency, CIFS rename durability, backup alerting, secret/keys recovery, retention and unattended reliability all remain unimplemented, untested or unapproved.

**No operational backup readiness:** PR #27/#29/#30 stay draft/unmerged; DEVELOPMENT checkout/status remains uninspected in this step; separate dedicated `ccpcerp-prod` remains non-serving. Existing `ccpcerpserver` PROD/DEV and old NAS `erpnext_backups` were not touched by this Step 127.
