import os
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.db import models
from accounts.models import User
from groups.models import SportsGroup


class Restriction(models.Model):
    """Restrictions makes it possible to create events for specific groups of users."""

    name = models.CharField(_('name'), max_length=50)

    class Meta:
        verbose_name = _('restriction')
        verbose_name_plural = _('restrictions')

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags makes searching for events easier by giving additional searchable elements."""

    name = models.CharField(_('name'), max_length=50)

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name


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

    def get_cover_upload_to(instance, filename):
        name = EventDescription.objects.get(event=instance, language=translation.get_language()).name
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
        event_description_get_language = EventDescription.objects.filter(event=self, language=translation.get_language())
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
        return EventRegistration.objects.filter(event = self)

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
    event = models.ForeignKey(Event, verbose_name = 'event')
    payment_id = models.CharField(_('Payment id'), max_length=100, blank=True, null=True)
    attendee = models.ForeignKey(User, verbose_name = 'attendee')

    class Meta:
        verbose_name = _('attendee for event')
        verbose_name_plural = _('attendees for event')
        unique_together = ('event', 'attendee')

    def __str__(self):
        return self.event.name() + ' - ' + self.attendee.email


class Category(models.Model):
    """Sub-events get divided into categories (e.g. based on different skill levels)."""

    event = models.ForeignKey(Event, verbose_name=_('event'))

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    # Returns the category's name, in the given language
    def name(self):
        category_description_get_language = CategoryDescription.objects.filter(category=self, language=translation.get_language())
        category_description_english = CategoryDescription.objects.filter(category=self, language='en')
        category_description = CategoryDescription.objects.filter(category=self)

        if category_description_get_language.exists():
            return category_description_get_language[0].name
        elif category_description_english.exists():
            return category_description_english[0].name
        elif category_description.exists():
            return category_description[0].name
        else:
            return 'No name given'

    def __str__(self):
        return self.name()


class CategoryDescription(models.Model):
    """Created to support multiple languages for each category's name and description."""

    name = models.CharField(_('name'), max_length=100)
    language = models.CharField(_('language'), max_length=30)
    category = models.ForeignKey(Category, verbose_name=_('category'))

    class Meta:
        verbose_name = _('description')
        verbose_name_plural = _('descriptions')

    def __str__(self):
        return self.name


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
    attendee = models.ForeignKey(User, verbose_name='attendee')

    class Meta:
        verbose_name = _('attendee for sub-event')
        verbose_name_plural = _('attendees for sub-event')
        unique_together = ('sub_event', 'attendee')

    def __str__(self):
        return self.sub_event.name() + ' - ' + self.attendee.email


class Guest(models.Model):
    email = models.EmailField(_('email address'))
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    phone_number = models.IntegerField(_('phone number'), max_length=8)

    class Meta:
        verbose_name = _('guest')
        verbose_name_plural = _('guests')

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)
