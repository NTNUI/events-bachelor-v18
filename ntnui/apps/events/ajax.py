from django.conf.urls import url
from .views import (

    create_event_request,
    get_events_request,
    edit_event_request,
    get_events,
    get_event,
    delete_subevent,
    get_attending_events_request,
    create_category_request,
    create_sub_event_request,
)
from .attend_event import (
    attend_event_request,
    attend_payment_event_request,
    waiting_list_event_request,
    waiting_list_payment_event_request,
)

urlpatterns = [
    url(r'^add-event$', create_event_request, name='create_event'),
    url(r'^get-events', get_events_request, name='get_events'),

    url(r'^create-category', create_category_request, name='create_category'),
    url(r'^create-sub-event', create_sub_event_request, name='create_sub_event'),
    url(r'^get-attending-events', get_attending_events_request, name='get_attending_events'),

    url(r'^edit-event$', edit_event_request, name='edit_event'),
    url(r'^delete-subevent$', delete_subevent, name='delete_subevent'),

    url(r'^(?P<id>\d+)$', get_event, name='get_event'),
    url(r'^attend-event$', attend_event_request, name='attend_event'),
    url(r'^attend-payment-event$', waiting_list_payment_event_request, name='attend_payment_event'),


]
