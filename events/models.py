from django.db import models
from groups.models import SportsGroup


"""Creates a model for events, with start date, end date, priority, host group and ntnui as host.
If ntnui is host, is_host_ntnui is true, otherwise false.
"""
class Event(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    priority = models.BooleanField(default=False)
    is_host_ntnui = models.BooleanField(default=False)
    sports_group = models.ManyToManyField(SportsGroup, null=True, blank=True)


"""Add description and name to event, this way a event can have name and description in different languages.
"""
class EventDescription(models.Model):
    name = models.CharField(max_length=100)
    description_text = models.CharField(max_length=500)
    language = models.CharField(max_length=30)
    event = models.ForeignKey(Event)
