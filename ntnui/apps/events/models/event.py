import os
from datetime import datetime

from django.db import models
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from events.models.abstract_classes import (CommonDescription, CommonEvent,
                                            CommonRegistration)
from events.models.guest import Guest
from events.models.restriction import Restriction
from groups.models import SportsGroup


class Event(CommonEvent):
    """ Event is the main model, which gets complemented by the rest of the models in different aspects. """

    place = models.CharField(_('place'), max_length=50, blank=True)
    restriction = models.ForeignKey(Restriction, verbose_name=_('restriction'), default=0)
    is_host_ntnui = models.BooleanField(_('hosted by NTNUI'), default=False)
    sports_groups = models.ManyToManyField(SportsGroup, verbose_name=_('hosted by'), blank=True)
    priority = models.BooleanField(_('priority'), default=False)

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    # Gets the path to the image folder.
    def get_cover_upload_to(self, filename):
        name = EventDescription.objects.get(event=self, language=translation.get_language()).name
        return os.path.join(
            'cover_photo/events/{}'.format(name.replace(' ', '-')), filename)

    cover_photo = models.ImageField(upload_to=get_cover_upload_to, default='cover_photo/events/ntnui-volleyball.png')

    # Finds the browser's language setting, and returns the event's name in the preferred language.
    def name(self):

        # Filter for desirable languages.
        browser_language_event_name = EventDescription.objects.filter(event=self, language=translation.get_language())
        english_event_name = EventDescription.objects.filter(event=self, language='en')
        any_event_name = EventDescription.objects.filter(event=self)

        # Checks if the event's name exists in the browser's language.
        if browser_language_event_name.exists():
            return browser_language_event_name[0].name

        # Checks if the event's name exists in English.
        elif english_event_name.exists():
            return english_event_name[0].name

        # Checks if the event's name exists in any language.
        elif any_event_name.exists():
            return any_event_name[0].name

        # No event name exists.
        else:
            return 'No name given'

    name.short_description = _('name')

    # Finds the browser's language setting, and returns the event's description in the preferred language.
    def description(self):

        # Filter for desirable languages.
        event_description_get_language = EventDescription.objects.filter(
            event=self, language=translation.get_language())
        event_description_english = EventDescription.objects.filter(event=self, language='en')
        event_description = EventDescription.objects.filter(event=self)

        # Checks if there exists an event description in the browser's language.
        if event_description_get_language.exists():
            return event_description_get_language[0].description_text

        # Checks if there exists an English event description.
        elif event_description_english.exists():
            return event_description_english[0].description_text

        # Checks if there exists any event description.
        elif event_description.exists():
            return event_description[0].description_text

        # No event description exists.
        else:
            return 'No description given'

    description.short_description = _('description')

    # Finds the event's host(s), and returns a list containing the host(s).
    def get_host(self):

        # Checks if NTNUI is hosting the event.
        if self.is_host_ntnui:
            return ['NTNUI']

        # Gets the group(s) hosting the event.
        groups = []
        for group in self.sports_groups.all():
            groups.append(group.name)
        return groups

    # Returns the event's attendee list consisting of users and guests.
    def get_attendee_list(self):
        return list(EventRegistration.objects.filter(event=self)) + \
               list(EventGuestRegistration.objects.filter(event=self))

    # Returns the event's waiting list consisting of users and guests.
    def get_waiting_list(self):
        return list(EventWaitingList.objects.filter(event=self)) + \
               list(EventGuestWaitingList.objects.filter(event=self))

    # Returns the next user or guest on the event's waiting list.
    def get_waiting_list_next(self):
        waiting_list = self.get_waiting_list()
        if len(waiting_list) > 0:
            # Sorts the waiting list by registration date.
            # Returns the first attendee and its payment for the event.
            sorted_waiting_list = sorted(waiting_list, key=lambda attendee: attendee.registration_time)
            next_on_waiting_list = sorted_waiting_list[0]
            return next_on_waiting_list.attendee, next_on_waiting_list.payment_id
        return None

    # Enrolls a user for an event.
    def user_attend(self, user, payment_id, registration_time, token):
        EventRegistration.objects.create(
            event=self, attendee=user, payment_id=payment_id, registration_time=registration_time, token=token)

    # Enrolls a guest for an event.
    def guest_attend(self, guest, payment_id, registration_time, token):
        EventGuestRegistration.objects.create(
            event=self, attendee=guest, payment_id=payment_id, registration_time=registration_time, token=token)

    # Enrolls a user for an event's waiting list.
    def user_attend_waiting_list(self, user, payment_id, registration_time, token):
        EventWaitingList.objects.create(
            event=self, attendee=user, payment_id=payment_id, registration_time=registration_time, token=token)

    # Enrolls a guest for an event's waiting list.
    def guest_attend_waiting_list(self, guest, payment_id, registration_time, token):
        EventGuestWaitingList.objects.create(
            event=self, attendee=guest, payment_id=payment_id, registration_time=registration_time, token=token)

    # Delete a event registration for a user.
    def user_attendance_delete(self, user):
        EventRegistration.objects.get(event=self, attendee=user).delete()

    # Enrolls a user for an event's waiting list.
    def user_waiting_list_delete(self, user):
        EventWaitingList.objects.get(event=self, attendee=user).delete()

    # Checks if a user attends the event.
    def is_user_enrolled(self, user):
        return EventRegistration.objects.filter(attendee=user, event=self).exists()

    # Checks if a guest attends the event.
    def is_guest_enrolled(self, guest):
        return EventGuestRegistration.objects.filter(attendee=guest, event=self).exists()

    # Checks if a user is on the event's waiting list.
    def is_user_on_waiting_list(self, user):
        return EventWaitingList.objects.filter(attendee=user, event=self).exists()

    # Checks if a guest is on the event's waiting list.
    def is_guest_on_waiting_list(self, guest):
        return EventGuestWaitingList.objects.filter(attendee=guest, event=self).exists()

    # Finds the subEvents associated with the event
    def get_sub_events(self):
        from events.models.sub_event import SubEvent
        from events.models.category import Category
        return SubEvent.objects.filter(category__in=Category.objects.filter(event=self))

    def __str__(self):
        return self.name()


