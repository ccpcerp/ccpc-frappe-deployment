# CCPC ERP Codex Engineering Guide

## Project Purpose

This repository contains the CCPC ERP deployment and operations framework for ERPNext/Frappe.

The framework is designed for:

- Reliability
- Maintainability
- Recoverability
- Predictability
- Simplicity
- Reusability
- Documentation-first operations

## Architecture

Preserve the existing layered architecture.

### Layer 1: Top-Level Commands

Examples:

- scripts/build.sh
- scripts/deploy.sh
- scripts/rollback.sh

Responsibilities:

- Validate input
- Coordinate workflows
- Report results

Do not place complex operational logic directly in top-level scripts.

### Layer 2: Workflow Modules

Example:

- scripts/modules/deployment.sh

Responsibilities:

- Coordinate reusable operational steps
- Reuse operational modules
- Avoid duplicate workflow implementations

### Layer 3: Operational Modules

Examples:

- scripts/modules/docker.sh
- scripts/modules/database.sh
- scripts/modules/env.sh
- scripts/modules/git.sh
- scripts/modules/health.sh
- scripts/modules/version.sh

Responsibilities:

- Perform one clearly defined task
- Remain reusable
- Avoid unrelated responsibilities

## Configuration

Central framework configuration belongs in:

scripts/config.sh

Do not hard-code environment-specific values in operational modules when a centralized configuration value is appropriate.

## Engineering Rules

Prefer simple, readable solutions over clever ones.

Follow single-responsibility design.

Avoid duplicate implementations.

Reuse existing functions before introducing new ones.

Keep top-level scripts small.

Preserve backwards compatibility unless a change explicitly requires otherwise.

Do not silently change release or deployment behavior.

Document all production-impacting changes.

## Bash Standards

Use:

set -euo pipefail

for top-level executable scripts where appropriate.

Quote shell variables unless intentional word splitting is required.

Check command failure explicitly where recovery behavior is needed.

Prefer functions with clear responsibilities.

Avoid destructive shell commands unless explicitly required and approved.

Use ShellCheck-compatible patterns where practical.

## Git Safety

Do not:

- force-push
- rewrite published history
- delete branches or tags without approval
- reset working trees destructively
- discard uncommitted work
- modify repository remotes without approval
- commit credentials or secrets

Before proposing a commit:

1. Review git status.
2. Review git diff.
3. Run appropriate validation.
4. Summarize the changes.

Do not push unless explicitly requested.

## Secrets and Credentials

Never print, expose, copy, commit, or modify:

- .env secrets
- passwords
- API keys
- GitHub tokens
- SSH private keys
- database credentials
- recovery codes
- administrator credentials

Treat .env as sensitive.

Do not add secrets to logs or documentation.

## Docker Safety

Do not run destructive Docker operations without explicit approval.

This includes:

- docker compose down -v
- docker volume rm
- docker system prune
- docker image prune
- deleting production images
- deleting production containers
- deleting persistent volumes

Image cleanup must preserve rollback images according to the release policy.

## Database Safety

Treat database operations as production-sensitive.

Do not:

- drop databases
- drop sites
- restore backups
- modify production data directly
- run destructive SQL
- change MariaDB configuration

without explicit approval.

Database migrations are potentially production-impacting.

Before changing migration behavior, explain:

- expected effect
- rollback implications
- failure handling

## Deployment Safety

Never execute a production deployment or rollback unless the user explicitly requests it.

Commands such as:

./scripts/deploy.sh
./scripts/rollback.sh

require explicit approval.

Before a production deployment, verify:

- repository state
- target image
- configuration backup
- rollback image availability
- expected migration behavior

Do not bypass the deployment framework with manual production changes unless explicitly directed.

## Failure Handling

Prefer fail-safe behavior.

When modifying deployment code, consider:

- configuration restoration
- container state
- database migration failure
- health-check failure
- rollback target
- logging
- recoverability

Do not assume restoring .env alone restores the previous operational state.

## Testing and Validation

Before considering a change complete, run the most appropriate available validation.

Examples:

- bash -n
- shellcheck
- targeted unit/integration tests
- git diff review

Do not claim tests passed unless they were actually executed.

If required tools are unavailable, state that clearly.

## Documentation

Documentation is part of the implementation.

Update relevant documentation when changing:

- architecture
- deployment behavior
- rollback behavior
- recovery procedures
- configuration
- release process
- operational workflows

Keep CHANGELOG and release documentation aligned with stable releases.

## Codex Workflow

For significant changes:

1. Analyze the existing implementation.
2. Explain the current behavior.
3. Identify risks and dependencies.
4. Propose a change plan.
5. Wait for approval if the change is architectural, destructive, production-impacting, or broad.
6. Implement the approved scope only.
7. Run validation.
8. Show the final diff and summarize the result.

Do not introduce unrelated refactors while implementing a focused change.

## Preferred Development Workflow

Use:

Issue or requirement
    -> analysis
    -> feature branch
    -> implementation
    -> validation
    -> pull request
    -> review
    -> merge
    -> build
    -> staging verification
    -> production deployment
    -> release

Production changes should be traceable and reversible.

## Current Framework Direction

The next framework improvements should prioritize operational safety, including:

- automatic rollback
- deployment history
- deployment logging
- image cleanup
- better error reporting
- stronger validation

Any implementation should preserve the existing modular architecture.
