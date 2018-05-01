from django.db import models
from django.utils.translation import gettext_lazy as _


class Restriction(models.Model):
    """Restrictions makes it possible to create events for specific groups of users."""

    name = models.CharField(_('name'), max_length=50)

    class Meta:
        verbose_name = _('restriction')
        verbose_name_plural = _('restrictions')

    def __str__(self):
        return self.name
