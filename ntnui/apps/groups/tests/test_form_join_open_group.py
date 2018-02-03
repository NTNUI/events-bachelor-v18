from django.test import TestCase
from django.core.urlresolvers import reverse
from ..forms import JoinOpenGroupForm
from accounts.models import User
from ..models import SportsGroup, Invitation


class JoinOpenGroupFormTest(TestCase):
    fixtures = ['users.json', 'groups.json',
                'memberships.json', 'invitations.json', 'boards.json']

    def setUp(self):
        self.USER_IS_MEMBER = User.objects.get(email='todd.packer@online.com')
        self.USER_IS_NOT_MEMBER = User.objects.get(email='meredith.palmer@dundermifflin.com')
        self.USER_IS_INVITED = User.objects.get(email='ryan.the.fireguy@hotmail.com')

    def test_should_throw_if_no_group_slug(self):
        form = JoinOpenGroupForm(slug='', user=self.USER_IS_NOT_MEMBER)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, ['Invalid group.'])

    def test_should_throw_if_user_is_already_member(self):
        form = JoinOpenGroupForm(slug='friidrett', user=self.USER_IS_MEMBER)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, [
            'This user is already a member of this group.'])

    def test_invitation_should_be_gone_after_joining(self):
        # We know that ryan.the.fireguy@hotmail.com is already invited
        form = JoinOpenGroupForm(slug='friidrett', user=self.USER_IS_INVITED)
        self.assertTrue(form.is_valid())
        membership = form.save()
        group = SportsGroup.objects.get(slug='friidrett')

        # Check that ryan is a member now
        self.assertEqual(membership.person, self.USER_IS_INVITED)
        self.assertEqual(membership.group, group)
        # Check that the invitation is gone
        try:
            no_inv = Invitation.objects.get(person=self.USER_IS_INVITED, group=group)
        except Invitation.DoesNotExist:
            no_inv = None
        self.assertEqual(no_inv, None)

    def test_should_join_group(self):
        form = JoinOpenGroupForm(slug='friidrett', user=self.USER_IS_NOT_MEMBER)
        self.assertTrue(form.is_valid())
        membership = form.save()
        group = SportsGroup.objects.get(slug='friidrett')

        self.assertEqual(membership.person, self.USER_IS_NOT_MEMBER)
        self.assertEqual(membership.group, group)

    def test_should_not_join_closed_group(self):
        form = JoinOpenGroupForm(slug='calisthenics', user=self.USER_IS_MEMBER)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.save(), None)


class OpenGroupViewTest(TestCase):
    fixtures = ['users.json', 'groups.json', 'boards.json']

    def setUp(self):
        self.login_response = self.client.login(email='meredith.palmer@dundermifflin.com',
                                                password='locoloco')
        url = reverse('group_index', kwargs={'slug': 'koiene'})
        self.response = self.client.get(url)

    def test_should_throw_if_no_button_present(self):
        self.assertContains(
            self.response, '<input type="submit" class="btn btn-success" name="join-group')
