from django.db import models
from django.contrib.auth.models import User

class SportsGroup(models.Model):
    name = models.CharField(max_length=50)
    president = models.ForeignKey(User, related_name='president')
    vice_president = models.ForeignKey(User,  related_name='vp')
    cashier = models.ForeignKey(User, related_name='cashier')

    def __str__(self):
        return self.name
