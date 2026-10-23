# CCPC ERP Recovery Guide

*Legacy backup/recovery procedures last verified: 2026-09-02. New-host design cross-reference added: 2026-10-23.*

## Dedicated new-host backup design — 2026-10-23

**Separate future system, not a change to the active legacy backup workflow.** For the new `ccpcerp-prod` host and Synology `//192.168.50.132/ccpcerp-prod_backups` share, use [DEDICATED-PRODUCTION-BACKUP-RECOVERY-DESIGN-2026-10-23.md](DEDICATED-PRODUCTION-BACKUP-RECOVERY-DESIGN-2026-10-23.md) as the **Step 122 design proposal** and [PRODUCTION-HOST-SETUP-HANDOFF.md](PRODUCTION-HOST-SETUP-HANDOFF.md) for current verified status and approvals.

The new host has passed temporary read-only and read/write CIFS smoke tests (Steps 120–121), **not** a complete four-artifact Frappe backup or restore. No new-host backup code, retention job, scheduler, persistent mount, site restore, application migration or production deployment is authorized/enabled by that design. The legacy `ccpcerpserver` / `erpnext_backups` procedures and retention described below remain independent, with their historic verification limitations preserved.

## Purpose

This document defines the recovery and backup procedures for the CCPC
ERP production environment.

It covers:

-   Complete server loss
-   Disk or operating-system failure
-   Docker configuration loss
-   ERPNext application recovery
-   MariaDB database recovery
-   Public and private file recovery
-   Synology NAS backup recovery
-   Backup validation
-   Deployment-framework recovery

The objective is to restore the environment safely, consistently, and
from verified recovery assets.

## Recovery principles

Recovery work should follow these principles:

-   Preserve existing recovery assets before making destructive changes.
-   Verify backup files before relying on them.
-   Restore configuration and application state before restoring
    business data.
-   Treat database restoration and migration as deliberate production
    operations.
-   Do not expose credentials, passwords, SSH private keys, NAS
    credentials, tokens, or recovery codes in documentation or
    troubleshooting output.
-   Do not assume that a backup is valid solely because a scheduled job
    reported success.
-   Prefer tested, reversible recovery steps.
-   Require explicit approval before destructive cleanup, database
    restoration, production deployment, rollback, migration, or
    container recreation.

## Recovery priorities

For a complete environment recovery, use this order:

1.  Restore the operating system and host networking.
2.  Restore the CCPC deployment framework.
3.  Restore Docker and Compose configuration.
4.  Restore required secrets and environment configuration from secure
    sources.
5.  Restore or rebuild the ERPNext application image.
6.  Restore the ERPNext database.
7.  Restore public files.
8.  Restore private files.
9.  Run required application/database migration only when explicitly
    approved.
10. Verify ERPNext operation and data integrity.
11. Verify backup scheduling and NAS access.

## Recovery assets

### Operating system

-   Ubuntu Server
-   Host network configuration
-   DNS configuration
-   Required filesystem mounts
-   Docker runtime

### Deployment framework

Primary repository:

`ccpcerp/ccpc-frappe-deployment`

Important assets include:

-   Compose configuration
-   CCPC Compose overrides
-   Build scripts
-   Deployment scripts
-   Rollback scripts
-   Operational modules
-   Framework documentation

The upstream `frappe/frappe_docker` remote should remain available as
the upstream source.

### ERPNext application

Primary custom application repository:

`ccpcerp/ccpcerp`

Expected application branch:

`version-16`

Internal Frappe site name:

`ccpcerp.local`

### ERPNext business data

A complete application-data backup requires all four Frappe backup
artifacts:

-   Compressed MariaDB database backup
-   Site configuration backup
-   Public files archive
-   Private files archive

A timestamped NAS backup directory should not be treated as complete
unless all four expected artifacts exist and are non-empty.

### Configuration and credentials

Recovery may also require:

-   `.env`
-   Secure environment/configuration backups
-   GitHub credentials
-   Docker credentials where applicable
-   ERPNext Administrator credentials
-   MariaDB credentials
-   SSH keys
-   Synology NAS credentials

