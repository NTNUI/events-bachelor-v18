from django.test import TestCase
from django.urls import resolve
from hs import views as hs_views


class AllMembersLoggedOutTest(TestCase):
    def setUp(self):
        url = 'hs/allmembers'
        self.response = self.client.get(url)

    def test_status_code(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class AllMembersLoggedInTest(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.login_response = self.client.login(email='jameshalpert@gmail.com',
                                                password='locoloco')
        url = 'hs/allmembers'
        self.response = self.client.get(url)

    def test_view_function(self):
        view = resolve('hs/allmembers')
        self.assertEquals(view.func, hs_views.list_all_members)

    def test_shows_member(self):
        self.assertContains(self.response, 'James Halpert', 1)


class AllMembersTest(AllMembersLoggedInTest):
    fixtures = ['users.json', 'groups.json', 'boards.json']

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_table_exists(self):
        self.assertContains(self.response, '<div class="members-list-header">', 1)
