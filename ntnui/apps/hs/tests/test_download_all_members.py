from django.test import TestCase
from django.core.urlresolvers import reverse


class DownloadButtonHSTest(TestCase):
    fixtures = ['users.json', 'mainboard.json', 'hs-memberships.json']

    def setUp(self):
        self.login_response = self.client.login(email='super@admin.com',
                                                password='supersuper')
        url = reverse('all_members')
        self.response = self.client.get(url)

    def test_download_button_exists(self):
        self.assertContains(self.response, '<img class="download-icon', 1)
