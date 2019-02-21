#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic --clear --noinput
python manage.py collectstatic --no-input

# exec "$@"
echo Starting gunicorn...
gunicorn django_server.wsgi:application --bind 0.0.0.0:8000