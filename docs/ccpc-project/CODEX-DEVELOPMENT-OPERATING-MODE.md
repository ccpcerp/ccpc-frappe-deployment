# CCPC ERPNext — Codex as an active DEVELOPMENT tool

**Owner decision:** 2026-11-21 (Asia/Manila)  
**Status:** Authorized **direction and workflow planning**; not a claim that Codex is installed, authenticated or running. No server command, Docker action, firewall change, Codex launch, database migration, pull or deployment has occurred as a result of this document.  
**Primary rule:** **Codex may contribute actively to CCPC ERPNext DEVELOPMENT; PRODUCTION is physically separate and explicitly out of scope.**

## 2026-11-21 operator status — Codex CLI installed, signed in, isolated clone created

**Newer evidence superseding the initial planning-only status above:** The operator reported installing standalone Codex CLI **0.171.0** on `ccpcerpserver` under their non-root account (Linux x86_64), and successfully completing ChatGPT device-code authentication. A fresh source-only `git clone --no-checkout` of `ccpcerp/ccpcerp` into `$HOME/ccpc-codex-work/ccpcerp` succeeded; no checkout was reported yet. GitHub independently confirmed the candidate Phase 1 release branch `release/withdrawal-department-phase1-2026-11-17` at **`034afb116cf3fe0e3f9315b932eceba6dc961ce6`**. The next operator action is the exact **new local review branch checkout + status/SHA check** in [CURRENT-HANDOFF-3.md](CURRENT-HANDOFF-3.md). No Codex agent session or code changes are yet reported; no live bench/DB/Docker/PRODUCTION operations were made for onboarding.

## Why this decision matters

The project owner reaffirmed: “the only restriction for codex is not to involve itsef in production server which is physically separate but for the development codex should be the best asset.” This resets priorities: the development environment exists for code creation, diagnosis and testing; do not require completion of a complex shared-host experimental Docker/Squid firewall project before beginning ordinary Codex-assisted development in a **separate, constrained workspace**.

The previously reported **Codex NO-GO** belongs to the specifically reviewed Docker/Squid agent/proxy laboratory and its unfinished launch/isolation acceptance, **not to all Codex CLI use**. PR #39 remains draft/unmerged. Do not turn this owner decision into authorization to start that exact stopped lab agent or to remove installed protective firewall rules without a separate reviewed launch path. Codex on DEVELOPMENT is the preferred operating direction; a separate VM purchase is not currently required.

## Permitted development workflow

1. **Understand and review code:** Read GitHub's latest applicable custom-app branches and current requirements; inspect or edit a project-owned working copy or disposable worktree, not an unchecked production checkout or shared live ERPNext application directory.
2. **Implement scoped DEVELOPMENT code changes:** Focus on the CCPC custom ERPNext application, tests, bug fixes, refactoring and documentation. Use a reviewed feature/review branch, preserve existing uncommitted DEVELOPMENT changes, and return verified commits and test evidence to GitHub.
3. **Test early and realistically:** Run local static/unit tests in a bounded isolated workspace and use the project's existing disposable CircleCI Frappe/ERPNext/MariaDB infrastructure for SQL, stock ledger, GL, invoice, rollback/concurrency and intercompany integration acceptance as approved. A mocked unit test is not a database integration test.
4. **DEV integration:** After reviewing Git status, branch, commit, backups and recovery, separately authorize a DEVELOPMENT pull/migration/restart or persistent database mutation when needed. Use genuine DEVELOPMENT acceptance to confirm functionality.
5. **Review before release:** GitHub remains source of truth; PRODUCTION deployment is a distinct owner-controlled process and must never follow automatically from a Codex or GitHub operation.

**Day-one delivery priority:** Withdrawal Slip → Material Issue → Stock Ledger/Expense GL → intercompany invoice, failure/replay/concurrency tests, then the four already-approved operating reports. Prefer these ERPNext deliverables to continued speculative Codex infrastructure engineering.

