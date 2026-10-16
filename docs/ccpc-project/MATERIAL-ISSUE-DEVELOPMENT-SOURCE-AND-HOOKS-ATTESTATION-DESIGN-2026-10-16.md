# CCPC ERPNext — DEVELOPMENT installed-source and effective-hook attestation: security design

**2026-10-16 | GITHUB-ONLY DESIGN | No operator command/script is authorized | No DEV/PROD runtime/site/config/Redis/SQL read | POSTING_NO_GO**

## 1. Goal and non-goals

The owner approved **designing**, not implementing or executing, a narrowly scoped method for identifying which Frappe, ERPNext and CCPC app versions and which hooks **DEVELOPMENT** actually uses, while honoring the project policy that DEVELOPMENT and PRODUCTION may share an Ubuntu host and Docker daemon.

The proposed attestation should eventually distinguish:
1. **Expected GitHub state:** reviewed repository refs, source hashes and expected registered hooks.
2. **Installed-at-rest DEVELOPMENT state:** exact package/source revisions and deviations from committed code *within an independently trusted DEV-only filesystem scope*.
3. **Effective site-specific hook configuration:** which custom hooks, enabled Notification/Webhook/Server Script records and other applicable extension mechanisms are active for the identified DEV site.
4. **Loaded-runtime state (separate and harder):** what a particular already-running DEV process actually imported/cached, including whether that state predates installed files, site configuration changes, or restarts.

**No single Git command, site config file, Docker label, process name, IP, hostname, cache value, or Python helper executed in a new child proves all four.** In particular, an installed Git HEAD is **not** the live code identity of a long-lived worker/Node process.

**Not in scope here:** Redis endpoint or instance proof; PRODUCTION inventory or metadata; network namespace examination; reads of worker queues, submitted Stock Entries, GL or SLE; changing app code or DB; cache clearing; pub/sub; notification deliveries; service restarts; Docker exec; staging; cron; migrations; transaction trials; or deployment.

## 2. GitHub source basis

- [GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) and [current handoff](CURRENT-HANDOFF.md).
- [Stock Ledger / repost / GL audit](MATERIAL-ISSUE-STOCK-LEDGER-REPOST-GL-REACHABILITY-AUDIT-2026-10-16.md), CCPC app pin `ccpcerp/ccpcerp@2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`, historical ERPNext review pin `frappe/erpnext@5af6561f5aa48104559692fb4fd82f2580e8d338`, and historical Frappe review pin `frappe/frappe@988e54f3c4c291e2077a83809663f123731abe76`. **Neither of the two framework source pins has been verified as the installed DEVELOPMENT version.**
- [Final 22-case suite review](MATERIAL-ISSUE-SOURCE-PINNED-22CASE-FINAL-SECURITY-REVIEW-2026-10-16.md): all 11 captured excerpts independently matched their reviewed GitHub source; security limits remain.
- Frappe pinned `frappe/__init__.py`, blob `f6224c701fa5a6b36bdbe25511be1d78cdc4f042`: `get_installed_apps` (near line 924), `_load_app_hooks` (near 962) and `get_hooks` (near 992) can depend on site/request/client caches. **Calling `get_hooks` is not automatically zero-side-effect**: it can populate a cache on miss.
- Frappe pinned `frappe/model/document.py`, blob `e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a`: `run_method` invokes registered hooks and, separately, Notification evaluation, Webhook dispatch and Server Script dispatch. Event configuration can be site/DB-specific.
- Frappe pinned `frappe/core/doctype/server_script/server_script_utils.py`, blob `292a70c93f3fe2a39bcd56d5abe4b7397a5eebe2`, shows enabled Server Script map can be cached.
- Frappe pinned `frappe/integrations/doctype/webhook/__init__.py`, blob `804560319ffb16c60798d807064a02defb336443`, and Notification module `frappe/email/doctype/notification/notification.py`, blob `df575e826ef16b96ea8aa379a2227d900b8e8a50`: enabled site records and conditions can influence external side effects.

The above pinning establishes how the **reviewed references** work, not the actual DEV deployment state.

## 3. Mandatory zero-read trust gate before any future runtime proposal

**P0 — independently attest a genuine DEV-only target, without querying the shared Docker daemon or guessing a path.** This is a prerequisite even for seemingly read-only inspection.

