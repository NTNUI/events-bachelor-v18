from django import forms
from .models import Invitation
from django.core.validators import validate_email
from ntnui.models import User
from .models import SportsGroup, Invitation

class NewInvitationForm(forms.Form):
    email = forms.CharField(max_length=100, validators=[validate_email])

    # make sure to get the slug
    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug') if 'slug' in kwargs else ''
        super(NewInvitationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewInvitationForm, self).clean()
        self.group = self.clean_group()
        self.validate_not_already_invited()
        # TODO: Check that a similair invitation does not exist already
        # one with same person and same group

    def validate_not_already_invited():
        pass

    def clean_group(self):
        groups = SportsGroup.objects.filter(slug=self.slug)
        if (len(groups) != 1):
            self.add_error(None, "Invalid group.")
            return
        return groups[0]

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            self.user = User.objects.get(email=email)
            # TODO: Check if match is already in same group
        except User.DoesNotExist:
            # Raise exception if email is not in use
            raise forms.ValidationError('This email address is not connected to a user.')

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






            self.group = self.get_group()