from datetime import datetime

from django.db import models
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from events.models.abstract_classes import CommonDescription, CommonEvent, CommonRegistration
from events.models.category import Category
from events.models.guest import Guest


class SubEvent(CommonEvent):
    """ Created to Makes it possible to divide an event into multiple sub-events (e.g. multiple disciplines). """

    category = models.ForeignKey(Category, verbose_name=_('category'))

    class Meta:
        verbose_name = _('sub-event')
        verbose_name_plural = _('sub-events')

    # Finds the browser's language setting, and returns the sub-event's name in the preferred language.
    def name(self):

        # Filter for desirable languages.
        sub_event_description_get_language = SubEventDescription.objects.filter(
            sub_event=self, language=translation.get_language())
        sub_event_description_english = SubEventDescription.objects.filter(sub_event=self, language='en')
        sub_event_description = SubEventDescription.objects.filter(sub_event=self)

        # Checks if the sub-event's name exists in the browser's language.
        if sub_event_description_get_language.exists():
            return sub_event_description_get_language[0].name

        # Checks if the sub-event's name exists in English.
        elif sub_event_description_english.exists():
            return sub_event_description_english[0].name

        # Checks if the sub-event's name exists in any language.
        elif sub_event_description.exists():
            return sub_event_description[0].name

        # No sub-event name exists.
        else:
            return 'No name given'

    # Finds the sub-event's host(s), and returns a list containing them.
    def get_host(self):
        event = self.category.event
        return event.get_host()

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
    def user_attend(self, user, payment_id, registration_time, token):
        SubEventRegistration.objects.create(
            sub_event=self, attendee=user, payment_id=payment_id, registration_time=registration_time, token=token)

    # Enrolls a guest for an sub-event.
    def guest_attend(self, guest, payment_id, registration_time, token):
        SubEventGuestRegistration.objects.create(
            sub_event=self, attendee=guest, payment_id=payment_id, registration_time=registration_time, token=token)

    # Enrolls a user for an sub-event's waiting list.
    def user_attend_waiting_list(self, user, payment_id, registration_time, token):
        SubEventWaitingList.objects.create(
            sub_event=self, attendee=user, payment_id=payment_id, registration_time=registration_time, token=token)

    # Enrolls a guest for an sub-event's waiting list.
    def guest_attend_waiting_list(self, guest, payment_id, registration_time, token):
        SubEventGuestWaitingList.objects.create(
            sub_event=self, attendee=guest, payment_id=payment_id, registration_time=registration_time, token=token)

    # Deletes an sub-event registration for a user.
    def user_attendance_delete(self, user):
        SubEventRegistration.objects.get(event=self, attendee=user).delete()

    # Deletes a user from an sub-event's waiting list.
    def user_waiting_list_delete(self, user, payment_id):
        SubEventWaitingList.objects.get(event=self, attendee=user, payment_id=payment_id).delete()

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

    def __str__(self):
        return self.name()


class SubEventDescription(CommonDescription):
    """ Created to support multiple languages for each sub-event's name and description. """

    custom_email_text = models.CharField(_('email text'), max_length=250, null=True, blank=True)
    sub_event = models.ForeignKey(SubEvent, verbose_name=_('sub-event'))

    class Meta:
        verbose_name = _('description')
        verbose_name_plural = _('descriptions')


class SubEventRegistration(CommonRegistration):
    """ Created to let users sign up for sub-events. """

    sub_event = models.ForeignKey(SubEvent, verbose_name='sub-event')
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee, user')
        verbose_name_plural = _('attendees, users')
        unique_together = ('sub_event', 'attendee')

    def __str__(self):
        return self.sub_event.name() + ' - ' + self.attendee.email


class SubEventWaitingList(CommonRegistration):
    """ Created to let users sign up for the waiting list, when an sub-event is capped out. """

    sub_event = models.ForeignKey(SubEvent, verbose_name='sub-event')
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('waiting list, user')
        verbose_name_plural = _('waiting list, users')
        unique_together = ('sub_event', 'attendee')

    def __str__(self):
        return self.sub_event.name() + ' - ' + self.attendee.email


class SubEventGuestRegistration(CommonRegistration):
    """ Created to let guests sign up for sub-events. """

    sub_event = models.ForeignKey(SubEvent, verbose_name='sub-event')
    attendee = models.ForeignKey(Guest, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee, guest')
        verbose_name_plural = _('attendees, guests')
        unique_together = ('sub_event', 'attendee')

    def __str__(self):
        return self.sub_event.name() + ' - ' + self.attendee.email


class SubEventGuestWaitingList(CommonRegistration):
    """ Created to let guests sign up for the waiting list, when an sub-event is capped out. """

    sub_event = models.ForeignKey(SubEvent, verbose_name='sub-event')
    attendee = models.ForeignKey(Guest, verbose_name='attendee')

    class Meta:
        verbose_name = _('waiting list, guest')
        verbose_name_plural = _('waiting list, guests')
        unique_together = ('sub_event', 'attendee')

    def __str__(self):
        return self.sub_event.name() + ' - ' + self.attendee.email
