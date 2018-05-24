from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytz
from django.test import TestCase
from django.utils import translation

from accounts.models import User
from events.models.event import (Event, EventDescription,
                                 EventGuestRegistration, EventGuestWaitingList,
                                 EventRegistration, EventWaitingList)
from events.models.guest import Guest
from groups.models import SportsGroup

""" Tests the Event model's functions. """


class TestEventModel(TestCase):

    def setUp(self):
        self.event = Event.objects.create(
            start_date=datetime.now(pytz.utc), end_date=datetime.now(pytz.utc) + timedelta(days=2))

    """ Tests the Event model's get_cover_upload_to function. """
    def test_get_cover_upload_to(self):

        # arrange
        path = 'cover_photo/events/event_name_nb\\filename'
        translation.get_language = Mock(return_value='nb')
        EventDescription.objects.create(
            event=self.event, language='nb', name='event_name_nb', description_text='event_description_nb')

        # act
        result = self.event.get_cover_upload_to('filename')

        # assert
        self.assertEqual(result, path)

    """ Tests the Event model's name function, where it chooses the browser's language. """
    def test_name_browser_language(self):

        # arrange
        translation.get_language = Mock(return_value='nb')
        EventDescription.objects.create(
            event=self.event, language='nb', name='name_nb', description_text='event_description_nb')

        # act
        result = self.event.name()

        # assert
        self.assertEqual(result, 'name_nb')

    """ Tests the Event model's name function, where it chooses the english fall back option. """
    def test_name_fall_back_english(self):

        # arrange
        EventDescription.objects.create(
            event=self.event, language='nn', name='name_nn', description_text='event_description_nn')
        EventDescription.objects.create(
            event=self.event, language='en', name='name_en', description_text='event_description_en')

        # act
        result = self.event.name()

        # assert
        self.assertEqual(result, 'name_en')

    """ Tests the Event model's name function, where it chooses any fall back option. """
    def test_name_fall_back_any(self):

        # arrange
        EventDescription.objects.create(
            event=self.event, language='nn', name='name_nn', description_text='event_description_nn')

        # act
        result = self.event.name()

        # assert
        self.assertEqual(result, 'name_nn')

    """ Tests the Event model's name function, where no name is given. """
    def test_name_no_name_given(self):

        # act
        result = self.event.name()

        # assert
        self.assertEqual(result, 'No name given')

    """ Tests the Event model's description function, where it chooses the browser's language. """
    def test_description_browser_language(self):

        # arrange
        translation.get_language = Mock(return_value='nb')
        EventDescription.objects.create(
            event=self.event, language='nb', name='name_nb', description_text='event_description_nb')

        # act
        result = self.event.description()

        # assert
        self.assertEqual(result, 'event_description_nb')

    """ Tests the Event model's description function, where it chooses the english fall back option. """
    def test_description_fall_back_english(self):

        # arrange
        EventDescription.objects.create(
            event=self.event, language='nn', name='name_nn', description_text='event_description_nn')
        EventDescription.objects.create(
            event=self.event, language='en', name='name_en', description_text='event_description_en')

        # act
        result = self.event.description()

        # assert
        self.assertEqual(result, 'event_description_en')

    """ Tests the Event model's description function, where it chooses any fall back option. """
    def test_description_fall_back_any(self):

        # arrange
        EventDescription.objects.create(
            event=self.event, language='nn', name='name_nn', description_text='event_description_nn')

        # act
        result = self.event.description()

        # assert
        self.assertEqual(result, 'event_description_nn')

    """ Tests the Event model's description function, where no name is given. """
    def test_description_no_description_given(self):

        # act
        result = self.event.description()

        # assert
        self.assertEqual(result, 'No description given')

    """ Tests the Event model's get_host() function, where NTNUI is the host. """
    def test_get_host_NTNUI(self):

        # arrange
        self.event.is_host_ntnui = Mock(return_value=True)

        # act
        result = self.event.get_host()

        # assert
        self.assertEqual(result, ['NTNUI'])

    """ Tests the Event model's get_host() function, where a sports group is the host. """
    def test_get_host_sports_group(self):

        # arrange
        sports_group = SportsGroup.objects.create(name='sports_group', slug='SG', description='description')
        sports_group.save()
        self.event.sports_groups.add(sports_group)

        # act
        result = self.event.get_host()

        # assert
        self.assertEqual(result, ['sports_group'])

    """ Tests the Event model's get_attendee_list() function. """
    def test_get_attendee_list(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)
        event_registration = EventRegistration.objects.create(
            event=self.event, attendee=user, registration_time=datetime.now(pytz.utc))
        event_guest_registration = EventGuestRegistration.objects.create(
            event=self.event, attendee=guest, registration_time=datetime.now(pytz.utc))

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(Event, 'name', return_value='event_name'):

            # act
            result = self.event.get_attendee_list()

            # assert
            self.assertEqual(result, [event_registration, event_guest_registration])

    """ Tests the Event model's get_waiting_list() function. """
    def test_get_waiting_list(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)
        event_waiting_list = EventWaitingList.objects.create(
            event=self.event, attendee=user, registration_time=datetime.now(pytz.utc))
        event_guest_waiting_list = EventGuestWaitingList.objects.create(
            event=self.event, attendee=guest, registration_time=datetime.now(pytz.utc))

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(Event, 'name', return_value='event_name'):

            # act
            result = self.event.get_waiting_list()

            # assert
            self.assertEqual(result, [event_waiting_list, event_guest_waiting_list])

    """ Tests the Event model's get_waiting_list_next() function, where one is on the waiting list. """
    def test_get_waiting_list_next(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        EventWaitingList.objects.create(event=self.event, attendee=user, registration_time=datetime.now(pytz.utc))

        # act
        result = self.event.get_waiting_list_next()

        # assert
        self.assertEqual(result, (user, None))

    """ Tests the Event model's get_waiting_list_next() function, where no one is on the waiting list. """
    def test_get_waiting_list_next_empty(self):

        # act
        result = self.event.get_waiting_list_next()

        # assert
        self.assertEqual(result, None)

    """ Tests the Event model's user_attend() function. """
    def test_user_attend(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')

        # act
        self.event.user_attend(user, None, datetime.now(pytz.utc), token='token')

        # assert
        self.assertEqual(EventRegistration.objects.count(), 1)

    """ Tests the Event model's guest_attend() function. """
    def test_guest_attend(self):

        # arrange
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)

        # act
        self.event.guest_attend(guest, None, datetime.now(pytz.utc), token='token')

        # assert
        self.assertEqual(EventGuestRegistration.objects.count(), 1)

    """ Tests the Event model's user_attend() function. """
    def test_user_attend_waiting_list(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')

        # act
        self.event.user_attend_waiting_list(user, None, datetime.now(pytz.utc), token='token')

        # assert
        self.assertEqual(EventWaitingList.objects.count(), 1)

    """ Tests the Event model's guest_attend() function. """
    def test_guest_attend_waiting_list(self):

        # arrange
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)

        # act
        self.event.guest_attend_waiting_list(guest, None, datetime.now(pytz.utc), token='token')

        # assert
        self.assertEqual(EventGuestWaitingList.objects.count(), 1)

    """ Tests the Event model's user_attendance_delete() function. """
    def test_user_attendance_delete(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        EventRegistration.objects.create(event=self.event, attendee=user, registration_time=datetime.now(pytz.utc))

        # act
        self.event.user_attendance_delete(user)

        # assert
        self.assertEqual(EventRegistration.objects.count(), 0)

    """ Tests the Event model's user_waiting_list_delete() function. """
    def test_user_waiting_list_delete(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        EventWaitingList.objects.create(event=self.event, attendee=user, registration_time=datetime.now(pytz.utc))

        # act
        self.event.user_waiting_list_delete(user)

        # assert
        self.assertEqual(EventWaitingList.objects.count(), 0)

    """ Tests the Event model's is_user_enrolled() function. """
    def test_is_user_enrolled(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        EventRegistration.objects.create(event=self.event, attendee=user, registration_time=datetime.now(pytz.utc))

        # act
        result = self.event.is_user_enrolled(user)

        # assert
        self.assertEqual(result, True)

    """ Tests the Event model's is_user_enrolled() function. """
    def test_is_user_on_waiting_list(self):

        # arrange
        user = User.objects.create(email='username@domain.com', password='password')
        EventWaitingList.objects.create(event=self.event, attendee=user, registration_time=datetime.now(pytz.utc))

        # act
        result = self.event.is_user_on_waiting_list(user)

        # assert
        self.assertEqual(result, True)

        """ Tests the Event model's is_user_enrolled() function. """

    def test_is_guest_enrolled(self):

        # arrange
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)
        EventGuestRegistration.objects.create(
            event=self.event, attendee=guest, registration_time=datetime.now(pytz.utc))

        # act
        result = self.event.is_guest_enrolled(guest)

        # assert
        self.assertEqual(result, True)

    """ Tests the Event model's is_user_enrolled() function. """

    def test_is_guest_on_waiting_list(self):

        # arrange
        guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)
        EventGuestWaitingList.objects.create(event=self.event, attendee=guest, registration_time=datetime.now(pytz.utc))

        # act
        result = self.event.is_guest_on_waiting_list(guest)

        # assert
        self.assertEqual(result, True)

    """ Tests the Event model's __str__ function. """
    def test_str(self):

        # arrange
        event_name = 'name'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(Event, 'name', return_value=event_name):

            # act
            result = str(self.event)

            # assert
            self.assertEqual(result, event_name)


""" 
    Tests the EventRegistration, EventWaitingList, EventGuestRegistration, and EventGuestWaitingList models' functions. 
"""


class TestEventRegistrationModels(TestCase):

    def setUp(self):
        self.user = User.objects.create(email='username@domain.com', password='password')

        self.guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)

        self.event = Event.objects.create(
            start_date=datetime.now(pytz.utc), registration_end_date=datetime.now(pytz.utc) + timedelta(days=2),
            end_date=datetime.now(pytz.utc) + timedelta(days=1), attendance_cap=100, price=100)

        self.event_registration = EventRegistration.objects.create(
            event=self.event, attendee=self.user, registration_time=datetime.now(pytz.utc))

        self.event_waiting_list = EventWaitingList.objects.create(
            event=self.event, attendee=self.user, registration_time=datetime.now(pytz.utc))

        self.event_guest_registration = EventGuestRegistration.objects.create(
            event=self.event, attendee=self.guest, registration_time=datetime.now(pytz.utc))

        self.event_guest_waiting_list = EventGuestWaitingList.objects.create(
            event=self.event, attendee=self.guest, registration_time=datetime.now(pytz.utc))

    """ Tests the EventRegistration model's __str__ function. """
    def test_event_registration_str(self):

        # arrange
        event_registration_name = 'event_name - username@domain.com'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(Event, 'name', return_value='event_name'):

            # act
            result = str(self.event_registration)

            # assert
            self.assertEqual(result, event_registration_name)

    """ Tests the EventWaitingList model's __str__ function. """
    def test_event_waiting_list_str(self):

        # arrange
        event_waiting_list_name = 'event_name - username@domain.com'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(Event, 'name', return_value='event_name'):

            # act
            result = str(self.event_waiting_list)

            # assert
            self.assertEqual(result, event_waiting_list_name)

    """ Tests the EventGuestRegistration model's __str__ function. """
    def test_event_guest_registration_str(self):

        # arrange
        event_guest_registration_name = 'event_name - username@domain.com'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(Event, 'name', return_value='event_name'):

            # act
            result = str(self.event_guest_registration)

            # assert
            self.assertEqual(result, event_guest_registration_name)

    """ Tests the EventGuestRegistration model's __str__ function. """
    def test_event_guest_waiting_list_str(self):

        # arrange
        event_guest_waiting_list_name = 'event_name - username@domain.com'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(Event, 'name', return_value='event_name'):

            # act
            result = str(self.event_guest_waiting_list)

            # assert
            self.assertEqual(result, event_guest_waiting_list_name)
