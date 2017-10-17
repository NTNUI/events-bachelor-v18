from django import forms
from django.core.validators import validate_email
from groups.models import SportsGroup, Membership
from accounts.models import User


class BaseForm(forms.Form):
    #group = forms.CharField(max_length=100, disabled=True, required=False)

    # make sure to get the slug
    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug') if 'slug' in kwargs else ''
        self.group = self.slug

        super(BaseForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(BaseForm, self).clean()
        print("I'm only using the first method...!")


class BoardChangeForm(BaseForm):
    leader_email = forms.CharField(max_length=100, validators=[validate_email])
    leader_name = forms.CharField(max_length=100, disabled=True, required=False)

    second_leader_email = forms.CharField(max_length=100, validators=[validate_email])
    second_leader_name = forms.CharField(max_length=100, disabled=True, required=False)

    treasurer_email = forms.CharField(max_length=100, validators=[validate_email])
    treasurer_name = forms.CharField(max_length=100, disabled=True, required=False)

    def __init__(self, *args, **kwargs):
        super(BoardChangeForm, self).__init__(*args, **kwargs)

    def get_group(self):
        try:
            return SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            return None

    @staticmethod
    def is_member(user, group):
        try:
            Membership.objects.get(person=user, group=group)
        except Membership.DoesNotExist:
            raise forms.ValidationError(
                'The user connected to this email is not a member of {}'.format(group.name))

    def clean_email(self):
        group = self.get_group()

        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            user = User.objects.get(email=email)
            print(user.first_name)
            self.is_member(user, group)
        except User.DoesNotExist:
            # Raise exception if email is not in use
            raise forms.ValidationError(
                'This email address is not connected to a user')
