from datetime import datetime
from django.db import models
from groups.models import SportsGroup
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from accounts.models import User
from django.core.urlresolvers import reverse


"""
Creates a model for events, with start date, end date, priority, host group and ntnui as host.
If ntnui is host, is_host_ntnui is true, otherwise false.
"""
class Event(models.Model):

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    priority = models.BooleanField(_('priority'), default=False)
    is_host_ntnui = models.BooleanField(_('hosted by NTNUI'), default=False)
    sports_groups = models.ManyToManyField(SportsGroup, blank=True, verbose_name=_('hosted by'))

    """Returnes the name of the event, in the current language"""
    def name(self):
        return EventDescription.objects.get(event=self, language=translation.get_language()).name
    name.short_description = _('name')

    """Returnes the description of the event, in the current language"""
    def description(self):
        return EventDescription.objects.get(event=self, language=translation.get_language()).description_text
    description.short_description = _('description')

    """Returnes the name of the host"""
    def get_host(self):
        if(self.is_host_ntnui):
            return 'NTNUI'
        groups = []
        for group in self.sports_groups.all():
            groups.append(group.name)
        return groups

    """Returnes the list of attendees for the event"""
    def get_attendees(self):
        return EventRegistration.objects.filter(event = self)

    """Add attendee to the event"""
    def add_attendee_to_attendees_list(self, user):
        EventRegistration.objects.create(user = user, event = self, registration_time = datetime.now())

    """Remove attendee from the event"""
    def remove_attendee_from_attendees_list(self, user):
        registration = EventRegistration.objects.get(user = user, event = self)
        registration.delete()

    def __str__(self):
        return self.name()



"""Add description and name to event, this way an event can have name and description in different languages."""
class EventDescription(models.Model):

    class Meta:
        verbose_name = _('event description')
        verbose_name_plural = _('event descriptions')

    name = models.CharField(_('name'), max_length=100)
    description_text = models.CharField(_('description'), max_length=500)
    language = models.CharField(_('language'), max_length=30)
    event = models.ForeignKey(Event, verbose_name =_('event'))

    def __str__(self):
        return self.name


"""Model for handling event registration"""
class EventRegistration(models.Model):

    class Meta:
        verbose_name = _('Attendee for event')
        verbose_name_plural = _('Attendees for events')
        unique_together = ('event', 'attendee')

    event = models.ForeignKey(Event, verbose_name = 'Event')
    attendee = models.ForeignKey(User, verbose_name = 'Attendee')
    registration_time = models.DateTimeField(_('Registered for Event at Time'))

    def __str__(self):
        return self.event.name(self) + ' / ' + self.attendee.email


