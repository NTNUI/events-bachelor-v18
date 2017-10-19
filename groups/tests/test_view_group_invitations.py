from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from accounts.models import User

from .mixins.general import (
    GeneralMemberMixin,
    TEST_USERS,
)

from .mixins.view_invitations import (
    VI_CoreBoardMemberMixin,
    VI_BoardMemberMixin,
    VI_GroupLeaderMixin,
)


VIEW_NAME = 'group_invitations'


class InvitationsLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse(VIEW_NAME, kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_status_code(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class ViewInvitationMemberTest(GeneralMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['member']
        self.url_name = VIEW_NAME
        super(ViewInvitationMemberTest, self).setUp()

    def test_view_function(self):
        view = resolve('/groups/volleyball/invitations')
        self.assertEquals(view.func, group_views.invitations)

    def test_contains_no_invitations(self):
        self.assertContains(self.response, '<div class="group-table-row"', 0)

    def test_shoud_contain_error_text(self):
        self.assertContains(
            self.response, 'You do not have permissions to see this.')

    def test_should_not_link_to_inviations(self):
        self.assertNotContains(self.response, reverse(
            'group_invitations', kwargs={'slug': 'volleyball'}))

    def test_should_not_link_to_new_invite(self):
        self.assertNotContains(self.response, reverse(
            'group_invite_member', kwargs={'slug': 'volleyball'}))


class ViewInvitationCashierTest(VI_BoardMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['cashier']
        self.url_name = VIEW_NAME
        super(ViewInvitationCashierTest, self).setUp()


class ViewInvitationVicePresidentTest(VI_GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['vice_president']
        self.url_name = VIEW_NAME
        super(ViewInvitationVicePresidentTest, self).setUp()


class ViewInvitationPresidentTest(VI_GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['president']
        self.url_name = VIEW_NAME
        super(ViewInvitationPresidentTest, self).setUp()
