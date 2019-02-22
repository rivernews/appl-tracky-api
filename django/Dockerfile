# pull official base image
FROM python:3.7-alpine

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
EXPOSE 8000

# set work directory
WORKDIR /usr/src/django

RUN echo Copying all stuff into container...
COPY . /usr/src/django/

# prepare db adapter dev env (psycopg2)
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev

# install dependencies
RUN pip install --upgrade pip
# COPY ./requirements.txt /usr/src/django/requirements.txt
RUN pip install -r requirements.txt

# cleanup db adapter installation artifacts
RUN apk del build-deps

# copy entrypoint.sh
# COPY ./entrypoint.sh /usr/src/django/entrypoint.sh

# copy project
# COPY . /usr/src/django/

# run entrypoint.sh
RUN echo In Dockerfile: chomd on entrypoint.sh
# ENTRYPOINT ["chmod +x /usr/src/django/entrypoint.sh && /usr/src/django/entrypoint.sh"]
# see https://stackoverflow.com/questions/29535015/error-cannot-start-container-stat-bin-sh-no-such-file-or-directory
ENTRYPOINT ["/bin/sh","-c","chmod +x /usr/src/django/entrypoint.sh && /usr/src/django/entrypoint.sh"]