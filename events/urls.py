from django.conf.urls import url
from events import views


urlpatterns = [
    url(r'^$', views.get_event_page, name='list_groups'),
    url(r'^/create-event$', views.get_create_event_page, name='create_event_page'),
     url(r'^/api/create-event$', views.create_event, name='create_event')
]
