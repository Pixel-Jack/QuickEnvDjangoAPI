# start.sh

#!/bin/bash

function manage_app () {
    python manage.py makemigrations
    python manage.py migrate
}

function collectstatic () {
    python manage.py collectstatic
}

function start_development() {
    # use django runserver as development server here.
    manage_app
    python manage.py runserver 0.0.0.0:8000
}

function start_production() {
    # use gunicorn for production server here
    manage_app
    collectstatic
    gunicorn my_project.wsgi:application -w 2 -b :8000
}

if [ ${ENVIRONMENT} == "dev" ]; then
    # use development server
    start_development
else
    # use production server
    start_production
fi