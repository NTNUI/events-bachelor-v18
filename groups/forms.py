from django import forms
from .models import Invitation
from django.core.validators import validate_email
from ntnui.models import User
from .models import SportsGroup, Invitation, Membership

class NewInvitationForm(forms.Form):
    email = forms.CharField(max_length=100, validators=[validate_email])

    # make sure to get the slug
    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug') if 'slug' in kwargs else ''
        super(NewInvitationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewInvitationForm, self).clean()
        self.validate_group()

    def validate_not_already_invited(self):
        # check if we find the user, and he is a member
        try:
            invitation = Invitation.objects.get(person=self.user, group=self.group)
            raise forms.ValidationError('This user is already invited.')
        except Invitation.DoesNotExist:
            return

    def validate_not_already_member(self):
        try:
            membership = Membership.objects.get(person=self.user, group=self.group)
            raise forms.ValidationError('This user is already a member of this group.')
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
            # TODO: Check if match is already in same group
            self.validate_not_already_invited()
            self.validate_not_already_member()
        except User.DoesNotExist:
            # Raise exception if email is not in use
            raise forms.ValidationError('This email address is not connected to a user.')

    def save(self):
        return Invitation.objects.create(person=self.user, group=self.group)
