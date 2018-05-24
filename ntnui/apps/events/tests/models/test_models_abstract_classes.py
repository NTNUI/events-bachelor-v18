from datetime import datetime, timedelta
from unittest.mock import patch

import pytz
from django.test import TestCase

from accounts.models import User
from events.models.event import Event, EventDescription

""" Tests the CommonDescription model's functions. """


class TestCommonDescriptionModel(TestCase):

    def setUp(self):
        self.event = Event.objects.create(
            start_date=datetime.now(pytz.utc), end_date=datetime.now(pytz.utc) + timedelta(days=2))
        self.event_description = EventDescription.objects.create(
            event=self.event, description_text='description_text', name='name', language='en')

    """ Tests the CommonDescription model's __str__ function. """
    def test_str(self):

        # arrange
        common_description_name = 'name'

        # act
        result = str(self.event_description)

        # assert
        self.assertEquals(result, common_description_name)


""" Tests the CommonEvent model's functions. """


class TestCommonEventModel(TestCase):

    def setUp(self):
        self.event = Event.objects.create(
            start_date=datetime.now(pytz.utc), registration_end_date=datetime.now(pytz.utc) + timedelta(days=2),
            end_date=datetime.now(pytz.utc) + timedelta(days=1), attendance_cap=100, price=100)

    """ Tests the CommonEvent model's is_attendance_cap_exceeded function. """
    def test_is_attendance_cap_exceeded(self):

        # arrange
        attendee_list = [User(), User(), User()]

        # the behaviour of event.get_attendee_list() is mocked to avoid dependencies
        with patch.object(Event, 'get_attendee_list', return_value=attendee_list):

            # act
            result = self.event.is_attendance_cap_exceeded()

            # assert
            self.assertFalse(result)

    """ Tests the CommonEvent model's is_registration_ended function. """
    def test_is_registration_ended(self):

        # arrange

        # act
        result = self.event.is_registration_ended()

        # assert
        self.assertFalse(result)

    """ Tests the CommonEvent model's is_payment_event function. """
    def test_is_payment_event(self):

        # arrange

        # act
        result = self.event.is_payment_event()

        # assert
        self.assertTrue(result)

    """ Tests the CommonEvent model's is_registration_ended function. """
    def test_is_payment_event(self):

        # arrange
        payment_id = 'payment_id'

        # act
        result = self.event.is_payment_created(payment_id)

        # assert
        self.assertTrue(result)
