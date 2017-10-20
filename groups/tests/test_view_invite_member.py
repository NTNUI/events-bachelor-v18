from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase

from .mixins.general import (
    GeneralMemberMixin,
    TEST_USERS,
)
from .mixins.view_invite_member import (
    VIM_CoreBoardMemberMixin,
    VIM_BoardMemberMixin,
    VIM_GroupLeaderMixin,
)
VIEW_NAME = 'group_invite_member'


class InviteLoggedOutTest(TestCase):
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
        view = resolve('/groups/volleyball/members/invite')
        self.assertEquals(view.func, group_views.invite_member)

    def test_shoud_contain_error_text(self):
        self.assertContains(
            self.response, 'You do not have permissions to see this.')

    def test_should_not_link_to_inviations(self):
        self.assertNotContains(self.response, reverse(
            'group_invitations', kwargs={'slug': 'volleyball'}))

    def test_should_not_contain_form_title(self):
        self.assertNotContains(self.response, 'Invite member to group')

    def test_should_not_contain_form_email_input(self):
        self.assertNotContains(
            self.response, '<input type="text" name="email"')

    def test_should_not_contain_form_email_submit(self):
        self.assertNotContains(self.response, '<button type="submit"')
        self.assertNotContains(self.response, 'Invite person</button>')


class ViewNewInvitationCashierTest(VIM_BoardMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['cashier']
        self.url_name = VIEW_NAME
        super(ViewNewInvitationCashierTest, self).setUp()


class ViewNewInvitationVicePresidentTest(VIM_GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['vice_president']
        self.url_name = VIEW_NAME
        super(ViewNewInvitationVicePresidentTest, self).setUp()


class ViewNewInvitationPresidentTest(VIM_GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['president']
        self.url_name = VIEW_NAME
        super(ViewNewInvitationPresidentTest, self).setUp()
