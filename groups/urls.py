from django.conf.urls import include, url
from . import views
from . import csv

urlpatterns = [
    url(r'^$', views.list_groups, name='list_groups'),
    url(r'^(?P<slug>[\w-]+)/members$', views.members, name='group_members'),
    url(r'^(?P<slug>[\w-]+)/members/(?P<member_id>[\d+]+)/settings$',
        views.member_settings, name='group_member_settings'),
    url(r'^(?P<slug>[\w-]+)/ajax/member/(?P<member_id>[\d+]+)$',
        views.member_info, name='group_member_ajax'),
    url(r'^(?P<slug>[\w-]+)/invitations$',
        views.invitations, name='group_invitations'),
    url(r'^(?P<slug>[\w-]+)/members/invite$',
        views.invite_member, name='group_invite_member'),
    url(r'^(?P<slug>[\w-]+)/requests', views.requests, name='group_requests'),
    url(r'^(?P<slug>[\w-]+)$', views.group_index, name='group_index'),
    url(r'^(?P<slug>[\w-]+)/settings$', views.settings, name='group_settings'),
    url(r'^(?P<slug>[\w-]+)/forms/', include('forms.urls')),
    url(r'^(?P<slug>[\w-]+)/members/download$',
        views.download_members, name='download_members'),
    url(r'^(?P<slug>[\w-]+)/members/download/get_all$',
        csv.download_members,
        name='download_all_group_members'),
    url(r'^(?P<slug>[\w-]+)/members/download/get_year$',
        csv.download_yearly_group_members,
        name='download_yearly_group_members')
]
