import os
import sys
from django.utils.translation import ugettext_lazy as _


PRODUCTION = False

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# TODO: Fix this before deployment - See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/
SECRET_KEY = 'cpivc$!*6-)c(u4k+bw-+cv*j1omilwt)#@#dezn6jb%m)j$y+'
STRIPE_SECRET_KEY = 'None given'
STRIPE_PUBLIC_KEY = 'pk_test_TagT9jGDj7CN9NOQfTnueTxz'



# SECURITY WARNING: don't run with debug turned on in production!
if PRODUCTION:
    DEBUG = False
else:
    DEBUG = True

ALLOWED_HOSTS = [
    'beta.ntnui.no',
    'localhost',
    '10.22.72.17'
]

##### APP CONFIGURATION #####
DJANGO_APPS = [
    # Default Django Apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rules.apps.AutodiscoverRulesConfig',
    # Admin panel
    'django.contrib.admin',
]

THIRD_PARTY_APPS = [
    'django_nose',
    'widget_tweaks',
]

LOCAL_APPS = [
    'accounts',
    'hs',
    'events',
    'groups',
    'forms'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

##### END APP CONFIGURATION ####

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ntnui.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

##### DATABASE CONFIGURATION #####

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'dev_database.db'),
    }
}

if os.environ.get('DATABASE_URL'):
    db_from_env = dj_database_url.config(conn_max_age=500)
    DATABASES['default'].update(db_from_env)
    print('Using DB from environment variable.')
else:
    print('Using default file-based DB.')

##### END DATABASE CONFIGURATION #####

##### AUTHENTICATION CONFIGURATION #####

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

AUTH_USER_MODEL = "accounts.User"
AUTH_GROUPIMAGE_MODEL = "groups.GroupImage"

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

##### END AUTHENTICATION CONFIGURATION #####

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en'


TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('en', _('English')),
    ('nb', _('Norwegian (bokmal)')),
)


##### STATIC FILE CONFIGURATION #####

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

MEDIA_URL = 'static/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static')

##### END STATIC FILE CONFIGURATION #####



##### MAILGUN SETTINGS #####

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'postmaster@mg.ntnui.no'
EMAIL_HOST_PASSWORD = os.environ.get('MAILGUN_PASSWORD')
EMAIL_USE_TLS = True


##### LOGIN CONFIGURATION #####
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# USER settings
DUMMY_USER_EMAIL = 'todd.packer@online.com'
DUMMY_USER_PASSWORD = 'locoloco'

##### END LOGIN CONFIGURATION #####

##### TEST CONFIGURATION #####
# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=groups, forms, accounts, events',
    '--cover-html',
    '--nocapture',
    '--nologcapture',
 ]
##### END TEST CONFIGURATION #####

##### SET STRIPE KEYS #####
if PRODUCTION and os.environ.get('STRIPE_SECRET_KEY_LIVE'):
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY_LIVE')
    STRIPE_PUBLIC_KEY = 'pk_live_SegObZmdoJnJQBGx0RQpCJcd'
elif os.environ.get('STRIPE_SECRET_KEY_TEST'):
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY_TEST')


