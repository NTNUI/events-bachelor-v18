from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.list_form, name='forms_list'),
    url(r'^fill/$', views.fill_form, name='forms_fill'),
    url(r'^validate_email/$', views.validate_email, name='validate_email'),
    url(r'^group_name/$', views.group_name, name='group_name')
    ]
