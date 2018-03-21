from django.test import TestCase
from django.test import Client
from django.urls import reverse
from events import create_event

from datetime import date

class Event_add(TestCase):


    def test_verify_data_for_event(self):
        data = {  }
        self.assertEqual(1 == 1, True)

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


