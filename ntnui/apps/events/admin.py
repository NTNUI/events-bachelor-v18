from django.contrib import admin
from events.models.tag import Tag
from events.models.guest import Guest
from events.models.restriction import Restriction
from events.models.category import Category, CategoryDescription
from events.models.event import Event, EventDescription, EventRegistration, EventGuestRegistration, EventWaitingList, EventGuestWaitingList
from events.models.sub_event import SubEvent, SubEventDescription, SubEventRegistration, SubEventGuestRegistration, SubEventWaitingList, SubEventGuestWaitingList


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


class EventGuestRegistrationInline(admin.TabularInline):
    """Creates an inline for the EventRegistration-model."""

    model = EventGuestRegistration
    # extra defines the inline's number of placeholders shown on the admin page (default = 3).
    extra = 0


class EventWaitingListInline(admin.TabularInline):
    """Creates an inline for the EventWaitingList-model."""

    model = EventWaitingList
    # extra defines the inline's number of placeholders shown on the admin page (default = 3).
    extra = 0


class EventGuestWaitingListInline(admin.TabularInline):
    """Creates an inline for the EventWaitingList-model."""

    model = EventGuestWaitingList
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


class SubEventGuestRegistrationInline(admin.TabularInline):
    """Creates an inline for the SubEventRegistration-model."""

    model = SubEventGuestRegistration
    # extra defines the inline's number of placeholders shown on the admin page (default = 3).
    extra = 0


class SubEventWaitingListInline(admin.TabularInline):
    """Creates an inline for the SubEventWaitingList-model."""

    model = SubEventWaitingList
    # extra defines the inline's number of placeholders shown on the admin page (default = 3).
    extra = 0


class SubEventGuestWaitingListInline(admin.TabularInline):
    """Creates an inline for the SubEventWaitingList-model."""

    model = SubEventGuestWaitingList
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
    inlines = [EventDescriptionInline, EventRegistrationInline,
               EventGuestRegistrationInline, EventWaitingListInline, EventGuestWaitingListInline]


class SubEventAdmin(admin.ModelAdmin):
    """Encapsulates the SubEvent-model's related tables."""

    # inlines defines which inline classes that will be added to the SubEvent's admin page.
    inlines = [SubEventDescriptionInline, SubEventRegistrationInline,
               SubEventGuestRegistrationInline, SubEventWaitingListInline, SubEventGuestWaitingListInline]


# adds the views to the admin.
admin.site.register(Guest)
admin.site.register(Tag)
admin.site.register(Restriction)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(SubEvent, SubEventAdmin)
