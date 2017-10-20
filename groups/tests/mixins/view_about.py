from django.core.urlresolvers import reverse
from django.urls import resolve
from groups import views as group_views


class VA_CoreMemberMixin(object):

    def test_view_function(self):
        view = resolve('/groups/volleyball')
        self.assertEquals(view.func, group_views.group_index)

    def test_has_description(self):
        self.assertContains(self.response, 'About NTNUI Volleyball')
        self.assertContains(
            self.response, 'NTNUI Volleyball is one of the largest groups within NTNUI')

    def test_total_count_board_members(self):
        self.assertContains(self.response, '<div class="group-member-name"', 3)
