from django.contrib import admin

from events.models import Event, EventDescription

"""The description and name for an Event"""
class EventDescriptionInline(admin.TabularInline):
    model = EventDescription
    # Setting extra to 0, the admin site wont show any extra descriptions (default is 3)
    extra = 0

class EventAdmin(admin.ModelAdmin):
    # Sets the attributes  to be listed
    list_display = ['id', 'name', 'description', 'start_date', 'end_date', 'priority','is_host_ntnui']
    # displays the eventdescription in the create event window
    inlines = [EventDescriptionInline,
               ]

# adds the view to the admin
admin.site.register(Event, EventAdmin)