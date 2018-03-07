from django.conf.urls import url
from . import views
from .views import (
    create_event,
    get_events,
    event_add_attendance,
    event_cancel_attendance
)



urlpatterns = [
    url(r'^add-event$', create_event_request, name='create_event'),
    url(r'^get-events', get_events_request, name='get_events'),
    url(r'^attend-event$', event_add_attendance, name='attend_event')
]
