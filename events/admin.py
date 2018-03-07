from django.contrib import admin

from events.models import Event, EventDescription, Category, SubEvent, CategoryDescription, SubEventDescription, Tag, \
    Restriction


class CategoryDescroptionInline(admin.TabularInline):
    model = CategoryDescription
    # Setting extra to 0, the admin site wont show any extra descriptions (default is 3)
    extra = 0


"""The description and name for an Event"""
class SubEventDescriptionInline(admin.TabularInline):
    model = SubEventDescription
    # Setting extra to 0, the admin site wont show any extra descriptions (default is 3)
    extra = 0


"""The description and name for an Event"""
class SubEventInline(admin.StackedInline):
    model = SubEvent
    # Setting extra to 0, the admin site wont show any extra descriptions (default is 3)
    extra = 0

class CategoryAdmin(admin.ModelAdmin):
    model = Category
    # displays the eventdescription in the create event window
    inlines = [CategoryDescroptionInline,
               SubEventInline
               ]


class SubEventAdmin(admin.ModelAdmin):
    # Sets the attributes  to be listed
    # displays the eventdescription in the create event window
    inlines = [SubEventDescriptionInline,
               ]

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
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubEvent, SubEventAdmin)
admin.site.register(Tag)
admin.site.register(Restriction)