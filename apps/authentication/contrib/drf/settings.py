from copy import deepcopy

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

# DEFAULT settings for this apps, if you want to change some of them you must define them in
# your setting file in an dict named FRONT_AUTHENTICATION
_DEFAULT_SETTINGS = {
    'SUBJECT_TEMPLATE_NAME': 'password_reset_subject.txt',
    'EMAIL_TEMPLATE_NAME': 'password_reset_email.html',
    'SITE_DOMAIN': None,
    'SITE_NAME': None,
    'SITE_USE_HTTPS': False,
    'SITE_NO_REPLY_EMAIL': None,
    'SITE_CONTACT_EMAIL': None,
    'INTERNAL_RESET_URL_TOKEN': 'set-password',
    'INTERNAL_RESET_SESSION_TOKEN': '_password_reset_token',
    'REDIRECT_CONFIRM': 'password-reset/',
    'TOKEN_GENERATOR': default_token_generator,
    'HTML_EMAIL_TEMPLATE_NAME': None
}

INTERNAL_SETTINGS = deepcopy(_DEFAULT_SETTINGS)
INTERNAL_SETTINGS.update(getattr(settings, 'FRONT_AUTHENTICATION', {}))
