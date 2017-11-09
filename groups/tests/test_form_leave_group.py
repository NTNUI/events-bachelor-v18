from django.test import TestCase
from django.core.urlresolvers import reverse
from ..forms import LeaveGroupForm
from accounts.models import User
from ..models import SportsGroup


class LeaveGroupFormTest(TestCase):
    fixtures = ['complete.json']

    def setUp(self):
        self.USER_IS_MEMBER = User.objects.get(email='todd.packer@online.com')
        self.USER_IS_NOT_MEMBER = User.objects.get(email='meredith.palmer@dundermifflin.com')

    def test_should_throw_if_no_group_slug(self):
        form = LeaveGroupForm(slug='', user=self.USER_IS_NOT_MEMBER)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, ['Invalid group.'])

    def test_should_throw_if_user_is_not_member(self):
        form = LeaveGroupForm(slug='friidrett', user=self.USER_IS_NOT_MEMBER)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, [
                         'This user is not a member of this group.'])

    def test_should_leave_group(self):
        form = LeaveGroupForm(slug='friidrett', user=self.USER_IS_MEMBER)
        self.assertTrue(form.is_valid())
        deleted = form.save()

        self.assertEqual(deleted[0], 1)


class LeaveGroupViewTest(TestCase):
    fixtures = ['complete.json']

    def setUp(self):
        self.login_response = self.client.login(email='todd.packer@online.com',
                                                password='locoloco')
        url = reverse('group_settings', kwargs={'slug': 'friidrett'})
        self.response = self.client.get(url)

    def test_should_throw_if_no_button_present(self):
        self.assertContains(self.response, '<input type="submit" name="leave-group')


class LeaveGroupAsPresidentViewTest(TestCase):
    fixtures = ['complete.json']

    def setUp(self):
        self.login_response = self.client.login(email='todd.packer@online.com',
                                                password='locoloco')
        url = reverse('group_settings', kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)

    def test_should_throw_if_button_present_for_leader(self):
        self.assertNotContains(self.response, '<input type="submit" name="leave-group')
