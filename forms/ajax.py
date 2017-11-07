from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^validate_email/$', views.ajax_validate_email, name='validate_email'),
    url(r'^group_name/$', views.ajax_group_name, name='group_name'),
]
