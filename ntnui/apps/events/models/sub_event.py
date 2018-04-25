from accounts.models import User
from events.models.tag import Tag
from events.models.category import Category
from django.db import models
from events.models.guest import Guest
from django.utils import translation
from django.utils.translation import gettext_lazy as _


class SubEvent(models.Model):
    """Makes it possible to divide an event into multiple sub-events (e.g. multiple disciplines)."""

    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    attendance_cap = models.IntegerField(_('attendance cap'), blank=True, null=True)
    registration_end_date = models.DateTimeField(_('registration end date'), blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name=_('category'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))
    waiting_list = models.ManyToManyField(User, verbose_name=_('waiting list'), blank=True)

    class Meta:
        verbose_name = _('sub-event')
        verbose_name_plural = _('sub-events')

    # Returns the name of the event, in the given language.
    def name(self):
        sub_event_description_get_language = SubEventDescription.objects.filter(sub_event=self, language=translation.get_language())
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

    def attends(self, user):
        if SubEventRegistration.objects.filter(sub_event=self, attendee=user).exists():
            return True
        return False

    def __str__(self):
        return self.name()


class SubEventDescription(models.Model):
    """Created to support multiple languages for each sub-event's name and description."""

    name = models.CharField(_('name'), max_length=100)
    language = models.CharField(_('language'), max_length=30)
    description = models.CharField(_('description'), max_length=500, null=True, blank=True)
    custom_email_text = models.CharField(_('email text'), max_length=250, null=True, blank=True)
    sub_event = models.ForeignKey(SubEvent, verbose_name=_('sub-event'))

    class Meta:
        verbose_name = _('description')
        verbose_name_plural = _('descriptions')

    def __str__(self):
        return self.name


class SubEventRegistration(models.Model):
    """Contains the relation between a user and an event, to  make a list of attendees."""

    registration_time = models.DateTimeField(_('registration time'))
    sub_event = models.ForeignKey(SubEvent, verbose_name ='sub-event')
    payment_id = models.CharField(_('Payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee for sub-event')
        verbose_name_plural = _('attendees for sub-event')
        unique_together = ('sub_event', 'attendee')

    def __str__(self):
        return self.sub_event.name() + ' - ' + self.attendee.email


class GuestSubEventRegistration(models.Model):
    """Contains the relation between a user and an event, to  make a list of attendees."""

    registration_time = models.DateTimeField(_('registration time'))
    sub_event = models.ForeignKey(SubEvent, verbose_name ='sub-event')
    payment_id = models.CharField(_('Payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(Guest, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee for sub-event')
        verbose_name_plural = _('attendees for sub-event')
        unique_together = ('sub_event', 'attendee')

    def __str__(self):
        return self.sub_event.name() + ' - ' + self.attendee.email