from django.conf.urls import url
from events import views


urlpatterns = [
    url(r'^$', views.get_event_page, name='list_events'),
    url(r'^create-event$', views.get_create_event_page, name='create_event_page'),
]


