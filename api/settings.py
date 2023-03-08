import os
from datetime import timedelta

# JWT settings.
from api.settings_jwt import *


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'o7lx@83-%tdncpo0qx4h#nbf-kd_bbswajgrvigy55-c8z!#dz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DISABLE_AUTHENTICATION = False # for debugging purposes only.

ALLOWED_HOSTS = ['*']

VENV_BIN = ""

# Application definition
# To include the app in our project add a reference to its configuration class in the INSTALLED_APPS.
# The infobloxConfig class is in the infoblox/apps.py file, so its dotted path is 'infoblox.apps.infobloxConfig'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'infoblox.middleware.Log.LogMiddleware',
    'infoblox.middleware.HTTP.HTTPMiddleware',
]

ROOT_URLCONF = 'api.urls'

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

WSGI_APPLICATION = 'api.wsgi.application'

# Redis cache

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'api',
        'USER': 'api', #DATABASE_USER
        'PASSWORD': 'password', #DATABASE_PASSWORD
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# e-mail (to platform's MTA).
EMAIL_HOST = "mta" # from /etc/hosts.

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'django': {
            'format': 'DJANGO_API - %(message)s',
        },
        'http': {
            'format': 'HTTP_API - %(message)s',
        },
    },
    'handlers': {
        'syslog_django': {
            'class': 'logging.handlers.SysLogHandler',
            'level': 'DEBUG',
            'address': '/dev/log',
            'facility': 'local0',
            'formatter': 'django',
        },
        'syslog_http': {
            'class': 'logging.handlers.SysLogHandler',
            'level': 'DEBUG',
            'address': '/dev/log',
            'facility': 'local0',
            'formatter': 'http',
        },
    },
    'loggers': {
        'django': {
            'handlers': [ 'syslog_django' ],
            'level': 'DEBUG',
            'propagate': True,
        },
        'http': {
            'handlers': [ 'syslog_http' ],
            'level': 'DEBUG',
        },
    },
}

# Django REST Framework.

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
    ],

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '600/minute'
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'RS256',
    'SIGNING_KEY': '',
    'VERIFYING_KEY': JWT_TOKEN['publicKey'],
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Variables.

API_SUPPLICANT_HTTP_PROXY = ""
API_SUPPLICANT_NETWORK_TIMEOUT = 60 # seconds.

LOCK_MAX_VALIDITY = 30 # seconds.

# If set to False only the permissions on the father are checked (exclude upper tree).
# If set to True some overhead is added.
INHERIT_GRANDPARENTS_PERMISSIONS = True

# Plugins and configuration.
IP_RESERVE_IMPLEMENTATION = ("infoblox.usecases.impl.Ipv4CustomReserve1", "Ipv4CustomReserve1")
CLOUD_ASSIGN_IMPLEMENTATION = ("infoblox.usecases.impl.CloudNetworkCustomAssign1", "CloudNetworkCustomAssign1")

PLUGINS = [
    'infoblox.plugins.CiscoSpark'
]

try:
    from api.plugins_conf.ciscospark import *
except Exception:
    pass
