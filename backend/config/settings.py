from pathlib import Path

import environ


env = environ.Env(
    DEBUG=(bool, False)
)
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(BASE_DIR.joinpath('.env'))

SECRET_KEY = env.str('SECRET_KEY')

DEBUG = env('DEBUG')

# TODO: consider list typing & defaults
ALLOWED_HOSTS = env.str('ALLOWED_HOSTS', default='*').split(' ')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',

    'recipes',
    'api',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
    'default': {
        "ENGINE": env.str("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": env.str("DB_NAME", BASE_DIR.joinpath("db.sqlite3")),
        "USER": env.str("POSTGRES_USER", "postgres"),
        "PASSWORD": env.str("POSTGRES_PASSWORD", "postgres"),
        "HOST": env.str("DB_HOST", "localhost"),
        "PORT": env.int("DB_PORT", 5432),
    }
}


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


LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.joinpath('static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.joinpath('media/')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

DJOSER = {
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.AllowAny'],
        'user': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
    },
    'SERIALIZERS': {
        'current_user': 'api.serializers.users_main.FoodgramUserSerializer',
        'user': 'api.serializers.users_main.FoodgramUserSerializer',
        'user_create': 'api.serializers.users_main.FoodgramUserCreateSerializer',
        'user_list': 'api.serializers.users_main.FoodgramUserSerializer',
    },
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
}
