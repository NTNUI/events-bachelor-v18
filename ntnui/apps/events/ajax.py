from django.conf.urls import url
from . import views
from .views import (
    attend_event_user,
    remove_attendance_event_user,
    waiting_list_event_user,
    attend_payment_event_user,
    remove_attendance_waiting_list_event_user,
    waiting_list_event_guest,
    attend_event_guest,
    attend_payment_event_guest,
    create_event_request,
    get_events_request,
    edit_event_request,
    get_events,
    refund_event,
    get_event,
)

urlpatterns = [
    url(r'^add-event$', create_event_request, name='create_event'),
    url(r'^get-events', get_events_request, name='get_events'),
    url(r'^(?P<id>\d+)$', get_event, name='get_event'),
    url(r'^edit-event$', edit_event_request, name='edit_event'),

    url(r'^attend_payment_event_guest', attend_payment_event_guest, name='attend_payment_event_guest'),

    url(r'^attend-event-user$', attend_event_user, name='attend_event_user'),
    url(r'^remove_attendance_event_user$', remove_attendance_event_user, name='remove_attendance_event_user'),
    url(r'^(?P<id>\d+)/attend_payment_event_user$', attend_payment_event_user, name='attend_payment_event_user'),
    url(r'^attend-event-guest$', attend_event_guest, name='attend_event_guest'),
    url(r'^refund_event$', refund_event, name='refund_event'),






]
"""
 url(r'^refund', refund_event, name='refund_event'),
  url(r'^attend-sub-event$', add_attendance_from_subevent, name='attend_event'),
  url(r'^remove-attend-sub-event$', remove_attendance_from_subevent, name='attend_event'),
"""