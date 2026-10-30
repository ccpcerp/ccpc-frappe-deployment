# PR #32 — isolated Integration2 backup restore rehearsal (approved scope, not yet executed)

**Prepared:** 2026-10-30 (Asia/Manila)  
**Owner approval:** Explicit approval to rehearse a **separately isolated, disposable Integration2 restore**, without touching the two live DEVELOPMENT sites or PRODUCTION. This authorizes preparation and the bounded rehearsal **only after the target and its access controls are verified**; it is not blanket permission to install Docker, attach interfaces, transfer live credentials to a lab, use another host, overwrite any MariaDB data, destroy a VM, change services, or deploy PR #32. Any new infrastructure operation requires a specific reviewed command/target. Record resulting evidence here and in [CURRENT-HANDOFF-2.md](CURRENT-HANDOFF-2.md).

## 1. Exact protected recovery source, already verified

- Existing live-development synthetic site: `ccpc-integration2.localhost`; two synthetic Companies `Integration Test Issuer (TISS)` and `Integration Test Requester (TREQ)`. Its **actual site backup content has not been separately classified as entirely fictitious or free of credentials**, despite synthetic Company names. Handle as confidential.
- DEV app commit installed at backup: `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`; Frappe 16.33.1, ERPNext 16.34.2, ccpcerp 0.0.1. Do **not** restore the backup first into PR32 HEAD `061e65710eb4b527fc8ac579aaab8ccad4dd131d`, which includes five additional Finance lifecycle DocTypes; first prove source-version restore at the original SHA.
- Immutable-intent local snapshot directory (protect): `/workspace/development/frappe-bench/.ccpc-pr32-snapshots/ccpc-integration2.localhost-20261029T132329Z-99d6786e` inside DEV, host equivalent `/home/gani/deployments/frappe_docker/development/frappe-bench/.ccpc-pr32-snapshots/ccpc-integration2.localhost-20261029T132329Z-99d6786e`. Separate main DEVELOPMENT backup must remain untouched.
- Checksum-verified NAS copy: `//192.168.50.132/erpnext_backups` mounted on `/mnt/erpnext_backups`, final directory `ccpc-development-pr32-20261029T234223Z-f38259861f97ed80` and `SHA256SUMS` manifest. Owner-reported **8/8** original vs destination hashes and published manifest PASS, **not** independent restore.
- Four archive components: database `*-database.sql.gz`, site config `*-site_config_backup.json`, public `*-files.tar`, private `*-private-files.tar`. Frappe v16 `BackupGenerator` created these outside Frappe's auto-deletion directory. They contain potentially sensitive SQL, credentials/encryption keys and attachments; never print raw contents or commit/send them to GitHub/CircleCI.

## 2. Existing candidate isolated environment and capacity decision

GitHub [Step 136 offline lab record](DEDICATED-BACKUP-STEP136-OFFLINE-COMPOSE-FAST-PATH.md) and [dedicated-host handoff](PRODUCTION-HOST-SETUP-HANDOFF.md) describe a pre-existing Windows Hyper-V private-network guest `CCPC-Step136-LAB` / `ccpc-step136-lab`, 4 GiB assigned RAM (3.8 GiB guest visible), ~50 GiB guest disk free at the earlier observation, **no Docker executable/daemon**, no guest route or DNS at its last network checks. It is an **option to assess, not a proven Frappe/MariaDB restore runner**. It was designed for *offline non-secret Compose work*; importing an actual `site_config` or SQL dump into it is a new sensitive-data handling decision. Its RAM may be inadequate for a full Frappe/ERPNext stack. Do not add a network uplink, attach a NAS share, use the existing shared legacy Docker daemon, or reuse new/old PRODUCTION systems merely to expedite this test.

**Alternative** if this VM is unsuitable: an independently disposable owner-controlled VM/host with adequate memory and local storage, own Docker daemon or equivalent Frappe/MariaDB runtime, private networking, no credentials or sockets from existing CCPC installations. A hosted CI run can test a **new synthetic fixture**, but sending actual Integration2 backups into hosted CI without a reviewed confidential-transfer mechanism is forbidden and would not by itself establish recovery of the Oct 29 source. A second site/database in the existing shared Frappe bench **does not satisfy this independently isolated rehearsal**.

## 3. Single immediate read-only sizing gate — metadata only

At `gani@ccpcerpserver:~$` (not in the lab), obtain the original Integration2 backup file count and *total size*, without opening its contents, revealing filenames or exposing site config or credentials:

