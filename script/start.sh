#!/bin/sh

function manage_app () {
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    django-admin compilemessages
}

function collectstatic () {
    python manage.py collectstatic --noinput
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
    gunicorn YOUR_PROJECT.wsgi:application -w 2 -b :8000
}

if [ ${ENVIRONMENT} == "dev" ]; then
    # use development server
    start_development
else
    # use production server
    start_production
fi