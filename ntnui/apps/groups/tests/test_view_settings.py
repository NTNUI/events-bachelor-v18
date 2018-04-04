from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase


class InviteLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse('group_settings', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_status_code(self):
        """Test that view is login protected."""
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
    fixtures = ['users.json', 'groups.json', 'boards.json']

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_button_exists(self):
        self.assertContains(self.response, '<input type="submit"', 1)
        self.assertContains(self.response, 'Change settings', 1)

    def test_radio_buttons_exists(self):
        self.assertContains(self.response, '<input type="radio"', 2)

    def test_image_input_exists(self):
        self.assertContains(self.response, '<input type="file" name="thumbnail', 1)
        self.assertContains(self.response, '<input type="file" name="cover_photo', 1)

    def test_description_exists(self):
        self.assertContains(self.response, '<textarea name="description', 1)
