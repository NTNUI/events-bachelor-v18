from django.test import TestCase
from django.utils.timezone import localtime, now
from ..forms import NewInvitationForm
from ntnui.models import User
from ..models import SportsGroup, Invitation


class InvitationFormTest(TestCase):
    fixtures = ['users.json', 'groups.json',
                'memberships.json', 'invitations.json']

    def test_form_has_right_fields(self):
        form = NewInvitationForm(slug='volleyball')
        expected = ['email']
        self.assertSequenceEqual(expected, list(form.fields))

    def test_should_throw_if_no_group_slug(self):
        form = NewInvitationForm(data={}, slug='')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), ['Invalid group.'])

    def test_should_throw_if_no_email_provided(self):
        form = NewInvitationForm(data={}, slug='volleyball')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['This field is required.'])

    def test_should_throw_if_email_not_in_database(self):
        form = NewInvitationForm(
            data={'email': 'random-email@random.com'}, slug='volleyball')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], [
                         'This email address is not connected to a user.'])

    def test_should_throw_if_email_is_already_member(self):
        form = NewInvitationForm(
            data={'email': 'todd.packer@online.com'}, slug='volleyball')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], [
                         'This user is already a member of this group.'])

    def test_should_throw_if_email_is_already_invited(self):
        # We know that ryan.the.fireguy@hotmail.com is already invited
        form = NewInvitationForm(
            data={'email': 'ryan.the.fireguy@hotmail.com'}, slug='volleyball')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], [
                         'This user is already invited.'])

    def test_should_create_a_new_invitation_on_save(self):
        form = NewInvitationForm(
            data={'email': 'meredith.palmer@dundermifflin.com'}, slug='volleyball'
        )
        self.assertTrue(form.is_valid())
        invitation = form.save()
        person = User.objects.get(email='meredith.palmer@dundermifflin.com')
        group = SportsGroup.objects.get(slug='volleyball')
        self.assertEqual(invitation.person, person)
        self.assertEqual(invitation.group, group)
        self.assertEqual(invitation.date_issued, now().date())
