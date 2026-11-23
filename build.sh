#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
# Con disco persistente (SQLITE_PATH) el disco no existe durante el build:
# las migraciones las corre start.sh al arrancar.
if [ -z "${SQLITE_PATH:-}" ]; then
  python manage.py migrate
fi
