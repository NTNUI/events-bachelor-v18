from datetime import date

from django.test import TestCase
from django.utils import translation
from groups.models import SportsGroup

from events.models import Event, EventDescription


class TestEventModel(TestCase):
    def setUp(self):
        # Create a new event with NTNUI as host
        event = Event.objects.create(start_date=date.today(), end_date=date.today(),
                                     priority=True, is_host_ntnui=True)

        # add norwegian and english description to the name and the description
        EventDescription.objects.create(name='Norsk', description_text='Norsk beskrivelse', language='nb', event=event)
        EventDescription.objects.create(name='Engelsk', description_text='Engelsk beskrivelse', language='en',
                                        event=event)

        # Create a second event with a group
        event = Event.objects.create(start_date=date.today(), end_date=date.today(),
                                     priority=True)
        # Add a sports group
        event.sports_groups.add(SportsGroup.objects.create(name='Test Group', description='this is a test group'))

        # add norwegian and english description to the name and the description
        EventDescription.objects.create(name='test norsk', description_text='test norsk', language='nb', event=event)
        EventDescription.objects.create(name='test engelsk', description_text='test engelsk', language='en',
                                        event=event)

    """Tests the event.name(), event.description() and str functions"""

    def test_event_eventdescription_norwegian(self):
        lang = 'nb'
        # Active the current language
        translation.activate(lang)

        # get the event object with the name Norsk
        event = Event.objects.get(eventdescription__name='Norsk')

        # Checks that the name function returnes the name of the event in norwegian
        self.assertEquals(event.name(), 'Norsk')

        # Cheks that the str function works as attended
        self.assertEquals(str(event), 'Norsk')

        # Checks that the event have the right description in the write language.
        self.assertEquals(event.description(), 'Norsk beskrivelse')

    """Tests the event.name(), event.description() and str functions"""

    def test_event_eventdescription_english(self):
        lang = 'en'
        # Active the current language
        translation.activate(lang)

        # Finds the event with the name Engelsk, same event as over, but with translation
        event = Event.objects.get(eventdescription__name='Engelsk')

        # Checks that it returnes the right name in the right language
        self.assertEquals(event.name(), 'Engelsk')

        # Checks that the str function work as attended
        self.assertEquals(str(event), 'Engelsk')

        # Checks that the description is right
        self.assertEquals(event.description(), 'Engelsk beskrivelse')

    def test_event_groups(self):
        lang = 'nb'
        # Active the current language
        translation.activate(lang)

        # Tests that the given event is hosted by ntnui
        event = Event.objects.get(eventdescription__name='Norsk')
        self.assertEquals(event.get_host(), ['NTNUI'])

        # Checks that the right group is host for test event
        event = Event.objects.get(eventdescription__name='test norsk')
        self.assertEquals((event.get_host())[0], str(SportsGroup.objects.get(name='Test Group')))
