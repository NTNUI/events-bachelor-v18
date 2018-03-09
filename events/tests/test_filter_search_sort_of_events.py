from django.test import TestCase
from django.test import Client
from django.urls import reverse

from events.models import Event, EventDescription
from groups.models import SportsGroup
from datetime import date
from accounts.models import User

class TestFilterSearchSortEvents(TestCase):

    def setUp(self):
        User.objects.create(email='testuser@test.com', password='4epape?Huf+V')

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
        response = c.get(reverse('list_groups'), follow = True)
        self.assertEqual(response.status_code, 200)
        #get events
        #search for given events
        #check if correct response

    def test_filtering(self):
        c = Client()
        # login
        c.login(email='testuser@test.com', password='4epape?Huf+V')