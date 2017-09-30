from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^members/$', views.members, name='group_members')
]
