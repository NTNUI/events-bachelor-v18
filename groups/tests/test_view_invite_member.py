from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase


class InviteLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('group_invite_member', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_status_code(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class InviteLoggedInTest(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.login_response = self.client.login(email='jameshalpert@gmail.com',
                                                password='locoloco')
        url = reverse('group_invite_member', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_view_function(self):
        view = resolve('/groups/volleyball/members/invite')
        self.assertEquals(view.func, group_views.invite_member)


class NoGroupTest(InviteLoggedInTest):

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 404)

    # TODO: Test that the form is not shown


class VolleyballGroupTest(InviteLoggedInTest):
    fixtures = ['users.json', 'groups.json']

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    # test that the form is shown
