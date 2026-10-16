# CCPC ERPNext — P0 DEVELOPMENT-only target identity / operator attestation checklist

**2026-10-16 | GITHUB-ONLY CHECKLIST DESIGN | NO OPERATOR ATTESTATION COLLECTED OR VERIFIED | DEV_PROVENANCE_UNVERIFIED_STOP | POSTING_NO_GO**

## Purpose and approval boundary

This is a **non-executable design checklist** for a future *separately authorized* operator-originated attestation of genuine CCPC DEVELOPMENT identity before considering any installed-source or effective-hook observation. It is not a shell runbook, script, permission grant, secret-collection form, or authorization to access the Ubuntu host, DEVELOPMENT, or PRODUCTION. No operator has supplied these attestations in this conversation. **No P0 checkpoint is currently passed.**

This checklist implements the [GitHub-only DEV installed-source/effective-hook attestation design](MATERIAL-ISSUE-DEVELOPMENT-SOURCE-AND-HOOKS-ATTESTATION-DESIGN-2026-10-16.md) after the [35-case final security review](MATERIAL-ISSUE-HARDENED-35CASE-FINAL-SECURITY-REVIEW-2026-10-16.md). CCPC DEV and PROD may share host infrastructure and Docker daemon. **Do not assume that a container/project label, a site name, service port, familiar bench directory, DNS name, `git status`, or a known user is an authenticated DEV boundary.**

**P0 aims to settle whether any future DEV-only *read* can be credibly scoped. It does not itself authorize that read, SQL access, an ERPNext transaction, Redis inspection, app deployment, or service changes.** A P0 result cannot prove Redis physical isolation, loaded web/worker/Node code, accounting/stock correctness or reversibility of cache/publication side effects.

## Sources and separation of duties

The *future* authorized operator should privately compare independent existing administrative records **without performing a new shared-daemon/PROD-inclusive probe under this authorization**. Possible source categories include owner-approved deployment/infrastructure change records, signed deployment manifests, trusted access-control documentation or already captured verified DEV-specific build/scope records. GitHub review sources may establish intended setup but are **not** proof of the current live environment.

Each accepted assertion should have:
- an authorized operator responsible for it and a second reviewer where practical;
- a source document revision/date and a *nonsecret* cross-reference in the private operator record;
- a determination of whether the underlying record predates the proposed probe and is independently trusted, or is merely a label guess;
- a timestamp/scope-validity statement, because changes in mounts, runtime ownership, Compose deployment or permissions can invalidate P0 immediately.

**Do not put paths, hostnames, usernames, IPs, site names, PIDs, Docker IDs, credentials, environment variables, uncommitted code, service configs, customer data, exact installed-app lists or sensitive infrastructure evidence in GitHub or in chat.** The private operator retains supporting originals within approved controls. This GitHub checklist records only status vocabulary and criteria, never source detail.

## Decision checklist (all mandatory for P0 acceptance)

| Gate | Question and required evidence | Accept only when | Otherwise |
| --- | --- | --- | --- |
| **P0-A: independent target origin** | Is there an existing trusted record binding **one uniquely defined DEVELOPMENT bench/site/service target** to an approved DEV identity independently of the shared Docker daemon's project/name labels and guessed host paths? | Authenticated owner/operator chain of custody and DEV target identity anchored before the probe | `DEV_TARGET_ORIGIN_UNKNOWN_STOP` |
| **P0-B: scope of objects** | Can every directory, mount, symlink and process scope that a proposed read could traverse be bounded **without enumerating or inspecting PRODUCTION**? | Explicit finite DEV allowlist, no unknown shared bind mounts, no symlink or mount escape, independent supporting records | `DEV_FILESYSTEM_SCOPE_UNKNOWN_STOP` |
| **P0-C: reader permission** | Is the future reader's identity scoped to the smallest DEV-only read capability, without root/Docker-socket privilege or write-capable Redis/SQL/site access? | Nonroot operator and permission restrictions shown to prevent unintended host/PROD access; no unbounded fallback commands | `DEV_READER_SCOPE_UNKNOWN_STOP` |
| **P0-D: exact provenance relation** | Is the proposed read target tied to installed Frappe, ERPNext, CCPC app/source checkout through an independently trusted reference, rather than to an arbitrary `git rev-parse` result or path name? | Current DEV-specific source ownership is documented; uncommitted/drift state is expressly unresolved until separate read | `DEV_CODE_ORIGIN_UNKNOWN_STOP` |
| **P0-E: effect minimization** | Is the eventual operation defined narrowly enough to avoid Frappe initialization, hook/cache warmup, SQL/Redis connections, service restart, file modifications, container listing, DNS/network queries and background job interactions? | The proposal uses only precise pre-reviewed low-impact operations and does not rely on an unreviewed `bench --site`/Python command | `DEV_READ_SIDE_EFFECT_UNKNOWN_STOP` |
| **P0-F: data minimization** | Can information be classified and filtered **before capture**, rather than collecting secrets/raw configs or PRODUCTION metadata and sanitizing afterwards? | Fixed, nonsecret status outputs only; no raw secret/config/process/ledger/hook event payloads | `DEV_OUTPUT_SCOPE_UNKNOWN_STOP` |
| **P0-G: instability** | Is the binding still valid at the proposed observation time, including deploy changes, shared mount changes, process replacement and code/cache drift? | A bounded freshness requirement and STOP-on-change procedure independent of PRODUCTION reads | `DEV_ATTESTATION_STALE_STOP` |
| **P0-H: approvals** | Are future implementation, staging, one-shot read and any site-data reads **separate, explicit owner approvals** covering their exact scope? | An approval ledger can differentiate each phase, and no consumed token is reused | `DEV_READ_NOT_AUTHORIZED_STOP` |

