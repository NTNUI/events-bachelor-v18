from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytz
from django.test import TestCase
from django.utils import translation

from accounts.models import User
from events.models.category import Category
from events.models.event import Event
from events.models.guest import Guest
from events.models.sub_event import (SubEvent, SubEventDescription,
                                     SubEventGuestRegistration,
                                     SubEventGuestWaitingList,
                                     SubEventRegistration, SubEventWaitingList)
from groups.models import SportsGroup

""" Tests the SubEvent model's functions. """


class TestEventModel(TestCase):

    def setUp(self):
        self.event = Event.objects.create(
            start_date=datetime.now(pytz.utc), end_date=datetime.now(pytz.utc) + timedelta(days=2))
        self.event.save()
        self.category = Category.objects.create(event=self.event)
        self.category.save()
        self.sub_event = SubEvent.objects.create(category=self.category, start_date=datetime.now(pytz.utc),
                                                 end_date=datetime.now(pytz.utc) + timedelta(days=2))

    """ Tests the SubEvent model's name function, where it chooses the browser's language. """
    def test_name_browser_language(self):

        # arrange
        translation.get_language = Mock(return_value='nb')
        SubEventDescription.objects.create(
            sub_event=self.sub_event, language='nb', name='name_nb')

        # act
        result = self.sub_event.name()

        # assert
        self.assertEqual(result, 'name_nb')

    """ Tests the SubEvent model's name function, where it chooses the english fall back option. """
    def test_name_fall_back_english(self):

        # arrange
        SubEventDescription.objects.create(
            sub_event=self.sub_event, language='nn', name='name_nn')
        SubEventDescription.objects.create(
            sub_event=self.sub_event, language='en', name='name_en')

        # act
        result = self.sub_event.name()

        # assert
        self.assertEqual(result, 'name_en')

    """ Tests the SubEvent model's name function, where it chooses any fall back option. """
    def test_name_fall_back_any(self):

        # arrange
        SubEventDescription.objects.create(
            sub_event=self.sub_event, language='nn', name='name_nn')

        # act
        result = self.sub_event.name()

        # assert
        self.assertEqual(result, 'name_nn')

    """ Tests the SubEvent model's name function, where no name is given. """
    def test_name_no_name_given(self):

        # act
        result = self.sub_event.name()

        # assert
        self.assertEqual(result, 'No name given')

    """ Tests the SubEvent model's get_host function. """
    def test_get_host(self):

        # the behaviour of event.get_host() is mocked to avoid dependencies
        with patch.object(Event, 'get_host', return_value=['sports_group']):

            # act
            result = self.sub_event.get_host()

            # assert
            self.assertEqual(result, ['sports_group'])

    """ Tests the SubEvent model's get_attendee_list() function. """
    def test_get_attendee_list(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)
        sub_event_registration = SubEventRegistration.objects.create(
            sub_event=self.sub_event, attendee=user, registration_time=datetime.now(pytz.utc))
        sub_event_guest_registration = SubEventGuestRegistration.objects.create(
            sub_event=self.sub_event, attendee=guest, registration_time=datetime.now(pytz.utc))

        # the behaviour of sub_event.name() is mocked to avoid dependencies
        with patch.object(SubEvent, 'name', return_value='event_name'):

            # act
            result = self.sub_event.get_attendee_list()

            # assert
            self.assertEqual(result, [sub_event_registration, sub_event_guest_registration])

    """ Tests the SubEvent model's get_waiting_list() function. """
    def test_get_waiting_list(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)
        sub_event_waiting_list = SubEventWaitingList.objects.create(
            sub_event=self.sub_event, attendee=user, registration_time=datetime.now(pytz.utc))
        sub_event_guest_waiting_list = SubEventGuestWaitingList.objects.create(
            sub_event=self.sub_event, attendee=guest, registration_time=datetime.now(pytz.utc))

        # the behaviour of sub_event.name() is mocked to avoid dependencies
        with patch.object(SubEvent, 'name', return_value='event_name'):

            # act
            result = self.sub_event.get_waiting_list()

            # assert
            self.assertEqual(result, [sub_event_waiting_list, sub_event_guest_waiting_list])

    """ Tests the SubEvent model's get_waiting_list_next() function, where one is on the waiting list. """
    def test_get_waiting_list_next(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        SubEventWaitingList.objects.create(
            sub_event=self.sub_event, attendee=user, registration_time=datetime.now(pytz.utc))

        # act
        result = self.sub_event.get_waiting_list_next()

        # assert
        self.assertEqual(result, (user, None))

    """ Tests the SubEvent model's get_waiting_list_next() function, where no one is on the waiting list. """
    def test_get_waiting_list_next_empty(self):

        # act
        result = self.sub_event.get_waiting_list_next()

        # assert
        self.assertEqual(result, None)

    """ Tests the SubEvent model's user_attend() function. """
    def test_user_attend(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')

        # act
        self.sub_event.user_attend(user, None, datetime.now(pytz.utc), token='token')

        # assert
        self.assertEqual(SubEventRegistration.objects.count(), 1)

    """ Tests the SubEvent model's guest_attend() function. """
    def test_guest_attend(self):

        # arrange
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)

        # act
        self.sub_event.guest_attend(guest, None, datetime.now(pytz.utc), token='token')

        # assert
        self.assertEqual(SubEventGuestRegistration.objects.count(), 1)

    """ Tests the SubEvent model's user_attend() function. """
    def test_user_attend_waiting_list(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')

        # act
        self.sub_event.user_attend_waiting_list(user, None, datetime.now(pytz.utc), token='token')

        # assert
        self.assertEqual(SubEventWaitingList.objects.count(), 1)

    """ Tests the SubEvent model's guest_attend() function. """
    def test_guest_attend_waiting_list(self):

        # arrange
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)

        # act
        self.sub_event.guest_attend_waiting_list(guest, None, datetime.now(pytz.utc), token='token')

        # assert
        self.assertEqual(SubEventGuestWaitingList.objects.count(), 1)

    """ Tests the SubEvent model's user_attendance_delete() function. """
    def test_user_attendance_delete(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        SubEventRegistration.objects.create(
            sub_event=self.sub_event, attendee=user, registration_time=datetime.now(pytz.utc))

        # act
        self.sub_event.user_attendance_delete(user)

        # assert
        self.assertEqual(SubEventRegistration.objects.count(), 0)

    """ Tests the SubEvent model's user_waiting_list_delete() function. """
    def test_user_waiting_list_delete(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        SubEventWaitingList.objects.create(
            sub_event=self.sub_event, attendee=user, registration_time=datetime.now(pytz.utc))

        # act
        self.sub_event.user_waiting_list_delete(user)

        # assert
        self.assertEqual(SubEventWaitingList.objects.count(), 0)

    """ Tests the SubEvent model's is_user_enrolled() function. """
    def test_is_user_enrolled(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        SubEventRegistration.objects.create(
            sub_event=self.sub_event, attendee=user, registration_time=datetime.now(pytz.utc))

        # act
        result = self.sub_event.is_user_enrolled(user)

        # assert
        self.assertEqual(result, True)

    """ Tests the SubEvent model's is_user_enrolled() function. """
    def test_is_user_on_waiting_list(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        SubEventWaitingList.objects.create(
            sub_event=self.sub_event, attendee=user, registration_time=datetime.now(pytz.utc))

        # act
        result = self.sub_event.is_user_on_waiting_list(user)

        # assert
        self.assertEqual(result, True)

        """ Tests the SubEvent model's is_user_enrolled() function. """

    def test_is_guest_enrolled(self):
        # arrange
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)
        SubEventGuestRegistration.objects.create(
            sub_event=self.sub_event, attendee=guest, registration_time=datetime.now(pytz.utc))

        # act
        result = self.sub_event.is_guest_enrolled(guest)

        # assert
        self.assertEqual(result, True)

    """ Tests the SubEvent model's is_user_enrolled() function. """

    def test_is_guest_on_waiting_list(self):

        # arrange
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)
        SubEventGuestWaitingList.objects.create(
            sub_event=self.sub_event, attendee=guest, registration_time=datetime.now(pytz.utc))

        # act
        result = self.sub_event.is_guest_on_waiting_list(guest)

        # assert
        self.assertEqual(result, True)

    """ Tests the Event model's __str__ function. """
    def test_str(self):

        # arrange
        sub_event_name = 'name'

        # the behaviour of sub_event.name() is mocked to avoid dependencies
        with patch.object(SubEvent, 'name', return_value=sub_event_name):

            # act
            result = str(self.sub_event)

            # assert
            self.assertEqual(result, sub_event_name)


""" 
    Tests the SubEventRegistration, SubEventWaitingList, 
    SubEventGuestRegistration, and SubEventGuestWaitingList models' functions. 
"""


class TestEventRegistrationModels(TestCase):

    def setUp(self):
        self.user = User.objects.create(email='username@domain.com', password='password')

        self.guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)

        self.event = Event.objects.create(
            start_date=datetime.now(pytz.utc), end_date=datetime.now(pytz.utc) + timedelta(days=2))

        self.category = Category.objects.create(event=self.event)

        self.sub_event = SubEvent.objects.create(category=self.category, start_date=datetime.now(pytz.utc),
                                                 end_date=datetime.now(pytz.utc) + timedelta(days=2))

        self.sub_event_registration = SubEventRegistration.objects.create(
            sub_event=self.sub_event, attendee=self.user, registration_time=datetime.now(pytz.utc))

        self.sub_event_waiting_list = SubEventWaitingList.objects.create(
            sub_event=self.sub_event, attendee=self.user, registration_time=datetime.now(pytz.utc))

        self.sub_event_guest_registration = SubEventGuestRegistration.objects.create(
            sub_event=self.sub_event, attendee=self.guest, registration_time=datetime.now(pytz.utc))

        self.sub_event_guest_waiting_list = SubEventGuestWaitingList.objects.create(
            sub_event=self.sub_event, attendee=self.guest, registration_time=datetime.now(pytz.utc))

    """ Tests the SubEventRegistration model's __str__ function. """
    def test_sub_event_registration_str(self):

        # arrange
        event_registration_name = 'event_name - username@domain.com'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(SubEvent, 'name', return_value='event_name'):

            # act
            result = str(self.sub_event_registration)

            # assert
            self.assertEqual(result, event_registration_name)

    """ Tests the SubEventWaitingList model's __str__ function. """
    def test_sub_event_waiting_list_str(self):

        # arrange
        sub_event_waiting_list_name = 'event_name - username@domain.com'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(SubEvent, 'name', return_value='event_name'):

            # act
            result = str(self.sub_event_waiting_list)

            # assert
            self.assertEqual(result, sub_event_waiting_list_name)

    """ Tests the SubEventGuestRegistration model's __str__ function. """
    def test_sub_event_guest_registration_str(self):

        # arrange
        sub_event_guest_registration_name = 'event_name - username@domain.com'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(SubEvent, 'name', return_value='event_name'):

            # act
            result = str(self.sub_event_guest_registration)

            # assert
            self.assertEqual(result, sub_event_guest_registration_name)

    """ Tests the SubEventGuestRegistration model's __str__ function. """
    def test_sub_event_guest_waiting_list_str(self):

        # arrange
        sub_event_guest_waiting_list_name = 'event_name - username@domain.com'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(SubEvent, 'name', return_value='event_name'):

            # act
            result = str(self.sub_event_guest_waiting_list)

            # assert
            self.assertEqual(result, sub_event_guest_waiting_list_name)
