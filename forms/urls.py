from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.list_forms, name='forms_list'),
    ]
