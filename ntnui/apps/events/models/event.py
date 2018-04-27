import os
from datetime import datetime

from django.db import models
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from groups.models import SportsGroup
from events.models.tag import Tag
from events.models.guest import Guest
from events.models.restriction import Restriction



class Event(models.Model):
    """Event is the main object, which gets complemented by the rest of the models in different aspects."""

    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    registration_end_date = models.DateTimeField(_('registration end date'), blank=True, null=True)
    place = models.CharField(_('place'), max_length=50, blank=True)
    restriction = models.ForeignKey(Restriction, verbose_name=_('restriction'), default=0)
    attendance_cap = models.IntegerField(_('attendance cap'), blank=True, null=True)
    priority = models.BooleanField(_('priority'), default=False)
    price = models.IntegerField(_('price'), default=0)
    is_host_ntnui = models.BooleanField(_('hosted by NTNUI'), default=False)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))
    sports_groups = models.ManyToManyField(SportsGroup, blank=True, verbose_name=_('hosted by'))

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    def get_cover_upload_to(self, filename):
        name = EventDescription.objects.get(event=self, language=translation.get_language()).name
        return os.path.join(
            "cover_photo/events/{}".format(name.replace(" ", "-")), filename)

    cover_photo = models.ImageField(upload_to=get_cover_upload_to, default='cover_photo/ntnui-volleyball.png')

    # Returns the event's name, in the given language
    def name(self):
        event_name_get_language = EventDescription.objects.filter(event=self, language=translation.get_language())
        event_name_english = EventDescription.objects.filter(event=self, language='en')
        event_name = EventDescription.objects.filter(event=self)

        if event_name_get_language.exists():
            return event_name_get_language[0].name
        elif event_name_english.exists():
            return event_name_english[0].name
        elif event_name.exists():
            return event_name[0].name
        else:
            return 'No name given'

    name.short_description = _('name')

    # Returns the event's description, in the given language
    def description(self):
        event_description_get_language = EventDescription.objects.filter(event=self,
                                                                         language=translation.get_language())
        event_description_english = EventDescription.objects.filter(event=self, language='en')
        event_description = EventDescription.objects.filter(event=self)

        if event_description_get_language.exists():
            return event_description_get_language[0].description_text
        elif event_description_english.exists():
            return event_description_english[0].description_text
        elif event_description.exists():
            return event_description[0].description_text
        else:
            return 'No description given'

    description.short_description = _('description')

    # Returns the event's host(s) as a list
    def get_host(self):
        if self.is_host_ntnui:
            return ['NTNUI']
        groups = []
        for group in self.sports_groups.all():
            groups.append(group.name)
        return groups

    # Checks whether a given user attends the event
    def user_attends(self, user):
        if EventRegistration.objects.filter(attendee=user, event=self).exists():
            return True
        return False

    def attend_event(self, user, payment_id, registration_time):
        EventRegistration.objects.create(event=self, attendee=user,
                                         payment_id=payment_id, registration_time=registration_time)

    def attend_waiting_list(self, user, payment_id, registration_time):
        EventRegistration.objects.create(event=self, attendee=user,
                                         payment_id=payment_id, registration_time=registration_time)
    # Checks whether a given guest attends the event
    def guest_attends(self, guest):
        if EventGuestRegistration.objects.filter(attendee=guest, event=self).exists():
            return True
        return False

    def guest_attend_event(self, guest, payment_id, registration_time):
        EventGuestRegistration.objects.create(event=self, attendee=guest,
                                              payment_id=payment_id, registration_time=registration_time)

    def guest_attend_waiting_list(self, guest, payment_id, registration_time):
        EventGuestWaitingList.objects.create(event=self, attendee=guest,
                                              payment_id=payment_id, registration_time=registration_time)

    # Returns a complete list of the event's attendees
    def get_attendees(self):
        user_attendees = EventRegistration.objects.filter(event=self)
        guest_attendees = EventGuestRegistration.objects.filter(event=self)

        return user_attendees + guest_attendees

    # Checks whether a given user is signed up for the event's waiting list
    def user_on_waiting_list(self, user):
        if EventWaitingList.objects.filter(attendee=user, event=self).exists():
            return True
        return False

    # Checks whether a given guest is signed up for the event's waiting list
    def guest_on_waiting_list(self, guest):
        if EventGuestWaitingList.objects.filter(attendee=guest, event=self).exists():
            return True
        return False

    def waiting_list_count(self):
        users_on_waiting_list = EventWaitingList.objects.filter(event=self).count()
        guests_on_waiting_list = EventGuestWaitingList.objects.filter(event=self).count()
        return users_on_waiting_list + guests_on_waiting_list

    def next_on_waiting_list(self):

        if self.waiting_list_count() > 0:

            user_waiting_list = EventWaitingList.objects.filter(event=self)
            guest_waiting_list = EventGuestWaitingList.objects.filter(event=self)

            waiting_list = list(user_waiting_list) + list(user_waiting_list)
            sorted_waiting_list = sorted(waiting_list, key=lambda attendee: attendee.registration_time, reverse=True)

            next_on_waiting_list = sorted_waiting_list[0]

            if isinstance(next_on_waiting_list, EventWaitingList):
                return 'user', next_on_waiting_list.attendee, next_on_waiting_list.payment_id
            else:
                return 'guest', next_on_waiting_list.attendee, next_on_waiting_list.payment_id

        else:
            return None

    # Checks whether the event is capped out.
    def check_attendance_cap(self):

        # The event has no attendance cap.
        if self.attendance_cap is None:
            return True
        # The event's attendance cap is greater than the amount of attendees.
        elif self.attendance_cap > self.get_attendees().count():
            return True
        # The event's capped out.
        else:
            return False

    def payment_required(self, payment_id):
        """Checks whether the event require payment."""

        # Checks whether the event is free.
        free_event = self.price == 0

        # The event is not free and there exist an payment ID.
        if not free_event and payment_id is not None:
            return True
        # The event is free.
        elif free_event:
            return False
        # Something went wrong.
        else:
            return False

    def check_sign_up_end_date(self):
        if self.registration_end_date > datetime.now():
            return True
        elif self.registration_end_date is None:
            return True
        else:
            return False

    def __str__(self):
        return self.name()


