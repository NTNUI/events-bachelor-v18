from django.test import TestCase
from django.core.urlresolvers import reverse


class DownloadButtonHSTest(TestCase):
    fixtures = ['users.json', 'mainboard.json', 'hs-memberships.json']

    def setUp(self):
        self.login_response = self.client.login(email='jameshalpert@gmail.com',
                                                password='locoloco')
        url = reverse('all_members')
        self.response = self.client.get(url)

    def test_download_button_exists(self):
        self.assertContains(self.response, '<div class="download-button', 1)
