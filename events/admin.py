from django.contrib import admin

from events.models import Events, EventDescription

admin.site.register(Events)
admin.site.register(EventDescription)