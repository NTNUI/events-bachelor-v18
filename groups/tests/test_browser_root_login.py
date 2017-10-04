from django.contrib.staticfiles.testing import StaticLiveServerTestCase, LiveServerTestCase
from django.test import TestCase
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver

StaticLiveServerTestCase.port = 5000

from ntnui.tests.browser.lib import BrowserTestCase

LOCAL = False


class SeleniumRemoteTestCase(StaticLiveServerTestCase):
    fixtures = ['users.json']

    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        if LOCAL:
            cls.selenium = webdriver.Chrome()
            cls.server_url = 'http://localhost:8000'
        else:
            cls.selenium = webdriver.Remote(
                command_executor='http://selenium:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.CHROME)
            cls.server_url = 'http://web:8000'
        cls.selenium.implicitly_wait(10)
        cls.precondition()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    @classmethod
    def precondition(self):
        pass

    def test_login(self):
        self.selenium.get('%s%s' % (self.server_url, '/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('todd.packer@online.com')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('locoloco')
        self.selenium.find_element_by_xpath('//button[text()="Log in"]').click()
        account_p = self.selenium.find_element_by_xpath('//p[text()="Account"]')
        self.assertEquals(account_p.text, 'Account')
        self.assertTrue('href="/logout/">Log out</a>' in self.selenium.page_source)
