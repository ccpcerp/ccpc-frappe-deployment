# Recovery Guide

## Purpose

This document describes the procedures required to recover the CCPC ERP deployment environment after a failure.

Recovery scenarios include:

- Complete server loss
- Disk failure
- Operating system corruption
- Docker configuration loss
- ERPNext deployment recovery
- Framework recovery

The objective is to restore the deployment environment safely and consistently.

---

## Recovery Priorities

Recovery should always follow this order.

1. Restore the operating system.
2. Restore the deployment framework.
3. Restore Docker configuration.
4. Restore ERPNext database.
5. Restore uploaded files.
6. Verify ERPNext operation.


---

## Recovery Assets

The following assets are required to fully restore the CCPC ERP environment.

### Operating System

- Ubuntu Server

---

### Deployment Framework

- Git repository
- Build scripts
- Deployment scripts
- Rollback scripts
- Framework documentation

---

### Docker Configuration

- compose.yaml
- apps.json
- example.env
- .env
- Docker images

---

### ERPNext Application

- Custom application source code
- Git repository
- Application branch

---

### ERPNext Data

- MariaDB database
- Public files
- Private files

---

### Infrastructure

- DNS configuration
- Network configuration
- Firewall rules

---

### Credentials

- GitHub credentials
- Docker credentials
- ERPNext Administrator account
- MariaDB credentials
- SSH keys




---

## Recovery Locations

The following table identifies the primary and backup locations for all critical assets.

| Asset | Primary Location | Backup Location | Status |
|--------|------------------|-----------------|--------|
| Deployment Framework | GitHub (ccpc-frappe-deployment) | Ubuntu Server | Active |
| ERPNext Application | Git Repository | Ubuntu Server | Active |
| Docker Configuration | Ubuntu Server | Git Repository | Active |
| Docker Images | Local Docker | Rebuild from source | Active |
| MariaDB Database | Ubuntu Server | Synology NAS | Verify Regularly |
| Public Files | Ubuntu Server | Synology NAS | Verify Regularly |
| Private Files | Ubuntu Server | Synology NAS | Verify Regularly |
| Environment Configuration (.env) | Ubuntu Server | Secure Backup | Verify Regularly |
| SSH Keys | Administrator Workstation | Secure Backup | Verify Regularly |
| Documentation | GitHub Repository | Ubuntu Server | Active |


---

## Recovery Time Objectives

| Recovery Scenario | Target Recovery Time |
|-------------------|---------------------:|
| Framework Recovery | 30 minutes |
| Docker Environment Recovery | 1 hour |
| ERPNext Application Recovery | 1 hour |
| Database Restore | 30 minutes |
| Complete Server Recovery | 4 hours |

Recovery times are targets and should be reviewed periodically based on operational experience.
