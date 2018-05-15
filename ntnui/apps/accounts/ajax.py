from django.conf.urls import url
from .views import (
    get_user
)

urlpatterns = [
    url(r'^$', get_user , name='get_user'),
]
