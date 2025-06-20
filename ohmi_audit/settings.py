import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-!5!tssmkukvxsjx+xwqc9mlw67^ej6*h+fa_gzc!h^sv5@(ax-'

"""
when it is False the 404.html is used automatically instead of 
django's default 404 page.
"""
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'ohmi-audit.onrender.com',
]

CSRF_TRUSTED_ORIGINS = [
    'https://ohmi-audit.onrender.com',
]

"""
New app:

1. python manage.py startapp hr_management
2. move hr_management to inside ohmi_audit directory
3. add 'ohmi_audit.hr_management' to INSTALLED_APPS
4. create a view
5. create a template for the view
6. create urls.py in hr_management directory and add a path
7. include the urls in the main urls.py

8. create models based on common_models_base.py
9. run migrations with comands:
    python manage.py makemigrations
    python manage.py migrate

"""

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'ohmi_audit.main_app',
    'ohmi_audit.hr_management',
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

ROOT_URLCONF = 'ohmi_audit.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'ohmi_audit.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# -----------------------------------------------------------------------------
# The base URL prefix for static files. Defines how static files are referenced
# in templates (/static/css/style.css) Used with the {% static %} template tag
STATIC_URL = '/static/'

# Additional directories to search for static files. Lists folders where Django
# should look for static files during development. Used with `collectstatic`
# (files are copied from here to STATIC_ROOT)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Where collected static files are stored for production. Single directory where
# all static files are gathered when running `collectstatic`. This is what your
# web server (Nginx/Apache) actually serves from
STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')


# -----------------------------------------------------------------------------
# Base URL for serving user-uploaded media files. Defines the URL prefix for media
# files in templates (/media/user_photos/avatar.jpg). Similar to STATIC_URL but for
# dynamic content. In templates:
# <img src="{{ object.image.url }}"> <!-- Resolves to /media/path/to/file.jpg -->
MEDIA_URL = '/media/'

# Absolute filesystem path where uploaded files are stored. Where Django saves
# files uploaded via FileField or ImageField. Analogous to STATIC_ROOT
# but for user content
MEDIA_ROOT = BASE_DIR / 'media_files'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
