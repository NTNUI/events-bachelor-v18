from datetime import datetime, timedelta

import pytz
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from events.models.category import Category, CategoryDescription
from events.models.event import (Event, EventDescription,
                                 EventGuestRegistration, EventGuestWaitingList,
                                 EventRegistration, EventWaitingList)
from events.models.sub_event import (SubEvent, SubEventDescription,
                                     SubEventGuestRegistration,
                                     SubEventGuestWaitingList,
                                     SubEventRegistration, SubEventWaitingList)


class TestAjax(TestCase):
    """Used to check that the pages load, according to what kind of account is in use"""
    def setUp(self):

        # Create a user.
        self.user = User.objects.create_user(email='testuser@test.com', password='4epape?Huf+V', customer_number=1)

        # Create an event.
        self.event = Event.objects.create(start_date=datetime.now(pytz.utc),
                                          end_date=datetime.now(pytz.utc) + timedelta(days=2),
                                          priority=True, is_host_ntnui=True)

        # Create a sub-event.
        self.category = Category.objects.create(event=self.event)
        self.sub_event = SubEvent.objects.create(start_date=datetime.now(pytz.utc),
                                                 end_date=datetime.now(pytz.utc) + timedelta(days=2),
                                                 category=self.category)
        print(self.event.id)
        # Creates a client and logs into the website.
        self.client_signed_in = Client()
        self.client_signed_in.login(email='testuser@test.com', password='4epape?Huf+V')

    def test_ajax_get_event(self):
        """ Checks that the server returns the given event. """

        # arrange
        request = self.client_signed_in.get(reverse('get_event', kwargs={'event_id': '1'}))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_ajax_get_events(self):
        """ Checks that the get_event url returns all events. """

        # arrange
        request = self.client_signed_in.get(reverse('get_events'))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_ajax_get_event_that_does_not_exits(self):
        """ Checks that the server returns error if the event dose not exist. """

        # arrange
        request = self.client_signed_in.get(reverse('get_event', kwargs={'event_id': '154545'}))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 400)

    def test_ajax_get_sub_event(self):
        """ Checks that the server returns the given sub-event. """

        # arrange
        request = self.client_signed_in.get(reverse('get_sub_event', kwargs={'sub_event_id': '1'}))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_ajax_get_sub_event_that_does_not_exits(self):
        """ Checks that the server returns error if the sub-event does not exist. """

        # arrange
        request = self.client_signed_in.get(reverse('get_sub_event', kwargs={'sub_event_id': '154545'}))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 400)
