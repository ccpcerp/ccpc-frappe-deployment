# CCPC ERPNext — Current DEVELOPMENT handoff (continuation 4)

## November 17, 2026 — DEVELOPMENT Procfile service declaration inventory COMPLETE; scheduler is CONFIGURED

Owner ran read-only Procfile service-name inventory and reported:

```text
WEB_DECLARED=YES
SOCKETIO_DECLARED=YES
SCHEDULE_DECLARED=YES
WORKER_SHORT_DECLARED=NO
WORKER_LONG_DECLARED=NO
WATCH_DECLARED=YES
REDIS_CACHE_DECLARED=NO
REDIS_QUEUE_DECLARED=NO
OTHER_SERVICE_COUNT=1
DEV_PROCFILE_INSPECTION=COMPLETE
```

**Interpretation:** Honcho's DEVELOPMENT Procfile configures a `schedule` service in addition to web, Socket.IO and watch, with one other unclassified service name. This **does not establish that the scheduler is currently running**, since Honcho can be started with a service subset and prior process classification used incomplete heuristics. But the scheduler is **not safely absent**: restarting the full Honcho Procfile risks starting `schedule` and enumerating the known broken third DEV site `ccpc-integration.localhost`. No application restarts, scheduler enable/disable, Procfile edits, DB writes, PROD effects or code reversion have been authorized. Code remains on-disk at PR33 SHA `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`; live HTTP module activation remains unverified.

**Next read-only check:** inspect the active Honcho launch arguments and all current PID command tokens privately, printing only allowlisted *role labels* plus whether `schedule` is a running service candidate and whether Honcho appears to have been started with an explicit subset. Never print raw args, environment, secrets, Procfile commands, and never restart the supervisor. Distinguish a declared service from a live process and from an authorized target for a future web-only restart.

## November 17, 2026 — bounded Honcho process-tree inventory PASS, no reload yet

Owner ran the second, strictly Honcho-descendant-only read-only classifier, ending `HONCHO_PROCESS_TREE=COMPLETE`. **Observed supervised tree (snapshot PIDs):** Honcho `543180` had direct children `543392` and `543393` marked UNCLASSIFIED. Under `543393`, children `543394` and `543395` remained UNCLASSIFIED. The `543394 → 543396` shell → `543398` Python chain was labelled WEB_CANDIDATE, with `544672` also a WEB_CANDIDATE descendant and `543417`, `544674` unclassified. The `543395 → 543399` shell → `543401` chain was labelled SOCKETIO_CANDIDATE. **No `SCHEDULER_CANDIDATE` or `WORKER_CANDIDATE` was identified within that Honcho tree**, but a heuristic filtered classifier is not proof that scheduler processes or background services are disabled outside it. Other PPID=1 Python processes remain unclassified, and multiple service runners may exist.

**Consequence:** The exact PR33 security fix source is installed on DEV disk at `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`, and the Frappe in-memory exact-source 15-test gate passed, but the in-use HTTP worker's loaded module version is **not proven**. Do not restart the parent Honcho supervisor, its whole Compose container or the bench scheduler merely to activate the fix. Next low-risk discriminator is to inspect only the names of declared DEV `Procfile` services and the code file's modification time relative to candidate web process start times, printing no Procfile commands, service argv, environment variables or credentials. If web-only activation appears necessary, review its actual supervisor relationship, failure/recovery and broken third-site exposure before seeking explicit *DEV-only targeted restart* authorization. PRODUCTION untouched; no process changes in this observation.

## November 17, 2026 — sanitized process-role classification COMPLETED (web candidates, Socket.IO, Honcho)

Owner executed the read-only, sanitized in-container `/proc` role classifier; terminal ended with `DEV_PROCESS_CLASSIFICATION=COMPLETE`. At inspection time the parent supervisor was `honcho` PID `543180`, with direct children `python3.14` PIDs `543392` (UNCLASSIFIED) and `543393` (WEB_CANDIDATE). The `543393` process had Python3.14 descendants `543394` and `543395` classified WEB_CANDIDATE, plus `sh`/`python` descendants; `543399` sh and `543401` MainThread classified SOCKETIO. Other web candidates include `543398` python and `544672` python. Separate `copilot-runtime` at `3610` was identified and **must not** be treated as the new clean Codex Stage A probe. Many older `python`, `python3.14`, `MainThread` processes were PPID=1 and UNCLASSIFIED; these are **not confirmed workers or schedulers**, and PID lifecycle has not been checked. No process role was positively labeled SCHEDULER in that snapshot.

**Interpretation limits:** Classification is heuristic and checks entire command lines privately for generic keywords; `WEB_CANDIDATE` / `SOCKETIO` are not verified listeners, scheduler non-detection does **not** prove the scheduler is disabled, and being PPID=1 does not prove harmless orphan state. The guard reviewed no process environment, credentials, private site records or sensitive command arguments, and performed no restart. Frappe source is at `25a7b6be...` on disk, but code activation of existing long-lived HTTP/worker processes and the known broken third-site scheduler risk remain **unverified**.

**Next safe step:** classify only current Honcho process tree with strict allowlisted signals from `/proc`, printing no raw argv or environment; look for a scheduler service and identify the precise supervised DEV web process. Do not restart Honcho, Docker, broad bench services, or scheduler; no production changes. A short new Frappe process can load GitHub code directly for another unit test, but does not prove the live HTTP handler was reloaded. Separate service/restart approval required.

## November 17, 2026 — DEVELOPMENT process inventory reveals active Honcho, service roles still unresolved

