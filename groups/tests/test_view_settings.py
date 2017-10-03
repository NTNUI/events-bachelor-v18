from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase


class InviteLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('group_settings', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_status_code(self):
        """
        test that view is login protected
        """
        self.assertEquals(self.response.status_code, 302)


class SettingsLoggedInTest(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.login_response = self.client.login(email='jameshalpert@gmail.com',
                                                password='locoloco')
        url = reverse('group_settings', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_view_function(self):
        view = resolve('/groups/volleyball/settings')
        self.assertEquals(view.func, group_views.settings)


class NoGroupTest(SettingsLoggedInTest):
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 404)



class VolleyballGroupTest(SettingsLoggedInTest):
    fixtures = ['users.json', 'groups.json']

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_button_exists(self):
        self.assertContains(self.response, '<button type="submit"', 1)
        self.assertContains(self.response, 'Change settings</button>', 1)

    def test_checkbox_exists(self):
        self.assertContains(self.response, '<input type="checkbox"', 1)
