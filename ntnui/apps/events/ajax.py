from django.conf.urls import url

from .create_event import create_event_request
from .event_attendance import (attend_event_request,
                               attend_payment_event_request,
                               remove_attendance_by_token_request,
                               remove_attendance_request,
                               waiting_list_event_request)
from .get_events import (get_attending_events_request, get_events_request)
from .manage_events import (create_category_request, create_sub_event_request,
                            delete_category_request, delete_event_request,
                            delete_sub_event_request, edit_category_request,
                            edit_event_request, edit_sub_event_request)
from .views import (get_event, get_sub_event)

urlpatterns = [
    url(r'^create-event$', create_event_request, name='create_event'),
    url(r'^edit-event$', edit_event_request, name='ajax_edit_event'),
    url(r'^(?P<event_id>\d+)$', get_event, name='get_event'),
    url(r'^get-events', get_events_request, name='get_events'),
    url(r'^delete/(?P<event_id>\d+)/$', delete_event_request, name='get_delete_event'),

    url(r'^create-category', create_category_request, name='create_category'),
    url(r'^edit-category', edit_category_request, name='edit_category'),
    url(r'^delete-category', delete_category_request, name='delete_category'),

    url(r'^sub-event/(?P<sub_event_id>\d+)$', get_sub_event, name='get_sub_event'),
    url(r'^create-sub-event', create_sub_event_request, name='create_sub_event'),
    url(r'^edit-sub-event', edit_sub_event_request, name='edit_sub_event'),
    url(r'^delete-sub-event$', delete_sub_event_request, name='delete_sub_event'),

    url(r'^get-attending-events', get_attending_events_request, name='get_attending_events'),

    url(r'^attend-event$', attend_event_request, name='attend_event'),
    url(r'^waiting-list$', waiting_list_event_request, name='waiting_list_event_request'),
    url(r'^attend-payment-event$', attend_payment_event_request, name='attend-payment-event'),
    url(r'^unattend-event$', remove_attendance_request, name='remove_attendance'),
    url(r'^unattend-event_by_token/(?P<token>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}'
        r'\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})$', remove_attendance_by_token_request, name='remove_attendance_by_token')
]
