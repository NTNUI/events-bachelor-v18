from datetime import datetime, timedelta
from unittest.mock import patch

import pytz
from django.test import TestCase

from accounts.models import User
from events.models.category import Category
from events.models.event import (Event, EventDescription,
                                 EventGuestRegistration, EventGuestWaitingList,
                                 EventRegistration, EventWaitingList)
from events.models.guest import Guest
from events.models.sub_event import SubEvent
from events.event_attendance import (attend_event_request, event_has_sub_events,
                                     delete_guest, create_mail_header)


class TestEventAttendanceView(TestCase):

    def setUp(self):
        self.user = User.objects.create(email='username@domain.com', password='password')

        self.guest = Guest.objects.create(
            first_name='first_name', last_name='last_name', email='username@domain.com', phone_number=41325095)

        self.event = Event.objects.create(
            start_date=datetime.now(pytz.utc), end_date=datetime.now(pytz.utc) + timedelta(days=2))

    def test_event_has_sub_events(self):

        # arrange
        self.category = Category.objects.create(event=self.event)

        self.sub_event = SubEvent.objects.create(category=self.category, start_date=datetime.now(pytz.utc),
                                                 end_date=datetime.now(pytz.utc) + timedelta(days=2))

        # act
        result = event_has_sub_events(self.event)

        # assert
        self.assertEqual(result[0], True)

    def test_event_has_sub_events_no_sub_event(self):

        # act
        result = event_has_sub_events(self.event)

        # assert
        self.assertEqual(result, (False, None))

    def test_delete_guest(self):

        # act
        delete_guest(self.guest)

        # assert
        self.assertEqual(Guest.objects.count(), 0)

    def test_create_mail_header(self):

        # arrange
        sender = 'noreply@mg.ntnui.no'
        receiver = ['username@domain.com']
        subject = 'event_name - NTNUI Handball'

        # the behaviour of event.name() is mocked to avoid dependencies
        with patch.object(Event, 'name', return_value='event_name'):

            # the behaviour of event.get_host() is mocked to avoid dependencies
            with patch.object(Event, 'get_host', return_value=['NTNUI Handball']):

                # act
                result = create_mail_header(self.event, self.user)

                # assert
                self.assertEqual(result, (sender, receiver, subject))
