# CCPC ERP Deployment Framework Roadmap

*Last updated: 2026-10-12 (current priority override)*

## Current priority override — 2026-10-12

The owner has **stopped extra Codex reporting/API automation work** and adopted the [GitHub-first CCPC custom-app workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md). The detailed historical P20 plans below are not active next steps. **Next:** inspect and preserve eight uncommitted DEV files + separately review `AGENTS.md` on a GitHub checkpoint branch; then complete Withdrawal Slip → Material Issue → Intercompany Billing concurrency/idempotency testing on DEV, with all subsequent app code changes reviewed in GitHub first. Production remains out of scope absent explicit approval.

## Purpose

This document tracks planned and partially completed improvements to the
CCPC ERP Deployment Framework.

Current verified operational state belongs in `ccpc-project-context.md`.
Completed historical changes belong in `changelog.md`. Detailed
procedures belong in `operations.md` and `recovery.md`.

Only stable and tested improvements should be promoted into production
releases.

## P20 — Automatic Codex reporting and independent AI review (2026-10-10)

**Present state:** P19 controlled live GitHub submission is complete, delivery
verified and recorded in SQLite; token revoked/removed and one-time approval
retired. General publisher remains disabled. The GitHub AI reviewer is a draft
PR #23, not activated. Automatic reporting is **not operational**.

| Phase | Current verified state | Gate to next phase |
| --- | --- | --- |
| P20A — confidentiality boundary and format | P20A-1 installed; P20A-2 passed 15/15 offline tests | Codex structured metadata handoff, atomic/stable task IDs, fail-closed producer tests |
| P20B — automatic report transport | Not enabled | Offline integration, dedup/reconciliation, credential rotation, scheduler isolation, safe failure handling |
| P20C — GitHub AI reviewer | Draft deployment PR #23 exists; not merged/enabled | Review event filters, bot-loop protection, API secret, retention, model/cost, permissions, adversarial inputs |
| P20D — end-to-end activation | Not started | Explicit operator approval for credential installation, live costs, workflow merge, and temporary/recurring automation |

**Automatic-summary scope:** metadata-only enumerated JSON, no agent free text,
paths, terminal transcript, source code or business data. The existing P20A
module enforces `version`, `environment`, `work_type`, `status`, `change_scope`,
`test_status`, `finding`, `risk`, `approval`, 1024 UTF-8 input bytes maximum.
The generated report is suitable for triage, **not independent evidence of
what code changed or which tests really passed**. Detailed engineering reports
remain manually reviewed and SHA-256 approved.

**Critical work before unattended posting:** tie each completion event to a
stable, immutable, non-sensitive task identity (the current renderer's generic
heading plus second-precision timestamp can collide); guarantee atomic report
creation and maturity, restrict producer scope and credentials, prevent
unexpected file names and replays, and test end-to-end cancellation/timeout
recovery. Never auto-post raw Codex free text. The automatic path must not
silently bypass the controlled path's safeguards.

**Next immediate step:** P20A-3, offline structured-metadata producer/handoff
and tests. Production ERPNext is out of scope.

## Current framework baseline

Framework version:

`v1.0.0`

Initial stable release:

`2026-07-27`

Since the initial v1.0.0 release, operational hardening has continued
without changing the framework version in this roadmap.

Verified improvements now include:

-   LAN production-access design and verification
-   Correct Frappe site routing for the LAN production path
-   CI runner disk-headroom mitigation
-   Loopback-only development port configuration in tracked devcontainer
    templates
-   Repaired Synology NAS backup mount
-   Hardened four-artifact production backup workflow
-   Manual end-to-end backup validation
-   Consolidated framework, operations, recovery, and project-context
    documentation

The first unattended execution of the hardened backup job remains
pending verification.

## Near-term priorities

The next framework work should focus on operational safety and
completing recovery validation.

### Deployment safety

Planned:

-   Automatic rollback semantics with explicit database recovery
    boundaries
-   Deployment history
-   Structured deployment logging
-   Better failure/error reporting
-   Safe Docker image lifecycle cleanup

Automatic rollback must never imply automatic database rollback. Any
design must preserve the previous release/configuration, distinguish
failures before and after migration, and keep database recovery as an
explicit decision.

### Recovery maturity

Partially completed:

