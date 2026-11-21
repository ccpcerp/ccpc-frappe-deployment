# Phase 1 — approved isolated two-site SQL + files recovery rehearsal

**Prepared:** 2026-11-19 Asia/Manila. **Status:** Operator procedure and script committed/verified; **the restore has NOT been executed**. Owner expressly approved a controlled, isolated restore rehearsal of the new MAIN + Integration2 DEVELOPMENT backups with no writes to the live DEVELOPMENT sites or old/new PRODUCTION. This authorization is strictly a **disposable test restore**, not deployment, site migration, metadata/Finance change, ordinary Docker services restart, live DB restore or a change to the bench's app checkout.

## Exact backup provenance

- MAIN snapshot: `development.localhost-20261118T233442Z-8db803832468`
- Integration2 snapshot: `ccpc-integration2.localhost-20261118T233442Z-8db803832468`
- NAS: `/mnt/erpnext_backups/ccpc-development-phase1-two-site-preswitch-20261118T233444Z-35c00130d53b457e`
- Local on the old `ccpcerpserver` DEVELOPMENT host: `/home/gani/deployments/frappe_docker/development/frappe-bench/.ccpc-pr32-snapshots`
- Previous operator output shows 2/2 four-file local backups and 2/2 matching Synology copies, 8/8 SHA256 PASS, exit 0; no recovery validation yet.

## Script identity and constraints

- Exact [operator script](../../scripts/development/operator/ccpc_phase1_two_site_restore_rehearsal_20261119.sh), created in GitHub commit **`3cffeb7e9b193a9a802a29432a7f7c3c7041b695`**, Git blob **`02f3acadb328bd87a7f76ae762067a53d9003b9d`**.
- Portable file SHA256: **`2389506f20f9b138599b9709eba24b1a9a466954bf665eecd79b74b52461bde0`** (local `git hash-object` agrees with verified GitHub blob; 14,401 bytes).
- Local static and synthetic tests on exact script file: `bash -n` PASS, embedded host Python AST parse PASS; simulated 4-component gzip/JSON/TAR manifest verified, synthetic public/private TAR contents extracted and checked, intentionally corrupted SQL source rejected. **No MariaDB container, production, persistent DEVELOPMENT or NAS was accessed during these tests.**
- Fixed source set only. The script verifies SHA256 of 8 **local** and 8 **NAS** component files and agrees per manifest; validates TAR paths, rejects unsafe links/absolute/path-traversal, confirms JSON type, checks host filesystem and MemAvailable, named running DEVELOPMENT container and Compose project, exact Synology CIFS mount, and an **already-installed** `docker.io/mariadb:11.8` image. No image pull; missing image causes STOP.
- The only database server the rehearsal writes to is an **ephemeral isolated** MariaDB 11.8 Docker container with `--network none`, no published port or host/NAS/SSH/Docker-socket mounts, 3 GiB RAM+swap cap, 2 CPU cap, 256-process cap, `no-new-privileges`. It imports SQL dumps from the verified NAS archives into **two newly created databases inside that container only** and validates that Frappe tables and `tabDocType` records exist. Site configuration and public/private TARs are recreated under a *new 0700 private scratch directory* inside `/home/gani`, never inside the Frappe bench. The script stops its unique container and removes the scratch directory after the test.
- This rehearsal uses the host's shared Docker daemon and temporarily consumes its bounded CPU/RAM/storage; it **does not** change existing containers or grant access to production mounts. The test container has no network, but the operator's host can still access the already-mounted Synology read-only by this script.
- **Evidence limits:** Actual restored SQL + files do not prove the complete Frappe v16 app can boot, migrations succeed, business document permissions are correct, or full site-level recovery can finish. A separate isolated full-Frappe acceptance is needed for those claims. No current source checkout, scheduler, Compose project or real site is changed by this rehearsal.

## Operator: transfer from Windows PowerShell

Download the exact script from the GitHub link above or the ChatGPT file link, and confirm the file exists under Windows Downloads. On Windows PowerShell (not on server):

```powershell
Test-Path "$HOME\Downloads\ccpc_phase1_two_site_restore_rehearsal_20261119.sh"
scp "$HOME\Downloads\ccpc_phase1_two_site_restore_rehearsal_20261119.sh" gani@192.168.50.166:/home/gani/
```

Use the same SSH authentication to the **verified DEVELOPMENT** host `192.168.50.166` as the successful previous transfer. Do **not** send the script to dedicated PRODUCTION `192.168.50.186`. The SCP step transfers the file only; it does not execute the rehearsal.

## Operator: verify and launch ONLY on the original DEVELOPMENT host

On `gani@ccpcerpserver` execute:

```bash
script=/home/gani/ccpc_phase1_two_site_restore_rehearsal_20261119.sh

if test "$(hostname -s)" = ccpcerpserver &&
   printf '%s  %s\n' '2389506f20f9b138599b9709eba24b1a9a466954bf665eecd79b74b52461bde0' "$script" | sha256sum -c -; then
    if CCPC_APPROVE_PHASE1_ISOLATED_RESTORE=YES bash "$script"; then
        echo 'RESTORE REHEARSAL EXIT CODE: 0'
    else
        result=$?
        echo "RESTORE REHEARSAL EXIT CODE: $result"
    fi
else
    echo 'STOP: wrong host or script SHA256 mismatch. No rehearsal executed.'
fi
```

