from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from ntnui.models import User


class GroupMembersLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('group_members')
        self.response = self.client.get(url)

    def test_status_code(self):
        """
        test that view is login protected
        """
        self.assertEquals(self.response.status_code, 302)


class GroupMembersLoggedInTest(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.login_response = self.client.login(email='jameshalpert@gmail.com',
                                                password='locoloco')
        url = reverse('group_members', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)


class NoGroupTest(GroupMembersLoggedInTest):

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 404)

    def test_view_function(self):
        view = resolve('/groups/volleyball/members')
        self.assertEquals(view.func, group_views.members)


class VolleyballGroupTest(GroupMembersLoggedInTest):
    fixtures = ['users.json', 'groups.json', 'memberships.json']

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_contains_members(self):
        self.assertContains(self.response, '<div class="group-member"', 15)

    def test_total_count_members(self):
        self.assertContains(self.response, '15 members')

    # def test_csrf(self):
    #    self.assertContains(self.response, 'csrfmiddlewaretoken')

#    def test_form_inputs(self):
#        """The view must contain two inputs: csrf and email."""
#        self.assertContains(self.response, '<input', 2)
#        self.assertContains(self.response, 'type="email"', 1)

    # def test_form_inputs(self):
    #    """The view must contain two inputs: csrf and two password fields."""
    #    self.assertContains(self.response, '<input', 3)
    #    self.assertContains(self.response, 'type="password"', 2)