Secrets must remain in their approved secure locations and must not be
committed to Git or copied into this document.

## Recovery locations

  ----------------------------------------------------------------------------------------
  Asset             Primary Location                   Recovery / Backup Current Status
                                                       Location          
  ----------------- ---------------------------------- ----------------- -----------------
  Deployment        GitHub                             ERP server        Active
  framework         `ccpcerp/ccpc-frappe-deployment`   working copy      

  ERPNext custom    GitHub `ccpcerp/ccpcerp`           ERP server        Active
  application                                          working copy      

  Docker            ERP server / Git repository        Git repository    Active
  configuration                                                          

  Docker images     Local Docker                       Rebuild from      Active
                                                       source            

  MariaDB database  Production ERPNext environment     Synology NAS      Backup workflow
                                                                         manually verified
                                                                         2026-09-02

  Public files      Production ERPNext environment     Synology NAS      Backup workflow
                                                                         manually verified
                                                                         2026-09-02

  Private files     Production ERPNext environment     Synology NAS      Backup workflow
                                                                         manually verified
                                                                         2026-09-02

  Site              Production ERPNext environment     Synology NAS      Backup workflow
  configuration                                                          manually verified
  backup                                                                 2026-09-02

  Environment       ERP server                         Approved secure   Verify separately
  configuration                                        backup            

  SSH keys          Administrator workstation          Approved secure   Verify separately
                                                       backup            

  Documentation     GitHub repository                  ERP server /      Active
                                                       Project Source    
  ----------------------------------------------------------------------------------------

## Synology NAS backup storage

The production backup share is mounted at:

`/mnt/erpnext_backups`

Expected filesystem type:

`cifs`

Expected CIFS source:

`//192.168.50.132/erpnext_backups`

The NAS address was corrected on 2026-09-02 after the network migration
made the former subnet address obsolete.

The host `/etc/fstab` entry uses a root-owned credentials file. The
credential contents must never be printed or copied into project
documentation.

Before a NAS backup or recovery operation, verify that:

-   `/mnt/erpnext_backups` is an actual mountpoint.
-   Its filesystem type is `cifs`.
-   Its source is exactly `//192.168.50.132/erpnext_backups`.
-   The mounted share is readable and writable as required.

A directory existing at `/mnt/erpnext_backups` is not sufficient proof
that the NAS is mounted.

## Production backup workflow

The active host backup script is:

`/usr/local/bin/erpnext_backup.sh`

A pre-hardening safety copy is retained at:

`/usr/local/bin/erpnext_backup.sh.backup-2026-09-02`

The hardened workflow performs these operations:

1.  Create a Frappe backup locally using
    `bench --site ccpcerp.local backup --with-files`.
2.  Identify the newly created backup set.
3.  Require the database, site configuration, public files, and private
    files artifacts to exist and be non-empty.
4.  Apply local Frappe backup retention.
5.  Verify the NAS mountpoint.
6.  Verify the filesystem is CIFS.
7.  Verify the exact expected NAS source.
8.  Verify the NAS is writable.
9.  Copy the complete backup set to a temporary `.partial-*` NAS
    directory.
10. Verify each copied artifact is non-empty.
11. Atomically rename the temporary directory to its final timestamped
    directory.
12. Apply NAS retention only to directories matching the backup
    timestamp naming convention.
13. Report success only after the full workflow completes.

This design prevents a missing NAS mount from silently turning
`/mnt/erpnext_backups` into a local-NVMe backup destination.

## Backup retention

Current retention policy:

-   Local Frappe backup files: **7 days**
-   NAS timestamped backup directories: **30 days**

NAS retention is deliberately restricted to timestamp-formatted backup
directories. It must not broadly delete arbitrary NAS directories such
as Synology's `#recycle`.

Changes to retention or manual deletion of backups are destructive
operations and require explicit approval.

## Backup scheduling

The production backup is scheduled in **root's crontab**:

`0 2 * * * /usr/local/bin/erpnext_backup.sh >> /var/log/erpnext_backup.log 2>&1`