The owner performed **read-only Docker process inspection** after the successful source-only update. The DEV Compose filter showed four running containers: `frappe_docker_devcontainer-frappe-1`, `frappe_docker_devcontainer-mariadb-1`, `frappe_docker_devcontainer-redis-cache-1`, `frappe_docker_devcontainer-redis-queue-1`. The first `docker top -eo comm` failed with Docker's `Couldn't find PID field in ps output` (diagnostic formatting requirement, **not** a verified Frappe service failure); corrected `docker top -eo pid,comm` succeeded.

The app container process names include **`honcho`**, four `python3.14` entries, several `python` and `MainThread` entries, `sh`/`bash`/`sleep`, and `copilot-runtime`; numbers vary and were not recorded in the handoff. This demonstrates a running Honcho supervisor / Python processes, **not** which precise Frappe web, workers or scheduler are live, nor whether the updated gateway is loaded in HTTP workers. `copilot-runtime` should not be conflated with the separately isolated stopped no-network Codex probe; do not launch unrestricted agents in the SSH-mounted legacy DEV container.

**Immediate next step:** one bounded **read-only** in-container process classification reading `/proc/<pid>/comm`, `status`, and `cmdline` but printing **only PID/PPID, executable category and allowlisted service role**, never raw argv, credentials, env, Procfiles or mount locations. The current `honcho` situation makes broad `bench start`, `bench schedule`, Compose restart, `kill` or Honcho restart unsafe without separate DEV service-boundary review, particularly given the known broken third site `ccpc-integration.localhost`. No restarts were performed in this checkpoint. The code checkout remains owner-verified at `25a7b6be...` but live process activation is still **UNVERIFIED**.

## November 17, 2026 — PR33 executive gateway security source-only update PASS in DEVELOPMENT (owner reported)

The owner executed the GitHub-reviewed and blob-pinned `scripts/development/operator/ccpc_pr33_security_source_only_four_commit_update_20261117.sh` from docs PR #37, under the exact guarded approval `CCPC_APPROVE_PR33_SOURCE_ONLY=YES`. **Operator terminal result:**

```text
SOURCE_UPDATE_SCRIPT_VERIFIED=PASS
PROTECTED_BACKUP_LOCATIONS=PASS (SHA256 independently operator-verified)
REMOTE_EXACT_PR33_HEAD=PASS
DEV_SOURCE_UPDATE=PASS
DEV_SOURCE_HEAD=25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87
PROTECTED_AGENTS_ONLY=PASS
SOURCE_DELTA=4_COMMITS_2_PYTHON_FILES
NOT_RUN=bench_migrate,benches,services,schedulers,user_grants,PRODUCTION
```

**Verified milestone / boundaries:** installed shared-development `apps/ccpcerp` Git checkout is now reported at the exact GitHub PR #33 head `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`. The four ancestral commits modify only `ccpcerp/ccpc_erp/executive_reporting.py` and `ccpcerp/ccpc_erp/test_executive_reporting.py`. Owner-reported guard shows the only untracked file remains protected `AGENTS.md` and its SHA-256 matched before/after source update. Two historical protected NAS backup manifest locations were present; previous SHA256 independently checked, **not a fresh backup or restore test**. ChatGPT did not access the legacy server directly. GitHub PR #33 independently rechecked exact head and remains draft/unmerged.

**No deployment extras:** no `bench migrate`, application server/worker/scheduler restarts, grants, DB modifications, financial transactions, old/new PRODUCTION operation, PR merge or paid CI triggered by this source-only command. **Runtime activation remains unverified:** long-running Frappe web/worker Python processes can continue using previously loaded code despite the updated on-disk checkout. Earlier 15/15 exact-source synthetic Frappe tests passed in a distinct Python process, not a live browser/user execution after this switch. Do not assume the security fix is effective for current HTTP requests until DEV-only process boundaries and restart requirements have been reviewed and separately authorized.

**Next meaningful safe gate:** inventory (read-only) which DEV-specific web/worker processes actually serve requests and whether a targeted DEV-only restart can avoid broken `ccpc-integration.localhost` scheduler/site enumeration and retained OLD PROD resources. Do **not** start bench-wide scheduler/Honcho, restart Docker Compose, or touch shared production containers. Then approve/test scoped DEV runtime activation and actual executive Company-boundary/HTTP permissions before claiming P1 closed in persistent DEV. PR33 financial acceptance remains incomplete: MAIN's single `Under Review` billing batch still has zero linked invoice pairs, and effective real-accounting roles and cancellation/concurrency/recovery cases require their own acceptance. PRODUCTION remains NO-GO and untouched.

## November 17, 2026 — owner approved protected PR33 source-only DEVELOPMENT update (PREPARED, NOT EXECUTED)

Owner explicitly **approved** moving only the existing detached MAIN/Integration2-shared DEVELOPMENT application checkout from source commit `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc` to exact GitHub-reviewed and 15/15 Frappe-regression-tested PR #33 commit `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`. No permission for `bench migrate`, service/scheduler restart, Finance record writes, PROD operations, Git history rewriting, automatic Codex agent or paid provider CI.

**Reviewed GitHub branch state:** app draft PR #33 `review/billing-authorization-correction-2026-11-03` remains exact `25a7b6be...` with four ancestral commits from `1bde04bf...`, **only two modified files** (`ccpcerp/ccpc_erp/executive_reporting.py`, `ccpcerp/ccpc_erp/test_executive_reporting.py`), no DocType schema or patch changes.

**Operator script committed on docs PR #37 review branch:** `scripts/development/operator/ccpc_pr33_security_source_only_four_commit_update_20261117.sh`. Adapted from the **previous successful** one-use Nov 16 source-only update. It checks exact host/operator, preserved NAS mount and two protected backup manifests, active named DEV Compose project, detached Git HEAD/worktree-only `?? AGENTS.md`, before/after SHA256 of protected untracked `AGENTS.md`, allowlisted GitHub origin, remote exact branch SHA, four-commit ancestry, exact two-path changed-file allowlist, `git diff --check`, and source-only `git switch --detach` to the pinned target. All operations are supervised deterministic `git` and Docker exec commands; **no AI agents in the historical SSH-mounted DEV container**. No reset/clean/stash/pull/merge, no DB, no service manipulation. `CCPC_APPROVE_PR33_SOURCE_ONLY=YES` required for the approved one-time operation.

**Execution/evidence state:** This conversation can commit to GitHub but does **not** have a direct SSH connection to `ccpcerpserver`. Script is **PREPARED, not run**. Do not claim the DEV source moved until the operator returns explicit `DEV_SOURCE_UPDATE=PASS`, `DEV_SOURCE_HEAD=25a7...`, and `PROTECTED_AGENTS_ONLY=PASS` plus no STOP error. Existing protected recovery manifests were historically checksum-verified, but a fresh backup/restore has not been independently verified; this is a two-Python-file source-only operation, not an accounting-data migration. The Git checkout can be returned to the prior commit under a *separately reviewed*, guarded source-only rollback if necessary; no automated rollback is included.

**After source-update evidence:** verify GitHub PR #33 head, run read-only active gateway verification and report execution/role checks on MAIN/Integration2 as appropriate. Running browser/real-accounting acceptance, posting paired invoices, creating correction records or starting bench-wide scheduler still requires distinct explicit control. PRODUCTION remains NO-GO.

## November 17, 2026 — exact-source Frappe 16 gateway regressions PASS (owner evidence)

The owner ran the operator-delivered in-memory supported-Frappe runtime verification for app review PR #33 SHA `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`, against the still-pinned MAIN DEVELOPMENT app checkout `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc`. The owner provided the terminal's concluding lines:

```text
OK
PR33_EXACT_FRAPPE_REGRESSIONS=PASS
PR33_SUPPORTED_RUNTIME_SOURCE_ONLY_TEST=COMPLETE
PR33_OPERATOR_RUNTIME_VERIFICATION=COMPLETE
```

**Interpretation:** The source-pinned wrapper loads the exact new executive gateway and test module **in-memory**, requires **exactly 15** unittest methods and `result.wasSuccessful()`, uses actual Frappe v16/Python >=3.14 runtime context, wraps MAIN database session in `START TRANSACTION READ ONLY` with `rollback()`, and does not alter the protected app checkout. The PASS/COMPLETE markers establish the scripted **15/15 Frappe-unit-regression gate succeeded, as reported by the operator**, including cross-Company equipment-code confidentiality denial. This is stronger than manually reconstructed standalone smoke tests but still primarily mocked source/authorization fixtures, **not** live executive browser/CSRF permissions or business database/report integration, not a general invoice/GL certification. The operator shared only final result lines; full test transcript was not supplied, and ChatGPT did not run remote commands itself.

**GitHub verification:** new app PR #33 remains open/draft at `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`. Docs PR #37 previously contained the exact driver/wrapper source at `3f44dd8bb4db9ceb76e0e78c399efb1f056c7ba3`. **No new DEV source update, persistent DB write, migration, service restart, invoice approval, PRODUCTION change or paid CI run is recorded.**

**Next gated action:** separately authorize protected **source-only DEVELOPMENT checkout update** from `1bde04bf...` to exact PR #33 `25a7b6be...`, after confirming no unexpected worktree changes (only protected untracked `AGENTS.md`), remote exact SHA and four-commit/two-file diff. Preserve the source and snapshot checkpoints. Do NOT use blind `git pull`, `git clean/reset --hard`, `bench migrate`, worker restarts or blanket site operations. After an approved source update, conduct read-only active-gateway verification; separate risk review and operator authorization are still needed for persistent Finance checker approval and invoice drafts. PRODUCTION remains NO-GO.

## November 17, 2026 — exact-source Frappe 16 gateway regression runner PREPARED (NOT EXECUTED)

Owner approved continuation to validate app [PR #33](https://github.com/ccpcerp/ccpcerp/pull/33) **new** head `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87` in a supported Frappe environment **before a separately authorized source-only DEVELOPMENT update**. No paid CircleCI run, shared service restart, migration or financial transaction was approved by this instruction. Current main DEV app is still pinned at `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc`.

On this docs PR #37 review branch, prepared two **operator-invoked** files:

**Final pinned Git blobs:** wrapper `f435fa4852876eca292f14d6a7991b08b0b16e6d`, in-memory driver `58330751ea03d3ad06a79b142434f7f75002ff4a`; both are on this same docs review branch. The exact-app PR #33 expected Git blobs remain `d75ffe318788d1cd8e3b8217a74dc3f9d8860cb4` (gateway) and `b78b42a858b9b1a98ca5be79b4037eb7c7b7a1fa` (test module). Runner enforces **exactly 15** unittest methods.
- `scripts/development/operator/ccpc_pr33_exact_gateway_frappe_test_once_20261117.sh` — guarded original host/user + named DEV Docker identity, private GitHub temporary SOURCE-only clone (new PR33 SHA, clean temporary worktree, two Git blobs checked), **tar streams only three reviewed source/test/runner files** into in-memory Python for exact test execution. No existing DEV checkout switched or overwritten. Asks `sudo -v` before source streaming to avoid corrupting stdin if authentication required. Stops on any guard failure. Keeps temporary host source for inspection; no destructive cleanup.
- `scripts/development/operator/ccpc_pr33_exact_gateway_frappe_test_driver_20261117.py` — checks incoming two Git blob IDs, installed DEV original HEAD/worktree/only protected `AGENTS.md`, Python >=3.14, Frappe v16. Connects **MAIN** `development.localhost` only, begins `START TRANSACTION READ ONLY`; temporarily substitutes exact PR33 gateway in that one Python process's module cache, executes the **15 original GitHub `test_executive_reporting.py` unittest methods** against Frappe context (with mocked authorization/data lookups), restores module references, explicitly rolls back and destroys the connection. No user/master/invoice/ledger creation; no DB write, fixture mutation, bench migration, service changes or third-site connection.

**Verification still pending:** script source committed and statically inspected in GitHub, but **not executed against the owner Frappe host** at this checkpoint. A successful `PR33_EXACT_FRAPPE_REGRESSIONS=PASS` would prove the exact production-relevant controller and unittest logic in the actual Frappe v16 interpreter, **not** live executive role/browser acceptability, SQL integration, confidential legacy records, posting/GL, concurrent approval, or PRODUCTION readiness. Current exact new GitHub head had no published CI checks when last queried; do not extrapolate earlier green results.

Next one operator step: fetch docs PR #37 pinned commit, verify wrapper and driver blobs, `bash -n` wrapper, and invoke one reviewed wrapper. Review output (expect 15 discovered tests, all PASS, rollback/COMPLETE), stopping on unexpected results without modifying the active DEV app. If this passes, decide separately whether to approve a protected DEVELOPMENT source-only update, followed by scoped live read-only gateway acceptance.

## November 17, 2026 — executive equipment cross-Company exposure fix committed to GitHub (NOT DEPLOYED)

**Owner authorization:** targeted executive-report security fix plus regression tests **in GitHub only**; no DEVELOPMENT checkout, service/migration, finance transaction or PRODUCTION change.

**Authoritative app review branch:** [draft PR #33](https://github.com/ccpcerp/ccpcerp/pull/33), `review/billing-authorization-correction-2026-11-03`, verified new HEAD **`25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`**, four commits ahead of the previously DEVELOPMENT-deployed `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc`, zero behind, **exactly two changed files**:

- `ccpcerp/ccpc_erp/executive_reporting.py` — `_assert_returned_companies()` now checks **both** returned frozen `source_equipment` and `source_equipment_code` identifier values against their `Equipment Registry.company`, denying any foreign, unresolved/missing registry, or malformed non-string identifier before the executive response is returned. Blank/null legacy values remain allowed, and duplicate local IDs are resolved only once per request. The native System Manager equipment report, its quality flags and report layout remain unchanged. Source code commit `c77156fe324e0789191fe8554453e0ac85c483a3`.
- `ccpcerp/ccpc_erp/test_executive_reporting.py` — focused mocked Frappe regressions for a foreign second code despite valid first link, foreign second with absent first, dangling first/second Registry names, foreign first with valid second, locally owned conflicting snapshots, no snapshot, repeated ID lookup, malformed reference type, and full `run_group_report()` denial with context reset. Tests commits `e69fd6c6050c95880e67daf7a4ed0d23103917ab`, `9a877191764e41d715dcaf4828bf839c57c4d2ea`, and style-only `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`.

**Evidence levels:** connected GitHub independently re-fetched changed blobs, PR #33 new head and exact two-file diff. The assistant executed **8/8 local standalone Python smoke cases** on a manually extracted/reconstructed ownership-guard branch; all passed, but this is **not** execution of the exact checked-in Frappe unittest file or a supported-runtime Frappe/MariaDB/browser test. No paid CI was manually triggered. At handoff write time the new GitHub commit had **no published commit statuses/check runs**; do not extrapolate prior CircleCI green checks at `1bde04bf...` to the new head. The exact GitHub regression methods must still run in a protected supported Frappe v16 environment, and an authorized executive data-boundary test must pass before release.

**Critical DEV separation:** MAIN and Integration2 currently share the already-verified *older* detached source checkout `1bde04bf...`; this GitHub-only fix has **not** reached them. No new DocType JSON/setup/hook/patch modifications, hence **no schema migration attributable to this focused fix**. Do not run Nov 4 consumed billing one-shot scripts, `git pull`, `bench migrate`, new invoice approval or services as part of the code commit. A separate reviewed **source-only** DEV update and read-only/bounded acceptance evidence are required; keep the sole protected untracked `AGENTS.md` and prior NAS recovery sets intact. PRODUCTION unchanged and NO-GO pending independent release approval.

## November 17, 2026 — two-site PR33 consolidated read-only billing audit COMPLETE

Owner ran the exact commit/blob-pinned `scripts/development/operator/ccpc_pr33_consolidated_readonly_dev_inventory_20261116.sh` from docs PR #37 (prior docs commit `8a3e4d82f1cf99d34d72151b285b279c6d4c697b`, Git blob `236b08e8405e7107f4c7cfc7cb1caad9b04de2e2`), supervised as `gani` on `ccpcerpserver`; reported `AUDIT_SCRIPT_VERIFIED=PASS`, `PINNED_SOURCE_AND_PROTECTED_WORKTREE=PASS`, `THREE_SITE_CONFIGS=PRESENT`, `BROKEN_THIRD_SITE=NOT_CONNECTED`, and final `DEV_CONSOLIDATED_READ_ONLY_AUDIT=COMPLETE`. Both MAIN `development.localhost` and synthetic Integration2 `ccpc-integration2.localhost` started explicit read-only transactions and completed their diagnostics. **No MAIN or Integration2 DB transaction or service action was authorized by this inventory; no third-site DB connection occurred.**

**MAIN PASS flags:** Billing Batch and Correction DocType/table presence, Billing Preparer/Finance Controller/Executive role definitions, all four report registrations, executive Page registration, two expected Companies/abbreviations, synthetic maker/checker enabled and each with exact expected role sets and exactly two generic Company User Permissions, billing DocPerm rows checked by script. Synthetic actor checks **PASS**, but do not certify effective composite DocPerm/Custom DocPerm, Account/Item/Customer/Supplier source reads, native Sales/Purchase Invoice submit rights or real nominated accounting users. Enabled named System User count by role (not identities): **2 Billing Preparers, 2 Finance Controllers**; counts are distinct from exact synthetic actor checks.

**Actual MAIN CCPC → Ricor billing state:** `MAIN_CCPC_RMC_BATCH_TOTAL=1`, `MAIN_BATCH_UNDER_REVIEW_COUNT=1`, `MAIN_BATCH_UNDER_REVIEW_SALES_LINKS=0`, `MAIN_BATCH_UNDER_REVIEW_PURCHASE_LINKS=0`; `MAIN_CORRECTION_TOTAL=0`. `MAIN_INVOICE_PAIR_TOTAL=0`, `MAIN_INVOICE_PAIR_SAMPLED=0`, `MAIN_INVOICE_PAIR_SAMPLED_MISMATCH_COUNT=0`. **Zero mismatches on zero pairs is NOT an invoice integrity PASS or demonstration of checker invoice creation**; the sole batch remains `Under Review` without invoices. Do not rerun consumed November 4 `9f174bb9...`-pinned one-shot maker/checker scripts.

**Integration2 PASS flags:** Billing Batch and Correction schemas, Billing Preparer/Finance Controller/Executive role definitions, all four report registrations and executive Page. These are **metadata checks only**; the earlier Integration2 missing-Department-column concern is not resolved by registered reports and remains subject to actual read-only `information_schema` or schema checks. No tests executed for the browser/HTTP/CSRF, effective real users, concurrent financial operations, ledger GL reconciliation, cancellation, correction, or production.

**Go/no-go:** This completes the agreed one-pass **read-only** DEVELOPMENT inventory and removes several metadata/role-presence uncertainties; overall PR #33 persistent DEV financial acceptance remains **NO-GO/PARTIAL** pending actual approved checker invoice-pair testing, real-user permissions, P1 executive equipment gateway disclosure fix, accurate report execution/reconciliation, concurrency and scheduler/recovery gates. The five-commit source-only PR33 checkout required **no new schema migration**; do not trigger bench-wide migrate or modify finance records without a separate bounded authorization and fresh scoped backup/recovery review. Keep PRODUCTION untouched.

**Next fastest value:** review the independent Codex P1 equipment-code source finding and prepare a focused, tested Python-only gateway regression/security fix in GitHub (requires owner approval for authorization behavior); separately get exact-head CI case logs and plan a safeguarded one-shot MAIN DEV Checker acceptance from the one existing `Under Review` batch. Use the Stage A offline Codex worker only as an offline proof; Stage B auth/egress remains gated.

## November 17, 2026 — separate Codex Stage A offline worker complete; Stage B gated

The owner reported successful execution of the approved, exact-source PR #36 `ccpc_codex_stage_offline_worker_20261116.sh` setup. Key output:

```text
ISOLATED_PROBE_CONFIG=PASS
ISOLATED_CODEX_CLI_VERSION=0.161.0
OFFLINE_WORKER_STAGE=PASS
PROBE_STOPPED=YES
NETWORK=NONE
NO_MODEL_AUTH_OR_AGENT_RUN=PASS
CURRENT_DEV_AND_PRODUCTION_UNCHANGED_BY_THIS_SETUP=YES
```

The Codex CLI printed one nonfatal warning that PATH aliases could not be created on the deliberately **read-only root filesystem** (`os error 30`). CLI version check nonetheless succeeded. **Do not turn off root read-only, retry the consumed one-shot setup or modify credentials** to quiet the warning.

**Verification level:** operator-reported guarded image build/container config and CLI-version smoke; not independent ChatGPT remote Docker inspection. The new `ccpc-codex-isolated:0.161.0-offline` image and stopped `ccpc-codex-isolated-offline-probe-20261116` now reportedly exist. No agent inference, login, model network access, host source mounts, DEV SQL mutations, services, or PROD changes occurred in Stage A. PR #36 handoff recorded this at commit `fea7cd81ce891da8cf37df9866d50ed8b4b13fdf`.

**Important NEXT GATE:** `--network none` means Stage A is not a functioning Codex research worker. Stage B must establish *credential-safe, outbound-only* model/auth access with verified private-LAN/PROD/host/metadata denial, and transient writable home for login without copying any existing authenticated Codex/SSH state. Generic Docker bridge or host network is **not** accepted as sufficient isolation. No agent run/CI billing/network/firewall modification has been authorized beyond Stage A. Review Stage B independently. Meanwhile, speed up actual ERPNext acceptance using the already prepared one consolidated read-only MAIN/Integration2 diagnostic combined with the supplied broad isolated Codex Cloud report; PR #33 remains draft/unmerged and PRODUCTION NO-GO.

## November 16, 2026 — owner approved separate Codex worker; offline setup prepared (NOT EXECUTED)

Owner explicitly approved setting up a **new, isolated DEVELOPMENT-only Codex worker** after confirming `codex-cli 0.161.0` inside the legacy SSH-mounted DEV container. The team **must not run Codex in that existing container** or under host `gani` (who has `sudo`/`docker`/`lxd`). The new worker setup is implemented **in GitHub only** on [draft docs PR #36](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/36), branch `review/development-execution-access-2026-11-15`, verified latest setup branch commit `dc32050fabf87edab83edd3785646c1ef6b321fb` (offline setup script blob `801d42c46168fc23d72a29655b07c72f7e0520cf`).

**Prepared new files:** `scripts/development/codex-isolated/Dockerfile` (clean nonroot image, Codex CLI pinned at 0.161.0); `scripts/development/codex-isolated/ccpc_codex_stage_offline_worker_20261116.sh` (owner-run, exact host Docker/OLD/DEV gate, build only new image, create new `--network none`/no-mount/no-root/no-socket probe, check CLI version, leave container stopped); `tests/test_ccpc_codex_isolated_offline_worker_static.py`; `scripts/development/codex-isolated/README.md`; and updated `docs/ccpc-project/DEVELOPMENT-DIRECT-EXECUTION-ACCESS-2026-11-15.md`.

**Why Stage A is offline:** The host operator can build a clean Node/Codex image with npm public package traffic, but the resulting runtime has `--network none`, so it **cannot yet run model inference, log in or investigate DEVELOPMENT autonomously**. Its only task is a reviewed `codex --version` isolation smoke. Do not copy any old `.codex` auth, SSH folders, GitHub tokens or DEV/PROD configuration into it. Before opening model egress, a separately reviewed network/credential boundary that blocks private LAN, OLD/NEW PROD, Docker daemon and all unrelated networks is required, along with sanitized read-only source/diagnostic delivery. No paid API or automatic reporter authorized.

**Status:** setup script committed to GitHub, **NOT executed** by ChatGPT or the operator as of this checkpoint. No new image/container/secret mount, site DB change, service restart, deployment, network/firewall change, old PROD data change or CI run observed. Next one operator step is exact GitHub commit/blob-pinned delivery of the Stage A script, static `bash -n`/unit tests, and supervised host execution; STOP on mismatch, no automatic retry. The Codex Cloud report plus consolidated MAIN/Integration2 read-only operator diagnostic remains the fast acceptance alternative.

## November 16, 2026 — Codex CLI present in legacy DEV container, execution still restricted

The owner ran a bounded no-agent invocation of the exact named DEVELOPMENT container and reported:

```text
CONTAINER_USER=frappe
CONTAINER_CODEX=FOUND
codex-cli 0.161.0
```

This **locates Codex CLI v0.161.0 inside** `frappe_docker_devcontainer-frappe-1`, not in the normal host `gani` shell's PATH. The command was a read-only executable/version check, **not** an agent investigation or authorization to give Codex database/Docker/production access. The container's previously verified `ssh_mount=true` at `/home/frappe/.ssh` remains a blocking security condition for agentic execution; its `privileged=false` and `docker_socket=false` results are not enough to neutralize credential exposure.

**Shortest safe approach:** use the already verified source-only Codex Cloud report plus owner-executed consolidated **read-only** two-site diagnostic to obtain real DEV evidence. For an on-host Codex runtime, review and separately approve a dedicated new isolated unprivileged worker (no shared host or DEV container user, no credential mounts/production configs, no sudo/Docker socket, no unrestricted network/host filesystem and no extra API billing); do **not** use `docker exec ... codex` inside the legacy DEV container, `sudo codex` as `gani`, or duplicate old autonomous Codex reporting. No worker was created or run.

## November 16, 2026 — host Codex CLI PATH / isolation availability reported

Owner ran the proposed read-only host identity and tool lookup on `gani@ccpcerpserver`; exact summarized output: `USER=gani`; groups `gani adm cdrom sudo dip plugdev users lxd docker`; `codex: not installed`, `bwrap: not installed`, `podman: not installed` (the command names were **not resolved by the current shell's PATH**, not proof of absence elsewhere). This does **not** mean that Codex isn't installed in the existing DEV container or a non-PATH directory.

**Security decision:** `gani` has `sudo`, `docker` and `lxd` memberships, each potentially privileged. Do not start unrestricted Codex on the host under this identity, run it as root, or reuse the existing `frappe_docker_devcontainer-frappe-1` container with its verified `/home/frappe/.ssh` mount. `codex --sandbox read-only` alone would not hide host-readable credentials or PRODUCTION resources.

**Single safe next operator action:** check whether a `codex` executable is discoverable in the named DEV container's default PATH or a small allowlist of executable paths using bounded `sudo docker exec --user frappe ... bash -c` identity/version inspection **without launching any agent**, opening configurations/auth files, exposing keys, inspecting sensitive mounts, or writing data. After locating the binary, design/reuse a dedicated new no-credential/no-sudo/no-Docker-socket isolated worker via reviewed PR #36 rather than enabling autonomous agents in the legacy DEV container. The consolidated read-only DEV diagnostic and cloud Codex report remain the practical alternate route pending that isolation.

## November 16, 2026 — broad Codex report received; local server Codex evaluated

Owner provided a one-pass Codex report for app SHA `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc` and docs commit `c1692157f8a6a5fa1f07717a2b9b59da7879bcbb`. The report states **57 static/isolated tests PASS** (46 policy/allocation/source; eight billing CI guards; three disposable site guards), 155 application Python files parse, but this was under Python **3.12.14** versus project requirement >=3.14, **not** actual supported-runtime/MariaDB acceptance. The supplied report is **not** an independently re-run Codex session in ChatGPT; no live host access, DEV database writes, provider CI run, deployment or commit was reported.

**P1 source finding independently reconfirmed in connected GitHub:** `ccpcerp/ccpc_erp/executive_reporting.py` `_assert_returned_companies()` equipment case checks `row['source_equipment']` ownership but **not** `row['source_equipment_code']`; `ccpc_erp/report/ccpc_equipment_job_material_activity/ccpc_equipment_job_material_activity.py` `_present()` emits both raw fields even for `SNAPSHOT_PAIR_CONFLICT`. Supplied Codex report claims a mocked reproduction of foreign-equipment-code passage; live data disclosure **not observed**. Proposed smallest fix is fail-closed on both identifiers and add regressions, without granting further roles, modifying existing native report diagnostics or touching production. **Application source not yet changed.**

Owner proposed running existing **host-installed Codex under `gani@ccpcerpserver`** for a more comprehensive live DEVELOPMENT investigation. This can be productive **after a separate isolation boundary**: `gani` has supervised `sudo docker` access and host visibility; DEV container `frappe_docker_devcontainer-frappe-1` has `ssh_mount=true`; OLD PROD MariaDB/Redis and backups coexist on original host. `codex --sandbox read-only` limits writes but not all reads available to that process's OS identity. Do **not** run the agent freely as `gani`, root, or inside existing SSH-mounted DEV container. Instead reuse the separate [`DEVELOPMENT-DIRECT-EXECUTION-ACCESS-2026-11-15.md`](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/review/development-execution-access-2026-11-15/docs/ccpc-project/DEVELOPMENT-DIRECT-EXECUTION-ACCESS-2026-11-15.md) design on draft PR #36: dedicated non-root/no-sudo isolated worker, no SSH/NAS/PROD/Docker-socket mounts, no host network, bounded egress; narrow allowlisted read-only DEV diagnostics whose aggregated results Codex can analyze. **No worker has been installed/activated by this chat**; no new API keys or auto-reporting.

**One read-only operator verification before considering host Codex:** report `hostname -s`, `id -un`, `id -nG`, `command -v codex`, and `codex --version` (no environment dumps, CLI config, auth files or secrets). Then review actual isolation capability. The previously prepared consolidated DEV read-only operator diagnostic on docs PR #37 can independently collect metadata and invoice-link counts without allowing Codex a general Docker shell. The attached report's remaining P1 gaps—effective real actor permissions, scheduler scope/restore—and P2 Integration2 Department fields are still pending. No broader host commands, live authorizations or PRODUCTION operations authorized.

## November 16, 2026 — switch to one broad Codex review plus consolidated DEV diagnostic

Owner explicitly approved a **wider, one-pass isolated Codex investigation** of the whole Withdrawal Slip → Material Issue → SLE/GL → Finance Mapping → Intercompany Billing → four-report delivery chain. This replaces the repetitive one-check-per-turn investigation as the preferred review technique. It **does not** authorize new API billing, paid provider CI, automatic Codex-to-GitHub reporting, persistent DEV or PRODUCTION writes, user changes, scheduler/service operations or a PR merge.

- **Codex task brief committed:** [`CODEX-CONSOLIDATED-READINESS-AUDIT-2026-11-16.md`](CODEX-CONSOLIDATED-READINESS-AUDIT-2026-11-16.md). One report covering source/code risks, real vs mocked test matrix, top five fixes, safe DEV acceptance and GO/NO-GO. Exact app review branch `review/billing-authorization-correction-2026-11-03` @ `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc`. Read-only external Codex Cloud task **NOT launched through ChatGPT** because no connected Codex task-launch action is exposed in this chat; it must be manually started in an isolated Cloud environment with only approved GitHub repository access. No restricted DEV SSH mount, local secrets, schedules, or self-hosted autonomous agents.
- **One host operator diagnostic prepared in GitHub, not executed:** [`scripts/development/operator/ccpc_pr33_consolidated_readonly_dev_inventory_20261116.sh`](../../scripts/development/operator/ccpc_pr33_consolidated_readonly_dev_inventory_20261116.sh). This uses read-only per-site Frappe transactions on exactly MAIN and Integration2 (broken third site checked for config but **never connected**), no secret/identity/document/amount output; guards exact PR #33 checkout/sole `AGENTS.md`, DEV Compose identity, NAS historical manifests. It produces role/master scoped synthetic checker/preparer counts, Company grants, DocPerm, billing status/link counts, invoice pair consistency sample, correction case counts, and four-report metadata presence. No migration, financial transaction, cache reset, scheduler/web service restart or PRODUCTION action.
- **Validated baseline:** supervised source update `DEV_SOURCE_UPDATE=PASS`, exact app head `1bde04bf...`; MAIN Billing Batch/Correction DocTypes and SQL tables plus Billing Preparer/Finance Controller role definitions all `PRESENT`; two protected Nov 4 Synology recovery sets passed `8/8 + 4/4` SHA-256 checks. Backup freshness and actual restore remain **NOT VERIFIED**. Third site scheduler exposure and DEVELOPMENT browser runtime still **NOT VERIFIED**. Previous Nov 4 one-use scripts were pinned to `9f174bb9...` and must **not be rerun** on the new app head.

**Next operational sequence (one user-controlled batch, no repeated approvals for reads):** manually start Codex Cloud's isolated broad audit; optionally run the exact GitHub-pinned read-only consolidated diagnostic once on the original DEV host; review those two evidence sets together and implement scoped fixes through GitHub. Production remains NO-GO without distinct release approval. The Codex brief and diagnostic are **prepared**, not executed; never report Codex tests or DEV diagnostic as PASSED without the actual outputs.

## November 16, 2026 — MAIN DEVELOPMENT PR #33 schema/role presence PASS (owner read-only)

Owner executed the approved exact-HEAD + protected-worktree, MAIN `development.localhost`, Frappe `START TRANSACTION READ ONLY` inventory, explicitly rolled back and destroyed the session. **Exact reported output:**

```text
BILLING_BATCH_DOCTYPE=PRESENT
BILLING_BATCH_TABLE=PRESENT
BILLING_CORRECTION_DOCTYPE=PRESENT
BILLING_CORRECTION_TABLE=PRESENT
BILLING_PREPARER_ROLE=PRESENT
FINANCE_CONTROLLER_ROLE=PRESENT
BILLING_METADATA_INSPECTION=COMPLETE
```

Interpretation: The installed Frappe metadata and underlying SQL tables for the Intercompany Material Billing Batch and new CCPC Intercompany Billing Correction are both present on MAIN; named `CCPC Billing Preparer` and `Finance Controller` role definitions exist. This supersedes the Nov 3 **absent correction/role** inventory, which was before the Nov 4 persistent DEV work. The five Nov 4→Nov 16 GitHub changes affect **only** the existing billing Python controller and test module, not DocType JSON, hooks, setup or schema. Accordingly, **do not rerun `bench migrate` merely for the Nov 16 source-only update**. However, presence alone does not establish complete field schema alignment, actual `Has Role` assignments, Company User Permissions, ledger/report correctness or successful real-user acceptance.

Next safe read-only step: verify the owner-nominated **existing synthetic DEV billing maker/checker** (`ccpc-billing-preparer-dev@testing.invalid` and `ccpc-billing-checker-dev@testing.invalid`, sourced from the Nov 4 reviewed operator scripts) are still enabled named System Users with exact expected roles, precisely scoped Company grants for Cagayan Corn Products Corporation and Ricor Mills Corporation, and review the status/invoice-link presence of existing CCPC→Ricor billing batches. Do **not** commit, finalize or approve financial transactions, create users/grants, run old SHA-pinned Nov 4 scripts (they intentionally reject current `1bde04bf...`), start bench or touch PRODUCTION. If synthetic acceptance records exist, read-only evidence comes first. Source-only checkout, protected backups 12/12 integrity and SSH-mount/agent restriction remain in force.

## November 16, 2026 — PR #33 source-only checkout completed in DEVELOPMENT (owner-reported PASS)

**Owner-supplied exact output from the approved pinned one-use operator script:**

```text
REMOTE_EXACT_PR33_HEAD=PASS
DEV_SOURCE_UPDATE=PASS
DEV_SOURCE_HEAD=1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc
PROTECTED_AGENTS_ONLY=PASS
NOT_RUN=bench_migrate,benches,services,schedulers,user_grants,PRODUCTION
```

**Scope and evidence:** The original named DEVELOPMENT container checkout was moved from `9f174bb9ce9b9ae103bf968c87c0d703aa039c34` to the exact newer PR #33 head `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc`; the operator script checked the private GitHub review ref, five-commit ancestry and two-file change allowlist, and preserved the sole protected untracked `AGENTS.md`. The operation was supervised by the owner, not performed through a ChatGPT terminal. GitHub PR #33 was rechecked and remains open/draft at exactly that SHA. **No migration, service/worker/scheduler restart, real-user grant or PRODUCTION change occurred in this operation** (not evidence about other historical changes).

**Important supersession:** Previous sections referring to an incomplete pending checkout are historical; **this source-only milestone is complete**. The Nov 4 two-site and MAIN billing Synology backups passed 8/8 + 4/4 SHA-256 earlier today, but were not refreshed or restore-tested on Nov 16. The existing DEV container still has an SSH bind mount (`privileged=false ssh_mount=true docker_socket=false`), so no unrestricted Codex/agent runs in it.

**Next one read-only MAIN DEV gate:** verify actual `development.localhost` DocType and SQL-table presence for `Intercompany Material Billing Batch` and `CCPC Intercompany Billing Correction`, and Role presence for `CCPC Billing Preparer` and `Finance Controller`, under a read-only Frappe database transaction, after guarding the new exact HEAD and preserved worktree. There were Nov 4 DEV-specific scripts for named synthetic billing actors, so do not rely on older Nov 3 role-absence inventory as current. The five-commit delta has **no DocType schema / hook / setup file changes**, and a new migration is **not presumed necessary**; decide only after actual metadata evidence. No blanket `bench migrate`, schema updates, user-role changes, CI reruns, scheduler starts, or production changes are authorized.

## November 16, 2026 — operator script host Docker invocation adjusted, NOT EXECUTED

The approved exact-scope PR #33 source-only operator script now uses the existing **`sudo docker inspect` / `sudo docker exec --user frappe`** access pattern from owner-provided host diagnostics. This is because the normal operator `gani` may not be in the Docker group; running the entire script as root would fail the required `gani` identity guard and weaken safeguards. **No other Git/source target, test, or DB behavior changed.** Exact source file: `scripts/development/operator/ccpc_pr33_source_only_five_commit_update_20261116.sh`, Git blob SHA **`076b94ada18ccd59247b05012cb7b8da649e5de7`**, reviewed script update commit `19a7beb53d77016452eed3268bc69e11ff4a697e`. Previous script blob `ee5e...` is superseded by this operator-only improvement.

The owner had explicitly approved this **source-only operation**, including the reviewed fail-closed procedure. It still must be executed **by the owner**, not by this GitHub-only chat. The procedure should be obtained from the GitHub branch, exact revision/blob verified and `bash -n` passed before `CCPC_APPROVE_PR33_SOURCE_ONLY=YES bash ...`. It does not authorize migrations, service starts, real users, backups/restores, Codex in SSH-mounted container or PROD. Collect outcome `DEV_SOURCE_UPDATE=PASS` and exact target HEAD; on STOP do not automatically retry.

## November 16, 2026 — owner approved supervised source-only update; execution pending

The owner explicitly approved running the previously prepared, GitHub-pinned **five-commit DEVELOPMENT source-only** procedure. **Authorization covers only** detached source checkout `9f174bb9ce9b9ae103bf968c87c0d703aa039c34` → `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc` on named legacy DEVELOPMENT host/container, after its fail-closed safeguards. The script is `scripts/development/operator/ccpc_pr33_source_only_five_commit_update_20261116.sh`, blob SHA `ee5e3608b84cd93d3cfab0e45fca8ab3179ff3c7`. Documentation review branch commit prior to this handoff edit: `712ee9054268e5ca77ec07da7840a35deb440c5f`.

GitHub was rechecked: app PR #33 still draft/open at target SHA, five commits ahead/zero behind installed revision, exactly two billing Python files differ. Private repository script contents were refetched and confirmed. **The ChatGPT session has no remote terminal/SSH execution tool, so the operator has to execute the approved procedure; this approval is NOT proof it ran.** Do not claim a completed checkout until owner reports `DEV_SOURCE_UPDATE=PASS` and target SHA, and independently revalidate status. The original `gani` account may need Docker permission; if host Docker invocation is denied, STOP and revise the reviewed procedure rather than run the entire script as root.

No migrations, database writes, backups/restores, service/worker/scheduler start, credentials exposure to Codex, user grants, PR merge, or OLD/NEW PRODUCTION action are included in this approval. Next after confirmed source checkout: fresh scoped backup/rollback and **separate migration authorization**; known broken third DEV site remains excluded.

## November 16, 2026 — 12/12 protected NAS checksums PASS; source-only PR33 update prepared

Owner ran the reviewed read-only `sha256sum --status --check SHA256SUMS` procedure on the exact protected Nov 4 Synology recovery sets, with host, NAS mount and per-manifest count checks. Reported complete output:

```text
BACKUP_8_FILES_CHECKSUM=PASS
BACKUP_4_FILES_CHECKSUM=PASS
PROTECTED_DEV_BACKUP_INTEGRITY=PASS
```

**Evidence:** All **12/12 backup archive/config/data file SHA-256 hashes** match each global manifest: eight entries in `ccpc-development-pr33-20261104T010408Z-82316b860fe951ad` and four in `ccpc-development-pr33-billing-preacceptance-20261104T082044Z-4231b0c38ab77bf0`. This establishes read integrity, **not** freshness as of Nov 16, database transaction currency, recovery drill success, or readiness to migrate. Do not replace/delete these recovery artifacts.

**Prepared GitHub-only script, NOT EXECUTED:** [`scripts/development/operator/ccpc_pr33_source_only_five_commit_update_20261116.sh`](../../scripts/development/operator/ccpc_pr33_source_only_five_commit_update_20261116.sh) on this docs review branch. It is pinned to the owner-confirmed DEV HEAD `9f174bb9ce9b9ae103bf968c87c0d703aa039c34` and GitHub PR #33 `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc`; requires an additional explicit one-use source-only execution authorization, exact normal host/operator and named DEV container/Compose project, backup locations, protected sole untracked `AGENTS.md`, detached clean tracked checkout, allowlisted GitHub origin, exact remote branch SHA, five-commit ancestry and exactly two changed billing Python files. It fetches just the review ref and performs a **detached source-only `git switch`**, then verifies exact target and worktree. No reset, clean, stash, merge, database/migration, services, scheduled jobs, user-role changes, backups, or PRODUCTION operation.

**Static shell syntax preflight:** An equivalent reconstructed script body passed local `bash -n` on Nov 16 (`BASH_SYNTAX=PASS`). This is **not** host runtime validation or a test of the exact GitHub file bytes on the office server; the GitHub file was separately refetched to review its contents and guards.

**Next decisive action:** owner separately approves or declines executing the pinned DEV **source-only** update. If approved, first ensure the operator can obtain and independently review the **exact checked-in script bytes** (GitHub private repository; never run an unreviewed downloaded script). Use existing supervised operator workflow, not Codex in SSH-mounted DEV. STOP on any failed guard or unexpected Git result; do not auto-retry. **Migrations require a new fresh scoped backup/recovery review and separate authorization**; even source-only update is not permission to migrate.

## November 16, 2026 — protected NAS backup manifest presence confirmed (operator read-only)

The operator ran the reviewed exact-host/NAS mount/manifests guard and reported `PROTECTED_DEV_BACKUP_MANIFESTS=PRESENT`. The check required:

- Host shortname `ccpcerpserver`.
- NAS `/mnt/erpnext_backups` mounted from the exact expected CIFS source `//192.168.50.132/erpnext_backups`.
- Existing global `SHA256SUMS` under `ccpc-development-pr33-20261104T010408Z-82316b860fe951ad` (two-site recovery set).
- Existing global `SHA256SUMS` under `ccpc-development-pr33-billing-preacceptance-20261104T082044Z-4231b0c38ab77bf0` (MAIN pre-billing-acceptance set).

