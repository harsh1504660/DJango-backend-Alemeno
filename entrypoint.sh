#!/bin/sh

# Create migration files (only first time, safe if repeated)
python manage.py makemigrations loans --noinput

# Apply migrations to create tables
python manage.py migrate --noinput

# Ingest data (safe to rerun, skips/updates existing)
python manage.py ingest_data || true

# Collect static files (optional)
python manage.py collectstatic --noinput || true

# Start Gunicorn server
exec gunicorn credit_system.wsgi:application --bind 0.0.0.0:8000
