

import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vuy$-kjz!i1zumy6z9b9p1(v(k#3^l*&6vrlt=ap=yvtk-nnrt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'membership.User'


# Using Meta Whatsapp API to send message to all members on whatsapp
WHATSAPP_ACCESS_TOKEN  = "EAAeP9Q6UpvMBSAsVSS9PDr7p2rwZCBm32GgfuwOkZCg7zZAmxcMrAcXqervdyABG0WDPaavl8BtwzE9Xn04xsXXU5L0sUR98OMh466rqAUeFJjvpdufB1jbidg6zzuG1uV7uAtm3IrOdijRXb3qOZC8QwdW2k4HpmTOoAboCUeK4mFsPeH8IiESPOddW9AZDZD"
WHATSAPP_PHONE_NUMBER_ID = "1310719008783024"
WHATSAPP_API_VERSION = "v26.0"  # Use the latest stable Graph API version



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
    'simple_history',
    'import_export',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # simple_history to track users log
    'simple_history.middleware.HistoryRequestMiddleware',
]

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


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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
TIME_ZONE = 'Asia/Dhaka'
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

