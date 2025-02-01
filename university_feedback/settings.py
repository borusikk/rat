import os
from pathlib import Path

# Основная директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность
SECRET_KEY = 'django-insecure-jgfk#$=8%%cxb2_=r^(%5wv5#@wy@-ufoegz4@i-38-58%hff4'
DEBUG = True
ALLOWED_HOSTS = []

# Установленные приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'feedback_app',  # Ваше приложение
    'django_recaptcha'
]

RECAPTCHA_PUBLIC_KEY = '6Lfz1sgqAAAAACJ_zOuuY9EFwmm0y37sXMTbKL14'
RECAPTCHA_PRIVATE_KEY = '6Lfz1sgqAAAAAFlv1Edt71CswaVkJEhLbIQE-Z04'

# Средства обработки запросов
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Основной URL конфигурации
ROOT_URLCONF = 'university_feedback.urls'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
import tempfile
tempfile.tempdir = '/tmp'




# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Если используете общую директорию шаблонов
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'university_feedback.wsgi.application'

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Аутентификация
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

# Интернационализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Директорія для зібраних статичних файлів
# Статические файлы
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
LOGIN_URL = '/login/'

# Медиафайлы (загрузка изображений)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Логирование (необязательно, но полезно для отладки)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "wwork8655@gmail.com"  # Ваша email-адреса
EMAIL_HOST_PASSWORD = "ggboria1996"  # Пароль від пошти (краще використовувати App Password)