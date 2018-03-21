from django.test import TestCase
from events.models import Event, EventDescription
from accounts.models import User
from datetime import date
from django.test import Client

class Event_add(TestCase):

    def setUp(self):

        # Create dummy user
        User.objects.create(email='testuser@test.com', password='4epape?Huf+V')

        # Create a new event with NTNUI as host
        self.event = Event.objects.create(start_date= date.today(), end_date= date.today(),
                                     priority=True, is_host_ntnui=True)

        # add norwegian and english description to the name and the description
        EventDescription.objects.create(name='Norsk', description_text='Norsk beskrivelse', language='nb', event=self.event)
        EventDescription.objects.create(name='Engelsk', description_text='Engelsk beskrivelse', language='en', event=self.event)


    def test_verify_data_for_event(self):
        return self.assertEqual(self.event.start_date, date.today())