class EventDescription(CommonDescription):
    """ Created to support multiple languages for each event's name and description. """

    event = models.ForeignKey(Event, verbose_name=_('event'))
    description_text = models.CharField(_('description'), max_length=500)
    custom_email_text = models.CharField(_('email text'), max_length=250, null=True, blank=True)

    class Meta:
        verbose_name = _('description')
        verbose_name_plural = _('descriptions')


class EventRegistration(CommonRegistration):
    """ Created to let users sign up for events. """

    event = models.ForeignKey(Event, verbose_name='event')
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee, user')
        verbose_name_plural = _('attendees, users')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email


class EventWaitingList(CommonRegistration):
    """ Created to let users sign up for the waiting list, when an event is capped out. """

    event = models.ForeignKey(Event, verbose_name='event')
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('waiting list, user')
        verbose_name_plural = _('waiting list, users')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email


class EventGuestRegistration(CommonRegistration):
    """ Created to let guests sign up for events. """

    event = models.ForeignKey(Event, verbose_name='event')
    attendee = models.ForeignKey(Guest, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee, guest')
        verbose_name_plural = _('attendees, guests')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email


class EventGuestWaitingList(CommonRegistration):
    """ Created to let guests sign up for the waiting list, when an event is capped out. """

    event = models.ForeignKey(Event, verbose_name='event')
    attendee = models.ForeignKey(Guest, verbose_name='attendee')

    class Meta:
        verbose_name = _('waiting list, guest')
        verbose_name_plural = _('waiting list, guests')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email
