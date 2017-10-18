from django import forms
from django.core.validators import validate_email
from groups.models import SportsGroup, Membership
from accounts.models import User


class BaseForm(forms.Form):
    # make sure to get the slug
    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug') if 'slug' in kwargs else ''
        self.group = self.slug

        super(BaseForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(BaseForm, self).clean()

    def perform_actions(self):
        raise NotImplementedError("You have not implemented the \' perform actions \' function")


class BoardChangeForm(BaseForm):
    leader_email = forms.CharField(max_length=100, validators=[validate_email])
    leader_name = forms.CharField(max_length=100, disabled=True, required=False)

    second_leader_email = forms.CharField(max_length=100, validators=[validate_email])
    second_leader_name = forms.CharField(max_length=100, disabled=True, required=False)

    treasurer_email = forms.CharField(max_length=100, validators=[validate_email])
    treasurer_name = forms.CharField(max_length=100, disabled=True, required=False)

    #Fields for storing the users
    form_leader = None
    form_second_leader = None
    form_treasurer = None

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
                    _('Invalid value: %(value) not part of group'),
                            params={'value': email},
                )

    def validate_and_store(self, group, data_field):
        email = self.cleaned_data.get(data_field)

        # Check to see if any users already exist with this email as a username.
        try:
            user = User.objects.get(email=email)
            self.is_member(user, group)

            return user
        except User.DoesNotExist:
            # Raise exception if email is not in use
            raise forms.ValidationError(
                _('Invalid value: %(value)s'),
                        params={'value': email},
            )

        return None

    def clean_leader_email(self):
        group = self.get_group()
        self.form_leader = self.validate_and_store(group, "leader_email")

    def clean_second_leader_email(self):
        group = self.get_group()
        self.form_second_leader = self.validate_and_store(group, "second_leader_email")

    def clean_treasurer_email(self):
        group = self.get_group()
        self.form_treasurer = self.validate_and_store(group, "treasurer_email")

    def perform_actions(self):
        change_group = self.get_group()

        # Make sure all the roles are input before performing a board change
        if (self.form_leader and self.form_second_leader and self.form_treasurer):
            # Perform board change
            change_group.board.president = self.form_leader
            print("New president set: {}".format(
                self.form_leader.first_name + " " + self.form_leader.last_name))

            change_group.board.vice_president = self.form_second_leader
            print("New vice president set: {}".format(
                self.form_second_leader.first_name + " " + self.form_second_leader.last_name))

            change_group.board.cashier = self.form_treasurer
            print("New treasuerer set: {}".format(
                self.form_treasurer.first_name + " " + self.form_treasurer.last_name))

            # Save the board changes
            change_group.board.save()
        else:
            raise forms.ValidationError(
                _('Invalid value: %(value)s'),
                    params={'value': 'Missing board members'}
        )
