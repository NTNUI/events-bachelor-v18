from datetime import datetime, timedelta

import pytz
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from events.models.event import (Event, EventDescription,
                                 EventGuestRegistration, EventGuestWaitingList,
                                 EventRegistration, EventWaitingList)
from groups.models import Board, SportsGroup


"""Used to check that the pages load, according to what kind of account is in use"""


class TestLoadEvents(TestCase):
    def setUp(self):

        # Create user.
        self.user = User.objects.create_user(email='testuser@test.com', password='4epape?Huf+V', customer_number=1)

        # Create an event.
        self.event = Event.objects.create(start_date=datetime.now(pytz.utc),
                                          end_date=datetime.now(pytz.utc) + timedelta(days=2),
                                          priority=True, is_host_ntnui=True)

        # Add Norwegian and English name and description to the event.
        EventDescription.objects.create(name='name_nb', description_text='description_nb', language='nb',
                                        event=self.event)
        EventDescription.objects.create(name='name_en', description_text='description_en', language='en',
                                        event=self.event)

        # Create a sports group and add the user to its board.
        self.swimming_group = SportsGroup.objects.create(name='Swimming', slug='slug',
                                                         description='Swimming events and tournaments')
        self.swimming_board = Board.objects.create(president=self.user, vice_president=self.user,
                                                   cashier=self.user, sports_group=self.swimming_group)
        self.swimming_group.active_board = self.swimming_board
        self.swimming_group.save()

        # Creates a client and logs into the website.
        self.client_signed_in = Client()
        self.client_signed_in.login(email='testuser@test.com', password='4epape?Huf+V')

        # Creates a client without logging into the website.
        self.client_anonymous = Client()

    def test_loading_main_event_page_user(self):
        """ Checks that a logged in user can load the main event page. """

        # arrange
        request = self.client_signed_in.get(reverse('get_main_page'))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_loading_main_event_page_guest(self):
        """ Checks that a guest can load the main event page. """

        # arrange
        request = self.client_anonymous.get(reverse('get_main_page'))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_loading_create_event_page_guest(self):
        """ Tests that a guest can not create a new event."""

        # arrange
        request = self.client_anonymous.get(reverse('create_event_page'))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 302)

    def test_loading_create_event_page_user(self):
        """ Checks that a user may create a new event. """

        # arrange
        request = self.client_signed_in.get(reverse('create_event_page'))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_loading_edit_event_page(self):
        """ Checks that a user may edit events. """
        request = self.client_signed_in.get(reverse('edit_event_page', kwargs={'event_id': self.event.id}))
        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_loading_edit_event_page_guest(self):
        """ Checks that a guest may edit events. """

        # arrange
        request = self.client_anonymous.get(reverse('edit_event_page', kwargs={'event_id': self.event.id}))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 302)

    def test_loading_remove_attendance_page_user(self):
        """ Checks that a user can load the remove attendance page. """

        # arrange
        request = self.client_signed_in.get(reverse('remove_attendance',
                                                    kwargs={'token': 'dc03e5b8-3a2b-4a38-8330-5a8401d7c19c'}))
        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_loading_remove_attendance_page_guest(self):
        """ Checks that a guest can load the remove attendance page. """

        # arrange
        request = self.client_anonymous.get(reverse('remove_attendance',
                                                    kwargs={'token': 'dc03e5b8-3a2b-4a38-8330-5a8401d7c19c'}))
        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_loading_attending_events_page_user(self):
        """ Checks that a attending page loads as a user. """
        request = self.client_signed_in.get(reverse('attending_events_page'))
        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_loading_attending_events_page_guest(self):
        """ Checks that the attending page does not load as a guest. """
        request = self.client_anonymous.get(reverse('attending_events_page'))
        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 302)

    def test_loading_event_attendees_page_user(self):
        """ Checks that a user can load the page showing event attendees. """

        # arrange
        request = self.client_signed_in.get(reverse('event_attendees', kwargs={'event_id': self.event.id}))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_loading_event_attendees_page_guest(self):
        """ Checks that a user can load the page showing event attendees. """

        # arrange
        request = self.client_anonymous.get(reverse('event_attendees', kwargs={'event_id': self.event.id}))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 302)

    def test_loading_event_details_page_user(self):
        """Checks that the event details page loads for a user"""
        request = self.client_signed_in.get(reverse('event_details', kwargs={'event_id': self.event.id}))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)

    def test_loading_event_details_page_guest(self):
        """ Checks that the event details page loads for a guest. """

        # arrange
        request = self.client_anonymous.get(reverse('event_details', kwargs={'event_id': self.event.id}))

        # act
        result = request.status_code

        # assert
        self.assertEquals(result, 200)
