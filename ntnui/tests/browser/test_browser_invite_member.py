from django.conf import settings
from ntnui.tests.browser.lib.browser_test_case import ChromeTestCase, FirefoxTestCase
from ntnui.tests.browser.lib.helpers import login_user
from selenium.webdriver.support.wait import WebDriverWait
from groups.models import Invitation, SportsGroup
from ntnui.models import User


def invite_success(cls, browser):
    browser.get(cls.server_url + '/groups/volleyball/members/invite')
    email_input = browser.find_element_by_name('email')
    email_input.send_keys('meredith.palmer@dundermifflin.com')
    browser.find_element_by_xpath('//button[text()="Invite person"]').click()
    element = WebDriverWait(browser, 10).until(
        lambda x: x.find_element_by_xpath('//div[contains(@class, "members-list-header")]'))
    cls.assertTrue('1 invitation' in browser.page_source)
    cls.assertTrue('Meredith Palmer' in browser.page_source)
    invitations = Invitation.objects.all()
    volleyball = SportsGroup.objects.get(slug='volleyball')
    meredith = User.objects.get(email='meredith.palmer@dundermifflin.com')
    cls.assertEquals(len(invitations), 1)
    cls.assertEquals(invitations[0].person, meredith)
    cls.assertEquals(invitations[0].group, volleyball)


class InviteChrome(ChromeTestCase):
    fixtures = ['users.json', 'groups.json', 'memberships.json']

    def test_success_invite(self):
        login_user(self, self.chrome)
        invite_success(self, self.chrome)


class LoginFirefox(FirefoxTestCase):
    fixtures = ['users.json', 'groups.json', 'memberships.json']

    def test_success_invite(self):
        login_user(self, self.firefox)
        invite_success(self, self.firefox)
