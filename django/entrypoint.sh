#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# to claer out the data, see https://stackoverflow.com/questions/7907456/emptying-the-database-through-djangos-manage-py
# python manage.py flush --no-input
# python manage.py migrate --fake

# this will only run on a fresh provision and the following.
# if you do `flush`, then this `migrate` will not work
# python manage.py makemigrations
# python manage.py makemigrations api
python manage.py migrate

python manage.py collectstatic --clear --noinput
python manage.py collectstatic --no-input
python manage.py initialize_superuser

# echo Starting gunicorn...
# how many workers: https://stackoverflow.com/questions/15979428/what-is-the-appropriate-number-of-gunicorn-workers-for-each-amazon-instance-type
gunicorn django_server.wsgi:application --forwarded-allow-ips="*" \
--workers=$((2 * $(getconf _NPROCESSORS_ONLN) + 1)) \
--bind 0.0.0.0:8000