Server timezone:

`Asia/Manila`

The scheduled backup therefore runs daily at:

**02:00 Asia/Manila (UTC+8)**

The server may display the timezone abbreviation `PST`; in this
environment that means Philippine Standard Time, not US Pacific Standard
Time.

A duplicate backup schedule previously present in user `gani`'s crontab
was removed on 2026-09-02. Root's crontab is intended to be the sole
scheduler for this backup job.

## Backup validation status

### Controlled manual test --- verified

A controlled production backup test was completed successfully on
2026-09-02.

The script exited with code `0` and produced:

`/mnt/erpnext_backups/2026-09-02_09-48`

The directory contained four non-empty artifacts:

-   `20260902_094850-ccpcerp_local-database.sql.gz`
-   `20260902_094850-ccpcerp_local-files.tar`
-   `20260902_094850-ccpcerp_local-private-files.tar`
-   `20260902_094850-ccpcerp_local-site_config_backup.json`

The test also verified the expected CIFS mount and completed without
leaving a `.partial-*` directory.

This establishes successful **manual end-to-end backup validation**.

### Unattended scheduled test --- pending

The first natural 02:00 execution of the hardened script has not yet
been verified.

Until its log and resulting NAS directory are inspected, unattended cron
execution should remain classified as:

**Pending validation**

Do not mark scheduled backup validation complete solely because the
manual test succeeded.

## Historical backup recovery performed on 2026-09-02

Before the NAS mount was repaired, the mountpoint path existed as an
ordinary directory on the server's local NVMe filesystem.

Because the former script created the destination before verifying the
NAS mount, backups were written into that local directory while
appearing to target the NAS.

Before restoring the CIFS mount, the local backup set was preserved at:

`/home/gani/erpnext-backup-recovery-2026-09-02`

The preserved recovery set contained:

-   29 timestamped backup directories
-   116 files
-   Four expected artifacts per recovered timestamp

The original local set and safety copy were verified to have matching
file counts and byte totals.

The recovered directories were transferred to the Synology NAS with
existing NAS files preserved. A checksum dry-run after transfer reported
no differences between the recovery copy and corresponding NAS content.

The recovery copy must remain in place until cleanup is explicitly
approved.

### Known historical gap

No backup for:

`2026-08-04`

was found in either the recovered local backup set or the NAS backup
set.

This is a known historical backup gap. It must not be represented as
recovered or reconstructed.

## Hidden local fallback data

The original accidental local backup directories remain physically
underneath `/mnt/erpnext_backups` on the ERP server's local filesystem.

They are hidden while the CIFS filesystem is mounted.

Removing them would require deliberately unmounting the NAS and deleting
local files. This is destructive cleanup and must not be performed as
part of normal backup validation.

Do not unmount the NAS or remove these files without explicit approval
and a separate cleanup procedure.

## Backup verification procedure

For routine verification, confirm:

1.  The NAS mount is the expected CIFS source.
2.  The most recent timestamped backup directory corresponds to the
    expected backup run.
3.  The directory contains exactly the required backup artifacts.
4.  All required artifacts are non-empty.
5.  No stale `.partial-*` directory indicates an interrupted transfer.
6.  The backup log reports successful completion.
7.  The root cron schedule remains present and there is no duplicate
    user-level schedule.

Successful creation verifies backup production; it does **not** by
itself prove that a complete disaster restore will succeed.

## Restore procedure --- controlled production operation

A full restore is a production-impacting operation and requires explicit
approval before execution.

The exact restore commands should be selected according to the
Frappe/ERPNext version and the recovery scenario rather than copied
blindly from an old procedure.

At a high level:

1.  Identify the exact timestamped backup to restore.
2.  Verify all four backup artifacts are present and non-empty.
3.  Preserve the current production state before overwriting anything
    when feasible.
4.  Confirm the intended target site is `ccpcerp.local`.
5.  Restore the database using the supported Frappe restore mechanism.
6.  Restore public files.
7.  Restore private files.
8.  Restore or reconcile site configuration only as appropriate for the
    target environment.
