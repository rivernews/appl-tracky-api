"""
Django settings for django_server project.

Generated by 'django-admin startproject' using Django 1.11.20.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!


try:
    from .credentials import *
    DEBUG = True
except ImportError:
    DEBUG = False

# You can also set DEBUG flag via env var, and this will overwrite it
DEBUG = os.environ.get('DEBUG', DEBUG)

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework', 'corsheaders',
    'django_filters',
    'social_django', 'rest_social_auth', # django social auth + rest social auth
    'cacheops',

    'api.apps.ApiConfig',
]

# django doc: https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts
if not DEBUG:
    ALLOWED_HOSTS = list(filter(bool, os.environ.get('DEPLOYED_DOMAIN', '').split(',')))
else:
    ALLOWED_HOSTS = []

# For DRF to generate link that correspond to request w/ the correct scheme of http and https
# https://docs.djangoproject.com/en/2.2/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Make sure when user login or input sensitive form, https is used; otherwise ban the request or login
# see https://rickchristianson.wordpress.com/2013/10/31/getting-a-django-app-to-use-https-on-aws-elastic-beanstalk/
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Make sure you setup `SECURE_PROXY_SSL_HEADER` AND setup nginx or the web server in front of django before using this.
# You will need to have nginx set the proxy header `X_FORWARDED_PROTO` to `https` when client request is indeed https.
# If you don't configure nginx and django don't receive the header and perceive the request as insecure (http), as you turn `SECURE_SSL_REDIRECT` on, you will get an infinite loop: django will redirect all your request which makes another (https) request, and so on.
if not DEBUG:
    SECURE_SSL_REDIRECT = True 

# Django CORS header settings
CORS_ORIGIN_WHITELIST = tuple(filter(bool, [ # filter: https://stackoverflow.com/questions/3845423/remove-empty-strings-from-a-list-of-strings
        'localhost:3000', # frontend react development server
    ] + os.environ.get('CORS_DOMAIN_WHITELIST', '').split(',') # frontend hosted on github page
))

# This sets the header to '*'. if frontend are sending credentials, you cannot use this.
# and needs to use CORS_ORIGIN_WHITELIST instead
# CORS_ORIGIN_ALLOW_ALL = True 

# This is necessary if frontend is sending auth credentials, otherwise browser will raise error:
# "The value of the 'Access-Control-Allow-Credentials' header in the response is '' 
# which must be 'true' when the request's credentials mode is 'include'."
CORS_ALLOW_CREDENTIALS = True # this includes cookie and JWT auth tokens


MIDDLEWARE = [
    # "Add CorsMiddleware as high as possible"
    # https://github.com/OttoYiu/django-cors-headers#setup
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('SQL_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('SQL_DATABASE', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.getenv('SQL_USER', 'user'),
        'PASSWORD': os.getenv('SQL_PASSWORD', 'password'),
        'HOST': os.getenv('SQL_HOST', 'localhost'),
        'PORT': os.getenv('SQL_PORT', '5432'),
        'OPTIONS': {
            # 'sslmode': 'require', # using port-forwarding now for postgres in k8 (only within localhost so is safe)
        }
    }
}


# https://github.com/Suor/django-cacheops
CACHEOPS_REDIS = {
    'host': os.getenv('REDIS_HOST', 'localhost'), # redis-server is on same machine
    'port': os.getenv('REDIS_PORT', '6379'),        # default redis port
    'db': int(os.getenv('CACHEOPS_REDIS_DB', '1')),             # SELECT non-default redis database
                         # using separate redis db or redis instance
                         # is highly recommended

    'socket_timeout': 5,   # connection timeout in seconds, optional
}

CACHEOPS = {
    'api.*': {'ops': {'get', 'fetch'}, 'timeout': 60*60}
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'global_static')

AUTH_USER_MODEL = 'api.CustomUser'

# REST framework settings
# https://www.django-rest-framework.org/tutorial/quickstart/#pagination

REST_FRAMEWORK = {
    # Hyperlink model
    'URL_FIELD_NAME': 'api_url',

    # Scalability - pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 8,

    # Filtering
    # drf: https://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend
    # django-filter: https://django-filter.readthedocs.io/en/master/guide/rest_framework.html
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),

    # Security - throttling
    # https://www.django-rest-framework.org/api-guide/throttling/
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle', # for unauthenticated users; use IP address to identify
        'rest_framework.throttling.UserRateThrottle' # identify by user id
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/min',
        'user': '180/min'
    },
    
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', # this will make all endpoints require login by default for all CRUD operations.
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

# if DEBUG:
#     REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = ('rest_framework.permissions.AllowAny',)


# JWT settings
# http://getblimp.github.io/django-rest-framework-jwt/
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=14),
}

# Social Auth
# https://github.com/st4lk/django-rest-social-auth

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend', # Django's native default
)

# these redirect settings are useless when using JWT, i.e., code + jwt flow for social auth
# REST_SOCIAL_OAUTH_REDIRECT_URI = '/'
# REST_SOCIAL_DOMAIN_FROM_ORIGIN = True
# REST_SOCIAL_OAUTH_ABSOLUTE_REDIRECT_URI = 'http://localhost:3000/auth/google/callback/'
REST_SOCIAL_LOG_AUTH_EXCEPTIONS = DEBUG #  log social auth authentication exceptions for debug purpose, can turn off in production (cuz you're not letting others to learn to use this API, it's only used by the web app)

# Social backend credentials
# available settings: https://python-social-auth.readthedocs.io/en/latest/backends/google.html?highlight=scope
# all scopes line-up: https://developers.google.com/identity/protocols/googlescopes#peoplev1
# https://python-social-auth.readthedocs.io/en/latest/configuration/porting_from_dsa.html?highlight=SOCIAL_AUTH_FACEBOOK_KEY

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',

    # will run the function update_user_avatar() in app `api`'s pipelines.py
    'api.pipelines.update_user_avatar',
)

# Django email setup
SERVER_EMAIL = ''
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', ''))
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = '[Appl Tracky API Server Notifier] '

ADMINS = os.getenv('ADMINS', [])
if ADMINS != []:
    ADMINS = [ tuple(data_pair.split(',')) for data_pair in ADMINS.split('|') ]