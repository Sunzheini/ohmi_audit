import os

import dj_database_url
from dotenv import load_dotenv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file (for local development)
if os.path.exists(os.path.join(BASE_DIR, '.env')):
    from dotenv import load_dotenv
    load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

"""
when it is False the 404.html is used automatically instead of 
django's default 404 page.
"""

"""
must be True for development, e.g. for .css, .js and media files to 
be loaded correctly
"""
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Env vars
"""
    - pip install python-dotenv
    - create .env file in the root of the project and add the vars there
    - from dotenv import load_dotenv and after the imports load_dotenv()  # loads the .env file
    - use os.environ.get('VAR_NAME') to get the value of the env var
    - add the .env file to .gitignore so it is not pushed to the repository
    - add the env vars in the Render dashboard
    - until finished, use DEBUG = True in render.com
"""

# -----------------------------------------------------------------

# Deployment Renderer.com /w sqlite
"""
    - run before deployment: python manage.py collectstatic
    - add 'ohmi-audit.onrender.com' in ALLOWED_HOSTS
    - add 'https://ohmi-audit.onrender.com' in CSRF_TRUSTED_ORIGINS
    - New web service
    - Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput
    - Build Command: pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
    (&& python manage.py migrate?)
    - Start Command: python manage.py runserver 0.0.0.0:8000 (while developing)
    - Start Command: gunicorn ohmi_audit.wsgi:application  (for production)
"""

# Changing to postgresql
"""
docker sign-in: gmail, docker user: Sunzheini1407
download the postgres image from Docker Hub

if resetting:
    docker stop my-postgres
    docker rm my-postgres
    docker volume prune

docker run --name my-postgres -e POSTGRES_DB=ohmi_audit_db -e POSTGRES_USER=postgres_user -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
docker ps to see the running containers, it should show the postgres container
add the database settings in the settings.py file as below
pip install psycopg2 # or psycopg2-binary
delete the db.sqlite3 file if it exists
in views.py temp replace all_users = list(UserModel.objects.all()) with all_users = []
Delete migration files and __pycache__ folders in all apps
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
"""

# Render.com /w postgresql
"""
Workspace -> +New -> Postgres
Set the info as in the database settings below
Get the link to the database and add it to the DATABASES in settings.py instead of localhost, postgresql://[USER]:[PASSWORD]@[HOST]/[DATABASE_NAME]
Deploy
Open shell in Render.com and run python manage.py migrate and python manage.py createsuperuser
pip install dj-database-url
add below:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
In render.com, go to the web service -> Environment -> Add Environment Variable -> DATABASE_URL: the string
restore view.py from above
"""

# Deployment GCP
"""
    - pip install gunicorn
    - install the Google Cloud SDK: https://cloud.google.com/sdk/docs/install
    - gcloud init
    ... (ongoing)
"""

# Django app to Docker container (including PostgreSQL, Redis)
"""
    - modify .env from:
        DEBUG=True
        SECRET_KEY=django-insecure-!5!tssmkukvxsjx+xwqc9mlw67^ej6*h+fa_gzc!h^sv5@(ax-
        ALLOWED_HOSTS=localhost,127.0.0.1,ohmi-audit.onrender.com
        DB_ENGINE=django.db.backends.postgresql
        DB_NAME=ohmi_audit_db
        DB_USER=postgres_user
        DB_PASSWORD=password
        DB_HOST=localhost
        DB_PORT=5432
        DATABASE_URL=postgresql://postgres_user:password@localhost:5432/ohmi_audit_db
        to:
        ALLOWED_HOSTS=localhost,127.0.0.1,ohmi-audit.onrender.com,web
        DB_HOST=db  # Changed from 'localhost' to 'db' (Docker service name)
        DB_PORT=5432
        # For Render.com deployment (keep this as is)
        DATABASE_URL=postgresql://postgres_user:password@localhost:5432/ohmi_audit_db
        # For Docker-compose (add this new variable)
        DOCKER_DATABASE_URL=postgresql://postgres_user:password@db:5432/ohmi_audit_db

    - create a Dockerfile in the root of the project (see the file for details)
    - create a requirements.txt file with all the dependencies
    - create a docker-compose.yml file to run the app and the database (see the file for details)
    - change CACHE:
        'redis://redis:6379',  # Changed from 127.0.0.1 to redis
    
    - again modify temporarily views.py like above
    - docker-compose down -v  # Stop containers and remove volumes
    - docker-compose up --build to build and run the app
    - access the app at http://localhost:8000, not 0.0.0.0:8000
    - now it is running
    - without stopping it, open a second terminal, it will be called `Local(2)` and run:
        Delete old migrations:
            docker-compose exec web find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
            docker-compose exec web find . -path "*/migrations/*.pyc" -delete
        Create new migrations:
            docker-compose exec web python manage.py makemigrations
        Apply migrations:
            docker-compose exec web python manage.py migrate
        Check if users exist, should  be empty:
            docker-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.all())" 
        If users exist, delete them:
            docker-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.all().delete()"
        Create a new superuser:
            docker-compose exec web python manage.py createsuperuser
            
        if you want again to run locally without Docker, i received an error, so:
        :: Delete virtual environment
            rmdir /s /q .venv
        :: Delete all __pycache__ folders
            for /r %i in (__pycache__) do rmdir /s /q "%i"
        :: Delete all migration files (keep __init__.py)
            for /r %i in (*.py) do if not "%~nxi"=="__init__.py" if "%~pi"=="\migrations\" del "%i"
        :: Create new virtual environment
            python -m venv .venv
            .\.venv\Scripts\activate
        :: Force reinstall Django and dependencies
            pip install --force-reinstall Django
            pip install -r requirements.txt
        
        python manage.py makemigrations
        python manage.py migrate
        run
"""

