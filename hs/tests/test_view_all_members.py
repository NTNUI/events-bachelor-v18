from django.test import TestCase
from django.urls import resolve
from django.core.urlresolvers import reverse
from hs import views as hs_views


class AllMembersLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('all_members')
        self.response = self.client.get(url)

    def test_status_code(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class AllMembersLoggedInTest(TestCase):
    fixtures = ['users.json', 'mainboard.json', 'hs-memberships.json']

    def setUp(self):
        self.login_response = self.client.login(email='super@admin.com',
                                                password='supersuper')
        url = reverse('all_members')
        self.response = self.client.get(url)

    def test_view_function(self):
        view = resolve('/hs/allmembers')
        self.assertEquals(view.func, hs_views.list_all_members)


class AllMembersTest(AllMembersLoggedInTest):
    fixtures = ['users.json', 'groups.json', 'boards.json', 'mainboard.json', 'hs-memberships.json']

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_table_exists(self):
        self.assertContains(self.response, '<div class="list-header">', 1)
