import os
import socket
from django.contrib.staticfiles.testing import StaticLiveServerTestCase, LiveServerTestCase
from django.test import TestCase
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver


class ChromeTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(self):
        if os.environ.get('BROWSER') == 'local':
            super().setUpClass()
            self.chrome = webdriver.Chrome()
            self.server_url = self.live_server_url
        else:
            self.host = socket.gethostbyname(socket.gethostname())
            super(ChromeTestCase, self).setUpClass()
            self.chrome = webdriver.Remote(
                command_executor='http://selenium:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.CHROME)
            self.server_url = self.live_server_url
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
        if os.environ.get('BROWSER') == 'local':
            super().setUpClass()
            self.firefox = webdriver.Firefox()
            self.server_url = self.live_server_url
        else:
            self.host = socket.gethostbyname(socket.gethostname())
            super(FirefoxTestCase, self).setUpClass()
            self.firefox = webdriver.Remote(
                command_executor='http://selenium:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.FIREFOX)
            self.server_url = self.live_server_url
        self.firefox.implicitly_wait(10)
        self.precondition()

    @classmethod
    def tearDownClass(self):
        self.firefox.quit()
        super().tearDownClass()

    @classmethod
    def precondition(self):
        pass
