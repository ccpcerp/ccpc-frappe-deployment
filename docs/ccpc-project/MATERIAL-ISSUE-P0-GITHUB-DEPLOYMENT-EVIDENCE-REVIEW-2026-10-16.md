# CCPC ERPNext — P0 DEVELOPMENT identity: GitHub deployment-record evidence review

**2026-10-16 | GITHUB DOCUMENTS ONLY | P0_DEV_PROVENANCE_UNVERIFIED_STOP | POSTING_NO_GO**

## Authorization and evidence question

Owner said **“Approved continue”** to the exact preceding proposal to review **existing GitHub deployment documentation** for independent proof of DEVELOPMENT identity **without any runtime lookup, new operator command, production inspection or script**. This is a static review of committed/historical materials, not a new operator sign-off or attestation. No tests run, no application/test/script changed, and no Ubuntu/DEVELOPMENT/PRODUCTION action occurred.

**Question:** Can currently versioned deployment evidence satisfy the [P0 DEV-only identity checklist](MATERIAL-ISSUE-DEV-IDENTITY-P0-OPERATOR-ATTESTATION-CHECKLIST-2026-10-16.md), so a future read of installed source/effective hooks could be designed without accessing PRODUCTION? **Answer: Not yet.** Records give a credible historical setup and operator testimony, but not an independently current, capability-bounded DEV-only read scope. A persistent or ephemeral container named DEV, a tracked Compose template, a documented bench path and an operator-reported command result are insufficient on their own.

## Pinned GitHub source register

These records were **read by connected GitHub tools** using the listed review/documentation branches. Values are Git **file-blob** identities, not live deployment hashes.

| Source | Branch/ref read | Verified blob | What it supports and limits |
| --- | --- | --- | --- |
| [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) | `docs/ccpc-checkpoint-2026-10-10` | `b3d9ac65b3a016de017093dcc47937b44fc0ee74` | Source-of-truth, past operator checks, current permissions policy. States PROD separate Compose project on same Ubuntu host and persistent DEV site. |
| [Docker DEV/PROD architecture](DOCKER-DEV-PROD-ARCHITECTURE.md) | same docs branch and independently identical on review branch | `6007ebef0c2f36794d4a4607a2c47efcd42a47e2` | Dated **2026-10-10** synthesis of earlier investigations, *explicitly not a new live Docker check*. Historical DEV path/container, host RW bind, two logical Compose projects and shared kernel/daemon; local active Compose file ignored by Git. |
| [Reviewed GitHub-to-DEVELOPMENT script delivery](REVIEWED-SCRIPT-DELIVERY-TO-DEVELOPMENT.md) | docs branch | `438db0f7003174014e462dd302f1e7bd2619de1d` | Operator-reported and connector-cross-checked **2026-10-15** private GitHub access, isolated operator-home script staging, checksum and one-shot *read-only Git reference* script execution; explicitly does **not** attest host filesystem boundary or allow new scripts. |
| [CCPC operations](operations.md) | docs branch | `e2eb1fa940a6c3d263e7a9724e534e850142399a` | Historical dedicated reporter-account mount/read restrictions; narrow reporter outbox is not an authenticated DEV bench/site/source scope. Reporter automation was cancelled. |
| [Project context](ccpc-project-context.md) | docs branch | `3c6f28a5d126dc1758c5a11c2d1d20262d3b3137` | Prior container/SSH-mount audits and source synchronization history; corroborates historical status but no fresh independent per-target attestation. |
| [Historical P20 handoff](P20-HANDOFF-2026-10-10.md) | docs branch | `ec1e7a41809cbd9cadd52bd5e5e44aa7f2736683` | Explicitly **archived/historical**; contains operator reports and incidents, not the active P0 state or present-day proof. |
| [Tracked devcontainer Compose example](../../devcontainer-example/docker-compose.yml) | deployment review branch | `75f57aac53dd03246d4d7d355db2e8ce641aa78e` | Declares intended services and host RW development workspace; a **template**, not the Git-ignored actual active DEV Compose file, mount permissions, runtime process identity or live DEV/PROD separation. |
| [P0 checklist](MATERIAL-ISSUE-DEV-IDENTITY-P0-OPERATOR-ATTESTATION-CHECKLIST-2026-10-16.md) | `review/material-issue-first-commit-preparation-2026-10-15` | `cf481fd2d80e02cdf1a0a166a93c8bb2cf54af42` | Mandatory conditions P0-A–H and STOP policy, not completed operator answers. |
| [DEVELOPMENT source/effective-hook design](MATERIAL-ISSUE-DEVELOPMENT-SOURCE-AND-HOOKS-ATTESTATION-DESIGN-2026-10-16.md) | same review branch | `fab6c6805cee59ea191a62b0e921aa6a42860dbb` | Separates expected GitHub source, DEV installed at rest, site effective hooks, and code actually loaded in long-lived processes. Design-only. |

