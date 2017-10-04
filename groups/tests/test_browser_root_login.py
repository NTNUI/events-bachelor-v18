from django.conf import settings
from ntnui.tests.browser.lib.browser_test_case import BrowserTestCase


class LoginTestCase(BrowserTestCase):
    fixtures = ['users.json']

    def test_login(self):
        self.browser.get(self.server_url + '/login/')
        username_input = self.browser.find_element_by_name('username')
        username_input.send_keys(settings.DUMMY_USER_EMAIL)
        password_input = self.browser.find_element_by_name('password')
        password_input.send_keys(settings.DUMMY_USER_PASSWORD)
        self.browser.find_element_by_xpath('//button[text()="Log in"]').click()
        account_p = self.browser.find_element_by_xpath('//p[text()="Account"]')
        self.assertEquals(account_p.text, 'Account')
        self.assertTrue(
            'href="/logout/">Log out</a>' in self.browser.page_source)
