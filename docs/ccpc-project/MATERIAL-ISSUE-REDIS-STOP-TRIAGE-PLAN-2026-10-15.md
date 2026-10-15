# CCPC ERPNext — Redis preflight STOP triage plan

**2026-10-15 | GitHub-only source review; NOT approval to run anything on Ubuntu.**

## Owner-approved DEVELOPMENT metadata check: PASS — 2026-10-15

The owner gave **separate, explicit approval** for one metadata-only read-only check of the three DEVELOPMENT site configuration paths, distinct from the previously consumed Redis preflight. The assistant provided a single Docker inspect identity gate followed by one `docker exec --user frappe` using `/bin/sh`. The check used only filesystem-type tests (`-L`, `-d`, `-f`, `-r`) and printed coarse labels. The operator reported the **complete** output:

```text
COMMON: PRESENT AND READABLE
ISOLATED: PRESENT AND READABLE
SHARED: PRESENT AND READABLE
METADATA-ONLY FILE CHECK: COMPLETED
READ-ONLY DEVELOPMENT INSPECTION: PASSED
```

This reports that the named running DEVELOPMENT Compose identity matched and that, **at inspection time**, the specified `sites` parent directory and three known common/test/shared configuration paths passed the script's nonsymlink, regular-file and readability tests as user `frappe`. No config JSON contents, Redis URLs, secrets, environment or database values were read or printed. This is **operator-reported**, not independently observed host access by ChatGPT, and it proves only the metadata predicate exercised by the check; it does not independently establish that an actual file-content open or JSON parse succeeds.

**Resolved narrow question:** basic file absence, symlink and observed mode/readability failures are not indicated by this new check. **Still unknown:** original Redis STOP cause; JSON parse errors, Redis URL and Sentinel configuration, effective Frappe overrides, actual overlap, DNS/services/worker/socketio/pubsub physical separation and Redis transaction effects. The old Redis preflight remains **unclassified STOP** and its permission is consumed; do not rerun it.

**Next owner-controlled gate:** Seek any retained earlier original STOP terminal lines if accessible without reexecution, omitting sensitive data. If unavailable, design a separate, credential-redacting, bounded configuration shape/parser check on the GitHub review branch with offline adversarial tests before any fresh, explicitly approved staging and distinct one-time execution. It should never print raw URL hostnames/ports or credentials and should not claim that configuration-only no-overlap proves runtime isolation. Avoid ad hoc repeated site probes without a reviewed procedure.

**Approval for this metadata check is consumed.** No further Docker/site reads or writes, Redis connections, Frappe initialization, app pulls, rollback rehearsal, permanent Material Issue posting or PRODUCTION operation are authorized. **Stock Entry/SLE/GL COMMIT: NO-GO.**

## Verified record

- Verified source before this documentation update: deployment review branch `review/material-issue-first-commit-preparation-2026-10-15` at commit `6a10a80f9e4496f3e1112c11b738bcde375440f5`; the reviewed Redis script blob and staged SHA256 below remain unchanged. Do not treat that historical tip as the new live branch HEAD.
- Original guarded Redis candidate blob `85123cd4d487110d01cdc375ad7e6969035bdc34`, staged SHA256 `837dcdee993f1fb8d9187dde473070c8b137254664d0d270b7b7d0fa21c35202`. Its approval is consumed: do not rerun or restage it.
- Only the final original wrapper result was provided: `ONE-SHOT READ-ONLY PREFLIGHT: STOPPED OR FAILED`. No preceding output or specific internal STOP category was provided.
- The subsequent VS Code terminal exit code 127 was *not definitively linked* to the original preflight. The user later reported copying example expected-output labels as shell commands on a separate attempt. Do not use the terminal closure to diagnose Redis.
- Source review identified a flaw in the original assistant execution *wrapper*: `set -e` within an `if ( ... )` subshell does not reliably prevent later commands after intermediate failures. This does not establish any defect in the vetted inner Redis script.
- Separately approved operator-reported host diagnostics verified the staged file checksum, Bash syntax and ownership; Docker CLI; running DEVELOPMENT container identity; the bench directory, Python interpreter startup and a harmless `docker exec -i` Python standard-input test. These establish transport and basic access, not what happened during the earlier preflight.

## Source-level STOP categories, not runtime findings

1. Outer shell guard, Docker inspect identity or container exec failure before Python enters the classifier.
2. Sanitized Python STOP: absent/unreadable/nonregular/symlinked site configuration, invalid JSON/URL, unsupported Sentinel mode, or other parsing problem. Exceptions are intentionally not echoed because they may contain secrets.
3. Explicit `REDIS CONFIGURATION ENDPOINT OVERLAP: DETECTED; STOP`, covering isolated cache/queue or isolated/shared endpoint equality (including known loopback aliases).
4. Configuration-only no-exact-overlap. Even this does **not** prove physical Redis, workers, Socket.IO, DNS, proxies, or pubsub isolation and does not authorize posting.

**These categories cannot be distinguished from the last wrapper line alone.** Ask first for earlier lines from that same original terminal run if available, without requesting raw credentials, JSON, Redis URLs, environment dumps, unfiltered history or unrelated logs.

## One future separate metadata-only diagnostic — PROPOSED, NOT AUTHORIZED

If the earlier lines cannot be recovered, seek explicit fresh consent for **one** independent read-only DEVELOPMENT container entry, not a replay of the consumed Redis script. Scope:

- Verify the named `frappe_docker_devcontainer-frappe-1` is still running with the exact expected Compose project/service labels before entering as `frappe`; otherwise STOP.
- Check only whether `/workspace/development/frappe-bench/sites` is a real directory and whether the three expected config paths (`common_site_config.json`, `ccpc-integration2.localhost/site_config.json`, `development.localhost/site_config.json`) have nonsymlink parents and are readable regular files.
- Report only coarse status labels `COMMON`, `ISOLATED`, `SHARED`: `PRESENT AND READABLE`, `MISSING OR UNREADABLE`, or `SYMLINK STOP`. Never print contents, endpoints, ports, env values, secrets, file names from an uncontrolled source, or exception traces.
- Do **not** open config files, parse JSON, initialize Frappe, call Redis/SQL/network, run any earlier script, change a file, manage containers, or access PRODUCTION. Stop without retry on unexpected conditions.
- A planned shell implementation was syntax-checked locally with `bash -n` and embedded `sh -n` only; it was neither staged nor executed on Ubuntu. It has not been submitted for owner runtime approval.

This metadata-only result may rule out path/permission problems but cannot identify a Redis overlap, prove isolation or establish what ran during the original STOP. Evaluate new evidence before requesting a different independently approved diagnostic. Avoid `if (set -e ... )` as a security gate; use explicit conditionals and a single clearly labeled copyable code block for operator instructions.

## Boundaries

The original read-only preflight and subsequent one-shot checks have consumed their authorizations. No additional Ubuntu/DEVELOPMENT activity is approved by `Continue`. The application posting candidate and inert review-only guard are untouched. **Persistent Material Issue Stock Entry/SLE/GL: NO-GO; Redis physical/worker/pubsub isolation unverified; PRODUCTION excluded.**
