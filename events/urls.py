from django.conf.urls import url
from events import views
from django.views.generic.base import RedirectView
from .views import (
    get_main_page,
    get_create_event_page,
    get_event_details
    )


urlpatterns = [
    url(r'^$', get_main_page, name='get_main_page'),
    url(r'^create-event$', get_create_event_page, name='create_event_page'),
    url(r'^(?P<id>\d+)/', get_event_details, name='event_details'),
    
]


