<<<<<<< HEAD
from django.conf.urls import include, url
=======

from django.conf.urls import url
>>>>>>> 31e71f404e6dc8f9e8bffafed346d4eb310433cd
from . import views

urlpatterns = [
    url(r'^$', views.list_groups, name='list_groups'),
    url(r'^(?P<slug>[\w-]+)/members$', views.members, name='group_members'),
    url(r'^(?P<slug>[\w-]+)/invitations$',
        views.invitations, name='group_invitations'),
    url(r'^(?P<slug>[\w-]+)/members/invite$',
        views.invite_member, name='group_invite_member'),
    url(r'^(?P<slug>[\w-]+)$', views.group_index, name='group_index'),
    url(r'^(?P<slug>[\w-]+)/settings$', views.settings, name='group_settings'),
    url(r'^(?P<slug>[\w-]+)/forms/', include('forms.urls')),
]
