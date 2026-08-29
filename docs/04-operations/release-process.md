# Release Process

## Purpose

This document defines the standard release process for the CCPC ERP Deployment Framework.

Every production release should follow this procedure to ensure consistency, traceability, and recoverability.

---

## Release Lifecycle

```
Development
      │
      ▼
Git Commit
      │
      ▼
Build Image
      │
      ▼
Deploy
      │
      ▼
Verify
      │
      ▼
Release Complete
```

---

## Release Principles

Every release should:

- Be reproducible.
- Be versioned.
- Be tested.
- Be documented.
- Be recoverable.

No release should bypass the deployment framework.

---

## Standard Release Procedure

### Step 1

Complete development work.

Requirements:

- All changes committed.
- Working tree clean.
- Correct Git branch.

---

### Step 2

Build a release image.

```bash
./scripts/build.sh
```

---

### Step 3

Review the generated version.

Example:

```
v16.38.0
```

---

### Step 4

Deploy the release.

```bash
./scripts/deploy.sh <image-tag>
```

Example:

```bash
./scripts/deploy.sh v16.38.0
```

---

### Step 5

Verify deployment.

Confirm:

- Containers running.
- Database migration successful.
- Health check passed.
- ERPNext accessible.

---

### Step 6

If deployment fails, execute rollback.

```bash
./scripts/rollback.sh <previous-image-tag>
```

---

## Release Checklist

Before every production release, confirm:

- [ ] Framework repository is up to date.
- [ ] Git working tree is clean.
- [ ] Docker image built successfully.
- [ ] Deployment completed successfully.
- [ ] Database migration completed.
- [ ] Health check passed.
- [ ] Rollback image available.
- [ ] Documentation updated if required.
