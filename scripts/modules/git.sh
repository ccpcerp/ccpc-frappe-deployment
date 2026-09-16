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

  if ! REMOTE_TAG_REFS="$(
    git ls-remote origin "refs/tags/$CCPC_REF" "refs/tags/$CCPC_REF^{}"
  )"; then
    error "Unable to query origin for frozen CCPC release $CCPC_REF"
  fi

  REMOTE_CCPC_SHA="$(
    printf '%s\n' "$REMOTE_TAG_REFS" |
      awk '/\^\{\}$/ {print $1; exit}'
  )"

  if [ -z "$REMOTE_CCPC_SHA" ]; then
    REMOTE_CCPC_SHA="$(
      printf '%s\n' "$REMOTE_TAG_REFS" |
        awk 'NR == 1 {print $1}'
    )"
  fi

  if [ -z "$REMOTE_CCPC_SHA" ]; then
    error "Frozen CCPC release $CCPC_REF was not found on origin"
  fi

  if [ "$REMOTE_CCPC_SHA" != "$CCPC_SHA" ]; then
    error "Frozen CCPC release $CCPC_REF does not match approved commit $CCPC_SHA"
  fi

  success "Frozen CCPC release verified ($CCPC_REF @ $CCPC_SHA)"

  # shellcheck disable=SC2103  # Restore the caller's directory in this sourced module.
  cd - >/dev/null || return 1
}
