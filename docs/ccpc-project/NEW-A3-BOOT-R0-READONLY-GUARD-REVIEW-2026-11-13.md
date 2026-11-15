# NEW A3 R0 boot-readiness audit — source/test review and operator safety gate

**Date:** 2026-11-13, Asia/Manila.
**State:** GitHub source prepared and independently tested only against **synthetic offline data**. **NOT STAGED OR EXECUTED ON NEW UBUNTU**. **NO STARTUP/RESTART POLICY MODIFICATIONS APPROVED.**
**Scope authorization:** Owner “aPPROVED continue” following the proposal to implement the **non-executing GitHub-only R0 audit and rollback plan**. Does not authorize a NEW-host deployment, changes to OLD PROD/DEV, updates to containers, service enablement, Docker state changes, reboot, migrations or employee production cutover.

## Exact reviewed source

- [Read-only R0 guard](../../scripts/ccpc_new_a3_boot_r0_readonly.py) — GitHub blob `a65b6c0907c0b28e390557b153d220ffd110c42b`, Python 3 stdlib only.
- [Offline synthetic test suite](../../tests/test_ccpc_new_a3_boot_r0_readonly.py) — GitHub blob `feabe9b32bea40f56a54ee5ee616933677a9bc04`, 21 tests.
- [G1 non-destructive boot-recovery design](NEW-A3-PRESERVATION-SAFE-BOOT-RECOVERY-DESIGN-2026-11-13.md).
- [Formal NEW A3 production readiness report](NEW-A3-FORMAL-PRODUCTION-READINESS-2026-11-13.md).

R0 is **read-only**. It deliberately contains **no** `--execute`, `docker update`, `docker start`/`stop`/`restart`, `docker compose up`, `systemctl enable`/`start`/`stop`, migration, backup/restore or SQL write operation. It inspects Docker metadata, systemd state, two fixed root-owned systemd unit text files and only the two effective site booleans `pause_scheduler`/`mute_emails`. It suppresses raw command stderr, avoids printing configuration/secrets and produces a small fixed PASS or generic STOP set. Reading JSON and launching a short `python3 -B` inside the pinned backend to examine site booleans can create transient process activity but intentionally does not change business data. No health HTTP probes or Redis PING are in R0 (those were separately performed live and passed).

**Important:** This is a **pre-change baseline guard**. It expects the six candidate restart policies to remain `no` and the active Caddy/relay socket to be boot-`disabled`; after an approved boot change the baseline must be intentionally revised and re-reviewed, not blindly reused. It detects drift, not a safe reboot or production readiness by itself.

## Guarded scope and validation

- Exactly **19 expected Docker containers total**, with immutable **64-character IDs** pinned in a separate root-only manifest: 12 running originals (six working NEW A3 and six Nov07 rehearsal support services), six running independent restored-test services, and the original failed isolated Stage3A backend deliberately preserved `Exited (1)`. Reject additions, missing names, ID substitutions and unexpected stops.
- Exact six candidate containers use one private **internal** network; network ID and membership must match the pinned manifest and exactly those six IDs. The three app containers must have the same pinned image digest and expected named sites/logs mounts; database and Redis-queue named volumes must persist. Candidate MariaDB must report Docker `healthy`. Candidate containers must have `RestartPolicy=no` and no host-published ports.
- Candidate frontend current IPv4 must be a private non-loopback address, exactly equal to the separately pinned manifest address and existing root-owned `ccpc-erpnext-upstream.service` `ExecStart` proxy target (port 8080); socket must listen exclusively on `127.0.0.1:8080`. Any drift fails closed.
- Docker and containerd must be active/enabled; Caddy active/disabled; upstream socket active/disabled; relay companion active/static. Site configuration booleans must have effective `pause_scheduler=true` and `mute_emails=true`. Other process types, external integrations, staff access, WAN/guest isolation, and business transactions are **not** tested by R0.
- Before even launching the site flag probe, the live collector checks all 19 pinned container identities, candidate backend image, its one private network and sites mount, and six-member network identity. No secrets, account identities, passwords, full JSON or certificate files are printed.
- The live mode demands sudo root on exactly `ccpcerp-prod` from `SUDO_USER=ccpcadmin`, with no `DOCKER_HOST` or `DOCKER_CONTEXT` environment overrides, and a manifest held in an absolute **root-owned regular file** with no group/other mode bits. The script will not generate the manifest, modify it or stage itself on the server.

