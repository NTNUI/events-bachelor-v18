
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.list_all_members, name='list_all_members'),

]
