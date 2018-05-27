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
        # Create dummy user
        self.user = User.objects.create_user(email='testuser@test.com', password='4epape?Huf+V')
        self.boardpresident = User.objects.create_user(
            email='boardpresident@test.com', password='12345', customer_number='20')

        self.boardvice = User.objects.create_user(email='boardvice@test.com', password='23456', customer_number='21')
        self.boardcashier = User.objects.create_user(email='boardcashier@test.com', password='34567',
                                                     customer_number='22')

        # create sports group/main board
        self.swimminggroup = SportsGroup.objects.create(name='Swimming', slug='slug',
                                                        description='Swimming events and tournaments',
                                                        )
        self.swimmingboard = Board.objects.create(president=self.boardpresident, vice_president=self.boardvice,
                                                  cashier=self.boardcashier, sports_group=self.swimminggroup)
        self.swimminggroup.active_board = self.swimmingboard
        self.swimminggroup.save()

        # put user into mainboard
        self.boardpresident_swimminggroup = Membership.objects.create(person=self.boardpresident,
                                                                      group=self.swimminggroup)
        # Create a new event with NTNUI as host
        self.event = Event.objects.create(start_date=datetime.now(),
                                          end_date=datetime.now() + timedelta(days=2), is_host_ntnui=True)
        self.event2 = Event.objects.create(start_date=datetime.now(),
                                          end_date=datetime.now() + timedelta(days=2), is_host_ntnui=True)
        self.event2.user_attend(self.boardpresident, "", datetime.now(), "")
        self.event2.save()

        self.category = Category.objects.create(event=self.event)
        CategoryDescription.objects.create(name="test", category=self.category, language='en')
        CategoryDescription.objects.create(name="test", category=self.category, language='nb')

        # Create a new event with NTNUI as host
        self.sub_event = SubEvent.objects.create(start_date=datetime.now(pytz.utc),
                                            end_date=datetime.now(pytz.utc) + timedelta(days=2),
                                            category=self.category)

        # add norwegian and english description to the name and the description
        SubEventDescription.objects.create(name='Norsk', language='nb', sub_event=self.sub_event)
        SubEventDescription.objects.create(name='Engelsk', language='en',
                                           sub_event=self.sub_event)


        # add norwegian and english description to the name and the description
        EventDescription.objects.create(name='Norsk', description_text='Norsk beskrivelse', language='nb',
                                        event=self.event)
        EventDescription.objects.create(name='Engelsk', description_text='Engelsk beskrivelse', language='en',
                                        event=self.event)
        # add norwegian and english description to the name and the description
        EventDescription.objects.create(name='Norsk', description_text='Norsk beskrivelse', language='nb',
                                        event=self.event2)
        EventDescription.objects.create(name='Engelsk', description_text='Engelsk beskrivelse', language='en',
                                        event=self.event2)

        self.c = Client()

        # login
        self.c.login(email='testuser@test.com', password='4epape?Huf+V')


    def test_attend_event_and_unnatend(self):
        """Tests the ability to attend events"""

        #Sign up for event without sub-events
        response = self.c.post(reverse('attend_event'), {'event_id':self.event2.id,})
        self.assertEqual(201, response.status_code)

        #Sign up for the same event twice
        response = self.c.post(reverse('attend_event'), {'event_id':self.event2.id,})
        self.assertEqual(400, response.status_code)

        # Sgin up for event with sub-events
        response = self.c.post(reverse('attend_event'), {'event_id':self.event.id,})
        self.assertEqual(400, response.status_code)

        #Unnatend the event
        response = self.c.post(reverse('remove_attendance'), {'event_id':self.event2.id,})
        self.assertEqual(201, response.status_code)

    def test_attend_full_event(self):
        """Tests the ability to attend waiting list"""
        self.event2.attendance_cap = 1
        self.event2.save()
        response = self.c.post(reverse('waiting_list_event_request'), {'event_id':self.event2.id,})
        self.assertEqual(201, response.status_code)

    def test_attend_payed_event(self):
        """Checks that it is not possible to attend payed events withour paying"""
        self.event2.price = 122
        self.event2.save()
        response = self.c.post(reverse('attend_event'), {'event_id':self.event2.id,})
        self.assertEqual(400, response.status_code)


    def test_attend_event_guest(self):
        """Tests the ability to attend events as a guest"""

        c = Client()


        #Sign up as guest  for event without sub-events
        response = c.post(reverse('attend_event'), {'event_id':self.event2.id,
                                                    'email':'test@test.no',
                                                    'first_name':"frode",
                                                    'last_name': 'pettersen',
                                                    'phone': '234234233'})
        self.assertEqual(201, response.status_code)


    def test_attend_sub_event(self):
        """Tests the ability to attend sub_events"""

        # Sign up for sub_event
        response = self.c.post(reverse('attend_event'), {'sub_event_id': self.sub_event.id, })
        self.assertEqual(201, response.status_code)


