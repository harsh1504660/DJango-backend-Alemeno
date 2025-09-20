import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'change-me-in-production'
DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_celery_beat',
    'loans',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'credit_system.urls'

TEMPLATES = []

WSGI_APPLICATION = 'credit_system.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB','creditdb'),
        'USER': os.getenv('POSTGRES_USER','credit'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD','creditpass'),
        'HOST': os.getenv('DB_HOST','db'),
        'PORT': os.getenv('DB_PORT','5432'),
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL','redis://redis:6379/0')
