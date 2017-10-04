from django.contrib.staticfiles.testing import StaticLiveServerTestCase, LiveServerTestCase
from django.test import TestCase
from browser.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver

LOCAL = False

class BrowserTestCase(StaticLiveServerTestCase):
    fixtures = ['users.json']

    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        if LOCAL:
            cls.browser = webdriver.Chrome()
            cls.server_url = 'http://localhost:8000'
        else:
            cls.browser = webdriver.Remote(
                command_executor='http://browser:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.CHROME)
            cls.server_url = 'http://web:8000'
        cls.browser.implicitly_wait(10)
        cls.precondition()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    @classmethod
    def precondition(self):
        pass
