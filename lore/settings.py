"""
Django settings for lore project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
import ast
import os
import platform

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
import yaml

VERSION = '0.13.0'

CONFIG_PATHS = [
    os.environ.get('LORE_CONFIG', ''),
    os.path.join(os.getcwd(), 'lore.yml'),
    os.path.join(os.path.expanduser('~'), 'lore.yml'),
    '/etc/lore.yml',
]


def load_fallback():
    """Load optional yaml config."""
    fallback_config = {}
    config_file_path = None
    for config_path in CONFIG_PATHS:
        if os.path.isfile(config_path):
            config_file_path = config_path
            break
    if config_file_path is not None:
        with open(config_file_path) as config_file:
            fallback_config = yaml.safe_load(config_file)
    return fallback_config

FALLBACK_CONFIG = load_fallback()


def get_var(name, default):
    """Return the settings in a precedence way with default."""
    try:
        value = os.environ.get(name, FALLBACK_CONFIG.get(name, default))
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_var(
    'SECRET_KEY',
    '36boam8miiz0c22il@3&gputb=wrqr2plah=0#0a_bknw9(2^r'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_var('DEBUG', False)

ALLOWED_HOSTS = get_var('ALLOWED_HOSTS', [])


# Application definition

INSTALLED_APPS = (
    # CAUTION: the cas app must be loaded first as its settings are
    # applied on application and it makes changes to other application
    # settings like django.contrib.admin and django.contrib.auth which
    # it modifies, and must do so before they are loaded.
    'cas',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'elastic_panel',
    'storages',
    'compressor',
    'bootstrap3',
    'guardian',
    'audit',
    'learningresources',
    'importer',
    'exporter',
    'ui',
    'taxonomy',
    'rest',
    'rest_framework',
    'search',
    'roles',
    'xanalytics',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

ROOT_URLCONF = 'ui.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/lore/templates/'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
            ],
        },
    },
]

# Settings to export to templates
SETTINGS_EXPORT = [
    'GOOGLE_ANALYTICS_ID',
]

WSGI_APPLICATION = 'lore.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
# Uses DATABASE_URL to configure with sqlite default:
# For URL structure:
# https://github.com/kennethreitz/dj-database-url
DEFAULT_DATABASE_CONFIG = dj_database_url.parse(
    get_var(
        'DATABASE_URL',
        'sqlite:///{0}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))
    )
)
# Enable SSL
if get_var('LORE_DB_DISABLE_SSL', False):
    DEFAULT_DATABASE_CONFIG['OPTIONS'] = {}
else:
    DEFAULT_DATABASE_CONFIG['OPTIONS'] = {'sslmode': 'require'}

DATABASES = {
    'default': DEFAULT_DATABASE_CONFIG
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "lore_indexing": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": get_var("LORE_INDEXING_CACHE_TIMEOUT", "60"),
    },
    "compressor": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

# Serve static files with dj-static
STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'
STATICFILES_FINDERS = (
    # defaults
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # custom finders
    'compressor.finders.CompressorFinder',
)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'ui', 'static'),
)
COMPRESS_PRECOMPILERS = (
    ('text/requirejs', 'requirejs.RequireJSCompiler'),
    (
        'text/jsx',
        'node node_modules/react-tools/bin/jsx < {infile} > {outfile}'
    ),
)
COMPRESS_OFFLINE = get_var('LORE_COMPRESS_OFFLINE', False)
COMPRESS_ENABLED = get_var('LORE_COMPRESS_ENABLED', not DEBUG)
COMPRESS_CACHEABLE_PRECOMPILERS = ('text/jsx',)
COMPRESS_CACHE_BACKEND = 'compressor'

# Media and storage settings
IMPORT_PATH_PREFIX = get_var('LORE_IMPORT_PATH_PREFIX', 'course_archives/')
EXPORT_PATH_PREFIX = get_var('LORE_EXPORT_PATH_PREFIX', 'resource_exports/')
MEDIA_ROOT = get_var('MEDIA_ROOT', '/tmp/')
MEDIA_URL = '/media/'
LORE_USE_S3 = get_var('LORE_USE_S3', False)
AWS_ACCESS_KEY_ID = get_var('AWS_ACCESS_KEY_ID', False)
AWS_SECRET_ACCESS_KEY = get_var('AWS_SECRET_ACCESS_KEY', False)
AWS_STORAGE_BUCKET_NAME = get_var('AWS_STORAGE_BUCKET_NAME', False)
# Provide nice validation of the configuration
if(
        LORE_USE_S3 and
        (not AWS_ACCESS_KEY_ID or
         not AWS_SECRET_ACCESS_KEY or
         not AWS_STORAGE_BUCKET_NAME)
):
    raise ImproperlyConfigured(
        'You have enabled S3 support, but are missing one of '
        'AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, or '
        'AWS_STORAGE_BUCKET_NAME'
    )
# Swap the storage
if LORE_USE_S3:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
else:
    # by default use django.core.files.storage.FileSystemStorage with
    # overwrite feature
    DEFAULT_FILE_STORAGE = 'storages.backends.overwrite.OverwriteStorage'


# Lore preview settings
LORE_PREVIEW_BASE_URL = get_var(
    'LORE_PREVIEW_BASE_URL', 'https://www.sandbox.edx.org/')


# Configure e-mail settings
EMAIL_HOST = get_var('LORE_EMAIL_HOST', 'localhost')
EMAIL_PORT = get_var('LORE_EMAIL_PORT', 25)
EMAIL_HOST_USER = get_var('LORE_EMAIL_USER', '')
EMAIL_HOST_PASSWORD = get_var('LORE_EMAIL_PASSWORD', '')
EMAIL_USE_TLS = get_var('LORE_EMAIL_TLS', False)
EMAIL_SUPPORT = get_var('LORE_SUPPORT_EMAIL', 'support@example.com')
DEFAULT_FROM_EMAIL = get_var('LORE_FROM_EMAIL', 'webmaster@localhost')

# e-mail configurable admins
ADMIN_EMAIL = get_var('LORE_ADMIN_EMAIL', '')
if ADMIN_EMAIL is not '':
    ADMINS = (('Admins', ADMIN_EMAIL),)
else:
    ADMINS = ()

CAS_ENABLED = get_var('LORE_USE_CAS', False)
CAS_SERVER_URL = get_var(
    'LORE_CAS_URL', 'https://example.com'
)

LOGIN_URL = "/admin/"

# Logging configuration
LOG_LEVEL = get_var('LORE_LOG_LEVEL', 'DEBUG')
DJANGO_LOG_LEVEL = get_var('DJANGO_LOG_LEVEL', 'DEBUG')
ES_LOG_LEVEL = get_var('ES_LOG_LEVEL', 'INFO')

# For logging to a remote syslog host
LOG_HOST = get_var('LORE_LOG_HOST', 'localhost')
LOG_HOST_PORT = get_var('LORE_LOG_HOST_PORT', 514)

HOSTNAME = platform.node().split('.')[0]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'formatters': {
        'verbose': {
            'format': (
                '[%(asctime)s] %(levelname)s %(process)d [%(name)s] '
                '%(filename)s:%(lineno)d - '
                '[{hostname}] - %(message)s'
            ).format(hostname=HOSTNAME),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'syslog': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local7',
            'formatter': 'verbose',
            'address': (LOG_HOST, LOG_HOST_PORT)
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'root': {
            'handlers': ['console', 'syslog'],
            'level': LOG_LEVEL,
        },
        'django': {
            'propagate': True,
            'level': DJANGO_LOG_LEVEL,
            'handlers': ['console', 'syslog'],
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': True,
        },
        'urllib3': {
            'level': 'INFO',
        },
        'elasticsearch': {
            'level': ES_LOG_LEVEL,
        },
    },
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'elastic_panel.panel.ElasticDebugPanel'
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest.pagination.LorePagination',
    'UPLOADED_FILES_USE_URL': False,
}

# Celery
BROKER_URL = get_var("BROKER_URL", get_var("REDISCLOUD_URL", None))
CELERY_RESULT_BACKEND = get_var(
    "CELERY_RESULT_BACKEND", get_var("REDISCLOUD_URL", None)
)
CELERY_ALWAYS_EAGER = get_var("CELERY_ALWAYS_EAGER", True)
CELERY_EAGER_PROPAGATES_EXCEPTIONS = get_var(
    "CELERY_EAGER_PROPAGATES_EXCEPTIONS", True)

# guardian specific settings
ANONYMOUS_USER_ID = None
GUARDIAN_RAISE_403 = True

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'URL': get_var('HAYSTACK_URL', 'http://127.0.0.1:9200'),
        'INDEX_NAME': get_var('HAYSTACK_INDEX', 'haystack'),
    }
}

XANALYTICS_URL = get_var('XANALYTICS_URL', "")

# Token required to access the status page.
STATUS_TOKEN = get_var(
    "STATUS_TOKEN",
    "7E17C32A63B2810F0053DE454FC8395CA3262CCB8392D2307887C5E67F132550"
)

# Statsd client config
STATSD_HOST = get_var('LORE_STATSD_HOST', 'localhost')
STATSD_PORT = get_var('LORE_STATSD_PORT', 8125)
STATSD_PREFIX = get_var('LORE_STATSD_PREFIX', None)
STATSD_MAXUDPSIZE = get_var('LORE_STATSD_MAXUDPSIZE', 512)

# Required for Django Debug Toolbar
INTERNAL_IPS = (get_var('HOST_IP', '127.0.0.1'), )

# Google analytics code
GOOGLE_ANALYTICS_ID = get_var('LORE_GOOGLE_ANALYTICS_ID', None)

# This is needed to connect the signals properly.
# pylint: disable=unused-import
import search.signals  # noqa