## Manifest schema — for later authorized preparation ONLY

No production identities, image IDs, database credentials or manifest were committed to GitHub. The expected UTF-8 JSON structure is:

```json
{
  "schema": 1,
  "container_ids": {
    "<all 19 exact protected Docker container names>": "<unique complete 64-character lowercase hexadecimal container ID>"
  },
  "network_name": "<exact current candidate private Docker network name>",
  "network_id": "<exact complete 64-character lowercase hexadecimal network ID>",
  "frontend_ipv4": "<currently verified candidate frontend private IPv4>",
  "app_image_id": "sha256:<exact complete 64-character app image digest>"
}
```

This is an illustrative schema, **not** a valid manifest: exactly 19 keys must be present in `container_ids`, and none of the angle-bracket placeholders are usable. Acquire each from a guarded **read-only** Docker snapshot of the correct NEW host only after reviewing a separate, minimally scoped operator collection procedure. Do not publish the real manifest to GitHub or paste its protected filesystem path into chats; Docker IDs themselves are not passwords, but the owner-approved root-only operating baseline should stay on the host. **Never fabricate or infer IDs from container names.**

## Test evidence and limitations

- In a separate isolated Python workspace, placed **exact identical Git blobs** for the source and test suite under `scripts/` and `tests/` and ran:
  `python -B -m unittest discover -s tests -p 'test_ccpc_new_a3_boot_r0_readonly.py' -v`
- **21/21 synthetic tests PASS**, including baseline PASS and offline command-line PASS/STOP. Failure tests cover extra network member/container, changed container ID/frontend IP, stale relay target, published port, missing volume, app image drift, unpaused scheduler, unmuted email, missing failed test backend, stopped original rehearsal service, restart policy unexpectedly changed, unexpected Caddy enablement, missing/duplicate/malformed manifest IDs. CLI negative case returned only `CCPC_NEW_A3_R0_STOP_REVIEW_REQUIRED` and nonzero exit. No actual Docker or systemd service was accessed by the offline tests.
- GitHub source blob and tested local Git blob matched exactly: `a65b6c0907c0b28e390557b153d220ffd110c42b`; test blob matched exactly: `feabe9b32bea40f56a54ee5ee616933677a9bc04`. This confirms code bytes tested are what GitHub currently contains at this checkpoint. **Not a live host validation**; live collection's Docker/systemd behavior remains separately untested.
- A Python syntax compilation and module import test completed locally with no errors. The offline cases do **not** establish no time-of-check/time-of-use race, boot reproducibility, real network failover, credential/role correctness, power failure resilience, or production release status.

## Next controlled decision

1. Prepare and review a short **read-only** candidate identity capture procedure (no files or secrets printed), then separately approve creating a unique **root-only** manifest on NEW Ubuntu and staging the exact SHA-verified script into a new protected path for the first `--live-readonly` preflight. This writes only new operator-owned operational audit files and executes read-only inspections; it **does not** enable any boot service or modify any container.
2. Review the resulting R0 PASS/STOP before considering the separate **Stage R1/R2** boot configuration rollout. Require a precise operator approval, reversible actions, recovery fallback, and an independent future reboot test approval.

Until those are completed: **G1 NO-GO**, employee PRODUCTION cutover NO-GO, OLD PROD/DEV and all 19 existing NEW-host containers/volumes and backups remain protected. Consumed one-use Stage3A/3R/3S/3T and NAS backup executors **must never be rerun**.

## November 13 — OWNER APPROVED guarded root-only manifest capture and source staging (NOT YET executed)

