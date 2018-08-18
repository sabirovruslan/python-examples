from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_DATABASE'),
        'USER': os.environ.get('DB_USERNAME'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'PORT': os.environ.get('DB_PORT'),
        'HOST': os.environ.get('DB_HOST'),
    }
}