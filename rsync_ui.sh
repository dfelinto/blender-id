
ROOT="$(dirname "$(readlink -f "$0")")"

APP="blender-id"
ASSETS="$ROOT/$APP/application/static/assets/"
TEMPLATES="$ROOT/$APP/application/templates/"
WEBROOT="/data/www/vhosts/www.blender.org/id"

cd $ROOT
if [ $(git rev-parse --abbrev-ref HEAD) != "production" ]; then
    echo "You are NOT on the production branch, refusing to rsync_ui." >&2
    exit 1
fi

echo "\n *** GULPA GULPA ***\n"
if [ -x ./node_modules/.bin/gulp ]; then
    ./node_modules/.bin/gulp
else
    gulp
fi

echo "\n *** SYNCING ASSETS ***\n"
rsync -avh $ASSETS borg@www.blender.org:$WEBROOT/$APP/application/static/assets/

echo "\n *** SYNCING TEMPLATES *** \n"
rsync -avh $TEMPLATES borg@www.blender.org:$WEBROOT/$APP/application/templates/

