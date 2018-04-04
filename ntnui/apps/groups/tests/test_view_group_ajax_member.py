from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from accounts.models import User

from .mixins.general import (
    TEST_USERS,
)

VIEW_NAME = 'group_member_ajax'
VALID_MEMBER_VIEW_URL = '/groups/volleyball/ajax/member/5'
NOT_VALID_MEMBER_VIEW_URL = '/groups/volleyball/ajax/member/999'
TEST_PASSWORD = 'locoloco'


class LoggedInMixin(object):
    fixtures = ['users.json']

    def setUp(self):
        if not hasattr(self, 'email'):
            raise ValueError('Make sure to specify email in your test class')
        if not hasattr(self, 'url_name'):
            raise ValueError('Make sure to include url_name in your test class')
        if not hasattr(self, 'member_id'):
            raise ValueError('Make sure to include member_id in your test class')
        self.login_response = self.client.login(email=self.email,
                                                password=TEST_PASSWORD)
        url = reverse(self.url_name, kwargs={'slug': 'volleyball', 'member_id': self.member_id})
        self.response = self.client.get(url)


class GroupMembersLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse(VIEW_NAME, kwargs={'slug': 'volleyball', 'member_id': '5'})
        self.response = self.client.get(url)

    def test_status_code_302(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class NoGroupTest(LoggedInMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['not_member']
        self.url_name = VIEW_NAME
        self.member_id = 5
        super(NoGroupTest, self).setUp()

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 404)


class MemberTest(LoggedInMixin, TestCase):
    fixtures = ['users.json', 'groups.json', 'memberships.json', 'boards.json']

    def setUp(self):
        self.email = TEST_USERS['member']
        self.url_name = VIEW_NAME
        self.member_id = 5
        super(MemberTest, self).setUp()

    def test_shoud_contain_error_text(self):
        self.assertContains(
            self.response, 'You do not have permission to see this.')

    def test_view_function(self):
        view = resolve(VALID_MEMBER_VIEW_URL)
        self.assertEquals(view.func, group_views.member_info)


class PresidentValidMemberTest(LoggedInMixin, TestCase):
    fixtures = ['users.json', 'groups.json', 'memberships.json', 'boards.json']

    def setUp(self):
        self.email = TEST_USERS['president']
        self.url_name = VIEW_NAME
        self.member_id = 5
        super(PresidentValidMemberTest, self).setUp()

    def test_should_contain_member_name(self):
        self.assertContains(self.response, 'Creed Bratton')

    def test_should_contain_member_email(self):
        self.assertContains(self.response, 'mynameiscreed@bratton.com')

    def test_view_function(self):
        view = resolve(VALID_MEMBER_VIEW_URL)
        self.assertEquals(view.func, group_views.member_info)


class PresidentInvalidMemberTest(LoggedInMixin, TestCase):
    fixtures = ['users.json', 'groups.json', 'memberships.json', 'boards.json']

    def setUp(self):
        self.email = TEST_USERS['president']
        self.url_name = VIEW_NAME
        self.member_id = 999
        super(PresidentInvalidMemberTest, self).setUp()

    def test_shoud_contain_error_text(self):
        self.assertContains(
            self.response, 'This membership does not exist.')

    def test_view_function(self):
        view = resolve(VALID_MEMBER_VIEW_URL)
        self.assertEquals(view.func, group_views.member_info)
