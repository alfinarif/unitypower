import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

import firebase_admin
from firebase_admin import credentials



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Initialize Firebase Admin SDK
# Set the path to your downloaded Firebase private key JSON
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, 'firebase_api.json')

# Initialize the default Firebase App
firebase_admin.initialize_app()

FCM_DJANGO_SETTINGS = {
     # Allows updating existing tokens instead of throwing integrity errors
     "UPDATE_ON_DUPLICATE_REG_ID": True,
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vuy$-kjz!i1zumy6z9b9p1(v(k#3^l*&6vrlt=ap=yvtk-nnrt'



AUTH_USER_MODEL = 'membership.User'



IMPORT_EXPORT_SKIP_ADMIN_CONFIRM = False
# Force UTF-8 encoding for text-based file formats
IMPORT_EXPORT_CSV_ENCODING = 'utf-8-sig'



# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'administration',
    'membership',
    'finance',
    'import_export',

    'easyaudit', # To tracking all users actions
    "django_tasks", # To run background tasks
    "django_tasks_db",     # The actual backend engine providing the DB tables
    "django_scheduled_tasks",
    'mathfilters', # To use math filters in templates

    'rest_framework',
    'fcm_django',
]

TASKS = {
    "default": {
        "BACKEND": "django_tasks_db.DatabaseBackend",
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'finance.middleware.AutoBillingSyncMiddleware', # Custom middleware to sync billing and payment summaries on every request

    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
]


REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication', # Allows logged-in admin sessions to register
        'rest_framework.authentication.BasicAuthentication',
    ],
}



ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'



# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', _('English')),
    ('bn-bd', _('Bengali')),
    ('ar', _('Arabic'))
]
TIME_ZONE = 'Asia/Riyadh'

# It is highly recommended to keep UTC enabled for database storage
USE_TZ = True

USE_I18N = True


LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = BASE_DIR / 'media'

# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = 'media/'



# 1. Ignore background, static, or admin paths from Request Logs
DJANGO_EASY_AUDIT_LOG_REQUESTS_RE_EXCLUDE = [
    r'^/admin/',       # Exclude internal admin clicks if you only want visitor traffic
    r'^/static/',      # Exclude static file requests
    r'^/media/',       # Exclude media file requests
    r'^/favicon\.ico', # Exclude browser icon requests
]


# 2. Exclude specific models from being tracked (e.g., the log models themselves)
DJANGO_EASY_AUDIT_UNREGISTERED_CLASSES_EXTRA = [
    'sessions.Session', # Avoid logging session updates on every click
]






