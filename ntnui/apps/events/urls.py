from django.conf.urls import url

from .views import (
    get_main_page,
    get_create_event_page,
    get_event_details,
    get_edit_event_page,
    get_delete_event,
)

urlpatterns = [
    url(r'^$', get_main_page, name='get_main_page'),
    url(r'^create-event$', get_create_event_page, name='create_event_page'),
    url(r'^(?P<id>\d+)/', get_event_details, name='event_details'),
    url(r'^edit/(?P<id>\d+)/', get_edit_event_page, name='edit_event_page'),
    url(r'^delete/(?P<id>\d+)/$', get_delete_event, name='get_delete_event'),
]
