from django.conf import settings
import time
from ntnui.tests.browser.lib.browser_test_case import ChromeTestCase, FirefoxTestCase
from ntnui.tests.browser.lib.helpers import login_user

def invite_success(cls, browser):
    browser.get(cls.server_url + '/groups/volleyball/members/invite')
    email_input = browser.find_element_by_name('email')
    email_input.send_keys('meredith.palmer@dundermifflin.com')
    browser.find_element_by_xpath('//button[text()="Invite person"]').click()
    time.sleep(3)
    # check that the invitation is in the list

    #account_p = browser.find_element_by_xpath('//p[text()="Account"]')
    #assertEquals(account_p.text, 'Account')
    #assertTrue(
    #    'href="/logout/">Log out</a>' in browser.page_source)"""

class InviteChrome(ChromeTestCase):
    fixtures = ['users.json', 'groups.json', 'memberships.json']

    #def test_login_chrome(self):
    #    login_user(self, self.chrome)
    #    invite_success(self, self.chrome)


#class LoginFirefox(FirefoxTestCase):
#    fixtures = ['users.json']
#
#    def test_login_chrome(self):
#        login_general(self, self.firefox)
