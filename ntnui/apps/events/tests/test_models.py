from datetime import date
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.utils import translation
from accounts.models import User
from groups.models import SportsGroup
from events.models import Event, EventDescription, \
    Restriction, Tag, EventRegistration, Category, \
    CategoryDescription, SubEvent, SubEventDescription, SubEventRegistration


"""
Tests for models.py methods which doesnt require database calls.
Tested Restriction method(s):           __str__.
Tested Tag method(s):                   __str__.
Tested Event method(s):                 __str__, attends, get_host.
Tested EventDescription method(s):      __str__.
Tested EventRegistration method(s):     __str__.
Tested Category method(s):              __str__.
Tested CategoryDescription method(s):   __str__.
Tested SubEvent method(s):              __str__, attends.
Tested SubEventDescription method(s):   __str__.
Tested SubEventRegistration method(s):  __str__.
"""


class TestEventModels(TestCase):

    def setUp(self):
        self.sub_event = SubEvent()
        self.attendee = User(email='username@domain.com')
        self.event_description = EventDescription()
        self.category_description = CategoryDescription()
        self.sub_event_description = SubEventDescription()
        self.event_description = EventDescription()
        self.event = Event.objects.create(start_date=date.today(), end_date=date.today())
        self.event_registration = EventRegistration(event=self.event, attendee=self.attendee)
        self.sub_event_registration = SubEventRegistration(sub_event=self.sub_event, attendee=self.attendee)

    """The Restriction model has the following method(s): __str__"""
    # test: __str__
    def test_restriction_str(self):
        # arrange
        name = 'restriction_name'
        restriction = Restriction(name=name)

        # act
        result = str(restriction)

        # assert
        self.assertEqual(result, name, "__str__ method: return self.name")

    """The Tag model has the following method(s): __str__"""
    # test: __str__
    def test_tag_str(self):
        # arrange
        name = 'tag_name'
        tag = Tag(name=name)

        # act
        result = str(tag)

        # assert
        self.assertEqual(result, name, "__str__ method: return self.name")

    """
    The Event model has the following method(s):
    get_cover_upload_to, name, description, get_host, get_attendees, attends, __str__
    """
    # test: get_host, is_host_ntnui true; the host is NTNUI
    def test_event_get_host_ntnui(self):
        # arrange
        self.event.is_host_ntnui = True

        # act
        result = self.event.get_host()

        # assert
        self.assertEqual(result, ['NTNUI'])

    # test: get_host, is_host_ntnui false; host are groups
    def test_event_get_host_groups(self):
        # arrange
        name = 'sports_group_name'
        sports_group = SportsGroup.objects.create(name=name)
        self.event.is_host_ntnui = False
        self.event.id = 1
        self.event.sports_groups.add(sports_group)

        # act
        result = self.event.get_host()

        # assert
        self.assertEqual(result, [name])

    # test: attends, return false; user doesn't attend event
    def test_event_attends_false(self):
        # act
        result = self.event.user_attends(self.attendee)

        # assert
        self.assertFalse(result)

    # test: attends, return true; user attends event
    def test_event_attends_true(self):
        # arrange
        # the behaviour of EventRegistration.objects is mocked to avoid dependencies
        with patch.object(EventRegistration, 'objects', return_value=self.event_registration):

            # act
            result = self.event.user_attends(self.attendee)

            # assert
            self.assertTrue(result)

    # test: __str__
    def test_event_str(self):
        # arrange
        name = 'event_name'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(Event, 'name', return_value=name):

            # act
            result = str(self.event)

            # assert
            self.assertEqual(result, name, "__str__ method: return self.name()")

    """The EventDescription model has the following method(s): __str__"""
    # test: __str__
    def test_event_description_str(self):
        # arrange
        name = 'event_description_name'
        self.event_description.name = name

        # act
        result = str(self.event_description)

        # assert
        self.assertEqual(result, name, "__str__ method: return self.name")

    """The EventRegistration model has the following method(s): __str__"""
    # test: __str__
    def test_event_registration_str(self):
        # arrange
        expected_result = 'event_name - username@domain.com'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(Event, 'name', return_value='event_name'):

            # act
            result = str(self.event_registration)

            # assert
            self.assertEqual(result, expected_result,
                             "__str__ method: return self.event.name() + ' - ' + self.attendee.email")

    """The Category model has the following method(s): name, __str__"""
    # test: __str__
    def test_category_str(self):
        # arrange
        name = 'category_name'
        category = Category()

        # the behaviour of category.name() is mocked to avoid dependencies
        with patch.object(Category, 'name', return_value=name):

            # act
            result = str(category)

            # assert
            self.assertEqual(result, name, "__str__ method: return self.name()")

    """The CategoryDescription model has the following method(s): __str__"""
    # Test: __str__
    def test_category_description_str(self):
        # arrange
        name = 'category_description_name'
        self.category_description.name = name

        # act
        result = str(self.category_description)

        # assert
        self.assertEqual(result, name, "__str__ method: return self.name")

    """The SubEvent model has the following method(s): name, attends, __str__"""
    # test: attends, return false; user doesn't attend sub-event
    def test_sub_event_attends_false(self):
        # assert
        self.assertFalse(self.sub_event.user_attends(self.attendee))

    # test: attends, return true; user attends sub-event
    def test_sub_event_attends_true(self):
        # the behaviour of SubEventRegistration.objects is mocked to avoid dependencies
        with patch.object(SubEventRegistration, 'objects', return_value=self.sub_event_registration):

            # act
            result = self.sub_event.user_attends(self.attendee)

            # assert
            self.assertTrue(result)

    # test: __str__
    def test_sub_event_str(self):
        # arrange
        name = 'sub_event_name'

        # the behaviour of sub_event.name() is mocked to avoid dependencies
        with patch.object(SubEvent, 'name', return_value=name):

            # act
            result = str(str(self.sub_event))

            # assert
            self.assertEqual(result, name, "__str__ method: return self.name()")

    """The SubEventDescription model has the following method(s): __str__"""
    # test: __str__
    def test_sub_event_description_str(self):
        # arrange
        name = 'sub_event_description_name'
        self.sub_event_description.name = name

        # act
        result = str(self.sub_event_description)

        # assert
        self.assertEqual(result, name, "__str__ method: return self.name")

    """The SubEventRegistration model has the following method(s): __str__"""
    # test: __str__
    def test_sub_event_registration_str(self):
        # arrange
        expected_result = 'sub_event_name - username@domain.com'

        # the behaviour of sub_event.name() is mocked to avoid dependencies
        with patch.object(SubEvent, 'name', return_value='sub_event_name'):

            # act
            result = str(self.sub_event_registration)

            # assert
            self.assertEqual(result, expected_result,
                             "__str__ method: return self.event.name() + ' - ' + self.attendee.email")
