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
    attendance_cap = models.IntegerField(_('attendance cap'), blank=True, null=True)
    registration_end_date = models.DateTimeField(_('registration end date'), blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name=_('category'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))

    class Meta:
        verbose_name = _('sub-event')
        verbose_name_plural = _('sub-events')

    # Returns the name of the event, in the given language.
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

    # Checks whether a given user attends the sub-event
    def user_attends(self, user):
        if SubEventRegistration.objects.filter(attendee=user, sub_event=self).exists():
            return True
        return False

    # Checks whether a given guest attends the sub-event
    def guest_attends(self, guest):
        if SubEventGuestRegistration.objects.filter(attendee=guest, sub_event=self).exists():
            return True
        return False

    # Returns a complete list of the sub-event's attendees
    def get_attendees(self):
        user_attendees = SubEventRegistration.objects.filter(sub_event=self)
        guest_attendees = SubEventGuestRegistration.objects.filter(sub_event=self)
        attendance_list = user_attendees + guest_attendees

        return attendance_list

    # Checks whether a given user is signed up for the sub-event's waiting list
    def user_on_waiting_list(self, user):
        if SubEventWaitingList.objects.filter(attendee=user, sub_event=self).exists():
            return True
        return False

    # Checks whether a given guest is signed up for the sub-event's waiting list
    def guest_on_waiting_list(self, guest):
        if SubEventGuestWaitingList.objects.filter(attendee=guest, sub_event=self).exists():
            return True
        return False

    # Returns the sub-event's complete waiting list
    def get_waiting_list(self):
        user_waiting_list = SubEventWaitingList.objects.filter(sub_event=self)
        guest_waiting_list = SubEventGuestWaitingList.objects.filter(sub_event=self)
        waiting_list = user_waiting_list + guest_waiting_list

        return waiting_list

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
