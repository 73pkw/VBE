"""
Django settings for vaana_app project.

Generated by 'django-admin startproject' using Django 3.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path
from datetime  import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-u8*p#)cuf@tp10yr31=urf)s44ihb688#wc06$=y4_xwy)15dg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

# smtp email configuration
EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.ionos.de'
EMAIL_HOST_USER = 'test.vaanah@kaeyros-analytics.de'
EMAIL_HOST_PASSWORD = '$Happy.Vaanah$'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# social auth keys
SOCIAL_SECRET = "vaanah"
GOOGLE_CLIENT_ID = "362829290794-91601oi5pvqjoclq9u6eu7lvp04m620u.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "ThaLBrUPHNfNIQbPanEnayWU"

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
}
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',

    'corsheaders',
    'django_extensions',
    'rest_framework',
    'djoser',
    'storages',

    'cores',
    'users',
    'categories',
    'products',
    'stores',
    'carts',
    'orders',
    'addresses',
    'countries',
    'django_seed',
    'shippings',
    'payments',
    'wishlist',
    'files',
    'funds',
    'wallets',

    # 'chatterbot.ext.django_chatterbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'corsheaders.middleware.CorsMiddleware',

]

ROOT_URLCONF = 'vaana_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'vaana_app/cores/templates')],
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

WSGI_APPLICATION = 'vaana_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'vaanah_user',
        'PASSWORD': 'secretsecret',
        'HOST': 'vaanahdb.cvamgenajfwz.eu-central-1.rds.amazonaws.com',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

#CORS_ORIGIN_WHITELIST = ['*']

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'cores.exceptions.core_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'error',

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'users.backends.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

APPEND_SLASH=False
# Tell Django about the custom `User` model we created. The string
# `authentication.User` tells Django we are referring to the `User` model in
# the `authentication` module. This module is registered above in a setting
# called `INSTALLED_APPS`.
AUTH_USER_MODEL = 'users.User'

FRONT_URL = 'http://ec2-18-193-203-105.eu-central-1.compute.amazonaws.com:8084'
STRIPE_PUBLISHABLE_KEY = 'pk_test_51HQ3ZXFunRLoLWctiy0l6VVOeflU8ES2IRjTyY7LL9rEpKedBIfOfKB1BSSftQk4Qmke8HdtRcdmje7R2whuWgTz00U7HXpwjn'
STRIPE_SECRET_KEY = 'sk_test_51HQ3ZXFunRLoLWctxxpIKhYLudKWPCFsLPQzDgKoR1UZykOkD8CIDkxT2GUrXC5aejGMQkTReqSrOCGGF6sUUBQo00Sz4ugrOQ'
SHIPPO_API_KEY = 'shippo_test_d88dfb2c748b3c9ea2483bded12428024b5f36e3'
AWS_ACCESS_KEY_ID = 'AKIATDIHX42OI3R4PSXV'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'vaanahs3media'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_REGION_NAME = 'eu-central-1'
AWS_LOCATION = 'static'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
