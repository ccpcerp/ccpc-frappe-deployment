# CCPC ERPNext — CURRENT HANDOFF 5

**Active from 2026-11-22 (Asia/Manila).** Read [GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) first, then this compact current checkpoint. Older [CURRENT-HANDOFF-3.md](CURRENT-HANDOFF-3.md) and [CURRENT-HANDOFF-4.md](CURRENT-HANDOFF-4.md) remain historical. Always independently verify actual GitHub/DEVELOPMENT state.

## TOP: MAIN DEVELOPMENT source synchronized to Phase 1 release SHA; persistent acceptance pending

**Completed and independently verified on 2026-11-22 using the GitHub connector:**

- [Custom-app PR #41](https://github.com/ccpcerp/ccpcerp/pull/41), `test(phase1): verify HTTP rollback and cancellation/reissue consumption`, was reviewed, marked ready and **merged** by the owner-authorized GitHub merge-commit method into `release/withdrawal-department-phase1-2026-11-17`. GitHub PR is **closed/merged**.
- Reviewed PR head `45c46836e50029e265c6e3d7ca443090c364c0f0`; pre-merge base `034afb116cf3fe0e3f9315b932eceba6dc961ce6`; compare: **6 ahead, 0 behind, four changed paths**: two test modules, disposable test-site guard, and one-shot GitHub Actions workflow. No changes to runtime business/accounting controllers, Finance policies, schemas or permissions.
- Verified merge commit: **`b0cbe5c13cb68499a7920de2879f65e72cff000a`** ([commit](https://github.com/ccpcerp/ccpcerp/commit/b0cbe5c13cb68499a7920de2879f65e72cff000a)). Independent release-branch read confirmed this exact head. A formal GitHub COMMENT review was submitted (review ID `6010671375`). No merge conflicts or unresolved review threads were reported.
- Corrected pinned [GitHub Actions run #44888315575](https://github.com/ccpcerp/ccpcerp/actions/runs/44888315575), job `136798369864`, attempt 1, at exact `45c4683` completed **SUCCESS**. Workflow API, step results and actual decoded logs confirmed source/test-blob guard, static policy tests, disposable Frappe/ERPNext v16 with MariaDB 11.8 and Redis, synthetic site migration and cleanup **PASS**. Actual integration methods: `test_cancelled_issue_excluded_and_reissue_reported_once` **Ran 1 test — OK** and `test_zzz_real_wsgi_method_session_role_and_csrf_enforcement` **Ran 1 test — OK**. Coverage includes cancellation/reissue counted once in Department report with actual SLE/GL, and authenticated HTTP/CSRF fault-after-ledger rollback checked via independent SQL, retry and replay rejection. Earlier failed/incomplete runs remain historical; no rerun initiated as part of merge.
- [Phase 1 PR #35](https://github.com/ccpcerp/ccpcerp/pull/35) was independently checked **open/draft, not merged**, with head `release/withdrawal-department-phase1-2026-11-17` now at `b0cbe5c...` and base `feature/finance-mapping-lifecycle-2026-10-28`.

**Boundary / explicitly not complete:**

- Phase 1 is **same-Company-only**; intercompany billing remains **disabled**, with separate draft [PR #33](https://github.com/ccpcerp/ccpcerp/pull/33) out of scope. The owner-approved policy permits Withdrawal Slip preparer self-approval, but issuance must be by a **different authorized authenticated Stockroom employee**.
- These two passing synthetic integration tests do **not** equal overall Phase 1 acceptance or persistent MAIN DEVELOPMENT validation. Finance Expense mapping owner sign-off where applicable, remaining release checks, PR #35 review/merge, DEVELOPMENT acceptance, backup/recovery readiness and PRODUCTION deployment are separate gates.
- **Newer 2026-11-22 operator evidence below supersedes the former DEVELOPMENT source-checkout status:** owner ran the reviewed guarded source-only fetch/detached switch and reported **PASS** at exact `b0cbe5c...`. No site migration, persistent business transaction, service restart or PRODUCTION action was reported. Backend/schema and site acceptance remain unverified.
- The one-shot GitHub Actions workflow remains committed in release history but is limited by its push trigger to the old test branch and workflow path. Any cleanup should be a separate reviewed source change, not a retroactive modification of tested evidence.

## Next concrete engineering action

**Fastest safe milestone:** Source-only DEVELOPMENT update to `b0cbe5c...` is operator-reported PASS. **Next verify CURRENT two-site DEV backup freshness and recovery readiness (rather than relying on Oct 29 historical snapshots), then perform separately approved persistent Phase 1 Withdrawal Slip → Material Issue → Stock Ledger and Expense GL → Department consumption acceptance**, including rollback/replay and reporting controls. The incoming `55eb10b...b0cbe5c` Git delta was CI/test-only, so this update alone does not introduce a new database schema change or justify a blind migration. Record real results and push reviewed fixes back to GitHub. Resolve Finance mapping sign-off; separately review draft PR #35 for release merge. PRODUCTION requires independent backup, recovery, rollback and explicit deployment approval.

Preserve GitHub-first scope, protected DEVELOPMENT and PRODUCTION data, no automatic Codex publishing or paid scheduled automation. See older handoffs for detailed audit history; do not promote their outdated next actions over this verified milestone.

## 2026-11-22 — MAIN DEVELOPMENT Git working tree inspected; source update not yet performed

**Owner-reported, read-only `docker exec --user frappe` output on `ccpcerpserver`:** custom app `/workspace/development/frappe-bench/apps/ccpcerp` at full SHA `55eb10b86a57de55a97e293a78228d9dd17b809a`, **DETACHED** HEAD, and blank `git status --short --untracked-files=all` (no listed staged, modified or untracked files). The command exited with `=== INSPECTION COMPLETE ===`. This is current *operator-provided* live state, not independent ChatGPT SSH access; it did not verify site backups or current service health.

**Independently verified GitHub comparison:** `55eb10b86a57de55a97e293a78228d9dd17b809a...b0cbe5c13cb68499a7920de2879f65e72cff000a` reports **8 commits ahead, 0 behind** with merge base exactly `55eb10b`, and **12 changed paths**, all under existing CircleCI config, one-shot GitHub CI, disposable-site guard and test modules, or Playwright test directory. No business runtime controller, schema, accounting mapping or permission file change between these source commits. Phase 1 PR #35 remains draft/unmerged and release branch still points to `b0cbe5c` at verification.

**Next action:** Operator may perform a narrowly guarded *source-only* fetch and detached checkout to pinned `b0cbe5c`, after rechecking current HEAD, clean working tree, expected app remote, source ancestry and exact changed paths. **Do not** run bench migration, write DEV business records, restore data, restart services or touch PRODUCTION during this source-sync step. Verify the resulting Git HEAD/status and stop on any guard failure. Before persistent acceptance tests, independently verify appropriate DEVELOPMENT backup/recovery state and test scope. No source sync or site change is claimed by this checkpoint.

## 2026-11-22 — MAIN DEVELOPMENT source synchronized to b0cbe5c (operator PASS)

**Newer owner-supplied terminal output following the reviewed, guarded source-only command:** fetched `release/withdrawal-department-phase1-2026-11-17` from `ccpcerp/ccpcerp`, updated the remote tracking ref from `55eb10b` to `b0cbe5c`, then switched the clean, detached DEVELOPMENT custom app to `b0cbe5c13cb68499a7920de2879f65e72cff000a`. Guards validated old HEAD, clean status, expected repo URL, exact `FETCH_HEAD`, ancestry and the 12 expected changed paths. Owner's output ended `DEVELOPMENT SOURCE UPDATE: PASS`, full target SHA, `NO DATABASE MIGRATION OR SERVICE RESTART PERFORMED`. GitHub independently verified the target commit/release branch and its source delta, but ChatGPT has no direct SSH/container session; server result is operator-reported, not remote independently re-read. No finance transaction, schema migration, maintenance action, or PRODUCTION operation has been reported.

**Backup evidence:** Older GitHub [PR32 read-only preflight](PR32-DEVELOPMENT-READ-ONLY-PREFLIGHT-2026-10-29.md) records two four-artifact DEVELOPMENT local snapshots from Oct 29, with off-host Synology checksums 8/8 PASS Oct 30, but no independent restore. These **do not prove a fresh current recovery point on Nov 22**. Next narrow read-only step: check the actual DEVELOPMENT snapshot directory ages and expected Synology mount/DEVELOPMENT-only historical set without touching legacy PRODUCTION backup operations; before any new persistent ledger/financial acceptance writes, obtain a new adequately protected two-site backup or documented equivalent and scoped approval for test mutations. Avoid repeatedly reopening already resolved Synology DSM ACL reviews absent new evidence. PR #35 remains draft/unmerged. PRODUCTION remains separate, explicitly gated.

## 2026-11-22 — Codex screenshot: existing local DEVELOPMENT snapshot ages; freshness gate still open

The owner shared a **mobile photo of a Codex read-only DEVELOPMENT recovery-inspection output**. The visible terminal lists several snapshot directories for each DEV site and labels the most recent for each: `development.localhost` **2026-11-18 23:34:43 UTC** and `ccpc-integration2.localhost` **2026-11-18 23:34:44 UTC** (as displayed; timezone not independently validated from the image). Both are earlier than the **2026-11-22** owner-reported source-only update to `b0cbe5c`. Screenshot capture provides evidence of a **directory inventory**, not proof that the newest snapshots contain complete readable four-part data or were copied off-host. The lower visible report recommends verifying the latest successful job against the source synchronization time. **The screenshot alone did not show mount/NAS status, completeness, or restore status; the owner's subsequent pasted Codex report below independently clarifies mount and historical directory presence.**

**Next practical gate:** Have Codex provide a very short, sanitized PASS/STOP/UNVERIFIED summary of any already completed NAS mount and backup jobs, without rerunning or modifying anything. Review the fresh two-site DEV backup creation and protected NAS-copy plan separately before persistent Withdrawal Slip/Stock Ledger/GL acceptance; never copy/restore/delete/migrate/restart automatically, and leave PRODUCTION out of scope.

## 2026-11-23 — Codex pasted final report — 12 snapshot directories, NAS mount PASS, freshness UNVERIFIED

Owner pasted Codex's final **read-only** result (reported process UID 1000): `.ccpc-pr32-snapshots` exists and contains **12** directory records across the two DEVELOPMENT sites (**7** `development.localhost`, **5** `ccpc-integration2.localhost`). **Correcting the earlier mobile-photo reading**, *both* sites have a latest listed `2026-11-18T233442Z-8db803832468` snapshot: main directory modified **2026-11-18 23:34:43 UTC**, integration2 directory modified **2026-11-18 23:34:44 UTC**. Their shared timestamp and suffix is as copied from the actual operator report; directory names/times alone cannot prove whether they are separate, complete, valid backup files or capture times. The newest listed per-site directories precede the Nov 22 source-only synchronization. The operator reported no unexpected path, permission, mount or access conditions (no STOP triggered).

**PASS, metadata only:** `findmnt` confirmed exact `//192.168.50.132/erpnext_backups` mounted as `cifs` at `/mnt/erpnext_backups`; previous DEVELOPMENT-only NAS directory `ccpc-development-pr32-20261029T234223Z-f38259861f97ed80` exists. Both local/NAS historical sets present at directory level. This is operator-provided Codex evidence, not live independent ChatGPT server access.

**Still UNVERIFIED:** Any backup job completion after source synchronization; fresh current two-site consistent recoverable backup; file/component integrity and size/checksums; off-host copy of any November snapshot; independent isolated restore. Do not interpret `STOP — No unexpected condition` in Codex output as a STOP failure; no STOP was reported. Existing Oct 30 NAS set did have historical 8/8 checksum PASS per PR32 docs, but that says nothing about today's snapshot freshness or restoration.

**Shortest safe path:** avoid more generic infrastructure or DSM ACL review already completed historically. Owner should explicitly authorize a *new bounded two-site DEVELOPMENT-only recovery operation*: new non-overwriting 4-component full backups for `development.localhost` and `ccpc-integration2.localhost` outside default Frappe automatic cleanup, metadata/stream-integrity checks, SHA-256 manifest and safeguarded exclusive copy to a distinct DEV-only NAS folder under the already confirmed mounted share. Codex may prepare the reviewed script/plan read-only now, but do not execute backup creation/copy until scoped operator approval. Never modify legacy production backup files, retention, services, schema, ledgers, or PRODUCTION. Even a successful archive/NAS copy is not a restore rehearsal. Review recovery before separately approved persistent stock/GL transactions.


## 2026-11-23 — one-shot two-site DEVELOPMENT backup approved; script pinned, NOT RUN

**Owner authorization in the active conversation:** one bounded DEVELOPMENT-only backup and NAS copy: full unfiltered four-component backup for each site (development.localhost and ccpc-integration2.localhost), integrity validation, SHA-256 manifest, exclusive non-overwriting new DEV-only directory on already verified Synology NAS. Authorization excludes any PRODUCTION or legacy production-backup changes, migrations, transactional ERPNext writes, app checkout changes, service restarts, restoration, retention/deletion, automatic retries or other Codex actions. Script publication is not a claim of execution.

**Reviewed GitHub operator artifact:**
- Repo: ccpcerp/ccpc-frappe-deployment; branch: review/dev-phase1-two-site-backup-2026-11-23.
- GitHub commit: 5a1a27c6432345b81b04e9d5b1d8c4f5b6139dfe (independently verified branch HEAD).
- Repository path: scripts/development/operator/ccpc_dev_phase1_two_site_backup_20261123.sh.
- Git blob SHA-1: 66778017244ea46f5b516f23ea2db59dea770a00; matched locally using git hash-object.
- Full file SHA-256: 27f19d27f11941b7a41659972b7ecefe7b429ae884b791f31045d88280b7cb60.
- Local static checks: bash -n and both outer and embedded Python syntax PASS. Actual Frappe execution and backup results UNVERIFIED. BackupGenerator use was checked against upstream Frappe source commit 988e54f; the script avoids the default backup cleanup path.

**Execution safeguards in reviewed artifact:** restrict host UID 1000 / ccpcerpserver, one exact DEV container and checked host bind, clean app SHA b0cbe5c13cb68499a7920de2879f65e72cff000a, exact historical Synology CIFS mount and DEV historical directory, storage space, two exact sites, Frappe backup encryption guard; create private new local snapshot directories outside the default Frappe retention tree using BackupGenerator(ignore_conf=True) with database + config + both attachment archives. Stream-test gzip/TAR and JSON, check four files per site, then make a unique NAS partial DEV directory, exclusively copy all eight components, verify sizes/SHA256, write and verify checksum manifest, rename to fresh final DEV-only directory. Leave old backups/partial directories intact; any STOP means stop, preserve results and investigate before deciding whether to rerun. NAS permissions rely on previously owner-verified Synology DSM shared-folder access (PR32 Oct30), not CIFS POSIX 0755 presentation; no share permission changes are permitted.

**Next operator step:** Existing restricted non-root Codex may, under the above one-operation owner approval and normal command approval prompts, fetch the exact reviewed GitHub branch into an isolated operator staging folder (not the protected DEVELOPMENT app checkout), verify the exact commit and file SHA256, and run the script once. No unrestricted Codex permissions, SSH key printing, automatic GitHub publication, scheduled action or PRODUCTION access. Return sanitized PASS/STOP summary. Actual point-in-time consistency and independent restore remain unverified even if all files/checksums pass.

## 2026-11-23 — Codex SSH preflight STOP before transfer; backup authorization remains unused

**Owner pasted Codex execution result:** host identity `ccpcerpserver`, UID `1000` PASS. Exact Git SSH `git ls-remote --exit-code git@github.com:ccpcerp/ccpc-frappe-deployment.git refs/heads/review/dev-phase1-two-site-backup-2026-11-23` failed exit **128** before any commit/script SHA-256 pin verification or operator artifact staging. Codex specifically reported SSH rejecting `/etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf` due to file ownership/permissions. Codex reported **both site backups STOP, script never executed; NAS 8/8 UNVERIFIED; no final NAS directory created by this attempt**. There are no new local or NAS backup artifacts *attributable to this run*. Do not call this a failed Frappe backup or retry the backup script; the script was never fetched or run.

**Independent GitHub recheck:** review branch still at `5a1a27c6432345b81b04e9d5b1d8c4f5b6139dfe`, file blob SHA-1 `66778017244ea46f5b516f23ea2db59dea770a00`. The script content's SHA-256 was recomputed and matches **`27f19d27f11941b7a41659972b7ecefe7b429ae884b791f31045d88280b7cb60`**. Thus source artifact remains verified *in GitHub*, but not locally staged.

**Next smallest safe Codex action:** Read-only inspect `stat` UID/GID/mode/type for `/etc/ssh/ssh_config`, `/etc/ssh/ssh_config.d`, and `/etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf`; optionally `namei -l` those exact path components. Return sanitized metadata and whether symlinks exist; **no file contents, credentials, environment variables or SSH verbose output**. Do not chmod/chown/delete/edit the system-wide SSH config, use sudo, force authentication, turn off StrictHostKeyChecking, override with `ssh -F /dev/null`, or bypass possible network-control rules. Decide on a separately approved repair or secure alternate code delivery after verifying what caused the bad ownership/mode report. The owner's narrowly approved one-time DEV backup/NAS-copy action has **not been consumed**, but execution should remain held pending safe delivery and exact checksum verification. PRODUCTION remains out of scope.

## 2026-11-23 — Codex SSH config UID mapping likely sandbox artifact; verify true host before remediation

Owner pasted read-only Codex commands and output: `stat -c '%n | UID=%u GID=%g MODE=%a TYPE=%F'` showed `/etc/ssh/ssh_config` **65534:65534 mode 644**, `/etc/ssh/ssh_config.d` **65534:65534 mode 755**, `/etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf` a **symlink** reported mode 777 with 65534:65534; `namei -l` followed the link to `/usr/lib/systemd/ssh_config.d/20-systemd-ssh-proxy.conf`, a regular **644 nobody:nogroup** file. Codex reported even standard root filesystem paths as `nobody:nogroup` in its session. **No file changes were made.**

**Interpretation:** Consistent with a Codex process sandbox / user namespace mapping rendering host-owned files as unmapped UID 65534, but **not yet proven**. Never infer the real host SSH files are misowned or run `sudo chown`, `chmod`, link edits, `ssh -F /dev/null` or host-wide SSH workarounds from the Codex view. The rejected `git ls-remote` remains a *pre-staging* failure, and the authorized one-shot DEV backup has not been executed or consumed.

**Next minimal safe check**: use the normal trusted Ubuntu host terminal **outside Codex/sandbox** as non-root gani, read-only, to report `hostname -s`, `id -u`, and `stat -Lc '%n | UID=%u GID=%g MODE=%a TYPE=%F' / /etc/ssh/ssh_config /etc/ssh/ssh_config.d /usr/lib/systemd/ssh_config.d/20-systemd-ssh-proxy.conf`. If host ownership is normal root:root on system paths, don't repair anything: plan ordinary host-side authenticated staging of exact reviewed script with strict SSH key verification and exact commit/SHA256, then execute only within the previously scoped approval. If host paths also show 65534, stop and investigate a host OS/package/sandbox identity fault separately before edits. No PRODUCTION impact, no backup was run in this diagnostic.

## 2026-11-23 — Normal Ubuntu host SSH config ownership independently checked by owner: PASS

**Owner's normal (non-Codex) Ubuntu terminal output:** hostname `ccpcerpserver`, UID `1000`. `stat -L` reported `/` **0:0 755 directory**, `/etc/ssh/ssh_config` **0:0 644 regular**, `/etc/ssh/ssh_config.d` **0:0 755 directory**, resolved `/usr/lib/systemd/ssh_config.d/20-systemd-ssh-proxy.conf` **0:0 644 regular**. These are expected secure host ownership and modes. The conflicting Codex-only UID/GID 65534 readings are consistent with unmapped ownership inside Codex's execution isolation, not damaged host SSH configuration. Do not chmod/chown/modify SSH or disable secure SSH config processing.

**Next scoped action:** deliver the exact GitHub-pinned operator script using `git fetch` from the **normal non-root Ubuntu host terminal outside Codex**, strict SSH host-key checking, isolated `git init` temp directory, pinned review branch commit `5a1a27c...` and exact file Git blob/SHA-256 checks; stage to a private, non-overwriting directory outside the protected DEVELOPMENT app checkout. **Staging alone is not backup execution.** After confirming the staged file's checksum, execute the already owner-approved script one time from the normal host; don't attempt unsafe Codex sandbox bypass, modify GitHub file, expand scope, or retry a partial backup without review. The first Codex SSH preflight did **not** execute the one-shot backup. No production operations permitted.

## 2026-11-23 — owner confirmed exact backup script staged and checksummed on trusted host

**Owner's direct Ubuntu host terminal result** (not Codex sandbox): `/home/gani/ccpc-reviewed-scripts/ccpc_dev_phase1_two_site_backup_20261123.sh: OK`, then `DEVELOPMENT BACKUP SCRIPT: STAGED AND VERIFIED`, `BACKUP NOT YET EXECUTED`. This is the output of the previously reviewed host-side staging procedure which fetched GitHub commit `5a1a27c6432345b81b04e9d5b1d8c4f5b6139dfe`, verified blob SHA `66778017244ea46f5b516f23ea2db59dea770a00`, and compared file SHA-256 `27f19d27f11941b7a41659972b7ecefe7b429ae884b791f31045d88280b7cb60`. GitHub branch head/file blob rechecked independently and unchanged in this follow-up. No Frappe backup or NAS transfer has yet occurred.

**Next owner action, already expressly approved for one execution:** From trusted host terminal as UID 1000, reverify host/UID, non-symlink regular staged file, stored SHA-256 and shell syntax; execute the pinned script exactly once. Do **not** use Codex's UID-mapped sandbox to run it, modify system SSH, disable guards, add auto-retry or touch PRODUCTION. The script itself checks exact DEV container/bind, app source commit, Synology mount, target site names, and writes new isolated DEV-only snapshots and NAS set. If any STOP occurs, preserve partials and return sanitized failure, with no rerun. A passing backup/copy still requires a separate independent restore/recovery gate before transactional acceptance.

## 2026-11-23 — owner read-only preflight isolates one failing guard: DEV BIND MOUNT

After owner reported Ubuntu terminal exited code 1 and no visible new local `*ccpc-development-phase1-*` backup directories (only a distinct historical 2026-11-18 NAS directory), operator reconfirmed the staged script owner `1000`, mode `600`, expected SHA-256 PASS, `bash -n` PASS, local backup root owner `1000` mode `700`. **Do not conflate** generic terminal exit code with a demonstrated script `STOP` line; its original stderr was not shown.

Owner's latest **read-only** exact-guard inventory: `HOST PASS`, `USER PASS`, `NAS MOUNT PASS`, `HISTORICAL NAS SET PASS`, `LOCAL FREE SPACE PASS`, `DEV CONTAINER RUNNING PASS`, `DEV BIND MOUNT STOP`, `APP COMMIT PASS` (`b0cbe5c`), `APP CLEAN PASS`. This isolates a **likely mismatch in the script's expected Docker mount Source/Destination/RW triple**, not evidence of a failed ERPNext backup or a reason to reconfigure Docker.

**Next single read-only command:** Docker inspect `frappe_docker_devcontainer-frappe-1` mounts, outputting only filtered DEVELOPMENT-related mount `Type/Source/Destination/RW` entries; no `Config.Env`, secrets, other service mounts. Compare to the script's pinned expected source `/home/gani/deployments/frappe_docker/development`, destination `/workspace/development`, RW true. **Do not** rerun the script, edit the staged checksum-pinned file, change bind mount configurations, use broad privileges or touch PRODUCTION. If a path mismatch is confirmed, review a narrow fail-closed correction in GitHub as a new commit and file checksum, check for any partial artifacts, then stage via trusted host outside Codex before proceeding within existing bounded DEV backup scope. Existing snapshots remain protected, NAS copy/restore unverified.

## 2026-11-23 — No mount matched previous narrow DEVELOPMENT filter; inspect /workspace mount next

**Owner's direct, read-only container inspection:** `NO MATCHING DEVELOPMENT MOUNT FOUND`, `READ-ONLY MOUNT INSPECTION COMPLETE`. The query filtered only Docker mount entries whose **Source started** with `/home/gani/deployments/frappe_docker/development` or whose **Destination started** with `/workspace/development`; it did not check an ancestor mount destination. This is consistent with the authoritative [DOCKER-DEV-PROD-ARCHITECTURE.md](DOCKER-DEV-PROD-ARCHITECTURE.md) describing a RW host bind mounted at **`/workspace`**, with `/workspace/development/frappe-bench` below that mount, but the actual live Source/Destination/RW values remain unverified.

**Next narrowly scoped read-only inspection:** run `docker inspect --format '{{json .Mounts}}' frappe_docker_devcontainer-frappe-1`, output only mount entry/entries whose Destination is exactly `/workspace` (Type, Source, Destination, RW). Do not reveal unrelated mount paths or credentials. Once confirmed, review a *new GitHub pinned script revision* correcting the outdated exact-backing-path guard to match the real workspace host/container ancestry. Do not remove the safety guard, edit the already checksummed script, change/recreate containers or rerun failed backup automatically. No newly created November 23 backup artifacts or new NAS copy have been reported; preserve all historical snapshots. PRODUCTION remains outside scope.

## 2026-11-23 — DEV workspace mount verified; corrected pinned backup script (not yet run)

**Owner read-only runtime result:** Docker container `frappe_docker_devcontainer-frappe-1` has verified RW bind mount **Type=bind, Source=`/home/gani/deployments/frappe_docker`, Destination=`/workspace`, RW=True**. The persistent DEVELOPMENT bench remains one level below, at `/home/gani/deployments/frappe_docker/development/frappe-bench` on the host and `/workspace/development/frappe-bench` in the container. The prior script failed because it required a **direct** bind mount at host `.../development` to container `/workspace/development`; Docker's actual mounted ancestor layout is different. This is not a reason to recreate/reconfigure Docker.

**Reviewed exact two-line guard correction in GitHub:** repo `ccpcerp/ccpc-frappe-deployment`, branch `review/dev-phase1-two-site-backup-2026-11-23`, commit **`c22cdd9c082e1359146ee8b765f84c003e4a354a`**, path `scripts/development/operator/ccpc_dev_phase1_two_site_backup_20261123.sh`. Only constants `DEV_BIND_HOST` and `DEV_BIND_CONTAINER` changed to the verified ancestor **`/home/gani/deployments/frappe_docker`** and **`/workspace`**, respectively. All other guards, backup implementation and non-overwrite NAS SHA-256 behavior are byte-identical. Re-fetch confirmed updated Git blob SHA-1 **`0c00015914afeb87bf55a7994eed9e63713f2ea4`**; full new script SHA-256 **`52461ebb9b3f7b900cf35813b611f358bd22993f3570b2dff9e563b96e03d220`**. SHA-256 hash implementation self-tested against known `abc` vector. Script static Bash/Python syntax remains as previously checked; change is two quoted string literals. Runtime execution unverified.

**Safe continuation within owner's existing one-shot backup/NAS-copy approval:** Stage revised exact GitHub commit into a NEW private filename outside live DEVELOPMENT checkout, not over the original checksum-verified `ccpc_dev_phase1_two_site_backup_20261123.sh`. Verify commit, Git blob SHA-1, full SHA-256 and `bash -n`; then execute once from trusted normal non-root Ubuntu host after guards. Do not modify the original staged file, alter host/docker mounts, bypass checks, auto-rerun, or touch production data/backups. No new local DEV backup or NAS copy has been reported following the earlier stopped guard. Even successful archive and checksum validation cannot prove isolated restore.

## 2026-11-23 — two-site DEVELOPMENT backup and SHA-256 verified Synology copy: PASS

**Owner-supplied actual terminal output, one completed execution on normal non-root Ubuntu host** with script `/home/gani/ccpc-reviewed-scripts/ccpc_dev_phase1_two_site_backup_20261123_v2.sh` (review commit `c22cdd9c082e1359146ee8b765f84c003e4a354a`, SHA-256 `52461ebb9b3f7b900cf35813b611f358bd22993f3570b2dff9e563b96e03d220`): staged script checksum OK, `CORRECTED BACKUP SCRIPT VERIFIED`, `STARTING APPROVED DEVELOPMENT BACKUP`, then `DEVELOPMENT-ONLY TARGET AND NAS GUARDS: PASS`. Site `ccpc-integration2.localhost`: **LOCAL FOUR-COMPONENT BACKUP PASS** and **NAS 4/4 SHA256 PASS**. Site `development.localhost`: **LOCAL FOUR-COMPONENT BACKUP PASS** and **NAS 4/4 SHA256 PASS**. Global **NAS 8/8 CHECKSUM PASS**, **TWO-SITE DEVELOPMENT BACKUP AND NAS COPY: PASS**.

**New, non-overwritten Synology NAS backup folder** (owner reported): `ccpc-development-phase1-20261123T014828Z-ee8c493c7b6bbfc9`. The script reported `RESTORE REHEARSAL: UNVERIFIED` and `NO MIGRATION, SERVICE RESTART, OR PRODUCTION OPERATION PERFORMED`. Treat as owner-reported execution evidence (not independent direct NAS inspection by ChatGPT). Historical backup sets and the older staged script were preserved. The single previously owner-approved guarded two-site backup + NAS-copy operation is **now completed; do not run it again without new authorization/need**.

**Recovery gate:** Four-component local archive and cross-NAS SHA-256 integrity PASS do *not* demonstrate logical database restore success, transactional point-in-time consistency, or usable recovered site. Plan a distinct, explicitly scoped **isolated DEVELOPMENT-only restore rehearsal** using a disposable site/database/volumes and a verified restore target, with non-overwrite and strict PROD exclusion. Verify source NAS manifest and components read-only, restore to isolated target, test login/sites+attachments and a small stock/GL acceptance smoke test, then record evidence/failures. Do not issue a `bench restore` against either persistent DEV site, any PROD site, or a target whose isolation is not verified. Restore/migration/new persistent data mutations need separate explicit owner approval after reviewing safeguards.

**Delivery priority after recovery gate:** Resume actual persistent DEVELOPMENT Withdrawal Slip → Material Issue → SLE/GL/Department consumption acceptance (and agreed day-one reports), recording integration results and any necessary GitHub corrections. No production deployment or migration authorized by successful backup.

## 2026-11-23 — owner approved independent DEV restore rehearsal; runtime target pending

**Owner:** "Approved, were will we test it, in Codex" in response to proposal for isolated DEVELOPMENT restore rehearsal of the 2026-11-23 verified two-site NAS backup. Interpret approval as scoped authorization to prepare and carry out a **safe, independently isolated, disposable DEVELOPMENT-only recovery test**, with a demonstrated disposable target first; NOT blanket permission for privileged host actions, database drops/overwrites, new production connectivity, secret egress, new infrastructure purchases, or destructive cleanup. The *physical target is not yet confirmed*. No restore action has been run.

**Clarification:** Codex CLI is a useful source/code/test assistant, **not a database/container isolation boundary**. Do not run `bench restore` in Codex's nested sandbox or the persistent DEVELOPMENT Frappe bench. Preferred data-local destination: an **independent disposable VM with its own Docker/MariaDB/Redis and new site/database**, no shared Docker daemon with persistent services, no DEV/PROD/NAS write mounts, no original DB endpoints, no outbound email/webhook connections; private copy of the exact backup with hashes checked by the human host operator, confidential site config/DB content never exposed in Codex/GitHub/chat logs. **Candidate only**: historically described Windows Hyper-V private-switch `CCPC-Step136-LAB` had just 4 GiB RAM and no Docker at 2026-10-30 checkpoint, and has **not** been shown to be a capable restoration target today. A fresh local isolated VM with adequate resources would be acceptable after host/resource/network checks. CircleCI is disposable for synthetic integration but requires separate explicit and carefully reviewed third-party data-egress authorization to handle **real backup content**; the old held Oct29 CircleCI/B2 restore workflow is not ready for this new Nov23 set.

**Next gate:** Read-only inventory of available host VM/independent runtime resources and architecture, then prepare a GitHub-reviewed non-overwrite one-shot lab restore runbook pinned to the exact new backup set. Prove isolation and absence of existing target DB/site *before* any restore. Initial acceptance: new disposable site can read the recovered SQL, both attachment classes, its site configuration and representative nonmutating ERPNext records; no migration or persistent DEV changes. Real side-effecting test transactions are a distinct later acceptance task. Preserve historical backups and November 23 NAS folder. Document exact PASS/FAIL and scope of recovery. PRODUCTION never in scope.

## 2026-11-23 — KVM device and virtualization CPU support confirmed for DEV restore VM

**Owner's normal Ubuntu DEVELOPMENT host read-only results:** `ccpcerpserver`; total RAM **29 GiB**, **26 GiB available** at inspection, swap **8 GiB** unused; root filesystem **915 GB**, **683 GB available**; CPU virtualization `vmx|svm` **SUPPORTED**; `/dev/kvm` character device **PRESENT**. Executable probes for `virsh`, `qemu-system-x86_64`, `virt-install`, `multipass`, `VBoxManage` returned **no installed tool path**. This verifies a feasible hardware/storage **candidate**, not a working installed hypervisor or confirmed user access to KVM; no host package installation or VM provisioning has occurred.

**Practical lab choice:** A bounded **independent KVM/QEMU VM on the DEVELOPMENT host**, with its *own* Docker daemon, MariaDB/Redis, guest Frappe/ERPNext bench, unique disposable DB/site/storage and a private guest disk. Initial indicative allocation **8 GiB RAM / 60 GiB disk**, subject to exact Ubuntu version, guest disk capacity, host KVM permissions, package inventory and isolation review. Do not share/bridge existing host Docker socket, persistent DEV DB or mounts, NAS write mount, SSH credentials, or any PRODUCTION route. Default automatically enabled libvirt NAT/bridge services and host networking changes must be reviewed, not assumed safe. Secret-containing Nov23 backup set stays on owner-controlled host/storage and is only copied into proved isolated guest scratch by a reviewed transfer, never into Codex/GitHub/chat/third-party CI.

**Next small read-only host prerequisite:** collect Ubuntu `ID/VERSION_ID` from `/etc/os-release`, `/dev/kvm` type/owner/mode, effective `id -nG`, relevant KVM modules, and whether any libvirt/QEMU tools/packages are already installed; print no environment secrets or host network inventory. Separate explicit owner approval is needed before installing virtualization packages, starting libvirt services/network, or creating a guest. Codex can help with runbook/source review but must not receive real backup credentials or host-wide Docker/libvirt authority. The separately approved **recovery objective** remains in scope, but no restore or VM operation has been executed. Persisted DEVELOPMENT sites and all NAS backups are protected.

## 2026-11-23 — Ubuntu 26.04 KVM access and hypervisor package status: NOT INSTALLED

**Owner's normal non-Codex terminal output:** OS `ubuntu 26.04`; `/dev/kvm` character device **UID 0, GID 992, mode 660**, and user's supplemental groups `gani adm cdrom sudo dip plugdev users lxd docker` (none directly matches a named `kvm` group). `dpkg-query` reports **NOT INSTALLED** for `qemu-system-x86`, `libvirt-daemon-system`, `libvirt-clients`, `virtinst`, `cloud-image-utils`. Earlier `command -v qemu-system-x86_64` also returned nothing. KVM capability and host spare memory/disk were already verified, but the non-root operator cannot yet be assumed to have /dev/kvm access. No virtualization packages, services, bridges, guests or restore commands have been run.

**Next fastest low-impact path, subject to host-change approval:** Prefer minimal standalone **QEMU/KVM** packages (`qemu-system-x86`, `qemu-utils`, `cloud-image-utils`) without installing or automatically starting `libvirt-daemon-system`, networking bridges, VM services or persistent managed virtual networks. Ubuntu 26.04 package catalogue lists QEMU packages; however **local Apt simulation is needed** to verify exact repositories and dependency side effects before host installation. Run read-only `apt-get -s install --no-install-recommends qemu-system-x86 qemu-utils cloud-image-utils` and name `/dev/kvm` group via `getent group 992` (without printing group member identities); review exact output and whether any host packages are removed/upgraded. Do not `apt update`, `sudo apt install`, `usermod`, `chmod /dev/kvm`, launch QEMU, alter routing, or create guest until explicit narrow host permission and runtime isolation review. After install, KVM device group access may require a separately approved exact-group membership change and new login; do not run guest as root just to bypass permissions.

**VM target design:** create a *single* privately owned 8-GiB RAM / 60-GiB disk local VM, no Docker socket, no shared live DEV volume/DB, no NAS mount, no original host credentials, and no production reachability; network isolation plus guest package provisioning must be designed/verified before starting or restoring data. Treat Nov23 SQL/config/attachment archives as confidential and immutable; do not put them in Codex workspace, GitHub, CircleCI, command output or public links. Perform restore only to a fresh independently verified guest-only DB/site, document success and keep original backups. A passed read-only preflight is not restore evidence. The owner-approved restore objective remains, but explicit host package/network/VM creation scope remains pending.

## 2026-11-23 — Ubuntu 26.04 simulated minimal QEMU installation: review passed, installation NOT authorized/executed yet

**Owner's direct normal Ubuntu DEVELOPMENT terminal:** `/dev/kvm` reported **GROUP=kvm, GID=992, MODE=660**. Earlier `gani` group list omitted `kvm`; KVM device use by this operator is **not yet confirmed**. `apt-get -s install --no-install-recommends qemu-system-x86 qemu-utils cloud-image-utils` returned **0 upgraded, 25 newly installed, 0 to remove, and 91 not upgraded**. It selected `qemu-system-x86`, `qemu-utils`, `cloud-image-utils` plus 22 dependencies, including `qemu-system-common`, `qemu-system-data`, `seabios`, `ubuntu-helper-virt-hwe` and `ubuntu-virt`. This is **simulation only**; no package installation, hypervisor activation, VM creation, network setup or backup restore has occurred. The 91 not upgraded are pre-existing pending packages, not upgrades requested by this transaction.

**Next deliberate host-change approval:** Present exact command `sudo apt-get install --no-install-recommends qemu-system-x86 qemu-utils cloud-image-utils` to owner for explicit consent as scoped host package installation; no `apt upgrade`, `apt autoremove`, `libvirt-daemon-system`, VM launch, bridge/NAT changes, `usermod`, `chmod /dev/kvm`, data restore or service restarts requested. Use interactive apt verification, stop if apt's live transaction proposes unreviewed removals/upgrades. After package installation verify selected packages and host service/network state read-only, then separately review KVM access and VM network isolation prior to guest creation. In case system packaging triggers changes beyond the simulation, stop and diagnose before proceeding. The owner-approved **isolated DEV recovery objective** and archival integrity remain, restore itself is still untested. No PRODUCTION operation permitted.

## 2026-11-23 — Owner authorized minimal QEMU package installation (result pending)

Following read-only Ubuntu 26.04 Apt simulation (`0 upgraded, 25 newly installed, 0 to remove, 91 not upgraded`), the owner explicitly replied **"Approved"** to the **exact** host package installation request only: `sudo apt-get install --no-install-recommends qemu-system-x86 qemu-utils cloud-image-utils` on the DEVELOPMENT host `ccpcerpserver`. Command was supplied to the human operator for normal-host manual execution, with interactive comparison against `0 upgraded / 25 new / 0 removed` and instruction to abort if the live transaction differs.

**Do not record installation as completed:** no live Apt result has been provided yet. Approval does **not** extend to `apt upgrade`, removing packages, membership/permission changes, libvirt daemon or bridges, launching a guest VM, modifying Docker or Frappe, touching the two existing DEVELOPMENT sites, copying confidential archives, executing a restore or PRODUCTION. Next: examine operator's final Apt output, then verify installed package state and any host-service side effects read-only before requesting a separate scoped VM/network authorization.

## 2026-11-23 — Owner-reported QEMU installation complete; service enablement and kernel notice

**Operator pasted full normal-host Apt installation output** (184 lines): `sudo apt-get install --no-install-recommends qemu-system-x86 qemu-utils cloud-image-utils` confirmed `0 upgraded, 25 newly installed, 0 to remove, 91 not upgraded`; accepted `Y`; fetched 20.2 MB; all 25 packages selected, unpacked and configured, including the three requested packages; no visible fatal apt/dpkg error. Configuring `qemu-system-common` **created symlink** `/etc/systemd/system/multi-user.target.wants/qemu-kvm.service` to package unit, meaning a service enablement side effect occurred even without `libvirt-daemon-system`; **current service ActiveState not yet checked**. Do not imply the installation made zero service changes.

`needrestart` reported **pending kernel upgrade**: running `7.0.0-38-generic`, installed/expected `7.0.0-43-generic`, and **did not reboot**. It listed service restarts being deferred, including `docker.service`, `dbus.service`, `systemd-logind.service`, etc., said **no containers need to be restarted**, and showed no VM guests with outdated QEMU. This does **not** authorize reboot or Docker restart. Running Docker/DEV container status and actual QEMU service state must be verified, not inferred solely from needrestart output.

**Next read-only one-step verification on trusted Ubuntu host**: check all 3 `dpkg-query` installed package states, `qemu-system-x86_64 --version` first line, `systemctl show qemu-kvm.service -p ActiveState -p SubState -p UnitFileState`, `systemctl is-active docker.service`, `docker inspect --format '{{.State.Running}}' frappe_docker_devcontainer-frappe-1`, `id -nG` and `stat -c '%G %a' /dev/kvm`. Do not restart/disable services as a cleanup, alter kernel/packages, add user to kvm group, launch guest, enable bridges/NAT, or restore NAS backup. Independently isolated VM network and access are yet unproven. All persistent DEVELOPMENT sites and PRODUCTION remain protected.

**Source:** Owner-pasted local apt output, not independently run by ChatGPT; retain output as owner-reported evidence. The explicit package-only approval is now **consumed** for this exact installation; any additional host mutation needs separate scoped authorization.

## 2026-11-23 — Operator verified QEMU installation and persistent DEVELOPMENT continuity

**Owner-provided read-only post-install verification, normal host `ccpcerpserver`:**
- `dpkg-query`: `cloud-image-utils`, `qemu-system-x86`, `qemu-utils` each `install ok installed`.
- QEMU emulator **10.2.1** (`1:10.2.1+ds-1ubuntu3.3`).
- `systemctl show qemu-kvm.service`: `ActiveState=active`, `SubState=exited`, `UnitFileState=enabled`. This service state does not attest a VM is running and alone is not evidence of a fault.
- `systemctl is-active docker.service`: **active**; `docker inspect --format '{{.State.Running}}' frappe_docker_devcontainer-frappe-1`: **true**. No runtime Docker disruption observed in this check.
- `id -nG`: `gani adm cdrom sudo dip plugdev users lxd docker`; `/dev/kvm` group **kvm**, mode **660**, so `gani` does not have normal group-based KVM access. Supplemental access-control-list access not checked; direct KVM access not yet demonstrated.

**Next scoped approval choice:** Recommend `sudo usermod -aG kvm gani` **only with the owner's separate explicit authorization for modifying host user group membership**, preserving all existing groups via `-aG`; then start a fresh login/session and read-only verify `id -nG` plus `test -r /dev/kvm && test -w /dev/kvm`. Do not run `newgrp` automatically in shared shells, `chmod 666 /dev/kvm`, launch VM as root, or grant Codex broad `sudo`/libvirt. This group membership persists across reboots; although user already belongs to `sudo` and `docker`, it remains a discrete host security change. Do not create/run a VM, change networking, copy NAS confidential data, perform restore, or touch PRODUCTION under this approval. VM isolation and guest bootstrap require separately reviewed actions.

**Status:** Packages installed, Docker and persistent DEVELOPMENT site container running; no guest created; no logical restore rehearsal attempted; NAS copies preserved.

## 2026-11-23 — Owner approved gani KVM supplemental group membership (execution pending)

Owner replied **"Approved"** to the narrowly scoped host user group change `sudo usermod -aG kvm gani` on `ccpcerpserver`. Existing verified condition: `/dev/kvm` group `kvm`, mode 660; `gani` was not in `kvm` in the then-active session. Approval **only** covers preserving existing supplemental groups while appending `kvm`; it does **not** authorize `chmod`, running QEMU as root, guest/bridge/NAT/VM creation, DB restore, changing Docker or PRODUCTION.

**Next operator step:** Human runs `sudo usermod -aG kvm gani` on trusted host, then `id -nG gani` to confirm the account's group list contains `kvm`. This is not proof the existing shell received updated groups. Open a fresh normal host login/session and verify `id -nG` includes `kvm` and `test -r /dev/kvm && test -w /dev/kvm` both pass before using KVM. No reboot needed. Do not claim membership is applied until user provides output. Next VM networking/runtime proposal needs separate isolation review and approval. The 2026-11-23 two-site NAS backup remains intact; restore rehearsal not yet executed.

## 2026-11-23 — Owner verified fresh-session gani kvm group membership

Owner pasted the new normal-Ubuntu-terminal `id -nG` output: `gani adm cdrom sudo dip plugdev users lxd kvm docker`. Therefore the owner-approved `sudo usermod -aG kvm gani` group change is reflected in the **active login session**, and prior groups remain listed. This confirms **group membership**, not yet direct device access: `/dev/kvm` is a group-`kvm` mode-`660` character device, but no successful `test -r /dev/kvm && test -w /dev/kvm` result has been supplied yet.

**Immediate next single read-only gate:** user runs `test -r /dev/kvm && test -w /dev/kvm && echo "KVM ACCESS: PASS" || echo "KVM ACCESS: STOP"`. If PASS, prepare an independently isolated QEMU VM specification and review network isolation + package/guest bootstrap before requesting approval to launch a guest. No new VM, host network changes, guest bootstrap, backup content transfer, restore or production operation has been performed or authorized by the group access check.

## 2026-11-23 — Owner reported KVM device-access STOP despite fresh-session group membership

After confirming fresh normal-Ubuntu-terminal `id -nG` contained `kvm` (`gani adm cdrom sudo dip plugdev users lxd kvm docker`), the owner ran the requested read/write access test and reported **`KVM ACCESS: STOP`**. This means at least one of `test -r /dev/kvm` and `test -w /dev/kvm` failed; it does **not** identify whether the device exists, the check was run in a different namespace/session, a permission/ACL issue, or another access boundary. Prior device metadata had `/dev/kvm` as group `kvm`, GID 992, mode 660, but current state has not yet been rechecked.

**Hold the restore-VM path.** Do not `chmod`, `chown`, alter ACLs, grant root/privileged access, change package installations, run QEMU, launch a VM, or access backup content. Next one-step normal host **read-only** diagnostic: print `whoami`, `id -nG`, `ls -l /dev/kvm`, `stat -c 'UID=%u GID=%g MODE=%a TYPE=%F' /dev/kvm`, `test -e/-r/-w /dev/kvm` as individual PASS/STOP lines. Decide on correction only after examining exact evidence; no host modification approved.

## 2026-11-23 — KVM access STOP explained by old active login session

Owner ran exact **read-only** per-session and device diagnostic in normal Ubuntu terminal:
`whoami` = `gani`; `id -nG` = `gani adm cdrom sudo dip plugdev users lxd docker` (**no kvm**); `ls -l /dev/kvm` = `crw-rw---- root kvm`; `stat` = `UID=0 GID=992 MODE=660 TYPE=character special file`; `test -e /dev/kvm` **YES**, `test -r /dev/kvm` **STOP**, `test -w /dev/kvm` **STOP**. Earlier owner pasted a *different terminal's* `id -nG` that included `kvm`, so account membership has apparently been updated but **this failing session retains the old group list**. This entirely explains access denial under normal POSIX group permissions, without indicating host KVM corruption.

**Next minimal safe action:** close/detach current remote SSH/VS Code connection and establish a **genuinely fresh SSH login**, not merely a shell/terminal pane inside the same stale remote process. Run `id -nG`, `id -nG gani`, and `test -r /dev/kvm && test -w /dev/kvm` from the fresh session. Expected fresh-session groups include `kvm` and read/write PASS. No `sudo`, `chmod`, `chown`, `usermod` repeat, service restart, or reboot. If access still fails with fresh `id -nG` containing kvm, investigate ACL/namespace restrictions read-only before any mutation.

**Recovery status:** QEMU packages installed and version verified, persistent DEVELOPMENT Docker/Frappe running as previously checked; no VM created/launched, no restore performed. Nov23 NAS 8/8 SHA-256 backup PASS remains preserved and PRODUCTION untouched.

## 2026-11-23 — New terminal remains without effective kvm group; try nonprivileged sg

Owner reported in a newly opened terminal that `id -nG` (effective current process groups) still returned `gani adm cdrom sudo dip plugdev users lxd docker` **without kvm**, whereas `id -nG gani` (account database groups) returned `gani adm cdrom sudo dip plugdev users lxd kvm docker`. `KVM ACCESS: STOP` again. This is direct evidence that the terminal inherits an **outdated process group set** even though the OS account database has the desired KVM membership. VS Code Remote SSH may reuse an older remote-server process when opening terminal tabs; this is a plausible cause, not yet independently verified. The /dev/kvm device itself was last observed `root:kvm` mode 660.

**Fastest nonmutating check:** From normal Ubuntu shell, run one child command using existing user group authorization: `sg kvm -c 'id -nG; if test -r /dev/kvm && test -w /dev/kvm; then echo "KVM ACCESS: PASS"; else echo "KVM ACCESS: STOP"; fi'`. `sg` runs only the child shell with the effective target group; it does not edit the user account, `/dev/kvm`, service state, or Docker and is not `sudo`. If `sg` is unavailable, prompts unexpectedly, or still fails, STOP for review rather than changing permissions or repeatedly restarting services. A fully separate fresh *external* SSH connection (e.g. Windows PowerShell SSH not via VS Code Remote integrated terminal) is the alternative.

No VM launched, no guest networking, no backup transfer, no restore. Historic NAS copies and both live DEV sites remain protected; no PRODUCTION operations.

## 2026-11-23 — scoped sg kvm child access PASS; QEMU restore VM plan prepared

**Owner terminal evidence:** after previous VS Code/SSH reused-session `id -nG` omitted `kvm`, operator invoked `sg kvm -c 'id -nG; if test -r /dev/kvm && test -w /dev/kvm; then echo "KVM ACCESS: PASS"; else echo "KVM ACCESS: STOP"; fi'`. Output `kvm adm cdrom sudo dip plugdev users lxd docker gani` and **`KVM ACCESS: PASS`**. Thus the host's group-based hardware KVM access is proven in a scoped non-root child shell; no need for chmod/chown, repeated usermod, reboot, Docker restart or running QEMU as root. Normal shell may still have stale groups. QEMU package version 10.2.1 and live DEV Docker were previously verified; no QEMU guest created/launched or restore attempted.

**New verified recovery lab design:** [DEVELOPMENT-20261123-ISOLATED-RESTORE-VM-PLAN.md](DEVELOPMENT-20261123-ISOLATED-RESTORE-VM-PLAN.md), docs branch commit `3a30719c7741ac98c269044ab5e8641f32c08f78`. Plans 8-GiB RAM, 4-vCPU, 60-GiB sparse qcow2 owner-run VM, first boot **QEMU `-nic none`**, no Docker socket/DEV DB/NAS mount, verified Ubuntu LTS cloud image, no lab autostart; later separately reviewed guest dependency ingress and backup restore. External QEMU manual verifies that `-nic none` is needed to override its implicit default NIC. This is a **design only**; guest image, disk, credentials, networking/restore plans and exact commands require further bounded approval. The owner already approved the *restore goal*, **not unreviewed VM creation or network changes**.

**Immediate next:** show owner the proposed offline VM staging scope and request approval once exact host-side non-overwrite script and pinned image integrity procedure are ready. Avoid long setup loops: minimal first test can be isolated guest boot before full Frappe provisioning. No production access, no changing current DEVELOPMENT sites and no fresh backup operation authorized.

## 2026-11-23 — Owner approved private offline Ubuntu image/VM disk staging; reviewed script ready

**Explicit owner approval:** Owner replied "aPPROVED" to exact proposal: on **DEVELOPMENT host `ccpcerpserver` only**, create one new private restore-lab directory, download and verify an **official Ubuntu 24.04 LTS cloud image**, allocate a **new 60-GiB sparse virtual disk**. **This is staging only**, not permission to launch a VM, attach a network, create cloud-init credentials, share/copy confidential DB/NAS backups, create/overwrite databases, restart Docker/services, install packages or touch PRODUCTION. Owner's earlier `sg kvm` child command showed **KVM ACCESS: PASS**; KVM access is not used for staging.

**Reviewed GitHub operator source:** repo `ccpcerp/ccpc-frappe-deployment`, branch `review/dev-restore-vm-staging-2026-11-23`, script `scripts/development/operator/ccpc_dev_restore_vm_stage_20261123.py`. Branch/creation commit **`2fc8c9353a120b8da35426ab9217a913e0328fff`**, Git blob SHA-1 **`fcfb91db4c12d7221103e87cc5c68702b59247b4`**, script SHA-256 **`071e7ad9ef0571e4f64069111c532429c2886cb305e52ff417e011017fdedd36`** (SHA256 implementation cross-checked against known abc vector). Reviewed exact source URL `https://cloud-images.ubuntu.com/releases/noble/release-20261017/ubuntu-24.04-server-cloudimg-amd64.img`; its `SHA256SUMS` and `SHA256SUMS.gpg` from the same dated official release directory; verifies GPG signature against **preinstalled** `/usr/share/keyrings/ubuntu-cloudimage-keyring.gpg` with pinned Ubuntu cloud signing key fingerprint **`D2EB44626FDDC30B513D5BB71A5D6C4C7DB87C81`** (Canonical Ubuntu public image verification guidance). It verifies image hash, QEMU qcow2 format/no backing reference, then creates a new `60G` sparse qcow2 overlay using that read-only image as backing. Unique new private paths `/home/gani/ccpc-restore-labs/ccpc-dev-restore-lab-20261123/`, owner UID1000, directory 0700 and output files 0600. Fail closed on missing packaged keyring, unexpected Git pin/host/user, DEV container not running, inadequate free storage, existing lab, image checksum/signature mismatch, or unexpected QEMU info. **Operator will separately run Python AST syntax preflight on the fetched exact file**. No host VM launch command exists in this script.

**Status:** GitHub file/branch/commit/blob successfully verified in this active conversation. This does **not** prove staging has run on Ubuntu; image availability and local packaged keyring still require operator execution. Human should fetch exact pinned commit with strict SSH, verify blob and script SHA-256, stage to a fresh file in `~/ccpc-reviewed-scripts`, AST parse, and execute **once** from normal host terminal outside Codex. Stop on any error; preserve partial lab files without rerun. No PROD operation. Once staging passes, next review is a separate, explicitly authorized offline guest boot; no network or backup access beforehand.

## 2026-11-23 — Owner verified official signed Ubuntu image and sparse offline VM disk staging PASS

**Owner reported successful exact GitHub-reviewed operator execution on normal Ubuntu DEVELOPMENT host:** staged `/home/gani/ccpc-reviewed-scripts/ccpc_dev_restore_vm_stage_20261123.py` passed SHA-256 verification (`OK`), `PYTHON SYNTAX: PASS`, `REVIEWED VM STAGING SCRIPT: VERIFIED`. Then `OFFICIAL UBUNTU IMAGE SIGNATURE AND SHA256: PASS` and `IMAGE SHA256: 04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94`. Script created private host staging directory `/home/gani/ccpc-restore-labs/ccpc-dev-restore-lab-20261123` and reported `SPARSE VIRTUAL DISK: 60 GiB`; `DEVELOPMENT RESTORE VM STAGING: PASS`; `VM NOT LAUNCHED; NO NETWORK OR BACKUP ACCESS`; `NO DOCKER, SERVICE RESTART, OR PRODUCTION OPERATION`. This is **owner-observed successful staging**, not an independently launched VM, restored DB or external inspect by ChatGPT.

**Pinned operator source:** deployment repo review branch `review/dev-restore-vm-staging-2026-11-23` at `2fc8c9353a120b8da35426ab9217a913e0328fff`, script Git blob `fcfb91db4c12d7221103e87cc5c68702b59247b4`, SHA-256 `071e7ad9ef0571e4f64069111c532429c2886cb305e52ff417e011017fdedd36`. Image cryptographic signing verification/sha matched the script's pinned official Ubuntu cloud-image release source. Original local/ NAS Nov23 four-part DEV archives remain protected.

**Next scoped gate:** Request separate explicit approval for *first bounded OFFLINE VM boot smoke test only*: KVM QEMU as non-root via already verified `sg kvm`, 8 GiB RAM/4 vCPU, exactly staged virtual disk, `-nic none`, no host folder/share/network/Synology/DEV Docker or production access, no ERPNext data or credentials attached. Prefer `-snapshot` so first boot changes are ephemeral, no VM autostart; console only and bounded lifetime with clear operator stop. Before boot, fail-closed read-only check image SHA, disk format/backing relationship, lab ownership and no unexpected existing VM process. Ubuntu cloud images normally need cloud-init seed for actual guest account/login, so initial offline boot without seed is **only a boot smoke test**, not a restored ERPNext or accessible configured guest. Full guest provisioning, any NIC, seed credentials, backup ingress and `bench restore` remain separately gated. No extra QEMU packages, reboot, Docker/network changes or production operations without their own approval.

## 2026-11-23 — Owner approved first 180-second OFFLINE QEMU VM boot; operator script pinned

Owner previously confirmed **staging PASS** on normal host: Ubuntu 24.04 signed cloud image and SHA-256 `04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94`, private `/home/gani/ccpc-restore-labs/ccpc-dev-restore-lab-20261123`, 60-GiB sparse qcow2 overlay, no VM launch/network/backup/production access. Owner then explicitly replied **"Approved"** for a first bounded **offline snapshot-only VM boot**, 8 GiB/4 vCPU using existing staged disk, no network/host folder/backup access. Approval does not cover guest provisioning, cloud-init credentials, enabling networking, restoring SQL, or persistent disk writes.

**Prepared exact review script** on repo `ccpcerp/ccpc-frappe-deployment`, branch `review/dev-restore-vm-staging-2026-11-23`, commit **`ccb8cfc2f1b9b6b16859e60eeb6dd99e1c144bb1`**, path `scripts/development/operator/ccpc_dev_restore_vm_offline_boot_20261123.py`, blob SHA-1 **`ca6e0f864db8da7c7a39ce1d5ce6616dd221e910`**, exact SHA-256 **`4e21b3ce4454f1793d87a11c1ec0d794566e8e92ed4c8b987f06084b9c7890d5`**. Re-fetched and SHA-256 algorithm checked against known abc vector. Checks expected UID1000, current `sg kvm` access, staged image hash/format/overlay backing, exclusive known lab directory contents, available temporary storage and running protected DEVELOPMENT container before starting QEMU. Foreground timeout **180s** plus kill-after **10s**, `-no-user-config -nodefaults -nic none -snapshot -monitor none -display none -serial stdio`. No Docker daemon/socket injection, guest mounts, QEMU networking, guest login credentials or persistent disk writes; console output still needs operator review. A timeout is a bounded stop **not proof the guest booted**.

**Current state:** Script successfully written in GitHub; staged/executed status on Ubuntu **NOT REPORTED YET**. Before running: human fetch exact pinned SHA/blob from GitHub using trusted strict SSH, new file in operator-only folder, compare SHA256, AST parse, then `sg kvm -c 'python3 -B /home/gani/ccpc-reviewed-scripts/ccpc_dev_restore_vm_offline_boot_20261123.py'` once. If error, STOP and do not auto-retry. The [DEV offline VM plan](DEVELOPMENT-20261123-ISOLATED-RESTORE-VM-PLAN.md) was updated at docs commit `7c810584bd31498a0a9fb94b655dc30f63be04e8`. Original 2026-11-23 backup integrity remains 8/8 NAS checksum PASS; restore still UNVERIFIED. Persistent DEVELOPMENT and PRODUCTION untouched by this new approval.

## 2026-11-23 — Owner reports QEMU process active after intended 180s offline boot timeout

After owner fetched and verified the exact reviewed offline boot script, operator pasted output: file SHA-256 OK, `PYTHON SYNTAX PASS`, `OFFLINE BOOT SCRIPT VERIFIED`, `OFFLINE VM BOOT SAFETY PREFLIGHT PASS`, `BOUNDED BOOT WINDOW: 180 SECONDS`, `NO NIC, NO GUEST NETWORK, NO SHARED HOST PATHS`, `GUEST WRITES TEMPORARY; STAGED QCOW2 NOT COMMITTED`, and `--- Guest serial console begins ---`. **No Ubuntu login/boot messages, ending marker, or final QEMU return code have been supplied.**

Owner then ran the suggested second-terminal process list and reported **`QEMU PROCESS ACTIVE — PID=2697588, ELAPSED=14:19`**. This exceeds the reviewed timeout window substantially, so **treat bounded-termination assurance as failed/UNVERIFIED**. Do not claim successful boot; the PID may belong to a distinct command/older process until exact argv/owner is verified. The pinned boot script used `timeout --signal=TERM --kill-after=10s 180s qemu-system-x86_64`, 8 GiB, 4 CPUs, `-nic none`, `-snapshot`, no monitor or external host shares. A foreground QEMU still running 14 minutes after start requires investigation (timeout parent/process tree, session exit, PID identity), not automatic retry.

**Immediate owner safety action**: From a normal non-Codex Ubuntu host terminal, check PID `2697588` is owned by UID1000 and its argv exactly identifies the approved recovery lab, `-nic none`, `-snapshot`, `-monitor none`, and the approved qcow2 disk. If so, send TERM **only to that PID**, with PIDFD identity protection where Python permits; do not kill Docker, service managers, other QEMU processes, or broad process groups, and do not force-kill before verifying response. If PID is already gone, print stopped; if mismatch, STOP without signal and return diagnostics with no secrets. Recheck whether target QEMU process remains after TERM. Preserve staged disk, backup sets, Docker and PRODUCTION. Investigate timeout-child behavior before another boot attempt. **No extra guest/backup/network permissions** are authorized by this diagnostic.

## 2026-11-23 — Correct offline QEMU PID sent SIGTERM; still present after five seconds

In response to anomalous QEMU runtime >14 minutes versus reviewed 180-second timeout, owner ran targeted guard code against PID **2697588**. Exact owner output: **`EXACT APPROVED OFFLINE VM: VERIFIED`**, **`TERMINATION SIGNAL: SENT`**, **`QEMU STILL PRESENT: REPORT FOR REVIEW`**. The command used Linux `pidfd_open`, validated UID 1000, exact recovery VM `-name ccpc-dev-restore-lab-20261123`, exact qcow2 overlay path, `-nic none`, `-monitor none` and `-snapshot`, sent `SIGTERM` **only** to the verified PID, waited five seconds, and checked `kill(pid,0)`. The continued existence can mean active process or zombie awaiting reaping; **do not infer that QEMU is still executing from `kill(pid,0)` alone**. Confirm process state before any additional signal.

**Immediate next step:** exact read-only `ps -p 2697588 -o pid,ppid,stat,etime,comm,args` from trusted normal Ubuntu terminal; request output. If state `Z`, no further kill; if process gone, already exited; if `S/R/D`, inspect specific process and parent/timeout chain, determine safe next targeted action. No blanket kill, no service restarts, Docker/DEV/PROD changes, no VM rerun or backup access. Offline VM boot evidence remains **UNVERIFIED**, time limit behavior **FAILED/UNKNOWN**; guest disk staged image is presumed unchanged by `-snapshot`, but host QEMU termination not yet confirmed.

## 2026-11-23 — QEMU found suspended (STAT Tl), termination pending; bounded stop via PIDFD proposed

Owner read-only `ps -p 2697588 -o pid,ppid,stat,etime,comm,args` output began: `2697588 2697587 Tl 31:09 qemu-system-x86 qemu-system-x86_64 -name ccpc-dev-restore-lab-20261123 -no-user-config -nodefaults -machine ...`. **`T` denotes process stopped/suspended by job control or signal (not a live progressing guest); `l` multithreaded.** Process PID 2697588 was previously UID1000/fully option-verified (`-name`, exact disk, `-snapshot -nic none -monitor none`) and a SIGTERM had been sent, but it remained present. The `T` state plausibly explains inability to handle TERM; parent PID **2697587** may be a similarly stopped GNU `timeout`, explaining why the reviewed 180-second limit did not enforce. **Parent identity/state not yet checked.** Do not mark offline boot PASS.

**Recommended tightly scoped safety action:** Because this is a disposable **`-snapshot`** no-network boot with no real backup, stop the suspended exact QEMU process with SIGKILL only after an immediate new guard of **process UID1000, command name, VM name, exact approved qcow2 path, `-nic none -monitor none -snapshot` and T state**, using PIDFD for signal identity. An immediate targeted SIGKILL should not be confused with graceful guest shutdown; it is appropriate for a frozen disposable smoke test and avoids resuming it with SIGCONT. Read-only inspect parent PID2697587 and child process states after signal, avoid broad `pkill`, group-wide signals, host restarts or killing unrelated services. If process has already exited or does not match exact identity, STOP without any signal. Any zombie state may require parent reaping; do not kill process blindly. Root, Docker, existing DEVELOPMENT DB and NAS backups must remain untouched. GitHub docs should be updated with **actual** owner output before claiming stopped.

## 2026-11-23 — Targeted QEMU SIGKILL succeeded; process state Z confirms guest stopped

Owner ran exactly the approved PIDFD-protected stop diagnostic against **PID 2697588** on the DEVELOPMENT host. Verbatim output:
```
EXACT SUSPENDED TEST VM: VERIFIED
TARGETED FORCED TERMINATION: SENT
REMAINING PROCESS STATE: Z
```
The script again verified UID1000, exact original `qemu-system-x86_64` recovery-lab name and disk path, `-nic none`, `-monitor none`, `-snapshot` and suspended state `T` before SIGKILL. After two seconds, target process state **`Z`**, meaning terminated/zombie awaiting reaping by parent, **not a running VM**. Do not repeat SIGKILL on this zombie; no VM boot PASS or database restore can be claimed. The first QEMU test had previously displayed `--- Guest serial console begins ---` but never provided usable boot success/Ubuntu login evidence. Its intended `timeout 180s` was ineffective for this suspended case (root cause remains to be diagnosed).

**Next safe read-only operator check:** `ps -p 2697587,2697588 -o pid,ppid,stat,etime,comm,args` to examine the specific parent timeout PID and zombie, and optionally `ps -u gani -o pid,ppid,stat,etime,comm,args | grep -E 'qemu-system-x86_64|timeout.*qemu-system-x86_64' | grep -v grep` for independently active QEMU. No broad kill, SIGCONT, service restart, extra disk writes or repeat boot. If the parent is in a stopped state, plan targeted disposal only after separate identity/role verification; do not kill unrelated timeouts. Protected NAS backups untouched, persistent DEV Docker/service/DB unchanged on user evidence, production not accessed. The frozen guest test must not be rerun before the termination pathology and console options are reviewed.

## 2026-11-23 — Confirmed timeout parent T and QEMU child Z; targeted timeout resume proposed

Owner pasted exact trusted Ubuntu host command `ps -p 2697587,2697588 -o pid,ppid,stat,etime,comm,args`:
```
PID    PPID STAT     ELAPSED COMMAND         COMMAND
2697587 2697569 T          49:53 timeout         timeout --signal=TERM --kill-after=10s 180s qemu-system-x86_64 -name ccpc-dev-restore-lab-20...
2697588 2697587 Z          49:53 qemu-system-x86 [qemu-system-x86] <defunct>
```
This **confirms the `timeout` monitor PID2697587 was itself suspended** (`T`) and thus unable to process the approved 180-second wall clock timeout normally; QEMU child PID2697588 is **exited** (`Z`, defunct), not operating any guest. The original stimulus for suspension (SIGSTOP/SIGTSTP/job control/other) has not been independently proven; Python script PID2697569 status is not yet known.

**Proposed next operator command:** PIDFD-guarded **SIGCONT to timeout PID2697587 only**, after checking that it is still a stopped UID1000 `timeout --signal=TERM --kill-after=10s 180s qemu-system-x86_64` command with approved VM name, exact disk, `-nic none`, `-snapshot`, `-monitor none`, and that QEMU child2697588 is still a zombie whose PPid is 2697587. This permits timeout to reap its defunct QEMU child, not to revive the QEMU guest (zombie cannot resume). After SIGCONT run one read-only `ps -p 2697569,2697587,2697588 -o pid,ppid,stat,etime,comm,args` to confirm exact status. Do not signal PID2697569 without its own read-only identity/status verification; do not kill any process groups/other VMs, do not touch Docker/NAS/production, and do not rerun smoke test. If identity or state differs, STOP and request output. If timeout itself becomes Z because parent Python is also stopped, do not claim fully reaped yet.

## 2026-11-23 — Timeout PID 2697587 already exited when targeted SIGCONT was attempted

Following owner-confirmed QEMU PID `2697588` terminated/zombie (`Z`) and GNU `timeout` parent PID `2697587` stopped (`T`) in the earlier `ps` evidence, owner ran the narrowly scoped PIDFD-guarded cleanup command and reported **`TIMEOUT ALREADY EXITED`**. The command raised `ProcessLookupError` from `os.pidfd_open(2697587)` and therefore exited **without issuing SIGCONT or any other signal**. The timeout parent is no longer present at that observation point. The former QEMU child was previously observed as a `Z` process, but **its eventual reaping has not been verified**. Do not infer that other unrelated QEMU processes are absent, nor claim Ubuntu reached login.

**Immediate safe operator check:** run the following read-only process listing from normal DEVELOPMENT host terminal: `ps -p 2697569,2697587,2697588 -o pid,ppid,stat,etime,comm,args`. Absence of PID2697587/2697588 would confirm both target processes gone; PID2697569 (Python) may or may not remain and should be assessed by state before any action. If no process listed and host is stable, close this **aborted/inconclusive boot** as safe process cleanup; root cause of suspended `timeout` and guest serial silence still unresolved. Do **not** relaunch the guest or copy real backups on this basis; plan revised test behavior and obtain new approval if needed. No production, existing DEVELOPMENT, Docker or NAS operations authorized.

## 2026-11-23 — All three offline-boot process IDs absent; cleanup COMPLETE, boot INCONCLUSIVE

**Final read-only operator evidence** from normal `gani@ccpcerpserver`:
```text
$ ps -p 2697569,2697587,2697588 -o pid,ppid,stat,etime,comm,args
    PID    PPID STAT     ELAPSED COMMAND         COMMAND
```
All original target PIDs have **exited and are absent**: Python boot script `2697569`, GNU `timeout` parent `2697587`, QEMU `2697588`. This follows the uniquely verified PIDFD-guarded SIGKILL to the suspended (`T`) `-snapshot -nic none` QEMU, which entered zombie (`Z`), and later natural disappearance of timeout (without SIGCONT). No more signals are warranted for these PIDs. **Process cleanup: PASS.**

**Boot acceptance: INCONCLUSIVE / NO PASS.** The operator saw the reviewed script pass integrity, hardware KVM and offline/temporary-disk preflight and then print `--- Guest serial console begins ---`, but there was **no confirmed guest kernel boot, Ubuntu login, shutdown marker or accurate timeout completion**. Timeout and guest previously had states `T` and `Z` respectively. `T` indicates job-control/signal suspension; accidental Ctrl+Z is one possible cause, **not yet proven**. The original QEMU script should **not** simply be rerun because the expected 180-second bound was not demonstrated effective under suspension and serial console behavior was inconclusive.

**Follow-up design:** review safer out-of-terminal bounded watchdog/console logging, controlled process lifecycle, avoiding inadvertent foreground SIGTSTP, and separately review a uniquely named/owned private serial-output log; preserve `-nic none`, `-snapshot`, exact staged private QCOW2 and rootless `sg kvm`. Obtain separate owner approval for a revised boot test (not the original already consumed approval). Verify protected DEVELOPMENT services still running with **read-only checks** before further host actions. No launch, backup ingress, DB restore, package/service modifications, production operations or broad cleanup authorized. The original Nov23 two-site NAS backup remains cryptographically verified as 8/8 checksum PASS; isolated restore has not happened.

## 2026-11-23 — revised independent offline VM watchdog committed, reviewed, NOT EXECUTED

**Latest owner message:** "Approved" in direct response to the recommendation to **revise** the suspended-QEMU smoke-test procedure with an independent watchdog and private serial log. Previous assistant explicitly said *review the procedure before authorizing another offline test*; treat this as **approval to author/review the revision only**, not launch a VM again. Protected last evidence: `ps -p 2697569,2697587,2697588` returned only heading, confirming all three previous guest-test processes absent. Previous Ubuntu first boot **INCONCLUSIVE**; guest recovery, DB restore **UNVERIFIED**. Host staging PASS (signed image SHA-256 `04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94`), November23 NAS 8/8 SHA256 PASS.

**Prepared versioned revised operator script:** deployment repo review branch `review/dev-restore-vm-staging-2026-11-23` commit **`d7ccb6167d64de3b0c2144ae7436c9f7e3bd0ccc`**, `scripts/development/operator/ccpc_dev_restore_vm_offline_watchdog_20261123.py`. Git blob SHA-1 **`fc87b307ebe7c310fb11eb00b21b911d7c3adf86`**; script SHA-256 **`b4324c08039b223bd9733167e5cc72871941fb3707861524c19374bb1c516fb0`**, verified against GitHub-fetched text and independently tested against local candidate. No second VM boot conducted or authorized yet.

**Review summary:** 8GiB/4vCPU, exact staged 60GiB qcow2, ephemeral `-snapshot`, **`-nic none`**, no host folder/backups/credentials, no guest networking, monitor disabled. Private one-shot `/home/gani/ccpc-restore-labs/ccpc-dev-restore-offline-test2-20261123`, log/status owner-only. Detaches Python supervisor AND 180s GNU timeout+QEMU from original interactive session/job control, independent timeout with 10s grace plus second hard deadline, targeted process-group cleanup on hard limit. Supervisor drains guest console capped at 2MiB and produces status.json flag `guest_boot_confirmed:false` pending independent review. Fail closed on host/user/device, original staged image SHA+disk owner/format/backing/size, RAM/storage margin, DEV Frappe container running and any overlapping lab VM; refuses to overwrite one-shot files. Script Python syntax + controlled mock success/nonzero/log cap tests **PASS**; **not an actual QEMU/Ubuntu/host integration test**. Review documentation at [DEVELOPMENT-20261123-ISOLATED-RESTORE-VM-PLAN.md](DEVELOPMENT-20261123-ISOLATED-RESTORE-VM-PLAN.md), docs branch commit `2ecc6025ddeb918ce376b7776139645655de8575`.

**Immediate gate:** Explain the reviewed change, then seek a **separate explicit owner authorization to execute revised one-shot OFFLINE smoke test**. If approved, use only exact GitHub commit/blob/hash, syntax preflight and `sg kvm` from normal host outside Codex; no existing lab restaging or re-run original script. After test, assess private `status.json`, safe serial lines and process states; never treat timeout alone as boot success. No guest/network changes, backup ingress, ERPNext restore, Docker restart, or production actions.

## 2026-11-23 — Owner approved revised detached OFFLINE QEMU boot execution (pending operator run)

Owner explicitly replied **"Approved"** to the separately requested scope **"executing one revised, offline, temporary VM boot test using this reviewed watchdog"**. This authorizes only a one-shot QEMU Ubuntu cloud image offline smoke test: 8 GiB RAM / 4 vCPUs; exact pre-staged Nov23 private qcow2; `-nic none`, `-snapshot`, `-monitor none`, no host shares, new guest accounts, backup copies, network, Docker changes, PRODUCTION operations, or database restoration. It does **not** authorize persistent VM disk writing/guest provisioning or subsequent reruns. No VM process has been launched by ChatGPT; execution awaits human running the reviewed commands outside Codex on DEVELOPMENT.

**Verified GitHub source before operator handoff:** branch `review/dev-restore-vm-staging-2026-11-23`, HEAD commit `d7ccb6167d64de3b0c2144ae7436c9f7e3bd0ccc`, exact script `scripts/development/operator/ccpc_dev_restore_vm_offline_watchdog_20261123.py`, blob SHA-1 `fc87b307ebe7c310fb11eb00b21b911d7c3adf86`, SHA-256 `b4324c08039b223bd9733167e5cc72871941fb3707861524c19374bb1c516fb0`. Exact script has preflight checks and 180s watchdog/grace/hard limit and writes one-shot private capped console and JSON status `/home/gani/ccpc-restore-labs/ccpc-dev-restore-offline-test2-20261123`. Original aborted test cleanup is complete (PIDs 2697569/2697587/2697588 absent), but Ubuntu guest boot was **INCONCLUSIVE**. Staged official Ubuntu image SHA256 `04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94` was owner-verified.

**Operator step:** fetch exact reviewed GitHub commit/blob with trusted strict hostkey SSH into a newly private temporary repo, verify SHA256, Python AST syntax, confirm `~/ccpc-reviewed-scripts` is private owner 0700, refuse to overwrite `ccpc_dev_restore_vm_offline_watchdog_20261123.py`, then run **once** via `sg kvm -c 'python3 -B /home/gani/ccpc-reviewed-scripts/ccpc_dev_restore_vm_offline_watchdog_20261123.py'` from normal Ubuntu terminal. Launcher should return a supervisor PID and private status/log paths **immediately**; this indicates launch request only, not boot success. User should follow up with a read-only listing of `status.json`, `supervisor.log` and **sanitized** console tail, and `ps` of exact test processes after the watchdog finishes. Do not paste credentials/private backup content. On STOP/error, no automatic rerun or removal of one-shot run folder. If log/JSON absent, inspect supervisor.log before inferring safety; no new VM automatically.

## 2026-11-23 — Revised detached watchdog script verified and launch requested, supervisor PID 2699269

Owner ran pinned revised detached watchdog script (GitHub review branch `review/dev-restore-vm-staging-2026-11-23`, commit `d7ccb6167d64de3b0c2144ae7436c9f7e3bd0ccc`, SHA-256 `b4324c08039b223bd9733167e5cc72871941fb3707861524c19374bb1c516fb0`) from their trusted normal host outside Codex. Owner pasted output:
```text
/home/gani/ccpc-reviewed-scripts/ccpc_dev_restore_vm_offline_watchdog_20261123.py: OK
PYTHON SYNTAX: PASS
REVISED OFFLINE WATCHDOG: VERIFIED
DETACHED OFFLINE VM WATCHDOG: LAUNCH REQUESTED
SUPERVISOR PID: 2699269
PRIVATE SERIAL LOG: /home/gani/ccpc-restore-labs/ccpc-dev-restore-offline-test2-20261123/serial-console.log
PRIVATE STATUS FILE (AFTER TEST): /home/gani/ccpc-restore-labs/ccpc-dev-restore-offline-test2-20261123/status.json
WINDOW: 180s + 10s TERM/KILL GRACE; NOT BOOT PASS
NO NIC / NO HOST SHARES / GUEST WRITES TEMPORARY
DO NOT RELAUNCH OR DELETE ONE-SHOT FILES
```
This verifies reviewed **launcher** path and distinct supervisor PID; **it does not establish detached supervisor actually started QEMU, guest boot success, watchdog clean termination, Docker continuity or database restore**. Runtime artifacts are only visible to the owner on DEVELOPMENT host.

**Immediate one-step read-only verification:** operator inspect `/home/gani/ccpc-restore-labs/ccpc-dev-restore-offline-test2-20261123/status.json` **if present** and private supervisor.log and sanitized serial tail; check `ps -p 2699269 -o pid,ppid,stat,etime,comm,args` and VM-specific QEMU process state without any signal. If status absent, report missing and supervisor state; if error, preserve all files; do not relaunch, kill processes, attach backups, alter network, restart Docker or touch PRODUCTION. Require independent console evidence before declaring Ubuntu boot PASS; `guest_boot_confirmed:false` in script is deliberately unverified.

## 2026-11-23 — Revised detached Ubuntu 24.04 guest kernel and systemd startup verified; watchdog still active at 1:17

Owner provided first **runtime evidence** for the separately authorized revised offline test, following prior GitHub-verified watchdog-launch request PID **2699269**. Read-only inspection returned:
```text
=== SUPERVISOR PROCESS ===
    PID    PPID STAT     ELAPSED COMMAND
2699269       1 Ss         01:17 python3
=== WATCHDOG STATUS ===
STATUS FILE NOT YET PRESENT
=== SUPERVISOR LOG ===
=== UBUNTU BOOT INDICATORS ===
[    0.000000] Linux version 6.8.0-147-generic (... Ubuntu 13.3.0-6ubuntu2~24.04.1) ... #147-Ubuntu ...
[    0.000000] DMI: QEMU Standard PC (Q35 + ICH9, 2009) ...
[    0.665232] GPT: Use GNU Parted to correct GPT errors.
[    2.633881] systemd[1]: systemd 255.4-1ubuntu8.18 running in system mode ...
Welcome to Ubuntu 24.04.5 LTS!
[    2.641774] systemd[1]: Hostname set to <ubuntu>.
Starting grub-initrd-fallback.service - GRUB failed boot detection...
[  OK  ] Finished grub-initrd-fallback.service - GRUB failed boot detection.
```
**Validated user-visible milestone:** actual guest Linux kernel boot + systemd reached Ubuntu 24.04.5 LTS startup banner on serial console, not merely a QEMU launch attempt. Does not yet confirm guest login, a completed login-ready multiuser environment, watchdog status, 180-second shutdown or absence of QEMU afterward. Supervisor `Ss` while only 1:17 elapsed is expected, and `status.json` absent at that observation point does not indicate failure. GPT resize diagnostic and GRUB detection-service name do not alone prove boot failure; do not change staged qcow2 to address these during a smoke test. All original staged images/overlay still expected unchanged under QEMU `-snapshot`.

**Next operator read-only evidence:** re-read the private run `/home/gani/ccpc-restore-labs/ccpc-dev-restore-offline-test2-20261123/status.json` if present; `ps -p 2699269 -o pid,ppid,stat,etime,comm`; check filtered safe boot markers from serial log and `supervisor.log`, report separately QEMU process state. No second launcher invocation, new disk, cloud-init, networking, backup ingress, Docker/DEVELOPMENT DB actions or PRODUCTION operation. If status `TIMEOUT_WINDOW_ELAPSED`, separately verify there is no remaining QEMU/timeout process and inspect final console boot markers before declaring end-to-end smoke test PASS. Restoration remains **UNVERIFIED**.

## 2026-11-23 — Revised detached Ubuntu VM reaches multi-user target and login prompt; watchdog 2:37 still pending

**Owner-provided exact read-only evidence from revised detached offline QEMU test at elapsed 02:37:**
```text
=== FINAL WATCHDOG STATUS ===
STATUS STILL PENDING
=== SUPERVISOR ===
2699269 1 Ss 02:37 python3
=== RECOVERY VM PROCESSES ===
2699271 2699269 Ss 02:37 timeout timeout --signal=TERM --kill-after=10s 180s qemu-system-x86_64 -name ccpc-dev-restore-lab-20261123 ... -nic none -display none -serial stdio -monitor none -snapshot -no-reboot
2699272 2699271 Sl 02:37 qemu-system-x86 qemu-system-x86_64 -name ccpc-dev-restore-lab-20261123 ... -nic none -display none -serial stdio -monitor none -snapshot -no-reboot
=== FINAL UBUNTU BOOT MARKERS ===
[  OK  ] Reached target multi-user.target - Multi-User System.
ubuntu login:
```

**Milestone: Ubuntu 24.04.5 LTS VM guest boot PASS** to `multi-user.target` and `ubuntu login:`, not merely kernel/systemd startup. This is real guest serial evidence from owner's private log. Verified process command line for lab QEMU includes **`-nic none`** and **`-snapshot`**, with no host share or port forwarding flags shown. Supervisor `Ss`, timeout `Ss`, QEMU `Sl`: none were stopped/suspended at 2m37s. **Watchdog completion NOT YET VERIFIED:** elapsed < 180-second window, `status.json` absent as expected, child still running. No proof yet of automatic QEMU termination, process reaping, or final status. Do NOT classify full revised boot+cleanup test as PASS until status file and no QEMU process verified. No backup import, cloud-init configuration, guest network, ERPNext restore or production operation. Staged Nov23 signed Ubuntu qcow2 + NAS 8/8 verified checksum backup preserved.

**Next owner step:** one **read-only**, normal-Ubuntu-terminal command to cat final `/home/gani/ccpc-restore-labs/ccpc-dev-restore-offline-test2-20261123/status.json` if it exists, check supervisor/timeout/QEMU PIDs `2699269,2699271,2699272` and display `supervisor.log` if nonempty. After time threshold reached, expect `TIMEOUT_WINDOW_ELAPSED` and no remaining QEMU/timeout, but do not invent result. If still pending beyond window or odd state, investigate instead of relaunching or sending broad signals.

## 2026-11-23 — Revised isolated Ubuntu boot-and-watchdog shutdown PASS (restore still UNVERIFIED)

**Final verified owner result** from **second detached, offline, temporary-disks-only** QEMU/KVM smoke test on the separate DEVELOPMENT host `ccpcerpserver`, after reviewer-prepared pinned script in branch `review/dev-restore-vm-staging-2026-11-23` at `d7ccb6167d64de3b0c2144ae7436c9f7e3bd0ccc`:
```json
{
  "backup_restore_executed": false,
  "console_bytes_observed": 78790,
  "console_truncated_at_2mib": false,
  "guest_boot_confirmed": false,
  "guest_network": "none",
  "snapshot": true,
  "state": "TIMEOUT_WINDOW_ELAPSED",
  "test": "ccpc-dev-restore-offline-test2-20261123",
  "timeout_returncode": 124
}
```
Owner final `ps -p 2699269,2699271,2699272 -o pid,ppid,stat,etime,comm` showed **only headers**: supervisor, GNU `timeout`, and QEMU original PIDs **all exited**. `supervisor.log` had **NO SUPERVISOR ERRORS RECORDED**. Earlier **actual serial-console** markers included `Welcome to Ubuntu 24.04.5 LTS!`, `[  OK  ] Reached target multi-user.target - Multi-User System.` and `ubuntu login:`, verifying guest OS boot to login. Watchdog's `guest_boot_confirmed:false` means its JSON does not automatically assert boot success; console provides the independent boot evidence.

**Assessment:** first separately authorized isolated VM **boot-and-bounded-shutdown smoke test: PASS** on revised detached watchdog. `timeout_returncode=124` is the expected GNU timeout result, NOT a guest crash by itself. The QEMU invocation was separately shown with `-nic none -snapshot` and no host shares; script's status says `guest_network:none` and `snapshot:true`. This is not proof of active LAN firewall isolation under different future VM arguments; network-off configuration is sufficient for this test. No application restore, guest database, permanent guest identity/provisioning, production transfer or DEV site integration occurred. **Recoverability of Nov23 backup remains UNVERIFIED** despite NAS 8/8 SHA-256 PASS.

**Evidence location:** user-held private `/home/gani/ccpc-restore-labs/ccpc-dev-restore-offline-test2-20261123/status.json`, `serial-console.log` (78,790 bytes observed; not truncated), and empty `supervisor.log`. One-shot logs and 60GiB staged qcow2 MUST remain preserved; do not rerun old test or reset folder. Earlier suspended foreground test was already cleaned up with all old PIDs absent.

**Next stage not yet authorized:** independently plan persistent-but-isolated guest configuration and private guest-only credentials/cloud-init without exposing secrets in GitHub or chat, suitable Frappe/ERPNext versions, and tightly controlled dependency supply that cannot reach existing DEV or PRODUCTION networks. **No guest network, backup copying, DB restore, Docker host actions or production changes without separate explicit approval**. Next verification can be a read-only check of DEVELOPMENT Docker container continuity, lab disk metadata and original NAS artifacts, but avoid unnecessary host probing.

## 2026-11-23 — Owner approves faster reusable recovery workflow; one-time G2 baseline preparation

Owner explicitly approved continuing after successful G1 Ubuntu boot-and-clean-shutdown proof and requested **less strict, faster subsequent recovery tests**. Outcome: **one-time isolated Frappe/ERPNext/CCPC recovery VM baseline**, then reuse via disposable qcow2 overlays for each new backup; never re-download Ubuntu cloud image or rerun G1 180-second smoke test per backup. Timebox each repeat to cryptographic source integrity, four-component DB/config/public/private restore into a guest-only site, read-only verification of apps/schema/docs/files, and concise PASS/FAIL; avoid endless preparatory checks or approval churn.

**Authoritative streamlined plan** now appended to [DEVELOPMENT-20261123-ISOLATED-RESTORE-VM-PLAN.md](DEVELOPMENT-20261123-ISOLATED-RESTORE-VM-PLAN.md) at docs commit `5f8e63acad49539ae5383ac0f41907a60ba03abd`. G1 earlier **PASS** was real Ubuntu `multi-user.target` + `login:` and detached watchdog's `TIMEOUT_WINDOW_ELAPSED`/no remaining processes. Nov23 NAS 8/8 checksum PASS remains **NOT** a real restore test.

**Immediate one safe step:** obtain actual running DEVELOPMENT bench app versions and exact Frappe/ERPNext/CCPC commits using only **read-only** `docker exec frappe_docker_devcontainer-frappe-1 bash -lc 'cd /workspace/development/frappe-bench; bench version; for app in frappe erpnext ccpcerp; do git -C apps/$app rev-parse HEAD; done'`. This does not connect to any DB, install anything, or reveal credentials. Once pinned, prepare **one** guest bootstrap with private cloud-init login, guest-only MariaDB/Redis and version-compatible Frappe/ERPNext/ccpcerp, then save baseline for repeated snapshot overlays.

**Approval boundary:** Owner's G2 approval authorizes one-time guest setup *planning/read-only version inspection* and standing preference for normal low-risk steps without repetitive prompts. It does **not** authorize unspecified host firewall/port changes, unrestricted guest Internet routing or live DEVELOPMENT/PRODUCTION DB edits. Consolidate subsequent significant network/backup import/first guest restore into **one clearly scoped approval** after exact method documented, rather than individual per-command approvals. Real confidential SQL/config/files stay on owner-controlled host/guest, not GitHub/Codex/public CI. PRODUCTION categorically excluded.

## 2026-11-23 — Running DEV source pins verified; reusable VM guest baseline staging script ready

**Owner read-only Docker/bench output from live DEVELOPMENT `frappe_docker_devcontainer-frappe-1`:**
```text
ccpcerp 0.0.1 HEAD (b0cbe5c)
erpnext 16.34.2 version-16 (4048fb7)
frappe 16.33.1 version-16 (988e54f)
frappe: 988e54f3c4c291e2077a83809663f123731abe76
erpnext: 4048fb70e14d1843956fcdabb7c3cca75a1cbcdd
ccpcerp: b0cbe5c13cb68499a7920de2879f65e72cff000a
```
The matching custom app `ccpcerp` release source HEAD was separately checked in GitHub. **Pin these exact app revisions** in any reusable recovery environment for the Nov23 backup.

**Owner preference (explicit):** recovery tests should be fast and reusable, without repeated image downloads, approval ceremonies or install loops. A one-time guest-only baseline setup is already approved for planning and non-disruptive staging, but any route from the guest to sensitive DEV/PROD/NAS, first import of actual private SQL/config/attachments, or material host changes still require a specific bounded review.

**New reviewed one-shot stage script on GitHub:** `ccpcerp/ccpc-frappe-deployment`, review branch `review/dev-restore-vm-staging-2026-11-23`, at commit **`e69ceb9c15e680f15b9ad134f78b4c9a624d20c5`**, path `scripts/development/operator/ccpc_dev_recovery_baseline_seed_20261123.py`, blob `fc2b4efdbe1c51c7d840c22d10ce155797006c55`, SHA-256 `57ed6745a32fdf0fe8576bca2e38960df3cefd95acb52c73a6accfa06afb5860` (refetched/sha-selftested). Creates guest-only **new** 60GiB persistent qcow2 backing existing verified image and offline `cloud-init` NoCloud seed with user `ccpc-restore` and random serial-console password stored **only** in 0600 private local operator file. Does not start QEMU or enable guest/host network, install packages, read actual NAS archives or alter active DEV/PROD, and refuses duplicate output folder. Syntax AST must be checked on exact operator-fetched source before execution. User has **NOT YET RUN** the script; staging result remains unverified. User must not post local secret password or cloud-init user-data.

**Documentation:** updated reusable lab plan at docs commit `4db745033c7b11d2daea2144113bf6e6eef1af8b`. Current official Frappe v16 guidance expects modern MariaDB/Python/Node toolchain, but do not assume these docs prove the already-running DEV container's dependency versions. Avoid unnecessary version polling: target exact pinned app commits, install guest dependencies once, and use reusable qcow2 clones in later tests.

**Immediate operator step:** fetch GitHub source pinned by commit/blob/SHA256 into `~/ccpc-reviewed-scripts`, AST parse, run once outside Codex as gani. Next is guest-only version-compatible Frappe bootstrap/first persistent guest boot, not an automatic repeat of the already completed G1 Ubuntu smoke test. Confidential backup restore still PENDING. The Nov23 NAS backup 8/8 SHA256 PASS remains intact and unchanged on existing owner evidence.

## 2026-11-23 — User verifies guest baseline disk and seed PASS; persistent no-NIC QEMU controls pinned

**Owner reported exact one-shot staging result:** `ccpc_dev_recovery_baseline_seed_20261123.py: OK`; `PYTHON SYNTAX: PASS`; `RECOVERY BASELINE DISK + OFFLINE CLOUD-INIT SEED: STAGED`; private `/home/gani/ccpc-restore-labs/ccpc-dev-recovery-baseline-20261123`; `GUEST USER: ccpc-restore`, password **only** in local 0600 file; source signed Ubuntu image, original guest qcow2, previous smoke-test logs all preserved; no VM launched, guest network, backup access, Docker/DB/service/prod modification.

**Exact application source** already read-only verified in running DEVELOPMENT: Frappe v16.33.1 `988e54f3c4c291e2077a83809663f123731abe76`; ERPNext v16.34.2 `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`; CCPC v0.0.1 `b0cbe5c13cb68499a7920de2879f65e72cff000a`. This is a *match target* for one-time guest bootstrap, not proof guest installed.

**Prepared reviewed dedicated guest control script:** `ccpcerp/ccpc-frappe-deployment` branch `review/dev-restore-vm-staging-2026-11-23`, commit `23b5f6fbd35bcdfef6d3de8aaa57e4bc5f80d723`, path `scripts/development/operator/ccpc_dev_recovery_guest_control_20261123.py`, Git blob `eaca6226e8304aa521700ef33edb0991895b63b3`, SHA-256 `32b774611639d18e9007cfbb6837db698e8ec5dede60ff96e53cdf75544afefb` (GitHub-fetched hash, JS hash helper self-tested with standard `abc` vector). **Not executed yet.** Operator must independently fetch reviewed file, check commit/blob/sha and AST. It implements **one-time `--start`** of the *new guest-only persistent qcow2 overlay* (NOT the original signed image/original smoke-test overlay), and subsequent `--status`, `--console`, `--shutdown` commands via private Unix serial/QMP sockets. Non-root QEMU uses verified `sg kvm` and exact owner 0700 runtime directory. No network `-nic none`, no host shares/hostfwd, no production, no backup ingress, no Docker socket access. **Important: QEMU launch is PERSISTENT (no `-snapshot`) and may run beyond terminal lifetime, with 8GiB RAM and 4 virtual CPUs reserved until `--shutdown`**. This is intended only to initialize reusable guest. Preserve original backups and previous two test-log bundles.

**Next operator step:** fetch pinned script into private `~/ccpc-reviewed-scripts`, Python AST preflight, then one `sg kvm -c 'python3 -B ... --start'` in normal Ubuntu terminal, outside Codex. Do not rerun script if it reports `STOP`/one-shot folder exists. After report, attach `--console` to cloud-init guest, login with local protected guest password **never pasted into ChatGPT/GitHub**, confirm `ccpc-restore` account and OS. Guest dependency provisioning and confidential Nov23 backup ingress **remain pending** and require separate exact verified method. Speed preference: install guest recovery app stack **once**, then disposable overlays per future backup; avoid repeating smoke tests/reinstall.
**Plan docs** updated and verified at commit `0b6a97a96e06bbd1fbad8167e17a58335456d78a`.

## 2026-11-23 — Persistent guest VM requested and QEMU PID 2701670 reported; login pending

Owner ran the exact pinned reviewed `ccpc_dev_recovery_guest_control_20261123.py --start` script on normal trusted `gani@ccpcerpserver` host via `sg kvm`. Terminal output:
```text
/home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_guest_control_20261123.py: OK
PYTHON SYNTAX: PASS
PERSISTENT GUEST CONTROL: VERIFIED
PERSISTENT GUEST START: REQUESTED; QEMU PID: 2701670
NETWORK: NONE; BACKUP TRANSFER: NONE
PERSISTENT GUEST DISK: /home/gani/ccpc-restore-labs/ccpc-dev-recovery-baseline-20261123/ubuntu-recovery-baseline.qcow2
GUEST LOGIN: ccpc-restore (password in private host-only file)
CONSOLE: python3 -B <this-script> --console
SHUTDOWN: python3 -B <this-script> --shutdown
NO DOCKER / DEVELOPMENT DB / PRODUCTION OPERATION
```
**Verified status:** reviewed file SHA256 and AST PASS on owner's machine; QEMU launch requested and virtual machine process assigned PID **2701670**; separate guest disk and private guest seed were previously owner-verified staged; QEMU controlled via Unix sockets with `-nic none` and no backups/host mounts. **Do not yet report guest cloud-init success, login, running app stack, backup recovery, or shutdown** without new operator evidence. The QEMU process may run across SSH disconnect until manual guest ACPI shutdown; 8 GiB RAM and four vCPUs budgeted.

**Next action (normal host outside Codex):** `python3 -B /home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_guest_control_20261123.py --status` if needing read-only state, then `python3 -B /home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_guest_control_20261123.py --console` in interactive terminal to reach `ccpc-recovery login:`. Username `ccpc-restore`, password stored only in local private file `/home/gani/ccpc-restore-labs/ccpc-dev-recovery-baseline-20261123/guest-console-password.txt` mode0600. **Do not disclose password, its hash, user-data or credentials in GitHub, tools, shared logs or ChatGPT**. Console exits with Ctrl+] without stopping VM; ACPI `--shutdown` only on actual owner request. If console rejects password/cloud-init failed, review sanitized outputs; never reboot/recreate host or touch live DEV/PROD.

Next: guest-only one-time package provisioning and matched app revisions: Frappe 16.33.1 `988e54f3c4c291e2077a83809663f123731abe76`; ERPNext 16.34.2 `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`; CCPC 0.0.1 `b0cbe5c13cb68499a7920de2879f65e72cff000a`. Preserve the clean baseline for reuse, limit any temporary provisioning connectivity, and do not access November23 NAS backup until carefully scoped guest import and restore plan. User's explicit preference: fast, repeatable backup tests without repeated long staging approval loops.

## 2026-11-23 — Persistent recovery guest interactive login PASS

Owner confirmed an interactive Ubuntu serial console **`ccpc-restore@ccpc-recovery:~$`** after prior `ccpc-recovery login:` prompt on the separate persistent guest (QEMU startup PID 2701670, guest-only qcow2, no NIC). **Guest account console login PASS**; no private credential was shared. The guest OS details and preinstalled dependency inventory are **PENDING**; no Frappe/ERPNext/ccpcerp or MariaDB setup, backup transfer, restore, guest networking or host/prod changes have yet been verified. The next owner action is one read-only guest shell command reporting `whoami`, hostname, `/etc/os-release`, `free -h`, `df -h /`, and presence of python3/node/npm/yarn/mariadb/redis-server/docker/bench/git. The preferred next stage is one-time application/runtime provisioning followed by fast disposable per-backup overlays—never repeat G1 boot smoke tests or official cloud image download. Guest stays running unless explicitly shut down with the reviewed VM controller; persistent guest qcow2 is not yet a clean provisioned ERPNext baseline.

## 2026-11-23 — Persistent recovery guest resource inventory PASS; assess offline image-reuse shortcut

Owner ran read-only guest inventory at `ccpc-restore@ccpc-recovery:~$`:
```text
whoami = ccpc-restore
hostname = ccpc-recovery
PRETTY_NAME="Ubuntu 24.04.5 LTS"
Mem: total 7.8Gi, used 395Mi, available 7.4Gi; Swap 0B
/dev/vda1: size 58G, used 1.7G, avail 56G, use 3%
python3: INSTALLED; git: INSTALLED
node, npm, yarn, mariadb, redis-server, docker, bench: NOT INSTALLED
```
**Verified:** private Ubuntu persistent guest boots and logs in, with 56GiB guest free disk; **no Frappe/ERPNext/CCPC application yet**. Guest explicitly has **no NIC**; running `apt install` or remote `bench init` would be unproductive without dependency ingress.

**Fast-path candidate before seeking guest networking authorization:** The deployment repo's current `images/custom/Containerfile` constructs Frappe images with Python `3.14.2`, Node `24.13.0`, Bench, Yarn, and many dependencies (declared default build args, not proof exact running container was built with those args). Host's existing `frappe_docker_devcontainer-frappe-1` was previously confirmed to have exactly Frappe 16.33.1, ERPNext 16.34.2, CCPC 0.0.1 and exact Git SHA pins. Determine if exact matching **DEVELOPMENT app image plus MariaDB and Redis images** already exist in owner-host Docker cache, then compare low-impact **offline OCI/Docker image export into an owner-controlled private guest-only volume** against needing guest outbound Internet. No export, external transfer or host Docker change authorized by this read-only inventory. Do not ever export running container rootfs/mounted volumes, SQL, config, NAS credentials, Docker socket or host SSH keys as part of an image bundle. `docker image save` of verified immutable images alone (once approved) excludes writable container filesystem and mounted data, but still audit image for build-time secrets before any transfer. Do not place image archives or source data on GitHub/CircleCI. For guest runtime Docker binaries, would need reviewed one-time offline install or a narrowly scoped empty-guest provisioning network.

**Immediate read-only DEVELOPMENT-host image inventory:** 
```bash
echo "=== DEVELOPMENT CONTAINER IMAGE ==="
docker inspect --format 'container_image_tag={{.Config.Image}} container_image_id={{.Image}}' frappe_docker_devcontainer-frappe-1
echo "=== LIKELY LOCAL DEPENDENCY IMAGES ==="
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}  {{.Size}}' | grep -Ei 'frappe|erpnext|ccpc|mariadb|redis|valkey' | head -n 35 || true
echo "=== DEV CONTAINER NAME/IMAGE ==="
docker ps --filter 'name=frappe_docker_devcontainer' --format '{{.Names}}  {{.Image}}'
```
Do not run docker save or export until image identities reviewed; preserve running DEVELOPMENT. Goal remains one-time guest stack, then fast disposable COW clones for repeat restore tests, with no default guest networking and no production changes.

## 2026-11-23 — DEVELOPMENT Docker image cache inventory confirmed; check source mounts before offline reuse

Owner provided read-only Docker inventory from DEVELOPMENT host `ccpcerpserver`:
```text
frappe_docker_devcontainer-frappe-1
  tag=vsc-frappe_docker-44f2900ffde10b6c7c15314ded07ccf4b223413d5596194fe5e2842bc75bc1cf-uid
  image ID=sha256:58db4c81ad96bfa10f37b2cac2f507cd42258db872f5f321875f2438c96953f7
local vsc-frappe_docker...-uid:latest = 58db4c81ad96 ~3.82GB
local ccpcerp:v16.50.0 = 4580454f7c43 ~4.11GB
local ccpcerp:v16.34.0 = 559c36478e9a ~3.82GB
other ccpcerp:v16.28.0 through :v16.49.0 listed ~3.82GB
local mariadb:11.8 = efb4959ef2c8 ~470MB
local redis:alpine = 9d317178ecea ~155MB
local redis:7-alpine = 7f7d30b7fdd0 ~58.5MB
local redis:8.6-alpine = 2cc044fc5a07 ~134MB
live MariaDB container = frappe_docker_devcontainer-mariadb-1 (mariadb:11.8)
live Redis containers = frappe_docker_devcontainer-redis-cache-1 and -redis-queue-1 (redis:alpine)
```
**Meaning:** matched dependency Docker images **exist in host cache**, but **not yet verified suitable** for isolated guest. The active development image's `vsc-` tag may contain tooling rather than bundled app code, which may instead be bind-mounted from host VS Code workspace; **do not assume `docker image save` includes actual Frappe/ERPNext/ccpcerp apps**. Nor does `ccpcerp:v16.34.0` tag alone prove it contains the exact current Frappe `988e54f3c4c291e2077a83809663f123731abe76`, ERPNext `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd` and CCPC `b0cbe5c13cb68499a7920de2879f65e72cff000a`. Do not export images yet; no guest Docker executable is installed, and guest NIC is disabled. Exporting full live containers, filesystems, guest configs, secrets and NAS backups is out of scope.

**Fastest verified next *read-only* check on host:** inspect only container mount destination/type and immutable image metadata (without printing ENV, source mount paths or private data):
```bash
docker inspect --format '{{range .Mounts}}{{printf "%s %s\n" .Type .Destination}}{{end}}' frappe_docker_devcontainer-frappe-1
docker image inspect sha256:58db4c81ad96bfa10f37b2cac2f507cd42258db872f5f321875f2438c96953f7 --format 'image_id={{.Id}} workdir={{.Config.WorkingDir}}'
```
If app code resides only on mounted workspace and not in image, prefer reviewed fully-built `ccpcerp` image matching all revision pins (verified by guest-only environment inspection) or build image once in isolated context. Then arrange one bounded dependency/engine transfer path for the *empty guest*, freeze clean baseline and use disposable qcow2 clone per backup. Preserve the already running no-NIC persistent guest, never rerun old G1 staging, do not attach guest network/NAS or change host/PROD.

## 2026-11-23 — Live development app sources are bind-mounted; select self-contained image via offline disposable inspection

Owner ran read-only `docker inspect` and reported:
```text
=== DEVELOPMENT CONTAINER MOUNTS ===
bind /home/frappe/.ssh
volume /vscode
bind /workspace
=== DEVELOPMENT IMAGE METADATA ===
image_id=sha256:58db4c81ad96bfa10f37b2cac2f507cd42258db872f5f321875f2438c96953f7 workdir=/home/frappe
```
Thus the active VS Code development container **uses external bind mounts**, including **`/workspace` where live application code was verified** and **`/home/frappe/.ssh` which must never be transferred**. Do not package/export a running container or claim that saving its base image captures the active code or credentials (the base image alone would omit mounted paths). No change to the host, live DB, credentials or guest has occurred in this inspection. This supersedes the earlier candidate inference that exporting the `vsc-frappe_docker...` image would provide full app code.

**GitHub source inspection:** `images/custom/Containerfile` on branch `review/dev-restore-vm-staging-2026-11-23` builds a complete `/home/frappe/frappe-bench` in its builder, verifies `EXPECTED_FRAPPE_SHA`, `EXPECTED_ERPNEXT_SHA`, `EXPECTED_CCPC_SHA` at build time, then **removes all `.git` folders** and copies the bench into the final backend image. Consequently, local `ccpcerp:v16.34.0` (~3.82GB) and `ccpcerp:v16.50.0` (~4.11GB) are *potentially reusable complete app images*, but **their tags/size alone do not establish their actual app versions or SHA pins**. Image history/git metadata may be absent. Any necessary Frappe/ERPNext/CCPC image verification should use immutable source/build attestation and read-only app version checks before doing an offline export; note Docker images often define anonymous `VOLUME` locations, which `--rm` cleans up.

**Immediate owner-host next operation (low-impact, disposable, no guest networking or secret access):** inspect `ccpcerp:v16.34.0` and `ccpcerp:v16.50.0` via `docker run --rm --network none --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 --memory 768m --entrypoint /bin/sh` (no host mounts, no Docker socket and no published ports). Read only app folder presence and `bench version`, if available. No image save, database/volume mount, backup ingress, Docker restart or PRODUCTION changes. If versions match Nov23, plan one-time guest Docker runtime setup and sealed image transfer. If not, build/pin suitable image once using verified app refs, then reuse a guest baseline. Live DEV currently remains Frappe 16.33.1 `988e54f3...`, ERPNext 16.34.2 `4048fb70...`, CCPC 0.0.1 `b0cbe5c...`; restore compatibility not yet proved.

## 2026-11-23 — Offline disposable image check confirms matching app versions in ccpcerp:v16.50.0

Owner ran the reviewed local-image check with **ephemeral** `docker run --rm --network none --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges`, no volume/host shares:
```text
=== CHECKING ccpcerp:v16.34.0 ===
frappe: PRESENT
erpnext: PRESENT
ccpcerp: PRESENT
ccpcerp 0.0.1  ()
erpnext 16.29.0  ()
frappe 16.28.0  ()
=== CHECKING ccpcerp:v16.50.0 ===
frappe: PRESENT
erpnext: PRESENT
ccpcerp: PRESENT
ccpcerp 0.0.1  ()
erpnext 16.34.2  ()
frappe 16.33.1  ()
```

**Decision:** `ccpcerp:v16.34.0` NOT SUITABLE for Nov23 restore; `ccpcerp:v16.50.0` **VERSION-MATCHING CANDIDATE** for guest-only recovery baseline. It contains all three app directories and matches the reported versions installed in live DEV (**Frappe 16.33.1, ERPNext 16.34.2, CCPC 0.0.1**). The `()` display is not Git HEAD evidence: build stage removes `.git`. The exact DEV commits pinned as Frappe `988e54f3c4c291e2077a83809663f123731abe76`, ERPNext `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`, CCPC `b0cbe5c13cb68499a7920de2879f65e72cff000a`; build provenance and any ERPNext patch **not yet independently verified for image `v16.50.0`**. Do NOT claim recoverability or exact source parity until a guest restore test. Do not use the active VS Code `vsc-...` image as a stand-in: Frappe apps are bind-mounted via `/workspace` and host SSH path `/home/frappe/.ssh` is also a bind mount.

**Next shortest read-only provenance check on DEVELOPMENT host:** `docker image inspect ccpcerp:v16.50.0` formatted to print only image ID/creation date/architecture/revision label, and `docker history --no-trunc` filtered to show **only SHA-1 pins** matching `EXPECTED_(FRAPPE|ERPNEXT|CCPC)_SHA=[0-9a-f]{40}` if present. Do NOT dump unrestricted image history/ENV/secrets in chat. This check may not expose pins; absent labels != invalid image. If no attestation, use the version-matching candidate on a **disposable guest restore** while clearly recording patch/revision uncertainty, or obtain audited image rebuild once. No export or guest package install authorized in this read-only step.

**Guest remains** persistent Ubuntu 24.04.5 `ccpc-restore`, 7.8Gi RAM, 56Gi free, no NIC, no Docker/MariaDB/Redis. One-time offline dependency/Docker engine image-ingress strategy remains unimplemented. Avoid repeat image download or VM boot tests; favor one bounded guest bootstrap and fast overlay-based per-backup tests. No production or actual private backup import.

## 2026-11-23 — Selected image older than mandatory Nov22 CCPC commit; version match is not code match

Owner supplied exact **read-only local Docker image metadata** for selected candidate:
```text
=== SELECTED RECOVERY IMAGE ===
ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8
CREATED=2026-09-16T15:55:49.950715082+08:00
ARCH=amd64
=== SOURCE REVISION LABEL ===
no revision label
=== BUILD COMMIT REFERENCES ===
<none printed>
```

**New critical provenance finding:** Connected GitHub confirms the required installed custom-app release commit **`b0cbe5c13cb68499a7920de2879f65e72cff000a` was committed November 22, 2026, at 06:08:19 UTC** (merge PR #41). Therefore, the reported image created **September 16, 2026** **cannot include that required Nov22 commit as-built**, despite exact `bench version` strings (Frappe 16.33.1/ERPNext 16.34.2/CCPC 0.0.1). **Do not promote `ccpcerp:v16.50.0` to a version-accurate clean Nov23 recovery baseline as-is.** The `0.0.1` custom app version is non-discriminating; labels/history are absent. The image may still serve as a **runtime/dependency base** after precise latest-app source overlay, or a **new image** may be built once at exact pinned Git commits. Prefer one-time build/overlay over redoing all dependency installation each backup. Exclude `ccpcerp:v16.34.0`: it has Frappe v16.28.0, ERPNext v16.29.0.

**Short critical path decision for operator:** prepare one reusable Frappe 16.33.1/ERPNext 16.34.2/CCPC Nov22 `b0cbe5c` **code-correct image** (using existing GitHub `images/custom/Containerfile` expected-SHA guard or audited source code overlay) on DEVELOPMENT host, confirm that no secrets/volumes from existing live DEV are packaged, then install a guest-only Docker engine and import vetted images into offline 24.04.5 guest. Existing `mariadb:11.8` and `redis:alpine` can be reused. Keep no guest network with confidential data; if temporary guest provisioning NIC is needed, seek one bounded approval and disconnect it before backup ingress. The currently running guest is still only a bare Ubuntu VM, 7.8Gi RAM/56Gi free, no guest DB/Redis/Docker/Frappe installed. No real backup has been restored; NAS 8/8 source checksum PASS remains unaffected. Owner's preference is quick repeatable recovery tests, not further serial metadata-only checks.

**One-time authorization limit:** earlier guest-only baseline setup approved, but a substantial new host Docker build/network change, first private backup copy/restore or any production operation is not implicitly approved. One explicit combined scope is preferable to per-command approvals. No SSH key/secret in guest, GitHub, or ChatGPT. The development `vsc-` image is invalid as complete app source since `/workspace` and `/home/frappe/.ssh` are externally bind-mounted.

## 2026-11-23 — One-time recovery environment setup approved; exact-source Docker image build helper ready, not executed

Owner explicitly approved a combined one-time recovery environment setup on the separate DEVELOPMENT recovery VM, including new **local recovery-only application image** and guest Docker/MariaDB/Redis runtime. No confidential backup copy/restore, live DEVELOPMENT MariaDB or PRODUCTION operation, or unrestricted guest LAN. User requests rapid repeatable restore tests with one provisioned guest and disposable COW overlays.

**Image provenance correction:** local candidate `ccpcerp:v16.50.0` image `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8` was built **2026-09-16**, no revision label/history SHA, although app versions match DEV. GitHub release commit `b0cbe5c13cb68499a7920de2879f65e72cff000a` was authored/committed **2026-11-22** and is the true Nov23 DEV source, so old image cannot contain exact custom-app source as originally built. Do not use old image as exact-source restore baseline.

**GitHub code implementation complete, host work pending:** review branch `review/dev-restore-vm-staging-2026-11-23` commit **`78b9c4c99330d6d6b97a6e6a4ff0ce8a8c371261`**, new reviewed script `scripts/development/operator/ccpc_dev_recovery_image_build_20261123.sh`, blob `818df55a056634ff20b84046f074929f80db5b45`, source SHA256 `8d60739f1d2b681b33598f8b6dd3443c9e5e03766c7272b7ba4543ec05fd47be` (GitHub refetched, hash-selftested). It uses a NEW private build context rather than a dirty DEV checkout, pinned existing `images/custom/Containerfile` at deployment commit `23b5f6fbd35bcdfef6d3de8aaa57e4bc5f80d723`, BuildKit secret SSH/known_hosts and private temp apps.json branch `release/withdrawal-department-phase1-2026-11-17` (GitHub-verified HEAD b0cbe5c), and enforces exact Frappe 988e54f, ERPNext 4048fb7, CCPC b0cbe5c, CCPC ERPNext patch+overlay SHA in the existing Dockerfile. Target image `ccpc-recovery:dev-nov23-b0cbe5c`. Source checksum and AST/bash syntax **not yet checked by operator**, no image build run or loaded yet. Image builder may use approved host network/CPU, no deployment or host/guest DB modification, no volumes or secret files copied to image. Private log under `/home/gani/ccpc-restore-labs/ccpc-recovery-image-build-20261123/build.log`, output validated with ephemeral `--network none --read-only` container.

**Next human operator step:** fetch exact script with pinned GitHub commit/blob/hash, `bash -n`, run once as `gani` on `ccpcerpserver` outside Codex (not root). If failure STOP, preserve image/build log, share sanitized last error only. Do not remove/switch current Docker images, restart Docker, change live DEVELOPMENT/PRODUCTION or rerun on same run folder automatically. After image build PASS, complete once-only offline media transfer and guest runtime setup without guest LAN and freeze clean baseline; no actual backup ingress authorized. Docs plan at commit `1d092b619b1dcf6a35b35d803641024e9b1af7d3`. The running persistent guest is Ubuntu 24.04.5 login-capable, 7.8Gi memory, 56Gi free, no NIC, no Docker.

## 2026-11-23 — Exact-Nov23 CCPC recovery Docker image BUILD PASS, local ID f53cc9ee

Owner executed GitHub-pinned shell helper `ccpc_dev_recovery_image_build_20261123.sh` **on normal `gani@ccpcerpserver`, outside Codex**, with SHA-256, Git blob and `bash -n` preflight. Owner's final terminal output:

```text
/home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_image_build_20261123.sh: OK
RECOVERY IMAGE BUILD SCRIPT: VERIFIED
RECOVERY IMAGE: fetching reviewed deployment source privately
RECOVERY IMAGE: building ONLY new local image tag ccpc-recovery:dev-nov23-b0cbe5c (no container deployment)
RECOVERY IMAGE: existing DEVELOPMENT image/DB and guest VM are not modified
RECOVERY IMAGE: build log is private: /home/gani/ccpc-restore-labs/ccpc-recovery-image-build-20261123/build.log
RECOVERY IMAGE: verifying image without networking, host folders, DB or secrets
RECOVERY IMAGE BUILD: PASS
IMAGE TAG: ccpc-recovery:dev-nov23-b0cbe5c
IMAGE ID: sha256:f53cc9ee316f758be669e4844655698b50776cd4cc3ccfb834bc433c1dec9bfb
FRAPPE GIT SHA: 988e54f3c4c291e2077a83809663f123731abe76
ERPNEXT GIT SHA: 4048fb70e14d1843956fcdabb7c3cca75a1cbcdd
CCPC GIT SHA: b0cbe5c13cb68499a7920de2879f65e72cff000a
IMAGE APP VERSIONS:
ccpcerp 0.0.1  ()
erpnext 16.34.2  ()
frappe 16.33.1  ()
PRIVATE AUDIT DIRECTORY: /home/gani/ccpc-restore-labs/ccpc-recovery-image-build-20261123
NO DEPLOYMENT, IMAGE EXPORT, VM NETWORKING OR BACKUP RESTORE
```

**Verified G3 milestone from owner evidence: PASS** new, exact-source, backend-stage app image compiled and its immutable SHA/version checks passed, Docker image available only in **host local image cache**, not yet loaded into recovery guest. Reviewed repo `images/custom/Containerfile` enforces upstream SHAs and original ERPNext CCPC overlay SHA. Build log is private; during build, Browserlist/Vite/font/Redis-cache warnings were observed and were nonfatal to overall PASS, but later restored sites still need runtime validation. Running DEVELOPMENT's original images, volumes, DB remain untouched by this operator build; **no deployment**. User approved combined one-time guest baseline setup earlier.

**Next authorized implementation:** create private **non-secret offline guest media** containing `docker image save` of the exact new image (`sha256:f53cc9ee...`), local `mariadb:11.8` (`efb4959e...`) and `redis:alpine` (`9d317178...`), plus a vetted Docker Engine+dependencies for Ubuntu 24.04.5 guest. Guest **still QEMU `-nic none`**, no direct network, no Docker; use a separate bounded read-only attached offline media via QMP or reviewed guest restart controller to deliver. Never export host container filesystem, guest private backup, mounted `/workspace`, `/home/frappe/.ssh`, SSH keys or Docker socket. Original DEVELOPMENT and PRODUCTION untouched, no actual confidential backup ingress or restore under this approval.

Docker's official [binary install docs](https://docs.docker.com/engine/install/binaries) allow test-only static engine installation but caution that distro packages are preferred and binary installs lack automatic security updates. For long-term reuse, pin/checksum engine archive, test offline Docker prerequisites (iptables/cgroup/overlayfs), and ensure no guest host/shared Docker daemon. No guest Docker installation/backup restore result is claimed.

## 2026-11-23 — Approved one-time offline runtime/image media creator committed; transfer not yet executed

After operator-reported **exact-source recovery Docker image BUILD PASS** `sha256:f53cc9ee316f758be669e4844655698b50776cd4cc3ccfb834bc433c1dec9bfb`, a **new image-only guest offline media script** was authored and GitHub-refetched on review branch `review/dev-restore-vm-staging-2026-11-23`, commit **`e27c06407325dd29112f9fa151c350223be92c37`**:
- path `scripts/development/operator/ccpc_dev_recovery_offline_media_20261123.sh`
- blob SHA-1 **`5ae8943d02a3af37f30857d3e98e94ec0727c51d`**
- full-source SHA-256 **`a35ddbc348b19badbf855df64586c6826875c8a43c86d4e084a31bab1039e9b9`** (JS SHA-256 verified with known test vector)
- **NOT YET RUN on owner host.**
- One-shot host script (normal `gani@ccpcerpserver`, local Docker only) checks expected existing exact app image SHA/id/label; expected MariaDB/Redis cached immutable image prefixes; no existing private one-shot media directory, 20GiB free, genisoimage/mkisofs, secure directory; downloads official Docker 29.7.2 amd64 **test-only static binary .tgz** via HTTPS **to the host** (never guest NIC), validates tar structure, performs **Docker image save** only of `ccpc-recovery:dev-nov23-b0cbe5c`, `mariadb:11.8`, `redis:alpine`, pipes through gzip -1 and 1600MiB split parts, verifies compressed stream; builds private Rock Ridge/Joliet ISO image `/home/gani/ccpc-restore-labs/ccpc-recovery-offline-media-20261123/ccpc-recovery-offline.iso`, SHA256 manifest for guest transfer and separate ISO SHA256 receipt. Does **not** export Docker volumes, container write layers, dev app `/workspace`, host `.ssh`, DB/site-config/site attachments or backups. Does **not** modify guest QEMU, Docker live container, host Docker daemon or PROD. ISO contains app source code and should remain private. Docker static engine selected only for a **throwaway isolated recovery test VM**; official Docker docs explicitly caution it is not a normal supported production deployment with distro security updates.
- Remaining: attach media through **reviewed QMP hotplug** or guest-only controlled graceful stop/restart path; verify ISO, guest prerequisites (especially `iptables`), install runtime only inside guest, `docker load` exactly approved images, start guest MariaDB/Redis/app and freeze baseline. No backup ingress or restore yet. Do not infer media preparation or guest Docker install succeeded until owner terminal confirms it. Original guest still launched `-nic none` with no shared resources. Avoid repeated provisioning or adding guest network.

Operator workflow: fetch immutable script by commit, check exact Git blob and SHA256 and `bash -n` once, then execute in host terminal. Do not rerun if one-shot folder exists; preserve evidence on error. User has approved the combined installation, no per-step approval needed for guest-only work, but no production or confidential backup restore approval.

## 2026-11-23 — Offline-media script initial run blocked at line 39; fix committed, rerun pending

Owner fetched GitHub-reviewed offline ISO prep script `ccpc_dev_recovery_offline_media_20261123.sh`, verified original SHA and `bash -n`, but first attempt failed before ISO creation:
```text
/home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_offline_media_20261123.sh: OK
OFFLINE MEDIA SCRIPT: VERIFIED
/home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_offline_media_20261123.sh: line 39: test: b0cbe5c13cb68499a7920de2879f65e72cff000a: unary operator expected
```
**Root cause exactly reviewed in connected GitHub source:** `test "$(docker image inspect ...)" =` incorrectly ended the shell line before its expected SHA argument, so Bash ran `test` with missing operand. User-reported error shows image label itself returned the expected Nov22 SHA. The script failed **before** one-shot directory `/home/gani/ccpc-restore-labs/ccpc-recovery-offline-media-20261123` is made (creation is after this check). It made no media/download/export or guest change. Original successful Frappe/ERPNext/CCPC image ID `sha256:f53cc9ee316f758be669e4844655698b50776cd4cc3ccfb834bc433c1dec9bfb` remains intact as far as evidence shows.

**GitHub fix committed and verified**, branch `review/dev-restore-vm-staging-2026-11-23`, path `scripts/development/operator/ccpc_dev_recovery_offline_media_20261123.sh`, commit **`9f30830565feeaa08067cb3b43db88bc5b293501`**, new blob SHA-1 **`eaa06809b5d84b5f110f65697e219efc34a73550`**, full script SHA-256 **`f765d08f2390c98f6a508050a45478f13516a70b9248108f1158ae2ca14e03d6`** (JS hash algorithm known-vector verified). Fixed by explicit `if test "$(docker image inspect ...label...)" != "b0cbe5c..."; then stop ...; fi`, no split test operands. Only source repair, original active DEV and guest unaffected.

**Next owner action**, normal host only: verify original local script hash `a35ddbc348b19badbf855df64586c6826875c8a43c86d4e084a31bab1039e9b9`, fetch corrected exact GitHub commit and blob into private temp directory, verify new SHA256 and `bash -n`, atomically replace prior local reviewed script, verify one-shot media directory absent, execute **only corrected ISO/media script** again. The original code-correct application Docker build should **never be repeated**. As yet no corrected media run result or guest VM import. If one-shot folder exists unexpectedly, STOP and inspect rather than delete. No PRODUCTION or private backup.

## 2026-11-23 — Offline ISO media creation PASS; controlled guest ISO restart helper ready

Owner ran the SHA/pinned fixed `ccpc_dev_recovery_offline_media_20261123.sh` on `gani@ccpcerpserver` and verified **PASS**:
```text
/home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_offline_media_20261123.sh: OK
/home/gani/.ccpc-media-fix.ooqzXe2B/fixed.sh: OK
/home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_offline_media_20261123.sh: OK
CORRECTED OFFLINE MEDIA SCRIPT: VERIFIED
RECOVERY OFFLINE MEDIA: downloading official Docker static testing runtime 29.7.2 on host
RECOVERY OFFLINE MEDIA: exporting exactly 3 pre-validated immutable images (no live container or volume)
RECOVERY OFFLINE MEDIA: app=ccpc-recovery:dev-nov23-b0cbe5c; db=mariadb:11.8; redis=redis:alpine
RECOVERY OFFLINE MEDIA: constructing read-only ISO from non-secret Docker images and testing runtime
RECOVERY OFFLINE MEDIA: PASS
ISO PATH: /home/gani/ccpc-restore-labs/ccpc-recovery-offline-media-20261123/ccpc-recovery-offline.iso
ISO SHA256: 32ac13073a0383a75c6bc0df7b93a8b7995750cfa0406e05133084aad9eb84b4
ISO SIZE BYTES: 1127800832
DOCKER RUNTIME VERSION: 29.7.2
APP IMAGE: ccpc-recovery:dev-nov23-b0cbe5c
NO BACKUP DATA OR HOST FILES EXPORTED
GUEST VM: NOT TOUCHED; NO GUEST NETWORK OR IMAGE IMPORT
```

**Verified G4 milestone: PASS offline non-backup media exported on DEVELOPMENT host only** (app image source-pinned `sha256:f53cc9ee...`, exact existing `mariadb:11.8`, `redis:alpine`, official Docker 29.7.2 guest-only test runtime; ISO exists with owner-reported byte count and SHA256). **No guest disk media attached, Docker runtime installed, services running, or backup restored yet.** Do not confuse host Docker engine with guest Docker. Original immutable backup still untouched; no PRODUCTION action.

**Next reviewed approach:** controlled ACPI graceful shutdown **of only the isolated guest**, verify old process exited, then restart same persistent qcow2 with the SHA-verified ISO added as a read-only third `if=virtio` block drive. This avoids unverified QMP PCIe hotplug on Q35 without preconfigured root ports. Do not restart or change Docker or host. Original reviewed guest controller `python3 -B /home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_guest_control_20261123.py --shutdown` only sends ACPI powerdown; then check same script `--status` for STOPPED. If original guest still running, do NOT launch duplicate or force-kill. Console previous connection Ctrl+] detach only. Shut down guest only, not DEVELOPMENT host.

**New reviewed media guest control script created and GitHub-refetched** branch `review/dev-restore-vm-staging-2026-11-23`, file `scripts/development/operator/ccpc_dev_recovery_guest_media_control_20261123.py`, commit **`285d4e03e1903ba354035f5883617776021bde11`**, blob `73d1182b160fbbf94d5860ecc25009c0a1d1052d`, source SHA256 `eea589ee27ea7d80780c145113064058917fd10abaf564c41ebafde52c509211` (JS known-vector verified). **Not yet fetched or AST-checked on operator host.** Controls `--start` via `sg kvm`, `--status`, `--console`, `--shutdown`. It verifies old guest no longer running; checks original Ubuntu + layered guest disk backing chain, private file modes, new media SHA+size, host/dev identity, KVM, 11GiB free RAM, Docker DEV container running and no one-shot runtime folder collision, before launching new separate private VM runtime at `/home/gani/ccpc-restore-labs/ccpc-dev-recovery-media-runtime-20261123`. New QEMU uses same 8GiB/4 CPU guest disk, original cloud-init ISO, **new read-only Docker media ISO**, `-nic none`, private Unix serial/QMP, no host shares, no Docker mounts, no guest network. It does not touch old runtime evidence or backups. **Host execution pending**; do not claim guest restart PASS until owner confirms console boot and guest reads /dev/vd* media. Once guest media attached, inspect `lsblk -f` + guest package prerequisites read-only; then implement one-time guest Docker testing runtime from ISO and three image import.

## 2026-11-23 — First persistent guest QMP shutdown script misclassified response; use guest-native poweroff

Owner ran reviewed original guest controller `--shutdown` followed by `--status` after offline ISO media preparation:
```text
PERSISTENT GUEST: RUNNING; PID: 2701670
QEMU NETWORK DISABLED: True
QEMU MONITOR DISABLED: True
STOP: QMP guest ACPI shutdown rejected
PERSISTENT GUEST: RUNNING; PID: 2701670
QEMU NETWORK DISABLED: True
QEMU MONITOR DISABLED: True
```
**Verified:** only the original persistent no-NIC guest remains observed RUNNING at status time; ISO is successfully built and remained on host, **not attached**. No forced shutdown/host/dev/PROD change. On code review of original controller `scripts/development/operator/ccpc_dev_recovery_guest_control_20261123.py`, its `shutdown()` sends `system_powerdown` via QMP then reads **exactly one JSON line** and mistakes any non-`return` JSON (e.g., async QMP `event`) as rejection. Thus error text is **not a reliable QEMU rejection diagnosis**, and a shutdown may have been initiated after the immediate status check. No cleanup or duplicate VM launch is safe until original PID stops.

**Immediate safer fallback (host operator):** first `python3 -B /home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_guest_control_20261123.py --status`; if `STOPPED`, do not enter console—proceed to ISO guest controller after verification. If still `RUNNING`, connect original guest `python3 -B ... --console`; login as `ccpc-restore` if needed, then run **inside guest** `sudo systemctl poweroff` (guest user has sudo ALL=(ALL) ALL as declared in original reviewed cloud-init seed, so password prompt will ask for private guest password). Password **never shared** in chat or logs. Guest console socket will disconnect on shutdown; return to **host** and recheck original controller `--status` for stopped before launching new media VM. Do not run `sudo systemctl poweroff` on host. Do not use `kill` or host reboot. Original VM persistent disk remains intact.

**Engineering follow-up:** Correct QMP command handling to use command IDs and skip unsolicited event records for both original and new media guest controller; keep diagnostics explicit. But guest-native shutdown is best immediate recovery unblocker. New media controller remains unexecuted, original disk intact, no backup restore.

## 2026-11-23 — Original persistent recovery guest gracefully stopped; ISO-equipped restart next

Owner reported **`PERSISTENT GUEST: STOPPED; PID NO LONGER EXISTS`** from original reviewed `ccpc_dev_recovery_guest_control_20261123.py --status` after the fallback for QMP ACPI error. **Shutdown verified by original controller's process/PID check; guest disk and Nov23 private ISO remain preserved.** Owner's exact shutdown mechanism (guest-native `sudo systemctl poweroff` vs asynchronously completed QMP request) was not separately observed; do not overclaim its cause. Do not run old `--start` again; its one-shot runtime folder exists.

**Next authorized one-time host step:** use the GitHub-reviewed media controller `scripts/development/operator/ccpc_dev_recovery_guest_media_control_20261123.py` from immutable commit `285d4e03e1903ba354035f5883617776021bde11` on branch `review/dev-restore-vm-staging-2026-11-23`, blob `73d1182b160fbbf94d5860ecc25009c0a1d1052d`, source SHA-256 `eea589ee27ea7d80780c145113064058917fd10abaf564c41ebafde52c509211`. Operator should fetch pinned file into **new** `/home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_guest_media_control_20261123.py`, confirm exact Git blob and SHA256, `python3 -m ast` or `ast.parse` preflight, then `sg kvm -c 'python3 -B ... --start'`. This creates separate private runtime but boots the **same previously shut down persistent guest qcow2**, with validated ISO `32ac13073a0383a75c6bc0df7b93a8b7995750cfa0406e05133084aad9eb84b4` read-only, `-nic none`, no host files/DB/secrets mounted. It cannot run if original matching guest still running and refuses repeated one-shot runs. Expected `RECOVERY GUEST WITH OFFLINE MEDIA: START REQUESTED`, not proof guest boot/login/media mount until guest follow-up verification. No image import, guest Docker runtime install or confidential backup restore has yet occurred. Do not delete old runtime evidence, original dev container, or production.

## 2026-11-23 — Offline ISO recovery guest QEMU start PASS, guest mount pending

Owner executed exact pinned `ccpc_dev_recovery_guest_media_control_20261123.py --start` using KVM group on the normal DEVELOPMENT host. Terminal output:
```text
/home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_guest_media_control_20261123.py: OK
PYTHON SYNTAX: PASS
OFFLINE MEDIA GUEST CONTROLLER: VERIFIED
RECOVERY GUEST WITH OFFLINE MEDIA: START REQUESTED; QEMU PID: 2717495
ISO SHA256 VERIFIED: 32ac13073a0383a75c6bc0df7b93a8b7995750cfa0406e05133084aad9eb84b4
OFFLINE MEDIA: READ-ONLY VIRTIO DRIVE
NETWORK: NONE; LIVE DEVELOPMENT / PRODUCTION: UNTOUCHED
NO CONFIDENTIAL BACKUP TRANSFER OR RESTORE
GUEST LOGIN: ccpc-restore (original private host-only password)
GUEST CONSOLE: python3 -B <this-script> --console
GUEST SHUTDOWN: python3 -B <this-script> --shutdown
```
**G5 startup PASS:** reviewed Python guest media script SHA and syntax checked on owner host; requested QEMU start returned PID **2717495** with already verified private **1,127,800,832-byte ISO** checksum, `-nic none`, ISO read-only drive, and same persistent Ubuntu guest disk. This does **not yet** verify Ubuntu guest login, ISO9660 recognition/mount, guest Docker installation, loading three images, or restored backup. Original persistent guest QEMU PID `2701670` had previously been verified stopped; do not run it concurrently with new QEMU. No PRODUCTION or live DEVELOPMENT services/volumes operated on.

**Immediate next host step:** 
```bash
python3 -B /home/gani/ccpc-reviewed-scripts/ccpc_dev_recovery_guest_media_control_20261123.py --console
```
Log into `ccpc-restore` with original private local-only password (do not share). **Inside the guest** run:
```bash
echo "=== OFFLINE RECOVERY MEDIA ==="
lsblk -o NAME,SIZE,RO,FSTYPE,LABEL,MOUNTPOINTS
```
Confirm separate read-only `iso9660` VirtIO device label `CCPCRECOVERY2026`. Do not assume `/dev/vdc` until verified; original cloud-init ISO may occupy `/dev/vdb`. After guest media recognition, perform source checksum verification and guest-only Docker runtime prerequisites/installation and `docker load` with no network. Guest ACPI QMP `--shutdown` uses same vulnerable simplistic response reader as old controller; may incorrectly reject an asynchronous event; use guest-native `sudo systemctl poweroff` if appropriate, and verify stopped before any guest disk clone. No confidential backup ingress or actual restore authorized.

## 2026-11-23 — Offline ISO guest successfully booted and logged in; lsblk pending

Owner attached to the exact reviewed **ISO-equipped recovery guest** via `ccpc_dev_recovery_guest_media_control_20261123.py --console` and reported:
```text
OFFLINE-MEDIA GUEST: RUNNING; PID: 2717495
QEMU NETWORK: NONE; ISO: READ-ONLY (launch argument)
NO HOST SHARES / PORT FORWARDS
GUEST CONSOLE ATTACHED. Ctrl+] to detach.
ccpc-recovery login: ccpc-restore
Password: [not shared]
Welcome to Ubuntu 24.04.5 LTS (GNU/Linux 6.8.0-147-generic x86_64)
ccpc-restore@ccpc-recovery:~$
```
**Verified:** previous persistent guest's baseline qcow2 successfully boots with additional **SHA-256-verified, read-only offline ISO as QEMU drive**; console login as `ccpc-restore` PASS; no NIC, no host shares/port forwards. Ubuntu reports inability to access changelogs over the Internet, which is expected without guest networking. No actual guest ISO filesystem read or mount verified yet, no guest Docker installed, no MariaDB/Redis/Frappe containers started, no confidential backup transfer or restore. No password disclosed.

**Next owner action** read-only inside `ccpc-restore@ccpc-recovery:~$`:
```bash
lsblk -o NAME,SIZE,RO,FSTYPE,LABEL,MOUNTPOINTS
```
Look for separate virtio block ISO9660 device `CCPCRECOVERY2026`; do not assume a fixed `/dev/vdc` prior to evidence. After confirmation, safely mount image read-only, verify payload manifest, evaluate Docker runtime dependencies offline, then load only the three verified image tags to guest. Host Docker remains untouched and PRODUCTION never operated on. Media image size=1127800832 bytes, owner-verified SHA256=32ac13073a0383a75c6bc0df7b93a8b7995750cfa0406e05133084aad9eb84b4.

## 2026-11-23 — Guest recognizes CCPC recovery ISO as read-only /dev/vdc, checksum check pending

Owner ran `lsblk -o NAME,SIZE,RO,FSTYPE,LABEL,MOUNTPOINTS` from successfully logged-in `ccpc-restore@ccpc-recovery` in QEMU media guest PID **2717495**:
```text
NAME     SIZE RO FSTYPE  LABEL            MOUNTPOINTS
vda       60G  0
├─vda1    59G  0 ext4    cloudimg-rootfs  /
├─vda14    4M  0
├─vda15  106M  0 vfat    UEFI             /boot/efi
└─vda16  913M  0 ext4    BOOT             /boot
vdb      366K  1 iso9660 cidata
vdc      1.1G  1 iso9660 CCPCRECOVERY2026
```
**G6 guest media recognition PASS:** only the intended extra read-only `iso9660` QEMU drive appears, labeled `CCPCRECOVERY2026`, at **`/dev/vdc`**. Persistent root filesystem `/dev/vda1`, preexisting cloud-init seed `/dev/vdb`. **Not yet mounted, manifest-verified, or installed** as of this operator response; no guest Docker daemon or MariaDB/Redis/ERPNext containers running; no private backup transferred/restored, no guest network.

**Immediate next action in guest (allowed under approved combined one-time lab setup):**
```bash
sudo mkdir -p /mnt/ccpc-recovery-media
sudo mount -t iso9660 -o ro,nosuid,nodev,noexec /dev/vdc /mnt/ccpc-recovery-media
cd /mnt/ccpc-recovery-media
sha256sum -c SHA256SUMS
```
Expected pass: `docker-29.7.2.tgz: OK` and all `images.tgz.part-*` files `OK`. This validates contents after SHA-verified host ISO construction, without extracting/executing anything. No installation until owner sends digest check result. If mount already in place, inspect first; do not mount unknown devices. The next step after PASS is verifying available guest host prerequisites for standalone Docker testing binaries, installing and loading only isolated images into guest disk; no host or PRODUCTION Docker changes.

## 2026-11-23 — Guest-mounted ISO SHA-256 manifest PASS; Docker preflight next

Owner used **inside isolated guest** `ccpc-restore@ccpc-recovery` (media QEMU PID 2717495):
```text
sudo mkdir -p /mnt/ccpc-recovery-media
sudo mount -t iso9660 -o ro,nosuid,nodev,noexec /dev/vdc /mnt/ccpc-recovery-media
cd /mnt/ccpc-recovery-media
sha256sum -c SHA256SUMS
=== VERIFYING OFFLINE RECOVERY MEDIA ===
docker-29.7.2.tgz: OK
images.tgz.part-000: OK
```
**G7 PASS:** ISO9660 `/dev/vdc` labeled `CCPCRECOVERY2026` successfully mounted **read-only/noexec/nodev/nosuid** in guest, both ISO manifest entries `docker-29.7.2.tgz` and `images.tgz.part-000` match source SHA-256. Combined offline 1.13GB media contains Docker testing runtime and exactly three host-exported immutable images. Guest still **no NIC**. The file manifest itself was generated by owner-host media script and host ISO SHA verified at QEMU start. No installation, running guest Docker, image load, MariaDB, Frappe service or confidential backup import yet.

**Next critical prerequisite before rootful static Docker testing runtime installation**, in guest only: read-only query presence of `iptables`, `ip6tables`, `modprobe`, `mount`, `systemctl`, `tar`, `gzip`, `sha256sum`, kernel overlayfs (`/proc/filesystems`), cgroups mount `/sys/fs/cgroup`, current `/usr/local/bin/docker` or `dockerd`, and free disk. Docker static installs (https://docs.docker.com/engine/install/binaries/) normally require `iptables`; however, QEMU has `-nic none` and the guest-only recovery design can explicitly run `dockerd --bridge=none --iptables=false --ip6tables=false --ip-forward=false --ip-masq=false` and containers with `--network host` solely inside guest, which shares only guest loopback and not host network. This needs testing and no assumption of success; do not install apt packages from network or enable guest NIC. Docker daemon configuration must remain guest-only; do **not** mount host Docker socket. Verify available guest prerequisites before deciding the minimal guest-only systemd service installation. User explicitly approved one-time isolated guest setup (no backup restore).

## 2026-11-23 — Offline Docker guest prerequisites PASS; reviewed one-time installation script ready

Owner ran read-only prerequisite inventory **inside offline Ubuntu 24.04.5 recovery guest**:
```text
tar: AVAILABLE
gzip: AVAILABLE
sha256sum: AVAILABLE
mount: AVAILABLE
systemctl: AVAILABLE
iptables: AVAILABLE
ip6tables: AVAILABLE
modprobe: AVAILABLE
docker: NOT INSTALLED
dockerd: NOT INSTALLED
=== KERNEL AND STORAGE ===
cgroup2
/dev/vda1 58G, 1.7G used, 56G available, 3% use
=== EXISTING DOCKER SOCKET ===
No Docker socket
```
**Verified G8 guest preflight:** cgroups v2 mounted, systemd and basic dependencies present, 56GiB free, Docker engine/socket not installed. `grep -w overlay /proc/filesystems` was blank: overlayfs **not yet listed** (may simply require loading kernel module). Guest QEMU is launched with `-nic none`, ISO `/dev/vdc` mounted `ro,nosuid,nodev,noexec`, `docker-29.7.2.tgz: OK`, `images.tgz.part-000: OK` as guest SHA manifest checks. No guest Docker load or backup import yet.

**Developer research:** Official Docker static binary install guide https://docs.docker.com/engine/install/binaries/ supports offline extraction/installation for **testing**, cautions not production; daemon flags described at https://docs.docker.com/reference/cli/dockerd/ support `--bridge=none`, `--iptables=false`, `--ip6tables=false`, `--ip-forward=false`, `--ip-masq=false`. Docker 29 defaults containerd image store for new installs (https://docs.docker.com/engine/storage/containerd), so approved lab config uses `"features":{"containerd-snapshotter":false}` and `"storage-driver":"overlay2"` to keep storage predictable and reduce compressed layer duplication on 58G guest.

**One-time guest-only Docker test setup prepared and GitHub-refetched:** `scripts/development/operator/ccpc_dev_recovery_guest_install_docker_20261123.sh` on review branch `review/dev-restore-vm-staging-2026-11-23`, commit **`0b475922b564b27addace1b5c27f54d240389005`**, blob SHA-1 **`61fc40b5cee0a2b150c21a1d15582abf3ad08cd4`**. It must be pasted/transferred **inside** the networkless guest because guest cannot fetch GitHub, then run as `ccpc-restore`; preflight hostname, mounted read-only ISO and both manifest SHA256 files, absent previous Docker installation/socket/systemd unit, basic `git/ps/xz`; then `sudo modprobe overlay` and require overlay in `/proc/filesystems`, expand official Docker 29.7.2 binaries from ISO under guest-only `/opt/ccpc-recovery-docker-static`, install into guest `/usr/local/bin`, create guest-only `/etc/docker/daemon.json` with no default bridge, no iptables/ip-forward/masq/proxy, legacy overlay2 storage under guest `/var/lib/ccpc-recovery-docker` and bounded logs; create a uniquely named `ccpc-recovery-docker.service` (not host Docker.service) and `systemctl start` without enabling on boot until verified; `sudo docker info` reports runtime. Owner has previously approved this combined isolated guest installation. User operation **PENDING**; no guest Docker runtime success yet. If it fails, stop and review guest `sudo systemctl status ccpc-recovery-docker.service --no-pager`; no automatic rerun/cleanup.

## 2026-11-23 — Guest Docker bootstrap stopped at root-only glob expansion; reviewed script repaired, resume pending

Owner pasted reviewed guest Docker install bash into **ISO-only Ubuntu recovery guest**, then executed; output:
```text
docker-29.7.2.tgz: OK
images.tgz.part-000: OK
nodev   overlay
install: cannot stat '/opt/ccpc-recovery-docker-static/docker/*': No such file or directory
```
Original installer `scripts/development/operator/ccpc_dev_recovery_guest_install_docker_20261123.sh` installed `/opt/ccpc-recovery-docker-static` as **root-owned mode 0700** and then tried `sudo install -m 0755 /opt/ccpc-recovery-docker-static/docker/* /usr/local/bin/`. Bash glob expansion happens in the **non-root calling shell**, which cannot traverse the parent directory; the literal `*` reaches sudo's `install`, yielding this error even when `tar` extraction succeeded. Since `set -e` stopped on that line, service/systemd/daemon.json operations after it **were not executed by the intended script**. User's pasted terminal echo appeared partially interleaved; exact guest file contents are not yet independently inspected. Do not assume successful Docker install.

**Fix committed/refetched on GitHub** review branch `review/dev-restore-vm-staging-2026-11-23`, path `scripts/development/operator/ccpc_dev_recovery_guest_install_docker_20261123.sh`, commit **`e5c89509cd358f624591280429bf2b2d8b614601`**, blob `dbd0b5c6af7489c259a3bf0dfbd3acdc3ad32d78`. Fix is `sudo sh -c 'set -eu; test -x /opt/ccpc-recovery-docker-static/docker/dockerd; test -x /opt/ccpc-recovery-docker-static/docker/docker; install -m 0755 /opt/ccpc-recovery-docker-static/docker/* /usr/local/bin/'`; now `*` expands under privileged shell only. ISO remained mounted and checksum verification PASS, kernel overlay module loaded (`nodev overlay`). Guest remains QEMU PID 2717495 and `-nic none`. No backup or PRODUCTION changed.

**Minimal safe owner recovery (inside guest only, no rerun of entire script):**
```bash
sudo sh -c '
set -eu
D=/opt/ccpc-recovery-docker-static/docker
test -x "$D/dockerd"
test -x "$D/docker"
test ! -e /usr/local/bin/dockerd
install -m 0755 "$D"/* /usr/local/bin/
'
/usr/local/bin/docker --version
/usr/local/bin/dockerd --version
```
This resumes **only the previously failed binary copy** after checking archive extraction; no host/guest Docker daemon changes and no service yet. After version output, inspect/recreate the intended guest-only `/etc/docker/daemon.json` and `ccpc-recovery-docker.service` cleanly and start it once. Never re-run the full installer automatically because the guest now has partially installed prerequisites; preserve guest evidence. No confidential Nov23 backup restore approval yet.

## 2026-11-23 — Manual guest Docker 29.7.2 binary copy PASS; isolated daemon setup pending

Owner executed manually scoped guest-only recovery command after failing shell glob expansion:
```bash
sudo sh -c '
set -eu
D=/opt/ccpc-recovery-docker-static/docker
test -x "$D/dockerd"
test -x "$D/docker"
test ! -e /usr/local/bin/dockerd
install -m 0755 "$D"/* /usr/local/bin/
'
/usr/local/bin/docker --version
/usr/local/bin/dockerd --version
```
Owner output:
```text
Docker version 29.7.2, build a7dcaa6
Docker version 29.7.2, build 6a43e3d
```
**G9 PASS:** guest-only Docker CLI and dockerd testing binaries now installed into `/usr/local/bin/` in isolated Ubuntu 24.04.5 QEMU PID 2717495; **daemon has NOT been configured, started or validated yet**. ISO remains guest read-only `/dev/vdc`, SHA manifest verified, no NIC. No guest MariaDB/Redis/application image load, no live DEVELOPMENT/PRODUCTION work or confidential backup ingress.

**GitHub engineering continuation prepared and refetched:** review branch `review/dev-restore-vm-staging-2026-11-23`, commit **`ceb7f3f8692a8a4771aaebfb80b5bb3744a99f13`**, path `scripts/development/operator/ccpc_dev_recovery_guest_finish_docker_20261123.sh`, Git blob SHA-1 `9263a33cc83cbda52b3c6d54517c0a5bce264f45`. New scoped resume script checks `ccpc-recovery` guest, `ccpc-restore`, pinned CLI+daemon versions, mounted read-only ISO, no existing daemon config/service/socket, only `lo` guest interface, overlayfs; writes guest-only `/etc/docker/daemon.json` with `overlay2` and legacy image storage, no default bridge, no iptables/ip-forward/masquerade; validates via `dockerd --validate --config-file`, creates `ccpc-recovery-docker.service` with `Type=notify` and `Delegate=yes`, starts but does **not enable** service on boot, verifies `sudo docker info` and absence of Docker bridge. May be pasted by owner **inside the guest only**; source content committed first in GitHub. This is not an image export, deployment, backup restore, or production operation. **Guest service start result still PENDING**. On any STOP, do not rerun script because it creates local files; inspect `sudo systemctl status ccpc-recovery-docker.service --no-pager` and `sudo journalctl -u ccpc-recovery-docker.service -n 35 --no-pager` without posting secrets. Do not confuse guest with host shell.

Once guest daemon runs successfully, load three image tags from `images.tgz.part-000` on read-only ISO, verify exact app image ID `sha256:f53cc9ee316f758be669e4844655698b50776cd4cc3ccfb834bc433c1dec9bfb`, MariaDB:11.8 and Redis:alpine, then stand up isolated database/Redis/test app on guest localhost only. Keep Nov23 original confidential NAS backup outside guest until separately approved.

## 2026-11-23 — Isolated guest Docker daemon STARTED PASS, image import pending

Owner resumed **only the remaining guest-side Docker configuration** from the reviewed `ccpc_finish_docker.sh` script after static CLI/daemon binaries were successfully installed. Output from `ccpc-restore@ccpc-recovery:/mnt/ccpc-recovery-media`:

```text
configuration OK
active
Storage=overlay2 Cgroup=2 Root=/var/lib/ccpc-recovery-docker
GUEST DOCKER ENGINE: STARTED
```

**G10 guest Docker Engine STARTED PASS:** daemon config validated, dedicated `ccpc-recovery-docker.service` active, Docker engine running **inside the isolated guest** with storage driver overlay2, cgroup v2, data-root `/var/lib/ccpc-recovery-docker`. Original shell includes guard against unintended guest NICs, checks mounted read-only ISO and no docker0 interface. Guest QEMU media controller started with `-nic none`; no host Docker socket or DEVELOPMENT volumes attached. This did **not** automatically import the application/DB/Redis images or start guest containers; no actual confidential backup ingress/restore or PRODUCTION operation has occurred. The guest Docker service was started, not enabled for boot; after future guest poweroff it will need controlled start or documented setup.

**Immediate approved next operator action, INSIDE GUEST ONLY:** verify signed-from-host ISO manifest again and load exactly approved image archive:
```bash
(
set -euo pipefail
MEDIA=/mnt/ccpc-recovery-media
cd "$MEDIA"
sha256sum -c SHA256SUMS
cat "$MEDIA"/images.tgz.part-* | gzip -dc | sudo docker image load
for IMAGE in ccpc-recovery:dev-nov23-b0cbe5c mariadb:11.8 redis:alpine; do
  sudo docker image inspect --format '{{.RepoTags}} {{.Id}}' "$IMAGE"
done
echo "GUEST RECOVERY IMAGES: LOADED"
)
```
This imports only immutable Docker image content from the read-only ISO into **guest** Docker data-root; no other host Docker daemon, no backup transfer, network pull or container launch. On successful image load, compare **full application image ID** against `sha256:f53cc9ee316f758be669e4844655698b50776cd4cc3ccfb834bc433c1dec9bfb`, DB and Redis against host inventory IDs; then prepare guest-only local DB/Redis and application test configuration. Do not claim restore validation until explicit owner approval and genuine isolated DB/site integration checks.

## 2026-11-23 — Three guest images loaded, image IDs differ from original host; provenance check pending

Owner successfully completed `docker image load` inside QEMU isolated no-NIC recovery guest, after SHA-256-verifying the mounted read-only ISO `/dev/vdc`, from `images.tgz.part-000` exported by the reviewed host media helper. Owner reported:

```text
=== VERIFYING RECOVERY IMAGES ===
[ccpc-recovery:dev-nov23-b0cbe5c] sha256:ab3a4d20bdc4648291e7cded957874bb80b0dc2f0808b269c726f10b52d311aa
[mariadb:11.8] sha256:0584f8a9edf68610996bd212f9fa3c45fe4fb85f53f1569de3311a15990227b6
[redis:alpine] sha256:55563f45704d59e891b6aa643014bb6b562abf21909a44b3b297502415b68e29
GUEST RECOVERY IMAGES: LOADED
```

**G11 guest image load PASS, image identity discrepancy OPEN:** all three tags exist in guest image store. The recorded host Docker image IDs were **app `sha256:f53cc9ee316f758be669e4844655698b50776cd4cc3ccfb834bc433c1dec9bfb`, MariaDB prefix `sha256:efb4959ef2c8`, Redis prefix `sha256:9d317178ecea`** (host values explicitly enforced by `scripts/development/operator/ccpc_dev_recovery_offline_media_20261123.sh` prior to `docker save`). In guest, **all three** are changed even though archive SHA verified. Do **not** claim identical image content from tag/ID alone. One plausible technical explanation is image identity differences under containerd vs classic image stores, especially newer Docker versions (see reported Docker CLI issue https://github.com/docker/cli/issues/6670 and Moby issue https://github.com/moby/moby/issues/51934), but **this is unverified for this host/guest pairing**; image ID mismatch must be explicitly reconciled with source metadata and read-only tests.

**Next owner action (read-only guest-only, no container startup yet):** inspect application labels and architecture of the imported image:
```bash
sudo docker image inspect --format 'OS={{.Os}} ARCH={{.Architecture}} FRAPPE={{index .Config.Labels "org.ccpc.recovery.frappe-sha"}} ERPNEXT={{index .Config.Labels "org.ccpc.recovery.erpnext-sha"}} CCPC={{index .Config.Labels "org.ccpc.recovery.ccpcerp-sha"}} BUILD={{index .Config.Labels "org.ccpc.recovery.deploy-commit"}}' ccpc-recovery:dev-nov23-b0cbe5c
```
Compare exactly FRAPPE `988e54f3c4c291e2077a83809663f123731abe76`, ERPNEXT `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`, CCPC `b0cbe5c13cb68499a7920de2879f65e72cff000a`, BUILD `23b5f6fbd35bcdfef6d3de8aaa57e4bc5f80d723`, `linux/amd64`. Then separately perform networkless/read-only isolated `bench version` smoke test. For full provenance, compare the archive's image config digests and file hashes against known host originals, not a possibly storage-backend-dependent `.Id` field. No containers launched, guest DB/Redis not configured, confidential backup not imported, no PRODUCTION operation. Do not delete images, rerun image load, or change Docker storage backend in response to this discrepancy.

## 2026-11-23 — Guest CCPC image provenance labels match exact source SHAs; isolated bench smoke next

Owner ran a guest-only read-only Docker image inspect command after the offline image import. Despite terminal copy/paste artifacts on some input lines, final formatted output was coherent and complete:
```text
OS=linux ARCH=amd64
FRAPPE=988e54f3c4c291e2077a83809663f123731abe76
ERPNEXT=4048fb70e14d1843956fcdabb7c3cca75a1cbcdd
CCPC=b0cbe5c13cb68499a7920de2879f65e72cff000a
BUILD=23b5f6fbd35bcdfef6d3de8aaa57e4bc5f80d723
```
**G12 image source-label verification PASS:** inspected imported guest image `ccpc-recovery:dev-nov23-b0cbe5c` has matching four full build-time source/deployment commit labels and platform `linux/amd64`. This reinforces chain of custody from host SHA-gated build through manifest-verified ISO. However Docker image content IDs **still do not match** host image IDs after save/load (all three), so do not claim byte-identical Docker image IDs or that labels alone cryptographically verify the image.

**Next one-time guest-only test:** replicate the host build helper's already reviewed, successfully executed **networkless read-only app smoke** inside the guest (not host) using:
```bash
sudo docker run --rm --network none --read-only --user 1000:1000 \
  --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 \
  --memory 768m --entrypoint /bin/sh \
  ccpc-recovery:dev-nov23-b0cbe5c -c '
    set -e
    cd /home/frappe/frappe-bench
    for a in frappe erpnext ccpcerp; do test -d "apps/$a"; done
    bench version
  '
```
Expected `frappe 16.33.1`, `erpnext 16.34.2`, `ccpcerp 0.0.1`; no guest NIC exists, Docker `--network none`, no host mounts, no DB, no backup restore, no production action. This is a smoke test, NOT real restored-site/database validation. On failure stop, inspect only; do not rerun automatically or change guest storage engine.

## 2026-11-23 — Guest CCPC bench smoke PASS; empty isolated MariaDB setup reviewed

Owner ran reviewed restrictive app-image smoke container **inside no-NIC recovery guest** after imported image source labels matched. Terminal output:
```text
ccpcerp 0.0.1  ()
erpnext 16.34.2  ()
frappe 16.33.1  ()
ccpc-restore@ccpc-recovery:/mnt/ccpc-recovery-media$
```
**G13 guest app smoke PASS:** `sudo docker run --rm --network none --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 --memory 768m --entrypoint /bin/sh ccpc-recovery:dev-nov23-b0cbe5c -c '... test -d apps/frappe/apps/erpnext/apps/ccpcerp; bench version'` returned all three exact versions; container auto-removed, no guest DB required, no backup import, no guest networking. The `()` fields in `bench version` are blank version/hash decoration, not a failure of the version smoke test. Image IDs after save/load still differ from host and are **not cryptographically reconciled** (labels/bench version match).

**Reviewed GitHub next step:** New one-shot guest-only empty MariaDB 11.8 setup script `scripts/development/operator/ccpc_dev_recovery_guest_start_mariadb_20261123.sh`, branch `review/dev-restore-vm-staging-2026-11-23`, commit **`73ef72870aff0d8a31651bbfbad2e00f004da4f0`**, blob **`814bad21b24c2d35ea093d8ce987c3b1692df3d1`**. Code refetched and verified. Guards guest hostname/user, only interface `lo`, active guest Docker service and exact guest Docker root, **no preexisting containers or volumes**, loaded MariaDB image, no preexisting guest password file. Generates random 32-byte root password as 64 hex digits to a **root-only 0600 file in root-owned 0700 guest dir** `/var/lib/ccpc-recovery-secrets/mariadb-root`, never logs/transfers password. Creates guest-only named volume `ccpc-recovery-mariadb-data`; launches `mariadb:11.8` **from loaded local image only** (`--pull=never`), `--network host` in the **guest** QEMU network namespace (guest has no NIC), passes password as `MARIADB_ROOT_PASSWORD_FILE` with **read-only guest-only secrets-dir mount**, binds server strictly `127.0.0.1`, 2GiB/pids limit, no restart. Docker official `--network host` shares only the network namespace of the Docker daemon host—which is **isolated QEMU guest**, not physical DEVELOPMENT host; QEMU remains `-nic none`, no port forward, no host Docker share. MariaDB docs support `MARIADB_ROOT_PASSWORD_FILE`. Does not create or restore site/company/business data. User's one-time isolated lab setup authorization already covers this. **Owner has NOT executed script yet; no MariaDB service or container startup verified**. After running it once, verify container readiness with guest-only `docker inspect`/readiness query, then configure separate guest Redis cache and queue on loopback. Never rerun if partial failure; inspect guest-only state without deleting it.

## 2026-11-24 — Guest-only MariaDB started, healthcheck and localhost binding pending

Owner executed the one-shot isolated guest MariaDB 11.8 setup with reviewed script from `review/dev-restore-vm-staging-2026-11-23`, initial commit `73ef72870aff0d8a31651bbfbad2e00f004da4f0`, on QEMU guest `ccpc-recovery` with `-nic none`. Reported:
```text
[sudo] password for ccpc-restore: [not disclosed]
[64-hex Docker container ID; omitted here]
GUEST MARIADB: ccpc-recovery-mariadb Up Less than a second
GUEST MARIADB: START REQUESTED
```
**G14 MariaDB container startup PASS, database readiness still PENDING.** Image was pulled from the already imported guest-only `mariadb:11.8` tag with `--pull=never`; configured to bind `127.0.0.1` **inside isolated QEMU guest** and uses `--network host` only within that guest, **not the DEVELOPMENT host**. New named guest Docker volume `ccpc-recovery-mariadb-data`; root password was generated locally into guest root-owned, private file `/var/lib/ccpc-recovery-secrets/mariadb-root`; its contents have **not** been shared. No backup imports/restores, no database/site data restored, no PRODUCTION or live DEVELOPMENT services operated on. Initial container status `Up Less than a second` is not evidence of SQL readiness.

**Next one-step read-only health test inside guest:**
```bash
(
set -e
sudo docker exec ccpc-recovery-mariadb healthcheck.sh --connect --innodb_initialized
echo 'MARIADB HEALTHCHECK: PASS'
sudo ss -lnt '( sport = :3306 )'
)
```
Official MariaDB image provides `healthcheck.sh --connect --innodb_initialized` (https://mariadb.com/docs/server/server-management/automated-mariadb-deployment-and-administration/docker-and-mariadb/using-healthcheck-sh); it verifies TCP connectivity and InnoDB initialization without printing root password. The `ss` output should show listening **127.0.0.1:3306**, not `0.0.0.0` or IPv6 all-address. If healthcheck returns nonzero, preserve guest logs/state and diagnose rather than rerunning one-shot script. **No Redis yet** until MariaDB readiness and listener scope verified.
