from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

class MySeleniumTests(StaticLiveServerTestCase):
    fixtures = ['users.json']

    @classmethod
    def setUpClass(cls):
        print('RUNNING CLASS YO!')

    def setUp(self):
        print('SEETTING UP')
