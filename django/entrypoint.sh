#!/bin/sh

set -ex

# if [ "$DATABASE" = "postgres" ]
# then
#     echo "Waiting for postgres..."

#     while ! nc -z $SQL_HOST $SQL_PORT; do
#       sleep 0.1
#     done

#     echo "PostgreSQL started"
# fi

export PGPASSWORD=$SQL_PASSWORD
export DEFAULT_DATABASE=default_database

if psql -h $SQL_HOST -p $SQL_PORT -U $SQL_USER $DEFAULT_DATABASE -tc "SELECT 1 FROM pg_database WHERE datname = '${SQL_DATABASE}'" | grep -q 1; then
    echo "Database ${SQL_DATABASE} already exist, will skip restore and just do a migrate"
    python manage.py migrate
else
    echo "Database ${SQL_DATABASE} does not exist, will now restore data from S3"

    # pull latest json from s3
    BUCKET=appl-tracky-backup
    s3_key=$(aws s3 ls s3://${BUCKET}/db-backup --recursive | sort | tail -n 1 | awk '{print $4}')
    aws s3 cp "s3://${BUCKET}/${s3_key}" db_backup.json

    psql -h $SQL_HOST -p $SQL_PORT -U $SQL_USER $DEFAULT_DATABASE -c "CREATE DATABASE ${SQL_DATABASE}"

    # migrate db using Django's schema, trim tables
    python manage.py migrate && echo "delete from auth_permission; delete from django_content_type;" | python manage.py dbshell

    # load into postgres VIA DJANGO manage command
    python manage.py loaddata db_backup.json
fi

python manage.py collectstatic --clear --noinput
python manage.py collectstatic --no-input
python manage.py initialize_superuser

# echo Starting gunicorn...
# how many workers: https://stackoverflow.com/questions/15979428/what-is-the-appropriate-number-of-gunicorn-workers-for-each-amazon-instance-type
PROPER_WORKER_NUM=$((2 * $(getconf _NPROCESSORS_ONLN) + 1))
echo We have $(getconf _NPROCESSORS_ONLN) cpu cores, we can spin up ${PROPER_WORKER_NUM} django workers...

# python manage.py runserver 0.0.0.0:8001
gunicorn django_server.wsgi:application --forwarded-allow-ips="*" --workers=${PROPER_WORKER_NUM} --log-level info --bind 0.0.0.0:8001