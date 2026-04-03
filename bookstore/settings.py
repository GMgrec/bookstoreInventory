from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de la aplicación
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'inventory',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'bookstore.urls'

WSGI_APPLICATION = 'bookstore.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de la API de tasas de cambio
EXCHANGE_RATE_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'
DEFAULT_EXCHANGE_RATE = config('DEFAULT_EXCHANGE_RATE', default=1.0, cast=float)
DEFAULT_CURRENCY = config('DEFAULT_CURRENCY', default='USD')
