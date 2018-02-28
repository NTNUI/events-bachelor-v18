from django.test import TestCase
from django.test import Client
from django.urls import reverse

from events.models import Event, EventDescription
from groups.models import SportsGroup
from datetime import date
from accounts.models import User

class TestLoadEvents(TestCase):

    def setUp(self):

        # Create dummy user
        User.objects.create(email='testuser@test.com', password='4epape?Huf+V')

        # Create a new event with NTNUI as host
        event = Event.objects.create(start_date= date.today(), end_date= date.today(),
                                     priority=True, is_host_ntnui=True)

        # add norwegian and english description to the name and the description
        EventDescription.objects.create(name='Norsk', description_text='Norsk beskrivelse', language='nb', event=event)
        EventDescription.objects.create(name='Engelsk', description_text='Engelsk beskrivelse', language='en', event=event)

    def test_loading_events(self):

        c = Client()

        # login
        c.login(email='testuser@test.com', password='4epape?Huf+V')

        request = c.get(reverse('get_events'), follow=True)
        self.assertEquals(request.status_code, 200)