Only run the exact verified script. It may request the usual `sudo` password. It will **not** request any production password or site-config credentials. Do not paste sensitive file contents, passwords or SQL records into chat.

Expected on a successful real run (illustration, **not yet evidence**):

```text
TWO LOCAL/NAS BACKUP SETS: 8/8 SHA256 PASS
OFFLINE MARIA DB IMAGE / DEV IDENTITY: VERIFIED
ISOLATED FILES/CONFIG RESTORE: ccpc_rehearsal_main PASS
ISOLATED FILES/CONFIG RESTORE: ccpc_rehearsal_int2 PASS
DISPOSABLE MARIADB: NETWORK NONE, NO PORTS, RESOURCE LIMITED
ISOLATED SQL RESTORE: ccpc_rehearsal_main PASS
ISOLATED SQL RESTORE: ccpc_rehearsal_int2 PASS
TWO-SITE ISOLATED SQL + FILE RECOVERY: PASS
FULL FRAPPE SITE BOOT / APP UAT: NOT TESTED
LIVE DEV / PROD SOURCE, DB, SERVICES: NOT MODIFIED
ISOLATED SCRATCH CLEANUP: PASS
PHASE1_TWO_SITE_ISOLATED_RESTORE_REHEARSAL: PASS
RESTORE REHEARSAL EXIT CODE: 0
```

On **STOP** or a nonzero exit code, do **not** automatically retry, change image restrictions, grant Docker extra privileges, remove logs, or delete old backups. Send only safe status lines. In particular an interrupted run or cleanup failure may leave **a uniquely labeled isolated container** or a private scratch folder. Review those exact temporary objects before retrying; never run broad `docker system prune`, `docker volume prune`, `rm -rf` on arbitrary paths, or `docker compose down` against the existing project.

## Deployment gate remains separate

After restore evidence is documented, the next project milestone is a shared-bench **two-site-aware** source-switch/rollback design, current PR33 checkout and protected `AGENTS.md` disposition, `setup.after_migrate()` impact review, separate actual DEVELOPMENT write authorization, real site UAT and only then independently approved PRODUCTION deployment.


## 2026-11-19 — Operator-reported isolated SQL/files restore: BOTH SITES PASS

**Evidence:** The owner ran the GitHub-reviewed isolated restore script on `gani@ccpcerpserver` and pasted the full terminal result in ChatGPT, including successful SHA256 check of the script itself:

```text
/home/gani/ccpc_phase1_two_site_restore_rehearsal_20261119.sh: OK
TWO LOCAL/NAS BACKUP SETS: 8/8 SHA256 PASS
OFFLINE MARIA DB IMAGE / DEV IDENTITY: VERIFIED
ISOLATED FILES/CONFIG RESTORE: ccpc_rehearsal_main PASS
ISOLATED FILES/CONFIG RESTORE: ccpc_rehearsal_int2 PASS
DISPOSABLE MARIADB: NETWORK NONE, NO PORTS, RESOURCE LIMITED
ISOLATED SQL RESTORE: ccpc_rehearsal_main PASS
ISOLATED SQL RESTORE: ccpc_rehearsal_int2 PASS
TWO-SITE ISOLATED SQL + FILE RECOVERY: PASS
FULL FRAPPE SITE BOOT / APP UAT: NOT TESTED
LIVE DEV / PROD SOURCE, DB, SERVICES: NOT MODIFIED
ISOLATED SCRATCH CLEANUP: PASS
PHASE1_TWO_SITE_ISOLATED_RESTORE_REHEARSAL: PASS
RESTORE REHEARSAL EXIT CODE: 0
```

**Result boundaries:** The script reported successful import of each `database.sql.gz` into its separately named MariaDB database inside a newly created, network-disabled disposable container, and extracted both configurations and public/private TAR files into a private scratch path. Both previously verified local and NAS sets passed checksum revalidation. Disposable database container shutdown and scratch cleanup were **script-reported PASS**, with exit `0`. This is a **successful isolated SQL+files restore rehearsal**, stronger than simple backup integrity verification; not a full Frappe bench/site restore or proof of successful application startup, scheduler, schema migration, real CCPC transactions or permission correctness. ChatGPT did not have independent SSH/Docker access and relies on operator-supplied terminal output. Script's own reporting says live DEV/PROD source, DB and services were not modified. No source pull/checkout, `bench migrate`, service restart or PRODUCTION deployment was authorized by this test.

**Decision:** Isolated backup content recoverability gate is satisfied for both valid DEVELOPMENT sites at the SQL/files level. Preserve 2026-11-19 backup set and historical Nov17 copies. Next gate is a **GitHub-reviewed, two-site-aware shared-bench integration and rollback plan**, including protected untracked `AGENTS.md`, PR33 billing isolation, full `setup.after_migrate` effects, and separately approved live DEVELOPMENT code/migration operations. No repeat of this successful restore necessary absent changed backups or environment.
