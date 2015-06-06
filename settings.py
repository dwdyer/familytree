import os.path

# Django settings for familytree project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

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
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media').replace('\\','/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'cj!ui_e^=y5tfsr8ndp+jbxy42giqyj8(b=57l$n^kx3kj+g30'

# Templates
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'), )
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# URLs
ROOT_URLCONF = 'urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
if DEBUG: MIDDLEWARE_CLASSES += ('middleware.QueryCountDebugMiddleware',)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'people',
    'tinymce',
    'taggit',
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
                          'content_css': '/static/tinymce.css',
                          'theme_advanced_resizing': True,
                          'theme_advanced_buttons1': 'bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,|,bullist,numlist,|,outdent,indent,|,link,unlink,|,sub,sup,charmap,|,undo,redo,|,cleanup,code'}

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