# -----------------------------------------------------------------------------

# Signals (Observer Pattern):
"""
1. create a new signal in ohmi_audit/main_app/signals.py
2. connect it to a function in ohmi_audit/main_app/apps.py
"""

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
CSRF_TRUSTED_ORIGINS = [
    'https://ohmi-audit.onrender.com',
]

# New app steps
"""
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
    # custom middleware: create it in the form of a decorator and add it here
    'common.custom_middleware.measure_time_middleware',

    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.locale.LocaleMiddleware', # for translation

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

                'django.template.context_processors.i18n',  # For language switcher
            ],
        },
    },
]

WSGI_APPLICATION = 'ohmi_audit.wsgi.application'

# -----------------------------------------------------------------------------

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Local PostgreSQL database settings
# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DB_ENGINE'),
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT'),
#     }
# }

# Render.com /w postgresql
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'ohmi_audit_db',                       # Database name
#         'USER': 'postgres_user',                       # Username (from before @ symbol)
#         'PASSWORD': '4lhyvQAk9zzRyHuApA78973PYtnEU6ro',  # Password (before @ symbol)
#         'HOST': 'dpg-d1jt68i4d50c738gt37g-a',         # Hostname (after @ symbol)
#         'PORT': '5432',                                # Default PostgreSQL port
#     }
# }

# Render.com /w dj_database_url to switch between local and production
# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.getenv('DATABASE_URL'),
#         conn_max_age=600,
#         conn_health_checks=True,
#     )
# }

# Django is in a Docker container, and the database is in another container
if os.getenv('DOCKER') == 'True':
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE'),
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),  # Will be 'db' in Docker
            'PORT': os.getenv('DB_PORT'),
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }


# -----------------------------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND':
            'django.core.cache.backends.redis.RedisCache',
        'LOCATION':
            # 'redis://127.0.0.1:6379',
            'redis://redis:6379',  # Changed from 127.0.0.1 to redis
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

# -----------------------------------------------------------------------------
# Localization
"""
    - LANGUAGE_CODE: The default language for the project (e.g., 'en-us' for English).
    - TIME_ZONE: The default time zone for the project (e.g., 'Europe/Sofia' for Bulgaria).
    - USE_I18N: Whether to enable Django's internationalization system.
    - USE_TZ: Whether to enable timezone support.
    - create a folder named localization/locale/bg/LC_MESSAGES in the root of the project
    - LOCALE_PATHS: A list of directories where Django will search for translation files.
    - LANGUAGES: A list of tuples defining the languages available in the project.
    - 'django.middleware.locale.LocaleMiddleware'    # After SessionMiddleware, before CommonMiddleWare
    - In templates add {% load i18n %} and {% trans "Save" %} for all the text. This doesn't work for variable text, e.g. {{ object.name }}.
    - python manage.py makemessages -l bg   # get all {%trans ... %} from the templates to the .po file
    - translate the messages in the .po file, remove the #fuzzy
    - python manage.py compilemessages  # apply translations
    - in the main urls.py add: 
        - from django.conf.urls.i18n import i18n_patterns
        - path('i18n/', include('django.conf.urls.i18n')),  # add this to the urlpatterns
        - at the bottom: urlpatterns += i18n_patterns(
            path('', include('ohmi_audit.main_app.urls')),
            path('hr-management/', include('ohmi_audit.hr_management.urls')),
            prefix_default_language=True,  # This will prefix the default language code to the URLs
    - in the navigation bar:
        <div class="lang">
            <form class="lang-form" action="{% url 'set_language' %}" method="post">
                {% csrf_token %}
                <input name="next" type="hidden" value="{{ redirect_to|default:request.path }}" />
                <select name="language" onchange="this.form.submit()">
                    {% get_current_language as LANGUAGE_CODE %}
                    {% get_available_languages as LANGUAGES %}
                    {% get_language_info_list for LANGUAGES as languages %}
                    {% for language in languages %}
                        <option value="{{ language.code }}"{% if language.code == LANGUAGE_CODE %} selected{% endif %}>
                            {{ language.name_local|capfirst }} ({{ language.code }})
                        </option>
                    {% endfor %}
                </select>
                {# The button is now optional since we're using onchange #}
            </form>
        </div>
    - in the views:
        - from django.utils.translation import gettext_lazy as _
        - page_title = _('Ohmi Audit Test')  # Mark for translation all similar strings
        - 'redirect_to': self.request.GET.get('next', ''),    # Add this to the context to ensure language switcher works
        - TEMPLATES = [
                {
                    # ...
                    'OPTIONS': {
                        'context_processors': [
                            # ...
                            'django.template.context_processors.i18n',  # For language switcher
                        ],
                    },
                },
            ]
            
        - when making new messages:
            - python manage.py makemessages -l bg
            - translate the messages in the .po file, remove the #fuzzy
            - python manage.py compilemessages  # apply translations
            - restart the server to see the changes
"""

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Sofia'
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'localization/locale'),
]
LANGUAGES = [
    ('en', 'English'),
    ('bg', 'Bulgarian'),
]


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

# Add this for production (Render):
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


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

# -----------------------------------------------------------------------------
# this is needed for the custom user model
AUTH_USER_MODEL = 'main_app.AppUser'

"""
Create superuser:
python manage.py createsuperuser

Superusers:
Sunzheini, daniel_zorov@abv.bg, Maimun06
"""
