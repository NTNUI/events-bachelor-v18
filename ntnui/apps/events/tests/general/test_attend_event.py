from datetime import date, datetime, timedelta

import pytz
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from events.models.event import (Event, EventDescription,
                                 EventGuestRegistration, EventGuestWaitingList,
                                 EventRegistration, EventWaitingList)
from groups.models import Board, Membership, SportsGroup
from hs.models import MainBoard, MainBoardMembership

from events.models.category import Category, CategoryDescription
from events.models.sub_event import SubEventDescription, SubEvent


class TestAttendEvents(TestCase):
    def setUp(self):

        # Create a user.
        self.user = User.objects.create_user(email='testuser@test.com', password='4epape?Huf+V', customer_number='1')
        self.user_2 = User.objects.create_user(email='boardpresident@test.com', password='12345', customer_number='2')

        # Create two events.
        self.event = Event.objects.create(start_date=datetime.now(pytz.utc),
                                          end_date=datetime.now(pytz.utc) + timedelta(days=2), is_host_ntnui=True)
        self.event_2 = Event.objects.create(start_date=datetime.now(pytz.utc),
                                            end_date=datetime.now(pytz.utc) + timedelta(days=2), is_host_ntnui=True)

        # Create a sub-event.
        self.category = Category.objects.create(event=self.event)
        self.sub_event = SubEvent.objects.create(start_date=datetime.now(pytz.utc),
                                                 end_date=datetime.now(pytz.utc) + timedelta(days=2),
                                                 category=self.category)

        # Creates a client and logs into the website.
        self.c = Client()
        self.c.login(email='testuser@test.com', password='4epape?Huf+V')

    def test_attend_event_and_unnatend(self):
        """ Tests the ability to attend events. """

        # Sign up for event without sub-events.
        response = self.c.post(reverse('attend_event'), {'event_id': self.event_2.id})
        self.assertEqual(201, response.status_code)

        # Sign up for the same event twice should fail.
        response = self.c.post(reverse('attend_event'), {'event_id': self.event_2.id})
        self.assertEqual(400, response.status_code)

        # Sign up for event with sub-events should fail.
        response = self.c.post(reverse('attend_event'), {'event_id': self.event.id})
        self.assertEqual(400, response.status_code)

        # Sign off event.
        response = self.c.post(reverse('remove_attendance'), {'event_id': self.event_2.id})
        self.assertEqual(201, response.status_code)

    def test_attend_full_event(self):
        """ Tests the ability to attend waiting list, when the event is fully booked. """

        # arrange
        self.event_2.attendance_cap = 1
        self.event_2.save()
        self.event_2.user_attend(self.user_2, "", datetime.now(pytz.utc), "")
        response = self.c.post(reverse('waiting_list_event_request'), {'event_id': self.event_2.id})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 201)

    def test_attend_payed_event(self):
        """ Checks that it is not possible to attend payed events without paying. """

        # arrange
        self.event_2.price = 122
        self.event_2.save()
        response = self.c.post(reverse('attend_event'), {'event_id':self.event_2.id, })

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 400)

    def test_attend_event_guest(self):
        """ Tests the ability to attend events as a guest. """

        # arrange
        response = self.c.post(reverse('attend_event'), {'event_id': self.event_2.id,
                                                    'email': 'test@test.no',
                                                    'first_name': "Frode",
                                                    'last_name': 'Pettersen',
                                                    'phone': '234234233'})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 201)

    def test_attend_sub_event(self):
        """ Tests the ability to attend sub-events. """

        # arrange
        response = self.c.post(reverse('attend_event'), {'sub_event_id': self.sub_event.id})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 201)
