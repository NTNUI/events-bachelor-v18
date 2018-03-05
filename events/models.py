from django.db import models
from groups.models import SportsGroup
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from accounts.models import User


class Tag(models.Model):
    """Add tags to models to make searchig easier"""

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    name = models.CharField(_('name'), max_length=50)

    def __str__(self):
        return self.name


class Restriction(models.Model):
    """Defines diffrent restrictions for event"""

    class Meta:
        verbose_name = _('restricton')
        verbose_name_plural = _('restrictions')

    name = models.CharField(_('name'), max_length=50)

    def __str__(self):
        return self.name


class Event(models.Model):
    """Creates a model for events, with start date, end date, priority, host group and ntnui as host.
    If ntnui is host, is_host_ntnui is true, otherwise false.
    """

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    place = models.CharField(_('place'), max_length=50, blank=True)
    restriction = models.ForeignKey(Restriction, verbose_name=_('restriction'), default=0)
    priority = models.BooleanField(_('priority'), default=False)
    is_host_ntnui = models.BooleanField(_('hosted by NTNUI'), default=False)
    attending_members = models.ManyToManyField(User, verbose_name=_('attending members'), blank=True)
    sports_groups = models.ManyToManyField(SportsGroup, blank=True, verbose_name=_('hosted by'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))

    # Returnes the name of the given event, in the given language
    def name(self):
        return EventDescription.objects.get(event=self, language=translation.get_language()).name
    name.short_description = _('name')

    # Returnes the description of a given event in a given language
    def description(self):
        return EventDescription.objects.get(event=self, language=translation.get_language()).description_text

    description.short_description = _('description')

    # Retunes a list of host or ntnui
    def get_host(self):
        if (self.is_host_ntnui):
            return 'NTNUI'
        groups = []
        for group in self.sports_groups.all():
            groups.append(group.name)
        return groups

    def __str__(self):
        return self.name()


class EventDescription(models.Model):
    """Add description and name to event, this way an event can have name and description in different languages."""
    class Meta:
        verbose_name = _('event description')
        verbose_name_plural = _('event descriptions')

    name = models.CharField(_('name'), max_length=100)
    description_text = models.CharField(_('description'), max_length=500)
    language = models.CharField(_('language'), max_length=30)
    event = models.ForeignKey(Event, verbose_name=_('event'))

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
    event = models.ForeignKey(Event, verbose_name=_('event'))


class CategoryDescription(models.Model):
    """Add name to a given subevent."""
    class Meta:
        verbose_name = _('description')
        verbose_name_plural = _('descriptions')

    name = models.CharField(_('name'), max_length=100)
    language = models.CharField(_('language'), max_length=30)
    category = models.ForeignKey(Category, verbose_name=_('category'))

    def __str__(self):
        return self.name


class SubEvent(models.Model):
    """Any category may contain subEvents"""
    class Meta:
        verbose_name = _('subEvnet')
        verbose_name_plural = _('subEvents')

    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    attending_members = models.ManyToManyField(User, verbose_name=_('attending members'), blank=True)
    category = models.ForeignKey(Category, verbose_name=_('category'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))


class SubEventDescription(models.Model):
    """Add name to a given subevent."""
    class Meta:
        verbose_name = _('description')
        verbose_name_plural = _('descriptions')

    name = models.CharField(_('name'), max_length=100)
    language = models.CharField(_('language'), max_length=30)
    sub_event = models.ForeignKey(SubEvent, verbose_name=_('subevent'))

    def __str__(self):
        return self.name
