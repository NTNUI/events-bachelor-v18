from django.test import TestCase
from events.views import create_event_for_group

class Event_add(TestCase):

'''Example test'''
    def test_verify_data_for_event(self):
        """ Verify data """
        data = {  }
        self.assertEqual(1 == 1, True)