**Evidence level:** manifest locations PRESENT, not actual contents/checksums reverified. These are Nov 4, not necessarily current DB/file recovery points. Do not infer latest transactional data, restore success or safe migration solely from file existence.

**Next approved read-only integrity check:** use `sha256sum --status --check SHA256SUMS` in each guarded NAS set with expected global manifest line counts **8 and 4** respectively, no filenames/data printed. Stop on checksum, NAS identity, path type or count mismatch. This reads NAS backup bytes but makes no changes to backup, database, Docker, service, Git, or PRODUCTION. It does not establish backup currency; before any approved persistent DEV data migration obtain a fresh scoped four-artifact snapshot and recovery check. The source-only checkout change is also separately approval-gated.

## November 16, 2026 — DEV container security flags observed (owner read-only output)

The operator inspected **only** `frappe_docker_devcontainer-frappe-1` using a metadata-only `sudo docker inspect --format` command and reported:

```text
privileged=false ssh_mount=true docker_socket=false
```

**Interpretation:** DEV container is nonprivileged and lacks the usual Docker socket mount, but **still has an SSH-directory bind mount at `/home/frappe/.ssh`**. This is consistent with the earlier October 10 direct observation of readable SSH material, although this latest three-flag check did **not** re-read key files or verify other mounts. Do not execute unrestricted/unattended Codex or another automated agent in this existing container. Neither deleting OLD PRODUCTION data nor granting Docker privileges would fix this mount exposure. It does **not** prevent supervised, bounded operator-driven diagnostics/source verification when reviewed for host side effects; no SSH-key contents were collected.

