from groups import views as group_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase

from .mixins.general import (
    GeneralMemberMixin,
    TEST_USERS,
)
from .mixins.view_requests import (
    VR_BoardMemberMixin,
    VR_GroupLeaderMixin,
)

VIEW_NAME = 'group_requests'


class InviteLoggedOutTest(TestCase):
    def setUp(self):
        url = reverse(VIEW_NAME, kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_status_code(self):
        """Test that view is login protected."""
        self.assertEquals(self.response.status_code, 302)


class ViewRequestMemberTest(GeneralMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['member']
        self.url_name = VIEW_NAME
        super(ViewRequestMemberTest, self).setUp()

    def test_view_function(self):
        view = resolve('/groups/volleyball/members/invite')
        self.assertEquals(view.func, group_views.invite_member)

    def test_should_contain_error_text(self):
        self.assertContains(
            self.response, 'You do not have permissions to see this.')

    def test_should_not_link_to_requests(self):
        self.assertNotContains(self.response, reverse(
            'group_requests', kwargs={'slug': 'volleyball'}))

    def test_should_not_contain_request_table(self):
        self.assertNotContains(self.response, 'Can I join?')

    def test_should_not_contain_request_table_content(self):
        self.assertNotContains(
            self.response, '<input type="hidden" name="request_id"')

    def test_should_not_contain_request_table_button(self):
        self.assertNotContains(self.response, 'input type="submit"')


class ViewNewInvitationCashierTest(VR_BoardMemberMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['cashier']
        self.url_name = VIEW_NAME
        super(ViewNewInvitationCashierTest, self).setUp()


class ViewNewInvitationVicePresidentTest(VR_GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['vice_president']
        self.url_name = VIEW_NAME
        super(ViewNewInvitationVicePresidentTest, self).setUp()


class ViewNewInvitationPresidentTest(VR_GroupLeaderMixin, TestCase):
    def setUp(self):
        self.email = TEST_USERS['president']
        self.url_name = VIEW_NAME
        super(ViewNewInvitationPresidentTest, self).setUp()
