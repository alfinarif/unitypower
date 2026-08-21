from .base import *
import os


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Using Meta Whatsapp API to send message to all members on whatsapp
WHATSAPP_ACCESS_TOKEN  = "EAAeP9Q6UpvMBSAsVSS9PDr7p2rwZCBm32GgfuwOkZCg7zZAmxcMrAcXqervdyABG0WDPaavl8BtwzE9Xn04xsXXU5L0sUR98OMh466rqAUeFJjvpdufB1jbidg6zzuG1uV7uAtm3IrOdijRXb3qOZC8QwdW2k4HpmTOoAboCUeK4mFsPeH8IiESPOddW9AZDZD"
WHATSAPP_PHONE_NUMBER_ID = "1310719008783024"
WHATSAPP_API_VERSION = "v26.0"  # Use the latest stable Graph API version



# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}






