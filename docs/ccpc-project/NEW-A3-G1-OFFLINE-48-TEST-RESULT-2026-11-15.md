# NEW A3 G1 — Isolated offline test result (48/48 PASS)

**Date:** 2026-11-15 (Asia/Manila). **User authorization:** “Approved” to run the 48 pending G1 offline test methods in an isolated test environment, after the full suite had not yet been executed. **This is an offline/mock test result, not a CI service run, database integration, NEW Ubuntu boot, Docker policy change, or production authorization.**

## Authoritative GitHub snapshot

Verified [Draft PR #35](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/35) was open, unmerged and pointed to head `df1b4f9ef04310776a03200b3eaf463bdc6ea5a1` on branch `review/new-a3-production-readiness-2026-11-13` before running the tests. Exactly these GitHub source/test files were reassembled into an isolated local test tree and checked using `git hash-object` against current GitHub Git blob IDs **before executing**:

| Exact GitHub file | Verified Git blob SHA |
| --- | --- |
| `scripts/ccpc_new_a3_g1_boot_gate.py` | `83e438c6ade07790d1b2a967923bc3abfc9e68bd` |
| `scripts/ccpc_new_a3_g1_safety.py` | `ffa02cec1eb478be6693b7b65929a06a846d517f` |
| `scripts/ccpc_new_a3_g1_policy_plan.py` | `5adfa048a82539df7f9945c3d162f4c89e84fb33` |
| `scripts/ccpc-new-a3-g1-boot-gate.service` | `826762847101af35b83d6c708c1808ea82b6b422` |
| `tests/test_ccpc_new_a3_g1_boot_gate.py` | `e1013817ba357afb5904e96125137c565c8ce1b5` |
| `tests/test_ccpc_new_a3_g1_gate_flow.py` | `2cffcc3b75cc528095acf46d1f1e5c08a224bc55` |
| `tests/test_ccpc_new_a3_g1_safety.py` | `acc9d34a922259623b049ad39bfb42407987d824` |
| `tests/test_ccpc_new_a3_g1_policy_plan.py` | `2e5d9f6b28170cd8ce110ef281b632e1b5c75045` |

The immutable R0 guard remained unchanged in the GitHub review branch: `scripts/ccpc_new_a3_boot_r0_readonly.py`, Git blob `a65b6c0907c0b28e390557b153d220ffd110c42b`. The existing source activates only if `G1_ACTIVATION_REVIEWED` is explicitly changed; this remains hardcoded `False`. The tests mock R0, Docker and systemd, and do not read a NEW-host manifest.

## Execution evidence

**Environment:** local isolated container, Python **3.13.5**, git **2.47.3**; test modules and Python standard library only. This is *not* a GitHub-hosted or CircleCI runner. No network connection to NEW/OLD PROD or DEV; no real Docker/systemd calls.

Command executed from an isolated `scripts/` + `tests/` tree:

```bash
python3 -B -m unittest discover -s tests -p 'test_ccpc_new_a3_g1_*.py' -v
```

| Suite | Methods run | Result |
| --- | ---: | --- |
| `test_ccpc_new_a3_g1_boot_gate.py` | 12 | PASS |
| `test_ccpc_new_a3_g1_gate_flow.py` | 7 | PASS |
| `test_ccpc_new_a3_g1_safety.py` | 15 | PASS |
| `test_ccpc_new_a3_g1_policy_plan.py` | 14 | PASS |
| **Total** | **48** | **PASS** |

Verbatim unittest summary:

```text
----------------------------------------------------------------------
Ran 48 tests in 0.074s

OK
```

The runner actually executed the complete revised set, including failure paths that test G1's activation interlock, no gateway start on config/listener failures, bounded subprocess deadline handling, exact identities and rollback-intent safety. These are synthetic checks **only**. They do not prove real backend/worker data integrity, restart resilience, Caddy live runtime trust or WAN/guest isolation.

## Separately unresolved external CI

A previous test-only GitHub Actions workflow run [43677160450](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/43677160450) reported `completed/failure` with job runner ID `0` and no job steps. Logs were unavailable. No Python test actually executed in that external run; failure origin was not established. The workflow was subsequently changed to `workflow_dispatch` only to prevent repeated automatic attempts. **Do not call this report a GitHub Actions/CircleCI PASS.** Existing project CircleCI configuration was not used in this execution.

## Next safety boundary

This offline milestone is **COMPLETE**. Keep Draft PR #35 unmerged, `G1_ACTIVATION_REVIEWED = False`, and original R0 manifest/19 protected containers unchanged. **P0 remains**: verify deployed backend process/entrypoint and queued-job/outbound write risks before adopting `unless-stopped`; verify full effective systemd/Caddy TLS and restricted network graph; implement and test identity-checked real policy executor/compensation separately if approved; then explicitly approve each NEW staging, policy change and a future supervised reboot.

**G1 BLOCKED. Employee production cutover NO-GO.**