The GitHub file search available for the repository returned no matches even for known existing titles/terms; therefore **this is a targeted audit of the verified source set above, not a claim to have exhaustively searched every possible branch/file**. The files actually cited were independently fetched and verified by path and Git blob, not inferred from search snippets. Unexamined private operator records or uncommitted Git-ignored deployment files could alter a future P0 determination, but cannot be presumed to exist or be valid.

## Historical findings supported by those records

1. **Logical DEV/PROD separation, shared trust infrastructure.** The architecture records two Compose projects and separate application sites on the **same Ubuntu host, Docker daemon and kernel**. A Compose project name is an operational identifier, not an authentication or least-privilege boundary. An operator with host Docker authority could potentially inspect/mutate both, regardless of the apparent project name.
2. **Previously observed DEV container/source and persistent site.** Earlier host/operator sessions identified a development bench/checkout and a persistent DEV site; workflow records also include an observed Git branch/HEAD/status from an earlier app checkpoint. That helps define what a future operator should verify, but **does not establish the live code/branch/tree today**, the effect of uncommitted changes, site ownership, mount symlinks or running process imports.
3. **Actual active DEV Compose differs in provenance from the GitHub template.** The architecture says the active local DEV Compose configuration is **Git-ignored** and the running container may predate changes to tracked configuration. A tracked `devcontainer-example` file does not authenticate a live container's mount/network/privilege topology.
4. **Recorded credential exposure defeats a casual read-safe assumption.** Earlier authorized read-only host audit identified SSH material **mounted and readable** inside the DEV container. The runbooks prohibit unattended/experimental coding agents there. No independent refreshed proof that this exposure was removed, or that a proposed metadata reader lacks such access, was found in these reviewed GitHub materials.
5. **Limited previous delivery works; scope still unknown.** The October 15 manual GitHub delivery/read-only Git-reference script passed according to operator evidence, checked against pinned GitHub source. It establishes that *this one scoped transfer/execution* happened as reported, not a generally isolated read mechanism for arbitrary DEV bench files, Docker containers or effective site hooks.
6. **Historical documentation contains broad host inventory commands** for separately authorized operational checks. These may include shared-daemon DEV/PROD results. **Do not reuse them under the current P0 constraint**. A host-wide list then filtering out PROD would itself touch PROD metadata, which is not authorized.
7. **No independently signed/current operator P0 A–H record** or trusted chain of custody for exact DEV-only target, mount/symlink limits and minimal read privileges was presented in the reviewed records. The P0 checklist remains unanswered. This is **absence of proof**, not a claim that a secure DEV-only mechanism cannot exist.

## P0-A–H evidence assessment (all eight mandatory)

