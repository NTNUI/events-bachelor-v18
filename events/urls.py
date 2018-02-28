from django.conf.urls import url
from events import views
from .views import (
    get_event_page,
    get_create_event_page,
    get_event_details
    )


urlpatterns = [
    url(r'^$', get_event_page, name='list_groups'),
    url(r'^create-event$', get_create_event_page, name='create_event_page'),
    url(r'^(?P<id>\d+)/$', get_event_details, name='event_details')
]


