import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "").strip()
if not SECRET_KEY or SECRET_KEY.startswith("django-insecure-"):
    raise ImproperlyConfigured(
        "Set DJANGO_SECRET_KEY to a strong, unique production secret."
    )

DEBUG = False
ALLOWED_HOSTS = get_env_list(
    "DJANGO_ALLOWED_HOSTS",
    ("unitypower.online", "www.unitypower.online"),
)
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("Set DJANGO_ALLOWED_HOSTS to your hostnames.")
if not FIREBASE_CREDENTIALS_PATH and not FIREBASE_USE_APPLICATION_DEFAULT_CREDENTIALS:
    raise ImproperlyConfigured(
        "Configure GOOGLE_APPLICATION_CREDENTIALS or enable "
        "FIREBASE_USE_APPLICATION_DEFAULT_CREDENTIALS."
    )

CSRF_TRUSTED_ORIGINS = get_env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    ("https://unitypower.online", "https://www.unitypower.online"),
)

SECURE_SSL_REDIRECT = get_env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

SECURE_HSTS_SECONDS = int(
    os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000")
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = get_env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    False,
)
SECURE_HSTS_PRELOAD = get_env_bool("DJANGO_SECURE_HSTS_PRELOAD", False)

if get_env_bool("DJANGO_TRUST_PROXY_SSL_HEADER", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
