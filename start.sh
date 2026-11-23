#!/usr/bin/env bash
# Inicio en Render cuando la base vive en un disco persistente (SQLITE_PATH).
# El disco no esta montado durante el build, por eso las migraciones corren
# aqui y no en build.sh. Start Command en Render: bash start.sh
set -o errexit
python manage.py migrate --no-input
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-10000}"
