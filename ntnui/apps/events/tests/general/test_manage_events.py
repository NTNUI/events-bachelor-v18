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


class TestManageEvents(TestCase):

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

        self.c = Client()

        # login
        self.c.login(email='testuser@test.com', password='4epape?Huf+V')


    def test_create_category(self):
        """Checks that creating a category work as intended"""
        response = self.c.post(reverse('create_category'), {'name_en': 'engelsk navn',
                                                    'name_nb': 'norsk navn',
                                                    'event': self.event.id
                                                    })
        self.assertEqual(201, response.status_code)

        response = self.c.get(reverse('create_category'), {'name_en': 'engelsk navn',
                                                    'name_nb': 'norsk navn',
                                                    'event': self.event.id,
                                                    })
        self.assertEqual(400, response.status_code)

    def test_edit_category(self):
        """Checks that editing a category work as intended"""
        response = self.c.post(reverse('edit_category'), {'name_en': 'navn',
                                                    'name_nb': 'navn',
                                                    'event': self.event.id,
                                                    'id': self.category.id,
                                                    })
        self.assertEqual(200, response.status_code)

        # test that it is not possible to edit using get
        response = self.c.get(reverse('edit_category'), {'name_en': 'navn',
                                                    'name_nb': 'navn',
                                                    'event': self.event.id,
                                                    'id': self.category.id,
                                                    })
        self.assertEqual(400, response.status_code)

    def test_delete_category(self):
        """Checks that deleting a category work as intended"""
        response = self.c.post(reverse('delete_category'), {'name_en': 'navn',
                                                    'name_nb': 'navn',
                                                    'event': self.event.id,
                                                    'id': self.category.id,
                                                    })
        self.assertEqual(200, response.status_code)

        # test that it is not possible to delete category that does not exist
        response = self.c.post(reverse('edit_category'), {'name_en': 'navn',
                                                    'name_nb': 'navn',
                                                    'event': self.event.id,
                                                    'id': 2323,
                                                    })
        self.assertEqual(400, response.status_code)

    def test_create_sub_event(self):
        """Checks that creating a sub-event work as intended"""
        response = self.c.post(reverse('create_sub_event'), {'start_date': datetime.now(),
                                                    'end_date': datetime.now() + timedelta(days=2),
                                                    'name_en': 'engelsk navn',
                                                    'name_nb': 'norsk navn',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': 'norsk beskrivelse',
                                                    'event': self.event.id,
                                                    'category': self.category.id
                                                    })
        self.assertEqual(201, response.status_code)

        # Test without category id
        response = self.c.post(reverse('create_sub_event'), {'start_date': datetime.now(),
                                                    'end_date': datetime.now() + timedelta(days=2),
                                                    'name_en': 'engelsk navn',
                                                    'name_nb': 'norsk navn',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': 'norsk beskrivelse',
                                                    'event': self.event.id,
                                                    })
        self.assertEqual(201, response.status_code)
        # Test without event id and category id
        response = self.c.post(reverse('create_sub_event'), {'start_date': datetime.now(),
                                                    'end_date': datetime.now() + timedelta(days=2),
                                                    'name_en': 'engelsk navn',
                                                    'name_nb': 'norsk navn',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': 'norsk beskrivelse',
                                                    })
        self.assertEqual(400, response.status_code)

    def test_edit_sub_event(self):
        """Checks that editing a sub-event work as intended"""
        response = self.c.post(reverse('edit_sub_event'), {'start_date': datetime.now(),
                                                    'end_date': datetime.now() + timedelta(days=2),
                                                    'name_en': ' navn',
                                                    'name_nb': ' navn',
                                                    'description_text_en': 'engelsk beskrivelse',
                                                    'description_text_no': 'norsk beskrivelse',
                                                    'category': self.category.id,
                                                    'id': self.sub_event.id,
                                                    })
        self.assertEqual(200, response.status_code)

    def test_edit_event(self):
        """Edits the event with the given id"""
        response = self.c.post(reverse('ajax_edit_event'), {'start_date': datetime.now(),
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
                                                    'id':self.event.id,
                                                    })

        self.assertEqual(200, response.status_code)

    def test_delete_event_request(self):
        """Tries to delete the event with the given id"""
        response = self.c.get(reverse('get_delete_event', kwargs={'event_id':self.event.id}))
        self.assertEqual(200, response.status_code)

