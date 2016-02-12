# -*- coding: utf-8 -*-
import os
from django.utils.translation import ugettext_lazy as _


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = True

SESSION_COOKIE_SECURE = False

ADMINS = ()

SERVER_EMAIL = ''

MANAGERS = ADMINS

SITE_URL = 'http://localhost:8000'

SECRET_KEY = 'yourSuperSecretKey'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'DATABASE.sqlite3'),
    }
}

EMAIL_HOST = ''
DEFAULT_FROM_EMAIL = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'baid',
    'accounts',
    'oidc_provider',
    'captcha',
    'social.apps.django_app.default',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',

    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'baid.urls'

WSGI_APPLICATION = 'baid.wsgi.application'

STATIC_URL = '/static/'

STATIC_ROOT = ''

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

LANGUAGE_CODE = 'es-ar'

LANGUAGES = (
    ('es-ar', _(u'Español Argentina')),
    ('en', _(u'Inglés')),
)

TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'accounts.utils.get_username',
    'social.pipeline.social_auth.associate_by_email',
    'accounts.utils.create_user',
    'accounts.utils.save_avatar',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)

SOCIAL_AUTH_LOGIN_ERROR_URL = '/accounts/login/'

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''

SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
RECAPTCHA_USE_SSL = True
RECAPTCHA = False

# Django OpenID Connect Provider

OIDC_AFTER_USERLOGIN_HOOK = 'baid.oidc_provider_settings.after_userlogin_hook'
OIDC_EXTRA_SCOPE_CLAIMS = 'baid.oidc_provider_settings.CustomScopeClaims'
OIDC_IDTOKEN_SUB_GENERATOR = 'baid.oidc_provider_settings.default_sub_generator'
OIDC_USERINFO = 'accounts.models.UserInfo'
