from django.test import TestCase
from django.core.urlresolvers import reverse


class TestPresidentFormCreation(TestCase):
    fixtures = ['complete.json']

    def setUp(self):
        self.login_response = self.client.login(email='todd.packer@online.com',
                                                password='locoloco')
        url = reverse('forms_list', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_can_see_form(self):
        self.assertContains(
            self.response, '<button type="submit" class="group-settings-public-check btn btn-success')


class TestMemberFormList(TestCase):
    fixtures = ['complete.json']

    def setUp(self):
        self.login_response = self.client.login(email='mynameiscreed@bratton.com',
                                                password='locoloco')
        url = reverse('forms_list', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_can_not_see_form(self):
        self.assertNotContains(
            self.response, '<button type="submit" class="form-button btn btn-success" name="openForm" value="Board Change Form"')


class TestNonMemberFormList(TestCase):
    fixtures = ['complete.json']

    def setUp(self):
        self.login_response = self.client.login(email='meredith.palmer@dundermifflin.com',
                                                password='locoloco')
        url = reverse('forms_list', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_get_redirect(self):
        self.assertEquals(self.response.status_code, 302)
