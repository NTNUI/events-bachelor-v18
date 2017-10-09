from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from ntnui.models import User


class InvitationsLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('group_invitations', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_status_code(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class InvitationsLoggedInTest(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.login_response = self.client.login(email='jameshalpert@gmail.com',
                                                password='locoloco')
        url = reverse('group_invitations', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)


class NoGroupTest(InvitationsLoggedInTest):

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 404)

    def test_view_function(self):
        view = resolve('/groups/volleyball/invitations')
        self.assertEquals(view.func, group_views.invitations)


class VolleyballGroupTest(InvitationsLoggedInTest):
    fixtures = ['users.json', 'groups.json', 'invitations.json', 'memberships.json']

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_contains_invitations(self):
        self.assertContains(self.response, '<div class="group-table-row"', 1)
        self.assertContains(self.response, 'Ryan Howard')

    def test_total_count_invitations(self):
        self.assertContains(self.response, '1 invitation')

    def test_total_count_members(self):
        self.assertContains(self.response, '15 members')

    def test_should_link_to_members(self):
        self.assertContains(self.response, reverse('group_members', kwargs={'slug': 'volleyball'}))

    #def test_should_link_to_requests(self):
    #    self.assertContains(self.response, reverse('group_requests', kwargs={'slug': 'volleyball'}))

    def test_should_link_to_invite(self):
        self.assertContains(self.response, reverse('group_invite_member', kwargs={'slug': 'volleyball'}))

class VolleyballNoInvitationsTest(InvitationsLoggedInTest):
    fixtures = ['users.json', 'groups.json']

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_contains_invitations(self):
        self.assertContains(self.response, '<div class="group-table-row"', 0)

    def test_total_count_invitations(self):
        self.assertContains(self.response, '0 invitations')

    def test_should_link_to_new_invite(self):
        self.assertContains(self.response, reverse('group_invite_member', kwargs={'slug': 'volleyball'}))

    def test_should_link_to_members(self):
        self.assertContains(self.response, reverse('group_members', kwargs={'slug': 'volleyball'}))

    #def test_should_link_to_requests(self):
    #    self.assertContains(self.response, reverse('group_requests', kwargs={'slug': 'volleyball'}))

    def test_total_count_members(self):
        self.assertContains(self.response, '0 members')
