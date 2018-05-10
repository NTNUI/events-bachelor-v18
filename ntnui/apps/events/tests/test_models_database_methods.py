from datetime import date
from unittest.mock import MagicMock, Mock, patch

from django.test import TestCase
from django.utils import translation

from accounts.models import User
from events.models import (Category, CategoryDescription, Event,
                           EventDescription, EventRegistration, Restriction,
                           SubEvent, SubEventDescription, SubEventRegistration,
                           Tag)
from groups.models import SportsGroup


"""
Tests for models.py methods which require database calls.
Tested Event method(s):     get_cover_upload_to, name, description, get_attendees.
Tested Category method(s):  name.
Tested SubEvent method(s):  name.
"""


class TestEventModels(TestCase):

    def setUpEventMethods(self):
        # event with norwegian and english event description
        self.event = Event.objects.create(start_date=date.today(), end_date=date.today())

        self.event_description_nb = EventDescription.objects.\
            create(event=self.event, language='nb', name='event_name_nb', description_text='event_description_nb')

        self.event_description_en = EventDescription.objects.\
            create(event=self.event, language='en', name='event_name_en', description_text='event_description_en')

        # event with an event description
        # fall back language for our test purpose when the event neither has norwegian nor english description
        self.event_second_fall_back = Event.objects.create(start_date=date.today(), end_date=date.today())

        self.event_description_second_fall_back = EventDescription.objects.\
            create(event=self.event_second_fall_back, language='second_fall_back',
                   name='event_name_second_fall_back', description_text='event_description_second_fall_back')

        # event with no event descriptions
        self.event_no_event_description = Event.objects.create(start_date=date.today(), end_date=date.today())

        # event registration
        self.attendee_event = User.objects.create()

        self.event_registration = EventRegistration.objects.\
            create(event=self.event, attendee=self.attendee_event, registration_time=date.today())

    def setUpCategoryMethods(self):
        self.event_for_category = Event.objects.create(start_date=date.today(), end_date=date.today())

        # category with norwegian and english category description
        self.category = Category.objects.create(event=self.event_for_category)

        self.category_description_nb = CategoryDescription.objects.\
            create(category=self.category, name='category_name_nb', language='nb')

        self.category_description_en = CategoryDescription.objects.\
            create(category=self.category, name='category_name_en', language='en')

        # category with an category description
        # fall back language for our test purpose when the category neither has norwegian nor english description
        self.category_second_fall_back = Category.objects.create(event=self.event_for_category)

        self.category_description_second_fall_back = CategoryDescription.objects.create(
            category=self.category_second_fall_back,
            language='second_fall_back', name='category_name_second_fall_back')

        # category with no category description
        self.category_no_event_description = Category.objects.create(event=self.event_for_category)

    def setUpSubEventMethods(self):
        self.event_for_category = Event.objects.create(start_date=date.today(), end_date=date.today())
        self.category_for_sub_event = Category.objects.create(event=self.event_for_category)

        # sub-event with norwegian and english category description
        self.sub_event = SubEvent.objects.\
            create(start_date=date.today(), end_date=date.today(), category=self.category_for_sub_event)

        self.sub_event_description_nb = SubEventDescription.objects.\
            create(sub_event=self.sub_event, language='nb', name='sub_event_name_nb')

        self.sub_event_description_en = SubEventDescription.objects.\
            create(sub_event=self.sub_event, language='en', name='sub_event_name_en')

        # sub-event with an category description
        # fall back language for our test purpose when the sub-event neither has norwegian nor english description
        self.sub_event_second_fall_back = SubEvent.objects.\
            create(start_date=date.today(), end_date=date.today(), category=self.category_for_sub_event)

        self.sub_event_description = SubEventDescription.objects.\
            create(sub_event=self.sub_event_second_fall_back,
                   language='second_fall_back', name='sub_event_name_second_fall_back')

        # sub-event with no category description
        self.sub_event_no_event_description = SubEvent.objects.\
            create(start_date=date.today(), end_date=date.today(), category=self.category_for_sub_event)

    """
    The Event model has the following method(s):
    get_cover_upload_to, name, description, get_host, get_attendees, attends, __str__
    """
    # test: get_cover_upload_to
    def test_event_get_cover_upload_to(self):
        # arrange
        self.setUpEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the event has an EventDescription for the given language
        translation.get_language = Mock(return_value='nb')

        # act
        result = self.event.get_cover_upload_to('filename')

        # assert
        self.assertEqual(result, 'cover_photo/events/event_name_nb\\filename',
                         "event's name = event_name_nb, image = filename")

    # test: name, if
    def test_event_name_given_language(self):
        # arrange
        self.setUpEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the event has an EventDescription for the given language
        translation.get_language = Mock(return_value='nb')

        # act
        result = self.event.name()

        # assert
        self.assertEqual(result, 'event_name_nb', "should return the event's name in the given language (nb).")

    # test: name, elif (first)
    def test_event_name_fall_back_english(self):
        # arrange
        self.setUpEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the event hasn't got an EventDescription for the given language
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.event.name()

        # assert
        self.assertEqual(result, 'event_name_en', "should return the event's name in english (en).")

    # test: name, elif (second)
    def test_event_name_second_fall_back(self):
        # arrange
        self.setUpEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the event hasn't got an EventDescription for the given language, nor english
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.event_second_fall_back.name()

        # assert
        self.assertEqual(result, 'event_name_second_fall_back',
                         "should return the event's name in the fall back language (second_fall_back).")

    # test: name, else
    def test_event_name_no_name_given(self):
        # arrange
        self.setUpEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the event hasn't got an EventDescription for the given language, english or any other language
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.event_no_event_description.name()

        # assert
        self.assertEqual(result, 'No name given',
                         "event has no name (EventDescription for event doesn't exist, hence no name).")

    # test: description, if
    def test_event_description_given_language(self):
        # arrange
        self.setUpEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the event has an EventDescription for the given language
        translation.get_language = Mock(return_value='nb')

        # act
        result = self.event.description()

        # assert
        self.assertEqual(result, 'event_description_nb',
                         "Should return the event's description in the given language (nb).")

    # test: description, elif (first)
    def test_event_description_fall_back_english(self):
        # arrange
        self.setUpEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the event hasn't got an EventDescription for the given language
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.event.description()

        # assert
        self.assertEqual(result, 'event_description_en', "Should return the event's description in english (en).")

    # test: description, elif (second)
    def test_event_description_second_fall_back(self):
        # arrange description, elif (second)
        self.setUpEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the event hasn't got an EventDescription for the given language, nor english
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.event_second_fall_back.description()

        # assert
        self.assertEqual(result, 'event_description_second_fall_back',
                         "Should return the event's description in the fall back language.")

    # test: description, else
    def test_event_name_no_description_given(self):
        # arrange
        self.setUpEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the event hasn't got an EventDescription for the given language, english or any other language
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.event_no_event_description.description()

        # assert
        self.assertEqual(result, 'No description given',
                         "Should return that the event has no description (EventDescription for event doesn't exist).")

    def test_get_attendees(self):
        # arrange
        self.setUpEventMethods()

        # act
        result = self.event.get_attendees()

        # assert
        self.assertCountEqual(result, EventRegistration.objects.filter(event=self.event))

    """The Category model has the following method(s): name, __str__"""
    # test: name, if
    def test_category_name_given_language(self):
        # arrange
        self.setUpCategoryMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the category has an CategoryDescription for the given language
        translation.get_language = Mock(return_value='nb')

        # act
        result = self.category.name()

        # assert
        self.assertEqual(result, 'category_name_nb', "should return the category's name in the given language (nb).")

    # test: name, elif (first)
    def test_category_name_fall_back_english(self):
        # arrange
        self.setUpCategoryMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the category hasn't got an CategoryDescription for the given language
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.category.name()

        # assert
        self.assertEqual(result, 'category_name_en', "should return the category's name in english (en).")

    # test: name, elif (second)
    def test_category_name_second_fall_back(self):
        # arrange
        self.setUpCategoryMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the event hasn't got an CategoryDescription for the given language, nor english
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.category_second_fall_back.name()

        # assert
        self.assertEqual(result, 'category_name_second_fall_back',
                         "Should return the category's name in the fall back language.")

    # test: name, else
    def test_category_name_no_name_given(self):
        # arrange
        self.setUpCategoryMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the category hasn't got a CategoryDescription for the given language, english or any other language
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.category_no_event_description.name()

        # assert
        self.assertEqual(result, 'No name given',
                         "Should return that the category has no name (CategoryDescription for category doesn't exist)")

    """The SubEvent model has the following method(s): name, attends, __str__"""
    # test: name, if
    def test_sub_event_name_get_language(self):
        # arrange
        self.setUpSubEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the sub-event has an event description for the given language
        translation.get_language = Mock(return_value='nb')

        # act
        result = self.sub_event.name()

        # assert
        self.assertEqual(result, 'sub_event_name_nb', "should return the sub-event's name in the given language (nb).")

    # test: name, elif (first)
    def test_sub_event_name_english(self):
        # arrange
        self.setUpSubEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the sub-event hasn't got an SubEventDescription for the given language
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.sub_event.name()

        # assert
        self.assertEqual(result, 'sub_event_name_en', "should return the sub-event's name in english (en).")

    # test: name, elif (second)
    def test_sub_event_name_fall_back(self):
        # arrange
        self.setUpSubEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the sub-event hasn't got an SubEventDescription for the given language, nor english
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.sub_event_second_fall_back.name()

        # assert
        self.assertEqual(result, 'sub_event_name_second_fall_back',
                         "should return the sub-event's name in the fall back language (second_fall_back).")

    # test: name, else
    def test_sub_event_name_no_name_given(self):
        # arrange
        self.setUpSubEventMethods()
        # the behaviour of translation.get_language() is mocked to avoid dependencies
        # the sub-event hasn't got an SubEventDescription for the given language, english or any other language
        translation.get_language = Mock(return_value='undefined language')

        # act
        result = self.sub_event_no_event_description.name()

        # assert
        self.assertEqual(result, 'No name given',
                         "sub-event has no name (SubEventDescription for event doesn't exist, hence no name).")
