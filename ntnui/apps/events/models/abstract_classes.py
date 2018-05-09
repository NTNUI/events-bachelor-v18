from django.db import models
from django.utils.translation import gettext_lazy as _

from events.models.tag import Tag


class CommonDescription(models.Model):
    """ Common fields and methods for CategoryDescription, EventDescription and SubEventDescription. """

    name = models.CharField(_('name'), max_length=100)
    language = models.CharField(_('language'), max_length=30)

    class Meta:
        abstract = True


class CommonEvent(models.Model):
    """ Common fields for Event and SubEvent. """

    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    registration_end_date = models.DateTimeField(_('registration end date'), blank=True, null=True)
    price = models.IntegerField(_('price'), default=0)
    attendance_cap = models.IntegerField(_('attendance cap'), blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))

    class Meta:
        abstract = True


class CommonRegistration(models.Model):
    """ Common fields for EventRegistration, EventGuestRegistration, EventWaitingList, EventGuestWaitingList,
        SubEventRegistration, SubEventGuestRegistration, SubEventWaitingList and SubEventGuestWaitingList. """

    registration_time = models.DateTimeField(_('registration time'))
    payment_id = models.CharField(_('payment id'), max_length=100, blank=True, null=True)
    token = models.CharField(_('token'), max_length=60, blank=True, null=True)

    class Meta:
        abstract = True
