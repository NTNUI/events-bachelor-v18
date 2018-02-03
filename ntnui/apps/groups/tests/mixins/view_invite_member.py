from django.core.urlresolvers import reverse
from django.urls import resolve
from groups import views as group_views
from .general import (
    CoreBoardMemberMixin,
    GeneralBoardMemberMixin,
    GeneralGroupLeaderMixin,
)


class VIM_CoreBoardMemberMixin(object):

    def test_view_function(self):
        view = resolve('/groups/volleyball/members/invite')
        self.assertEquals(view.func, group_views.invite_member)

    def test_should_contain_form_title(self):
        self.assertContains(self.response, 'Invite member to group')

    def test_should_contain_form_email_input(self):
        self.assertContains(self.response, '<input type="text" name="email"')

    def test_should_contain_invite_email_submit(self):
        self.assertContains(self.response, '<button type="submit"')
        self.assertContains(self.response, 'Invite person</button>')


class VIM_BoardMemberMixin(VIM_CoreBoardMemberMixin, GeneralBoardMemberMixin):
    def setUp(self):
        super(VIM_BoardMemberMixin, self).setUp()


class VIM_GroupLeaderMixin(VIM_CoreBoardMemberMixin, GeneralGroupLeaderMixin):
    def setUp(self):
        super(VIM_GroupLeaderMixin, self).setUp()