-   Backup verification --- manual end-to-end backup workflow verified
-   Recovery validation checklist --- documented in `recovery.md`
-   NAS mount/source validation --- implemented in the production backup
    workflow
-   Complete backup artifact validation --- implemented for database,
    site configuration, public files, and private files

Still planned:

-   Verify the first unattended 02:00 hardened backup
-   Periodic isolated restore testing
-   Measured restore-test results
-   Backup-failure alerting/monitoring
-   Recovery automation where it can be implemented safely
-   Verification of secure recovery arrangements for non-Frappe assets
    such as environment configuration and SSH keys

Backup creation and restore testing remain separate controls. Manual
backup success must not be represented as proof that a full disaster
restore has been tested.

### Application and network hardening

Planned follow-ups:

-   Verify canonical application URL behavior in a normal browser
-   Verify redirects and host/scheme normalization
-   Verify browser WebSocket behavior end-to-end
-   Review cookie and CSRF behavior
-   Review the current HSTS/plain-HTTP combination
-   Review intended LAN/VLAN segmentation
-   Consider internal HTTPS as a separate hardening project

### Development environment hardening

The tracked devcontainer configuration has been changed to bind
development port ranges to loopback.

Still pending:

-   Deliberately recreate the running devcontainer when appropriate
-   Verify the recreated container's published ports are loopback-only

Container recreation is an operational action and should not be
performed merely to update documentation.

## ERPNext business configuration

Infrastructure is sufficiently stable for normal ERPNext business
configuration to proceed in parallel with the remaining hardening work.

Recommended sequence:

1.  Company and accounting foundation
2.  Warehouses
3.  Item Groups and Units of Measure
4.  Item master data
5.  Suppliers and customers
6.  Opening stock
7.  Purchasing and receiving
8.  Stock transfers, issues, and adjustments
9.  Selling and delivery
10. Roles, permissions, and approval workflows
11. Operational reports and end-to-end testing

Do not enter material opening inventory until warehouse structure, UOM
design, item coding, valuation approach, and related accounting
configuration have been reviewed.

## Longer-term framework direction

Potential future capabilities include:

-   CI/CD integration
-   Multiple deployment environments
-   Automated release management
-   Zero-downtime deployment where justified
-   More comprehensive deployment observability
-   Automated recovery assistance
-   Notification and alerting integrations
-   Stronger GitHub repository controls if account/plan capabilities
    change

These are future capabilities, not current verified functionality.

## Guiding principles

Every framework improvement should preserve:

### Reliability

Changes must not reduce deployment reliability.

### Simplicity

Prefer small, understandable, reusable components.

### Recoverability

Production changes should preserve a known recovery path.

### Explicit production control

Code changes and production execution are separate. Deployment,
rollback, migration, restoration, destructive cleanup, and production
container recreation require explicit approval.

### Documentation

Major operational behavior should be documented without creating
unnecessary duplicate sources of truth.

### Testing

Changes should be validated before release, preferably without using
production as the test environment.

### Versioning and traceability

Stable framework releases should have appropriate Git history, release
identification, documentation updates, and changelog entries.

## Development workflow

``` text
Idea
  |
  v
Discussion / Design
  |
  v
Feature or Fix Branch
  |
  v
Implementation
  |
  v
Validation
  |
  v
Documentation
  |
  v
Pull Request / CI
  |
  v
Merge
  |
  v
Release Decision
  |
  v
Explicit Production Approval
  |
  v
Production Execution
```

Merging code is not equivalent to deploying it.

## Completion criteria

A roadmap item should move to completed status only when:

-   The implementation is complete.
-   Appropriate validation has passed.
-   Documentation reflects the verified behavior.
-   Known limitations are recorded.
-   Production execution, if required, was separately approved and
    verified.
-   The item is not relying on an unverified assumption.

## Current recommended focus

The next operational milestones are:

1.  Verify the first natural unattended hardened backup.
2.  Establish an isolated restore-test procedure.
3.  Continue application/network hardening as needed.
4.  Recreate and verify the devcontainer when operationally convenient.
5.  Begin ERPNext business configuration, starting with
    company/accounting and warehouse design.
6.  Design deployment-history/logging and safe rollback improvements as
    separate framework changes.

The framework should continue evolving incrementally, with recovery and
operator control taking priority over automation for its own sake.