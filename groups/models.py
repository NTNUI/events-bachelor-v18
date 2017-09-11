from django.db import models
from django.contrib.auth.models import User


class SportsGroup(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(User, through='Membership')

    def __str__(self):
        return self.name


class Board(models.Model):
    president = models.ForeignKey(User, related_name='board_president')
    vice_president = models.ForeignKey(User,  related_name='board_vp')
    cashier = models.ForeignKey(User, related_name='board_cashier')
    sports_group = models.OneToOneField(SportsGroup, on_delete=models.CASCADE)

    def __str__(self):
        return "Board of NTNUI %s" % self.sports_group.name


class Membership(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(SportsGroup, on_delete=models.CASCADE)
    date_joined = models.DateField()
