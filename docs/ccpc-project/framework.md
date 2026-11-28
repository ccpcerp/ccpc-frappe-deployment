# CCPC ERP Deployment Framework

*Last updated: 2026-09-02*

## Purpose

The CCPC ERP Deployment Framework provides a structured, repeatable, and
recoverable process for building, deploying, verifying, and rolling back
the CCPC ERPNext environment.

This document is the consolidated reference for:

-   Framework architecture
-   Engineering principles
-   Component responsibilities
-   Build, deployment, and rollback design
-   Configuration and versioning concepts
-   Safety and maintainability principles
-   Framework evolution

Detailed production procedures belong in the operations documentation,
while current environment-specific facts and verified operational state
belong in `ccpc-project-context.md`.

## Mission

Build and maintain a deployment framework that is:

-   Reliable
-   Maintainable
-   Recoverable
-   Predictable
-   Reusable
-   Easy to understand

The framework should reduce operational risk rather than increase it.

## Architecture goals

The framework is designed around:

-   Reliability
-   Simplicity
-   Single responsibility
-   Reusability
-   Testability
-   Recoverability
-   Documentation
-   Reversible production operations

## High-level architecture

``` text
                 Operator
                    |
                    v
       build.sh / deploy.sh / rollback.sh
                    |
                    v
          Reusable Workflow Modules
                    |
                    v
          Operational Modules
                    |
                    v
   Docker / Git / Environment / Database /
        Health / Version / Configuration
```

Top-level commands coordinate workflows.

Reusable workflow modules coordinate operational steps.

Operational modules implement focused capabilities.

This layered structure reduces duplication and allows individual
components to evolve without turning the top-level scripts into large
monolithic programs.

## Framework layers

### Layer 1 --- top-level commands

Primary entry points:

-   `scripts/build.sh`
-   `scripts/deploy.sh`
-   `scripts/rollback.sh`

Responsibilities:

-   Validate operator input.
-   Establish the requested workflow.
-   Call reusable framework functions.
-   Report the final result.

Top-level scripts should remain small and should not duplicate
operational logic.

### Layer 2 --- workflow modules

Primary example:

-   `scripts/modules/deployment.sh` or the repository's current
    equivalent deployment workflow module

Responsibilities:

-   Coordinate reusable operational steps.
-   Define the sequence required for a deployment or rollback.
-   Keep deployment behavior consistent between top-level commands.

Deployment and rollback should reuse common workflow logic wherever
their operational behavior is intentionally the same.

### Layer 3 --- operational modules

The framework uses focused modules for responsibilities such as:

-   Docker operations
-   Database operations
-   Environment/configuration handling
-   Health verification
-   Git validation
-   Release/version handling

Each module should have one clearly defined responsibility.

## Configuration

Framework configuration is centralized rather than scattered through
top-level scripts.

Important concepts include:

-   Application branch
-   Release prefix
-   Custom application path
-   Docker image name
-   Containerfile location
-   Internal Frappe site name
-   Deployment timing/settings
-   Intended application endpoint
-   Compose configuration used for the CCPC environment

Current environment-specific values should be verified against the
repository and `ccpc-project-context.md` rather than inferred from an
older documentation snapshot.

This distinction is important because Project Source copies of scripts
may lag behind the live Git repository.

## Build workflow

The build workflow is responsible for producing a verified CCPC ERP
Docker image.

Conceptually:

``` text
Start
  |
  v
Verify Project
  |
  v
Verify Git State
  |
  v
Determine Release Version
  |
  v
Build Docker Image
  |
  v
Verify Image
  |
  v
Finish
```

A build should:

1.  Verify that it is running from the expected project.
2.  Verify the required Git/application repository state.
3.  Confirm the expected application branch.
4.  Verify synchronization requirements.
5.  Determine the release version according to the framework's current
    versioning implementation.
6.  Ensure the target image/version does not conflict with an existing
    release.
7.  Build the image.
8.  Verify that the resulting image exists and is usable for the next
    stage.

Building an image does not itself authorize deployment to production.

## Deployment workflow

A deployment installs a selected application image into the ERPNext
environment.

Conceptually:

``` text
Verify Request
      |
      v
Verify Image
      |
      v
Preserve Configuration
      |
      v
Apply Release Configuration
      |
      v
Deploy Containers
      |
      v
Verify Containers
      |
      v
Database Migration
      |
      v
Application Health Check
      |
      v
Deployment Complete
```

Production deployment is a production-impacting operation and requires
explicit operator approval.

The exact Compose invocation, endpoint, routing configuration, and
environment behavior must come from the current Git repository and
current project context---not from stale documentation examples.

## Rollback workflow

Rollback should reuse the deployment framework rather than maintain a
separate duplicate implementation.

Conceptually:

``` text
Select Previous Release
        |
        v
Verify Release Image
        |
        v
Shared Deployment Workflow
        |
        v
Verify Recovered Application
```

Reusing the common workflow provides consistent behavior and reduces
maintenance.

However, application rollback and database rollback are not equivalent.

A container/image rollback must not automatically be treated as a
database rollback. Database migrations may require a separate recovery
decision. Automatic rollback design must therefore preserve explicit
database-recovery boundaries.

Production rollback requires explicit operator approval.

## Health verification

Post-deployment health verification should prove that the intended CCPC
ERP application is responding through the intended routing path.

A health check should not merely prove that some HTTP service answered.

It should account for:

-   Intended host-published port
-   Intended Frappe site routing
-   Correct application endpoint
-   Container health/running state where applicable
-   Backend availability

Current endpoint details belong in `ccpc-project-context.md` and the
current Git implementation.