- Following explicit operator **“Approved”** in response to the precise scope to create **one protected manifest**, stage the exact verified R0 source and run its first `--live-readonly` check on **NEW only**, prepared a separate **one-time** capture helper. Approval permits that narrow non-business operational file creation and read-only check, **not** any boot changes, service enablement, container policy update/restart, database restore/migration or employee cutover. No NEW-host action has yet been performed under this approval.
- Guarded helper: [`scripts/ccpc_new_a3_boot_r0_manifest_once.py`](../../scripts/ccpc_new_a3_boot_r0_manifest_once.py), Git blob `4d9eac17bb99f9285f58c331fd37c011d612561d`, local checked matching Git blob, SHA256 `2f0ddfd426b11831d03d05ef75b6ba7dc5999a7c81e42675319c1b14e12d9f73`. Imports exact existing R0 source and, from NEW host only as sudo from `ccpcadmin`, first validates all 19 expected container names/IDs and states; original protected sets running, exited failed drill backend retained; source app image pinned to `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`; DB healthy, internal six-member candidate network, no candidate host ports, frontend remains `172.20.0.7`. It calls complete existing R0 `snapshot_live`/`evaluate` for volumes, systemd boot-state, relay, scheduler and email booleans before writing **anything**.
- On full PASS only, the helper creates previously absent root-owned `/var/lib/ccpc-new-a3-r0-manifest-20261113` mode 0700 and exclusively creates `manifest.json` mode 0600; the file holds Docker IDs/image/network metadata **only**, no passwords, DB rows, site config or credentials. Fixed path is operator-only, not to be uploaded into GitHub. If directory/file exists, preflight differs, write fails/interrupts or STOP appears, **do not rerun, delete, chmod, overwrite or retry**; preserve any partial state for review. No writing to candidate named volumes or existing backups. Root staging of the two SHA-verified source files requires a separately reviewed exact no-overwrite copy procedure, not a random `curl | bash`.
- Synthetic test source: [`tests/test_ccpc_new_a3_boot_r0_manifest_once.py`](../../tests/test_ccpc_new_a3_boot_r0_manifest_once.py), Git blob `c05f2cbb6faf4662a55fcc0527d000ce0ce0bbe5`, exact locally tested Git blob, **17/17 Python unittest synthetic cases PASS**. The helper's 17 synthetic cases mock Docker data and the full R0 snapshot/evaluate outcomes while exercising manifest construction/denial and root-only exclusive file writing under temporary directories. A later second execution imported the **exact genuine GitHub R0 module** rather than an R0 stub: **38/38 combined R0 + helper offline Python unittest cases PASS**. Source Git blobs independently matched GitHub and local test copies. The full R0 live Docker/systemd collector remains **unverified on NEW**; synthetic tests are not actual reboot/integration proof. The original exact R0 guard separately had **21/21 synthetic/offline PASS**. Both source and helper syntax compile cleanly; no new online CI spend/trigger or live change performed.
- For Windows pinned source download, immutable GitHub commit `72aac798a229610d5bc2c297026be6dba87eee0a` includes both code files. Exact built-in SHA256 expected: R0 `3f4e03d0e5f5d55bacfd16492fb021045eeb06b0199577a1612c9f18e0a3d72b`, helper `2f0ddfd426b11831d03d05ef75b6ba7dc5999a7c81e42675319c1b14e12d9f73`; user to verify **before** SCP. Do not supply files from a moving branch head without exact hashes. Windows download alone does not authorize host execution; after Windows download check, review remote safe staging and then manifest capture in distinct small steps.
- Next operator action: **Windows PowerShell only**, download both source files from exact immutable GitHub commit into a previously absent uniquely named Downloads subdirectory, verify SHA256 using Windows built-ins and print sanitized PASS. Do not paste raw code, backup/config files or credentials into chat. On STOP, preserve state without blindly rerunning. This is local-only preparation, no NEW/OLD host changes. On PASS, prepare a protected SCP + no-overwrite root staging step, then one-time manifest creation and `--live-readonly` guard test; each operator result recorded before the next step.

- An optional transfer-only ZIP was assembled locally from the two *exact* verified GitHub Python source blobs (no credentials or JSON identity manifest), plus a plain-text checksum note; archive SHA256 `59ac0cad5923d0abcd84af00a5d1d8f4252981b084182ce74963593615f06230`, 7,346 bytes, internal ZIP read-back and both source SHA256 checks PASS. Archive file is a chat-delivered convenience copy **not a GitHub commit or NEW-host installation**. Once downloaded, verify archive SHA256 before extraction; any mismatch is STOP with no retry/execute. Root-owned source staging and one-time manifest execution remain separate operator steps under the narrow existing approval.

## November 15, 2026 — R0 two-script transfer and NEW-host SHA256 verification PASS

- Operator reported Windows ZIP `CCPC_R0_SOURCE_ARCHIVE_SHA256_PASS`, extracted sources `CCPC_R0_TWO_SCRIPTS_SHA256_PASS` (both code SHA256 verified), private NEW-host transfer directory `/home/ccpcadmin/ccpc-new-a3-r0-transfer-20261115` created with `CCPC_NEW_A3_R0_TRANSFER_FOLDER_CREATED_PASS`, and SCP transfer via existing authorized `ccpcerp_prod_ed25519` SSH key finished 100% for both scripts. Initial plain SSH default-key auth denial resolved by using already-established SSH key procedure; **no SSH security policy changes**.
- On the actual NEW Ubuntu shell `ccpcadmin@ccpcerp-prod`, operator then ran guarded read-only server-side SHA256 check and reported **exact**:

