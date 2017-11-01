from django.conf.urls import url
from . import views
from . import csv

urlpatterns = [
    url(r'^$', views.hs_space, name='hs_space'),
    url(r'^allmembers$', views.list_all_members, name='all_members'),
    url(r'^allmembers/downloadmembers$', csv.download_all_members, name='download_all_members'),

]