| Gate | Source-grounded historical signal | Present determination | Missing proof |
| --- | --- | --- | --- |
| **A — independent target origin** | Historic DEV container/bench/site and operator shell observations are documented, but correlate mostly with names/Compose/project paths | **UNVERIFIED STOP** | Independently authenticated, current DEV-only target ownership *not derived from untrusted Docker labels or self-described path names* |
| **B — filesystem/process scope** | Template host RW bind, Git-ignored active Compose, same host/daemon; sensitive material historically mounted | **UNVERIFIED STOP** | Finite actual mounts/symlinks/permissions and assurance a future reader cannot traverse or enumerate PROD |
| **C — least-privilege reader** | Historical narrow reporter account existed for outbox only; separate DEV container exposed SSH materials | **UNVERIFIED STOP** | Proposed NEW reader with DEV-source-only rights and no Docker, PROD mount, Redis/SQL or secret capability; reporter cannot simply be repurposed |
| **D — at-rest source provenance** | Earlier DEV checkout branch/HEAD operator report and private GitHub commit readbacks | **UNVERIFIED STOP** | Current trusted link to installed Frappe/ERPNext/CCPC code and effective physical file contents, including any local drift |
| **E — side-effect control** | Manual delivery success was narrowly read-only Git reference; documented generic commands include host-wide Docker inventories | **UNVERIFIED STOP** | Exact independently reviewed inspection that cannot initialize Frappe, populate cache, read shared daemon, lock DB or trigger events |
| **F — output minimization** | Existing script review/redacted status design shows useful procedural approach | **DESIGNED, NOT ATTESTED** | Output filtering **before acquisition**, restricted data types, bounded error/output handling for an actual proposed reader |
| **G — freshness / TOCTOU** | Architecture consolidation dated Oct 10; previous operator tests Oct 12–15; active Compose may change without GitHub updates | **UNVERIFIED STOP** | Current operator-verified ownership, deployment/build, permissions/mount state and expiry/recheck protocol, without PROD reads |
| **H — separate approvals** | GitHub-only scope granted for this review; prior one-shot read/test approvals consumed | **RUNTIME NOT AUTHORIZED STOP** | Separate implementation, staging and specific one-shot DEV read approvals after A–G are established; PROD needs its own approval |

**Overall:** `P0_DEV_PROVENANCE_UNVERIFIED_STOP`. At best the reviewed documentation supports **`HISTORICAL_DEV_LAYOUT_DOCUMENTED`** and **`GITHUB_EXPECTED_STATE_ONLY`**. **None of the current P0-A–E or G conditions is independently passed by these versioned records; F is a design capability only; H remains a future consent gate.** No installed-version, site-hook or in-process runtime evidence is authorized or collected.

## Practical next gate (without an unapproved host probe)

**Do not write another guessed-host-path script, scan containers/processes, reuse an old token, request blanket operator inventory, or infer safe DEV identity by comparing sites.** The current blocker is an *independent existing operator-owned provenance record*.

A future new, narrowly scoped **P0 operator evidence-review authorization** could ask the administrator to **review previously held, trusted DEV-specific administrative records privately, without running any command**, and report only whether the eight P0 categories can be independently substantiated. Supporting material and topology remain private, not pasted to chat or GitHub. If such records do not exist, record STOP and consider a separately risk-reviewed **new DEV-only containment boundary** as infrastructure design—not as an implicit read or PROD action.

Only after independently established provenance should there be a separate, reviewed **non-executable** proposal for a single finite DEV installed-source metadata read; implementation, staging and one-shot execution would each require fresh approvals. Site DB/config hook queries, loaded worker/process checks and business transactions are **not included** in source-at-rest permission.

## Decision and unchanged protections

**DECISION: current verified GitHub deployment records are INSUFFICIENT for P0. NO-GO for DEV runtime source or hook attestation.**