```text
R0_READONLY_SCRIPT_SHA256_PASS
R0_MANIFEST_SCRIPT_SHA256_PASS
CCPC_NEW_A3_R0_TRANSFER_VERIFICATION_COMPLETE
```

- Both transferred files were reported to match reviewed GitHub code source hashes: R0 `3f4e03d0e5f5d55bacfd16492fb021045eeb06b0199577a1612c9f18e0a3d72b` and once-only helper `2f0ddfd426b11831d03d05ef75b6ba7dc5999a7c81e42675319c1b14e12d9f73`. Verified files are presently **only** inside the owner's private transfer directory; neither script was run, no root-only manifest has been created, and no Docker/ERPNext/systemd/DB or business data changes are reported. Current boot/recovery G1 **BLOCKED**, overall PRODUCTION **NO-GO**.
- **Next exact operator-only step under existing narrow approval:** root-stage both previously SHA-verified Python files into a unique previously absent root-only directory with mode0700 and files mode0600, rejecting any pre-existing destination and aborting on SHA mismatch. This is new operator-owned file creation only; do not execute either script in this step. Stop and preserve state on unexpected file ownership, existing path, or checksum mismatch; do not overwrite, delete or rerun blindly. Then separately verify staged SHA256 and execute a single guarded once-only capture + R0 check only after reviewing the first step.

## November 15, 2026 — Root-only R0 source staging operator PASS

- Operator confirmed exact status `CCPC_NEW_A3_R0_ROOT_STAGING_VERIFIED_PASS` after completing an owner-approved guarded `sudo bash` on `ccpcadmin@ccpcerp-prod`: existing private transfer files rechecked against SHA256, **previously absent** `/root/ccpc-new-a3-r0-20261115` created mode 0700, both source Python scripts copied mode 0600 and on-host checksums rechecked. Neither script was executed at this stage, and the protected one-use R0 identity manifest under `/var/lib/ccpc-new-a3-r0-manifest-20261113/manifest.json` has not yet been reported created. No Docker, service, DB, ERPNext site or OLD PROD/DEV changes authorized/reported.
- Source unchanged: guard SHA256 `3f4e03d0e5f5d55bacfd16492fb021045eeb06b0199577a1612c9f18e0a3d72b` Git blob `a65b6c0907c0b28e390557b153d220ffd110c42b`; one-time capture helper SHA256 `2f0ddfd426b11831d03d05ef75b6ba7dc5999a7c81e42675319c1b14e12d9f73` Git blob `4d9eac17bb99f9285f58c331fd37c011d612561d`; existing draft PR #35 open, unmerged.
- **Next single operator step under existing narrow owner approval:** use `sudo python3 -B` to invoke only the SHA-verified fixed `/root/ccpc-new-a3-r0-20261115/ccpc_new_a3_boot_r0_manifest_once.py --capture-once` with a wrapper that reasserts exact host, caller, staging dir/files owner/mode, both source SHA256 hashes, and destination path absence. The helper independently verifies **all 19 exact protected containers and statuses, pinned A3 app image, internal network and original six, fixed frontend IP, root-owned relay/systemd state, volumes, scheduler paused/email muted BEFORE creating new root-only manifest**. On any `STOP` do not rerun, delete or repair state without separate review. This command does not change Docker container/service policies or production business data, and root-only manifest is not to be pasted into chat or committed to GitHub. Once capture passes, verify R0 with a separate read-only command.

## November 15, 2026 — NEW A3 guarded one-time R0 manifest capture operator PASS

- Owner ran the separately authorized once-only guarded root staging/identity capture from NEW shell as `ccpcadmin`, reporting the script's exact successful markers:

```text
CCPC_NEW_A3_R0_CAPTURE_PREFLIGHT_PASS
CCPC_NEW_A3_R0_IDENTITY_CAPTURE_VERIFIED_PASS
CCPC_NEW_A3_R0_ROOT_ONLY_MANIFEST_CREATED_PASS
```

