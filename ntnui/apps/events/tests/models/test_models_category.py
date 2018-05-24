from datetime import datetime
from unittest.mock import Mock, patch

import pytz
from django.test import TestCase
from django.utils import translation

from events.models.category import Category, CategoryDescription
from events.models.event import Event

""" Tests the Category model's functions. """


class TestCategoryModel(TestCase):

    def setUp(self):
        self.event = Event.objects.create(
            start_date=datetime.now(pytz.utc), end_date=datetime.now(pytz.utc))
        self.category = Category.objects.create(event=self.event)

    """ Tests the Category model's __str__ function. """
    def test_str(self):

        # arrange
        category_name = 'name'

        # the behaviour of category.name() is mocked to avoid dependencies
        with patch.object(Category, 'name', return_value=category_name):

            # act
            result = str(self.category)

            # assert
            self.assertEqual(result, category_name)

    """ Tests the Category model's name function, where it chooses the browser's language. """
    def test_name_browser_language(self):

        # arrange
        translation.get_language = Mock(return_value='nb')
        self.category_description = CategoryDescription.objects.create(
            category=self.category, name='name_nb', language='nb')

        # act
        result = self.category.name()

        # assert
        self.assertEqual(result, 'name_nb')

    """ Tests the Category model's name function, where it chooses the english fall back option. """
    def test_name_fall_back_english(self):

        # arrange
        self.category_description = CategoryDescription.objects.create(
            category=self.category, name='name_nn', language='nn')
        self.category_description = CategoryDescription.objects.create(
            category=self.category, name='name_en', language='en')

        # act
        result = self.category.name()

        # assert
        self.assertEqual(result, 'name_en')

    """ Tests the Category model's name function, where it chooses any fall back option. """
    def test_name_fall_back_any(self):

        # arrange
        self.category_description = CategoryDescription.objects.create(
            category=self.category, name='name_nn', language='nn')

        # act
        result = self.category.name()

        # assert
        self.assertEqual(result, 'name_nn')

    """ Tests the Category model's name function, where no name is given. """
    def test_name_no_name_given(self):

        # act
        result = self.category.name()

        # assert
        self.assertEqual(result, 'No name given')
