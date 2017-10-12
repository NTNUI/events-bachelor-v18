from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from ntnui.models import User


class GroupAboutLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('group_index', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_status_code(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class GroupAboutLoggedInTest(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.login_response = self.client.login(email='jameshalpert@gmail.com',
                                                password='locoloco')
        url = reverse('group_index', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)


class NoGroupTest(GroupAboutLoggedInTest):

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 404)

    def test_view_function(self):
        view = resolve('/groups/volleyball')
        self.assertEquals(view.func, group_views.group_index)


class VolleyballGroupTest(GroupAboutLoggedInTest):
    fixtures = ['users.json', 'groups.json',
                'boards.json']

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_has_description(self):
        self.assertContains(self.response, 'About NTNUI Volleyball')
        self.assertContains(
            self.response, 'NTNUI Volleyball is one of the largest groups within NTNUI')

    def test_total_count_board_members(self):
        self.assertContains(self.response, '<div class="group-member-name"', 3)
