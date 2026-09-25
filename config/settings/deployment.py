from .base import *
import os


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['unitypower.online', 'www.unitypower.online', 'https://unitypower.online']


# Using Meta Whatsapp API to send message to all members on whatsapp
WHATSAPP_ACCESS_TOKEN  = "EAAeP9Q6UpvMBShgbZBZAikFgUZAMHYWXtiaAQKjFmT5AJUm26q1KYQYtBqIZBEKbEXKAhkExnJrLS1ZCumYiRzFFdO4gy11tqRroAbW0UkmIkIJgXHh4ZBDtZCDZBhMbRI1wUtWSVYTVu9SBRow5erTO7AFf1bZCODhZAj5PwKYdeOw87a9tDXuZBxijCcWrEXPplZAJxQZDZD"
WHATSAPP_PHONE_NUMBER_ID = "1245915641949243"
WHATSAPP_API_VERSION = "v26.0"  # Use the latest stable Graph API version



# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}