- No new scripts or tests produced or run; prior offline hardened **35/35 normal and 35/35 optimized** remains historical, not rerun or a production-readiness proof.
- CCPC app on `feature/withdrawal-material-issue-safety` remains as last verified; no branch switch/pull/deploy.
- **PRODUCTION not accessed**; DEVELOPMENT not accessed; no Docker/Redis/SQL/Node/RQ/site config reads, no mutations, no Stock Entry/SLE/GL.
- `P0_DEV_PROVENANCE_UNVERIFIED_STOP`, `INSTALLED_SOURCE_UNVERIFIED`, `EFFECTIVE_HOOKS_UNVERIFIED`, `LOADED_RUNTIME_UNVERIFIED`, `NODE_ROUTE_UNVERIFIED`, `WORKER_ROUTE_UNVERIFIED`, `DEV_PROD_SEPARATION_UNVERIFIED`, **`POSTING_NO_GO`**.

**GitHub documentation-only review complete; no further automated activity or server action is scheduled.**


## Operator-held record availability follow-up — records only (2026-10-16)

**Approval interpreted narrowly:** The owner approved continuing the previously proposed **private review of existing trusted DEV-specific operator/deployment records only**. This does not authorize running any Ubuntu command, inspecting Docker, accessing DEV/PROD apps or data, enabling an external service, developing/probing a new reader, or submitting a financial transaction.

**Available evidence and actual checks:**
- Rechecked the authoritative GitHub workflow, current handoff, this P0 audit and the existing P0 operator checklist on their verified branches. No current operator-signed P0 A–H provenance record was found in those versioned documents.
- Inspected **six locally available, historical Project reference files** (`framework.md`, `operations.md`, `roadmap.md`, `changelog.md`, `ccpc-project-context.md`, `recovery.md`) for independent DEV-only identity/access documentation. They describe historical deployment, credentials-protection rules, DEV/PROD separation, and backup/recovery processes; **none provided a currently signed or independently authenticated DEV-only process/filesystem reader boundary**. These legacy reference copies have *lower authority* than current GitHub information; do not treat their metadata as current live proof.
- Used **metadata-only, targeted** searches in the connected Google Drive for CCPC ERPNext, DEVELOPMENT attestation, and CCPC deployment. The searches returned no identifiable operator deployment-identity attestation record. Two loosely related implementation spreadsheets were not accessed or treated as source evidence because their contents were not a demonstrated administrative attestation. Search is **not exhaustive**; no claim is made about private, offline or unindexed operator files.
- **No private operator-held files outside these available sources were supplied, accessed, or verified.** No operator signed P0, and no secret-bearing data was collected. The absence of an accessible attestation is a limit on current evidence, not proof that such a record does not exist elsewhere.

**Disposition:** `P0_OPERATOR_RECORD_NOT_AVAILABLE_FOR_INDEPENDENT_REVIEW` and **`P0_DEV_PROVENANCE_UNVERIFIED_STOP`**. No P0 gate has been advanced from the prior assessment. Historical DEV identifiers, earlier Git branch observations, the tracked Compose template, and historical read-only script transfer continue to be **insufficient** to authorize even a new DEV read.

**Next meaningful operator step — does not require server execution:** The authorized deployment administrator may privately locate any **pre-existing** trusted, dated DEV-specific identity, access-control, mount/namespace and reader-permission records and obtain independent internal review against [P0-A–H](MATERIAL-ISSUE-DEV-IDENTITY-P0-OPERATOR-ATTESTATION-CHECKLIST-2026-10-16.md). Keep original records and their contents in the approved private administrative system. A future *separately requested* status report can contain only eight **YES / NO / UNKNOWN** determinations with nonsecret evidence categories, independent-review indicator and currency/expiry status; **NO/UNKNOWN means STOP**. Such a high-level operator report is a **claim**, not substitute for verified provenance; before a probe it needs a separate assessment of authenticity, least privilege and no-PROD reachability. Do not paste service paths, SSH material, secrets, user data, environment contents, Docker metadata or actual production settings.

**No additional automatic searches or scripts scheduled.** No DEVELOPMENT or PRODUCTION runtime activity, no code modifications, no test reruns and no Material Issue posting. `POSTING_NO_GO` remains.
