from django.contrib import admin

from events.models import Event, EventDescription, Category, SubEvent, CategoryDescription, SubEventDescription, Tag, \
    Restriction, EventRegistration


class CategoryDescroptionInline(admin.TabularInline):
    """Description inline for a given category"""
    model = CategoryDescription
    # Setting extra to 0, the admin site wont show any extra descriptions (default is 3)
    extra = 0


class SubEventDescriptionInline(admin.TabularInline):
    """The description and name for a SubEvent"""
    model = SubEventDescription
    # Setting extra to 0, the admin site wont show any extra descriptions (default is 3)
    extra = 0


class SubEventInline(admin.StackedInline):
    """SubEventInline, used in category to list events for a given category"""
    model = SubEvent
    # Setting extra to 0, the admin site wont show any extra descriptions (default is 3)
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    """Adds the category model, with its related tables"""
    model = Category
    # displays the eventdescription in the create event window
    inlines = [CategoryDescroptionInline,
               SubEventInline
               ]


class SubEventAdmin(admin.ModelAdmin):
    """Adds subevent to admin"""
    # displays the eventdescription in the create event window
    inlines = [SubEventDescriptionInline,
               ]


class EvenetRegistrationInline(admin.TabularInline):
    """ADd event registration as a inline"""
    model = EventRegistration
    # Setting extra to 0, the admin site wont show any extra descriptions (default is 3)
    extra = 0


class EventDescriptionInline(admin.TabularInline):
    """The description and name for an Event"""
    model = EventDescription
    # Setting extra to 0, the admin site wont show any extra descriptions (default is 3)
    extra = 0


class EventAdmin(admin.ModelAdmin):
    """Add the event  model to admin"""
    # Sets the attributes  to be listed
    list_display = ['id', 'name', 'description', 'start_date', 'end_date', 'priority', 'is_host_ntnui']
    # displays the eventdescription in the create event window
    inlines = [EventDescriptionInline,
               EvenetRegistrationInline
               ]


# adds the views to the admin
admin.site.register(Event, EventAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubEvent, SubEventAdmin)
admin.site.register(Tag)
admin.site.register(Restriction)
