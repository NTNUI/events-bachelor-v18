from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add-event$', views.create_event, name='create_event')
]
