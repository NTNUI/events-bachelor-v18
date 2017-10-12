from django.db import models
from django.conf import settings


class Form(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=12)
    isApproved = models.BooleanField()

    def __str__(self):
        return self.name