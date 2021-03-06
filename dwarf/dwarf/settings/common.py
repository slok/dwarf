from os.path import abspath, dirname, basename
import datetime


#-------------------------PATH CONFIGURATION-----------------------------------
# Absolute filesystem path to the Django project directory:
# Two levels (../../) -> two dirnames
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
#Three dirnames up from thsi file (../../../)
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
#path.append(DJANGO_ROOT)
#------------------------END PATH CONFIGURATION--------------------------------


#------------------------DEBUG CONFIGURATION-----------------------------------
DEBUG = False

TEMPLATE_DEBUG = DEBUG
#-----------------------END DEBUG CONFIGURATION--------------------------------


#-----------------------MANAGERS CONFIGURATION---------------------------------
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS
#---------------------END MANAGERS CONFIGURATION-------------------------------


#-----------------------DATABASE CONFIGURATION---------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dwarf.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
#---------------------END DATABASE CONFIGURATION-------------------------------

#-----------------------HOSTS CONFIGURATION------------------------------------
# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []
#-----------------------END HOSTS CONFIGURATION--------------------------------

#-----------------------LOCALE CONFIGURATION-----------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True
#-----------------------END LOCALE CONFIGURATION-------------------------------

#--------------------------MEDIA CONFIGURATION---------------------------------
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''
#------------------------END MEDIA CONFIGURATION-------------------------------


#-------------------------STATIC CONFIGURATION---------------------------------
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    SITE_ROOT + "/static",
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
#---------------------END STATIC CONFIGURATION---------------------------------


#-----------------------SECRET KEY CONFIGURATION-------------------------------
# Make this unique, and don't share it with anybody.
#SECRET_KEY = ''
#-----------------------END SECRET KEY CONFIGURATION---------------------------


#-----------------------TEMPLATE CONFIGURATION---------------------------------
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    SITE_ROOT + "/templates",
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'notifications.context_processors.push_notifications_context_processor',
    'linkshortener.context_processors.link_shortener_form_context_processor',
    'dwarfutils.context_processors.current_url_context_processor',
    'django.core.context_processors.request',
)
#---------------------END TEMPLATE CONFIGURATION-------------------------------


#-----------------------MIDDLEWARE CONFIGURATION-------------------------------
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
#---------------------END MIDDLEWARE CONFIGURATION-----------------------------


#--------------------------URL CONFIGURATION-----------------------------------
ROOT_URLCONF = 'dwarf.urls'
#------------------------END URL CONFIGURATION---------------------------------


#-------------------------WSGI CONFIGURATION-----------------------------------
# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'dwarf.wsgi.application'
#-----------------------END WSGI CONFIGURATION---------------------------------


#-------------------------APPS CONFIGURATION-----------------------------------
DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
)

THIRD_PARTY_APPS = (
    'djcelery',
)

LOCAL_APPS = (
    'linkshortener',
    'simple',
    'forwarder',
    'requestdataextractor',
    'clickmanager',
    'dwarfutils',  # Common utils across the app
    'userprofile',
    'homepage',
    'metrics',
    'achievements',
    'notifications',
    'links',
    'level'
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
#-----------------------END APPS CONFIGURATION---------------------------------

#-------------------------AUTH CONFIGURATION-----------------------------------
AUTHENTICATION_BACKENDS = (
    'userprofile.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend'
)
#-----------------------END AUTH CONFIGURATION---------------------------------

#-------------------------GEOIP CONFIGURATION----------------------------------
GEOIP_PATH = ""
#GEOIP_COUNTRY = "GeoIP.dat"
#-----------------------END GEOIP CONFIGURATION--------------------------------

#-------------------------AUTH CONFIGURATION----------------------------------
LOGIN_URL = "/profile/login/"
LOGIN_REDIRECT_URL = "/profile/"
#-----------------------END AUTH CONFIGURATION--------------------------------


#-----------------------LOGGING CONFIGURATION----------------------------------
# Colors
COLOR_RESET = "\x1b[0m"
COLOR_RED = "\x1b[31m"
COLOR_GREEN = "\x1b[32m"
COLOR_YELLOW = "\x1b[33m"
COLOR_BLUE = "\x1b[34m"
COLOR_MAGENTA = "\x1b[35m"
COLOR_CYAN = "\x1b[36m"
COLOR_WHITE = "\x1b[37m"

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {

        'cyan': {
            'format': COLOR_CYAN +\
                      '[%(levelname)s %(asctime)s %(module)s] %(message)s' +\
                      COLOR_RESET
        },

        'red': {
            'format': COLOR_RED +\
                      '[%(levelname)s %(asctime)s %(module)s] %(message)s' +\
                      COLOR_RESET
        },

        'normal': {
            'format': '[%(levelname)s %(asctime)s %(module)s] %(message)s'
        },
    },
    'handlers': {
        'console_debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'cyan'
        },

        'console_error': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'red'
        },

        'file_handler': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'normal',
            'filename': 'dwarf.log',
            'maxBytes': 1024,
            'backupCount': 3,
        },


    },
    'loggers': {
        'dwarf': {
            'handlers': ['console_debug', 'console_error', 'file_handler'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

#######################THIRD PARTY CONFIGURATION###############################

#----------------------END LOGGING CONFIGURATION-------------------------------


#-------------------------REDIS CONFIGURATION----------------------------------
#REDIS_HOST = "127.0.0.1"
#REDIS_PORT = 6379
#REDIS_DB = 0
#REDIS_MAX_CONN = 30

#Redis settings for push notifications
#REDIS_NOTIFICATIONS_HOST = "127.0.0.1"
#REDIS_NOTIFICATIONS_PORT = 6379
#REDIS_NOTIFICATIONS_DB = 1
#REDIS_NOTIFICATIONS_MAX_CONN = 10
#-----------------------END REDIS CONFIGURATION--------------------------------


#-------------------------CELERY CONFIGURATION---------------------------------
import djcelery
djcelery.setup_loader()
#BROKER_URL = 'amqp://guest:guest@localhost:5672/'
#CELERY_RESULT_BACKEND = "amqp"

#----------------------END CELERY CONFIGURATION--------------------------------

############################LOCAL CONFIGURATION################################

#-----------------------LINK SHORTENER CONFIGURATION---------------------------
#START_URL_TOKEN_LENGTH = 4
#ALPHABET = None
#---------------------END LINK SHORTENER CONFIGURATION-------------------------

#-------------------------ACHIEVEMENTS CONFIGURATION---------------------------
ENABLE_ACHIEVEMENTS = True
#-----------------------END ACHIEVEMENTS CONFIGURATION-------------------------

#---------------------PUSH NOTIFICATIONS CONFIGURATION-------------------------
PUSH_NOTIFICATIONS_SERVER_HOST = "127.0.0.1"
PUSH_NOTIFICATIONS_SERVER_PORT = 8001
PUSH_NOTIFICATIONS_SERVER_TYPE = "notifications"
PUSH_NOTIFICATIONS_SERVER_URL = "http://{0}:{1}/{2}".format(
    PUSH_NOTIFICATIONS_SERVER_HOST,
    PUSH_NOTIFICATIONS_SERVER_PORT,
    PUSH_NOTIFICATIONS_SERVER_TYPE
)
#-----------------------END ACHIEVEMENTS CONFIGURATION-------------------------

#-------------------------PASSWORD RESET CONFIGURATION-------------------------
PASSWORD_RESET_TOKEN_MAX_TIME = datetime.timedelta(hours=36)
#---------------------END PASSWORD RESET CONFIGURATION-------------------------
