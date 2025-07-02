#!/usr/bin/env bash

set -e

echo "Run apply migrations.."
alembic -c fastapi_application/alembic.ini upgrade head
echo "Migrations applied!"

exec "$@"