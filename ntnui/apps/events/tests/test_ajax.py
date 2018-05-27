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

        hs = MainBoard.objects.create(name="super geir", slug="super-geir")
        MainBoardMembership.objects.create(person=self.user, role="president", board=hs)

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

    def test_ajax_get_events(self):
        """Checks that the get_event url returners events"""
        request = self.client_signed_in.get(reverse('get_events'))
        self.assertEquals(request.status_code, 200)

    def test_ajax_get_event(self):
        """Checks that the server returns the given event"""
        request = self.client_signed_in.get(reverse('get_event',
                                                    kwargs={'event_id':'1'}))
        self.assertEquals(request.status_code, 200)

    def test_ajax_get_event_that_does_not_exits(self):
        """Chckecs that the server returns error if event dose not exists"""
        request = self.client_signed_in.get(reverse('get_event',
                                                    kwargs={'event_id':'154545'}))
        self.assertEquals(request.status_code, 400)

    def test_ajax_get_sub_event(self):
        """Checks that the server returns the given sub-event"""
        request = self.client_signed_in.get(reverse('get_sub_event',
                                                    kwargs={'sub_event_id':'1'}))
        self.assertEquals(request.status_code, 200)

    def test_ajax_get_sub_event_that_does_not_exits(self):
        """Checks that the server returns error if sub-event dose not exists"""
        request = self.client_signed_in.get(reverse('get_sub_event',
                                                    kwargs={'sub_event_id':'154545'}))
        self.assertEquals(request.status_code, 400)



