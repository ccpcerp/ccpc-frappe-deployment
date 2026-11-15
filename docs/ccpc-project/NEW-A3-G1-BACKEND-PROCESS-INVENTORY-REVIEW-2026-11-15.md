# NEW A3 G1 — Pinned backend process inventory, review only

**Date:** 2026-11-15 Asia/Manila. **Status:** GitHub-only reviewed source + isolated synthetic tests. **No NEW-host execution or approval to install/run this script.** Draft PR #35 remains unmerged, G1 activation interlock remains `False`, and employee PRODUCTION cutover is **NO-GO**.

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
- Real Docker-top formatting/daemon behavior and the running NEW image remain unverified until a separately reviewed, owner-authorized one-shot read-only NEW-host execution. The first live run should use a SHA256-pinned source downloaded through the existing manual GitHub-to-Ubuntu staging process, without copying the protected manifest or raw process output to chat.
- A genuine go/no-go for backend auto-recovery needs **more than this inventory**: reviewed queue-length-only inspection with no job payloads, process/external-consumer ownership, deployed image-to-source mapping, startup hooks/integration effects, single-writer OLD/NEW guard, replay/duplicate GL-stock-purchasing prevention and a separately approved failure-path test. Do not enable candidate `unless-stopped` policies, G1 unit, Caddy/socket auto-boot, restart, reboot or employee cutover based on this read-only inventory.

## Next decision

Review this source and its 15 tests against the PR #35 branch, then separately authorize exactly **one** NEW-only read-only inspection under the existing pinned-source manual delivery procedure. There is no automatic execution in GitHub; do not install, execute or stage anything on NEW/OLD/DEV without that separately reviewed operator step.
