#!/bin/sh

set -e

if echo "$@" | grep -q "gunicorn"; then
    echo "Running Migrations..."
    python manage.py makemigrations
    python manage.py migrate

    echo "Collecting Static files..."
    python manage.py collectstatic --noinput
fi

exec "$@"