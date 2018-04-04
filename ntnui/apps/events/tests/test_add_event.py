from datetime import date

from accounts.models import User
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from events.models import Event, EventDescription
from groups.models import SportsGroup, Membership, Board

from events import create_event


class Event_add(TestCase):
    def setUp(self):
        # Create dummy user
        User.objects.create(email='testuser@test.com', password='4epape?Huf+V')

    def setUp(self):
        # Create dummy user
        User.objects.create_user(email='testuser@test.com', password='4epape?Huf+V')
        self.boardpresident = User.objects.create_user(email='boardpresident@test.com', password='12345',
                                                       customer_number='20')
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
        self.event = Event.objects.create(start_date=date.today(), end_date=date.today(),
                                          priority=True, is_host_ntnui=True)

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
                                                    'description_text_no': 'norsk beskrivelse',
                                                    'start_date': date.today(),
                                                    'end_date': date.today(),
                                                    'priority': 'false',
                                                    'host': 'NTNUI'
                                                    }, follow=True)

        return self.assertEqual(
            create_event.event_has_description_and_name(response.get('description_text_en'), response.get('name_en')),
            (False, 'Event must have description'))

    def test_create_event_with_unauthorized_user(self):
        c = Client()

        # login
        c.login(email='testuser@test.com', password='4epape?Huf+V')

        response = c.post(reverse('create_event'), {'start_date': date.today(),
                                                    'end_date': date.today(),
                                                    'place': '',
                                                    'restriction': '0',
                                                    'priority': 'false',
                                                    'hosted by NTNUI': 'true',
                                                    'name_en': 'engelsk navn',
                                                    'name_no': 'norsk navn',
                                                    'host': 'NTNUI',
                                                    'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': 'norsk beskrivelse',
                                                    }, follow=True)

        return self.assertEqual(
            response.status_code, 400)

    def test_create_event_hosted_by_boardmember(self):
        c = Client()
        c.login(email='boardpresident@test.com', password='12345')

        response = c.post(reverse('create_event'), {'start_date': date.today(),
                                                    'end_date': date.today(),
                                                    'place': '',
                                                    'restriction': '0',
                                                    'priority': 'false',
                                                    'hosted by NTNUI': 'false',
                                                    'name_en': 'engelsk navn',
                                                    'name_no': 'norsk navn',
                                                    'host': self.swimminggroup.id,
                                                    'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': 'norsk beskrivelse',
                                                    }, follow=True)

        return self.assertEqual(response.status_code, 201)

    def test_create_event_with_no_norwegian_description(self):
        c = Client()
        c.login(email='boardpresident@test.com', password='12345')

        response = c.post(reverse('create_event'), {'start_date': date.today(),
                                                    'end_date': date.today(),
                                                    'place': '',
                                                    'restriction': '0',
                                                    'priority': 'false',
                                                    'hosted by NTNUI': 'false',
                                                    'name_en': 'engelsk navn',
                                                    'name_no': 'norsk navn',
                                                    'host': self.swimminggroup.id,
                                                    'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': '',
                                                    }, follow=True)

        return self.assertEqual(response.status_code, 400)
