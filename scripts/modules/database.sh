# shellcheck shell=bash

###########################################
# Database Module
###########################################

###########################################
# Run Database Migrations
###########################################
run_migrations() {

  header "Run Database Migrations"

  if ! ccpc_compose exec backend \
    bench --site "$SITE_NAME" migrate; then

    restore_env
    error "Database migration failed"

  fi

  success "Database migration completed"
}
