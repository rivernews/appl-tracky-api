# pull official base image
# debian
# FROM python:3.7-slim
# alpine
FROM python:3.7-alpine

# set environment varibles
# let Python don't try to write .pyc files which we also do not desire.
ENV PYTHONDONTWRITEBYTECODE 1 
# ensures our console output looks familiar and is not buffered by Docker, which we don’t want. 
ENV PYTHONUNBUFFERED 1
ENV PROJECT_DIR /usr/src/django
EXPOSE 8000

RUN echo Copying all stuff into container...
RUN mkdir -p $PROJECT_DIR
WORKDIR $PROJECT_DIR
COPY . .

# prepare db adapter dev env (psycopg2)
# alpine version
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev
# debian version
# RUN set -ex \
#     && RUN_DEPS=" \
#         libpcre3 \
#         mime-support \
#         postgresql-client \
#     " \
#     && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
#     && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
#     && rm -rf /var/lib/apt/lists/*


# install dependencies
# alpine version
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/django/requirements.txt
RUN pip install -r requirements.txt
# cleanup db adapter installation artifacts
RUN apk del build-deps
# debian version
# RUN set -ex \
#     && BUILD_DEPS=" \
#         build-essential \
#         libpcre3-dev \
#         libpq-dev \
#     " \
#     && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
#     # && python3.7 -m venv /venv \
#     # && /venv/bin/pip install -U pip \
#     && pip install -U pip \
#     # && /venv/bin/pip install --no-cache-dir -r ./requirements.txt \
#     && pip install --no-cache-dir -r ${PROJECT_DIR}/requirements.txt \
#     \
#     && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
#     && rm -rf /var/lib/apt/lists/*

# copy entrypoint.sh
# COPY ./entrypoint.sh /usr/src/django/entrypoint.sh

# copy project
# COPY . /usr/src/django/

# run entrypoint.sh
# RUN echo In Dockerfile: chomd on entrypoint.sh
# ENTRYPOINT ["chmod +x /usr/src/django/entrypoint.sh && /usr/src/django/entrypoint.sh"]
# see https://stackoverflow.com/questions/29535015/error-cannot-start-container-stat-bin-sh-no-such-file-or-directory
# ENTRYPOINT ["/bin/sh","-c","chmod +x /usr/src/django/entrypoint.sh && /usr/src/django/entrypoint.sh"]
RUN chmod +x ${PROJECT_DIR}/entrypoint.sh
ENTRYPOINT ["/usr/src/django/entrypoint.sh"]
# CMD ["/bin/sh", "-c", "chmod +x /usr/src/django/entrypoint.sh && /usr/src/django/entrypoint.sh"]
# CMD ["/bin/sh", "-c", "chmod +x entrypoint.sh && entrypoint.sh"]