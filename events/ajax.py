from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add-event$', views.create_event_request, name='create_event'),
    url(r'^get-events', views.get_events_request, name='get_events')
]
