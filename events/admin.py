from django.contrib import admin

from events.models import Event, EventDescription

class EventDescriptionInline(admin.TabularInline):
    model = EventDescription
    extra = 1

class EventAdmin(admin.ModelAdmin):
    inlines = [EventDescriptionInline,
               ]

admin.site.register(Event, EventAdmin)