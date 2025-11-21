#!/bin/sh
set -o errexit
set -o pipefail

if [ -n "$GOOGLE_OAUTH2_TOKEN_B64" ]; then
    TOKEN_PATH=${GOOGLE_OAUTH2_TOKEN_STORAGE:-/app/users/oauth/token.pkl}
    mkdir -p "$(dirname "$TOKEN_PATH")"
    echo "$GOOGLE_OAUTH2_TOKEN_B64" | base64 -d > "$TOKEN_PATH"
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"