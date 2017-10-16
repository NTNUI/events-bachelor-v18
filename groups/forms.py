from django import forms
from django.core.validators import validate_email
from accounts.models import User
from .models import SportsGroup, Invitation, Membership


class NewInvitationForm(forms.Form):
    email = forms.CharField(max_length=100, validators=[validate_email])

    # make sure to get the slug
    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug') if 'slug' in kwargs else ''
        self.inviter = kwargs.pop('user') if 'user' in kwargs else None
        super(NewInvitationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewInvitationForm, self).clean()
        self.validate_group()
        # Validate that you can only submit this form as group leader or vp
        self.validate_user_can_invite_members()


    def validate_user_can_invite_members(self):
        if self.inviter == None:
            self.add_error(None, "No user supplied.")
        elif not self.inviter.has_perm('groups.can_invite_member', self.get_group()):
            self.add_error(None, 'You can not invite members.')

    def validate_not_already_invited(self):
        # check if we find the user, and he is a member
        try:
            invitation = Invitation.objects.get(
                person=self.user, group=self.group)
            raise forms.ValidationError('This user is already invited.')
        except Invitation.DoesNotExist:
            return

    def validate_not_already_member(self):
        try:
            membership = Membership.objects.get(
                person=self.user, group=self.group)
            raise forms.ValidationError(
                'This user is already a member of this group.')
        except Membership.DoesNotExist:
            return


    def validate_group(self):
        try:
            SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            self.add_error(None, "Invalid group.")

    def get_group(self):
        try:
            return SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            return None

    def clean_email(self):
        # Clean group as here to avoid double work
        self.group = self.get_group()

        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            self.user = User.objects.get(email=email)
            self.validate_not_already_invited()
            self.validate_not_already_member()
        except User.DoesNotExist:
            # Raise exception if email is not in use
            raise forms.ValidationError(
                'This email address is not connected to a user.')

    def save(self):
        return Invitation.objects.create(person=self.user, group=self.group)


class SettingsForm(forms.Form):
    public = forms.BooleanField(required=False)

    # make sure to get the slug
    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug') if 'slug' in kwargs else ''
        super(SettingsForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(SettingsForm, self).clean()
        self.validate_group()

    def clean_public(self):
        self.group = self.get_group()

        if self.group is None:
            return

        # Get the public flag
        self.group.public = self.cleaned_data.get('public')
        self.group.save()

    def get_group(self):
        try:
            return SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            return None

    def validate_group(self):
        try:
            return SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            self.add_error(None, "Invalid group")
