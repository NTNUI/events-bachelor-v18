from datetime import date

from accounts.models import User
from django.test import TestCase
from events.models import Event, EventDescription, CategoryDescription, Category, SubEvent, SubEventDescription
from groups.models import SportsGroup, Board, Membership
from hs.models import MainBoard, MainBoardMembership

from events import views


class TestViewMethods(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@test.com', password='4epape?Huf+V', customer_number=1)
        self.user2 = User.objects.create_user(email='testuser1@test.com', password='4epape?Huf+V')
        # Create a new event with NTNUI as host
        self.event = Event.objects.create(start_date=date.today(), end_date=date.today(),
                                          priority=True, is_host_ntnui=True)

        # add norwegian and english description to the name and the description
        EventDescription.objects.create(name='Norsk', description_text='Norsk beskrivelse', language='nb',
                                        event=self.event)
        EventDescription.objects.create(name='Engelsk', description_text='Engelsk beskrivelse', language='en',
                                        event=self.event)

        category = Category.objects.create(event=self.event)
        CategoryDescription.objects.create(name="test", category=category, language='en')
        CategoryDescription.objects.create(name="test", category=category, language='nb')

        # Create a new event with NTNUI as host
        sub_event = SubEvent.objects.create(start_date=date.today(), end_date=date.today(), category=category)

        # add norwegian and english description to the name and the description
        SubEventDescription.objects.create(name='Norsk', language='nb', sub_event=sub_event)
        SubEventDescription.objects.create(name='Engelsk', language='en',
                                           sub_event=sub_event)

        # create sports group/main board
        self.swimminggroup = SportsGroup.objects.create(name='Swimming', slug='slug',
                                                        description='Swimming events and tournaments',
                                                        )
        self.swimmingboard = Board.objects.create(president=self.user, vice_president=self.user,
                                                  cashier=self.user, sports_group=self.swimminggroup)
        self.swimminggroup.active_board = self.swimmingboard
        self.swimminggroup.save()

        # put user into mainboard
        Membership.objects.create(person=self.user, group=self.swimminggroup)

        hs = MainBoard.objects.create(name="super geir", slug="super-geir")
        MainBoardMembership.objects.create(person=self.user, role="president", board=hs)

        # Create a second event with a group
        event = Event.objects.create(start_date=date.today(), end_date=date.today(),
                                     priority=True)
        # Add a sports group
        event.sports_groups.add(SportsGroup.objects.create(name='Test Group', description='this is a test group'))

        # add norwegian and english description to the name and the description
        EventDescription.objects.create(name='test norsk', description_text='test norsk', language='nb', event=event)
        EventDescription.objects.create(name='test engelsk', description_text='test engelsk', language='en',
                                        event=event)

    def test_user_is_in_mainboard(self):
        # Checks user that is in main board
        self.assertEquals(views.user_is_in_mainboard(self.user), True)

        # Checks user is not in main board
        self.assertEquals(views.user_is_in_mainboard(self.user2), False)
