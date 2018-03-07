from django.conf.urls import url
from . import views
from .views import (
    create_event_request,
    event_add_attendance,
    get_events_request
)



urlpatterns = [
    url(r'^add-event$', create_event_request, name='create_event'),
    url(r'^get-events', get_events_request, name='get_events'),
    url(r'^attend-event$', event_add_attendance, name='attend_event')
]
