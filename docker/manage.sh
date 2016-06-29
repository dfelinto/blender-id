#!/usr/bin/env bash -e

# We have to be in the correct directory for Alembic to find its ini file.
cd /data/git/blender-id/blender-id

. /data/venv/bin/activate && python manage.py "$@"
