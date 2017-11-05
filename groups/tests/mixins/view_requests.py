from django.core.urlresolvers import reverse
from django.urls import resolve
from groups import views as group_views
from .general import (
    CoreBoardMemberMixin,
    GeneralBoardMemberMixin,
    GeneralGroupLeaderMixin,
)


class VR_CoreBoardMemberMixin(object):

    def test_view_function(self):
        view = resolve('/groups/volleyball/requests')
        self.assertEquals(view.func, group_views.requests)

    def test_contains_all_requests(self):
        self.assertContains(self.response, '<div class="group-table-row"', 1)
        self.assertContains(self.response, 'Ryan Howard')

    def test_total_count_invitations(self):
        self.assertContains(self.response, '1 request')

    def test_total_count_members(self):
        self.assertContains(self.response, '16 members')

    def test_should_link_to_members(self):
        self.assertContains(self.response, reverse(
            'group_members', kwargs={'slug': 'volleyball'}))


class VR_BoardMemberMixin(VR_CoreBoardMemberMixin, GeneralBoardMemberMixin):
    def setUp(self):
        super(VR_BoardMemberMixin, self).setUp()


class VR_GroupLeaderMixin(VR_CoreBoardMemberMixin, GeneralGroupLeaderMixin):
    def setUp(self):
        super(VR_GroupLeaderMixin, self).setUp()

    def test_should_link_to_requests(self):
        self.assertContains(self.response, reverse(
            'group_requests', kwargs={'slug': 'volleyball'}))

    def test_should_contain_request_table(self):
        self.assertContains(self.response, 'Can I join?')

    def test_should_contain_request_table_content(self):
        self.assertContains(
            self.response, '<input type="hidden" name="request_id"')

    def test_should_contain_request_table_button(self):
        self.assertContains(self.response, 'input type="submit"')
