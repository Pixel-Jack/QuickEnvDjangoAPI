from django.contrib.auth.models import AbstractUser, UnicodeUsernameValidator
from django.contrib.auth.models import UserManager as UserManagerOld
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.user.validators import GenericInternationalPhoneNumberValidator

from .validators import NotEmailValidator


class UserManager(UserManagerOld):
    pass


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    COMMON = 0
    BANNED = 1
    STATUS_CHOICES = (
        (COMMON, 'common'),
        (BANNED, 'banned'),
    )
    # already in abstractUser
    # id
    # email (overwrite here)
    # first_name (overwrite here)
    # date_joined
    # is_active
    # is_staff
    # is_superuser
    # last_login
    # last_name (overwrite here)
    # password
    # username (overwrite here)
    id_status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=COMMON,
    )
    first_name = models.CharField(_('first name'), max_length=255, blank=True)
    last_name = models.CharField(_('last name'), max_length=255, blank=True)
    username = models.CharField(
        _('username'),
        max_length=255,
        unique=True,
        help_text=_('Required. 255 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator, NotEmailValidator()],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )

    phone_number = models.CharField(
        _('phone number'),
        max_length=255,
        blank=True,
        validators=[GenericInternationalPhoneNumberValidator],
        help_text=_('Enter a phone number. This number must be in the generic international format.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    last_login = models.DateTimeField(_('last login'), default=timezone.now)
    is_email_confirmed = models.BooleanField(_('email confirmed'), default=False)
    city = models.CharField(_('city'), max_length=255, blank=True)
    profile_picture = models.URLField(_('Profile picture'), max_length=255, blank=True)  # Todo: link to our assets
    facebook = models.URLField(_('Facebook'), max_length=255, blank=True)
    linkedin = models.URLField(_('LinkedIn'), max_length=255, blank=True)
    google = models.URLField(_('Google'), max_length=255, blank=True)
    twitter = models.URLField(_('Twitter'), max_length=255, blank=True)
    website = models.URLField(_('website'), max_length=255, blank=True)

    objects = UserManager()

    class Meta:
        db_table = 'user'
        indexes = [
            models.Index(fields=['username'], name='username_idx'),
            models.Index(fields=['email'], name='email_idx'),
        ]

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save()