**Next DEV acceptance Gate A:** read-only check of the exact protected local and Synology backup manifest locations using the November 4 operator runbooks, without reading/deleting protected data or executing older one-use backup scripts. Verify source checkout remains pinned before any later source update. Full backup integrity/freshness and rollback readiness are **still unverified**; existence alone is not enough to approve checkout/migration. GitHub remains authoritative for tracked source changes. PR #33 draft head is five commits ahead of owner-confirmed installed `9f174bb9...`.

## November 16, 2026 — owner-reported read-only DEVELOPMENT Git/site preflight PASS

**Verified from exact operator output**, not from a direct ChatGPT host connection:

```text
DEV_HEAD=9f174bb9ce9b9ae103bf968c87c0d703aa039c34
DEV_BRANCH=DETACHED
DEV_WORKTREE=PROTECTED_AGENTS_ONLY
SITE_PRESENT=development.localhost
SITE_PRESENT=ccpc-integration2.localhost
SITE_PRESENT=ccpc-integration.localhost
```

Interpretation: running named DEV container's app checkout at `9f174bb9...` and clean tracked worktree, **only** protected untracked `AGENTS.md`, three known site configuration filenames. GitHub independently confirms app PR #33 remains open/draft at `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc`; ancestry compare from live DEV SHA gives **five commits ahead, zero behind, only two modified files**: `intercompany_material_billing_batch.py` and `test_intercompany_material_billing_batch.py`. Latest head has successful `python-syntax`, manual approval and isolated billing-integration CircleCI statuses. A successful status does not by itself establish actual DEV runtime/metadata acceptance.

