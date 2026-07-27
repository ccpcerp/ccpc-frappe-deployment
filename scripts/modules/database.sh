#!/bin/bash

###########################################
# Database Module
###########################################


###########################################
# Run Database Migrations
###########################################
run_migrations() {

    header "Run Database Migrations"

    if ! docker compose exec backend \
        bench --site "$SITE_NAME" migrate; then

        restore_env
        error "Database migration failed"

    fi

    success "Database migration completed"
}

