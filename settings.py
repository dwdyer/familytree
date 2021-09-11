from secret_settings import *
import os.path
import socket

# Django settings for familytree project.

DEBUG = socket.gethostname() != HOST
ALLOWED_HOSTS = ['*'] if DEBUG else [DOMAIN]

ADMINS = ((ADMIN_NAME, ADMIN_EMAIL),)
MANAGERS = ADMINS

DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql',
                         'NAME': 'familytree',
                         'USER': 'familytree',
                         'PASSWORD': DATABASE_PASSWORD}}
CONN_MAX_AGE = 0 if DEBUG else 21600 # 6-hour keep-alive (must be <= MySQL's default of 8 hours)
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Locale/iternationalisation
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'
USE_I18N = False
USE_L10N = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/familytree-static'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

MEDIA_URL = '/media/'
MEDIA_ROOT = 'media' if DEBUG else '/var/www/familytree-media'

SITE_ID = 1

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.dirname(__file__), 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {'debug': DEBUG,
                    'context_processors': [
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                        'django.template.context_processors.debug',
                        'django.template.context_processors.media',
                        'django.template.context_processors.request',
                        'django.template.context_processors.static',
                        'django_settings_export.settings_export',
                    ]},
    }
]

SETTINGS_EXPORT = ('MAPBOX_ACCESS_TOKEN', 'ADMIN_NAME', 'ADMIN_EMAIL')

# URLs
ROOT_URLCONF = 'urls'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout/'

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'stronghold.middleware.LoginRequiredMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
if DEBUG: MIDDLEWARE += ('middleware.QueryCountMiddleware',)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    'tinymce',
    'taggit',
    'easy_thumbnails',
    'mathfilters',
    'dbbackup',
    'django_cron',
    'stronghold',
    'people',
)

# TinyMCE configuration
TINYMCE_DEFAULT_CONFIG = {'theme': 'advanced',
                          'relative_urls': False,
                          'plugins': 'paste,autoresize',
                          'width': '100%',
                          'paste_text_sticky': True,
                          'paste_text_sticky_default': True,
                          'paste_text_linebreaktype': 'p',
                          'content_css': '/static/people/css/tinymce.css',
                          'theme_advanced_resizing': True,
                          'theme_advanced_buttons1': 'bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,|,bullist,numlist,|,outdent,indent,|,link,unlink,|,sub,sup,charmap,|,undo,redo,|,cleanup,code'}

# Taggit
TAGGIT_TAGS_FROM_STRING = 'people.forms.tag_comma_splitter'
TAGGIT_STRING_FROM_TAGS = 'people.forms.tag_comma_joiner'

# Back-up
DBBACKUP_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DBBACKUP_CLEANUP_KEEP = 3
DBBACKUP_CLEANUP_KEEP_MEDIA = 1

# Send 500 errors to admins and log DB request counts in DEBUG mode.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {'level': 'ERROR', 'filters': ['require_debug_false'], 'class': 'django.utils.log.AdminEmailHandler'},
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler'},
    },
    'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}},
    'loggers': {
        'django.request': {'handlers': ['mail_admins'], 'level': 'ERROR', 'propagate': True},
        'middleware': {'handlers': ['console'], 'level': 'DEBUG'},
    }
}

# Cron
CRON_CLASSES = [
    'cron.BackupsJob',
]
DJANGO_CRON_DELETE_LOGS_OLDER_THAN = 3 # Keep cron logs for 72 hours.
