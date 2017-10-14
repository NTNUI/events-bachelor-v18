from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from accounts.models import User

# We test with the group 'volleyball'

# TEST USERS
# Todd Packer     - todd.packer@online.com            - President
# James Halpert   - jameshalpert@gmail.com            - Vice President
# Angela Martin   - frankela@steinberg.org            - Cashier
# Michael Scott   - michael.scott@dundermifflin.com   - Normal Member
# Meredith Palmer - meredith.palmer@dundermifflin.com - Not a member

# All test users have password "locoloco"

TEST_USERS = {
    'president': 'todd.packer@online.com',
    'vice_president': 'jameshalpert@gmail.com',
    'cashier': 'frankela@steinberg.org',
    'member': 'michael.scott@dundermifflin.com',
    'not_member': 'meredith.palmer@dundermifflin.com'
}

TEST_PASSWORD = 'locoloco'


class GroupMembersLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('group_members', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_status_code(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class LoggedInMixin(object):
    fixtures = ['users.json']

    def setUp(self):
        self.login_response = self.client.login(email=self.email,
                                                password=TEST_PASSWORD)
        url = reverse('group_members', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)


class GroupMixin(LoggedInMixin):
    fixtures = ['users.json', 'groups.json',
                'memberships.json', 'invitations.json', 'boards.json']

    def setUp(self):
        super(GroupMixin, self).setUp()

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_should_link_to_about(self):
        self.assertContains(self.response, reverse(
            'group_index', kwargs={'slug': 'volleyball'}))


class NoGroupTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['not_member']
        super(NoGroupTest, self).setUp()

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 404)

    def test_view_function(self):
        view = resolve('/groups/volleyball/members')
        self.assertEquals(view.func, group_views.members)


class MemberTest(GroupMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['member']
        super(MemberTest, self).setUp()

    def test_contains_no_members(self):
        self.assertContains(self.response, '<div class="group-table-row"', 0)

    def test_shoud_contain_text_about_why_you_cant_see_members(self):
        self.assertContains(
            self.response, 'You do not have permissions to see this.')

    def test_should_not_link_to_inviations(self):
        self.assertNotContains(self.response, reverse(
            'group_invitations', kwargs={'slug': 'volleyball'}))

    def test_should_not_link_to_new_invite(self):
        self.assertNotContains(self.response, reverse(
            'group_invite_member', kwargs={'slug': 'volleyball'}))


class BoardMemberMixin(GroupMixin):
    def setUp(self):
        super(BoardMemberMixin, self).setUp()

    def test_contains_members(self):
        self.assertContains(self.response, '<div class="group-table-row"', 16)

    def test_total_count_members(self):
        self.assertContains(self.response, '16 members')

    def test_total_count_invitations(self):
        self.assertContains(self.response, '1 invitation')

    def test_should_link_to_inviations(self):
        self.assertContains(self.response, reverse(
            'group_invitations', kwargs={'slug': 'volleyball'}))


class GroupLeaderMixin(BoardMemberMixin):
    def setUp(self):
        super(GroupLeaderMixin, self).setUp()

    def test_should_link_to_new_invite(self):
        self.assertContains(self.response, reverse(
            'group_invite_member', kwargs={'slug': 'volleyball'}))


class CashierTest(BoardMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['cashier']
        super(CashierTest, self).setUp()

    def test_should_not_link_to_new_invite(self):
        self.assertNotContains(self.response, reverse(
            'group_invite_member', kwargs={'slug': 'volleyball'}))


class VicePresidentTest(GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['vice_president']
        super(VicePresidentTest, self).setUp()


class PresidentTest(GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['president']
        super(PresidentTest, self).setUp()
