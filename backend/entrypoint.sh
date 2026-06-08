#!/bin/sh
set -e

export FLASK_APP=manage.py

python wait_for_db.py
flask db upgrade
python seed.py

exec "$@"