**This resolves the prior ambiguous checkout SHA:** don't cite `e1d67f2` as still installed. It does **not** verify migrations, roles, site DB health, third-site scheduler safety, recovery backups, host mounts/SSH exposure or current process state. No checkout/pull/migration/permissions changes made.

**Next one read-only Gate A check:** exact DEV-container privileged/SSH-key/Docker-socket mount flags plus existence (not contents) of approved protected recovery manifests/NAS mount. If credential bind mount persists, **do not run Codex or unattended agent inside this existing container**. Only after worktree, backups and environment gate match can a fresh, narrowly scoped source-only update to the five-commit-later PR #33 head be proposed for separate approval. No broad bench startup while broken third DEV site remains in scheduler scope.

## Newest checkpoint — 2026-11-16: PR #33 billing acceptance preparation (GitHub-only)

Owner approved resuming application development pending work, reviewing latest billing changes/migration and permissions, and preparing a safe persistent DEVELOPMENT acceptance path. **No** host/DEV checkout change, migration, permission assignment, CI provider execution, PR merge or OLD/NEW PRODUCTION action occurred during this checkpoint.

- Application [PR #33](https://github.com/ccpcerp/ccpcerp/pull/33) remains **draft/open/unmerged**: exact head `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc`, base finance `a2f0e89f12afbc28ac10dab71b6af47a455fdc95`; 40 commits ahead, 0 behind, 18 changed files. Latest commit has GitHub status **success** for CircleCI `python-syntax`, manually approved billing hold and `billing-controls-isolated-integration`. Original documented Build #143 **10/10** genuine DB case results are on prior `9f174bb9...`, not automatically identical to latest head; latter is five commits further with invoice posting-date/reciprocal-link fixes/tests.
- [PR #32](https://github.com/ccpcerp/ccpcerp/pull/32) four day-one reports were **merged into finance feature** Nov 2, merge SHA `e1d67f2716d15e8ffdf42f0547c44d8324516d7e`, not yet stable production release. Last owner-reported MAIN DEV checkout was that SHA, protected untracked `AGENTS.md`; fresh live checkout/worktree verification **PENDING**. Last MAIN DEV role inventory: Billing Preparer role and correction DocType **ABSENT**, Finance Controller exists with **0 enabled named assigned users**. Recheck live before write.
- Migration `before_migrate` bootstraps role definitions without named grants, and `after_migrate` has numerous broader CCPC metadata, roles, permissions, workflow and backfill effects; it is **not billing-only**. Private correction DocType and Billing DocPerm are new. Validate exact schema, duplicate/replay/row locks and backup/rollback before any persistent DEV migration. The known excluded broken third site `ccpc-integration.localhost` may be enumerated by the bench-wide scheduler; **HOLD full Honcho startup** pending reviewed scope isolation.
- **Reviewed proposed gate plan:** [PR33-DEVELOPMENT-BILLING-ACCEPTANCE-2026-11-16.md](PR33-DEVELOPMENT-BILLING-ACCEPTANCE-2026-11-16.md), on GitHub documentation review branch `review/pr33-dev-acceptance-2026-11-16`. Exact task order: A read-only host/worktree/mount/site/role inventory → B disposable integration where needed → C separately approved protected DEV checkout/backup and sequential site migration → D separately approved real maker/checker Company/DocPerm setup → E site-isolated DEV web/queue/report/GL acceptance. No unrelated production infrastructure work.
- **Single next operator action:** when available, **read-only** DEV host check of branch/HEAD/status (without opening `AGENTS.md`), three site-config names, snapshot manifest presence, current service states and SSH/Docker mount risk. Do not restart bench, delete excluded site or OLD data, change roles or migrate based on this documentation alone. User's permission to prepare is not a blanket live-operation approval.


**Checkpoint: 2026-11-02, Asia/Manila.** This is the latest concise status after the oversized `CURRENT-HANDOFF-3.md`. Read that file for historical milestones; do not interpret its old final "next action" as current. Operational policy remains `GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md`.

## Immutable scope / source

- Source of truth: `ccpcerp/ccpcerp` PR **#32**, review branch `review/four-day-one-reports-integration-2026-10-29`, **draft/open/unmerged** at exact head `532a28d99bd0548241854495156a61f94eb1ac6b` (reconfirmed through connected GitHub on Nov 2).
- Installed code in **DEVELOPMENT only**: Docker container `frappe_docker_devcontainer-frappe-1`, bench `/workspace/development/frappe-bench`, app `apps/ccpcerp`, detached HEAD pinned to that SHA; only `?? AGENTS.md` untracked and protected. Avoid checkout or cleanup.
- DEVELOPMENT sites: synthetic `ccpc-integration2.localhost` and MAIN `development.localhost`, distinct databases. **PRODUCTION has not been touched** and requires separate explicit approval for any change.
- Protected Nov 2 four-part snapshots (do not clean up) at `/workspace/development/frappe-bench/.ccpc-pr32-snapshots/`: `ccpc-integration2.localhost-20261102T001358Z-00771ef0fbcf` and `development.localhost-20261102T002314Z-7dc759b9afc9`. Verified SHA256 copies on Synology `/mnt/erpnext_backups/ccpc-development-pr32-20261102T003434Z-237495dd9a3d4061`. No full isolated restore test.
- DEV Honcho/web/workers/scheduler were gracefully stopped for migrations and remain **not restarted** as of this checkpoint; earlier process sweep found 4 idle shells that must remain untouched. No broad Docker/host restarts.

## Owner-run verified outcomes

1. Source switch to exact pinned PR32 SHA, with worktree guard and untouched `AGENTS.md`: **PASS**.
2. Both **sequential** owner-approved DEVELOPMENT migrations (`bench --site ccpc-integration2.localhost migrate`, then `bench --site development.localhost migrate`): **PASS**, exit 0. Schema/data/backfill migration was an approved DB write; no PRODUCTION migration.
3. Postmigration metadata validation on **both sites**: Role `CCPC Group Executive Reporting`, standard Page `ccpc-group-executive-reporting` with exclusive Role, four standard native Script Reports each restricted to `System Manager`, reference DocTypes, and **0 users assigned** the new executive role: **PASS**.
4. Synthetic Integration2 lacks `tabStock Entry.department` and `tabStock Entry Detail.department`; **MAIN has both**. Department source SQL on synthetic Integration2 is not compatible and must not be represented as tested; do not manually add columns.
5. MAIN six raw underlying report SQL statements on October 1–31, 2026, explicit read-only transaction and bounded rows: **6/6 PASS**. Counts: Dept material 2, equipment material 2, equipment job 0, intercompany CCPC/RMC 1, stock source 2, P&L GL 2. Zero equipment jobs means Job Order row presentation still lacks coverage.
6. Initial standalone full-report test failed at `frappe.connect()` with `FileNotFoundError: database.log` because Python was launched from bench root while Frappe expected the sites working directory. Exact mistaken target: `/workspace/development/logs/database.log` (missing parent). Correct real bench logger: `/workspace/development/frappe-bench/logs/database.log` (present and writable). **Resolved by changing diagnostic working directory**, not by creating new directories or modifying code/database.
7. **Most recent owner-run corrected MAIN real Frappe runtime test PASS, exit 0**: run from `/workspace/development/frappe-bench/sites` with `frappe.init(site="development.localhost", sites_path=".")`, `frappe.connect()`, `START TRANSACTION READ ONLY`, Administrator diagnostic identity. Four full report `execute()` functions succeeded: Department **19 columns / 2 rows**, Equipment Material & Job **24 / 2**, Intercompany Billing **22 / 1**, Stock & P&L GL **17 / 4**. Guest and Administrator invoking `run_group_report` were **both denied** by `frappe.PermissionError`. Transaction explicitly rolled back, destroyed Frappe session, no business records/roles changed. DEVELOPMENT services **NOT RESTARTED**, PRODUCTION **NOT TOUCHED**.

## Pending / limitations

- Positive authorized executive gateway test **not performed**: new Role assigned to zero named users, and do not assign roles or create fake accounts merely for testing without approval. Further named nonexec denial, cross-company and role/DocPerm isolation, source-quality flags, row-level permissions, and web/browser UX remain pending. Historical pre-migration test found some named System Managers lacked all underlying source DocType read permissions, so do not broaden those grants automatically.
- Report outputs successfully render in Administrator diagnostic context; that does **not** certify financial totals, posted accounting balances, original source quality, or production release readiness. Original SLE, P&L GL and billing values must not be incorrectly aggregated as one cost.
- Review guarded DEV-only service restoration procedure and current stopped process status before starting services; verify exact Docker container, bench Procfile and ensure no duplicate Honcho or shared-infrastructure impact. **Do not blindly run `docker restart`, `bench start` in the background, or signal unrelated processes.** If owner authorizes the narrow service start, restore only DEVELOPMENT processes and confirm both sites and reporting browser paths. No PRODUCTION activity. No PR merge/release yet.

## Immediate next safe action

Perform a **read-only DEVELOPMENT service-start readiness audit**: inspect Procfile, process/listener inventory, process manager and exact launch mechanism from deployment docs/current environment, without starting/stopping anything. Separately decide whether to perform remaining security tests before/after DEV service restoration. Preserve protected recovery snapshots and untracked `AGENTS.md`. Update this handoff with verified results during active conversation.

## Key pointers

- Prior history: `docs/ccpc-project/CURRENT-HANDOFF-3.md`.
- Workflow: `docs/ccpc-project/GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md`.
- Code PR: https://github.com/ccpcerp/ccpcerp/pull/32 .


## 2026-11-02 — DEVELOPMENT-only service restart readiness PASS (owner output)

**Owner-reported read-only service-start audit after both DEV site migrations and successful four native report executions:**
```text
PINNED SOURCE AND AGENTS.md: PASS
PROCFILE SERVICES: web, socketio, watch, schedule, worker
PROCFILE FIVE SERVICES: PASS
DEVELOPMENT SITE CONFIGURATIONS: PASS
BENCH LOG DIRECTORY: PASS
LIVE SERVICE CANDIDATES: 0
ZOMBIE PROCESSES IGNORED: 48
DEVELOPMENT SERVICE LISTENERS: []
SERVICE RESTART READINESS: PASS
NO PROCESSES SIGNALED
NO SERVICES STARTED
NO DATABASE CHANGES
READINESS_AUDIT_EXIT_CODE=0
```
**Interpretation:** exact pinned detached PR32 source `532a28d99bd0548241854495156a61f94eb1ac6b` and protected `?? AGENTS.md` intact. The named DEV container has exactly the expected five bench Procfile labels; both DEV site configs and bench log directory present. No matching active service processes or listeners were found. **48 zombies are dead process entries, not services to signal or delete**. No files, Docker state, site DB, application code, scheduled queue state, or PRODUCTION changed by this audit. Connected GitHub reconfirms PR #32 draft/open/unmerged and head unchanged.

**Previously owner-approved next controlled action:** re-guard source, backups, exact DEV container, Procfile labels, absence of active managers/workers/web/scheduler/watch/socketio/listeners; then launch exactly one detached DEV-only Honcho `/home/frappe/.local/bin/honcho start` from `/workspace/development/frappe-bench`, using a private non-clobber log there. Verify one live Honcho manager and pinned SHA after launch. Do not restart containers, affect shared host/PRODUCTION, clear zombie entries, rerun migrations, alter roles, merge PR or automatically retry a failed launch. Manager PASS alone does not establish site HTTP readiness; separately test both sites and queue/worker/scheduler on next operator step. Retain all local+Synology snapshots and original `AGENTS.md`.


## 2026-11-02 — Honcho restart blocked by overrestrictive socketio Procfile preflight; no launch

**Owner-reported output from step 23, the guarded DEVELOPMENT-only postmigration Honcho startup attempt:**
```text
PROTECTED SYNOLOGY BACKUPS: PASS
PINNED SOURCE AND LOCAL BACKUPS: PASS
STOP: Review Procfile command socketio
DEVELOPMENT_START_EXIT_CODE=1
STOP: Do not automatically retry startup
```
The script exited during **read-only Procfile validation**, before reaching its `docker exec -d` Honcho launch. Thus this attempt **did not start** a new DEVELOPMENT Honcho manager, run a migration, change code, or touch PRODUCTION. The preflight used the predicate `'socketio.js' in command` and rejected any `;\`, `&&`, `||`, `|`, or backtick; actual Socket.IO Procfile line was not printed, so it is **unknown whether the problem was the expected path fragment, a forbidden operator, or both**. Earlier read-only readiness audit found exactly five labels `web, socketio, watch, schedule, worker`, zero live service candidates, no DEV listeners, and 48 zombie process entries (defunct, do not signal). Nov2 NAS and local backup manifests and exact pinned source guards passed in the attempted restart. Full Frappe MAIN four-report execution and Guest/Admin gateway denial previously PASS; no positive executive user test. PR #32 remains draft/open/unmerged at pinned SHA `532a28d99bd0548241854495156a61f94eb1ac6b`.

**Next one safe diagnostic:** read only the `socketio` entry in exact DEV bench `Procfile`; print its literal command after redacting any env-like secrets, and individual pass/fail booleans for `socketio.js` path fragment and each forbidden shell operator. Guard exact app SHA, detached status and protected sole `?? AGENTS.md`. No service launch or file modification. Then revise *the temporary startup guard*, not the app Procfile, based on its actual safe command; re-run full guarded DEV-only startup once after review, with no automatic retries. MAIN/Integration2 and PRODUCTION remain unchanged.


## 2026-11-02 — Socket.IO Procfile confirmed `bench socketio`; adjust only temporary Honcho guard

**Owner-run read-only exact DEVELOPMENT Procfile inspection after preflight-only startup block:**
```text
PINNED SOURCE: PASS
PROCFILE SERVICE LABELS: PASS
SOCKETIO COMMAND: bench socketio
CONTAINS socketio.js: False
CONTAINS realtime: False
CONTAINS SHELL MARKER ';': False
CONTAINS SHELL MARKER '&&': False
CONTAINS SHELL MARKER '||': False
CONTAINS SHELL MARKER '|': False
CONTAINS SHELL MARKER '`': False
SOCKETIO PROCFILE INSPECTION: COMPLETED
NO FILES MODIFIED
NO SERVICES STARTED
SOCKETIO_INSPECTION_EXIT_CODE=0
```
**Established:** the prior startup preflight incorrectly hardcoded an old Socket.IO launch fragment (`socketio.js`). The actual valid current Procfile line is **`socketio: bench socketio`** without forbidden shell operators, and exactly the five labels `web, socketio, watch, schedule, worker` remain. Do **not** modify the Procfile, app or site databases to satisfy the previous test. Source stays detached pinned at `532a28d99bd0548241854495156a61f94eb1ac6b` with only protected untracked `AGENTS.md`. Previous startup attempt stopped **before launch**. No services started, no production change. All four MAIN complete report executions and Guest/Admin gateway-denial tests already PASS; positive named executive viewer not tested because role has 0 assignments. Connected GitHub PR32 rechecked still draft/open/unmerged with exact SHA.

**Next authorized one action:** after repeating strict backup and process guards, modify only startup validation to accept `bench socketio` (exact command), and launch exactly one DEV-only Honcho process with non-clobber private bench log; verify single live manager and unchanged Git source. Fail closed on unexpected other Procfile commands, existing service processes/listeners or ambiguous launch state. No automatic retry, broad container restart, migrations, user-role edits, PR merge or PRODUCTION activity. If successful, next separate HTTP site and worker/scheduler health checks.


## 2026-11-02 — Corrected DEV startup preflight stops at worker command; no Honcho launch

**Owner report from second guarded startup attempt:**
```text
PROTECTED SYNOLOGY BACKUPS: PASS
PINNED SOURCE AND LOCAL BACKUPS: PASS
STOP: Review Procfile worker
DEVELOPMENT_START_EXIT_CODE=1
STOP: Do not automatically retry startup
```
This exited at read-only Procfile validation, **before** the one detached Honcho launch instruction. The previous Socket.IO mismatch was fixed in the temporary script: actual Procfile entry `socketio: bench socketio`. The worker failed because the script requires `shlex.split(command)[:2] == ['bench','worker']` and disallows certain shell metacharacters, but the actual worker command and precise failed predicate were not printed. It is **not** evidence that the worker is misconfigured. Earlier Procfile inspection verified five entries: web, socketio, watch, schedule, worker. The pinned source/AGENTS and NAS/local backup presence guards passed on attempted launch. Both DEV migrations, MAIN 6/6 raw SQL, four real report `execute()` functions and Guest/Admin gateway denial PASS. No service launch, code/schema/data change or PRODUCTION modification from this attempt. PR32 remains draft/open/unmerged at `532a28d99bd0548241854495156a61f94eb1ac6b` per connected GitHub.

**Next one read-only action:** inspect all five exact DEV `Procfile` commands, their tokenized command heads, and whether the current start-script validation would reject each, redacting sensitive assignments. Avoid repeating blind startup attempts. Then revise **only the temporary validation logic**, not the Procfile, to match reviewed safe commands; recheck live processes/listeners before any authorized DEV-only single-Honcho launch. No automatic retry, migrations, Docker restart, role edits, PR merge or PRODUCTION action.


## 2026-11-02 — All five DEVELOPMENT Procfile commands inventoried; worker redirects explain startup preflight stop

**Owner-reported read-only full Procfile diagnostic (`PROCFILE_DIAGNOSTIC_EXIT_CODE=0`)** verified pinned source and all five labels and commands:
```text
web:      bench serve  --port 8000
socketio: bench socketio
watch:    bench watch
schedule: bench schedule
worker:   bench worker 1>> logs/worker.log 2>> logs/worker.error.log
```
All five tokenize correctly; service heads match expected `bench serve/socketio/watch/schedule/worker`. The only shell marker across these commands is the expected worker log append redirection `>`; the previous temporary launch script rejected that marker globally, resulting in `STOP: Review Procfile worker` **before Honcho startup**. Worker redirection syntax is normal for this bench Procfile and is not proof of misconfiguration. The operator confirmed `NO FILES MODIFIED`, `NO SERVICES STARTED`, `NO DATABASE CHANGES`, `PRODUCTION: NOT TOUCHED` from diagnostic. App still pinned exact detached PR32 SHA `532a28d99bd0548241854495156a61f94eb1ac6b` with sole protected untracked `AGENTS.md`. GitHub PR32 remains draft/open/unmerged. Earlier successful MAIN postmigration metadata, 6/6 SQL, four real Frappe execute reports and Guest/Admin gateway denials remain valid.

**NEXT operator action under previously approved DEV maintenance:** launch **one** DEV-only Honcho manager after rechecking NAS+local snapshot manifests, correct app pinned source + sole AGENTS, no existing active DEV managers/services or listeners and Procfile **exact known five definitions**. Use corrected validator which allows **only** exact `worker: bench worker 1>> logs/worker.log 2>> logs/worker.error.log`, not arbitrary shell redirection or other unreviewed commands; preserve existing Procfile. Use a new unique non-clobber bench log and `docker exec -d` inside the single named DEV container; postcheck one live manager; if anything fails, **never blindly retry**, inspect resulting state first. No broad Docker restarts, Git checkout, data mutations, process signals, PR merge or PRODUCTION action. Following startup, verify both DEV sites HTTP health and workers/scheduler in separate step.


## 2026-11-02 — Third DEV Honcho startup preflight stops at strict exact-two site inventory

**Owner's result from re-guarded DEVELOPMENT-only startup attempt with five exact verified Procfile commands:**
```text
SYNOLOGY RECOVERY MANIFESTS: PASS
PINNED SOURCE AND LOCAL BACKUPS: PASS
VERIFIED FIVE PROCFILE COMMANDS: PASS
WORKER LOG REDIRECTIONS: PASS
STOP: Unexpected DEVELOPMENT bench sites
DEVELOPMENT_START_EXIT_CODE=1
STOP: Inspect state before any further startup attempt
```
**Scope and interpretation:** The temporary startup script's Python preflight compared every directory under the DEV bench `sites/*/site_config.json` to an **exact** set containing only `development.localhost` and `ccpc-integration2.localhost`. The strict set-equality failed. This can indicate additional legitimate site configs, a missing named config, or another filesystem issue; do not infer any particular third site without an inventory. Earlier audits confirmed both named DEV site configs exist, so additional site(s) are plausible. The script exited **before** the `docker exec -d` Honcho launch, with no startup/migration/code or production operation from this attempt. NAS/local recovery manifest and pinned source+AGENTS, five Procfile commands and worker append redirection guards passed. No PR merge; GitHub confirms PR32 draft/open/unmerged at `532a28d99bd0548241854495156a61f94eb1ac6b`.

**NEXT safe step:** read-only exact DEVELOPMENT bench site_config inventory from the named DEV container, guard pinned app SHA and protected AGENTS, print site directory names and classify expected/extra, detect symlinks and anonymous distinct DB checks without printing credentials, DB names or contents; do not mutate files. **Before starting Honcho**, review whether any extra site is potentially PRODUCTION or otherwise a workload not authorized to restart, since a bench-wide scheduler/worker can operate on all configured sites and DEV and PROD may share host infrastructure. Do not merely relax the set to allow arbitrary sites, and do not rerun startup until scope is understood. If all extras are verified DEV-only, change the startup guard to check both approved sites are present and no production/unknown sites would be acted on. All previous migrations and MAIN reporting tests remain PASS; web/workers/scheduler still down as of last verified inspection.


## 2026-11-02 — Three DEV bench site configs found; third known broken integration site excluded from rollout

**Owner's read-only exact DEV bench inventory after third guarded Honcho preflight stop:**
```text
PINNED SOURCE: PASS
SITE CONFIGURATION COUNT: 3
EXPECTED SITES PRESENT: True
ADDITIONAL SITE COUNT: 1
SITE: ccpc-integration.localhost
CLASSIFICATION: ADDITIONAL - REVIEW REQUIRED
SITE DIRECTORY SYMLINK: False
CONFIGURATION SYMLINK: False
SITE: ccpc-integration2.localhost
CLASSIFICATION: EXPECTED DEVELOPMENT
SITE DIRECTORY SYMLINK: False
CONFIGURATION SYMLINK: False
SITE: development.localhost
CLASSIFICATION: EXPECTED DEVELOPMENT
SITE DIRECTORY SYMLINK: False
CONFIGURATION SYMLINK: False
SITE INVENTORY: COMPLETED
NO CONFIGURATION CONTENTS DISPLAYED
NO FILES OR DATABASES MODIFIED
NO SERVICES STARTED
PRODUCTION: NOT TOUCHED
SITE_INVENTORY_EXIT_CODE=0
```
**Important GitHub reconciliation:** Earlier authoritative `CURRENT-HANDOFF-3.md`, `DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md` and `PR32-DEVELOPMENT-READ-ONLY-PREFLIGHT-2026-10-29.md` explicitly call `ccpc-integration.localhost` a **known incomplete/failed/broken integration site excluded from the approved two-site migration/recovery scope**. Thus the third site is **not an unknown PRODUCTION site on existing documentary evidence**, but it is explicitly **not part of the tested/migrated rollout**, and its lingering `site_config.json` might still be enumerated by bench-wide scheduler/web workers on a Honcho start. Do not simply relax the startup guard and treat all three as valid; do not remove, rename, migrate, restore or alter the broken site without separate review/authorization. The strict exact-two check correctly stopped before launch and exposed this latent topology risk. HEAD still pinned `532a28d99bd0548241854495156a61f94eb1ac6b`, only protected `?? AGENTS.md`; NAS/local backups and five exact Procfile commands passed previously. Both approved DEV migrations, MAIN metadata, 6/6 raw SQL, all four native report `execute()`, and Guest/Admin gateway-denials PASS. DEVELOPMENT services remain down at last observed audit. PRODUCTION untouched; PR32 draft/open/unmerged.

**NEXT safe owner action:** one read-only targeted three-site configuration/scheduler-scope check inside named DEV container: compare database names for 3/3 distinctness **without printing names, secrets, or hostname**, inspect site-level `disable_scheduler` and `maintenance_mode` flags, and report whether the known broken site's config is complete or points to any approved DEV DB. Avoid contacting/writing the broken site DB, changing any files or starting services. Depending on evidence, review Frappe's actual bench-wide scheduler site-selection behavior before the next DEV Honcho start. Full launch requires explicit scoped decision to keep broken site inactive or otherwise safely isolate it; no unapproved changes to site configs or PRODUCTION.


## 2026-11-02 — Three DEV site configs distinct; broken excluded site's scheduler not disabled; hold Honcho startup

**Owner's read-only three-site config/scheduler-scope check output:**
```text
PINNED SOURCE: PASS
SITE CONFIGURATIONS: 3/3 PRESENT
ALL DATABASE NAMES CONFIGURED: True
ALL THREE DATABASE NAMES DISTINCT: True
TWO APPROVED DATABASES DISTINCT: True
COMMON DISABLE_SCHEDULER: NOT SET
SITE: development.localhost
DB CONFIGURED: True
DB HOST CONFIGURED: True
SITE DISABLE_SCHEDULER: NOT SET
SITE MAINTENANCE_MODE: NOT SET
SITE: ccpc-integration2.localhost
DB CONFIGURED: True
DB HOST CONFIGURED: True
SITE DISABLE_SCHEDULER: NOT SET
SITE MAINTENANCE_MODE: NOT SET
SITE: ccpc-integration.localhost
DB CONFIGURED: True
DB HOST CONFIGURED: True
SITE DISABLE_SCHEDULER: NOT SET
SITE MAINTENANCE_MODE: NOT SET
CONFIGURATION INSPECTION: COMPLETED
DATABASE CONNECTIONS: NONE
NO FILES OR DATABASES MODIFIED
NO SERVICES STARTED
PRODUCTION: NOT TOUCHED
SITE_SCOPE_CHECK_EXIT_CODE=0
```
**Interpretation:** all three site configs have separate configured database names and database hosts and no explicit site-level scheduler disable or maintenance settings, with no common disable_scheduler flag. The third `ccpc-integration.localhost` is a known incomplete/broken **DEVELOPMENT** site explicitly excluded from owner-approved two-site backup/migration/release testing per `CURRENT-HANDOFF-3.md` and controlled DEV plan. Distinct names rule out *configured aliasing between these three DB names*, not host-level or credentials isolation; they do not guarantee no scheduler activity. No Frappe DB was connected in this check; cannot infer enabled site scheduler from config alone, since database-held scheduler/maintenance state and installed framework code may affect behavior. Starting full bench-wide Honcho without identifying installed scheduler site enumeration could attempt work on broken third site. **Hold DEV startup until verified or explicit safe isolation decision.** Latest operator command was read-only, no server processes launched or PRODUCTION touched. Pinned PR32 `532a28d99bd0548241854495156a61f94eb1ac6b` remains draft/open/unmerged as independently rechecked on connected GitHub. Successful two-site migrations, MAIN metadata, 6/6 raw SQL, four native report `execute()`, Guest/Admin gateway denials unchanged.

**NEXT safe read-only operator action:** inspect the **installed** `apps/frappe` scheduler source around site enumeration, `bench schedule`, and disabled-site checks with bounded excerpts only, using exact DEV container/app source guard; inspect no credentials/DB contents, run no scheduler, Frappe session, migrations or startup. Determine whether shared `bench schedule` will include the broken third site by default. Review site isolation options before any configuration-write authorization; do not rename/delete site, set flags, change Procfile, or start Honcho without appropriate scope.


## 2026-11-02 — Installed Frappe scheduler discovery includes broken third integration site; full Honcho startup held

**Owner-run read-only source inspection of installed DEVELOPMENT Frappe code (exit=0):** `get_sites` traverses `os.listdir(sites_path)`, accepts directory not symlink and containing `site_config.json`, and appends each site. `enqueue_events_for_all_sites` calls `get_sites()`, loops over returned sites and calls `enqueue_events_for_site(site=site)`; that function performs `frappe.init(site)`, **`frappe.connect()`**, then `is_scheduler_inactive()` before enqueueing. `is_scheduler_inactive()` checks `maintenance_mode`, `pause_scheduler` and `is_scheduler_disabled()`; disable check reads `frappe.conf.disable_scheduler` and `System Settings.enable_scheduler`. All requested function and pattern checks found (source inspection: completed, no DB connections, no scheduler/Honcho start, no modifications, PRODUCTION not touched). The earlier three-site inventory found `ccpc-integration.localhost` as a **real non-symlink directory with site_config.json**; prior GitHub docs classify it as a known broken/incomplete integration site **excluded** from approved migrations. Three site configs reference distinct database names and no disable or maintenance flags are set. **Inference from installed source:** bench-wide `bench schedule` may try initial DB connection on excluded site even if scheduler is subsequently found inactive, so blindly starting full Honcho risks unintended interaction with broken site. Explicitly HOLD full DEV Honcho startup and do not delete/rename site or change config without separate review/approval. The two migrated intended DEV sites and all four MAIN reports remain PASS; PR32 pinned exact `532a28d99bd0548241854495156a61f94eb1ac6b`, draft/open/unmerged.

**Next read-only operator step:** inspect the installed CLI declaration of `bench schedule` (path `apps/frappe/frappe/commands/scheduler.py`) and the scheduler's site-specific options plus runtime `start_scheduler` loop (path `apps/frappe/frappe/utils/scheduler.py`) using small AST/source excerpts; do not start scheduler, connect to DB, change site files/Procfile or execute CLI with write effects. Determine if any actual `--site` selector truly constrains `get_sites()` for background scheduling. Public Frappe CLI documents `schedule` as **bench-wide**, while other scheduler management commands have per-site options; do not assume a generic `bench --site X` context constrains this scheduler. Based on evidence, propose DEV-only minimal safe isolation, or deliberate no-start pending scope confirmation. PRODUCTION untouched.
