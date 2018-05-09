from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    """ Created to make searching for events and sub-events easier by giving additional searchable elements. """

    name = models.CharField(_('name'), max_length=50)

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name