## Non-negotiable boundaries: PRODUCTION and data integrity

- **Never connect to, SSH into, modify, query, deploy to, back up/restore, or issue API requests to the physically separate PRODUCTION server or its data** as part of Codex DEVELOPMENT work. No production DNS/IP targets, credentials, network mounts, backups or customer records may be available in its workspace. Do not use PROD as a test target.
- Ordinary development actions are encouraged **without repeat approval** when they remain within reviewed source/worktree changes, offline tests and disposable synthetic fixtures. The owner still separately authorizes activities with persistent consequences: modifying real DEVELOPMENT accounting/stock/customer records, migrations or schema changes, host-wide Docker/firewall/network edits, service restarts, applying unreviewed pull/merge, destructive cleanup or privileged access changes. This preserves the permanent GitHub-first and transaction-integrity requirements; “only restriction is production” expresses the desired broad developmental role, not permission for accidental data loss.
- Do not expose host root privileges, the Docker socket, production credentials, SSH keys, other users' secrets, sensitive shared mounts or unnecessary network access to unreviewed Codex subprocesses. An **unprivileged, dedicated DEVELOPMENT workspace** with explicit tool approvals is the default. Do not enable dangerous bypass/full-access modes by default. Allow a broader test action only when its scope and effect are reviewed.
- Codex is a collaborator for supervised engineering, **not an autonomous publisher or deployment agent**. The cancelled automatic Codex-report-to-GitHub workflow and paid API/reporting arrangement stay cancelled. No background or scheduled reporting is implied.
- Never overwrite dirty DEVELOPMENT files. Capture branch, commit, `git status` and pending work before changes; prefer a separate reviewed worktree and commit provenance. No PRODUCTION-side operations or silent migrations.

## Practical low-friction start (next operator action, not yet executed)

**First establish what is already installed** on the DEVELOPMENT server using a specifically reviewed, read-only, unprivileged inventory: the current human user, whether `codex` CLI exists, its version if installed, and the current safe project/worktree state. Do not print environment variables, secret names/values, credential files, Docker inventories, or repository remotes with embedded tokens.

Then, based on actual observed state, choose the least intrusive option:

- **CLI present:** Run Codex manually as a non-root operator inside a clean, project-only checkout/worktree, with approval prompts on and only the permissions needed for the current source task. Do not start or attach the old stopped Docker/Squid laboratory simply to use Codex.
- **CLI absent:** Prepare a narrow installation proposal and verify official supported installation/authentication for the current platform. Installation or authentication must not be presumed complete, performed silently, or require new paid API accounts unless the owner expressly requests them.
- **A needed test requires actual Docker or MariaDB:** Prefer the existing approved disposable CI environment; for persistent DEVELOPMENT integration, use a separate reviewed and recoverable procedure with exact scope.

**First valuable assignment once a suitable Codex workspace is actually available:** Inspect current reviewed GitHub custom-app branches and relevant tests; find the next concrete failure or unverified business flow in Withdrawal Slip → Material Issue → intercompany billing; implement/verify a focused GitHub change and identify the next real disposable integration test. Keep results and branch/commit evidence in GitHub.

## Relationship to the earlier security review

PR [#39](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/39) and [Step 132](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/review/codex-proxy-network-hardening-2026-11-19/docs/ccpc-project/CODEX-STEP-132-FAIL-CLOSED-LAUNCH-HOLD-DESIGN.md) describe the **specific networked Docker/Squid laboratory** and remain a valid, uncompleted security review. The operator-reported Step 130/131 snapshots establish that that agent was stopped and restart-disabled at inspection time. Those outputs do not prove current CLI installation, safe host sandbox configuration or authorization to launch the old agent.

**Next milestone:** A single focused, sanitized read-only assessment of a normal non-root Codex CLI/development workspace, followed by ordinary source work if suitable. No new physical server or unbounded firewall redesign is a prerequisite for that assessment. No host action has been taken by this GitHub-only policy update.
