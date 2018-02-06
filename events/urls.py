from django.conf.urls import url
from events import views


urlpatterns = [
    url(r'^$', views.get_event_page, name='list_groups')
]
