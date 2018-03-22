from django.conf.urls import url
from . import views
from .views import (
    create_event_request,
    add_attendance_to_event,
    remove_attendance_from_event,
    add_attendance_from_subevent,
    remove_attendance_from_subevent,
    get_events_request
)

urlpatterns = [
    url(r'^add-event$', create_event_request, name='create_event'),
    url(r'^get-events', get_events_request, name='get_events'),
    url(r'^attend-event$', add_attendance_to_event, name='attend_event'),
    url(r'^remove-attend-event$', remove_attendance_from_event, name='attend_event'),
    url(r'^attend-sub-event$', add_attendance_from_subevent, name='attend_event'),
    url(r'^remove-attend-sub-event$', remove_attendance_from_subevent, name='attend_event')
]
