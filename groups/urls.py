from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.members, name='group_members'),
    url(r'^(?P<slug>[\w-]+)/members$', views.members, name='group_members'),
]
