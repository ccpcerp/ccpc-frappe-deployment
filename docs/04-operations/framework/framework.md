# CCPC ERP Deployment Framework

Version: 1.0.0

## Overview

The CCPC ERP Deployment Framework provides a structured and repeatable process for building, deploying, and rolling back custom ERPNext Docker images.

It is designed around reusable modules so that deployment workflows remain simple, maintainable, and easy to extend.

## Directory Structure

```
scripts/
│
├── build.sh
├── deploy.sh
├── rollback.sh
├── config.sh
├── lib.sh
│
└── modules/
    ├── database.sh
    ├── deployment.sh
    ├── docker.sh
    ├── env.sh
    ├── git.sh
    ├── health.sh
    └── version.sh
```

## Script Responsibilities

### build.sh

Builds a new Docker image for the CCPC ERP application.

### deploy.sh

Deploys a selected Docker image to the ERPNext environment.

### rollback.sh

Rolls back the ERPNext environment to a previously built Docker image.

## Framework Architecture

The deployment framework is organized into three layers.

```
                build.sh
                deploy.sh
               rollback.sh
                     │
                     ▼
          Reusable Workflow Modules
                     │
                     ▼
      Reusable Operations (Docker, Git,
      Environment, Database, Health)
```

The top-level scripts are intentionally small.

Each script coordinates reusable modules rather than implementing deployment logic directly.

This architecture reduces code duplication and makes future enhancements easier to implement and maintain.

## Module Responsibilities

### config.sh

Contains framework configuration values including:

- Framework information
- Application configuration
- Docker image names
- Site configuration
- Directory locations
- Timeouts

---

### lib.sh

Provides common utility functions used throughout the framework.

Examples include:

- banner()
- header()
- info()
- success()
- warn()
- error()
- verify_project_directory()
- print_configuration()
- verify_git_repository()

---

### git.sh

Provides Git-related operations.

Responsibilities include:

- Verify working tree
- Verify current branch
- Verify synchronization with GitHub

---

### version.sh

Handles release version management.

Responsibilities include:

- Detect current release
- Calculate next release version
- Verify version availability

---

### docker.sh

Provides Docker-related operations.

Responsibilities include:

- Build Docker images
- Verify Docker images
- Deploy containers
- Wait for services
- Verify running containers

---

### env.sh

Manages deployment configuration.

Responsibilities include:

- Backup .env
- Update image tag
- Restore configuration

---

### database.sh

Provides ERPNext database operations.

Responsibilities include:

- Run database migrations

---

### health.sh

Performs post-deployment verification.

Responsibilities include:

- Verify ERPNext HTTP response

---

### deployment.sh

Provides reusable deployment workflows.

Responsibilities include:

- Deploy a release using reusable framework modules

## Build Workflow

The build process creates a new Docker image for deployment.

```
Start
  │
  ▼
Verify Project Directory
  │
  ▼
Print Configuration
  │
  ▼
Verify Git Repository
  │
  ▼
Verify Git Status
  │
  ▼
Detect Current Version
  │
  ▼
Calculate Next Version
  │
  ▼
Verify Version Availability
  │
  ▼
Build Docker Image
  │
  ▼
Verify Image
  │
  ▼
Finish
```

### Build Sequence

1. Verify the current project directory.
2. Display framework configuration.
3. Verify the Git repository.
4. Ensure the working tree is clean.
5. Confirm the correct Git branch.
6. Verify synchronization with GitHub.
7. Detect the current release version.
8. Calculate the next release version.
9. Ensure the target version does not already exist.
10. Build the Docker image.
11. Verify the newly created image.

## Deployment Workflow

The deployment process installs a selected Docker image into the ERPNext environment.

```
Start
  │
  ▼
Verify Project Directory
  │
  ▼
Print Configuration
  │
  ▼
Verify Arguments
  │
  ▼
Verify Docker Image
  │
  ▼
Deploy Release
  │
  ▼
Deployment Summary
  │
  ▼
Finish
```

### Deploy Release Workflow

The reusable deployment workflow performs the following operations.

```
Backup .env
    │
    ▼
Update .env
    │
    ▼
Deploy Containers
    │
    ▼
Wait for Services
    │
    ▼
Verify Containers
    │
    ▼
Run Database Migrations
    │
    ▼
Health Check
```

## Rollback Workflow

The rollback process restores a previously built Docker image using the same deployment workflow as a normal deployment.

```
Start
  │
  ▼
Verify Project Directory
  │
  ▼
Print Configuration
  │
  ▼
Verify Arguments
  │
  ▼
Verify Docker Image
  │
  ▼
Deploy Release
  │
  ▼
Rollback Summary
  │
  ▼
Finish
```

### Rollback Process

The rollback workflow does not contain a separate deployment implementation.

Instead, it reuses the common deployment workflow.

```
rollback.sh
      │
      ▼
deploy_release()
      │
      ▼
Backup .env
Update .env
Deploy Containers
Wait for Services
Verify Containers
Run Database Migrations
Health Check
```

This design guarantees that deployment and rollback always follow the same operational steps, reducing maintenance effort and eliminating duplicate deployment logic.

## Configuration

Framework configuration is centralized in `scripts/config.sh`.

Configuration includes:

- Framework information
- Docker image name
- Application branch
- ERPNext site name
- Dockerfile location
- Project directories
- Deployment timeouts

Changing framework behavior should normally require updating only this file rather than modifying deployment scripts.

## Versioning

Docker images follow semantic versioning.

Example:

```
v16.30.0
v16.31.0
v16.32.0
```

During the build process the framework:

1. Detects the latest available release.
2. Calculates the next release version.
3. Verifies that the version does not already exist.
4. Builds the new Docker image.

## Framework Roadmap

### Version 1.0

The initial framework provides:

- Modular architecture
- Docker image build automation
- Deployment automation
- Rollback automation
- Database migration support
- Health verification
- Centralized configuration
- Reusable deployment workflow

---

### Planned Enhancements

Future versions may include:

- Automatic rollback on deployment failure
- Release history logging
- Git tag creation
- Docker image cleanup
- Backup verification
- Disaster recovery automation
- Deployment notifications
- CI/CD integration

---

## Design Principles

The framework follows these principles.

### Single Responsibility

Each module has one responsibility.

Examples:

- Docker operations
- Database operations
- Health verification
- Environment management

---

### Reusability

Reusable functions should exist only once.

Deployment and rollback should reuse the same workflow whenever possible.

---

### Maintainability

Top-level scripts should coordinate workflows rather than implement deployment logic directly.

---

### Safety

The framework should verify operations before making changes whenever possible.

Examples include:

- Verify project directory
- Verify Git status
- Verify Docker image
- Backup configuration before deployment
- Verify health after deployment

---

### Simplicity

Each script should remain small, readable, and easy to understand.

Complex logic belongs inside reusable modules rather than top-level scripts.
