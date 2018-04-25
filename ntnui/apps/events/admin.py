from django.contrib import admin
from events.models.guest import Guest
from events.models.tag import Tag
from events.models.event import Event, EventDescription, EventRegistration, Restriction
from events.models.sub_event import SubEvent, SubEventDescription, SubEventRegistration
from events.models.category import Category, CategoryDescription

class CategoryDescriptionInline(admin.TabularInline):
    """Creates an inline for the CategoryDescription-model."""

    model = CategoryDescription
    # extra defines the inline's number of placeholders shown on the admin page (default = 3).
    extra = 0


class EventDescriptionInline(admin.TabularInline):
    """Creates an inline for the EventDescription-model."""

    model = EventDescription
    # extra defines the inline's number of placeholders shown on the admin page (default = 3).
    extra = 0


class EventRegistrationInline(admin.TabularInline):
    """Creates an inline for the EventRegistration-model."""

    model = EventRegistration
    # extra defines the inline's number of placeholders shown on the admin page (default = 3).
    extra = 0


class SubEventInline(admin.StackedInline):
    """Creates an inline for the SubEvent-model."""

    model = SubEvent
    # extra defines the inline's number of placeholders shown on the admin page (default = 3).
    extra = 0


class SubEventDescriptionInline(admin.TabularInline):
    """Creates an inline for the SubEventDescription-model."""

    model = SubEventDescription
    # extra defines the inline's number of placeholders shown on the admin page (default = 3).
    extra = 0


class SubEventRegistrationInline(admin.TabularInline):
    """Creates an inline for the SubEventRegistration-model."""

    model = SubEventRegistration
    # extra defines the inline's number of placeholders shown on the admin page (default = 3).
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    """Encapsulates the Category-model's related tables."""

    # inlines defines which inline classes to be added to the Category's admin page.
    inlines = [CategoryDescriptionInline, SubEventInline]


class EventAdmin(admin.ModelAdmin):
    """Encapsulates the Event-model's related tables."""

    # list_display defines which attributes to be listed at the Event's overview admin page.
    list_display = ['id', 'name', 'description', 'start_date', 'end_date', 'priority', 'is_host_ntnui']
    # inlines defines which inline classes to be added to the Event's admin page.
    inlines = [EventDescriptionInline, EventRegistrationInline]


class SubEventAdmin(admin.ModelAdmin):
    """Encapsulates the SubEvent-model's related tables."""

    # inlines defines which inline classes that will be added to the SubEvent's admin page.
    inlines = [SubEventDescriptionInline, SubEventRegistrationInline]


# adds the views to the admin.
admin.site.register(Tag)
admin.site.register(Guest)
admin.site.register(Restriction)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(SubEvent, SubEventAdmin)
