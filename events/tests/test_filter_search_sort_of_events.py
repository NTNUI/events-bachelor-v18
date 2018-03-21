from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils.encoding import force_text

from django.utils import translation

from events.models import Event, EventDescription
from groups.models import SportsGroup
from datetime import date
from accounts.models import User

class TestFilterSearchSortEvents(TestCase):

    def setUp(self):
        User.objects.create_user(email='testuser@test.com', password='4epape?Huf+V')

        # Create a new event with NTNUI as host
        event = Event.objects.create(start_date=date.today(), end_date=date.today(),
                                     priority=True, is_host_ntnui=True)
        # Create a second event with NTNUI as host
        event2 = Event.objects.create(start_date=date.today(), end_date=date.today(),
        priority=True, is_host_ntnui=True)

        # Create a third event with NTNUI as host
        event3 = Event.objects.create(start_date=date.today(), end_date=date.today(),
        priority=True, is_host_ntnui=True)

        # Create a new event where NTNUI is not host
        event4 = Event.objects.create(start_date=date.today(), end_date=date.today(),
        priority=True)

        # Add a sports group
        event4.sports_groups.add(SportsGroup.objects.create(name='Test Group', description='this is a test group'))

        # Add a sports group
        event.sports_groups.add(SportsGroup.objects.create(name='Test Group', description='this is a test group'))

        # add norwegian and english description to the name and the description for the first event
        EventDescription.objects.create(name='Søppelplukking', description_text='Her plukker vi søppel.', language='nb', event=event)
        EventDescription.objects.create(name='Trash collection', description_text='Come and pick up trash with us.', language='en',
                                        event=event)

        # add norwegian and english description to the name and the description for the second event
        EventDescription.objects.create(name='Teater', description_text='Vi vil prøvespille til vårt teaterlag.', language='nb', event=event2)
        EventDescription.objects.create(name='Theatre', description_text='We are gathering you for test play to our theatre.', language='en',
                                        event=event2)

        # add norwegian and english description to the name and the description for the third event
        EventDescription.objects.create(name='Rockeringturnering', description_text='Her vil vi kåre årets rokkeringperson.', language='nb', event=event3)
        EventDescription.objects.create(name='Rock ring tournament', description_text='We will see who is best at rocking the rock ring.', language='en',
                                        event=event3)

        # add norwegian and english description to the name and the description for the fourth event
        EventDescription.objects.create(name='Campingtur i skogen', description_text='Vi vil gjerne ta deg med på campingtur i skogen.', language='nb', event=event4)
        EventDescription.objects.create(name='Camping in the woods', description_text='We will take you camping in the deep woods of Norway.', language='en',
                                        event=event4)


    def test_searching(self):
        c = Client()
        c.login(email='testuser@test.com', password='4epape?Huf+V')
        response = c.get(reverse('get_events'))
        translation.activate('en')
        self.maxDiff = None
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'events': [{'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'Come and pick up trash with us.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 1,
              'name': 'Trash collection',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We are gathering you for test play to our '
                             'theatre.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 2,
              'name': 'Theatre',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We will see who is best at rocking the rock ring.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 3,
              'name': 'Rock ring tournament',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We will take you camping in the deep woods of '
                             'Norway.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['Test Group'],
              'id': 4,
              'name': 'Camping in the woods',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'}],
          'page_count': 1,
          'page_number': 1})

        search_response = c.get(reverse('get_events'), {'search': 'Rock'})
        self.assertJSONEqual(search_response.content, {'events': [{'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We will see who is best at rocking the rock ring.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 3,
              'name': 'Rock ring tournament',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'}],
          'page_count': 1,
          'page_number': 1})


        #get events
        #search for given events
        #check if correct response

    def test_filtering(self):
        c = Client()
        c.login(email='testuser@test.com', password='4epape?Huf+V')
        response = c.get(reverse('get_events'))
        translation.activate('en')
        self.maxDiff = None
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'events': [{'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'Come and pick up trash with us.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 1,
              'name': 'Trash collection',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We are gathering you for test play to our '
                             'theatre.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 2,
              'name': 'Theatre',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We will see who is best at rocking the rock ring.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 3,
              'name': 'Rock ring tournament',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We will take you camping in the deep woods of '
                             'Norway.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['Test Group'],
              'id': 4,
              'name': 'Camping in the woods',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'}],
          'page_count': 1,
          'page_number': 1})

        filter_response = c.get(reverse('get_events'), {'filter-host': 'NTNUI'})
        self.assertJSONEqual(filter_response.content, {'events': [{'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'Come and pick up trash with us.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 1,
              'name': 'Trash collection',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We are gathering you for test play to our '
                             'theatre.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 2,
              'name': 'Theatre',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We will see who is best at rocking the rock ring.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 3,
              'name': 'Rock ring tournament',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'}],
          'page_count': 1,
          'page_number': 1})

    def test_sorting(self):
        c = Client()
        c.login(email='testuser@test.com', password='4epape?Huf+V')
        response = c.get(reverse('get_events'))
        translation.activate('en')
        self.maxDiff = None
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'events': [{'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'Come and pick up trash with us.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 1,
              'name': 'Trash collection',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We are gathering you for test play to our '
                             'theatre.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 2,
              'name': 'Theatre',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We will see who is best at rocking the rock ring.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 3,
              'name': 'Rock ring tournament',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We will take you camping in the deep woods of '
                             'Norway.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['Test Group'],
              'id': 4,
              'name': 'Camping in the woods',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'}],
          'page_count': 1,
          'page_number': 1})

        sorting_response = c.get(reverse('get_events'), {'sort-by': 'name'})
        self.assertJSONEqual(sorting_response.content, {'events': [{'cover_photo': 'cover_photo/ntnui-volleyball.png',
         'description': 'We will take you camping in the deep woods of '
                        'Norway.',
         'end_date': '2018-03-21T00:00:00Z',
         'host': ['Test Group'],
         'id': 4,
         'name': 'Camping in the woods',
         'place': '',
         'priority': True,
         'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We will see who is best at rocking the rock ring.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 3,
              'name': 'Rock ring tournament',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
              'description': 'We are gathering you for test play to our '
                             'theatre.',
              'end_date': '2018-03-21T00:00:00Z',
              'host': ['NTNUI'],
              'id': 2,
              'name': 'Theatre',
              'place': '',
              'priority': True,
              'start_date': '2018-03-21T00:00:00Z'},
             {'cover_photo': 'cover_photo/ntnui-volleyball.png',
                'description': 'Come and pick up trash with us.',
                'end_date': '2018-03-21T00:00:00Z',
                'host': ['NTNUI'],
                'id': 1,
                'name': 'Trash collection',
                'place': '',
                'priority': True,
                'start_date': '2018-03-21T00:00:00Z'}],
          'page_count': 1,
          'page_number': 1})
