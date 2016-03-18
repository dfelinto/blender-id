#!/usr/bin/env bash -e

. /data/venv/bin/activate

# We have to be in the correct directory for Alembic to find its ini file.
cd /data/git/blender-id/blender-id
python ./manage.py "$@"
