import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=False)

from .base import *  # noqa: E402,F403


DEBUG = get_env_bool("DJANGO_DEBUG", True)
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-development-only-do-not-use-in-production",
)
ALLOWED_HOSTS = get_env_list(
    "DJANGO_ALLOWED_HOSTS",
    ("localhost", "127.0.0.1", "testserver"),
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
