from django.test import TestCase
from events.models import Event, EventDescription
from datetime import date
from django.utils import translation


class TestEventModel(TestCase):
    def setUp(self):
        event = Event.objects.create(start_date= date.today(), end_date= date.today(),
                                     priority=True, is_host_ntnui=True)
        EventDescription.objects.create(name='Norsk', description_text='Norsk beskrivelse', language='nb', event=event)
        EventDescription.objects.create(name='Engelsk', description_text='Engelsk beskrivelse', language='en', event=event)

    def test_event(self):
        translation.activate('nb')
        event = Event.objects.get(eventdescription__name='Norsk')
        self.assertEquals(event.name(), 'Norsk')

        translation.activate('en')
        event = Event.objects.get(eventdescription__name='Engelsk')
        self.assertEquals(event.name(), 'Engelsk')