A later *separately approved* operator-originated provenance record must specify:
- Exact authorized DEV service/bench/site context and **pre-existing trusted identity evidence** that is independent of Docker Compose labels, container names, redis URLs, shared-daemon filtering, guessable host directories or unverified PIDs. The owner/operator must attest it from existing trusted deployment administration records **before** any probe. Do not solicit or print secrets, site names, PID or credentials in chat/source control.
- Exact target file/directory or process binding, its owning service user, intended read scope, known symlinks and mount boundaries, and a way to verify there is no traversal to a shared/PROD mount **before reading contents**. Any directory or mount check that requires PROD enumeration is out of scope.
- Exact executable/build that would perform the reads, absolute executable paths, a fixed allowlist of operations and outputs, a nonroot execution identity with no ability to follow unexpected links, and a STOP response if the scope cannot be established using preapproved evidence.
- Explicit confirmation by the operator that the same permissions cannot read PROD code/config/data through an unexpected mount, privileged Docker socket, or shared service connection. If this cannot be established independently, `DEV_PROVENANCE_UNVERIFIED_STOP`, **no runtime command**.

**No trusted DEV process/file anchor is verified in this conversation.** As a result, P0 is **NOT PASSED**. A suggested command targeting an assumed DEV filename, PID, site, container or socket would be premature.

## 4. Phase A — GitHub-only expected-state evidence (no DEV operations)

This is the only implementable evidence tier under the *current* GitHub-only authorization:

1. Pin reviewed CCPC custom app feature/review commit and Frappe/ERPNext **reference** GitHub commits, plus the exact source blob hashes of the hooks and stock/ledger code needed for auditing.
2. Inventory expected hooks from committed `hooks.py` files, including CCPC Stock Entry `validate`, `before_submit`, `on_submit`, `on_cancel` and any additional stock, GL, Bin, Serial/Batch/Inventory Dimension hooks in reviewed dependencies. Distinguish direct Stock Entry hooks from hooks on child documents and from `override_doctype_class`, `extend_doctype_class`, permissions, site installed app list and other Frappe extension points.
3. Produce a **fixed-category expected-hazard matrix**: standard source hook, app-defined, data-driven Notification, Webhook, Server Script, scheduler/worker; for each state source `EXPECTED_FROM_GITHUB`, `UNKNOWN_INSTALLED`, `UNKNOWN_ACTIVE`, not `ACTIVE`.
4. Avoid committing site config, real app configuration, usernames, emails, supplier/customer/stock data, service credentials or raw hook payloads. This is *expected* not *observed* evidence.

**Limitation:** GitHub cannot determine actual deployed site records, code drift, cached hooks, installed-app order, enabled Server Scripts or live process imports.

## 5. Phase B — future independently DEV-scoped installed-source inventory (separate approval)

**Not executable from this design.** Only after P0:

- Bind to the one, exact operator-attested DEV code tree, without Docker daemon calls, container listing, recursive filesystem search, symlink following outside the trust boundary, broad process reads or PROD mapping.
- Obtain an **at-rest** read-only source inventory of the exact Frappe, ERPNext and CCPC app revision IDs and meaningful uncommitted/deployed differences inside that boundary. A `git rev-parse` alone is insufficient: unpackaged code, dirty tree, injected overrides or mounted modules may differ. `git status` and other commands may touch index caches/lock files, so choose/verify a truly read-only method or record limitations rather than claiming absolute no-write.
- Scope comparison to a finite, explicit list of pre-reviewed source files and dependency packages; preserve file digests under private operator control if any manifest is potentially sensitive. Git SHA or module file path should not be treated as a credential; still avoid exposing host paths and deployment topology in GitHub.
- Do **not** start Frappe via a new child process merely to read config. That child's imports/overrides may not represent running processes and site initialization can write caches or touch databases.
- If source directories or package origins are ambiguous, or path traversal/shared mounts cannot be ruled out, **STOP**. Even a perfect at-rest inventory cannot prove which modules long-lived processes loaded.

Potential safe output categories only:
`DEV_SOURCE_AT_REST_MATCH`,
`DEV_SOURCE_AT_REST_DIFF_STOP`,
`DEV_SOURCE_SCOPE_UNKNOWN_STOP`,
`INSTALLED_SOURCE_UNVERIFIED`.

Do not print exact private paths, site IDs, hostnames, configs, usernames, credentials, database names, raw module contents, uncommitted file contents or secrets.

## 6. Phase C — future DEV-effective hooks, site config and cached behavior (separate approval)

Requires **more than** at-rest code and a distinct permission review: effective hooks may depend on site-installed apps and order, site/request/Redis caches, enabled DB documents and a long-lived process.

