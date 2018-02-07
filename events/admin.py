from django.contrib import admin

from events.models import Event, EventDescription

admin.site.register(Event)
admin.site.register(EventDescription)