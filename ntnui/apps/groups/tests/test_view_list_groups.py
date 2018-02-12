from django.test import TestCase
from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from ..models import Membership


class ListGroupLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('home')
        self.response = self.client.get(url)

    def test_status_code(self):
        """
        test that view is login protected
        """
        self.assertEquals(self.response.status_code, 302)


class ListGroupsLoggedInTest(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.login_response = self.client.login(email='jameshalpert@gmail.com',
                                                password='locoloco')
        url = reverse('home')
        self.response = self.client.get(url)

    def test_view_function(self):
        view = resolve('/')
        self.assertEquals(view.func, group_views.list_groups)


class NoListTest(ListGroupsLoggedInTest):
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)


class MyGroupTest(ListGroupsLoggedInTest):
    fixtures = ['complete.json']

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_group_number(self):
        self.assertContains(self.response, '<div class="group-card-all-groups', 3)
