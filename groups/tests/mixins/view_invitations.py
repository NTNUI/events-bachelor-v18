from django.core.urlresolvers import reverse
from django.urls import resolve
from groups import views as group_views
from .general import (
    CoreBoardMemberMixin,
    GeneralBoardMemberMixin,
    GeneralGroupLeaderMixin,
)


class VI_CoreBoardMemberMixin(object):

    def test_view_function(self):
        view = resolve('/groups/volleyball/invitations')
        self.assertEquals(view.func, group_views.invitations)

    def test_contains_all_invitations(self):
        self.assertContains(self.response, '<div class="group-table-row', 1)
        self.assertContains(self.response, 'Ryan Howard')

    def test_total_count_invitations(self):
        self.assertContains(self.response, '1 invitation')

    def test_total_count_members(self):
        self.assertContains(self.response, '16 members')

    def test_should_link_to_members(self):
        self.assertContains(self.response, reverse(
            'group_members', kwargs={'slug': 'volleyball'}))


class VI_BoardMemberMixin(VI_CoreBoardMemberMixin, GeneralBoardMemberMixin):
    def setUp(self):
        super(VI_BoardMemberMixin, self).setUp()

    def test_should_not_link_to_new_invite(self):
        self.assertNotContains(self.response, reverse(
            'group_invite_member', kwargs={'slug': 'volleyball'}))


class VI_GroupLeaderMixin(VI_CoreBoardMemberMixin, GeneralGroupLeaderMixin):
    def setUp(self):
        super(VI_GroupLeaderMixin, self).setUp()

    def test_should_link_to_new_invite(self):
        self.assertContains(self.response, reverse(
            'group_invite_member', kwargs={'slug': 'volleyball'}))
