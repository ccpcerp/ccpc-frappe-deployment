# CCPC ERPNext — Dedicated PRODUCTION Host Setup Handoff

**Current operational checkpoint, 2026-10-23.** This is the live companion to [CURRENT-HANDOFF.md](CURRENT-HANDOFF.md) for the separate `ccpcerp-prod` preparation. GitHub remains the authoritative documentation source; later completed checkpoints should go at the top of this file. This host is not yet carrying live production ERPNext traffic or data.

## 2026-10-23 STEP 111 BLOCKED — DOCKER API SOCKET ACCESS DENIED; NO INVENTORY

Owner manually attempted the approved **read-only** Docker-daemon inventory on new host `ccpcadmin@ccpcerp-prod`. The pasted terminal shows the source command's guard checks and local Docker-context check, followed by:

```text
permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
ccpcadmin@ccpcerp-prod:~$
```

**Status: BLOCKED, NOT PASSED.** The Docker daemon refused the invoking user's API access. The command stopped before returning its per-project container, named-volume and network counts; **no evidence yet about existing Docker resources or project-namespace collisions**. Its intended operations were query-only. The command paste contains interactive garbling, so the precise byte sequence of each guard is not independently assured. No image/volume/container creations, real credentials, Git checkouts or production service changes were instructed or reported.

**Do not** run `sudo docker`, loosen `/var/run/docker.sock` permissions, add `ccpcadmin` to the `docker` group, or change the daemon until owner separately reviews and approves the privilege implications; Docker daemon access generally grants root-equivalent control.

**Next one Step 111a:** operator runs a **no-sudo, no Docker API** diagnostic on new host: `id -nG`; `stat -Lc` the `/var/run/docker.sock` type/mode/owner/group; inspect `docker context show` and `docker context inspect` endpoint (client-only); optionally `systemctl is-active docker` (service status only). Do not expose SSH keys, passwords, full environment or Docker configuration. If the context is not the expected `unix:///var/run/docker.sock`, STOP. Await operator output, then decide whether a narrowly scoped privileged **read-only** inventory merits separate consent. Never infer that lack of user permission means Docker is stopped or that Docker volumes are absent.

**Verified GitHub continuity:** draft PR #29 `security/dedicated-prod-external-env-2026-10-23` remains OPEN/DRAFT/UNMERGED at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`; parent draft PR #27 remains OPEN/DRAFT/UNMERGED at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. Steps 106–110 were separate, credential-free, non-deploying reviews; rollback/migration and reliable backup/recovery remain unresolved.

## 2026-10-23 STEP 110 PASSED BY OPERATOR OUTPUT — ISOLATED REVIEW PROJECT, EXPECTED NAMED VOLUMES AND NO BIND MOUNTS

Owner ran the approved, non-deploying Step 110 on NEW host `ccpcadmin@ccpcerp-prod`, using the separate review checkout `/home/ccpcadmin/ccpc-pr29-review`. The command included guards for original clean PR #27 checkout at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, review clean PR #29 checkout at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`, absence of review `.env`, disposable `DB_PASSWORD=CCPC_DUMMY_CONFIG_ONLY` in private external temporary `compose.env`, and `ccpc_compose config --format json` piped straight to fixed-output Python assertions.

Reported terminal output:

```text
PASS: Isolated review project name
PASS: Three expected named volumes
PASS: Correct service mounts; no bind mounts
PASS: Step 110 validation completed
## security/dedicated-prod-external-env-2026-10-23...origin/security/dedicated-prod-external-env-2026-10-23
ccpcadmin@ccpcerp-prod:~$
```

**Pass as terminal-reported:** Compose review project resolved to `ccpc-pr29-review`; expected named volumes are `sites`, `db-data`, `redis-queue-data`, with generated names `ccpc-pr29-review_sites`, `ccpc-pr29-review_db-data`, `ccpc-pr29-review_redis-queue-data`; all seven application containers mount sites at `/home/frappe/frappe-bench/sites`, `db` mounts db-data at `/var/lib/mysql`, `redis-queue` mounts redis-queue-data at `/data`; no extra bind mounts in reviewed effective model. **No actual volumes were created.** Terminal paste contains garbled/truncated middle commands but coherent fixed PASS output and clean Git status. Real cleanup not independently verified beyond the intended narrow trap; no real credentials, container create/up, migration or restoration.

**Independent GitHub review:** PR #29 and PR #27 still draft, open and unmerged at pinned commits above. Existing docs `docs/04-operations/recovery.md` list a generic environment `.env` and aspirational restoration time targets; this is **legacy/general guidance, not a tested new-host recovery plan**. `docs/04-operations/deployment-guide.md` and `docs/04-operations/release-process.md` show `./scripts/rollback.sh <previous-tag>` as rollback, but source `scripts/rollback.sh` invokes `deploy_release` and hence **runs migrations again**; it does not reverse database migrations or guarantee transaction/data recovery. Dedicated PR #29's `restore_env` intentionally performs no state rollback. Treat dedicated deployment rollback/recovery as **UNRESOLVED** until an explicit safe procedure, backup integrity and restore drill are reviewed. Do not use generic rollback.sh as a substitute for a database rollback.

**Next Step 111 recommendation:** a **read-only Docker daemon inventory on the NEW host only**, verifying its Docker context is local and checking for existing container/volume/network project namespace collisions for `ccpc-frappe-deployment` (expected original checkout directory name) and `ccpc-pr29-review` (test checkout name) before choosing explicit production project names. Report fixed-status findings only; do not run `docker compose up`, create/delete volumes, set production credentials, modify any checkout, or touch old PROD/DEV. Verify all previous review guards first; on unexpected Docker context or existing resources, STOP and investigate before changes.

## 2026-10-23 STEP 109 PASSED — EMPTY EXTERNAL DB_PASSWORD REJECTED BY REAL COMPOSE

Owner ran the guarded, non-deploying negative test from separate review checkout `/home/ccpcadmin/ccpc-pr29-review` on the NEW `ccpcadmin@ccpcerp-prod` host. The command guarded the original checkout at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, review checkout at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`, clean branches and absent review `.env`. It created a temporary private directory and `compose.env` containing only `DB_PASSWORD=`, sourced the opt-in dedicated config/Compose wrapper with explicit dummy image/tag, and checked that real `ccpc_compose config --quiet` failed with the specific required-password message while keeping the expanded Compose configuration and error details out of terminal output.

Terminal output:

```text
PASS: Empty database password correctly rejected
## security/dedicated-prod-external-env-2026-10-23...origin/security/dedicated-prod-external-env-2026-10-23
ccpcadmin@ccpcerp-prod:~$
```

**Passed as terminal-reported:** empty **value**, not merely unset variable, fails the real dedicated Compose interpolation guard. The owner paste again contains a garbled middle portion of the command; the two final outcomes and returned shell prompt are coherent, but no claim that the exact source command bytes were independently reconstructed. Temporary dummy directory removal was specified via narrow EXIT trap; it was not independently inventoried. **No real secrets or Docker service start, build, database migration, data restoration or production modification.**

**Independently verified current GitHub state:** draft PR #29 remains OPEN/DRAFT/UNMERGED at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`, dependent on draft PR #27 OPEN/DRAFT/UNMERGED at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. Original new-host checkout remains pinned to PR #27; separate review checkout remains on PR #29.

**Next release-safety issue discovered in source review (NOT fixed, NOT runtime-tested):** `scripts/modules/deployment.sh:deploy_release` still calls `deploy_containers` → `verify_containers` → `run_migrations` → `health_check` in order. In the dedicated path, `scripts/modules/env.sh:restore_env` deliberately emits a warning and returns without restoring a file, because there is no dedicated `.env` backup; the other modules call this helper on deployment, container-state and migration failure, then abort. No atomic automatic rollback of containers, images, volumes, or Frappe database changes exists in that path. **Success of Steps 106–109 does not authorize a deployment or establish recoverability.** A reviewed, operator-driven backup/restore and rollback strategy—including migration failure handling, image provenance and volumes—must precede any live rollout; do not switch over production on these static checks alone.

**Recommended next single Step 110:** before any Docker operation, inspect the **effective named volumes, bind mounts and Compose project namespace** on the separate PR #29 review checkout, using only another temporary dummy external environment file and fixed-output Python JSON assertions; do not print the entire Compose file or interpolate real credentials. This will inform the backup/restore and project-isolation plan. No merges or host changes beyond the already authorized isolated review tests.

## 2026-10-23 STEP 108 PASSED BY OPERATOR OUTPUT — EFFECTIVE DEDICATED COMPOSE JSON ASSERTIONS

Operator executed guarded, non-deploying Step 108 from the **separate** PR #29 review checkout `/home/ccpcadmin/ccpc-pr29-review` on NEW host `ccpcadmin@ccpcerp-prod`. The command checked the untouched original checkout pinned to PR #27 commit `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, clean review checkout pinned to PR #29 commit `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`, and absence of review `.env`. It used a `mktemp -d` directory, disposable `DB_PASSWORD=CCPC_DUMMY_CONFIG_ONLY` file, sourced `scripts/config.sh`, `scripts/lib.sh`, `scripts/modules/docker.sh`, and piped actual `ccpc_compose config --format json` directly into a fixed-output Python verifier, not displaying expanded Compose config. Terminal output:

```text
PASS: Frontend loopback-only port
PASS: No other published host ports
PASS: All application images use the expected name and tag
PASS: External dummy database password correctly mapped
PASS: Step 108 validation completed
## security/dedicated-prod-external-env-2026-10-23...origin/security/dedicated-prod-external-env-2026-10-23
ccpcadmin@ccpcerp-prod:~$
```

**Passed as terminal-reported:** effective Docker Compose model defines exactly one `127.0.0.1:8080` frontend publication; no other service publishes host ports; the seven CCPC application services use `ccpcerp:review-only-tag`; and the merged DB service contains `MYSQL_ROOT_PASSWORD=CCPC_DUMMY_CONFIG_ONLY` loaded from the protected external dummy file. Git worktree reports clean. The pasted interactive command text includes a garbled/truncated portion after the scratch-file definition; the expected validation messages are coherent but do **not** independently establish an exact unabridged command byte sequence. Temporary file removal was specified by an EXIT trap, not independently inventoried. No real credentials, Docker up/build, migration, restore, firewall/DNS edit or cutover performed.

**GitHub state reverified:** draft PR #29 `security/dedicated-prod-external-env-2026-10-23` OPEN/DRAFT/UNMERGED at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`; parent draft PR #27 OPEN/DRAFT/UNMERGED at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`.

**Next one Step 109 — negative test for an explicitly EMPTY password through the protected external file:** only in the isolated review checkout, recheck both Git branch/commits/clean status and no `.env`; create temporary `0700` directory plus `0600` external environment file containing *only* `DB_PASSWORD=`. Unset ambient `DB_PASSWORD` and set explicit `CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls`, `CUSTOM_IMAGE=ccpcerp`, `CUSTOM_TAG=review-only-tag`. Source reviewed modules; run `ccpc_compose config --quiet` capturing combined output **in memory without displaying it**, expect **nonzero** and the specific `Dedicated production requires a nonempty DB_PASSWORD` interpolation error. Print only fixed PASS/FAIL, exit 1 on any unexpected result; narrow EXIT trap deletes only dummy file/directory. This proves empty-value handling under real Compose; it does not measure password strength or runtime secret safety. Do not provision real secrets or run live services.

**Outstanding approval/release gates:** Independent PR review, implementation and validation of real secret generation/protection/off-host recovery, failure/rollback/migrations/backup plan, image provenance, runtime networking/TLS and actual deployment approval. Existing PROD/DEV and pinned original new-host checkout remain out of scope.

## 2026-10-23 STEP 107 PASSED BY OPERATOR OUTPUT — REAL COMPOSE PARSED EXTERNAL DUMMY CONFIG

Owner executed Step 107 in a guarded child shell on the **new dedicated** `ccpcadmin@ccpcerp-prod` host from isolated PR #29 checkout `/home/ccpcadmin/ccpc-pr29-review`; supplied resulting terminal:

```text
PASS: Dedicated Compose model parsed with external dummy credentials
## security/dedicated-prod-external-env-2026-10-23...origin/security/dedicated-prod-external-env-2026-10-23
ccpcadmin@ccpcerp-prod:~$
```

**Passed as terminal-reported:** Docker Compose's real `config --quiet` accepted the five-file `dedicated-pre-tls` model with `CCPC_DEDICATED_ENV_FILE` pointing to temporary, 0600, locally created `DB_PASSWORD=CCPC_DUMMY_CONFIG_ONLY` under private `mktemp -d` directory, and `CUSTOM_IMAGE=ccpcerp`, `CUSTOM_TAG=review-only-tag`. The originating command included pinned commit and clean-worktree checks, `unset DB_PASSWORD`, sourced reviewed `scripts/config.sh`, `scripts/lib.sh` and `scripts/modules/docker.sh`, called `ccpc_compose config --quiet`, and had a trap removing only temporary dummy file/directory. **Transcript qualification:** the owner's pasted interactive command contains a garbled/truncated line near the end, but the complete expected success line, clean branch-tracking status and returned shell prompt are present. Avoid claiming independent proof of the exact full command byte sequence or of post-test removal beyond intended trap. No real credentials or Docker deployment involved.

