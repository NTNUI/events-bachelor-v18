from django.conf import settings
from ntnui.tests.browser.lib.browser_test_case import ChromeTestCase, FirefoxTestCase


def login_general(browser, server_url, assertEquals, assertTrue):
    browser.get(server_url + '/login/')
    username_input = browser.find_element_by_name('username')
    username_input.send_keys(settings.DUMMY_USER_EMAIL)
    password_input = browser.find_element_by_name('password')
    password_input.send_keys(settings.DUMMY_USER_PASSWORD)
    browser.find_element_by_xpath('//button[text()="Log in"]').click()
    account_p = browser.find_element_by_xpath('//p[text()="Account"]')
    assertEquals(account_p.text, 'Account')
    assertTrue(
        'href="/logout/">Log out</a>' in browser.page_source)

class LoginChrome(ChromeTestCase):
    fixtures = ['users.json']

    def test_login_chrome(self):
        login_general(self.chrome, self.server_url, self.assertEquals, self.assertTrue)

class LoginFirefox(FirefoxTestCase):
    fixtures = ['users.json']

    def test_login_chrome(self):
        login_general(self.firefox, self.server_url, self.assertEquals, self.assertTrue)
