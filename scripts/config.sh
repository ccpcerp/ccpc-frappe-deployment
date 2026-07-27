#!/bin/bash

###########################################
# Framework
###########################################

FRAMEWORK_NAME="CCPC ERP Deployment Framework"
FRAMEWORK_VERSION="1.0.0"

###########################################
# CCPC ERP Release Configuration
###########################################

# Git
APP_BRANCH="version-16"
RELEASE_PREFIX="v16"
APP_PATH="development/frappe-bench/apps/ccpcerp"

# Docker
IMAGE_NAME="ccpcerp"
DOCKERFILE="images/custom/Containerfile"

# ERPNext
SITE_NAME="ccpcerp.local"

# Build logs
LOG_DIR="logs"

# Directories
LOG_DIR="logs"
BACKUP_DIR="backups"

# Timing
SERVICE_STARTUP_WAIT=10
