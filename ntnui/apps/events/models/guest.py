from django.db import models
from django.utils.translation import gettext_lazy as _


class Guest(models.Model):
    """ Created to make it possible for people who aren't NTNUI members to sign-up for events and sub-events. """

    email = models.EmailField(_('email address'))
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    phone_number = models.IntegerField(_('phone number'))

    class Meta:
        verbose_name = _('guest')
        verbose_name_plural = _('guests')

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)
