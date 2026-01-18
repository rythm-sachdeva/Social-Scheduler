#!/bin/sh

set -e

if echo "$@" | grep -q "gunicorn"; then
    echo "Running Migrations..."
    uv run manage.py makemigrations
    uv run manage.py migrate
    
    echo "Collecting Static files..."
    uv run manage.py collectstatic --noinput
fi

exec "$@"