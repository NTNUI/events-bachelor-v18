from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from accounts.models import User

from .mixins.general import (
    LoggedInMixin,
    GroupMixin,
    GeneralBoardMemberMixin,
    GeneralGroupLeaderMixin,
    GeneralMemberMixin,
    CoreBoardMemberMixin,
    TEST_USERS,
)


class GroupMembersLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('group_members', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_status_code(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class NoGroupTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['not_member']
        super(NoGroupTest, self).setUp()

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 404)

    def test_view_function(self):
        view = resolve('/groups/volleyball/members')
        self.assertEquals(view.func, group_views.members)


class MemberTest(GeneralMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['member']
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


class MP_CoreBoardMemberMixin(object):
    #def setUp(self):
    #    super(MP_CoreBoardMemberMixin, self).setUp()

    def test_contains_all_members(self):
        self.assertContains(self.response, '<div class="group-table-row"', 16)

    def test_total_count_members(self):
        self.assertContains(self.response, '16 members')

    def test_total_count_invitations(self):
        self.assertContains(self.response, '1 invitation')

    def test_should_link_to_inviations(self):
        self.assertContains(self.response, reverse(
            'group_invitations', kwargs={'slug': 'volleyball'}))


class MP_BoardMemberMixin(MP_CoreBoardMemberMixin, GeneralBoardMemberMixin):
    def setUp(self):
        super(MP_BoardMemberMixin, self).setUp()

    def test_should_not_link_to_new_invite(self):
        self.assertNotContains(self.response, reverse(
            'group_invite_member', kwargs={'slug': 'volleyball'}))


class MP_GroupLeaderMixin(MP_CoreBoardMemberMixin, GeneralGroupLeaderMixin):
    def setUp(self):
        super(MP_GroupLeaderMixin, self).setUp()

    def test_should_link_to_new_invite(self):
        self.assertContains(self.response, reverse(
            'group_invite_member', kwargs={'slug': 'volleyball'}))


class CashierTest(MP_BoardMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['cashier']
        super(CashierTest, self).setUp()


class VicePresidentTest(MP_GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['vice_president']
        super(VicePresidentTest, self).setUp()


class PresidentTest(MP_GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['president']
        super(PresidentTest, self).setUp()
