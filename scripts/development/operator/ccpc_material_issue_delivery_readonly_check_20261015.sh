#!/usr/bin/env bash
# CCPC ERPNext: read-only proof of GitHub script-delivery readiness.
# New artifact for manual operator use; does not inspect or change ERPNext.
set -euo pipefail
umask 077

stop() {
  printf 'STOP: %s\n' "$1" >&2
  exit 1
}

[[ "$(id -u)" -ne 0 ]] || stop 'Run as the normal Ubuntu operator, not root.'
command -v git >/dev/null 2>&1 || stop 'Git is not available.'

export GIT_TERMINAL_PROMPT=0
export GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10'
docs_repo='git@github.com:ccpcerp/ccpc-frappe-deployment.git'
app_repo='git@github.com:ccpcerp/ccpcerp.git'
docs_ref='refs/heads/docs/ccpc-checkpoint-2026-10-10'
app_ref='refs/heads/feature/withdrawal-material-issue-safety'
expected_app='2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6'

docs_line="$(git ls-remote --refs "$docs_repo" "$docs_ref")" || stop 'Private deployment repo read failed.'
read -r docs_sha docs_returned_ref <<< "$docs_line"
[[ "$docs_sha" =~ ^[0-9a-f]{40}$ && "$docs_returned_ref" == "$docs_ref" ]] ||
  stop 'Deployment documentation ref was missing or invalid.'

app_line="$(git ls-remote --refs "$app_repo" "$app_ref")" || stop 'Private application repo read failed.'
read -r app_sha app_returned_ref <<< "$app_line"
[[ "$app_sha" == "$expected_app" && "$app_returned_ref" == "$app_ref" ]] ||
  stop 'Pinned Material Issue feature branch no longer matches the reviewed commit.'

printf '%s\n' \
  'PRIVATE GITHUB READ: PASSED' \
  'PINNED MATERIAL ISSUE SOURCE BRANCH: VERIFIED' \
  'DELIVERY PREPARATION READ-ONLY CHECK: PASSED' \
  'NO ERPNext SITE, DATABASE, DOCKER, BACKUP OR PRODUCTION OPERATION PERFORMED'