## Database operations

Database migration is a production-impacting operation.

Framework database functions should:

-   Target the intended Frappe site.
-   Fail clearly when migration fails.
-   Preserve recoverability.
-   Avoid hiding errors.
-   Never imply that reversing an application image automatically
    reverses database schema/data changes.

Database restore, destructive database operations, and migrations
require explicit approval.

## Environment handling

Deployment configuration should be preserved before modification when
practical.

Environment-handling logic should:

-   Verify required configuration exists.
-   Preserve the previous deployable state.
-   Make narrowly scoped changes.
-   Verify the requested change took effect.
-   Restore configuration when a safely reversible failure path supports
    doing so.
-   Never expose secrets in logs or documentation.

`.env`, credentials, tokens, passwords, private keys, NAS credentials,
and similar secret material must not be committed to Git or copied into
project documentation.

## Git principles

Git is the authoritative source for tracked deployment-framework code.

The framework should favor:

-   Clean working state before releases.
-   Feature/fix branches for tracked changes.
-   Pull requests into `main`.
-   CI validation before merge.
-   Traceable commits.
-   Stable release points.
-   Preservation of the upstream Frappe remote.
-   No force-push or destructive manipulation of stable branches as
    normal practice.

The private CCPC deployment repository is the authoritative source for
CCPC-specific tracked framework code.

Uploaded Project Source script copies are reference snapshots only and
can become stale. They must not override a newer verified Git state.

## Engineering standards

### Simplicity

Prefer straightforward solutions over clever ones.

Readable and auditable code is more valuable than minimizing line count.

### Single responsibility

Each module should have one primary responsibility.

Examples include:

-   Docker
-   Database
-   Environment
-   Health
-   Git
-   Versioning

### Reusability

If multiple workflows need the same operational behavior, implement that
behavior once and reuse it.

Deployment and rollback should share common workflow code where
appropriate.

### Testability

Significant framework changes should be validated before release.

Validation should be appropriate to the changed component and should
avoid using production as an unnecessary test environment.

### Documentation

Documentation is part of the framework.

Major production-facing behavior should be documented, but documentation
should avoid duplicating volatile implementation details unnecessarily.

### Recoverability

Production changes should preserve a known recovery path.

A successful change is not fully operationally safe if there is no
understood way to recover from failure.

### Explicit production control

Code merge and production execution are separate actions.

Merging deployment code does not authorize:

-   Deployment
-   Rollback
-   Database migration
-   Database restoration
-   Destructive Docker cleanup
-   Production container recreation
-   Destructive backup cleanup

These actions require explicit operator approval.

## Safety principles

The framework should verify conditions before making changes whenever
practical.

Examples:

-   Verify project/repository context.
-   Verify Git state.
-   Verify requested image.
-   Preserve configuration before modification.
-   Verify containers after deployment.
-   Verify application health.
-   Fail rather than silently ignore critical errors.

Error handling should favor a clear failure over a false-success state.

## Source-of-truth model

The project deliberately separates different kinds of authoritative
information.

### Git repository

Authoritative for:

-   Tracked scripts
-   Compose files and overrides
-   CI configuration
-   Version-controlled documentation
-   Application source
-   Deployment-framework implementation

### Production server and NAS

Authoritative for live operational state such as:

-   Running containers
-   Active mounts
-   Current cron configuration
-   Live logs
-   Existing backup files
-   Current host/network state

### `ccpc-project-context.md`

Authoritative Project Source summary for:

-   Verified current state
-   Important infrastructure decisions
-   Known pending validations
-   Protected local state
-   Operational safety boundaries
-   Current work and roadmap context

### `recovery.md`

Authoritative recovery procedure for:

-   Backup expectations
-   NAS recovery
-   Disaster recovery
-   Restore principles
-   Recovery validation

Project Sources should provide concise, useful context rather than
become an uncontrolled duplicate of the entire Git repository.

## Documentation organization

The preferred consolidated documentation model is:

-   `ccpc-project-context.md` --- current verified project/environment
    state
-   `framework.md` --- architecture and engineering principles
-   `operations.md` --- release, deployment, rollback, and routine
    operational procedures
-   `recovery.md` --- backup and disaster-recovery procedures
-   `roadmap.md` --- future work
-   `changelog.md` --- release/change history, if retained separately

This reduces overlapping documents while keeping each document's
responsibility clear.

## Framework evolution

The framework should evolve through focused, reusable components rather
than increasingly large top-level scripts.

Potential future capabilities include:

-   Improved deployment history/logging
-   Automatic rollback with explicit database boundaries
-   Better error reporting
-   Image lifecycle/cleanup controls
-   Backup verification integration
-   Recovery automation
-   Notifications
-   CI/CD integration
-   Multiple environments
-   Zero-downtime deployment where justified

New capabilities should not weaken the core architecture or bypass
safety controls.

## Change criteria

A framework improvement should normally satisfy these questions before
it is considered complete:

1.  Is the design understandable?
2.  Is operational logic placed in the appropriate module?
3.  Does it avoid unnecessary duplication?
4.  Does it preserve or improve recoverability?
5.  Are failure paths understood?
6.  Has appropriate validation been performed?
7.  Is documentation updated where necessary?
8.  Is the change traceable in Git?
9.  Does any production execution remain separately controlled?

## Long-term vision

The CCPC ERP Deployment Framework should remain a small, understandable
operations platform around ERPNext rather than become an opaque
automation layer.

Automation should increase consistency and safety while preserving
operator visibility and control.

Reliability, simplicity, maintainability, and recoverability remain the
primary architectural priorities.