- **App hooks**: compare reviewed `hooks.py` definitions against site-specific installed apps/order and Frappe hook resolution; do not assume CCPC `hooks.py` is the only source, and do not assume a new `frappe.get_hooks('doc_events')` call is nonmutating, because its source can populate caches.
- **Dynamic event records**: at minimum classify whether relevant Stock Entry, Stock Ledger Entry, GL Entry, Withdrawal Slip, Repost Item Valuation and related child DocTypes have enabled document Notifications, Webhooks, Server Scripts, and other custom event subscriptions. The *existence* of enabled records is not an assertion their conditions fired during a Material Issue. Treat rendered templates, scripts, webhook URLs, message recipients and credentials as sensitive; never export them to GitHub.
- **Explicit readonly transaction boundary**: a future site-specific read should use truly read-only permissions and a vetted query/listing mechanism if feasible. Do not assume `bench --site ...` or Frappe API calls are harmless: site initialization, cache misses, server-script map construction, or authentication can write externally, and read queries can contend with live transactions.
- **Loaded process reality**: no at-rest or new-Python-child query can prove what an existing Node/RQ/Frappe web process has cached/imported. A genuinely *in-process* read-only attestation may require code injection, instrumentation or restart, which is **not authorized** and can risk PROD on the shared host. If in-process provenance cannot be independently bounded to DEV, output `LOADED_RUNTIME_UNVERIFIED` and stop; do not perform `/proc/*/environ`, process-wide enumeration, Redis `CLIENT LIST`, test events, or network probes.
- **Sanitized return**: report only classification flags and grounded counts of approved hook categories (e.g., `NOTIFICATION_STATE_UNKNOWN`, `STOCK_ENTRY_HOOKS_HAVE_EXTRA_ENTRIES`) without raw hook names/code, scripts, URLs, site IDs, addresses, email destinations, log lines or DB records. Counts may also be withheld when too identifying.

**No DEVELOPMENT read of any kind is presently approved.** Even if later P0 is satisfied, approval to collect installed-source revisions does not imply approval to read site DB, inspect hook caches, or alter processes.

## 7. Preflight, risk review, and STOP conditions for any future design-to-execution transition

| Gate | Evidence required before a later step | STOP if |
| --- | --- | --- |
| P0 scope | Operator-attested DEV identity and independent provenance, trusted exact path/process boundaries, nonroot read scope, explicit no-PROD reachability | Only Docker labels, guessed folders, shared socket permissions or PROD-inclusive inspection available |
| P1 artifact | Independently reviewed exact file/script hash; GitHub review branch and clean versioned code; default-deny output | Unreviewed code, arbitrary shell/script execution, reliance on `assert` for authorization |
| P2 no side effects | Static proof future methods will not initialize/warm caches, spawn connections/processes, lock production resources or modify files; a narrow rollback plan | Unproven Frappe initialization, hook/Redis caching, database locks, Docker exec, service restart or network requests |
| P3 output | Fixed redacted status vocabulary; no raw source/config/credentials/hook payloads/PROD metadata | Any sensitive endpoint/secret/cross-env raw data required for conclusion |
| P4 consent | **Separate** owner approval for proposal implementation; separate staging approval; separate exact one-shot DEV evidence collection approval; still no PROD scope | Only a generic “continue”, stale/consumed run token, or any request to expand to PROD without explicit scope |
| P5 interpretation | Distinguish expected GitHub, at-rest DEV, effective DB-config, and genuinely loaded process evidence | Conflating Git HEAD with running process or treating DB hook flags as proof of redis/network separation |

**Cannot resolve this by attempting a broad host inventory:** DEV and PROD share host/daemon; scanning all containers or processes, reading raw environments/configs, inspecting Redis endpoints/clients, or following mounted paths into PROD would violate the current boundary.

## 8. Recommended order of next approvals

**First next proposed unit (GitHub-only, requires new explicit approval):** harden the 22-case offline suite's immutable-fixture and execution trust boundaries, with failing optimized-mode tests and pre-exec source validation; keep fixture and test code on review branch only and rerun fully offline. That closes a concrete test-harness issue identified in the [final review](MATERIAL-ISSUE-SOURCE-PINNED-22CASE-FINAL-SECURITY-REVIEW-2026-10-16.md) before it is reused as a gate.

**Afterwards**, if owner wants site evidence, **a separate GitHub-only P0 design and operator-attestation checklist** must be approved and completed before any runtime inspection; it must state a genuinely DEV-bound identity source or explicitly conclude `DEV_PROVENANCE_UNVERIFIED_STOP`. This is distinct from permission to run any command. Continue broader transaction-side-effect review only as authorized, with no live business write.

**Current outputs:** `GITHUB_EXPECTED_SOURCES_ONLY`, `SOURCE_PINS_11_OF_11_MATCH`, historical `OFFLINE_SOURCE_PINNED_22_OF_22_PASS`, `DEV_PROVENANCE_UNVERIFIED_STOP`, `INSTALLED_SOURCE_UNVERIFIED`, `EFFECTIVE_HOOKS_UNVERIFIED`, `LOADED_RUNTIME_UNVERIFIED`, `NODE_ROUTE_UNVERIFIED`, `WORKER_ROUTE_UNVERIFIED`, `DEV_PROD_SEPARATION_UNVERIFIED`, **`POSTING_NO_GO`**.

**No code, tests, Ubuntu operation, DEVELOPMENT runtime activity, Redis/SQL access, PRODUCTION access or financial transaction occurred.**
