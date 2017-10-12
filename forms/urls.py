from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.list_form, name='forms_list'),
    ]