**Hard decision rule:** All gates must be supported by independent, operator-owned evidence before *any* DEV probe proposal can be considered for staging. **Unknown is failure, not "probably DEV."** The review must not manufacture a scope by reading PROD and then filtering it out. An operator's unsupported assertion, unverified branch name, Docker Compose label, expected network, volume prefix or matching Redis URL is insufficient.

## Proposed sign-off artifacts (future only; no sign-off exists)

A future operator-owned P0 record should contain the following **privately**, not in a public GitHub issue, this chat or a code commit:

- Scope description and inventory of evidence categories A–H without embedding raw data;
- Authoritative owner/operator and second-review confirmation, dated at the time of assessment;
- Explicit statement whether any DEV/PROD shared host, daemon, mount, user, or network constraints remain unresolved;
- Known limitations, TOCTOU risk and expiry condition requiring re-attestation;
- The *exact category* of contemplated next read (at-rest source metadata, site-effective-hook existence categories, or loaded-process metadata) and whether that category needs its **own** approval;
- A STOP result when any item cannot be independently shown.

Only a **coarse status** may be added to the rolling GitHub handoff after separate authorization, e.g., `P0_OPERATOR_RECORD_REVIEWED` or `P0_DEV_PROVENANCE_UNVERIFIED_STOP`. Even a privately accepted P0 is **not** evidence of a full live process mapping or network separation.

## What a future pass would and would not unlock

```text
Current GitHub-only expected source and 35 offline tests
       |
       v
P0 independent genuine DEV target + least-privilege/scope record
       |-- insufficient independent evidence --> STOP (no commands)
       |
       v  (still requires fresh approval)
P1 implementation security review of one finite read-only source inventory
       |
       v  (still requires distinct staging approval, exact hashes)
P2 controlled staging on DEV identity only
       |
       v  (still requires distinct one-shot execution approval)
P3 installed-at-rest source comparison, fixed redacted outputs
       |
       v  (still no automatic permission for site DB or live process reads)
P4 separate effective-hook / cached-state read design and approval
       |
       v
Transaction-specific integration gate (accounting/inventory/redis),
still POSTING_NO_GO until independently verified and approved
```

**Gate separation:** Source-at-rest **does not** establish effective Notification/Webhook/Server Script enablement, loaded worker routes, cache state, pub/sub isolation, committed transaction safety or a safe rollback experiment. A separately approved SQL-credentialed/site effective-hook check would require its own risks, read-only semantics and data minimization; no one should derive it automatically from P0.

## Unsafe shortcuts to reject

- Reading all Docker containers/projects to determine which belong to PROD versus DEV, or using Docker `inspect` on IDs selected from unauthenticated labels.
- Treating shared daemon scope or `docker exec` as isolated because it is called "development".
- Listing all host PIDs/`/proc/*/environ`, commands, Redis clients, network peers, DNS records or mounts and then discarding PROD results.
- Running `bench --site` / `frappe.get_hooks` for "read-only metadata" without independently checking initialization, cache warming, SQL/Redis effects and authorized exact site scope.
- Extracting site configuration, credentials, raw scripts/webhooks/notifications, secrets or topology into GitHub, chat, logs or a test fixture.
- Reusing previous Stage A v1/v2 approval flag or treating this checklist's existence as a one-shot authorization.
- Assuming that stock/GL transaction rollback will reverse Redis cache invalidation, realtime messages or background jobs.

## Current disposition / next consent gate

**Design reviewed in GitHub only. P0 NOT SATISFIED.** There is **no verified independently trusted DEV target, no operator P0 record and no authorization to read the Ubuntu host**. Return statuses:
`GITHUB_EXPECTED_STATE_ONLY`,
`P0_DEV_PROVENANCE_UNVERIFIED_STOP`,
`INSTALLED_SOURCE_UNVERIFIED`,
`EFFECTIVE_HOOKS_UNVERIFIED`,
`LOADED_RUNTIME_UNVERIFIED`,
`NODE_ROUTE_UNVERIFIED`,
`WORKER_ROUTE_UNVERIFIED`,
`DEV_PROD_SEPARATION_UNVERIFIED`,
**`POSTING_NO_GO`**.

**Recommended next conversation scope if owner authorizes:** GitHub-only review of whether the current approved deployment runbooks/records themselves contain enough nonsecret provenance to design a P0 procedure, without asking the operator to run a command or supply secrets. If not, document that no source of trusted DEV-only identity is currently demonstrated and STOP. A real host or site read is a later, separately authorized action.

**No shell commands, scripts, runtime measurements, environment-specific target values or executable probes are furnished in this document. PRODUCTION remains untouched.**
