from django import forms
from django.utils.translation import gettext as _
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from groups.models import SportsGroup, Membership, Board
from accounts.models import User
from forms.models import BoardChange


class BoardChangeForm(forms.Form):
    president_email = forms.CharField(max_length=100, validators=[validate_email])
    president_name = forms.CharField(max_length=100, disabled=True, required=False)

    vice_president_email = forms.CharField(max_length=100, validators=[validate_email])
    vice_president_name = forms.CharField(max_length=100, disabled=True, required=False)

    cashier_email = forms.CharField(max_length=100, validators=[validate_email])
    cashier_name = forms.CharField(max_length=100, disabled=True, required=False)

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug') if 'slug' in kwargs else ''
        self.group = self.slug

        super(BoardChangeForm, self).__init__(*args, **kwargs)

    def get_group(self):
        """ Returns the sportsgroup object if it exists, else raise validation error """

        if isinstance(self.group, 'groups.models.SportsGroup'):
            return
        try:
            self.group = SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            raise ValidationError(_('Group does not exist'))

    @staticmethod
    def get_user(group, email):
        """ Returns the user object if it exists and is part of the group,
            else raise validation error """

        try:
            user = User.objects.get(email=email)
            try:
                Membership.objects.get(person=user, group=group)
            except Membership.DoesNotExist:
                raise ValidationError(
                    _('{} does not belong to {}'.format(user.get_full_name(), group)))
        except User.DoesNotExist:
            if email:
                raise ValidationError(_("{} not found".format(email)))
            else:
                raise ValidationError(_("This email does not exist in the database"))

        return user if user else None

    def clean(self):
        cleaned_data = super(BoardChangeForm, self).clean()

    def clean_president_email(self):
        """ Magic django function that is called along with form.is_Valid() in the view-file
            Atempts to set the president based on the president_email input field
        """
        self.get_group()  # Make sure the group exists before continuing

        try:
            self.president = self.get_user(self.group, self.cleaned_data["president_email"])
        except KeyError:
            raise ValidationError(_("The president email field is empty"))

    def clean_vice_president_email(self):
        """ Magic django function that is called along with form.is_Valid() in the view-file
            Atempts to set the vice president based on the vice_president_email input field
        """
        self.get_group()  # Make sure the group exists before continuing

        try:
            self.vice_president = self.get_user(
                self.group, self.cleaned_data["vice_president_email"])
        except KeyError:
            raise ValidationError(_("The vice president email field is empty"))

    def clean_cashier_email(self):
        """ Magic django function that is called along with form.is_Valid() in the view-file
            Atempts to set the cashier based on the cashier input field
        """
        self.get_group()  # Make sure the group exists before continuing

        try:
            self.cashier = self.get_user(self.group, self.cleaned_data["cashier_email"])
        except KeyError:
            raise ValidationError(_("The cashier email field is empty"))

    def create_model(self):
        if (self.president and self.vice_president and self.cashier):
            old_president = Board.objects.get(sports_group=self.group).president

            model = BoardChange.create(self.group, old_president,
                                       self.president, self.vice_president, self.cashier)

            if old_president == self.president:
                model.vice_president_approved = False

            if model not in BoardChange.objects.all():
                model.save()
