from secret_settings import *
import os.path

# Django settings for familytree project.

DEBUG = True
ALLOWED_HOSTS = ['*'] if DEBUG else []

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql',
                         'NAME': 'familytree',
                         'USER': 'familytree',
                         'PASSWORD': 'familytree'}}
CONN_MAX_AGE = 0 if DEBUG else 21600 # 6-hour keep-alive (must be <= MySQL's default of 8 hours)

# Locale/iternationalisation
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'
USE_I18N = False
USE_L10N = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/familytree-static'
STATICFILES_DIRS = (os.path.join(os.path.dirname(__file__), 'static'), )
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

MEDIA_URL = '/media/'
MEDIA_ROOT = 'media' if DEBUG else '/var/www/familytree-resources'

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
                        'django.template.context_processors.debug',
                        'django.template.context_processors.media',
                        'django.template.context_processors.static',
                        'django_settings_export.settings_export',
                    ]},
    }
]

SETTINGS_EXPORT = ('MAPBOX_PROJECT_ID', 'MAPBOX_ACCESS_TOKEN')

# URLs
ROOT_URLCONF = 'urls'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/people/'
LOGOUT_URL = '/logout/'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'middleware.LoginRequiredMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
if DEBUG: MIDDLEWARE_CLASSES += ('middleware.QueryCountMiddleware',)

INSTALLED_APPS = (
    'people',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'tinymce',
    'taggit',
    'easy_thumbnails',
    'mathfilters',
    'dbbackup',
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

# Back-up
DBBACKUP_STORAGE = 'storages.backends.dropbox.DropBoxStorage'
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