```bash
python3 - <<'PY'
from pathlib import Path
root = Path("/home/gani/deployments/frappe_docker/development/frappe-bench/.ccpc-pr32-snapshots")
d = root / "ccpc-integration2.localhost-20261029T132329Z-99d6786e"
if d.is_symlink() or not d.is_dir():
    raise SystemExit("STOP: Integration2 snapshot directory missing or symlinked")
fs = list(d.iterdir())
if len(fs) != 4 or any(p.is_symlink() or not p.is_file() or not p.stat().st_size for p in fs):
    raise SystemExit("STOP: Integration2 snapshot missing one of four nonempty regular files")
dbs = [p for p in fs if p.name.endswith("-database.sql.gz")]
if len(dbs) != 1:
    raise SystemExit("STOP: Database component missing or duplicate")
stem = dbs[0].name.removesuffix("-database.sql.gz")
if not stem.endswith("-ccpc-integration2_localhost"):
    raise SystemExit("STOP: Wrong backup site identity")
expected = {
    stem + "-database.sql.gz",
    stem + "-site_config_backup.json",
    stem + "-files.tar",
    stem + "-private-files.tar",
}
if {p.name for p in fs} != expected:
    raise SystemExit("STOP: Unexpected backup component names")
print("INTEGRATION2 SOURCE COMPONENTS: 4/4 PASS")
print("INTEGRATION2 TOTAL BACKUP GiB:", round(sum(p.stat().st_size for p in fs) / (1024**3), 3))
print("READ-ONLY SIZING COMPLETE")
PY
```

This is **not** permission to copy, open or restore the backups. The previously reported 4-part gzip/TAR/JSON readability and NAS SHA256 validation need not be needlessly rerun before sizing.

## 4. Required isolation and exact restore steps — do NOT execute until R0 approved target is proven

1. **R0: Target approval and isolation proof.** Name the disposable VM/host, owner, resource limits, storage/cleanup plan and verified separate virtualization/daemon/volumes; no routes to current DEV or PRODUCTION hosts or NAS, no shared Docker socket, no mounted prod credentials, no host-only path that can overwrite original backups. Confirm memory/disk for Frappe 16 + ERPNext 16 + MariaDB and the verified backup size; a powered-on/idle VM is not proof it is ready. Don't convert the existing private-switch lab into a networked runtime without specific approval.
2. **R1: Confidential data transfer design.** For the Integration2 set only, maintain exact SHA256 integrity across a controlled encrypted/offline or otherwise access-restricted transfer into fresh isolated scratch storage, and keep the original four artifacts separate and read-only. Do not upload SQL, site config, private attachments, recovered passwords or encryption key to GitHub, CircleCI, public cloud, chat, logs or a shared hypervisor folder. Document where temporary sensitive data resides, who can access it and safe retirement. Even the synthetic site may hold real test-user identities or secrets.
3. **R2: Exact source/runtime recreation.** In the isolated lab **only**, install pinned Frappe 16.33.1 and ERPNext 16.34.2, plus CCPC exact app `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`, compatible private MariaDB/Redis and a wholly new unique site/database/DB user. Ensure outgoing emails, background workers, webhooks and integrations cannot reach real services. The old backup's site-config JSON is evidence, **not safe to install blindly**: it can include original database credentials/host/keys; provision lab-only DB credentials and preserve any necessary encryption key privately, without enabling connection to live DEV MariaDB.
4. **R3: Restore into unique lab-only target.** Before constructing or executing a Frappe `bench --site <lab-only-name> restore <sql.gz> --with-public-files ... --with-private-files ...` operation, independently verify the working directory, app commit, site identity, distinct DB name/host/user, target's local MariaDB instance and its absence of original data, source backup hashes, no shared host mounts/routes, and isolated files destination. **Important pinned Frappe v16 source finding:** `frappe/commands/site.py` calls `restore_backup` -> `_new_site(..., force=True, source_sql=...)`. This may recreate/drop the target database; an operator must never run it within the shared DEVELOPMENT bench or against either existing site. Do not include original `--db-root-password` on a visible command line.
5. **R4: Read-only acceptance after restored lab comes up.** Verify restored site login with lab-only password; installed apps, DocTypes and patch logs match original commit; two TISS/TREQ Companies and representative synthetic Finance/Withdrawal mappings exist; database reads succeed; a representative public and authorized private attachment open; no leaking host URLs, emails, scheduled tasks or background integrations. Recheck storage/backup SHA against the source. Any migration into PR32's five new DocTypes is a **separate follow-up test and explicit stage**, not part of proof that old commit restores.
6. **R5: Reporting and disposal.** Record sanitized result (target type, exact source SHAs, archive inventory, import outcome, representative business read checks, attachment checks, credentials handled safely, rollback/teardown plan). Discard isolated **test** databases and artifacts only after explicit target-scoped cleanup approval, never use wildcard or shared-host destruction. Preserve original DEV and NAS recovery sets and old PRODUCTION services.

**Current gate status:** Owner approved the isolated rehearsal objective; GitHub review and source-method assessment complete. **No independent restore, lab provisioning, data transfer, Docker installation, DB import, site migration, or teardown has been executed.** The next non-mutating operator step is **section 3 backup size only**, then choose a proven target; do not conflate synthetic CircleCI (86/86) with actual Oct 29 backup restoration. **PRODUCTION remains NO-GO.**
