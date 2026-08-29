# Deployment Guide

## Purpose

This guide describes the standard deployment process for the CCPC ERP Deployment Framework.

It should be used for every production deployment.

---

## Deployment Workflow

The deployment process follows this sequence.

```
Build Image
      │
      ▼
Verify Image
      │
      ▼
Backup Configuration
      │
      ▼
Deploy Containers
      │
      ▼
Run Database Migrations
      │
      ▼
Health Check
      │
      ▼
Deployment Complete
```

---

## Prerequisites

Before deploying, verify the following.

- Ubuntu Server is running.
- Docker services are operational.
- Git working tree is clean.
- Latest application changes have been committed.
- Framework version is current.

---

## Standard Deployment Procedure

### Step 1

Build a new Docker image.

```bash
./scripts/build.sh
```

---

### Step 2

Review the generated image version.

Example:

```
v16.37.0
```

---

### Step 3

Deploy the selected image.

```bash
./scripts/deploy.sh <image-tag>
```

Example:

```bash
./scripts/deploy.sh v16.37.0
```

---

### Step 4

Verify successful deployment.

Expected checks include:

- Docker containers are running.
- Database migration completed.
- ERPNext health check passed.
- Application is accessible.

---

## Rollback Procedure

If a deployment fails after release, perform a rollback.

### Step 1

Identify the previous working image.

Example:

```
v16.36.0
```

---

### Step 2

Execute the rollback.

```bash
./scripts/rollback.sh <image-tag>
```

Example:

```bash
./scripts/rollback.sh v16.36.0
```

---

### Step 3

Verify recovery.

Confirm:

- Containers are running.
- Database migration completed.
- ERPNext is accessible.
- Users can log in successfully.
