import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase, LiveServerTestCase
from django.test import TestCase
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver


class ChromeTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        if os.environ.get('BROWSER') == 'local':
            self.chrome = webdriver.Chrome()
            self.server_url = 'http://localhost:8000'
        else:
            self.chrome = webdriver.Remote(
                command_executor='http://selenium:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.CHROME)
            self.server_url = 'http://web:8000'
        self.chrome.implicitly_wait(10)
        self.precondition()

    @classmethod
    def tearDownClass(self):
        self.chrome.quit()
        super().tearDownClass()

    @classmethod
    def precondition(self):
        pass

class FirefoxTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        if os.environ.get('BROWSER') == 'local':
            self.firefox = webdriver.Firefox()
            self.server_url = 'http://localhost:8000'
            print('SERVER URL:', self.server_url)
        else:
            self.firefox = webdriver.Remote(
                command_executor='http://selenium:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.FIREFOX)
            self.server_url = 'http://web:8000'
        self.firefox.implicitly_wait(10)
        self.precondition()

    @classmethod
    def tearDownClass(self):
        self.firefox.quit()
        super().tearDownClass()

    @classmethod
    def precondition(self):
        pass
