from django.db import models
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from events.models.abstract_classes import CommonDescription
from events.models.event import Event


class Category(models.Model):
    """ Created to make it possible to categorize sub-events into sections (e.g. based on different skill levels). """

    event = models.ForeignKey(Event, verbose_name=_('event'))

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    # Finds the browser's language setting, and returns the category's name in the preferred language.
    def name(self):

        # Filter for desirable languages.
        browser_language_category_description = CategoryDescription.objects.filter(
            category=self, language=translation.get_language())
        english_category_description = CategoryDescription.objects.filter(category=self, language='en')
        any_category_description = CategoryDescription.objects.filter(category=self)

        # Checks if there exists a category name in the browser's language.
        if browser_language_category_description.exists():
            return browser_language_category_description[0].name

        # Checks if there exists an English category name.
        elif english_category_description.exists():
            return english_category_description[0].name

        # Checks if there exists any category name.
        elif any_category_description.exists():
            return any_category_description[0].name

        # No category name exists.
        else:
            return 'No name given'

    def __str__(self):
        return self.name()


class CategoryDescription(CommonDescription):
    """ Created to support multiple languages for each category's name and description. """

    category = models.ForeignKey(Category, verbose_name=_('category'))

    class Meta:
        verbose_name = _('description')
        verbose_name_plural = _('descriptions')