- A stray **garbled terminal/paste fragment** appeared before the success markers (`ROOT--capture-once...`); it was not treated as a verification result. The two source scripts had previously passed NEW Ubuntu SHA256 verification and protected root-only staging. The capture helper is designed to perform full `snapshot_live` + `evaluate` validation **before** creating a protected metadata-only manifest. Based on the reported markers, the one-time manifest **appears successfully created** in protected root-owned `/var/lib/ccpc-new-a3-r0-manifest-20261113/manifest.json` (mode0600 inside mode0700 folder). Do not display/paste this JSON, upload to GitHub, overwrite, delete, re-create or rerun the capture. No Docker/systemd changes or business data writes are authorized or reported.
- **Next one read-only independent verification:** on NEW via exact `ccpcadmin` sudo, assert root-owned mode0700 manifest directory and root-owned mode0600 regular non-symlink JSON, root-owned 0700 staged scripts directory and 0600 guard source, re-verify guard SHA256 `3f4e03d0e5f5d55bacfd16492fb021045eeb06b0199577a1612c9f18e0a3d72b`, then run only existing `ccpc_new_a3_boot_r0_readonly.py --manifest /var/lib/ccpc-new-a3-r0-manifest-20261113/manifest.json --live-readonly` with `python3 -B`. No printer of raw JSON or Docker inspect. This comparison checks current live 19 pinned container IDs/volumes/network/relay/systemd/paused/muted flags against saved manifest. Any STOP/exception: do not retry/restore/modify; review. **G1 still BLOCKED; overall PRODUCTION remains NO-GO**, no boot policy, Caddy/socket enablement, restart, reboot or staff cutover authorized.

## November 15, 2026 — R0 first independent live read-only verification PASS (owner reported)

- Owner completed separate, safeguarded **read-only** `sudo python3 -B` R0 check against the root-owned, once-captured `/var/lib/ccpc-new-a3-r0-manifest-20261113/manifest.json` on NEW `ccpcadmin@ccpcerp-prod`. Full reported result:

```text
CCPC_NEW_A3_R0_PROTECTED_FILES_PASS
CCPC_NEW_A3_R0_IDENTITY_STORAGE_NETWORK_PASS
CCPC_NEW_A3_R0_GATEWAY_AND_PRECUTOVER_FLAGS_PASS
CCPC_NEW_A3_R0_READONLY_PREFLIGHT_PASS
```

- A terminal paste/display fragment `ROOT--live-readonlynifest" \\ED_FILES_PASS"` preceded the result and is **not interpreted as an extra command or a validation marker**. The guarded wrapper verified staged R0 source SHA256, root-owned mode0700 staging folder, mode0600 script, root-owned mode0700 manifest folder, mode0600 regular manifest; original guard checks pinned **19 existing protected container IDs** and service states, image/site/log/DB/Redis-queue persistent volumes, exact six candidate network members/private fixed frontend IP/loopback relay, candidate no-published-port and 6/6 RestartPolicy=no, systemd states, and pause_scheduler/mute_emails flags. The success markers indicate all of those checks passed **at the time of this verification**. Neither script performs a Docker update/restart/enable, writes business records, or changes existing environment services.
- **Milestone complete:** approved Stage **R0** source verification, one-time NEW root-only manifest creation and first independent live read-only preflight **PASS**, alongside 38/38 combined offline synthetic tests. User did not report command exit status separately; R0 prints PASS only after evaluate success and returns 0. Do **not** rerun once-only capture, print/copy manifest contents or place them in GitHub. Immutable manifest is a pre-change baseline: any future authorized RestartPolicy or Caddy/socket enabled-state changes will cause **expected R0 baseline STOP** until a separately reviewed post-change baseline is prepared; never bypass a STOP or relax checks blindly.
- **Remaining G1 BLOCKER:** Docker itself active/enabled, but six candidate containers have `RestartPolicy=no` and Caddy and upstream socket are active/disabled; the operator has **not** authorized any boot configuration change/reboot. A successful R0 audit proves current identities, safety flags, state and liveness-at-baseline **only**, not automatic recovery after power loss. Next work is GitHub-only command-level G1 review of the chosen preservation-safe restart-owner/boot-gate plan and rollback with the exact pinned existing IDs read on host (never publish real manifest to GitHub), then request separate, narrowly scoped owner consent before any live mutation. Do not enable scheduler/emails, migrate, reopen WAN/guest, rerun consumed backup/restore executors or make employee cutover. **Overall production NO-GO** pending G1–G7.