9.  Perform required migrations only with explicit approval.
10. Start/verify the required services.
11. Verify application login and core ERPNext functionality.
12. Verify representative business records and attachments.
13. Record the recovery operation and backup timestamp used.

Never perform a database restore merely to test whether a backup file
exists.

## Restore testing

Backup creation and restore testing are separate controls.

The current hardened backup workflow has been manually validated, but a
documented periodic restore test is still recommended.

A future restore-test procedure should preferably use an isolated
non-production environment so that the backup can be restored and
verified without overwriting the production database.

Restore testing should verify at minimum:

-   Database decompression/import succeeds.
-   Frappe recognizes the restored site.
-   Public files are accessible.
-   Private files are accessible with appropriate authorization.
-   Representative ERPNext documents are present.
-   Attachments open correctly.
-   Application migrations can complete where required.
-   Core business workflows load without database/schema errors.

## Complete server recovery

For complete ERP server loss, the recovery sequence should be:

1.  Provision the replacement Ubuntu Server.
2.  Restore the required network configuration.
3.  Install and verify Docker/Compose prerequisites.
4.  Restore the deployment repository from GitHub.
5.  Restore the custom `ccpcerp` application source from GitHub.
6.  Restore approved environment configuration and secrets from secure
    storage.
7.  Restore the Synology CIFS mount configuration without exposing its
    credentials.
8.  Verify the NAS mount source and filesystem type.
9.  Rebuild or restore the required CCPC ERP Docker image.
10. Create the required Frappe/Docker environment.
11. Select and verify a complete NAS backup set.
12. Restore the database and files.
13. Run required migrations only with explicit approval.
14. Verify ERPNext health and application access.
15. Verify representative business records and attachments.
16. Re-establish and verify the root backup schedule.
17. Perform a fresh post-recovery backup after the restored system is
    stable.

## Recovery time objectives

Current target recovery times remain planning targets rather than
guaranteed service-level objectives.

  Recovery Scenario                Target Recovery Time
  ------------------------------ ----------------------
  Framework recovery                         30 minutes
  Docker environment recovery                    1 hour
  ERPNext application recovery                   1 hour
  Database restore                           30 minutes
  Complete server recovery                      4 hours

These targets should be revised using measured results from future
restore exercises.

## Remaining recovery work

The following work remains:

-   Verify the first unattended 02:00 hardened backup.
-   Establish a periodic isolated restore test.
-   Document measured restore-test results.
-   Consider backup-failure alerting.
-   Verify secure backup arrangements for `.env`, SSH keys, and other
    non-Frappe recovery assets.
-   Decide when the temporary recovery copy at
    `/home/gani/erpnext-backup-recovery-2026-09-02` can be removed.
-   Separately decide whether to clean the old hidden local fallback
    backups.
-   Preserve the documented `2026-08-04` backup gap.
-   Review recovery-time targets after actual restore testing.

## Recovery checklist

Before declaring a recovery complete, verify:

-   [ ] Correct server/network environment restored
-   [ ] Deployment framework restored from trusted source
-   [ ] Correct application source/version restored
-   [ ] Docker/Compose configuration restored
-   [ ] Secrets restored from approved secure sources
-   [ ] Synology NAS mounted from the expected CIFS source
-   [ ] Selected backup contains all four required artifacts
-   [ ] Database restored successfully
-   [ ] Public files restored successfully
-   [ ] Private files restored successfully
-   [ ] Required migrations completed successfully, if approved and
    applicable
-   [ ] ERPNext login works
-   [ ] Representative business data verified
-   [ ] Representative attachments verified
-   [ ] Production health checks pass
-   [ ] Root backup schedule verified
-   [ ] Fresh post-recovery backup completed
-   [ ] Recovery event documented

## Safety notes

Do not expose secrets during recovery.

Do not delete backup data, alter retention, unmount the NAS, restore a
database, migrate the production site, recreate production containers,
or perform destructive Docker cleanup without explicit approval.

When uncertain, preserve the current state first and validate recovery
assets before making changes.