from django.db import models
from django.conf import settings
import os
from groups.models import Membership, Invitation
import datetime


def get_cover_upload_to(instance, filename):
    return os.path.join(
        "cover_photo/%s" % instance.slug, filename)


class MainBoard(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=12)
    cover_photo = models.ImageField(upload_to=get_cover_upload_to, default='cover_photo/ntnui-volleyball.png')

    def __str__(self):
        return self.name


class HSMembership(models.Model):
    person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    board = models.ForeignKey(MainBoard)
    date_joined = models.DateField(default=datetime.date.today)
    role = models.CharField(max_length=30)
