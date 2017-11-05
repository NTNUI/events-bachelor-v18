from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.list_form, name='forms_list'),
    url(r'^fill/$', views.fill_form, name='forms_fill'),
    url(r'^forms_list', views.forms_list_submitted, name='forms_list_submitted'),
    url(r'^forms_read/(?P<forms_id>[\w-]+)', views.forms_read, name='forms_read')
    ]
