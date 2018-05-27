from datetime import date, datetime, timedelta

import pytz
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from events import create_event
from events.models.event import (Event, EventDescription,
                                 EventGuestRegistration, EventGuestWaitingList,
                                 EventRegistration, EventWaitingList)
from groups.models import Board, Membership, SportsGroup
from hs.models import MainBoard, MainBoardMembership


class CreateEvent(TestCase):

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

        self.description = 123

        # add norwegian and english description to the name and the description
        EventDescription.objects.create(name='Norsk', description_text='Norsk beskrivelse', language='nb',
                                        event=self.event)
        EventDescription.objects.create(name='Engelsk', description_text='Engelsk beskrivelse', language='en',
                                        event=self.event)

    def test_create_event_with_no_description(self):
        c = Client()

        # login
        c.login(email='testuser@test.com', password='4epape?Huf+V')

        response = c.post(reverse('create_event'), {'name_en': 'engelsk navn',
                                                    'name_no': 'norsk navn',
                                                    'description_text_en': '',
                                                    'place': 'Trondheim',
                                                    'description_text_no': 'norsk beskrivelse',
                                                    'start_date': datetime.now(),
                                                    'end_date': datetime.now() + timedelta(days=2),
                                                    'host': 'NTNUI'
                                                    }, follow=True)

        return self.assertEqual(
            create_event.event_has_description_and_name(response.get('description_text_en'), response.get('name_en')),
            (False, 'Event must have description'))

    def test_create_event_with_unauthorized_user(self):
        c = Client()

        # login
        c.login(email='testuser@test.com', password='4epape?Huf+V')

        response = c.post(reverse('create_event'), {'start_date': datetime.now(),
                                                    'end_date': datetime.now() + timedelta(days=2),
                                                    'place': '',
                                                    'restriction': '0',
                                                    'hosted by NTNUI': 'true',
                                                    'name_en': 'engelsk navn',
                                                    'name_no': 'norsk navn',
                                                    'host': 'NTNUI',
                                                    'place': 'Trondheim',
                                                    'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': 'norsk beskrivelse',
                                                    }, follow=True)

        return self.assertEqual(400, response.status_code)

    def test_create_event_hosted_by_boardmember(self):
        c = Client()
        c.login(email='boardpresident@test.com', password='12345')

        response = c.post(reverse('create_event'), {'start_date': datetime.now(),
                                                    'end_date': datetime.now() + timedelta(days=2),
                                                    'place': '',
                                                    'restriction': '0',
                                                    'hosted by NTNUI': 'false',
                                                    'name_en': 'engelsk navn',
                                                    'name_no': 'norsk navn',
                                                    'place': 'Trondheim',
                                                    'host': self.swimminggroup.id,
                                                    'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': 'norsk beskrivelse',
                                                    }, follow=True)

        return self.assertEqual(201, response.status_code)

    def test_create_event_with_no_norwegian_description(self):
        c = Client()
        c.login(email='boardpresident@test.com', password='12345')

        response = c.post(reverse('create_event'), {'start_date': datetime.now(),
                                                    'end_date': datetime.now() + timedelta(days=2),
                                                    'place': '',
                                                    'restriction': '0',
                                                    'hosted by NTNUI': 'false',
                                                    'name_en': 'engelsk navn',
                                                    'name_no': 'norsk navn',
                                                    'place': 'Trondheim',
                                                    'host': self.swimminggroup.id,
                                                    'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': '',
                                                    }, follow=True)

        return self.assertEqual(400, response.status_code)

    def test_create_event_hosted_by_NTNUI(self):
        hs = MainBoard.objects.create(name="super geir", slug="super-geir")
        MainBoardMembership.objects.create(person=self.user, role="president", board=hs)
        c = Client()
        c.login(email='testuser@test.com', password='4epape?Huf+V')

        response = c.post(reverse('create_event'), {'start_date': datetime.now(),
                                                    'end_date': datetime.now() + timedelta(days=2),
                                                    'place': '',
                                                    'restriction': '0',
                                                    'hosted by NTNUI': 'true',
                                                    'name_en': 'engelsk navn',
                                                    'name_no': 'norsk navn',
                                                    'host': 'NTNUI',
                                                    'place': 'Trondheim',
                                                    'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': 'norsk beskrivelse',
                                                    }, follow=True)
        print(response.content)
        return self.assertEqual(201, response.status_code)

    def test_create_event_for_group_fails(self):
        c = Client()
        response = c.post(reverse('create_event'), {'start_date': datetime.now(),
                                                    'end_date': datetime.now() + timedelta(days=2),
                                                    'place': '',
                                                    'restriction': '0',
                                                    'hosted by NTNUI': 'true',
                                                    'name_en': 'engelsk navn',
                                                    'name_no': 'norsk navn',
                                                    'host': 'NTNUI',
                                                    'place': 'Trondheim',
                                                    'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': 'norsk beskrivelse',
                                                    }, follow=True)

        return self.assertEqual(create_event.create_event_for_group(response.wsgi_request,
                                                                    response.get('hosted by NTNUI')), (False, None))
