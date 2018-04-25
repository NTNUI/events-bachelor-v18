from django.db import models
from django.utils.translation import gettext_lazy as _


class Guest(models.Model):
    """Guest makes it possible to sign up for events and sub events when the user ain't a member of NTNUI."""

    email = models.EmailField(_('email address'))
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    phone_number = models.IntegerField(_('phone number'))

    class Meta:
        verbose_name = _('guest')
        verbose_name_plural = _('guests')

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)