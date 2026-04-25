#!/bin/bash

# Exit on error
set -e

# These variables should be passed via Docker Compose environment
# For api-app: DB_HOST=db-app, DB_USER=amaury, DB_NAME=footballapp_db
# For api-ml:  DB_HOST=db-ml,  DB_USER=amaury, DB_NAME=footballml_db

if [ -z "$DB_HOST" ] || [ -z "$DB_USER" ] || [ -z "$DB_NAME" ]; then
  echo "Error: DB_HOST, DB_USER and DB_NAME must be set."
  exit 1
fi

echo "Waiting for database $DB_NAME at $DB_HOST..."

# Use pg_isready (native Postgres tool) instead of netcat for more reliability
until pg_isready -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME"; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is up - executing migrations"

# Run alembic migrations
alembic upgrade head

echo "Migrations completed - starting application"

# Execute the CMD from Dockerfile
exec "$@"
