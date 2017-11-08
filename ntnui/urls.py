"""
NTNUI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from accounts import views as accounts_views
from groups import views as groups_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', groups_views.list_groups, name='home'),
    url(r'^groups/', include('groups.urls')),
    url(r'^hs/', include('hs.urls')),
    # url(r'^signup/$', accounts_views.signup, name='signup'),
    url(r'^logout/', auth_views.logout, name='logout'),
    url(r'^login/$', auth_views.LoginView.as_view(
        template_name='accounts/login.html'), name='login'),
    url(r'^reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='accounts/password_reset_email.html',
            subject_template_name='accounts/password_reset_subject.txt'
        ),
        name='password_reset'
        ),
    url(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'),
    url(r'^settings/password/$', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html'),
        name='password_change'),
    url(r'^settings/password/done/$', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'),
        name='password_change_done'),
    url(r'^cron/accounts/all$', accounts_views.add_all_users_from_exeline,
        name='add_all_users_from_exeline'),
    url(r'^cron/accounts/lastday$', accounts_views.add_last_week_users_from_exeline,
        name='add_last_week_users_from_exeline'),
]
