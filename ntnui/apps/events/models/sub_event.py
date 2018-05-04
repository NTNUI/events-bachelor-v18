from datetime import datetime
from django.db import models
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from events.models.tag import Tag
from events.models.guest import Guest
from events.models.category import Category


class SubEvent(models.Model):
    """Makes it possible to divide an event into multiple sub-events (e.g. multiple disciplines)."""

    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    registration_end_date = models.DateTimeField(_('registration end date'), blank=True, null=True)
    price = models.IntegerField(_('price'), default=0)
    attendance_cap = models.IntegerField(_('attendance cap'), blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))
    category = models.ForeignKey(Category, verbose_name=_('category'))

    class Meta:
        verbose_name = _('sub-event')
        verbose_name_plural = _('sub-events')

    # Returns the name of the sub-event, in the given language.
    def name(self):
        sub_event_description_get_language = SubEventDescription.objects.filter(sub_event=self,
                                                                                language=translation.get_language())
        sub_event_description_english = SubEventDescription.objects.filter(sub_event=self, language='en')
        sub_event_description = SubEventDescription.objects.filter(sub_event=self)

        if sub_event_description_get_language.exists():
            return sub_event_description_get_language[0].name
        elif sub_event_description_english.exists():
            return sub_event_description_english[0].name
        elif sub_event_description.exists():
            return sub_event_description[0].name
        else:
            return 'No name given'

    # Returns the sub-event's attendee list consisting of users and guests.
    def get_attendee_list(self):
        return list(SubEventRegistration.objects.filter(sub_event=self)) + \
               list(SubEventGuestRegistration.objects.filter(sub_event=self))

    # Returns the sub-event's waiting list consisting of users and guests.
    def get_waiting_list(self):
        return list(SubEventWaitingList.objects.filter(sub_event=self)) + \
               list(SubEventGuestWaitingList.objects.filter(sub_event=self))

    # Returns the next user or guest on the sub-event's waiting list.
    def get_waiting_list_next(self):
        waiting_list = self.get_waiting_list()
        if len(waiting_list) > 0:
            # Sorts the waiting list by registration date.
            # Returns the first attendee and its payment for the sub-event.
            sorted_waiting_list = sorted(waiting_list, key=lambda attendee: attendee.registration_time)
            next_on_waiting_list = sorted_waiting_list[0]
            return next_on_waiting_list.attendee, next_on_waiting_list.payment_id
        return None

    # Enrolls a user for an sub-event.
    def user_attend(self, user, payment_id, registration_time):
        SubEventRegistration.objects.create(sub_event=self, attendee=user, payment_id=payment_id,
                                            registration_time=registration_time)

    # Enrolls a guest for an sub-event.
    def guest_attend(self, guest, payment_id, registration_time):
        SubEventGuestRegistration.objects.create(sub_event=self, attendee=guest, payment_id=payment_id,
                                                 registration_time=registration_time)

    # Enrolls a user for an sub-event's waiting list.
    def user_attend_waiting_list(self, user, payment_id, registration_time):
        SubEventWaitingList.objects.create(sub_event=self, attendee=user, payment_id=payment_id,
                                           registration_time=registration_time)

    # Enrolls a guest for an sub-event's waiting list.
    def guest_attend_waiting_list(self, guest, payment_id, registration_time):
        SubEventGuestWaitingList.objects.create(sub_event=self, attendee=guest, payment_id=payment_id,
                                                registration_time=registration_time)

    # Deletes an event registration for a user.
    def user_attendance_delete(self, user):
        SubEventRegistration.objects.get(event=self, attendee=user).delete()

    # Deletes an event registration for a guest.
    def guest_attendance_delete(self, guest):
        SubEventGuestRegistration.objects.get(event=self, attendee=guest).delete()

    # Deletes a user from an event's waiting list.
    def user_waiting_list_delete(self, user, payment_id, registration_time):
        SubEventWaitingList.objects.get(event=self, attendee=user, payment_id=payment_id,
                                        registration_time=registration_time).delete()

    # Deletes a guest from an event's waiting list.
    def guest_waiting_list_delete(self, guest, payment_id, registration_time):
        SubEventGuestWaitingList.objects.get(event=self, attendee=guest, payment_id=payment_id,
                                             registration_time=registration_time).delete()

    # Checks if a user attends the sub-event.
    def is_user_enrolled(self, user):
        return SubEventRegistration.objects.filter(attendee=user, sub_event=self).exists()

    # Checks if a guest attends the sub-event.
    def is_guest_enrolled(self, guest):
        return SubEventGuestRegistration.objects.filter(attendee=guest, sub_event=self).exists()

    # Checks if a user is on the sub-event's waiting list.
    def is_user_on_waiting_list(self, user):
        return SubEventWaitingList.objects.filter(attendee=user, sub_event=self).exists()

    # Checks if a guest is on the sub-event's waiting list.
    def is_guest_on_waiting_list(self, guest):
        return SubEventGuestWaitingList.objects.filter(attendee=guest, sub_event=self).exists()

    # Checks if the sub-event's attendance capacity is exceeded.
    def is_attendance_cap_exceeded(self):
        return self.attendance_cap is not None and self.attendance_cap < len(self.get_attendee_list())

    # Checks if the sub-event's registration has ended.
    def is_registration_ended(self):
        return self.registration_end_date is not None and \
               self.registration_end_date.replace(tzinfo=None) < datetime.now()

    # Checks if the sub-event requires payment.
    def is_payment_event(self):
        return self.price > 0

    # Checks if a payment is created and that the sub-event require payment.
    def is_payment_created(self, payment_id):
        return payment_id is not None and self.is_payment_event()

    def __str__(self):
        return self.name()


