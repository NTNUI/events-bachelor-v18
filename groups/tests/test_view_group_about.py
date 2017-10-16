from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from accounts.models import User


from .mixins.general import (
    GeneralMemberMixin,
    GeneralBoardMemberMixin,
    GeneralGroupLeaderMixin,
    TEST_USERS,
)
from .mixins.view_about import VA_CoreMemberMixin


class GroupAboutLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('group_index', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_status_code(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class ViewAboutMemberTest(GeneralMemberMixin, VA_CoreMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['member']
        self.url_name = 'group_index'
        super(ViewAboutMemberTest, self).setUp()


class ViewAboutCashierTest(GeneralBoardMemberMixin, VA_CoreMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['cashier']
        self.url_name = 'group_index'
        super(ViewAboutCashierTest, self).setUp()


class ViewAboutVicePresidentTest(GeneralGroupLeaderMixin, VA_CoreMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['vice_president']
        self.url_name = 'group_index'
        super(ViewAboutVicePresidentTest, self).setUp()


class ViewAboutPresidentTest(GeneralGroupLeaderMixin, VA_CoreMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['president']
        self.url_name = 'group_index'
        super(ViewAboutPresidentTest, self).setUp()
