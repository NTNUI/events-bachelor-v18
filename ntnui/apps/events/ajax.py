from django.conf.urls import url
from .views import (
    user_attend_event,
    user_attend_payment_event,
    user_waiting_list_event,

    user_unattend_event,
    user_unattend_payment_event,
    user_unattend_waiting_list_event,

    guest_attend_event,
    guest_attend_payment_event,
    guest_waiting_list_event,

    user_attend_sub_event,
    user_attend_payment_sub_event,
    user_waiting_list_sub_event,

    guest_attend_sub_event,
    guest_attend_payment_sub_event,
    guest_waiting_list_sub_event,

    user_unattend_sub_event,
    user_unattend_payment_sub_event,
    user_unattend_waiting_list_sub_event,

    create_event_request,
    get_events_request,
    edit_event_request,
    get_events,
    get_event,
    delete_subevent,
    get_attending_events_request,
    create_category_request,
    create_sub_event_request,
    edit_category,
    edit_subevent,
)

urlpatterns = [
    url(r'^add-event$', create_event_request, name='create_event'),
    url(r'^get-events', get_events_request, name='get_events'),

    url(r'^create-category', create_category_request, name='create_category'),
    url(r'^edit-category', edit_category, name='edit_category'),
    url(r'^create-sub-event', create_sub_event_request, name='create_sub_event'),
    url(r'^edit-sub-event', edit_subevent, name='edit_subevent'),
    url(r'^get-attending-events', get_attending_events_request, name='get_attending_events'),

    url(r'^edit-event$', edit_event_request, name='ajax_edit_event'),
    url(r'^delete-sub-event$', delete_subevent, name='delete_subevent'),

    url(r'^(?P<id>\d+)$', get_event, name='get_event'),
    url(r'^(?P<event_id>\d+)/user-attend-event$', user_attend_event, name='user_attend_event'),
    url(r'^(?P<event_id>\d+)/user-attend-payment-event$', user_attend_payment_event, name='user_attend_payment_event'),
    url(r'^(?P<event_id>\d+)/user-waiting-list-event$', user_waiting_list_event, name='user_waiting_list_event'),

    url(r'^user-unattend-event$', user_unattend_event, name='user_unattend_event'),
    url(r'^user-unattend-payment-event$', user_unattend_payment_event, name='user_unattend_payment_event'),
    url(r'^user-unattend-waiting-list-event$', user_unattend_waiting_list_event,
        name='user_unattend_waiting_list_event'),

    url(r'^(?P<event_id>\d+)/guest-attend-event$', guest_attend_event, name='guest_attend_event'),
    url(r'^(?P<event_id>\d+)/guest-attend-payment-event$', guest_attend_payment_event,
        name='guest_attend_payment_event'),
    url(r'^(?P<event_id>\d+)/guest-waiting-list-event$', guest_waiting_list_event, name='guest_waiting_list_event'),

    url(r'^(?P<sub_event_id>\d+)/user-attend-sub-event$', user_attend_sub_event, name='user_attend_sub_event'),
    url(r'^(?P<sub_event_id>\d+)/user-attend-payment-sub-event$', user_attend_payment_sub_event,
        name='user_attend_payment_sub_event'),
    url(r'^(?P<sub_event_id>\d+)/user-waiting-list-sub-event$', user_waiting_list_sub_event,
        name='user_waiting_list_sub_event'),

    url(r'^user-unattend-sub-event$', user_unattend_sub_event, name='user_unattend_sub_event'),
    url(r'^user-unattend-payment-sub-event$', user_unattend_payment_sub_event, name='user_unattend_payment_sub_event'),
    url(r'^user-unattend-waiting-list-sub-event$', user_unattend_waiting_list_sub_event,
        name='user_unattend_waiting_list_sub_event'),

    url(r'^(?P<sub_event_id>\d+)/guest-attend-sub-event$', guest_attend_sub_event, name='guest_attend_sub_event'),
    url(r'^(?P<sub_event_id>\d+)/guest-attend-payment-sub-event$', guest_attend_payment_sub_event,
        name='guest_attend_payment_sub_event'),
    url(r'^(?P<sub_event_id>\d+)/guest-waiting-list-sub-event$', guest_waiting_list_sub_event,
        name='guest_waiting_list_sub_event')
]