class SubEventDescription(models.Model):
    """Created to support multiple languages for each sub-event's name and description."""

    name = models.CharField(_('name'), max_length=100)
    language = models.CharField(_('language'), max_length=30)
    custom_email_text = models.CharField(_('email text'), max_length=250, null=True, blank=True)
    sub_event = models.ForeignKey(SubEvent, verbose_name=_('sub-event'))

    class Meta:
        verbose_name = _('description')
        verbose_name_plural = _('descriptions')

    def __str__(self):
        return self.name


class SubEventRegistration(models.Model):
    """Created to let users sign up for sub-events"""

    registration_time = models.DateTimeField(_('registration time'))
    sub_event = models.ForeignKey(SubEvent, verbose_name='sub-event')
    payment_id = models.CharField(_('payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee, users')
        verbose_name_plural = _('attendees, users')
        unique_together = ('sub_event', 'attendee')

    def __str__(self):
        return self.sub_event.name() + ' - ' + self.attendee.email


class SubEventWaitingList(models.Model):
    """Created to let users sign up for the waiting list, when an sub-event is capped out"""

    registration_time = models.DateTimeField(_('registration time'))
    sub_event = models.ForeignKey(SubEvent, verbose_name='sub-event')
    payment_id = models.CharField(_('payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('waiting list, user')
        verbose_name_plural = _('waiting list, users')
        unique_together = ('sub_event', 'attendee')

    def __str__(self):
        return self.sub_event.name() + ' - ' + self.attendee.email


class SubEventGuestRegistration(models.Model):
    """Created to let guests sign up for sub-events"""

    registration_time = models.DateTimeField(_('registration time'))
    sub_event = models.ForeignKey(SubEvent, verbose_name='event')
    payment_id = models.CharField(_('payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(Guest, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee, guest')
        verbose_name_plural = _('attendees, guests')
        unique_together = ('sub_event', 'attendee')

    def __str__(self):
        return self.sub_event.name() + ' - ' + self.attendee.email


class SubEventGuestWaitingList(models.Model):
    """Created to let guests sign up for the waiting list, when an sub-event is capped out"""

    registration_time = models.DateTimeField(_('registration time'))
    sub_event = models.ForeignKey(SubEvent, verbose_name='event')
    payment_id = models.CharField(_('payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(Guest, verbose_name='attendee')

    class Meta:
        verbose_name = _('waiting list, guest')
        verbose_name_plural = _('waiting list, guests')
        unique_together = ('sub_event', 'attendee')

    def __str__(self):
        return self.sub_event.name() + ' - ' + self.attendee.email
