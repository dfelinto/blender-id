#!/bin/bash -e

# Deploys the current production branch to the production machine.
PROJECT_NAME="blender-id"
REMOTE_ROOT="/data/www/vhosts/www.blender.org/id/"

SSH="ssh -o ClearAllForwardings=yes borg@www.blender.org"
ROOT="$(dirname "$(readlink -f "$0")")"
cd ${ROOT}

# Check that we're on production branch.
if [ $(git rev-parse --abbrev-ref HEAD) != "production" ]; then
    echo "You are NOT on the production branch, refusing to deploy." >&2
    exit 1
fi

# Check that production branch has been pushed.
if [ -n "$(git log origin/production..production --oneline)" ]; then
    echo "WARNING: not all changes to the production branch have been pushed."
    echo "Press [ENTER] to continue deploying current origin/production, CTRL+C to abort."
    read dummy
fi

# SSH to cloud to pull all files in
echo "==================================================================="
echo "UPDATING FILES ON ${PROJECT_NAME}"
${SSH} git -C ${REMOTE_ROOT} fetch origin production
${SSH} git -C ${REMOTE_ROOT} log origin/production..production --oneline
${SSH} git -C ${REMOTE_ROOT} merge --ff-only origin/production

# RSYNC the UI
./rsync_ui.sh

# Update the virtualenv
${SSH} -t /data/www/vhosts/www.blender.org/id/venv/bin/pip install -U -r ${REMOTE_ROOT}/requirements.txt --exists-action w

# Notify Bugsnag of this new deploy.
echo
echo "==================================================================="
GIT_REVISION=$(${SSH} git -C ${REMOTE_ROOT} describe --always)
echo "Notifying Bugsnag of this new deploy of revision ${GIT_REVISION}."
BUGSNAG_API_KEY=$(${SSH} python -c "\"import sys; sys.path.append('${REMOTE_ROOT}/${PROJECT_NAME}'); import config_local; print(config_local.BUGSNAG_API_KEY)\"")
curl --data "apiKey=${BUGSNAG_API_KEY}&revision=${GIT_REVISION}" https://notify.bugsnag.com/deploy
echo

# Wait for [ENTER] to restart the server
echo
echo "==================================================================="
echo "NOTE: If you want to edit config_local.py on the server, do so now."
echo "NOTE: Press [ENTER] to continue and gracefully restart the server."
read dummy
${SSH} sudo apachectl graceful

echo "Server process restarted"
echo
echo "==================================================================="
echo "Deploy of ${PROJECT_NAME} is done."
echo "==================================================================="
