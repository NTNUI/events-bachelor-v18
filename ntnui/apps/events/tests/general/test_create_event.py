from datetime import datetime, timedelta
import pytz
from accounts.models import User
from django.test import Client, TestCase
from django.urls import reverse
from events.models.event import (Event)
from groups.models import Board, SportsGroup
from hs.models import MainBoard, MainBoardMembership


class TestCreateEvent(TestCase):
    def setUp(self):
        # Create user.
        self.user = User.objects.create_user(email='testuser@test.com', password='4epape?Huf+V')

        # Create the users in the swimming group board.
        self.board_president = User.objects.create_user(email='boardpresident@test.com', password='12345',
                                                        customer_number='20')
        self.board_vice_president = User.objects.create_user(email='boardvice@test.com', password='23456',
                                                             customer_number='21')
        self.board_cashier = User.objects.create_user(email='boardcashier@test.com', password='34567',
                                                      customer_number='22')

        # Create the swimming group and its board.
        self.swimming_group = SportsGroup.objects.create(name='Swimming', slug='slug',
                                                         description='Swimming events and tournaments')
        self.swimming_board = Board.objects.create(president=self.board_president,
                                                   vice_president=self.board_vice_president,
                                                   cashier=self.board_cashier,
                                                   sports_group=self.swimming_group)
        self.swimming_group.active_board = self.swimming_board
        self.swimming_group.save()

        # Create a new event with NTNUI as host
        self.event = Event.objects.create(start_date=datetime.now(pytz.utc),
                                          end_date=datetime.now(pytz.utc) + timedelta(days=2), is_host_ntnui=True)

        self.description = 123

        self.c = Client()

    def test_create_event_with_no_description(self):
        """ Checks that it is not possible to create a event without description. """

        # arrange
        self.c.login(email='testuser@test.com', password='4epape?Huf+V')
        response = self.c.post(reverse('create_event'), {'name_en': 'name_en',
                                                         'name_no': 'name_no',
                                                         'description_text_en': '',
                                                         'place': 'Trondheim',
                                                         'description_text_no': 'description_no',
                                                         'start_date': datetime.now(),
                                                         'end_date': datetime.now() + timedelta(days=2),
                                                         'host': 'NTNUI'
                                                         }, follow=True)

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 400)

    def test_create_event_with_unauthorized_user(self):
        """ Checks that an unauthorized user can not create events. """

        # arrange
        self.c.login(email='boardpresident@test.com', password='12345')
        response = self.c.post(reverse('create_event'), {'start_date': datetime.now(),
                                                         'end_date': datetime.now() + timedelta(days=2),
                                                         'place': '',
                                                         'restriction': '0',
                                                         'hosted by NTNUI': 'true',
                                                         'name_en': 'name_en',
                                                         'name_no': 'name_no',
                                                         'host': 'NTNUI',
                                                         'place': 'Trondheim',
                                                         'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                         'description_text_en': 'description_en',
                                                         'description_text_no': 'description_no',
                                                         }, follow=True)
        # act
        result = response.status_code

        # assert
        return self.assertEqual(result, 400)

    def test_create_event_hosted_by_board_member(self):
        """ Checks that an even with valid input is created. """

        # arrange
        self.c.login(email='boardpresident@test.com', password='12345')
        response = self.c.post(reverse('create_event'), {'start_date': datetime.now(),
                                                         'end_date': datetime.now() + timedelta(days=2),
                                                         'restriction': '0',
                                                         'hosted by NTNUI': 'false',
                                                         'name_en': 'name_en',
                                                         'name_no': 'name_no',
                                                         'place': 'Trondheim',
                                                         'host': self.swimming_group.id,
                                                         'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                         'description_text_en': 'description_en',
                                                         'description_text_no': 'description_no',
                                                         }, follow=True)

        # act
        result = response.status_code

        # assert
        return self.assertEqual(result, 201)

    def test_create_event_with_no_norwegian_description(self):
        """ Checks that an event can not be created without a given description. """

        # arrange
        self.c.login(email='boardpresident@test.com', password='12345')
        response = self.c.post(reverse('create_event'), {'start_date': datetime.now(),
                                                         'end_date': datetime.now() + timedelta(days=2),
                                                         'restriction': '0',
                                                         'hosted by NTNUI': 'false',
                                                         'name_en': 'name_en',
                                                         'name_no': 'name_no',
                                                         'place': 'Trondheim',
                                                         'host': self.swimming_group.id,
                                                         'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                         'description_text_en': 'description_en',
                                                         'description_text_no': '',
                                                         }, follow=True)

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 400)

    def test_create_event_hosted_by_NTNUI(self):
        """ Checks that a main board member can create a new event. """

        # arrange
        main_board = MainBoard.objects.create(name="NTNUI", slug="NTNUI")
        MainBoardMembership.objects.create(person=self.user, role="president", board=main_board)
        self.c.login(email='testuser@test.com', password='4epape?Huf+V')
        response = self.c.post(reverse('create_event'), {'start_date': datetime.now(),
                                                         'end_date': datetime.now() + timedelta(days=2),
                                                         'restriction': '0',
                                                         'hosted by NTNUI': 'true',
                                                         'name_en': 'name_en',
                                                         'name_no': 'name_no',
                                                         'host': 'NTNUI',
                                                         'place': 'Trondheim',
                                                         'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                         'description_text_en': 'description_en',
                                                         'description_text_no': 'description_no',
                                                         }, follow=True)

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 201)

    def test_create_event_for_group_fails(self):
        """ Checks that a guest user is redirected, and thus can not create an event. """

        # arrange
        response = self.c.post(reverse('create_event'), {'start_date': datetime.now(),
                                                         'end_date': datetime.now() + timedelta(days=2),
                                                         'restriction': '0',
                                                         'hosted by NTNUI': 'true',
                                                         'name_en': 'name_en',
                                                         'name_no': 'name_no',
                                                         'host': 'NTNUI',
                                                         'place': 'Trondheim',
                                                         'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                         'description_text_en': 'description_en',
                                                         'description_text_no': 'description_no',
                                                         })

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 302)
