from django.db import models
from accounts.models import User


class FormDoc(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)

    def __str__(self):
        return self.name

class BoardChange(FormDoc):
    president = models.ForeignKey(User, related_name='president')
    vice_president = models.ForeignKey(User, related_name='vice_president')
    cashier = models.ForeignKey(User, related_name='cashier')
