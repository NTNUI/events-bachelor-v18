from datetime import datetime

import pytz
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from events.models.event import (Event, EventDescription,
                                 EventGuestRegistration, EventGuestWaitingList,
                                 EventRegistration, EventWaitingList)
from groups.models import SportsGroup
import ntnui.settings.common as common

from django.utils import translation
from unittest.mock import Mock

class TestFilterSearchSortEvents(TestCase):
    def setUp(self):

        self.date = datetime.now(pytz.utc)
        # Format code to match format from json
        self.date_string = self.date.isoformat()[0:-9] +"Z"

        User.objects.create_user(email='testuser@test.com', password='4epape?Huf+V')

        # Create a new event with NTNUI as host
        event = Event.objects.create(start_date=self.date, end_date=self.date,
                                     priority=True, is_host_ntnui=True)
        # Create a second event with NTNUI as host
        event2 = Event.objects.create(start_date=self.date, end_date=self.date,
                                      priority=True, is_host_ntnui=True)

        # Create a third event with NTNUI as host
        event3 = Event.objects.create(start_date=self.date, end_date=self.date,
                                      priority=True, is_host_ntnui=True)

        # Create a new event where NTNUI is not host
        event4 = Event.objects.create(start_date=self.date, end_date=self.date,
                                      priority=True)

        # Add a sports group
        event4.sports_groups.add(SportsGroup.objects.create(name='Test Group', description='this is a test group'))

        # Add a sports group
        event.sports_groups.add(SportsGroup.objects.create(name='Test Group', description='this is a test group'))

        # add norwegian and english description to the name and the description for the first event
        EventDescription.objects.create(name='Søppelplukking', description_text='Her plukker vi søppel.', language='nb',
                                        event=event)
        EventDescription.objects.create(name='Trash collection', description_text='Come and pick up trash with us.',
                                        language='en',
                                        event=event)

        # add norwegian and english description to the name and the description for the second event
        EventDescription.objects.create(name='Teater', description_text='Vi vil prøvespille til vårt teaterlag.',
                                        language='nb', event=event2)
        EventDescription.objects.create(name='Theatre',
                                        description_text='We are gathering you for test play to our theatre.',
                                        language='en',
                                        event=event2)

        # add norwegian and english description to the name and the description for the third event
        EventDescription.objects.create(name='Rockeringturnering',
                                        description_text='Her vil vi kåre årets rokkeringperson.', language='nb',
                                        event=event3)
        EventDescription.objects.create(name='Rock ring tournament',
                                        description_text='We will see who is best at rocking the rock ring.',
                                        language='en',
                                        event=event3)

        # add norwegian and english description to the name and the description for the fourth event
        EventDescription.objects.create(name='Campingtur i skogen',
                                        description_text='Vi vil gjerne ta deg med på campingtur i skogen.',
                                        language='nb', event=event4)
        EventDescription.objects.create(name='Camping in the woods',
                                        description_text='We will take you camping in the deep woods of Norway.',
                                        language='en',
                                        event=event4)

        # Show more text (for debugging)
        self.maxDiff = None


        # Login client
        self.c = Client()
        self.c.login(email='testuser@test.com', password='4epape?Huf+V')
        translation.get_language = Mock(return_value='en')

        # Trash collection event JSON
        self.trash_collection = {'cover_photo': 'cover_photo/events/ntnui-volleyball.png',
                                 'description': 'Come and pick up trash with us.',
                                 'end_date': self.date_string,
                                 'host': ['NTNUI'],
                                 'id': 1,
                                 'price':0,
                                 'name': 'Trash collection',
                                 'place': '',
                                 'priority': True,
                                 'start_date': self.date_string}

        # Theatre event JSON
        self.theatre = {'cover_photo': 'cover_photo/events/ntnui-volleyball.png',
                        'description': 'We are gathering you for test play to our '
                                       'theatre.',
                        'end_date': self.date_string,
                        'host': ['NTNUI'],
                        'id': 2,
                        'price': 0,
                        'name': 'Theatre',
                        'place': '',
                        'priority': True,
                        'start_date': self.date_string}

        # Rock ring tournament event JSON
        self.rock_ring_tournament = {'cover_photo': 'cover_photo/events/ntnui-volleyball.png',
                                     'description': 'We will see who is best at rocking the rock ring.',
                                     'end_date': self.date_string,
                                     'host': ['NTNUI'],
                                     'id': 3,
                                     'price': 0,
                                     'name': 'Rock ring tournament',
                                     'place': '',
                                     'priority': True,
                                     'start_date': self.date_string}

        # Camping in the woods event JSON
        self.camping_in_the_woods = {'cover_photo': 'cover_photo/events/ntnui-volleyball.png',
                                     'description': 'We will take you camping in the deep woods of '
                                                    'Norway.',
                                     'end_date': self.date_string,
                                     'host': ['Test Group'],
                                     'id': 4,
                                     'price': 0,
                                     'name': 'Camping in the woods',
                                     'place': '',
                                     'priority': True,
                                     'start_date': self.date_string}

    def test_get_default_english_content(self):
        # Response for the default page
        response = self.c.get(reverse('get_events'))

        self.assertEqual(response.status_code, 200)

        # Check the default response
        self.assertJSONEqual(response.content, {'events': [self.trash_collection,
                                                           self.theatre,
                                                           self.rock_ring_tournament,
                                                           self.camping_in_the_woods],
                                                'page_count': 1,
                                                'page_number': 1})

    def test_get_default_norwegian_content(self):
        # Response for the default page
        translation.get_language = Mock(return_value='nb')
        response = self.c.get(reverse('get_events'), HTTP_ACCEPT_LANGUAGE='nb')
        translation.get_language = Mock(return_value='en')

        # Check the default norwegian response
        self.assertJSONEqual(response.content, {'events': [{'cover_photo': 'cover_photo/events/ntnui-volleyball.png',
                                                            'description': 'Her plukker vi søppel.',
                                                            'end_date': self.date_string,
                                                            'host': ['NTNUI'],
                                                            'id': 1,
                                                            'price': 0,
                                                            'name': 'Søppelplukking',
                                                            'place': '',
                                                            'priority': True,
                                                            'start_date': self.date_string},
                                                           {'cover_photo': 'cover_photo/events/ntnui-volleyball.png',
                                                            'description': 'Vi vil prøvespille til vårt teaterlag.',
                                                            'end_date': self.date_string,
                                                            'host': ['NTNUI'],
                                                            'id': 2,
                                                            'price': 0,
                                                            'name': 'Teater',
                                                            'place': '',
                                                            'priority': True,
                                                            'start_date': self.date_string},
                                                           {'cover_photo': 'cover_photo/events/ntnui-volleyball.png',
                                                            'description': 'Her vil vi kåre årets rokkeringperson.',
                                                            'end_date': self.date_string,
                                                            'host': ['NTNUI'],
                                                            'id': 3,
                                                            'price': 0,
                                                            'name': 'Rockeringturnering',
                                                            'place': '',
                                                            'priority': True,
                                                            'start_date': self.date_string},
                                                           {'cover_photo': 'cover_photo/events/ntnui-volleyball.png',
                                                            'description': 'Vi vil gjerne ta deg med på campingtur i skogen.',
                                                            'end_date': self.date_string,
                                                            'host': ['Test Group'],
                                                            'id': 4,
                                                            'price': 0,
                                                            'name': 'Campingtur i skogen',
                                                            'place': '',
                                                            'priority': True,
                                                            'start_date': self.date_string}],
                                                'page_count': 1,
                                                'page_number': 1})

    def test_search_content(self):
        # Results for search on 'Rock'
        search_response = self.c.get(reverse('get_events'), {'search': 'Rock'})
        self.assertJSONEqual(search_response.content, {'events': [self.rock_ring_tournament],
                                                       'page_count': 1,
                                                       'page_number': 1})

    def test_search_content_does_not_exist(self):
        # Results for search on 'ferry', empty array is expected
        response = self.c.get(reverse('get_events'), {'search': 'ferry'})
        self.assertJSONEqual(response.content, {'events': [],
                                                'page_count': 1,
                                                'page_number': 1})

    def test_search_no_content(self):
        # Results for search on nothing
        search_response = self.c.get(reverse('get_events'), {'search': ''})
        self.assertJSONEqual(search_response.content, {'events': [self.trash_collection,
                                                                  self.theatre,
                                                                  self.rock_ring_tournament,
                                                                  self.camping_in_the_woods],
                                                       'page_count': 1,
                                                       'page_number': 1})

    def test_filtering_NTNUI(self):
        # Check the filtered content for NTNUI events
        response = self.c.get(reverse('get_events'), {'filter-host': 'NTNUI'})
        self.assertJSONEqual(response.content, {'events': [self.trash_collection,
                                                           self.theatre,
                                                           self.rock_ring_tournament],
                                                'page_count': 1,
                                                'page_number': 1})

    def test_filtering_two_parameters(self):
        # Check the filtered content for NTNUI and 'Test group' (id='1') events
        response = self.c.get(reverse('get_events'), {'filter-host': 'NTNUI-1'})
        self.assertJSONEqual(response.content, {'events': [self.trash_collection,
                                                           self.theatre,
                                                           self.rock_ring_tournament,
                                                           self.camping_in_the_woods],
                                                'page_count': 1,
                                                'page_number': 1})

    def test_filtering_group(self):
        # Check the filtered content for 'Test group' (id='1') events
        response = self.c.get(reverse('get_events'), {'filter-host': '1'})
        self.assertJSONEqual(response.content, {'events': [self.camping_in_the_woods],
                                                'page_count': 1,
                                                'page_number': 1})

    def test_filtering_no_content(self):
        # Check the filtered content for 'Test group' (id='1') events
        response = self.c.get(reverse('get_events'), {'filter-host': ''})
        self.assertJSONEqual(response.content, {'events': [self.trash_collection,
                                                           self.theatre,
                                                           self.rock_ring_tournament,
                                                           self.camping_in_the_woods],
                                                'page_count': 1,
                                                'page_number': 1})

    def test_sorting_ascending_name(self):
        # Check response for filtered by name (ascending) content
        response = self.c.get(reverse('get_events'), {'sort-by': 'name'})
        self.assertJSONEqual(response.content, {'events': [self.camping_in_the_woods,
                                                           self.rock_ring_tournament,
                                                           self.theatre,
                                                           self.trash_collection],
                                                'page_count': 1,
                                                'page_number': 1})

    def test_sorting_ascending_name(self):
        # Check response for filtered by name (ascending) content
        response = self.c.get(reverse('get_events'), {'sort-by': 'description'})
        self.assertJSONEqual(response.content, {'events': [self.trash_collection,
                                                           self.theatre,
                                                           self.rock_ring_tournament,
                                                           self.camping_in_the_woods],

                                                'page_count': 1,
                                                'page_number': 1})

    def test_sorting_descending_name(self):
        # Check response for filtered by name (descending) content
        response = self.c.get(reverse('get_events'), {'sort-by': '-name'})
        self.assertJSONEqual(response.content, {'events': [self.trash_collection,
                                                           self.theatre,
                                                           self.rock_ring_tournament,
                                                           self.camping_in_the_woods],
                                                'page_count': 1,
                                                'page_number': 1})

    def test_sorting_random(self):
        response = self.c.get(reverse('get_events'), {'sort-by': 'dsf'})

        self.assertEqual(response.status_code, 200)

        # Check the default response
        self.assertJSONEqual(response.content, {'events': [self.trash_collection,
                                                           self.theatre,
                                                           self.rock_ring_tournament,
                                                           self.camping_in_the_woods],
                                                'page_count': 1,
                                                'page_number': 1})

    def test_sorting_no_input(self):
        response = self.c.get(reverse('get_events'), {'sort-by': ''})

        self.assertEqual(response.status_code, 200)

        # Check the default response
        self.assertJSONEqual(response.content, {'events': [self.trash_collection,
                                                           self.theatre,
                                                           self.rock_ring_tournament,
                                                           self.camping_in_the_woods],
                                                'page_count': 1,
                                                'page_number': 1})

    def test_loading_events_post(self):
        response = self.c.post(reverse('get_events'))
        self.assertEquals(404, response.status_code)
