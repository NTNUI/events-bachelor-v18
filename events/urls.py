from django.conf.urls import url
from events import views


urlpatterns = [
    url(r'^$', views.events, name='list_groups'),
    url(r'^create-event$', views.get_create_event_page, name='create_event_page'),
]