**Independently checked GitHub:** stacked [draft PR #29](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/29) OPEN/DRAFT/UNMERGED at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`, parent draft PR #27 at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. This validation is **Compose parsing only**, not proof that image identity, loopback-only host port and MariaDB password interpolation are correct in effective JSON, nor actual runtime isolation.

**Next one Step 108 — non-deploying effective model assertions on new host only:** repeat a guarded isolated PR #29 `ccpc_compose config --format json` with private temporary external dummy secret, `set -o pipefail`, and pipe **directly** to a local Python JSON validator (never dump expanded Compose config). Assert exactly the expected published frontend port `127.0.0.1:8080:8080/tcp`, no host-published ports for other services, all seven Frappe/ERPNext services using `ccpcerp:review-only-tag` instead of fallback images, and MariaDB `MYSQL_ROOT_PASSWORD` equal to **known dummy** `CCPC_DUMMY_CONFIG_ONLY`. Print only static PASS/FAIL labels. The dummy file must remain external to both checkout directories, owned by user, 0600 under 0700 temp directory, and be deleted by narrowly scoped EXIT trap. No production password, environment dump, `docker compose up`, changes to originals/old PROD+DEV, firewall/DNS, migrations/restoration, merge or cutover.

## 2026-10-23 STEP 106 PASSED — PINNED PR #29 REGRESSIONS PASS ON NEW HOST, NO DOCKER INVOCATION

Owner ran the guarded test on **new** `ccpcadmin@ccpcerp-prod`, within separately checked-out `/home/ccpcadmin/ccpc-pr29-review`. Operator command checked original `/home/ccpcadmin/ccpc-frappe-deployment` remains at original clean PR #27 branch `security/dedicated-production-pre-tls-2026-10-23` HEAD `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`; isolated review remains clean on PR #29 branch `security/dedicated-prod-external-env-2026-10-23` HEAD `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`, with no checkout `.env`. Output:

```text
PASS: Five Bash files passed syntax validation
PASS: owner-only external environment file accepted
PASS: rejected relative path
PASS: rejected file inside checkout
PASS: rejected symlink
PASS: rejected world-readable file
PASS: rejected world-searchable parent
PASS: rejected ambient DB_PASSWORD
PASS: rejected missing explicit image tag
PASS: rejected missing explicit image name
PASS: rejected wrong image name
PASS: dedicated Compose uses protected external env file
PASS: rejected dedicated .env backup
PASS: rejected dedicated .env editing
PASS: dedicated recovery never copies a checkout .env
[INFO] Dedicated profile: external credentials; no .env copy or update
PASS: dedicated release skips .env backup/edit and exports explicit tag
PASS: legacy-lan Compose invocation unchanged
PASS: dedicated external environment regressions
PASS: PR #29 security regression suite completed
## security/dedicated-prod-external-env-2026-10-23...origin/security/dedicated-prod-external-env-2026-10-23
```

**Passed:** Bash syntax and all checked-in test assertions on the actual review checkout, with built-in mocked Docker and disposable `TEST_PLACEHOLDER_NOT_REAL` credential fixture. The owner pasted a garbled portion of the interactive command text but coherent, full expected test output; treat success as terminal-reported, not a reconstructed source command. No Docker Compose engine called by this test, no services started, and no real credentials used. GitHub independently verified PR #29 remains **OPEN/DRAFT/UNMERGED** at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`.

**Next one Step 107 — approved, non-deploying REAL Docker Compose model evaluation from isolated PR #29 checkout only.** Guard both repository commits/branches/clean status; require review checkout `.env` absent; create a **temporary** private `mktemp -d` directory outside both checkouts with `0700` directory and `0600` `compose.env` containing only `DB_PASSWORD=CCPC_DUMMY_CONFIG_ONLY`, never production credentials. Use the GitHub-reviewed `scripts/config.sh`, `scripts/lib.sh`, and `scripts/modules/docker.sh` sourced in a subshell, explicit `CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls`, `CCPC_DEDICATED_ENV_FILE` pointing to disposable file, `CUSTOM_IMAGE=ccpcerp`, `CUSTOM_TAG=review-only-tag`, and `unset DB_PASSWORD`. Run `ccpc_compose config --quiet`; optionally pipe `ccpc_compose config --format json` directly to a Python checker to assert frontend 127.0.0.1:8080 only, no DB/Redis exposed, all application images `ccpcerp:review-only-tag`, and MariaDB receives dummy password. **Never print expanded Compose JSON/environment or real secrets.** Bash trap removes *only* this temporary dummy file/directory; no deletion of either checkout. If guard or validation fails, stop and inspect only nonsecret output. User must supply terminal evidence; until then PR #29's real Compose resolution is **unverified**.

**Boundaries unchanged:** no `docker compose up`, build, migrate, restore, actual secret provisioning, old shared PROD/DEV changes, DNS/firewall, PR merges, or live traffic cutover without separate approval.

## 2026-10-23 STEP 105 PASSED — PR #29 REVIEW WORKTREE CHECKED OUT CLEANLY

Operator executed the approved, guarded checkout command on the separate NEW-host directory `/home/ccpcadmin/ccpc-pr29-review`. Guard clauses required the original `/home/ccpcadmin/ccpc-frappe-deployment` to be clean at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, branch `security/dedicated-production-pre-tls-2026-10-23`, and review clone to be a non-symlink, expected GitHub origin, branch `security/dedicated-prod-external-env-2026-10-23`, pinned HEAD `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`, with empty working root except `.git`. No STOP printed; checkout via `git restore --source=HEAD --staged --worktree -- .` completed and returned:

```text
## security/dedicated-prod-external-env-2026-10-23...origin/security/dedicated-prod-external-env-2026-10-23
```

**Pass:** checkout of PR #29's source into **separate review tree** with no modified/untracked files shown. Guarded command makes no changes to original source tree. GitHub connector independently confirmed PR #29 still OPEN/DRAFT/UNMERGED at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`; ref matches. No Docker service, database, secret file, merge, or deployment was performed.

**Next one Step 106 — guarded, credential-free checked-in regression test on NEW host:** confirm review and original HEAD/branch and both clean worktrees; confirm review `.env` absent; `bash -n` the five exact source/test files; then, from the review clone only, invoke `env -u DB_PASSWORD -u CCPC_DEDICATED_ENV_FILE -u CCPC_DEPLOYMENT_PROFILE -u CUSTOM_TAG -u CUSTOM_IMAGE -u IMAGE_NAME bash tests/test_dedicated_env_security.sh`. The GitHub-reviewed test sources libs, stubs Docker with a shell function, makes a `mktemp -d` scratch directory and writes only `DB_PASSWORD=TEST_PLACEHOLDER_NOT_REAL` inside it; its `EXIT` trap deletes **only that scratch directory**. It checks protected path/mode, rejection rules, image/tag selection, no dedicated `.env` backups, and legacy Compose unchanged; no live Docker Compose is executed. Print its PASS/FAIL output, then confirm clean review Git status; stop on any failure. **Do not** run deployment scripts, Docker up/build, use real credentials, change either checkout, touch shared live PROD/DEV, DNS/firewall, or restore/migrate/cut over.

**Test scripts not yet run on the NEW host:** awaiting owner Step 106 terminal evidence. Docker Compose merge test for PR #29 remains pending and must use a disposable, external, correctly permissioned environment *after* Step 106.

## 2026-10-23 STEP 104 PASSED — PR #29 REVIEW REPOSITORY CLONED WITHOUT CHECKOUT

Owner manually ran the guarded, read-only Git object clone command on **new** host `ccpcadmin@ccpcerp-prod`, targeting only `$HOME/ccpc-pr29-review`. Terminal reports Git remote enumeration / transfer / delta resolution at 100% and:

```text
Cloning into '/home/ccpcadmin/ccpc-pr29-review'...
Receiving objects: 100% (12402/12402), 10.53 MiB | 4.30 MiB/s, done.
Resolving deltas: 100% (6436/6436), done.
Review branch:
security/dedicated-prod-external-env-2026-10-23
Review commit:
bd92ade7ac859b9f6b21b157bdc1629e93f4540c
```

**Verified:** new review clone's terminal-reported branch and HEAD match expected pinned GitHub PR #29; connector independently reverified draft PR #29 remains OPEN/DRAFT/UNMERGED at that HEAD, based on draft PR #27 at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. Clone command specified `--no-checkout`, so **worktree files were not intentionally materialized**. The pasted interactive terminal command text had a garbled/truncated portion; resulting Git output is coherent, but **re-run all safety guards before a file checkout**. Owner has not run a PR #29 Compose test and no dummy or real password was created.

**Next Step 105 — operator-only guarded source-file checkout, in review clone only:** verify the **original** `$HOME/ccpc-frappe-deployment` is still on branch `security/dedicated-production-pre-tls-2026-10-23` at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f` and has zero `git status --porcelain` output; verify review clone HEAD `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`, branch `security/dedicated-prod-external-env-2026-10-23`, origin `git@github.com:ccpcerp/ccpc-frappe-deployment.git`, and root has **no entries except `.git`**. STOP on any mismatch. Only then `git -C "$review" restore --source=HEAD --staged --worktree -- .`, followed by `git -C "$review" status --short --branch`. A clean branch-tracking line with no changed files is expected. This performs *Git source checkout only*, not Docker, secret provisioning, service management, merge, or deployment. One operator step at a time.

**Strict boundaries:** No changes to original cloned deployment code, old shared PROD+DEV, credentials, Docker containers, databases, firewall/DNS, or production cutover. Do not assume the worktree is empty simply because `--no-checkout` was requested; test before restoring any files.

## 2026-10-23 STEP 104 OWNER APPROVAL — SEPARATE PR #29 REVIEW-ONLY CLONE, NO CHECKOUT YET

Owner explicitly replied "Approved" to a **separate, temporary review checkout on the NEW `ccpcerp-prod` server for credential-free, non-deploying Compose tests of draft PR #29**. This authorizes a separate *test directory only*, not updating the existing pinned deployment checkout, starting Docker, creating real secrets, changing old PROD/DEV, migrating/restoring, DNS/firewall edits, merging, or a production cutover.

GitHub connector reverified on 2026-10-23: draft PR #29 remains OPEN/DRAFT/UNMERGED on `security/dedicated-prod-external-env-2026-10-23` at `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`. Its base is `security/dedicated-production-pre-tls-2026-10-23`; parent PR #27 is OPEN/DRAFT/UNMERGED at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. The current authoritative Step 103 notes pass of the exact-binary Bash fixtures in a credential-free local test and that *real* Compose validation of PR #29 remains pending.

**Next single operator action, Step 104 (on NEW host only):** use a guarded `git clone --no-checkout --single-branch --branch security/dedicated-prod-external-env-2026-10-23` into the previously vacant `$HOME/ccpc-pr29-review`. Before cloning, verify `$HOME/ccpc-frappe-deployment` HEAD and branch remain exactly `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f` and `security/dedicated-production-pre-tls-2026-10-23`, no modifications/untracked files, and that target does not exist, including no symlink. Use previously verified, read-only `$HOME/.ssh/ccpc_github_deploy_ed25519` identity with `BatchMode=yes`, `IdentitiesOnly=yes`, strict host-key checking and pinned `ssh-ed25519` algorithm. On any STOP or error, do not overwrite or clean anything. A successful `--no-checkout` clone only fetches Git objects; **no worktree checkout or Compose execution**.

After owner supplies terminal output, independently check new review clone's branch, HEAD, and remote before a guarded file checkout, then execute tests with disposable dummy values only. No real `DB_PASSWORD` or `.env` may be created or sent through chat.

## 2026-10-23 STEP 103 PASSED — EXACT GITHUB CODE BLOBS TESTED IN ISOLATED CREDENTIAL-FREE WORKSPACE

Owner requested "Continue" after Step 102. On 2026-10-23 ChatGPT rechecked the GitHub-first workflow, current production-host handoff, draft PR #29 and exact branch HEAD **`bd92ade7ac859b9f6b21b157bdc1629e93f4540c`**. PR #29 remains **OPEN/DRAFT/UNMERGED** with base `security/dedicated-production-pre-tls-2026-10-23` (draft PR #27). Its patch still contains six intended files and no old-host changes.

To eliminate the earlier "tests were reconstructed, not exact" evidence gap, the five executable/supporting Bash files used by `tests/test_dedicated_env_security.sh` were fetched **directly from that exact pinned GitHub commit** and reproduced in a credential-free temporary local Git repository. Independent `git hash-object` compared each local file's **exact bytes** against its GitHub source blob:
- `scripts/lib.sh`: `7f83828f99273445b6b95d171fb9f9b4862c0587`
- `scripts/modules/docker.sh`: `453959daf3b548fa67f8bdc647be0f147acd603e`
- `scripts/modules/env.sh`: `38a6fdef14abc9e61ae8425ab606dce6201290c1`
- `scripts/modules/deployment.sh`: `ab862074235f174bf5de042ea7c6562965a34243`
- `tests/test_dedicated_env_security.sh`: `d09081bf6a7c99af836d261881257debbd698dcb`

All five source files passed actual `bash -n`. The **exact checked-in test script** ran using its built-in mock `docker` function, temporary dummy-only secret and isolated local Git repository; **exit code 0**. PASS assertions covered owner-only 0600/0700 external environment, reject relative/checkout/symlink/world-readable/world-searchable/ambient DB_PASSWORD, require explicit image tag and exact image name, pass environment file path to mocked Docker, forbid dedicated `.env` backup/edit and restore, export correct image/tag, preserve legacy-lan Compose call. No real password was used or displayed.

**Scope limitation:** this tests five exact *Git blobs* in an independently initialized local Git repository, **not** the entire GitHub commit checked out via a remote clone. Docker CLI/Compose and ShellCheck are unavailable in this isolated testing environment; no real Docker Compose model, containers, DB integration, host network, backup/restore or TLS check was performed for PR #29. No new-host action performed. PR #29 description updated to reflect the improved evidence. The full new-host checkout is still pinned to pre-TLS draft PR #27 `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, unchanged.

**Next gate:** perform a non-deploying Compose interpolation/merge test against the exact proposed PR #29 checkout in an *approved isolated test environment* with a **dummy** owner-only external credential file and reviewed image/tag; separately assess failure/rollback handling. Never pull/switch code on the actual new production host, create real credentials, deploy, migrate, restore, change DNS/firewall or touch old PROD+DEV without explicit separate authorization. PR #27 and PR #29 remain unmerged/draft; no production-readiness claim.

## 2026-10-23 STEP 102 REVIEW HARDENING — IMAGE IDENTITY PINNED; DRAFT PR #29 UPDATED AND VERIFIED

After the initial code-only review, source inspection identified that the base Compose image template can fall back to a generic Frappe/ERPNext image if `CUSTOM_IMAGE` is not explicitly selected. The **new-host-only** feature branch now:
- Requires `CUSTOM_IMAGE` to exactly equal the configured `IMAGE_NAME` in the dedicated `ccpc_compose` wrapper, **and** a nonempty explicit `CUSTOM_TAG`.
- Exports `CUSTOM_IMAGE="$IMAGE_NAME"` alongside `CUSTOM_TAG="$IMAGE_TAG"` in the dedicated `deploy_release` path; the old `legacy-lan` path remains unchanged.
- Extends the offline mocked-Docker regression suite to reject absent or mismatched custom image names and check both variables are exported for a reviewed release.
- Updates the external-credentials documentation and draft PR description.

**Latest independently verified GitHub ref and [draft PR #29](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/29):** `security/dedicated-prod-external-env-2026-10-23` HEAD **`bd92ade7ac859b9f6b21b157bdc1629e93f4540c`**, base `security/dedicated-production-pre-tls-2026-10-23` (PR #27), **OPEN/DRAFT/UNMERGED**, **6 changed files, 10 commits**. GitHub PR patches independently refetched and checked for image guard, release export, and tests.

**Test precision:** `bash -n` and mocked regressions in a **local isolated reconstruction** passed including the new image-name tests. The exact GitHub checkout has not been executed in a real, credential-free CI/test environment; no Docker, image build, database, TLS, deployment, or restoration validation performed. Avoid representing this as validated production code.

**Next gate:** independent source-level review and run tests from the exact pinned GitHub review commit in a credential-free test checkout, then review live rollout procedure and dedicated secret storage requirements. The existing dedicated host still has review branch PR #27 checked out at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`; no pull, branch switch, checkout update, `.env`, credential creation, container operation, old PROD/DEV change, DNS/firewall edit, or cutover has been authorized.

## 2026-10-23 STEP 102 CODE-ONLY IMPLEMENTATION COMPLETE — DEDICATED EXTERNAL SECRETS DRAFT PR #29

Owner approved **preparing a separate GitHub-only security change** after Step 101 verified new-host `.env` absent and identified unsafe legacy `.env` backups. ChatGPT used the connected GitHub tools to create branch `security/dedicated-prod-external-env-2026-10-23` **from the exact draft PR #27 HEAD** `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. Branch HEAD verified at **`ea0b7133d2746bca5904a69bab9790b1fa6578a5`**. A separate draft, **[PR #29](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/29)**, is **OPEN/UNMERGED**, head `security/dedicated-prod-external-env-2026-10-23`, base `security/dedicated-production-pre-tls-2026-10-23` (stacked onto OPEN/DRAFT PR #27; no merge to `main`). The GitHub PR patch was fetched and reviewed; code and doc commits were refetched successfully.

**Changes already committed on this review-only branch:**
- `scripts/modules/docker.sh`: exclusively for `CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls`, require explicit absolute `CCPC_DEDICATED_ENV_FILE` outside the checkout, normal file not symlinked, owned by current user mode 0600 with parent directory owned by user mode 0700; reject checkout `.env`, ambient `DB_PASSWORD`, missing explicit `CUSTOM_TAG`. Pass `--env-file` to Compose. Default `legacy-lan` wrapper unchanged.
- `scripts/modules/deployment.sh`: dedicated release skips `.env` backup/rewrite, exports `CUSTOM_TAG` from explicitly chosen image tag in current process only; legacy path still calls existing `backup_env` and `update_env`.
- `scripts/modules/env.sh`: dedicated guard rejects accidental `.env` backup/edit and avoids invalid `restore_env` of a non-existent backup on failure, warning that container/database recovery is separate. Legacy code remains.
- `tests/test_dedicated_env_security.sh`: credential-free mocked-Docker tests for safe external file, paths, modes, symlink, ambient variable, tag, env backup/edit rejection, release path and legacy invocation.
- `docs/04-operations/dedicated-production-external-credentials.md` explains limitations/secret handling; existing `docs/04-operations/dedicated-production-port-profile.md` now links this stacked review dependency.

**Testing evidence, carefully scoped:** Bash parser (`bash -n`) and the security regression assertions passed in an **isolated local reconstruction of the changed functions** with a mocked `docker` function and dummy password, NOT as a checkout byte-verified against the new GitHub branch. Expected pass cases included 0600/0700, reject relative/checkout/symlink/world-readable/environment password/missing image tag, forbid dedicated `.env` backup/update, no `.env` restore, explicit image tag propagation, and original legacy Compose invocation. A full exact-GitHub-tree test, automated CI, real Docker runtime and database integration have **not** run. Do not claim production readiness.

**Next engineering gate:** independent review of draft PR #29 and direct tests of the exact GitHub checkout in an isolated credential-free environment, including source-level checks, error-path behavior, effective Compose configuration with dummy values, and regression review. Decide/document password provenance/rotation/off-host recovery and safe migration/rollback procedures **before any credential provisioning**. New dedicated host `/home/ccpcadmin/ccpc-frappe-deployment` is **unchanged and remains pinned** to PR #27 commit `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`; **do not pull, switch, merge, or checkout PR #29 there without a separately reviewed plan and owner approval**. Old shared PROD+DEV unaffected. No secret files, containers, builds, data migrations/restores, DNS/firewall changes, or production cutover authorized.

## 2026-10-23 STEP 101 PASSED — .env ABSENT AND GIT-IGNORED; CREDENTIAL FLOW REVIEW REQUIRED

Owner ran the approved read-only new-host check on `ccpcadmin@ccpcerp-prod` and returned exactly:

```text
PASS: No .env path exists in the new-host checkout
PASS: .env is excluded by Git ignore rules
```

**Verified from terminal:** `/home/ccpcadmin/ccpc-frappe-deployment/.env` is absent at this checkpoint (including an existing symlink), and `git check-ignore -q -- .env` succeeds. No real production credential has been created or supplied. Git ignore rules prevent accidental ordinary inclusion in Git, **but are not secret storage protection**.

**Important new GitHub code-review finding before provisioning any secrets:** the checked-out review branch's `scripts/deploy.sh` invokes `deploy_release`, whose `scripts/modules/deployment.sh` calls `backup_env` and `update_env` before deployment. `scripts/modules/env.sh` has `backup_env` run `mkdir -p "$BACKUP_DIR"` and `cp .env "$BACKUP_FILE"` into `backups/env.TIMESTAMP.bak`; `update_env` requires `.env` in checkout and rewrites its `CUSTOM_TAG`. This means **placing `DB_PASSWORD` in checkout `.env` would cause password-containing backup copies** during later deployments, regardless of Git ignore. Simply moving all variables into an external file would *not* work unchanged with the current `update_env` expectation. No current-source modification was made and no execution of `deploy.sh` was authorized. These scripts are not yet approved for the dedicated host; old shared PROD/DEV must remain untouched.

**Required next engineering decision / Step 102:** before creating real credentials, review and choose a dedicated-host **opt-in** credential and deployment flow that keeps the DB secret outside the Git checkout, maintains restrictive file ownership and access, prevents untracked backup/log secret copies, accommodates the current `.env` and `CUSTOM_TAG` release mechanism or safely replaces it, and preserves existing `legacy-lan` behavior. Prefer a focused, GitHub-only implementation on a separate review branch with static tests and explicit owner authorization **before** any new-host rollout. A stop/go approval for this **code-only security change** is needed; do not infer authorization to change server secrets from successful read-only tests.

**Outstanding release gates:** PR #27 `security/dedicated-production-pre-tls-2026-10-23` remains OPEN/DRAFT/UNMERGED at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. Passing local Compose syntax and port assertions is not production-ready: no runtime binding check, TLS/reverse proxy, backup/restore rehearsal, credential mechanism, app image validation, or cutover approval. No Docker up/build, migrations/restores, old-host changes, firewall/DNS changes, or live user traffic move.

## 2026-10-23 STEP 100 PASSED — MISSING DB_PASSWORD ENFORCEMENT CONFIRMED; SECRET INVENTORY NEXT

Owner provided the expected exact status after manually running the Step 100 negative test on NEW `ccpcadmin@ccpcerp-prod` with the five-file dedicated profile, `env -u DB_PASSWORD`, `--env-file /dev/null`, dummy `CUSTOM_TAG=config-check-only`, `config --quiet`, error-output captured without display:

```text
PASS: Missing DB_PASSWORD is rejected for dedicated production
```

The result supports a guarded assertion that Compose returned nonzero and its captured diagnostic contained `Dedicated production requires a nonempty DB_PASSWORD`. **Passed for missing/unset password only**; no real credential has been entered, printed, stored, or verified, and the actual deployment remains unapproved. This does not independently test an explicitly empty password, password strength, secret file ownership or backup, nor live database behavior. Connected GitHub also verified `.gitignore` on the source branch includes `.env`, but its existence or absence on the new host is not yet known. Draft PR #27 remains OPEN/DRAFT/UNMERGED at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`.

**Next single Step 101 (read-only, NEW host only):** inspect whether checkout `.env` is absent, a regular existing path, or a symlink; independently verify `.env` is ignored by Git. Never display the contents of any `.env`. Suggested command:
```bash
(
  repo="$HOME/ccpc-frappe-deployment"
  if [ -L "$repo/.env" ]; then
    echo "STOP: .env is a symlink; inspect before making any changes"
  elif [ -e "$repo/.env" ]; then
    echo "NOTICE: .env already exists; do not overwrite"
  else
    echo "PASS: No .env path exists in the new-host checkout"
  fi

  if git -C "$repo" check-ignore -q -- .env; then
    echo "PASS: .env is excluded by Git ignore rules"
  else
    echo "STOP: .env is not ignored by Git"
  fi
)
```
This is a **presence/ignore-status check only**, not an instruction to create or edit secrets in the repository. If a file exists or is symlinked, stop and review safely without dumping it. Design owner-controlled production secret provisioning and Compose environment delivery explicitly before any deployment. Do not ask the owner to paste passwords into chat; no containers, migration, data restoration, firewall/DNS edits, old PROD/DEV changes or cutover.

## 2026-10-23 STEP 99 PASSED BY REPORTED ASSERTIONS — MERGED COMPOSE PORT BINDINGS ARE LOOPBACK-ONLY

On the NEW `ccpcadmin@ccpcerp-prod` checkout of pinned branch `security/dedicated-production-pre-tls-2026-10-23` at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, the operator ran the approved Step 99: Compose `config --format json` with `--env-file /dev/null` and disposable command-scoped `DB_PASSWORD=CCPC_CONFIG_CHECK_NOT_REAL`, `CUSTOM_TAG=config-check-only`, piping structured output directly into a Python assertion script. Terminal showed both expected checks:

```text
PASS: Frontend binds only 127.0.0.1:8080
PASS: No other services publish host ports
```

**Passed as reported:** merged Compose model was accepted and the Python validator reported precisely one frontend TCP mapping on `127.0.0.1:8080` → `8080`, with no other host-published ports from any service. **Transcript qualification:** the owner's pasted command has an apparently truncated/garbled line near the Python `frontend_ok` expression (`)   sys.exit(1): Could not validate Compose port information")`); this is not interpreted as a separate validation failure, since the two PASS outputs were produced, but the exact unabridged pasted script cannot be independently reconstructed from that transcript. No full interpolated Compose output was shown and no real credentials were supplied. This is a **static merged-model assertion only**—not a live Docker binding, UFW isolation, TLS verification, or production deployment. GitHub PR #27 remains open/draft/unmerged at the checked commit.

**Next Step 100 — verify the required dedicated-host DB password safeguard rejects an unset value (NEW host only).** Run `docker compose --env-file /dev/null ... config --quiet` with `DB_PASSWORD` deliberately removed via `env -u DB_PASSWORD`, but capture all errors into a temporary Bash variable (do not print). Check for the exact message `Dedicated production requires a nonempty DB_PASSWORD` and a nonzero exit. Print only fixed PASS/FAIL status. `CUSTOM_TAG=config-check-only` remains disposable, there is no real DB password, and the full merged config must never be displayed. This is a negative validation test; a *correct rejection* is PASS. If negative test fails, stop and investigate before configuring any secret.

Suggested controlled command:
```bash
(
  cd "$HOME/ccpc-frappe-deployment" || exit 1
  [ "$(git rev-parse --verify HEAD)" = "0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f" ] || { echo "STOP: Unexpected Git commit"; exit 1; }
  result=$(env -u DB_PASSWORD CUSTOM_TAG=config-check-only docker compose --env-file /dev/null \
    -f compose.yaml \
    -f overrides/compose.mariadb.yaml \
    -f overrides/compose.redis.yaml \
    -f overrides/compose.lan-production.yaml \
    -f overrides/compose.dedicated-pre-tls.yaml \
    config --quiet 2>&1)
  code=$?
  if [ "$code" -ne 0 ] && [[ "$result" == *"Dedicated production requires a nonempty DB_PASSWORD"* ]]; then
    echo "PASS: Missing DB_PASSWORD is rejected for dedicated production"
  else
    echo "FAIL: Password safeguard not verified"
    exit 1
  fi
)
```

**Safety boundaries:** do not echo `$result`, show `.env`, reveal/enter a real DB password, run `docker compose up`, build, deploy, migrate, restore, change DNS/firewall, touch the existing PROD/DEV host, or cut over users. A pass would prove only missing-value rejection under this dummy validation environment, not strength, lifecycle, or secure production provisioning.

## 2026-10-23 STEP 98 PASSED — FIVE-FILE COMPOSE MODEL PARSED WITH DISPOSABLE PLACEHOLDERS

Owner ran the approved Step 98 on the NEW `ccpcadmin@ccpcerp-prod` host: guarded exact pinned HEAD `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, disposable command-scoped `DB_PASSWORD=CCPC_CONFIG_CHECK_NOT_REAL` and `CUSTOM_TAG=config-check-only`, `docker compose --env-file /dev/null` with all five files in their approved order, and `config --quiet`. Terminal output:

```text
PASS: Five-file Compose model parsed with disposable placeholders
```

**Passed:** Compose accepts the opt-in five-file syntax/interpolation/merge structure when dummy values are supplied and without attempting deployment. This is **not** proof that port publishing is restricted to loopback, real production credentials are provisioned securely, containers can start, app image is correct or TLS works. The configuration was not printed and the placeholder was not persisted. GitHub confirms draft PR #27 is still open/unmerged at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`; `overrides/compose.dedicated-pre-tls.yaml` uses `ports: !override` to prescribe `127.0.0.1:8080:8080/tcp`. Redis and MariaDB overrides do not prescribe host-published database/Redis ports.

**Next single Step 99 — inspect only effective Compose published ports on the NEW host.** Re-run `docker compose --env-file /dev/null ... config --format json` using only the disposable command-scoped placeholder password and image tag, pipe its JSON **directly to a local Python parser** rather than printing expanded config, and assert: frontend has precisely one `127.0.0.1:8080` → `8080/tcp` mapping; no other services have host-published ports. Parse and print only safe fixed PASS/FAIL messages without dumping JSON, `.env`, passwords or environment variables. Use `set -o pipefail` so Compose errors cannot be masked by the parser. If assertions fail, STOP before further operations and review without displaying secrets. No containers, databases, migrations, restores, firewall/DNS changes or old PROD/DEV/cutover operations authorized.

## 2026-10-23 STEP 97 PASSED — DEDICATED PROFILE FILE ORDER AND HEALTH TARGET VERIFIED

On `ccpcadmin@ccpcerp-prod`, the operator ran the approved isolated child-shell `CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls` test sourcing only the reviewed `scripts/config.sh` and printing solely Compose filenames and the health target. Terminal output:

```text
Compose file order:
compose.yaml
overrides/compose.mariadb.yaml
overrides/compose.redis.yaml
overrides/compose.lan-production.yaml
overrides/compose.dedicated-pre-tls.yaml
Health target: http://127.0.0.1:8080
```

**Passed:** five files selected in the intended order, with the dedicated opt-in override last and local health target `127.0.0.1:8080`. This does **not** verify the effective merged Compose model, that the frontend has only a loopback binding, real secret provisioning, database configuration, or running Docker behavior. Existing old-host legacy profile remains out of scope and no services were started. GitHub verified draft PR #27 stays OPEN/UNMERGED at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`.

**Next Step 98 — non-deploying syntax/model check on the new host using a disposable, clearly non-production dummy password and image tag, never the real `DB_PASSWORD`:** inspect only the already reviewed five files in their verified order with `docker compose --env-file /dev/null ... config --quiet`. Supplying `--env-file /dev/null` avoids automatic parsing of any `.env` in the checkout, and `config --quiet` avoids printing interpolated configuration. A one-command process environment override provides `DB_PASSWORD=CCPC_CONFIG_CHECK_NOT_REAL` and `CUSTOM_TAG=config-check-only`. Ensure exact verified Git HEAD first. Do not persist placeholders in `.env` or treat resulting model as ready to deploy.

Suggested operator command:
```bash
(
  cd "$HOME/ccpc-frappe-deployment" || exit 1
  [ "$(git rev-parse --verify HEAD)" = "0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f" ] || { echo "STOP: Unexpected HEAD"; exit 1; }
  DB_PASSWORD=CCPC_CONFIG_CHECK_NOT_REAL CUSTOM_TAG=config-check-only \
  docker compose --env-file /dev/null \
    -f compose.yaml \
    -f overrides/compose.mariadb.yaml \
    -f overrides/compose.redis.yaml \
    -f overrides/compose.lan-production.yaml \
    -f overrides/compose.dedicated-pre-tls.yaml \
    config --quiet && echo "PASS: Five-file Compose model parsed with disposable placeholders"
)
```

**Strict limitation:** This is syntactic/Compose merge validation only; passing cannot demonstrate actual firewall isolation or safely provisioned credentials. Do not run `docker compose up`, generate real secrets, print `docker compose config` or environment values, deploy, restore, migrate, open ports, modify DNS/firewall/old PROD+DEV, or cut over production traffic. Review exact Step 98 output before moving to projected port inspection, still without real secrets.

## 2026-10-23 STEP 96 PASSED — DOCKER COMPOSE VERSION SUPPORTS !override; PROFILE SELECTION NEXT

Owner executed `docker compose version` on the new `ccpcadmin@ccpcerp-prod` host and supplied exact output:
```text
Docker Compose version v5.6.1
```
**Verified operator evidence:** Docker Compose CLI reports v5.6.1. The official Docker Compose merge documentation states that `!override` requires Compose v2.24.4 or later (https://docs.docker.com/reference/compose-file/merge/). Therefore the host-reported Compose version meets the documented minimum for the reviewed `overrides/compose.dedicated-pre-tls.yaml` use of `ports: !override`. This is a *version prerequisite only*, not a successful merged/effective Compose-model test. GitHub draft PR #27 remains OPEN/UNMERGED at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`; its profile is not production-deployed.

**Next one Step 97 (on NEW host only; no secrets):** evaluate only the already GitHub-reviewed `scripts/config.sh` in an isolated child Bash shell with `CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls`; print only selected Compose file paths and nonsecret host-local health target, not environment variable dumps:
```bash
CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls bash -c '
  source "$1" || exit 1
  printf "Compose file order:\n"
  for ((i=1; i<${#COMPOSE_FILE_ARGS[@]}; i+=2)); do
    printf "%s\n" "${COMPOSE_FILE_ARGS[i]}"
  done
  printf "Health target: %s\n" "$HEALTHCHECK_URL"
' _ "$HOME/ccpc-frappe-deployment/scripts/config.sh"
```
Expected five files, last `overrides/compose.dedicated-pre-tls.yaml`, and `Health target: http://127.0.0.1:8080`. `source` executes the vetted configuration script only in the isolated shell; do not source arbitrary new files or print `.env`, `DB_PASSWORD`, interpolated Compose model, SSH keys, or other credentials. Do not yet run `docker compose config` on full project without an approved secure secret-handling procedure.

**No deployment permission:** no containers, Docker changes, migrations, database restore, firewall/DNS edits, old PROD/DEV modifications, or production traffic cutover.

## 2026-10-23 STEP 95 PASSED — CONFIG SCRIPT BASH SYNTAX VERIFIED; COMPOSE VERSION NEXT

Owner ran `bash -n "$HOME/ccpc-frappe-deployment/scripts/config.sh" && echo "PASS: scripts/config.sh syntax"` on new dedicated `ccpcerp-prod` and reported `PASS: scripts/config.sh syntax` with return to shell prompt. **Verified from terminal:** Bash parser accepted the checked-out config script. This does not execute the script, validate selected `CCPC_DEPLOYMENT_PROFILE` behavior, evaluate Compose interpolation, verify port bindings, or prove deployability.

Connected GitHub checked draft PR #27 on 2026-10-23: still OPEN/DRAFT/UNMERGED at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. Its `overrides/compose.dedicated-pre-tls.yaml` uses Compose's `!override` tag for loopback frontend binding and a required `DB_PASSWORD` interpolation. **Do not run `docker compose config` or print an expanded Compose model before reviewing secret handling.**

**Next Step 96, one read-only operator check on the NEW host:**
```bash
docker compose version
```
Report the version or exact error so Compose `!override` support can be assessed before any model validation. Version command does not launch the stack, manipulate containers, or read `.env`. Preserve no-change boundaries: no `docker compose up`, deployment, migration, restore, credential display, DNS/firewall edits, old PROD/DEV changes, or cutover.

## 2026-10-23 STEP 94 PASSED — DEDICATED-HOST CHECKOUT COMPLETE; REVIEW VALIDATION NEXT

Owner manually executed the guarded new-host checkout command at `ccpcadmin@ccpcerp-prod`, requiring exact current branch `security/dedicated-production-pre-tls-2026-10-23`, pinned local HEAD `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, and no pre-existing worktree files outside `.git`. The guarded command then ran `git -C "$repo" restore --source=HEAD --staged --worktree -- .`, followed by `git status --short --branch`. Owner supplied output:

```text
## security/dedicated-production-pre-tls-2026-10-23...origin/security/dedicated-production-pre-tls-2026-10-23
```

**Passed:** no STOP guard was printed; Git status shows the expected branch tracking its remote with no modified/untracked files listed. These are checked-out *Git source files only* in `/home/ccpcadmin/ccpc-frappe-deployment`. No Docker Compose model evaluated, service started, database operation, production deployment or old-host modification performed. GitHub independently reconfirmed draft PR #27 remains OPEN/UNMERGED at the pinned SHA, and inspected `scripts/config.sh`, `overrides/compose.dedicated-pre-tls.yaml`, and the dedicated pre-TLS policy at that branch.

**Next Step 95 — read-only Bash parser check on the NEW host only:**
```bash
bash -n "$HOME/ccpc-frappe-deployment/scripts/config.sh" && echo "PASS: scripts/config.sh syntax"
```
This checks syntax without executing/sourcing the script or interpolating secrets. After observing the output, plan a separately controlled, secrets-safe Compose effective-model check when the appropriate configuration and permission are in place. Do not print `.env`, `DB_PASSWORD`, private keys or interpolated Compose configuration. No `docker compose up`, deployment, migration, restore, DNS, firewall, cutover, or old PROD/DEV operations are authorized.

## 2026-10-23 STEP 93 PASSED — NO PROJECT FILES PRESENT; CONTROLLED SOURCE CHECKOUT NEXT

Owner ran `find "$HOME/ccpc-frappe-deployment" -mindepth 1 -maxdepth 1 ! -name .git -print` on `ccpcadmin@ccpcerp-prod`; terminal returned directly to prompt with **no output**. This verifies, at inspection time, that the just-cloned repository directory contained no root entries other than `.git`. Step 92 independently verified branch `security/dedicated-production-pre-tls-2026-10-23`, HEAD `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, and origin `git@github.com:ccpcerp/ccpc-frappe-deployment.git`. GitHub PR #27 remains OPEN/DRAFT/UNMERGED at that SHA. No checkout performed yet.

**Next Step 94 on NEW host only:** use a read-only command guard to recheck the exact HEAD, branch, and that worktree is still vacant except `.git`, then run `git -C "$HOME/ccpc-frappe-deployment" restore --source=HEAD --staged --worktree -- .` to populate *only* this new-host clone with its already downloaded pinned source. Git's `--no-checkout` clone starts with staged deletions; restoring both index and worktree from pinned HEAD is a non-forced way to materialize the already verified commit without switching branches or reaching the network. If any guard fails, **STOP**; do not overwrite any existing files. Afterwards review status and key tracked files separately. The operator controls execution and must paste output; no claim of successful checkout until then.

Checkout is **not** approval to run Docker Compose, start containers, install ERPNext, migrate/restore any data, alter firewall/DNS, modify the old PROD+DEV host, or cut over production traffic. No live changes are authorized by this milestone.

## 2026-10-23 STEP 92 PASSED — NEW-HOST CLONED BRANCH, HEAD, ORIGIN VERIFIED; CHECKOUT NOT DONE

Owner ran the three read-only Git commands on `ccpcadmin@ccpcerp-prod` in `/home/ccpcadmin/ccpc-frappe-deployment` and provided:
```text
security/dedicated-production-pre-tls-2026-10-23
0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f
git@github.com:ccpcerp/ccpc-frappe-deployment.git
```
These values **exactly match** the intended review branch, full pinned commit and repository origin. Independently verified on GitHub on 2026-10-23, draft PR #27 is still open/unmerged and its branch HEAD remains `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. This verifies the *downloaded Git HEAD*, **not** a checked-out worktree, deployed configuration, or Docker Compose runtime.

**Next single Step 93 — read-only worktree occupancy guard, on the NEW host only:**
```bash
find "$HOME/ccpc-frappe-deployment" -mindepth 1 -maxdepth 1 ! -name .git -print
```
**Expected:** no output for a clean `--no-checkout` clone. If anything is printed, stop and inspect before selecting a non-destructive checkout approach; do not discard local files. Only after confirmation plan a manual checkout of already downloaded reviewed code to this new host's directory. A Git checkout is **not** authorization to build or start Docker, migrate, restore, deploy, alter databases or backups, or change old live PROD/DEV, DNS, firewall or cutover. Preserve the one-step-at-a-time procedure.

## 2026-10-23 STEP 91 PASSED — NEW-HOST REPOSITORY CLONED WITH NO CHECKOUT

Owner executed on `ccpcadmin@ccpcerp-prod` the guarded `git clone --no-checkout --single-branch --branch security/dedicated-production-pre-tls-2026-10-23` via the dedicated `ccpc_github_deploy_ed25519` SSH identity, targeting the previously vacant `/home/ccpcadmin/ccpc-frappe-deployment`. The owner supplied Git terminal output:

```text
Cloning into '/home/ccpcadmin/ccpc-frappe-deployment'...
remote: Enumerating objects: 12354, done.
remote: Counting objects: 100% (355/355), done.
remote: Compressing objects: 100% (32/32), done.
remote: Total 12354 (delta 338), reused 325 (delta 323), pack-reused 11999 (from 2)
Receiving objects: 100% (12354/12354), 10.52 MiB | 4.19 MiB/s, done.
Resolving deltas: 100% (6407/6407), done.
```

**Verified from owner terminal:** Git completed the object-transfer/delta-resolution steps and returned to the shell without a reported error. Because the clone used `--no-checkout`, normal project working-tree file checkout was intentionally deferred. Local HEAD / branch / origin still require an explicit read-only verification on the new host. Independently, GitHub shows draft PR #27 branch `security/dedicated-production-pre-tls-2026-10-23` at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f` (OPEN/UNMERGED).

**Next one Step 92 (read-only verification, no checkout or changes):**
```bash
git -C "$HOME/ccpc-frappe-deployment" branch --show-current
git -C "$HOME/ccpc-frappe-deployment" rev-parse --verify HEAD
git -C "$HOME/ccpc-frappe-deployment" remote get-url origin
```
Expected branch `security/dedicated-production-pre-tls-2026-10-23`, full commit `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, origin `git@github.com:ccpcerp/ccpc-frappe-deployment.git`. Inspect actual operator output before any checkout or Compose validation. No Docker, containers, services, production records, DEVELOPMENT state, migrations, backups, firewall/DNS or live cutover changed or authorized.

## 2026-10-23 STEP 90 PASSED — NEW-HOST REPOSITORY TARGET AVAILABLE; NO CLONE YET

Owner ran the Step 90 read-only path existence/symlink check on `ccpcadmin@ccpcerp-prod`. Terminal returned exactly `TARGET AVAILABLE: /home/ccpcadmin/ccpc-frappe-deployment`. This confirms the proposed *new-host* directory was not present when checked; no claim is made about filesystem state beyond that check, and no files were created. Step 89 already verified SSH-based private repository read access at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`.

Connected GitHub independently rechecked draft PR #27 on 2026-10-23: `security/dedicated-production-pre-tls-2026-10-23` is still OPEN/UNMERGED with HEAD `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`.

**Next Step 91 — optional operator-executed safe source-only clone on the new host:** guard against a now-occupied path, then `git clone --no-checkout --single-branch --branch security/dedicated-production-pre-tls-2026-10-23` from `git@github.com:ccpcerp/ccpc-frappe-deployment.git` into `$HOME/ccpc-frappe-deployment`, with explicit named `~/.ssh/ccpc_github_deploy_ed25519`, SSH `IdentitiesOnly=yes`, `BatchMode=yes`, `StrictHostKeyChecking=yes`, `HostKeyAlgorithms=ssh-ed25519`. Because `--no-checkout` avoids populating the worktree, the subsequent step must independently verify local HEAD exactly matches expected commit before considering a controlled checkout. This clone only downloads repository objects and writes to the checked-available new-host directory; it is **not deployment approval**. Do not run Compose, Docker build, Frappe, database operations, migrations, backups/restores, DNS/firewall changes, or modify old live PROD/DEV. Clone execution remains operator-controlled; wait for command output.

## 2026-10-23 STEP 89 PASSED — NEW-HOST PRIVATE GITHUB BRANCH READ ACCESS VERIFIED; NO CLONE

Owner executed the exact `GIT_SSH_COMMAND="ssh -i $HOME/.ssh/ccpc_github_deploy_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o HostKeyAlgorithms=ssh-ed25519" git ls-remote --heads git@github.com:ccpcerp/ccpc-frappe-deployment.git security/dedicated-production-pre-tls-2026-10-23` on `ccpcadmin@ccpcerp-prod`. Terminal returned:

```text
0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f        refs/heads/security/dedicated-production-pre-tls-2026-10-23
```

**Passed:** this proves the dedicated new-host SSH key authenticates to GitHub and can read the intended private deployment repository's specific development branch; reported SHA matches GitHub's independently verified branch ref `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. Draft PR #27 is still OPEN/UNMERGED. It does not show a local clone, site deployment, resolved Docker Compose model, or any change to running infrastructure; repository-deploy-key read-only permissions were selected by owner and are not independently checkable through the connected API.

**Next single Step 90:** read-only check whether proposed new-host checkout location `$HOME/ccpc-frappe-deployment` already exists (including symlink) before considering any `git clone`; stop if occupied. Example:
```bash
if [ -e "$HOME/ccpc-frappe-deployment" ] || [ -L "$HOME/ccpc-frappe-deployment" ]; then printf 'TARGET EXISTS: do not overwrite\n'; ls -ld -- "$HOME/ccpc-frappe-deployment"; else printf 'TARGET AVAILABLE: %s\n' "$HOME/ccpc-frappe-deployment"; fi
```
After output is reviewed, prepare a separately approved pinned-branch clone, explicitly scoped to the new host, and verify the checkout HEAD and working-tree status before running any build or Compose validation. No clone, checkout, Docker execution, old production/DEVELOPMENT change, DNS, firewall, database, backup, or cutover is authorized by this read-access milestone.

## 2026-10-23 STEP 88 COMPLETE — GITHUB SSH AUTHENTICATION VERIFIED; STEP 89 REPOSITORY READ CHECK NEXT

Owner provided the exact new-host terminal response after accepting GitHub's official ED25519 host fingerprint on `ccpcadmin@ccpcerp-prod`:
```text
Warning: Permanently added 'github.com' (ED25519) to the list of known hosts.
Hi ccpcerp/ccpc-frappe-deployment! You've successfully authenticated, but GitHub does not provide shell access.
```
The official GitHub ED25519 host fingerprint displayed immediately before confirmation was `SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU`, matching the previously verified expected value. The transcript now confirms SSH server authenticity was checked and the dedicated new-host deploy key was accepted by GitHub for the deployment repository. It does **not** yet show `git ls-remote` read authorization for the exact branch. Do not interpret “does not provide shell access” as an error; this is GitHub's normal successful SSH authentication greeting. The key's read-only setting remains owner-reported, not independently inspected via GitHub deploy-key settings.

**GitHub verified again on 2026-10-23:** draft PR #27 is open and unmerged; branch `security/dedicated-production-pre-tls-2026-10-23` still at `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`.

**Next one read-only action, Step 89, on new host only:**
```bash
GIT_SSH_COMMAND="ssh -i $HOME/.ssh/ccpc_github_deploy_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o HostKeyAlgorithms=ssh-ed25519" git ls-remote --heads git@github.com:ccpcerp/ccpc-frappe-deployment.git security/dedicated-production-pre-tls-2026-10-23
```
Expected one line: `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f refs/heads/security/dedicated-production-pre-tls-2026-10-23` (tab separated). Verify actual terminal output before proceeding. No clone, new deployment, changes to existing production or DEVELOPMENT, DNS, firewall, database, Docker, or cutover have been authorized or carried out.

## 2026-10-23 STEP 88 — OWNER REPORTS GITHUB SSH KEY AUTHENTICATION CONFIRMED; REPOSITORY READ CHECK PENDING

In the continuation supplied by the owner, the final status was **“Confirmed key authentication”** following Step 88's new-host command (`ssh -T -i "$HOME/.ssh/ccpc_github_deploy_ed25519" -o IdentitiesOnly=yes -o HostKeyAlgorithms=ssh-ed25519 git@github.com`). This is an **owner-reported successful GitHub SSH authentication**, not a terminal transcript inspected in this conversation; do not claim that repository read authorization or clone has been proven. Owner previously reported registering the repository-scoped deploy key with write access unchecked.

**GitHub-side verification on 2026-10-23:** draft PR #27 remains **OPEN, UNMERGED** with head branch `security/dedicated-production-pre-tls-2026-10-23`, SHA `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. Draft PR #28 also remains unmerged and out of scope for this Git read test.

**Next single Step 89 on `ccpcadmin@ccpcerp-prod` only:** a noninteractive `git ls-remote --heads` with `GIT_SSH_COMMAND` set to the named per-repository private key and `IdentitiesOnly=yes`, `StrictHostKeyChecking=yes`, `BatchMode=yes`, `HostKeyAlgorithms=ssh-ed25519`, targeting only `git@github.com:ccpcerp/ccpc-frappe-deployment.git` and branch `security/dedicated-production-pre-tls-2026-10-23`. Verify that the reported SHA matches `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f` before considering a later separately reviewed clone. No clone, code execution, deployments, Docker changes, firewall/DNS edits, PROD/DEV changes or cutover authorized.

## 2026-10-23 STEP 87 — OWNER REPORTS READ-ONLY GITHUB DEPLOY KEY ADDED; SSH CONNECTION NOT YET TESTED

Owner explicitly confirmed **“Key added”** after instructions to register the public `ccpc_github_deploy_ed25519.pub` key as repository deploy key `ccpcerp-prod-readonly` in GitHub `ccpcerp/ccpc-frappe-deployment` with `Allow write access` unchecked. This is **owner-reported registration**, not independently confirmed via GitHub settings or a successful new-host SSH attempt; GitHub connector has no deploy-key listing action. Recorded public key fingerprint from Step 85: `SHA256:FLKm7I7nrGrw1f3o6J+PJGzRGMtcuxuNLKw/lWPCMWs`. Do not expose private key or alter Windows inbound SSH key/`authorized_keys`. **Next one test on the new `ccpcerp-prod` only:** `ssh -T -i "$HOME/.ssh/ccpc_github_deploy_ed25519" -o IdentitiesOnly=yes -o HostKeyAlgorithms=ssh-ed25519 git@github.com`. When first prompted about GitHub SSH host authenticity, verify that the ED25519 HOST fingerprint exactly matches official GitHub `SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU` (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints) **before** typing `yes`; stop if different. GitHub's expected success message says authenticated but no shell access (ssh -T exit status 1 may be expected). No clone, Docker, PROD/DEV, DNS, UFW or production deployment authorized.

## 2026-10-23 STEP 86 COMPLETE — PUBLIC DEPLOY KEY RETRIEVED AND FINGERPRINT MATCHED; REGISTRATION PENDING

Owner ran `cat "$HOME/.ssh/ccpc_github_deploy_ed25519.pub"` on new `ccpcerp-prod` and retrieved one `ssh-ed25519` public key with comment `ccpcerp-prod deployment repository`. Independently SHA-256 hashed the provided encoded public-key blob: fingerprint **`SHA256:FLKm7I7nrGrw1f3o6J+PJGzRGMtcuxuNLKw/lWPCMWs`**, matching the server's prior `ssh-keygen -lf` result. The private key (`~/.ssh/ccpc_github_deploy_ed25519`) remains secret, was not viewed or transmitted. **GitHub registration NOT yet confirmed.** Step 87: owner must add **only the public `.pub` key** under `ccpcerp/ccpc-frappe-deployment` → Settings → Deploy keys → Add deploy key; suggested title `ccpcerp-prod-readonly`; **leave Allow write access unchecked**. Confirm saved entry before testing the SSH remote. GitHub connected tools do not expose deploy key registration, so this is a manual permission step. Repo is private, do not add an account-wide SSH key or a PAT for this purpose. No checkout, infrastructure changes, deployment, DNS edits, firewall changes or alterations to `authorized_keys`.

## 2026-10-23 STEP 85 COMPLETE — NEW GITHUB DEPLOY KEY PAIR CREATED LOCALLY

Owner ran the guarded Ed25519 `ssh-keygen` command on dedicated new `ccpcerp-prod` while logged in as `ccpcadmin`. Terminal returned `256 SHA256:FLKm7I7nrGrw1f3o6J+PJGzRGMtcuxuNLKw/lWPCMWs ccpcerp-prod deployment repository (ED25519)`. This shows the new SSH **public-key fingerprint** was printed successfully from `~/.ssh/ccpc_github_deploy_ed25519.pub`; counterpart private key is `~/.ssh/ccpc_github_deploy_ed25519`. The guarded script used `umask 077` and no passphrase for intended noninteractive repository-only read access. **No private key contents have been displayed, copied into chat, or committed.** The new key is not yet registered with GitHub, so outbound read access is not verified. Existing Windows administrator key and server `authorized_keys` should remain unchanged. **Next safe Step 86:** display only the new *public* key with `cat "$HOME/.ssh/ccpc_github_deploy_ed25519.pub"`, then register it under repository Settings → Deploy keys with `Allow write access` unchecked (a separate authorization/UI action). Do NOT use `cat` on the private key without `.pub`. GitHub connector offers no deploy-key registration action. Before future SSH Git clone/ls-remote, verify GitHub server host authenticity and scope. No containers, production migrations, server network, firewall, old PROD+DEV or DNS changes.

## 2026-10-23 STEP 84 COMPLETE — INBOUND SSH AUTH FILE ONLY; GITHUB DEPLOY KEY NEXT

Operator ran `find "$HOME/.ssh" -maxdepth 1 -type f -printf '%f\\n' 2>/dev/null` (actual shell command used `-printf '%f\n'`) from new `ccpcerp-prod` and received only `authorized_keys`. No SSH private key file exists directly under `~/.ssh` for GitHub outbound authentication at this checkpoint; any keys in other locations are not excluded by this limited search. **Preserve `authorized_keys`**: it maintains administrative inbound key-only login from Windows, and it must not be edited/replaced for GitHub access. GitHub official documentation confirms repository deploy keys are read-only by default (when 'Allow write access' remains unchecked) and scoped to one repository. **Next operator action (Step 85, separate key generation)**: create a uniquely named Ed25519 key pair on new host under `~/.ssh`, with no passphrase for unattended read-only repo operations, private-key file permission restricted. Do not reuse/copy Windows SSH admin private key and never paste/upload the private key; the *public* `.pub` is the only material for later registration to the repository, after verifying scope and owner approval. The new host is still not deployed, no GitHub deploy key yet authorized, and existing PROD/DEV/DNS/firewall unchanged.

## 2026-10-23 STEP 83 — NEW-HOST HTTPS GIT READ ACCESS BLOCKED BY AUTHENTICATION

Owner ran `GIT_TERMINAL_PROMPT=0 git ls-remote --heads https://github.com/ccpcerp/ccpc-frappe-deployment.git security/dedicated-production-pre-tls-2026-10-23` from the separate new `ccpcerp-prod` and received `fatal: could not read Username for 'https://github.com': terminal prompts disabled`. **This does not establish repository absence, network outage or branch mismatch**: Git over HTTPS reached an authentication-required path but had no usable non-interactive credentials. GitHub connector independently verified draft PR #27 remains OPEN/UNMERGED at branch `security/dedicated-production-pre-tls-2026-10-23` and head `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. No new-host checkout was created or secrets supplied. Preferred approach when approved: separate **read-only per-repository GitHub SSH deploy key** for this server, never copy the Windows administrative login private key or commit any private key/token. **Next one read-only operator step:** inventory only filenames in new-host SSH directory: `find "$HOME/.ssh" -maxdepth 1 -type f -printf '%f\n' 2>/dev/null` (empty output is okay; no key contents). Review before generating/configuring an outgoing deploy key, adding to GitHub, pulling or changing the server. No old PROD+DEV, firewall, DNS, containers, cutover or deployment changes.

## 2026-10-23 STEP 82 COMPLETE — GIT 2.43.0 INSTALLED ON NEW HOST

Operator ran `git --version` from `ccpcadmin@ccpcerp-prod:~$`; received `git version 2.43.0`. Git client availability is now verified. Step 81 found no `.git` checkout within four levels of the current user's HOME. Connected GitHub verified draft PR #27 is still OPEN/UNMERGED at branch `security/dedicated-production-pre-tls-2026-10-23`, head `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f` (and PR #28 remains draft/unmerged, head `622e41e47c0dcf81016b4e03c349ceeee05953b0`). **Next single read-only operator check (Step 83):** on the new host run `GIT_TERMINAL_PROMPT=0 git ls-remote --heads https://github.com/ccpcerp/ccpc-frappe-deployment.git security/dedicated-production-pre-tls-2026-10-23` to check whether the host can access the exact reviewed branch; the environment setting prevents interactive username/password prompts. Authentication may fail for a private repository; in that case, inspect the error and devise minimally privileged access, without providing any secrets in chat or changing host auth blindly. No checkout/clone, credentials, Docker containers, firewall, DNS, PROD/DEV or cutover change authorized or performed.

## 2026-10-23 STEP 81 COMPLETE — NO GIT CHECKOUT FOUND UNDER HOME (FOUR LEVELS)

Owner ran `find "$HOME" -maxdepth 4 -type d -name .git -print` at `ccpcadmin@ccpcerp-prod:~$`; **output was empty**. This verifies no `.git` directory within four levels of the current user's HOME at check time, not an exhaustive scan of other filesystem locations or hidden repo configurations. Existing live `ccpcerpserver` PROD+DEV remains unchanged; new `ccpcerp-prod` has not been used to deploy ERPNext. Preparation can use a separately reviewed new clone later without overwriting uncommitted files. **Next one read-only operator check:** `git --version` on `ccpcerp-prod` to confirm the Git client is available before planning authenticated access to the private GitHub deployment repository and exact-code Docker Compose validation. Do not clone, change branches, pull, create containers, modify firewall/DNS or deploy yet.

## 2026-10-23 STEP 81 SSH RECONNECT — WINDOWS CUSTOM KEY VERIFIED

**Operator confirmed successful reconnection** to the separate new server, reaching the shell prompt `ccpcadmin@ccpcerp-prod:~$`, after an earlier Windows SSH session reset (`client_loop: send disconnect: Connection reset`). Bare `ssh ccpcadmin@192.168.50.186` returned `Permission denied (publickey)`. Windows file inventory (filenames only) showed `ccpcerp_prod_ed25519`, its `.pub`, `config`, and `known_hosts*` in the user's `.ssh` directory. The explicit key command **worked** in Windows PowerShell:

`ssh -i "$env:USERPROFILE\.ssh\ccpcerp_prod_ed25519" ccpcadmin@192.168.50.186`

**Continuity rule:** use the above explicit `-i` key path for reconnection from this Windows profile, or inspect a separately verified SSH alias; do not assume default-key discovery. **The GitHub record contains only key filename/path and command—not private/public key contents, passphrase, fingerprint or credentials.** SSH key-only server configuration is unchanged. No server configuration, networking, Docker, database, PROD/DEV or DNS operations were performed.

**Pending Step 81, now that SSH is restored:** at `ccpcadmin@ccpcerp-prod:~$`, run read-only `find "$HOME" -maxdepth 4 -type d -name .git -print` to inventory Git checkouts before deciding how to validate the new-host Compose profile. Await operator's output.

## 2026-10-23 STEP 79 — BROWSER REMAINS HTTP; INTERMITTENT ROOT CAUSE STILL UNKNOWN

**Owner observed after explicitly entering `http://ccpcerp.com` in the affected Windows browser that the displayed address remains `http://ccpcerp.com/`.** This rules out an immediate automatic browser upgrade to HTTPS **in that observation**, so the Step 78 unavailable TCP 443 does not yet explain the owner's intermittent HTTP availability. The user did not explicitly report a fresh successful load in this turn; do not infer continuous availability. Previous successful HTTP 200, resolver `192.168.50.1` mapping to `192.168.50.166`, and failed HTTPS connection still stand as distinct time-bound observations. Next diagnostic requires **evidence during an actual failure**, checking router DNS, ordinary HTTP request, and an HTTP request routed directly to `192.168.50.166` with hostname preserved via curl `--resolve`, to isolate resolver instability from connectivity/ERPNext errors. Do not modify browser security, DNS, router, old or new production server, Docker, TLS, firewall, or GitHub draft PRs #27/#28. No production operations authorized.

## 2026-10-23 STEP 78 — OLD ERP HTTP WORKS, HTTPS TCP 443 UNREACHABLE FROM WINDOWS LAN

**Owner-reported Windows command:** `curl.exe -I --connect-timeout 5 --max-time 10 https://ccpcerp.com` returned `curl: (7) Failed to connect to ccpcerp.com:443 after 2053 ms: Could not connect to server`. This is a **TCP connection failure**, NOT a TLS certificate validation failure. Step 77's `http://ccpcerp.com` gave `HTTP/1.1 200 OK`, nginx login page; Step 76 router DNS `192.168.50.1` returned current name `192.168.50.166`, distinct from new host `192.168.50.186`. In these tests, HTTP works and HTTPS connection on the existing endpoint does not; the current server may not listen on 443 or path/firewall could block it. **Potential intermittency mechanism:** browser bookmark, automatic HTTPS-first upgrade, cached HSTS policy or user-entered HTTPS could attempt unreachable 443, while explicit HTTP works. Browser cause NOT proven without seeing the failed address bar/error. The HTTP response includes HSTS header but modern browsers ignore HSTS presented over insecure HTTP; it alone does not create browser policy. Plaintext HTTP could expose login credentials/session data on the LAN; do not treat it as a secure long-term solution. **Next one read-only observation:** on the affected Windows browser manually enter `http://ccpcerp.com` and report the final address shown (`http://` vs `https://`) and any error, without sending credentials for this diagnostic. Do not disable browser protection/HSTS, change router/DNS, open 443 on old server, touch new `ccpcerp-prod`, or change prod/dev until separately approved. GitHub PR #27 and #28 remain review-only.

## 2026-10-23 STEP 77 — ACTIVE HTTP ENDPOINT VERIFIED; HTTPS DIAGNOSTIC NEXT

**Owner-provided Windows client read-only `curl.exe -I --connect-timeout 5 --max-time 10 http://ccpcerp.com` succeeded while the application was working:** `HTTP/1.1 200 OK`, `Server: nginx/1.22.1`, `Content-Type: text/html; charset=utf-8`, `X-Page-Name: login`, `X-From-Cache: False`, `Set-Cookie: sid=Guest`, `Connection: keep-alive`. Prior Step 76 DNS resolution from router `192.168.50.1` returned old/current target `192.168.50.166`, not new dedicated `192.168.50.186`. This confirms functioning HTTP resolution/connectivity/web/login-page delivery **at that moment**, but neither sustained reliability nor successful HTTPS/browser access. **The HTTP response carries `Strict-Transport-Security`**, which browsers ignore when received over plain HTTP; browsers may use HTTPS because of an earlier valid HSTS policy or HTTPS-only settings. There is no evidence yet that TCP 443 on the old server serves valid HTTPS, and no proof that DNS causes intermittent reports. **Next single read-only step on same Windows LAN client:** `curl.exe -I --connect-timeout 5 --max-time 10 https://ccpcerp.com` (do **not** use `-k` to bypass certificate verification). Compare with working browser URL and repeat during an observed outage. No router/DNS/SSL, Docker, UFW, old PROD+DEV or new-host changes authorized or performed; both PR #27 and #28 remain draft and unmerged.

## 2026-10-23 STEP 76 — WINDOWS DNS RESOLVER IS LAN ROUTER; CURRENT NAME RESOLVES TO .166

**Operator-supplied read-only Windows test on CCPC LAN:** `nslookup ccpcerp.com` returned `Server: UnKnown`, `Address: 192.168.50.1` (the DNS resolver/router) and `Name: ccpcerp.com`, `Address: 192.168.50.166`. The lookup **succeeded at that moment**, and `Server: UnKnown` ordinarily indicates missing resolver reverse DNS name rather than a failed forward lookup. The DNS response targets **192.168.50.166**, not the separately verified **new `ccpcerp-prod` 192.168.50.186**. The role/current health of `.166` is not freshly verified in this particular step; it is the address returned for the active ERPNext name. Do not switch DNS targets or cut over prematurely. **Intermittent ERPNext access is not proven to be caused by DNS**, and a separate private DNS server is not yet justified by this one successful DNS result. Next safe single test from that same Windows client: `curl.exe -I --connect-timeout 5 --max-time 10 http://ccpcerp.com` to verify HTTP response through the normal hostname, without changing any system. Repeat during an actual access failure later for comparison; a HEAD rejection or redirect alone is not evidence of DNS failure. Keep all existing production services, DNS, router, firewall, DEV and new-host state unchanged.

## 2026-10-23 RELIABILITY-FIRST NAMING CHECKPOINT

Owner reports inconsistent access using `ccpcerp.com` and no known managed DNS provider. Root cause has not been verified. Preferred candidate for future **LAN-only** access is `erp.ccpc.internal`, backed by dependable local DNS and new host IPv4 `192.168.50.186`. Keep an emergency direct-IP method with valid trusted HTTPS certificate; internal CA and client trust are pending. Router/DNS reliability, DHCP lease persistence and DNS-independent operation are required acceptance checks. Do not change the live DNS or old production server. The HTTPS proposal in [draft PR #28](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/28) was updated on branch `docs/dedicated-production-https-gateway-2026-10-23` at commit `622e41e47c0dcf81016b4e03c349ceeee05953b0`. Next read-only diagnosis on an affected Windows client: `nslookup ccpcerp.com`. No deployment approval has been given.

## 2026-10-23 PR #27 EXACT-SOURCE TESTS PASSED; SEPARATE HTTPS GATEWAY DESIGN PR #28 (NO DEPLOYMENT)

**Owner approved continuing safe review/validation and preparing the port-443 design**, not installation, firewall change, Git merge, PRODUCTION deployment, data restore, migration or cutover. **Draft PR #27** stays OPEN/UNMERGED (branch `security/dedicated-production-pre-tls-2026-10-23`, head `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`). Its exact GitHub `scripts/config.sh` and `overrides/compose.dedicated-pre-tls.yaml` contents were reconstructed in an isolated test directory and **Git blob hashes matched** `32614da1044c768bd67dcb9b9491e7c48ff2653a` and `9b69b0c7a1d64191a51da5126ddc82498202446f`. `bash -n` passed, default profile preserved existing 4-file Compose / localhost:80 health, opt-in dedicated profile selected final fifth override and localhost:8080 health, invalid profile rejected; offline PyYAML parse with an explicit custom `!override` tag supported the single `127.0.0.1:8080:8080/tcp` binding and required DB_PASSWORD interpolation. **Caveat:** The isolated environment has neither Docker Compose nor ShellCheck; there is NO live/effective Compose semantic validation, CI evidence, container/network test, or credential-strength test. Exact-source tests were posted in PR #27 conversation, GitHub comment ID `6354214013`. **Do not merge as production-ready or deploy.**

**New GitHub design-only deliverable:** Draft [PR #28](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/28), branch `docs/dedicated-production-https-gateway-2026-10-23`, committed/verified at `f9ee780be7734ffbfc55f3cac3729122a2272526`, based on `main`, one new documentation file `docs/04-operations/dedicated-production-https-gateway-design.md`. Recommended: **host-level** Caddy TLS proxy bound to IPv4 `192.168.50.186:443`, upstream only to Docker `127.0.0.1:8080`; host UFW INPUT can then restrict TCP 443 sources, avoiding a Docker-published 443 listener that can bypass UFW INPUT. No port 80 redirect or HTTP/3 UDP 443 initially; no hostname/DNS cutover. This is a reference **design**, not a Caddy installation or runnable approved configuration. Certificate/trust blocker: either publicly trusted DNS-01 issuance **only if authoritative public DNS control is verified**, with tightly scoped credentials, or owner-controlled internal CA with CA-root-only client distribution. Browser session/CSRF, WebSockets, Frappe Host/scheme, TLS renewal, client allow/deny tests, off-host backups and rollback are separate gates.

**Next:** before further production changes, choose the certificate/trust path by verifying DNS zone control/client trust capability; arrange real `docker compose ... config --quiet` review in an appropriate separated environment without exposing DB secrets and with verified code checksums. Do not touch `ccpcerp-prod` Docker/UFW/SSH, current `ccpcerpserver` PROD+DEV, live DNS, database/NAS or backup/recovery state. No deployment/merge performed.

## 2026-10-23 GITHUB-ONLY DEDICATED PRODUCTION PRE-TLS PORT PROFILE — DRAFT PR #27

**Owner requested GitHub-only preparation and asked for standard ports. Decision/recommendation:** Standard **TCP 443 HTTPS** as the eventual employee-facing `https://ccpcerp.com` LAN endpoint; TCP 80 only optional later for redirect; internal ERPNext HTTP 8080, DB 3306 and Redis 6379 stay unexposed from LAN. HTTPS requires trusted certificates and a separately reviewed TLS reverse proxy; **PR #27 does not implement HTTPS, 443 or a live LAN endpoint**.

**Implementation committed and connector-verified in deployment repo on new feature branch `security/dedicated-production-pre-tls-2026-10-23`, based on `main` (not the unmerged docs checkpoint):** final commit `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`. Draft PR: https://github.com/ccpcerp/ccpc-frappe-deployment/pull/27 (base `main`, draft). Exactly three changed files, 3 commits ahead, 0 behind:
- `overrides/compose.dedicated-pre-tls.yaml`: **opt-in last overlay** replaces frontend mapping with `127.0.0.1:8080:8080/tcp` (no 80 or 443 published) and requires nonempty `DB_PASSWORD` at Compose interpolation for new-host profile instead of relying on old MariaDB fallback.
- `scripts/config.sh`: old `legacy-lan` remains default, preserving old host's four-file Compose selection; explicit `CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls` appends fifth file and changes loopback health URL to `127.0.0.1:8080`; unrecognized profile rejected.
- `docs/04-operations/dedicated-production-port-profile.md`: describes staged/target ports, TLS/CA plan, private DB/Redis, source filtering, secrets, backups, no deployment/cutover.

**Verification:** GitHub connector refetch and compare verified all three files, branch and draft PR; structural/static assertions for default profile, host binding, health URL, required DB password and no 80/443 binding all passed. A locally reconstructed shell/YAML sample also passed `bash -n`, profile selection checks, invalid-profile negative check and YAML parse, but those test copies' Git blob hashes did not match GitHub's exact blobs, so **do not count this as exact-GitHub-source Bash/Compose testing**. GitHub commit status returned no reported status checks at review; actual Docker Compose resolution, CI, TLS, backup/restore and runtime are **not tested**. There were **no SSH, UFW, Docker daemon/Compose runtime, container, NAS, database, DNS, PRODUCTION or DEVELOPMENT server changes**.

**Next:** Review draft PR #27 and separately obtain approval for a safe exact-code syntax/Compose validation in a reviewed environment. Design cert trust and HTTPS reverse proxy/source filtering as a second, explicit new-host-only change; do not start new host stack or touch old `ccpcerpserver` until separately approved.

## 2026-10-23 STEP 74 — NO NON-LINK-LOCAL IPV6 ADDRESSES; COMPOSE DESIGN REVIEWED

**Operator-provided read-only command on the new dedicated `ccpcerp-prod`:** `ip -6 -br address show scope global` returned no output. Together with Step 73 (no IPv6 default route) and Step 72 (`enp5s0 UP 192.168.50.186/24`, link-local `fe80::3256:fff:fe38:dfce/64` only on this NIC), this supports an IPv4 LAN-facing initial design. This snapshot does **not** prove future Docker-published ports cannot expose IPv6, or that IPv6 on-link traffic is impossible. No reason to disable IPv6 or edit the Docker daemon. Operator did not make any host changes.

**Read-only GitHub code review of tracked files on docs branch, 2026-10-23:** `compose.yaml` publishes frontend `8080:8080` without a host IP; `overrides/compose.lan-production.yaml` replaces that mapping with `${HTTP_PUBLISH_PORT:-80}:8080`, also without a host IP. `scripts/config.sh` assembles these four files (base, MariaDB, Redis and LAN override), sets `HTTP_PUBLISH_PORT` default 80, and sets `HEALTHCHECK_URL=http://127.0.0.1:$HTTP_PUBLISH_PORT`. `scripts/modules/health.sh` actually curls that loopback URL with the Frappe site header. Therefore changing frontend publication to **only** `192.168.50.186:80:8080` without adjusting the health check would make that loopback-based check fail. Any new-host-only port-binding design must include a compatible health-check strategy and verify it before use. Existing MariaDB template has insecure `${DB_PASSWORD:-123}` fallback; do not deploy with a default/fallback production credential. Redis and MariaDB have no host-published ports in these reviewed overrides. Preserve live old-host deployment; prefer a separately reviewed new-host-specific override rather than changing old-host production behavior implicitly.

**Docker security design remaining:** define a specific IPv4 frontend bind, a source-network restriction policy for intended `192.168.50.0/24` clients (possibly narrower after owner review), private DB/Redis service exposure, non-default secrets, correct Frappe Host routing and health check, and controlled verification of effective Compose/iptables forwarding before any application deployment. An IP-specific host bind does not by itself restrict source addresses; Docker-published ports can bypass ordinary UFW INPUT rules. See https://docs.docker.com/engine/network/port-publishing/ and https://docs.docker.com/engine/network/packet-filtering-firewalls/. No Compose code changes, Docker/NAT/UFW changes, containers, data transfer, production deployment or old-host changes have been authorized/performed in this check.

**Next engineering step:** prepare/review a narrowly scoped new-host-only Compose port policy **and** the matching health-check change on a reviewed GitHub branch. Obtain separate approval before any deployment on `ccpcerp-prod`, migration, restore or production cutover.

## 2026-10-23 STEP 73 — NO IPV6 DEFAULT ROUTE; GLOBAL IPV6 ADDRESS CHECK NEXT

**Operator-provided read-only `ip -6 route show default` on the new dedicated `ccpcerp-prod` returned no routes.** This verifies that the current IPv6 routing table has **no default route**. Step 72 showed only link-local IPv6 on `enp5s0` and retained IPv4 `192.168.50.186/24`; no IPv6 default route does not prove there are no global/ULA IPv6 addresses on other interfaces, on-link IPv6 reachability, or future Docker IPv6 port exposure. Do not disable IPv6 or change routing/firewall rules based on this result. This supports pursuing reviewed explicit IPv4 host binding in the future ERPNext Compose configuration, with additional source-network/firewall restrictions rather than relying solely on host bind addresses.

**Next one read-only operator step on the NEW host:** `ip -6 -br address show scope global` to inventory non-link-local IPv6 addresses across all interfaces. Afterward shift to Compose/firewall policy review; no unnecessary repeated IPv6 preflights. **No containers, ERPNext install, production restore, database migration, DNS cutover, or existing `ccpcerpserver` PROD/DEV changes were made.**

## 2026-10-23 STEP 72 — LAN NIC ADDRESSES VERIFIED; IPV6 DEFAULT ROUTE NEXT

**Operator-provided read-only `ip -br addr show dev enp5s0` on the distinct new `ccpcerp-prod` host:** `enp5s0 UP 192.168.50.186/24 metric 100 fe80::3256:fff:fe38:dfce/64`. The NIC is UP and still has the intended DHCP-assigned LAN IPv4 address; the only IPv6 address shown **on this NIC** is link-local (`fe80::/10`). The output does not prove whether other interfaces have IPv6 addresses, whether an IPv6 default route exists, or whether a router reservation survives a lease renewal. For future ERPNext frontend publication, an explicit host bind to `192.168.50.186` is a candidate, subject to reviewed Compose and firewall configuration and source-network restrictions. **Host address binding alone is not an access-control rule**; Docker port publishing may bypass host UFW's normal INPUT filtering. No firewall, Docker daemon, container, ERPNext, DNS, backup or old-server change was executed.

**Next single read-only check on NEW host:** `ip -6 route show default` to see whether the host currently has an IPv6 default route. After reviewing, design the new host's secure LAN-facing publication and source restrictions before any container is launched. Existing `ccpcerpserver` PRODUCTION and DEVELOPMENT remain untouched.

## 2026-10-22 STEP 71 — NO DAEMON.JSON; HOST ADDRESS CHECK NEXT

**Operator-provided Step 71 read-only result on dedicated NEW Ubuntu host `ccpcerp-prod`:** `sudo test -f /etc/docker/daemon.json` returned false, and the script printed `Docker daemon.json absent`. This is normal on a fresh Docker Engine installation; the engine is using built-in or other existing service defaults. **No daemon configuration needs to be created now and no Docker restart is needed.** Continue with explicit Docker Compose port host-IP mappings rather than changing daemon-wide defaults without a reason. Tracked `overrides/compose.lan-production.yaml` currently omits a host IP in its frontend published-port syntax, so a reviewed new-host-specific override/change is needed before containers are launched. Docker documentation (current): https://docs.docker.com/reference/compose-file/services/ describes `ports[].host_ip`, and https://docs.docker.com/engine/network/port-publishing/ explains unspecified host binding can include IPv4 and IPv6. **A specific host-IP binding limits the destination address, but does not by itself enforce allowed source networks; routed clients/firewall paths must also be reviewed.** MariaDB and Redis should not publish host ports. Do not start any ERPNext containers or change existing `ccpcerpserver` live PROD/DEV, NAS backup, DNS or cutover.

**Next one read-only operator step on the NEW host:** `ip -br addr show dev enp5s0`. Confirm current active IPv4 and any IPv6 addresses on the production LAN NIC prior to designing front-end bind IPs and IPv4/IPv6 access restrictions; note router DHCP reservation is owner-reported but not independently lease-renewal tested. No change is requested to Ubuntu DHCP or network configuration.

## 2026-10-22 STEP 70 — DEFAULT BRIDGE BIND-ALL VERIFIED; SECURE COMPOSE DESIGN NEXT

**Owner-provided read-only `sudo docker network inspect bridge` on dedicated new `ccpcerp-prod`:** default `bridge` driver local network, `EnableIPv4=true`, `EnableIPv6=false`; IPAM subnet `172.17.0.0/16`, gateway `172.17.0.1`; `Internal=false`; default bridge `docker0`, `enable_icc=true`, `enable_ip_masquerade=true`, `host_binding_ipv4=0.0.0.0`; `Containers: {}`. Thus no attached containers currently. **Security finding:** publishing a port without explicit host-IP can bind to all available interfaces, potentially including IPv6 via Docker userland proxy despite `EnableIPv6=false`. Bridge defaults do not automatically govern user-defined Compose bridge networks. Source: https://docs.docker.com/engine/network/port-publishing/ (publishing ports, IPv6 mapping and per-network/default-network-opts settings). No container ports have been published, and no changes to networking have been made.

**GitHub-first read-only code inspection of deployment repo branch `docs/ccpc-checkpoint-2026-10-10`:** root `compose.yaml` has `frontend.ports: ["8080:8080"]` (unspecified host IP); `overrides/compose.lan-production.yaml` overrides ports to `["${HTTP_PUBLISH_PORT:-80}:8080"]`, likewise unspecified host IP; `overrides/compose.mariadb.yaml` uses `MYSQL_ROOT_PASSWORD: ${DB_PASSWORD:-123}` (unsafe fallback absent properly provided secret), and `overrides/compose.redis.yaml` has no host-published Redis ports. The tracked templates are not proof of effective existing production configuration. For the NEW host, require an explicit safe publishing/reverse-proxy plan, private DB/Redis networks, non-default secrets, TLS/access policy and IPv6/Docker firewall exposure validation before deploying. Do **not** edit code, secrets or existing live environment without change authorization. Docker firewall/UFW caveat: https://docs.docker.com/engine/network/packet-filtering-firewalls/ .

**Next one safe read-only operator command on the NEW server:** `if sudo test -f /etc/docker/daemon.json; then echo "Docker daemon.json exists"; else echo "Docker daemon.json absent"; fi`. This checks whether the new daemon already has a local config file before proposing persistent secure defaults. Do not echo any daemon file contents unreviewed in case they contain sensitive settings. Subsequently choose between explicit Compose bind addresses (recommended) and, if necessary, daemon defaults; any changes require review of restart/network impacts. Existing `ccpcerpserver` PRODUCTION+DEVELOPMENT, NAS backups, DNS, site/data and cutover remain untouched.

## 2026-10-22 STEP 69 — IPV6 NAT VERIFIED; DEFAULT BRIDGE INSPECTION NEXT

**Owner-provided read-only `sudo ip6tables -t nat -S` from new `ccpcerp-prod`:** IPv6 NAT base policies `PREROUTING ACCEPT`, `INPUT ACCEPT`, `OUTPUT ACCEPT`, `POSTROUTING ACCEPT`; empty `DOCKER` chain; `PREROUTING -m addrtype --dst-type LOCAL -j DOCKER` and `OUTPUT ! -d ::1/128 -m addrtype --dst-type LOCAL -j DOCKER`. No displayed IPv6 DNAT/published-port/masquerading rules. Earlier IPv6 filter rules (Step 66) showed INPUT/FORWARD DROP, and earlier `docker ps --all` showed no containers. NAT ACCEPT does not cancel the filter-table default drops. **Current security evidence applies only to the empty Docker installation**; future container port publishing can introduce additional IPv4/IPv6 NAT and filter behavior, and host UFW alone is insufficient evidence of safety.

**Next single read-only operator command on the NEW server:** `sudo docker network inspect bridge`. Inspect `EnableIPv6`, default bridge `IPAM.Config`, `Options` (including any host bind defaults) and empty `Containers`. A safe, explicit Compose published-port binding/access strategy and firewall testing are pending before starting ERPNext containers. No iptables/UFW changes, services restarts, restore, migration, old `ccpcerpserver` PRODUCTION/DEVELOPMENT change, backup change, or DNS cutover.

## 2026-10-22 STEP 68 — IPV4 NAT VERIFIED; IPV6 NAT NEXT

**Owner-provided read-only output on the dedicated NEW host `ccpcerp-prod`:** `sudo iptables -t nat -S` shows IPv4 NAT base policies `PREROUTING ACCEPT`, `INPUT ACCEPT`, `OUTPUT ACCEPT`, `POSTROUTING ACCEPT`; the `DOCKER` NAT chain exists, with `PREROUTING` traffic to local destinations and `OUTPUT` traffic to non-loopback local destinations jumping to `DOCKER`. `POSTROUTING` has `-s 172.17.0.0/16 ! -o docker0 -j MASQUERADE` for Docker's default bridge subnet. **No DNAT or published-container forwarding entries appeared** in the output, consistent with the prior `docker ps --all` inventory showing zero containers. These NAT ACCEPT base policies do not cancel the separately observed IPv4 filter-table INPUT/FORWARD DROP policies. However, this does not prove future Docker-published ports will be restricted to the LAN; when containers are added, NAT and filter chains may change. Existing UFW SSH allowance (LAN 192.168.50.0/24 only) remains documented; no modification, restarts, application installation, restoration or production cutover performed.

**Next one safe read-only command on the NEW host:** `sudo ip6tables -t nat -S` to inspect IPv6 NAT rules. Subsequently review Docker bridge/address binding and a LAN-only published-port strategy (plus IPv6 behavior) prior to deploying ERPNext containers. **No ports should be published until those controls have been reviewed.** Existing `ccpcerpserver` live PRODUCTION and DEVELOPMENT systems, NAS backups, DNS and business records remain untouched.

## 2026-10-22 STEP 67 — IPV4 FILTER TABLE VERIFIED; NAT REVIEW NEXT

**Owner-provided read-only command on new `ccpcerp-prod`:** `sudo iptables -S`. Base chains: `-P INPUT DROP`, `-P FORWARD DROP`, `-P OUTPUT ACCEPT`. UFW hooked into IPv4 INPUT and FORWARD; `ufw-user-input` contains only a specified inbound SSH allow `-s 192.168.50.0/24 -p tcp --dport 22 -j ACCEPT` (normal UFW auxiliary ICMP, DHCP, loopback, established/related allowances also present). Docker filter chains `DOCKER`, `DOCKER-USER`, `DOCKER-FORWARD`, `DOCKER-BRIDGE`, `DOCKER-CT` are present. `FORWARD` traverses `DOCKER-USER` and `DOCKER-FORWARD` **before** UFW's forward chains. No custom entries were shown inside `DOCKER-USER`; `DOCKER-FORWARD` contains bridge path rules including `-i docker0 -j ACCEPT`. Earlier `sudo docker ps --all` showed **no containers** and no published ports. This confirms the IPv4 host firewall and forwarding arrangement, but **does not prove future published Docker container ports will be LAN restricted**: Docker performs destination NAT before ordinary UFW INPUT filtering. Docker documentation: https://docs.docker.com/engine/network/packet-filtering-firewalls/ and https://docs.docker.com/engine/network/firewall-iptables/ .

**Next single read-only command on NEW host:** `sudo iptables -t nat -S` to inspect Docker's IPv4 NAT/prerouting/output/masquerading rules, then review IPv6 NAT, planned Compose published-port host-IP binding, and any required DOCKER-USER source restrictions before running containers. Do not change `iptables`, UFW, SSH, Docker daemon options, container-port publishing, existing `ccpcerpserver` PROD/DEV, backups, DNS, site or data until separately assessed/approved. No production cutover authorization has been given.

## Current prepared-host baseline

New Ubuntu Server 24.04.5 LTS (Noble amd64) `ccpcerp-prod`, admin `ccpcadmin`; LAN IP `192.168.50.186/24` on `enp5s0`, gateway `192.168.50.1`; owner reports a router DHCP reservation. SSH key-only remote access; UFW active, inbound default deny and SSH 22 allowed only from `192.168.50.0/24` in IPv4. AMD Ryzen 7 7700 (8 cores/16 threads); 14 GiB RAM + 4 GiB swap. NVMe storage: 800G root LVM, ext4 `/` approx 740G available; additional ~128.46G VG free held in reserve. Official Docker APT repository and signing key were verified. Docker Engine 29.9.2, Docker Compose plugin 5.6.1, Buildx 0.38.1, containerd 2.4.2 installed (APT reported 7 new packages, 0 removals/upgrades). `systemctl is-active docker containerd` both active. No Docker containers, no ERPNext site, no DB restore or migration on new host. Old `ccpcerpserver` still hosts live production and development; no production cutover. Off-host backup/recovery and application volume planning remain outstanding gates.

## Historical immediately preceding checkpoint — Step 66

## 2026-10-22 NEW HOST IPV6 FIREWALL VERIFIED — IPV4 FILTER INSPECTION NEXT

**Owner-provided Step 66 `sudo ip6tables -S` output on separate `ccpcerp-prod`:** IPv6 base policies `-P INPUT DROP`, `-P FORWARD DROP`, `-P OUTPUT ACCEPT`. The INPUT chain traverses UFW6 input chains; `ufw6-before-input` accepts loopback, ESTABLISHED/RELATED, necessary ICMPv6/neighbor-discovery/DHCPv6 and selected multicast traffic, then jumps to `ufw6-user-input`. No explicit TCP/22 IPv6 allow rule in the supplied rules. Hence unsolicited IPv6 SSH is not explicitly allowed through these chains and should fall under INPUT DROP (based on the displayed ip6tables rules); this is configuration review, not a remotely tested IPv6 access probe. `sshd` does listen on `[::]:22`. FORWARD traverses `DOCKER-USER` and `DOCKER-FORWARD` **ahead of UFW6 forward chains**; Docker bridge/published-port filtering must be evaluated independently. `docker ps -a` was empty in Step 64, and there were no other application listeners in Step 65. No firewall or SSH configuration changes made. Existing `ccpcerpserver` PROD/DEV, production data, NAS, DNS and cutover are untouched.

**Next one read-only check on new server:** `sudo iptables -S` to inspect the IPv4 INPUT/FORWARD policies, UFW hooks and Docker chains, then separately inspect NAT and proposed port bindings before starting any ERPNext container. Docker documentation confirms published bridge-container traffic can bypass ordinary UFW filtering: https://docs.docker.com/engine/network/packet-filtering-firewalls/ . Preserve key-only SSH and IPv4 LAN-only access; do not disable firewall, Docker iptables management or IPv6 without explicit controlled review.

## Archived recent new-host checkpoints — Steps 65 through 53

## 2026-10-22 NEW HOST LISTENING SOCKETS VERIFIED — IPV6 FILTER REVIEW NEXT

**Operator-provided Step 65 read-only output on new `ccpcerp-prod`:** `sudo ss -lntup` showed SSH listening on IPv4 `0.0.0.0:22` and IPv6 `[::]:22` (`sshd`/systemd); loopback systemd-resolved DNS on TCP+UDP `127.0.0.53:53` and `127.0.0.54:53`; and systemd-networkd DHCP client bound to `192.168.50.186%enp5s0:68/udp`. No ERPNext, Redis, MariaDB, HTTP(S), or other publicly listening application ports shown. The Docker container inventory was empty in Step 64. The earlier UFW check showed active default deny inbound/routed with SSH IPv4 allowance from `192.168.50.0/24`. **Caution:** The existence of an IPv6 SSH listener means IPv6 packet-filtering must be inspected separately; a visible IPv4-only UFW allow rule is not sufficient to conclude IPv6 has equivalent restrictions. Also, listening-socket inspection alone does not prove future Docker NAT port publishing is blocked.

**Next one read-only operator step on NEW host:** `sudo ip6tables -S` to inspect IPv6 filter-chain policies and UFW6 jumps, and determine whether inbound IPv6 SSH is restricted before making changes. Do not disable IPv6 or change UFW/SSH without a verified safe access plan. Continue Docker NAT and published-port review before any ERPNext deployment. No changes to existing `ccpcerpserver` PROD+DEV, data, backups, DNS or cutover were undertaken.

## 2026-10-22 DOCKER CONTAINER INVENTORY EMPTY — LISTENING PORTS NEXT

**Operator-provided Step 64 evidence from dedicated new server `ccpcerp-prod`:** `sudo docker ps --all --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'` returned exactly the `NAMES STATUS PORTS` header without any container rows. Thus there are **no Docker containers, running or stopped, and no container-published ports associated with Docker containers** at the time of the check. Docker and containerd services were previously verified active, and UFW previously remained active with `deny incoming`, `deny routed` and `22/tcp ALLOW IN 192.168.50.0/24`. Neither that UFW rule listing nor the empty container inventory establishes that all host listening ports or possible future Docker publishes are secured. No application deployment or site/DB/data migration, DNS cutover, existing-host `ccpcerpserver` PROD+DEV change, backup change or firewall edit occurred in Step 64.

**Next single read-only command on the new host:** `sudo ss -lntup` to inspect listening TCP/UDP sockets, local bind addresses and associated processes without changing networking. Then separately review Docker's NAT/filter policy and explicit port-bind plan before any ERPNext container starts. Preserve the existing LAN-only SSH and UFW policy. Do not publish application ports or assume UFW restricts Docker-published ports without further controls.

## 2026-10-22 NEW HOST UFW POLICY RETAINED — DOCKER CONTAINER INVENTORY NEXT

**Operator-reported Step 63 read-only firewall output on dedicated new `ccpcerp-prod`:** `sudo ufw status verbose` returned `Status: active`, `Logging: on (low)`, `Default: deny (incoming), allow (outgoing), deny (routed)`, and a single listed rule `22/tcp ALLOW IN 192.168.50.0/24`. Thus the previously authorized LAN-limited SSH rule and UFW defaults remain visible after installing Docker 29.9.2 and starting Docker/containerd. **Caution:** UFW alone does not prove Docker-published container ports are LAN-limited, since Docker modifies packet-filtering/forwarding rules. No firewall policy changes made in this step. Existing `ccpcerpserver` PROD+DEV, DNS, backups, production data and cutover remain untouched.

**Next single read-only check on NEW host:** `sudo docker ps --all --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'` to inventory any running/stopped containers and their published ports without creating or changing a container. Later separately inspect listening sockets, Docker firewall configuration and published-port policy before any ERPNext containers are launched. Do not change UFW, reboot, restart Docker or publish ports yet.

## 2026-10-22 NEW HOST DOCKER AND CONTAINERD ACTIVE — FIREWALL CHECK NEXT

**Owner-provided Step 62 live evidence from dedicated `ccpcerp-prod`:** `systemctl is-active docker containerd` returned `active` and `active`, confirming both Docker Engine and the containerd service are running after the verified 7-package installation. This is service-state verification only; **no `docker info`, container listing, or firewall exposure verification yet**, and no ERPNext application or migration has been deployed on the new host. Docker and Compose packages installed: Docker Engine 29.9.2, Docker Compose plugin 5.6.1. Existing `ccpcerpserver` PROD+DEV, DNS, data, backups and cutover remain untouched.

**Next single read-only operator command on the NEW host:** `sudo ufw status verbose`. Verify continued active default deny inbound policy and existing SSH allowance from the LAN `192.168.50.0/24`. **UFW output by itself does not establish safety of Docker-published container ports**, since Docker creates packet-filtering rules that may bypass UFW; prior to any container port binding, separately inspect `docker ps`, listening sockets, firewall/NAT and binding configuration, and restrict published ports explicitly to the intended interfaces. Do not restart, alter firewall, publish ports or deploy/restore site yet. Official Docker firewall documentation: https://docs.docker.com/engine/network/packet-filtering-firewalls/ .

## 2026-10-22 NEW HOST DOCKER ENGINE INSTALLED — DAEMON STATUS PENDING

**Operator-provided Step 60/61 evidence on dedicated `ccpcerp-prod`:** APT installation simulation showed 7 new packages, no upgrades or removals; operator then explicitly confirmed the matching real installation. `sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin` finished successfully, downloading 102 MB and installing seven packages: `docker-ce` / `docker-ce-cli` 29.9.2, `containerd.io` 2.4.2, `docker-buildx-plugin` 0.38.1, `docker-compose-plugin` 5.6.1, `docker-ce-rootless-extras` 29.9.2 and `pigz` 2.8. APT showed **0 upgraded, 7 newly installed, 0 removed, 7 not upgraded**; Docker and containerd systemd unit symlinks were created. No errors in output; service activity, socket exposure, firewall effects and usability are **not yet verified**. No ERPNext site deployed, no containers started intentionally, and no DNS/backup/old `ccpcerpserver` PROD/DEV changes.

**Next one safe read-only command on the new host:** `systemctl is-active docker containerd` to confirm actual daemon and runtime status without starting or changing anything. Afterward verify SSH/UFW and Docker networking prior to publishing any ports. GitHub-first rules remain in force; no production migration or cutover approved.

## 2026-10-22 NEW HOST DOCKER CANDIDATE VERSIONS VERIFIED — APT SIMULATION NEXT

Step 58: Operator ran `sudo apt update` on new `ccpcerp-prod` host. Docker's Noble repository fetched InRelease and stable/amd64 package index without errors; 7 Ubuntu package upgrades remained pending. Step 59: Operator ran `apt-cache policy` on five official Docker packages. None installed. Candidate versions: docker-ce and docker-ce-cli `5:29.9.2-1~ubuntu.24.04~noble`; containerd.io `2.4.2-3~ubuntu.24.04~noble`; docker-buildx-plugin `0.38.1-1~ubuntu.24.04~noble`; docker-compose-plugin `5.6.1-1~ubuntu.24.04~noble`. All candidates came from `https://download.docker.com/linux/ubuntu` Noble stable amd64. Docker is not yet installed, and no application containers or network ports were touched.

Next one read-only step on NEW host: `apt-get -s install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin`. Examine exactly what installation/removals/upgrades would occur. Do not execute a real installation until separately reviewed, as Docker daemon startup can affect forwarding and firewall rules; Docker published ports can bypass UFW. Existing PROD and DEV on `ccpcerpserver`, backup state, DNS and cutover remain untouched. Docker official references: https://docs.docker.com/engine/install/ubuntu/ and https://docs.docker.com/engine/network/packet-filtering-firewalls/ .

## 2026-10-22 DOCKER APT SOURCE VERIFIED — PACKAGE INDEX REFRESH NEXT

**Owner-provided Step 57 live output on the distinct new Ubuntu host `ccpcerp-prod`:** `/etc/apt/sources.list.d/docker.sources` exists and contains exactly the intended deb822 fields: `Types: deb`, `URIs: https://download.docker.com/linux/ubuntu`, `Suites: noble`, `Components: stable`, `Architectures: amd64`, `Signed-By: /etc/apt/keyrings/docker.asc`. The Docker signing-key fingerprint was verified in Step 56 as `9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88`. Thus the APT source **file contents** are verified from the operator terminal; **the repository metadata has not yet been fetched and verified by APT**. No Docker Engine, Compose, Buildx, container/site or network-port deployment has occurred. Existing `ccpcerpserver` PRODUCTION and DEVELOPMENT remain untouched; no DNS, data copy or cutover action.

**Next safe single operator step on NEW host only:** `sudo apt update`. Review results for `https://download.docker.com/linux/ubuntu noble InRelease` or equivalent successful Docker repository metadata/index retrieval, signature validity, and absence of errors. This refreshes APT's package lists **without installing/upgrading packages or starting Docker**. After successful output, inspect available Docker package versions and deliberate Docker daemon networking/UFW exposure before installation. Docker official Ubuntu install instructions: https://docs.docker.com/engine/install/ubuntu/ ; note firewall limitations. Seven Ubuntu upgrades were previously pending, with no blanket approval to install them or modify existing `ccpcerpserver`.

## 2026-10-22 DOCKER SIGNING KEY FINGERPRINT VERIFIED — APT SOURCE NEXT

**Operator-reported read-only Step 56 verification on dedicated `ccpcerp-prod`:** `gpg --show-keys --with-fingerprint /etc/apt/keyrings/docker.asc` succeeded and displayed `pub rsa4096 2017-02-22 [SCEA]`, UID `Docker Release (CE deb) <docker@docker.com>`, signing-key fingerprint **`9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88`**, with `sub rsa4096 2017-02-22 [S]`. The fingerprint matches the expected Docker repository signing key. GPG initialized `/home/ccpcadmin/.gnupg` and an empty keybox on first use; this is expected and not evidence of a Docker daemon installation. Docker CE, Compose and Buildx are **not yet installed**, and Docker APT source is **not yet created**. No network/firewall/container/old-host/site/backup changes were reported.

**Next safe Step 57 on the NEW Ubuntu 24.04 Noble/amd64 host only:** add an APT source file `/etc/apt/sources.list.d/docker.sources` using Docker's documented deb822 fields: `Types: deb`, `URIs: https://download.docker.com/linux/ubuntu`, `Suites: noble` (or from `UBUNTU_CODENAME` in os-release), `Components: stable`, `Architectures: amd64` (from `dpkg --print-architecture`), `Signed-By: /etc/apt/keyrings/docker.asc`. First test if target file already exists; **do not overwrite** without review. Show created file content to operator; `sudo apt update` to verify repository metadata should be a subsequent separate step after inspection. Official source https://docs.docker.com/engine/install/ubuntu/ (rechecked 2026-10-22). Starting Docker later could modify host forwarding/firewall rules; UFW alone does not constrain Docker-published ports (https://docs.docker.com/engine/network/packet-filtering-firewalls/). No production data movement or existing `ccpcerpserver` changes are approved.

## 2026-10-22 NEW HOST DOCKER SIGNING KEY DOWNLOADED — FINGERPRINT CHECK NEXT

**Operator-provided Step 55 terminal output from dedicated Ubuntu 24.04 host `ccpcerp-prod`:** executed `sudo install -m 0755 -d /etc/apt/keyrings`, checked that `/etc/apt/keyrings/docker.asc` did not already exist, then ran `sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc` followed by `sudo chmod a+r /etc/apt/keyrings/docker.asc`. Output was `Docker signing key downloaded`, establishing the download/chmod commands returned success through the shell `&&` sequence. **Key content/fingerprint is not yet independently inspected**, and Docker repository config, Docker engine/Compose installation and daemon startup remain **NOT DONE**. Official Docker Ubuntu docs continue to prescribe this `docker.asc` path: https://docs.docker.com/engine/install/ubuntu/ .

**Next one safe operator step on NEW host only:** read-only key inspection `if command -v gpg >/dev/null 2>&1; then gpg --show-keys --with-fingerprint /etc/apt/keyrings/docker.asc; else echo "gpg not installed; fingerprint not verified"; fi`. Compare reported Docker Release (CE deb) fingerprint; historically `9DC858229FC7DD38854AE2D88D81803C0EBFCD88`. Because the upstream key bundle may be updated, inspect the full output and do not assume unknown additional/new fingerprints should be accepted without verification. Do **not** create APT source until contents have been reviewed. No Docker runtime changes, port publication, site/data transfer, DNS cutover or existing `ccpcerpserver` PRODUCTION/DEVELOPMENT changes are authorized or completed. Existing key-only SSH and UFW LAN restriction remain protected.

## 2026-10-22 NEW HOST DOCKER PREREQUISITES VERIFIED — SIGNING KEY NEXT

**Operator-provided Step 54 APT output from new, dedicated `ccpcerp-prod` host:** `sudo apt update && sudo apt install ca-certificates curl` succeeded. Ubuntu Noble repositories were reached without errors; APT reported both `ca-certificates` (`20260816ubuntu0.24.04.1`) and `curl` (`8.5.0-2ubuntu10.16`) already at their newest offered versions. Final APT result: **0 upgraded, 0 newly installed, 0 to remove, 7 not upgraded**. These seven upgrades remain **pending review**, not installed and not assumed security-only. The earlier package check found no installed docker/containerd/runc/podman packages matching the query; Docker CLI was absent. No Docker packages, Docker daemon, containers, site, DNS, network rule, old server service or backup were changed.

**Current official Docker Ubuntu Noble installation guidance verified 2026-10-22:** https://docs.docker.com/engine/install/ubuntu/ . Use the Docker-maintained APT repo and `/etc/apt/keyrings/docker.asc` key file, not the convenience script. **Step 55 (operator action pending):** create the keyrings directory `sudo install -m 0755 -d /etc/apt/keyrings`; if `/etc/apt/keyrings/docker.asc` already exists, STOP and inspect rather than overwriting; otherwise download the Docker official public key from `https://download.docker.com/linux/ubuntu/gpg` into `/etc/apt/keyrings/docker.asc` and make it readable via `sudo chmod a+r /etc/apt/keyrings/docker.asc`. After operator output, inspect and verify key fingerprint *before* creating `docker.sources`. This procedure does not install or start Docker; actual Docker package installation and daemon-start network impact are future separate operations. UFW/Docker published-port bypass remains a safety consideration: https://docs.docker.com/engine/network/packet-filtering-firewalls/ . Existing `ccpcerpserver` PRODUCTION+DEVELOPMENT, ERPNext data and cutover are untouched.

## 2026-10-22 NEW HOST DOCKER PACKAGE-CHECK CLEAN — OFFICIAL REPOSITORY PREPARATION NEXT

**Owner-provided read-only package check on dedicated new host `ccpcerp-prod`:** `dpkg -l | grep -E '^ii +((docker|containerd|runc|podman)[^ ]*)' || echo "No Docker-related packages found"` printed `No Docker-related packages found`. Thus no matching Docker/containerd/runc/podman packages appear installed according to this query; it is not proof of absence of every container runtime/tool. Earlier `command -v docker` also returned no executable in PATH. **No uninstallation is necessary based on current evidence; do not remove unrelated packages.**

**Docker installation preparation — next step on the NEW host only:** Official Docker Engine Ubuntu documentation confirms Noble 24.04 LTS amd64 is supported and recommends the official APT repository over the testing-oriented convenience script. **Next single operator action:** `sudo apt update && sudo apt install ca-certificates curl`; inspect the package manager's proposed changes and abort if unexpected removals are proposed. These are prerequisite/support-package operations, **not yet Docker installation**. Later: add the official Docker signing key and `.sources` APT entry, install `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, `docker-compose-plugin`, and verify. Docker Engine can modify host networking on daemon startup and published container ports can bypass UFW: no publishing or application containers until a specific LAN exposure review. Existing key-only SSH, UFW rules, old `ccpcerpserver` PROD/DEV, DNS, site/data, NAS backups and cutover remain untouched; no Docker installer or package changes have yet been executed as part of this checkpoint. Official docs: https://docs.docker.com/engine/install/ubuntu/ and https://docs.docker.com/engine/network/packet-filtering-firewalls/ .

## 2026-10-22 NEW HOST DOCKER CLI ABSENT — PACKAGE-CONFLICT INSPECTION NEXT

**Operator-provided read-only shell check on dedicated `ccpcerp-prod`:** `command -v docker` was false and the command printed `Docker CLI not installed`. This confirms Docker executable not present in `PATH` but does **not** independently prove no Docker/containerd/Podman packages, binary in unusual location, or Docker service exist. Prior new-host inventory remains Ryzen 7 7700 (8 cores / 16 logical threads), 14 GiB RAM, 4 GiB swap, ext4 root 740G filesystem available, with ~128.46G unused LVM VG capacity. No package installation or change to either physical host was executed.

**Installation plan (not yet executed):** Use Docker's official Ubuntu 24.04/Noble amd64 APT repository for Docker Engine, Compose plugin and Buildx rather than `get.docker.com` convenience script, after inspecting conflicting distro packages. Official Docker documentation requires checking `docker.io`, old Compose packages, `podman-docker`, `containerd` and `runc` before installing official `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, `docker-compose-plugin`. Docker networking can bypass UFW rules on published container ports; avoid publishing/starting ERPNext containers before network policy and localhost/LAN exposure review. Keep existing key-only SSH/UFW configuration intact. **Next one read-only operator step on the NEW host:** `dpkg-query -W -f='${binary:Package} ${Version} ${Status}\n' docker.io docker-compose docker-compose-v2 docker-doc docker-buildx podman-docker containerd runc docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin 2>/dev/null | grep 'install ok installed' || echo 'No listed Docker-related packages installed'`. Inspect the result before package changes. Existing `ccpcerpserver` PROD/DEV, production data, DNS and cutover remain protected; no site deployment, restore, migration, restart or backup adjustment was authorized.

