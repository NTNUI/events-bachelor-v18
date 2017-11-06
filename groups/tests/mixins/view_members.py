from django.core.urlresolvers import reverse
from django.urls import resolve
from groups import views as group_views
from .general import (
    CoreBoardMemberMixin,
    GeneralBoardMemberMixin,
    GeneralGroupLeaderMixin,
)


class VM_CoreBoardMemberMixin(object):

    def test_contains_all_members(self):
        self.assertContains(self.response, '<div class="group-table-row', 16)

    def test_total_count_members(self):
        self.assertContains(self.response, '16 members')

    def test_total_count_invitations(self):
        self.assertContains(self.response, '1 invitation')

    def test_should_link_to_inviations(self):
        self.assertContains(self.response, reverse(
            'group_invitations', kwargs={'slug': 'volleyball'}))

    def test_view_function(self):
        view = resolve('/groups/volleyball/members')
        self.assertEquals(view.func, group_views.members)


class VM_BoardMemberMixin(VM_CoreBoardMemberMixin, GeneralBoardMemberMixin):
    def setUp(self):
        super(VM_BoardMemberMixin, self).setUp()

    def test_should_not_link_to_new_invite(self):
        self.assertNotContains(self.response, reverse(
            'group_invite_member', kwargs={'slug': 'volleyball'}))


class VM_GroupLeaderMixin(VM_CoreBoardMemberMixin, GeneralGroupLeaderMixin):
    def setUp(self):
        super(VM_GroupLeaderMixin, self).setUp()

    def test_should_link_to_new_invite(self):
        self.assertContains(self.response, reverse(
            'group_invite_member', kwargs={'slug': 'volleyball'}))