class EventDescription(models.Model):
    """Created to support multiple languages for each event's name and description."""

    name = models.CharField(_('name'), max_length=100)
    description_text = models.CharField(_('description'), max_length=500)
    custom_email_text = models.CharField(_('email text'), max_length=250, null=True, blank=True)
    language = models.CharField(_('language'), max_length=30)
    event = models.ForeignKey(Event, verbose_name=_('event'))

    class Meta:
        verbose_name = _('description')
        verbose_name_plural = _('descriptions')

    def __str__(self):
        return self.name


class EventRegistration(models.Model):
    """Created to let users sign up for events"""

    registration_time = models.DateTimeField(_('registration time'))
    event = models.ForeignKey(Event, verbose_name='event')
    payment_id = models.CharField(_('payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee, user')
        verbose_name_plural = _('attendees, users')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email


class EventWaitingList(models.Model):
    """Created to let users sign up for the waiting list, when an event is capped out"""

    registration_time = models.DateTimeField(_('registration time'))
    event = models.ForeignKey(Event, verbose_name='event')
    payment_id = models.CharField(_('payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('waiting list, user')
        verbose_name_plural = _('waiting list, users')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email


class EventGuestRegistration(models.Model):
    """Created to let guests sign up for events"""

    registration_time = models.DateTimeField(_('registration time'))
    event = models.ForeignKey(Event, verbose_name='event')
    payment_id = models.CharField(_('payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(Guest, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee, guest')
        verbose_name_plural = _('attendees, guests')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email


class EventGuestWaitingList(models.Model):
    """Created to let guests sign up for the waiting list, when an event is capped out"""

    registration_time = models.DateTimeField(_('registration time'))
    event = models.ForeignKey(Event, verbose_name='event')
    payment_id = models.CharField(_('payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(Guest, verbose_name='attendee')

    class Meta:
        verbose_name = _('waiting list, guest')
        verbose_name_plural = _('waiting list, guests')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email

