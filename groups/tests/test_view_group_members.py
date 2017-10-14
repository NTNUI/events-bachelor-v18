from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from accounts.models import User

from .mixins.general import (
    LoggedInMixin,
    GeneralMemberMixin,
    CoreBoardMemberMixin,
    TEST_USERS,
)

from .mixins.view_members import (
    VM_CoreBoardMemberMixin,
    VM_BoardMemberMixin,
    VM_GroupLeaderMixin,
)


class GroupMembersLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('group_members', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_status_code_302(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class NoGroupTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['not_member']
        self.url_name = 'group_members'
        super(NoGroupTest, self).setUp()

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 404)

    def test_view_function(self):
        view = resolve('/groups/volleyball/members')
        self.assertEquals(view.func, group_views.members)


class MemberTest(GeneralMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['member']
        self.url_name = 'group_members'
        super(MemberTest, self).setUp()

    def test_contains_no_members(self):
        self.assertContains(self.response, '<div class="group-table-row"', 0)

    def test_shoud_contain_members_error_text(self):
        self.assertContains(
            self.response, 'You do not have permissions to see this.')

    def test_should_not_link_to_inviations(self):
        self.assertNotContains(self.response, reverse(
            'group_invitations', kwargs={'slug': 'volleyball'}))

    def test_should_not_link_to_new_invite(self):
        self.assertNotContains(self.response, reverse(
            'group_invite_member', kwargs={'slug': 'volleyball'}))


class CashierTest(VM_BoardMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['cashier']
        self.url_name = 'group_members'
        super(CashierTest, self).setUp()


class VicePresidentTest(VM_GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['vice_president']
        self.url_name = 'group_members'
        super(VicePresidentTest, self).setUp()


class PresidentTest(VM_GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['president']
        self.url_name = 'group_members'
        super(PresidentTest, self).setUp()
