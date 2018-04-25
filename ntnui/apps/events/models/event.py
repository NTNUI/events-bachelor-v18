import os
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
    waiting_list = models.ManyToManyField(User, verbose_name=_('waiting list'), blank=True)
    sports_groups = models.ManyToManyField(SportsGroup, blank=True, verbose_name=_('hosted by'))

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    def get_cover_upload_to(self, filename):
        name = EventDescription.objects.get(event=self, language=translation.get_language()).name
        return os.path.join(
            "cover_photo/events/{}".format(name.replace(" ", "-")), filename)

    cover_photo = models.ImageField(upload_to=get_cover_upload_to, default='cover_photo/ntnui-volleyball.png')

    def require_payment(self):
        if self.price > 0:
            return True
        return False

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

    # Returns the event's attendees
    def get_attendees(self):
        return EventRegistration.objects.filter(event=self) + self.get_attendees()

    # Checks a given user attends the event
    def attends(self, user):
        if EventRegistration.objects.filter(attendee=user, event=self).exists():
            return True
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
        verbose_name = _('event description')
        verbose_name_plural = _('event descriptions')

    def __str__(self):
        return self.name


class EventRegistration(models.Model):
    """Contains the relation between a user and an event, to  make a list of attendees"""

    registration_time = models.DateTimeField(_('registration time'))
    event = models.ForeignKey(Event, verbose_name='event')
    payment_id = models.CharField(_('Payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee for event')
        verbose_name_plural = _('attendees for event')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email


class EventGuestRegistration(models.Model):
    """Contains the relation between a user and an event, to  make a list of attendees"""

    registration_time = models.DateTimeField(_('registration time'))
    event = models.ForeignKey(Event, verbose_name='event')
    payment_id = models.CharField(_('Payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(Guest, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee for event')
        verbose_name_plural = _('attendees for event')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email


class EventWaitingListRegistration(models.Model):
    """Contains the relation between a user and an event, to  make a list of attendees"""

    registration_time = models.DateTimeField(_('registration time'))
    event = models.ForeignKey(Event, verbose_name='event')
    payment_id = models.CharField(_('Payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee for event')
        verbose_name_plural = _('attendees for event')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email


class EventGuestWaitingListRegistration(models.Model):
    """Contains the relation between a user and an event, to  make a list of attendees"""

    registration_time = models.DateTimeField(_('registration time'))
    event = models.ForeignKey(Event, verbose_name='event')
    payment_id = models.CharField(_('Payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(Guest, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee for event')
        verbose_name_plural = _('attendees for event')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email
