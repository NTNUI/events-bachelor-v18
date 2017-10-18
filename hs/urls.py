from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.hs_space, name='hs_space'),
    url(r'^allmembers$', views.list_all_members, name='all_members'),
]
