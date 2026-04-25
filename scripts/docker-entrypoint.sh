#!/bin/bash

# Exit on error
set -e

# These variables should be passed via Docker Compose environment
# For api-app: DB_HOST=db-app, DB_PORT=5432
# For api-ml:  DB_HOST=db-ml,  DB_PORT=5432

if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ]; then
  echo "Error: DB_HOST and DB_PORT must be set."
  exit 1
fi

echo "Waiting for database at $DB_HOST:$DB_PORT..."

# Use netcat to check if the port is open
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "Database is up - executing migrations"

# Run alembic migrations
# Ensure we are in the correct directory if needed, 
# though Dockerfile WORKDIR should handle it.
alembic upgrade head

echo "Migrations completed - starting application"

# Execute the CMD from Dockerfile
exec "$@"
