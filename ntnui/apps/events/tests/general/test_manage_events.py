from datetime import datetime, timedelta

import pytz
from accounts.models import User
from django.test import Client, TestCase
from django.urls import reverse
from events.models.category import Category, CategoryDescription
from events.models.event import Event, EventDescription
from events.models.sub_event import SubEventDescription, SubEvent
from groups.models import SportsGroup, Board


class TestManageEvents(TestCase):

    def setUp(self):
        # Create a user.
        self.user = User.objects.create_user(email='testuser@test.com', password='4epape?Huf+V')

        # Create an event.
        self.event = Event.objects.create(start_date=datetime.now(pytz.utc),
                                          end_date=datetime.now(pytz.utc) + timedelta(days=2))

        # Add norwegian and English name and description to the event.
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

        # Sets the swimming_group to the event's host.
        self.event.sports_groups.add(self.swimming_group)

        # Create a category for the event.
        self.category = Category.objects.create(event=self.event)
        CategoryDescription.objects.create(name="test", category=self.category, language='en')
        CategoryDescription.objects.create(name="test", category=self.category, language='nb')

        # Create a sub-event.
        self.sub_event = SubEvent.objects.create(start_date=datetime.now(pytz.utc),
                                                 end_date=datetime.now(pytz.utc) + timedelta(days=2),
                                                 category=self.category)

        # Add norwegian and English name and description to the sub-event.
        SubEventDescription.objects.create(name='name_nb', language='nb', sub_event=self.sub_event)
        SubEventDescription.objects.create(name='name_en', language='en', sub_event=self.sub_event)

        # Creates a client and logs into the website.
        self.c = Client()
        self.c.login(email='testuser@test.com', password='4epape?Huf+V')

    def test_create_category(self):
        """ Checks that creating a category works as intended. """

        # arrange
        response = self.c.post(reverse('create_category'), {'name_en': 'name_en', 'name_nb': 'name_nb',
                                                            'event': self.event.id})
        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 201)

        """ Test that it is not possible to create a category using GET. """

        # arrange
        response = self.c.get(reverse('create_category'), {'name_en': 'name_en', 'name_nb': 'name_nb',
                                                           'event': self.event.id})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 400)

    def test_edit_category(self):
        """ Checks that editing a category work as intended. """

        # arrange
        response = self.c.post(reverse('edit_category'), {'name_en': 'name_en',
                                                          'name_nb': 'name_nb',
                                                          'event': self.event.id,
                                                          'id': self.category.id})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 200)

        """ Test that it is not possible to edit a category using GET. """

        # arrange
        response = self.c.get(reverse('edit_category'), {'name_en': 'name_en',
                                                         'name_nb': 'name_nb',
                                                         'event': self.event.id,
                                                         'id': self.category.id})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 400)

    def test_delete_category(self):
        """ Checks that deleting a category work as intended. """

        # arrange
        response = self.c.post(reverse('delete_category'), {'name_en': 'name_en',
                                                            'name_nb': 'name_nb',
                                                            'event': self.event.id,
                                                            'id': self.category.id})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 200)

        """ Test that it is not possible to delete a category that does not exist. """

        # arrange
        response = self.c.post(reverse('edit_category'), {'name_en': 'name_en',
                                                          'name_nb': 'name_nb',
                                                          'event': self.event.id,
                                                          'id': 2323})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 400)

    def test_create_sub_event(self):
        """ Checks that creating a sub-event work as intended. """

        # arrange
        response = self.c.post(reverse('create_sub_event'), {'start_date': datetime.now(),
                                                             'end_date': datetime.now() + timedelta(days=2),
                                                             'name_en': 'name_en',
                                                             'name_nb': 'name_nb',
                                                             'description_text_en': 'description_en',
                                                             'description_text_nb': 'description_nb',
                                                             'event': self.event.id,
                                                             'category': self.category.id})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 201)

        """ Test without category id. """

        # arrange
        response = self.c.post(reverse('create_sub_event'), {'start_date': datetime.now(),
                                                             'end_date': datetime.now() + timedelta(days=2),
                                                             'name_en': 'name_en',
                                                             'name_nb': 'name_nb',
                                                             'description_text_en': 'description_en',
                                                             'description_text_nb': 'description_nb',
                                                             'event': self.event.id})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 201)

        """ Test without event id and category id. """

        # arrange
        response = self.c.post(reverse('create_sub_event'), {'start_date': datetime.now(),
                                                             'end_date': datetime.now() + timedelta(days=2),
                                                             'name_en': 'name_en',
                                                             'name_nb': 'name_nb',
                                                             'description_text_en': 'description_en',
                                                             'description_text_nb': 'description_nb',})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 400)

    def test_edit_sub_event(self):
        """ Checks that editing a sub-event work as intended. """
        response = self.c.post(reverse('edit_sub_event'), {'start_date': datetime.now(),
                                                           'end_date': datetime.now() + timedelta(days=2),
                                                           'name_en': 'name_en',
                                                           'name_nb': 'name_nb',
                                                           'description_text_en': 'description_en',
                                                           'description_text_nb': 'description_nb',
                                                           'category': self.category.id,
                                                           'id': self.sub_event.id})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 200)

    def test_edit_event(self):
        """ Edits the event with the given id. """

        # arrange
        response = self.c.post(reverse('ajax_edit_event'), {'start_date': datetime.now(),
                                                            'end_date': datetime.now() + timedelta(days=2),
                                                            'restriction': '0',
                                                            'hosted by NTNUI': 'true',
                                                            'name_en': 'name_en',
                                                            'name_nb': 'name_nb',
                                                            'description_text_en': 'description_en',
                                                            'description_text_nb': 'description_nb',
                                                            'host': 'NTNUI',
                                                            'place': 'Trondheim',
                                                            'cover_photo': 'cover_photo/ntnui-volleyball.png',
                                                            'id': self.event.id})

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 200)

    def test_delete_event_request(self):
        """ Tries to delete the event with the given id. """

        # arrange
        response = self.c.get(reverse('get_delete_event', kwargs={'event_id': self.event.id}))

        # act
        result = response.status_code

        # assert
        self.assertEqual(result, 200)
