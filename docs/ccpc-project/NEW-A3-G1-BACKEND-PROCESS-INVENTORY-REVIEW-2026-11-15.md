# NEW A3 G1 — Pinned backend process inventory, review only

**Date:** 2026-11-15 Asia/Manila. **Status:** GitHub-reviewed source and isolated synthetic tests, followed by one owner-authorized, one-time, read-only NEW-host process inspection, **operator-reported PASS**. This is not independent host verification or a backend write-safety certification. Draft PR #35 remains unmerged, G1 activation interlock remains `False`, and employee PRODUCTION cutover is **NO-GO**.

## Why this check

Prior 48/48 complete G1 gate tests passed offline with mocked Docker/systemd. That does not establish whether the deployed NEW backend will run embedded queue workers, schedulers, custom startup handlers or business-write integrations when Docker recovers it after a host reboot. Generic `compose.yaml` declares separate worker/scheduler services; owner-reported NEW six-candidate Docker identity and paused scheduler flags do not prove absence of embedded, delayed, or external consumers.

## New source contract (not an operator runbook)

- Script: [`scripts/ccpc_new_a3_g1_backend_process_readonly.py`](../../scripts/ccpc_new_a3_g1_backend_process_readonly.py). It is **not an installer, executor of writes, or business-safety certifier**.
- Requires root invoked by approved `ccpcadmin` via sudo on hostname `ccpcerp-prod` with no Docker remote/context environment overrides.
- Reads (never prints or modifies) the pre-existing 0700/0600 root-only R0 manifest. Fails closed unless all 19 expected Docker names, full pinned 19 IDs, current running/exited identity pattern and `RestartPolicy=no` still match; pins backend image ID and its single network membership.
- Uses only bounded `docker --host unix:///var/run/docker.sock ps -a`, `container inspect`, and `top <full pinned container ID> -eo pid,ppid,comm,args` on **six** current candidates. It rechecks 19 IDs/policies after inspection. **No `docker exec`, Frappe import, Redis key operation, SQL, queue read, process signal, service start, restart-policy update or host file write.**
- Raw entrypoints/argv are classified only in memory; standard output is restricted to fixed markers, bounded integer counts, and YES/NO signature indicators. No raw process commands, IDs, environment, secrets, job arguments, site configs, passwords, or business records are printed.
- Counts *recognizable* `bench worker`, `rq worker`, `celery worker`, `bench schedule`, and related command signatures. These are **positive detections only**: a count of zero must **never** be interpreted as proof of no asynchronous work, no embedded Python job, no external consumer, no migrations or no duplicate writes.
- It intentionally prints `QUEUE_CONTENTS_NOT_INSPECTED=YES` and `EXTERNAL_CONSUMERS_NOT_INSPECTED=YES`; pending Redis jobs/retries, other network consumers, outbound integrations, effective site code and OLD/NEW single-writer safety remain **unverified**.
- On any mismatch, output is one sanitized `CCPC_NEW_A3_G1_PROCESS_STOP_REVIEW_REQUIRED` marker and nonzero exit. No automatic retries, restoration, service activation or compensating action.

## Validation and safety limitations

- New synthetic suite: [`tests/test_ccpc_new_a3_g1_backend_process_readonly.py`](../../tests/test_ccpc_new_a3_g1_backend_process_readonly.py); **15/15 PASS** in isolated local Python 3.13.5 mock context on exact local files. Tests include worker/scheduler positive detection, non-leakage of an injected secret token, missing/malformed top, wrong host/sudo/root, Docker override, duplicate IDs, unexpected container, policy drift, accidentally started drill backend, and startup command risk signature. **No Docker daemon or NEW/OLD/DEV runtime accessed.**
- Existing independently completed G1 offline suite remains **48/48 PASS**; new test suite is separate and does not claim a 63-test combined execution.
- NEW-host `docker top` and Docker inspector responses returned the script's PASS markers during the one authorized operator-run. We have only the operator-supplied sanitized stdout, not independent host access or raw process tables. The source was SHA256-verified on NEW before execution; do not infer exact source-to-image mapping or hidden process behavior.
- A genuine go/no-go for backend auto-recovery needs **more than this inventory**: reviewed queue-length-only inspection with no job payloads, process/external-consumer ownership, deployed image-to-source mapping, startup hooks/integration effects, single-writer OLD/NEW guard, replay/duplicate GL-stock-purchasing prevention and a separately approved failure-path test. Do not enable candidate `unless-stopped` policies, G1 unit, Caddy/socket auto-boot, restart, reboot or employee cutover based on this read-only inventory.

## Next decision

The one-time process inspection is complete; **do not rerun it automatically**. Next prepare (GitHub-only) an independently reviewed **metadata/counts-only Redis queue inspection**, without queue payloads, keys, credentials or writes, plus external consumer and deployed-image source mapping. Obtain separate specific approval before another NEW-host execution. Do not activate G1, change restart policies, restart/reboot, or cut over users.


## 2026-11-15 — one-time authorized NEW-host execution record (operator-reported)

- Branch/head independently rechecked through GitHub PR #35: `review/new-a3-production-readiness-2026-11-13`, commit `0c4d60c2b0117d30e581404ee86d45003651572a`. Script Git blob `0bbebf66f35be2be0d761850d863f433bb92afb6`; pinned UTF-8 SHA256 `a1c5c28ba500965699af76d9cecb4a1b8c041b67cebd2c0e97491c630769353a`.
- Initial NEW-host SSH-to-GitHub staging **STOPPED**: `Permission denied (publickey)`. No relaxation of host-key checks or server credential changes. A Windows-to-NEW SCP using the operator's existing SSH key then reported the full 8,751-byte file transferred, not executed. On NEW, operator reported `CCPC_NEW_A3_G1_PROCESS_SCRIPT_VERIFIED_PASS` and `CCPC_NEW_A3_G1_PROCESS_NOT_EXECUTED` after SHA256 and permission verification.
- Operator then ran the reviewed inspector exactly once with sudo on NEW and returned the following bounded stdout; this output is evidence supplied by the operator, **not** an independent connector-host result:

```text
CCPC_NEW_A3_G1_BACKEND_PROCESS_IDENTITIES_19_PASS
CCPC_NEW_A3_G1_CANDIDATE_PROCESS_TABLES_6_PASS
CCPC_NEW_A3_G1_BACKEND_PROCESS_COUNT=3
CCPC_NEW_A3_G1_CANDIDATE_WORKER_SIGNATURE_COUNT=0
CCPC_NEW_A3_G1_CANDIDATE_SCHEDULER_SIGNATURE_COUNT=0
CCPC_NEW_A3_G1_START_COMMAND_WORKER_SIGNATURE=NO
CCPC_NEW_A3_G1_START_COMMAND_SCHEDULER_SIGNATURE=NO
CCPC_NEW_A3_G1_QUEUE_CONTENTS_NOT_INSPECTED=YES
CCPC_NEW_A3_G1_EXTERNAL_CONSUMERS_NOT_INSPECTED=YES
CCPC_NEW_A3_G1_PROCESS_READONLY_INVENTORY_COMPLETE
```

- **Interpretation:** pinned 19 identities/policies and six process tables matched; backend had three processes; no *recognized* worker/scheduler process or startup signatures detected. This is a **limited live metadata observation only**; opaque embedded executors, future jobs, Redis backlog/retries, external queue consumers, hooks and OLD/NEW single-writer risks remain unresolved. No restart, reboot, migration, business write, policy change or G1 enablement was authorized or reported.
