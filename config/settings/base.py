import os
from pathlib import Path

import firebase_admin
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default

    normalized_value = value.strip().lower()
    if normalized_value in {"1", "true", "yes", "on"}:
        return True
    if normalized_value in {"0", "false", "no", "off"}:
        return False
    raise ImproperlyConfigured(f"{name} must be a boolean value.")


def get_env_list(name, default=()):
    return [
        item.strip()
        for item in os.getenv(name, ",".join(default)).split(",")
        if item.strip()
    ]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
DEBUG = False
ALLOWED_HOSTS = []

WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v26.0")

FIREBASE_USE_APPLICATION_DEFAULT_CREDENTIALS = get_env_bool(
    "FIREBASE_USE_APPLICATION_DEFAULT_CREDENTIALS",
    False,
)
FIREBASE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not FIREBASE_CREDENTIALS_PATH:
    default_firebase_credentials = BASE_DIR / "firebase_api.json"
    if default_firebase_credentials.is_file():
        FIREBASE_CREDENTIALS_PATH = str(default_firebase_credentials)

if FIREBASE_CREDENTIALS_PATH:
    firebase_path = Path(FIREBASE_CREDENTIALS_PATH).expanduser()
    if not firebase_path.is_absolute():
        firebase_path = BASE_DIR / firebase_path
    if not firebase_path.is_file():
        raise ImproperlyConfigured(
            "GOOGLE_APPLICATION_CREDENTIALS must point to an existing credential file."
        )
    FIREBASE_CREDENTIALS_PATH = str(firebase_path)
    os.environ.setdefault(
        "GOOGLE_APPLICATION_CREDENTIALS",
        FIREBASE_CREDENTIALS_PATH,
    )

if FIREBASE_CREDENTIALS_PATH or FIREBASE_USE_APPLICATION_DEFAULT_CREDENTIALS:
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app()

FCM_DJANGO_SETTINGS = {
     # Allows updating existing tokens instead of throwing integrity errors
     "UPDATE_ON_DUPLICATE_REG_ID": True,
}

AUTH_USER_MODEL = 'membership.User'



IMPORT_EXPORT_SKIP_ADMIN_CONFIRM = False
# Force UTF-8 encoding for text-based file formats
IMPORT_EXPORT_CSV_ENCODING = 'utf-8-sig'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASE_ENGINE = os.getenv(
    "DATABASE_ENGINE",
    "django.db.backends.sqlite3",
)
DATABASE_NAME = os.getenv("DATABASE_NAME", str(BASE_DIR / "db.sqlite3"))
if DATABASE_ENGINE.endswith("sqlite3"):
    if not DATABASE_NAME:
        raise ImproperlyConfigured("DATABASE_NAME must be set for SQLite.")
    sqlite_path = Path(DATABASE_NAME).expanduser()
    if not sqlite_path.is_absolute():
        sqlite_path = BASE_DIR / sqlite_path
    DATABASE_NAME = str(sqlite_path)
DATABASES = {
    "default": {
        "ENGINE": DATABASE_ENGINE,
        "NAME": DATABASE_NAME,
        "CONN_MAX_AGE": int(os.getenv("DATABASE_CONN_MAX_AGE", "0")),
    }
}
if DATABASE_ENGINE.endswith("postgresql"):
    missing_database_settings = [
        setting_name
        for setting_name in (
            "DATABASE_NAME",
            "DATABASE_USER",
            "DATABASE_PASSWORD",
            "DATABASE_HOST",
        )
        if not os.getenv(setting_name)
    ]
    if missing_database_settings:
        raise ImproperlyConfigured(
            "Set PostgreSQL connection variables: "
            + ", ".join(missing_database_settings)
        )
    DATABASES["default"].update(
        {
            "USER": os.getenv("DATABASE_USER", ""),
            "PASSWORD": os.getenv("DATABASE_PASSWORD", ""),
            "HOST": os.getenv("DATABASE_HOST", ""),
            "PORT": os.getenv("DATABASE_PORT", "5432"),
            "CONN_HEALTH_CHECKS": True,
        }
    )


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'api',
    'administration',
    'membership',
    'finance',
    'activity',
    'import_export',
    "django_tasks", # To run background tasks
    "django_tasks_db",     # The actual backend engine providing the DB tables
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
    # Default permission classes
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication', # Allows logged-in admin sessions to register
        'rest_framework.authentication.BasicAuthentication',
    ],
    # Default pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
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
    ('en', 'English'),
    ('bn', 'বাংলা'),
    ('ar', 'العربية')
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

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = BASE_DIR / 'media'

# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# 1. Ignore background, static, or admin paths from Request Logs
DJANGO_EASY_AUDIT_LOG_REQUESTS_RE_EXCLUDE = [
    r'^/admin/',       # Exclude internal admin clicks if you only want visitor traffic
    r'^/static/',      # Exclude static file requests
    r'^/media/',       # Exclude media file requests
    r'^/favicon\.ico', # Exclude browser icon requests
]
