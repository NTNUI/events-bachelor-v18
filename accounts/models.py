from __future__ import unicode_literals

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import datetime
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    customer_no=models.CharField(_('customer no'), unique=True, max_length=20)
    email = models.EmailField(_('email address'), blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    phone = models.CharField(_('phone number'), max_length=12, blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = '{} {}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Contract(models.Model):
    person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contract_type = models.CharField(max_length=3, blank=True)
    expiry_date = models.DateField(default=datetime.date.today, blank=True)
