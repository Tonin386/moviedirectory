"""
Django settings for moviedirectory project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('django', 'secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['movie-directory.com']
AUTH_USER_MODEL = 'moviedirectory.User'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = "login"
SECURE_SSL_REDIRECT = True

EMAIL_USE_TLS = True
EMAIL_HOST = str(config.get('mail', 'host'))
EMAIL_HOST_USER = str(config.get('mail', 'user'))
EMAIL_HOST_PASSWORD = str(config.get('mail', 'password'))
EMAIL_PORT = int(config.get('mail', 'port'))
DEFAULT_FROM_EMAIL = "\"Movie Directory\" <support@movie-directory.com>"

INTERNAL_IPS = [
    'localhost',
    '127.0.0.1',
    '86.120.142.122',
]


# Application definition

INSTALLED_APPS = [
    'main',
    'moviedirectory',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_registration',
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'moviedirectory.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'moviedirectory.wsgi.application'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config.get('database', 'engine'),
        'NAME': config.get('database', 'name'),  # Nom de la base de données
        'USER': config.get('database', 'user'),  # User ici
        'PASSWORD': config.get('database', 'password'),  # Mdp ici
        'HOST': config.get('database', 'host'),  # Utile si votre base de données est sur une autre machine
        'PORT': config.get('database', 'port'),  # ... et si elle utilise un autre port que celui par défaut
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

ugettext = lambda x: x

LANGUAGES = (
    ('fr', ugettext('French')),
    ('en', ugettext('English')),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "/home/fiddleco/www/static/"

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

try:
    from local_settings import *
except ImportError:
    pass
