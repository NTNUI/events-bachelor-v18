from django.db import models
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from events.models.event import Event


class Category(models.Model):
    """Sub-events get divided into categories (e.g. based on different skill levels)."""

    event = models.ForeignKey(Event, verbose_name=_('event'))

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    # Returns the category's name, in the given language
    def name(self):
        category_description_get_language = CategoryDescription.objects.filter(category=self,
                                                                               language=translation.get_language())
        category_description_english = CategoryDescription.objects.filter(category=self, language='en')
        category_description = CategoryDescription.objects.filter(category=self)

        if category_description_get_language.exists():
            return category_description_get_language[0].name
        elif category_description_english.exists():
            return category_description_english[0].name
        elif category_description.exists():
            return category_description[0].name
        else:
            return 'No name given'

    def __str__(self):
        return self.name()


class CategoryDescription(models.Model):
    """Created to support multiple languages for each category's name and description."""

    name = models.CharField(_('name'), max_length=100)
    language = models.CharField(_('language'), max_length=30)
    category = models.ForeignKey(Category, verbose_name=_('category'))

    class Meta:
        verbose_name = _('description')
        verbose_name_plural = _('descriptions')

    def __str__(self):
        return self.name
