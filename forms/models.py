from django.db import models
from accounts.models import User


class FormDoc(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)

    def __str__(self):
        return self.name

class BoardChange(models.Model):
    president = models.ForeignKey(User, related_name='president')
    vice_president = models.ForeignKey(User, related_name='vice_president')
    cashier = models.ForeignKey(User, related_name='cashier')

    @classmethod
    def create(cls, p, vp, c):
        board_change = cls(president=p, vice_president=vp, cashier=c)

        return board_change

    def __str__(self):
        return "President: {}\nVice President: {}\nCashier: {}".format(
            self.president, self.vice_president, self.cashier)

    def __eq__(self, other):
        if self.president != other.president:
            return False

        if self.vice_president != other.vice_president:
            return False

        if self.cashier != other.cashier:
            return False

        return True
