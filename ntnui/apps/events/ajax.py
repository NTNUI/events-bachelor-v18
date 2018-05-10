from django.conf.urls import url
from .views import (

    get_events_request,
    edit_event_request,
    get_event,
    get_attending_events_request,
    create_category_request,
    create_sub_event_request,
    edit_category,
    edit_subevent,
    delete_category_request,
    delete_subevent_request,
)
from .create_event import (create_event_request)
from .event_attendance import (
    attend_event_request,
    attend_payment_event_request,
    waiting_list_event_request,
    remove_attendance_request,
    remove_attendance_by_token_request
)

urlpatterns = [
    url(r'^add-event$', create_event_request, name='create_event'),
    url(r'^get-events', get_events_request, name='get_events'),

    url(r'^create-category', create_category_request, name='create_category'),
    url(r'^edit-category', edit_category, name='edit_category'),
    url(r'^delete-category', delete_category_request, name='delete_category'),
    url(r'^create-sub-event', create_sub_event_request, name='create_sub_event'),
    url(r'^edit-sub-event', edit_subevent, name='edit_subevent'),
    url(r'^delete-sub-event$', delete_subevent_request, name='delete_subevent'),
    url(r'^get-attending-events', get_attending_events_request, name='get_attending_events'),

    url(r'^edit-event$', edit_event_request, name='ajax_edit_event'),


    url(r'^(?P<id>\d+)$', get_event, name='get_event'),

    url(r'^attend-event$', attend_event_request, name='attend_event'),
    url(r'^waiting-list$', waiting_list_event_request, name='waiting_list_event_request'),
    url(r'^attend-payment-event$', attend_payment_event_request, name='attend-payment-event'),
    url(r'^attend-payment-event$', attend_payment_event_request, name='attend-payment-event'),
    url(r'^unattend-event$', remove_attendance_request, name='remove_attendance'),
    url(r'^unattend-event_by_token$', remove_attendance_by_token_request, name='remove_attendance_by_token'),
]
