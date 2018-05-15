from django.conf.urls import url

from .views import (get_attending_events_page, get_create_event_page,
                    get_edit_event_page, get_event_attendees_page,
                    get_event_details_page, get_events_main_page,
                    get_remove_attendance_page)

urlpatterns = [
    url(r'^$', get_events_main_page, name='get_main_page'),
    url(r'^create-event$', get_create_event_page, name='create_event_page'),
    url(r'^(?P<event_id>\d+)/', get_event_details_page, name='event_details'),
    url(r'^edit/(?P<event_id>\d+)/', get_edit_event_page, name='edit_event_page'),
    url(r'^attending/$', get_attending_events_page, name='attending_events_page'),
    url(r'^attendees/(?P<event_id>\d+)', get_event_attendees_page, name='event_attendees'),
    url(r'^remove-attendance/(?P<token>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}'
        r'\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/', get_remove_attendance_page, name='remove-attendance'),
]
