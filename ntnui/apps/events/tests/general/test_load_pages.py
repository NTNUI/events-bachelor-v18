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
from groups.models import Board, Membership, SportsGroup
from hs.models import MainBoard, MainBoardMembership


class TestLoadEvents(TestCase):
    """Used to check that the pages load, according to what kind of account is in use"""

    def setUp(self):
        """Set up database"""
        self.user = User.objects.create_user(email='testuser@test.com', password='4epape?Huf+V', customer_number=1)

        # Create a new event with NTNUI as host
        self.event = Event.objects.create(start_date=datetime.now(pytz.utc),
                                          end_date=datetime.now(pytz.utc) + timedelta(days=2),
                                          priority=True, is_host_ntnui=True)

        # add norwegian and english description to the name and the description
        EventDescription.objects.create(name='Norsk', description_text='Norsk beskrivelse', language='nb',
                                        event=self.event)
        EventDescription.objects.create(name='Engelsk', description_text='Engelsk beskrivelse', language='en',
                                        event=self.event)

        category = Category.objects.create(event=self.event)
        CategoryDescription.objects.create(name="test", category=category, language='en')
        CategoryDescription.objects.create(name="test", category=category, language='nb')

        # Create a new event with NTNUI as host
        sub_event = SubEvent.objects.create(start_date=datetime.now(pytz.utc),
                                            end_date=datetime.now(pytz.utc) + timedelta(days=2),
                                            category=category)

        # add norwegian and english description to the name and the description
        SubEventDescription.objects.create(name='Norsk', language='nb', sub_event=sub_event)
        SubEventDescription.objects.create(name='Engelsk', language='en',
                                           sub_event=sub_event)

        # create sports group/main board
        self.swimminggroup = SportsGroup.objects.create(name='Swimming', slug='slug',
                                                        description='Swimming events and tournaments',
                                                        )
        self.swimmingboard = Board.objects.create(president=self.user, vice_president=self.user,
                                                  cashier=self.user, sports_group=self.swimminggroup)
        self.swimminggroup.active_board = self.swimmingboard
        self.swimminggroup.save()

        # put user into mainboard
        Membership.objects.create(person=self.user, group=self.swimminggroup)

        # Create a second event with a group
        event = Event.objects.create(start_date=datetime.now(pytz.utc),
                                     end_date=datetime.now(pytz.utc) + timedelta(days=2),
                                     priority=True)
        # Add a sports group
        event.sports_groups.add(SportsGroup.objects.create(name='Test Group', description='this is a test group'))

        # add norwegian and english description to the name and the description
        EventDescription.objects.create(name='test norsk', description_text='test norsk', language='nb', event=event)
        EventDescription.objects.create(name='test engelsk', description_text='test engelsk', language='en',
                                        event=event)

        self.client_signed_in = Client()
        # login
        self.client_signed_in.login(email='testuser@test.com', password='4epape?Huf+V')

        self.client_anonymous = Client()

    def test_loading_main_event_page_user(self):
        """Checks that a logged in user can load the main event page"""
        request = self.client_signed_in.get(reverse('get_main_page'))
        self.assertEquals(request.status_code, 200)

    def test_loading_main_event_page_guest(self):
        """Checks that a guest can load the main event page"""
        request = self.client_anonymous.get(reverse('get_main_page'))
        self.assertEquals(request.status_code, 200)

    def test_loading_create_event_page_guest(self):
        """Tests that a guest can not create a new event"""
        request = self.client_anonymous.get(reverse('create_event_page'))
        self.assertEquals(request.status_code, 302)

    def test_loading_create_event_page_user(self):
        """Checks that a user may create a new event"""
        request = self.client_signed_in.get(reverse('create_event_page'))
        self.assertEquals(request.status_code, 200)

    def test_loading_edit_event_page(self):
        """Checks that a user may edit events"""
        request = self.client_signed_in.get(reverse('edit_event_page', kwargs={'event_id':self.event.id}))
        self.assertEquals(request.status_code, 200)

    def test_loading_edit_event_page_guest(self):
        """Checks that a guest may edit events"""
        request = self.client_anonymous.get(reverse('edit_event_page', kwargs={'event_id':self.event.id}))
        self.assertEquals(request.status_code, 302)

    def test_loading_remove_attendance_page_user(self):
        """Checks that a user can load the remove attendance page"""
        request = self.client_signed_in.get(reverse('remove_attendance',
                                                    kwargs={'token':'dc03e5b8-3a2b-4a38-8330-5a8401d7c19c'}))
        self.assertEquals(request.status_code, 200)

    def test_loading_remove_attendance_page_guest(self):
        """Checks that a guest can load the remove attendance page"""
        request = self.client_anonymous.get(reverse('remove_attendance',
                                                    kwargs={'token':'dc03e5b8-3a2b-4a38-8330-5a8401d7c19c'}))
        self.assertEquals(request.status_code, 200)

    def test_loading_attening_evnets_page_user(self):
        """Checks that a attending page loads as a user"""
        request = self.client_signed_in.get(reverse('attending_events_page'))
        self.assertEquals(request.status_code, 200)

    def test_loading_attening_evnets_page_guest(self):
        """Checks that the attending page does not load as a guest"""
        request = self.client_anonymous.get(reverse('attending_events_page'))
        self.assertIsNot(request.status_code, 200)

    def test_loading_event_attendees_page_user(self):
        """Checks that a user can load the page showing event attendees"""
        request = self.client_signed_in.get(reverse('event_attendees', kwargs={'event_id':self.event.id}))
        self.assertEquals(request.status_code, 200)

    def test_loading_event_attendees_page_guest(self):
        """Checks that a user can load the page showing event attendees"""
        request = self.client_anonymous.get(reverse('event_attendees', kwargs={'event_id':self.event.id}))
        self.assertEquals(request.status_code, 302)

    def test_loading_event_details_page_user(self):
        """Checks that the event details page loads for a user"""
        request = self.client_signed_in.get(reverse('event_details', kwargs={'event_id':self.event.id}))
        self.assertEquals(request.status_code, 200)

    def test_loading_event_details_page_guest(self):
        """Checks that the event details page loads for a guest"""
        request = self.client_anonymous.get(reverse('event_details', kwargs={'event_id':self.event.id}))
        self.assertEquals(request.status_code, 200)

