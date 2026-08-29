# shellcheck shell=bash

###########################################
# Git Module
###########################################

###########################################
# Verify Git Status
###########################################
verify_git_status() {

  header "Git Status"

  cd "$APP_PATH" || return 1

  if [ -n "$(git status --porcelain)" ]; then
    error "Working tree is not clean. Commit or stash your changes."
  fi

  success "Working tree is clean"

  CURRENT_BRANCH=$(git branch --show-current)

  if [ "$CURRENT_BRANCH" != "$APP_BRANCH" ]; then
    error "Current branch is '$CURRENT_BRANCH'. Expected '$APP_BRANCH'."
  fi

  success "Branch verified ($CURRENT_BRANCH)"

  git fetch origin >/dev/null 2>&1

  LOCAL=$(git rev-parse HEAD)
  REMOTE=$(git rev-parse "origin/$APP_BRANCH")

  if [ "$LOCAL" != "$REMOTE" ]; then
    error "Local branch is not synchronized with origin/$APP_BRANCH"
  fi

  success "GitHub is up to date"

  # shellcheck disable=SC2103  # Restore the caller's directory in this sourced module.
  cd - >/dev/null || return 1
}
