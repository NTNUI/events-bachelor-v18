from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from events.models.tag import Tag


class CommonDescription(models.Model):
    """ Common fields and methods for CategoryDescription, EventDescription and SubEventDescription. """

    name = models.CharField(_('name'), max_length=100)
    language = models.CharField(_('language'), max_length=30)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class CommonEvent(models.Model):
    """ Common fields for Event and SubEvent. """

    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    registration_end_date = models.DateTimeField(_('registration end date'), blank=True, null=True)
    price = models.IntegerField(_('price'), default=0)
    attendance_cap = models.IntegerField(_('attendance cap'), blank=True, null=True)
    tags = models.ManyToManyField(Tag, verbose_name=_('tags'), blank=True)

    class Meta:
        abstract = True

    # Checks if the event's attendance capacity is exceeded.
    def is_attendance_cap_exceeded(self):
        return self.attendance_cap is not None and self.attendance_cap <= len(self.get_attendee_list())

    # Checks if the event's registration has ended.
    def is_registration_ended(self):
        return self.registration_end_date is not None and \
               self.registration_end_date.replace(tzinfo=None) < datetime.now()

    # Checks if the sub-event requires payment.
    def is_payment_event(self):
        return self.price > 0

    # Checks if a payment is created and that the sub-event require payment.
    def is_payment_created(self, payment_id):
        return payment_id is not None and self.is_payment_event()


class CommonRegistration(models.Model):
    """ Common fields for EventRegistration, EventGuestRegistration, EventWaitingList, EventGuestWaitingList,
        SubEventRegistration, SubEventGuestRegistration, SubEventWaitingList and SubEventGuestWaitingList. """

    registration_time = models.DateTimeField(_('registration time'))
    payment_id = models.CharField(_('payment id'), max_length=100, blank=True,   null=True)
    token = models.CharField(_('token'), max_length=60, blank=True, null=True)

    class Meta:
        abstract = True
