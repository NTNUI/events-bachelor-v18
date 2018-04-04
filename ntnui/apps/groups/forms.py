from django import forms
from django.core.validators import validate_email
from accounts.models import User
from .models import SportsGroup, Invitation, Membership, Request


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
        if self.inviter is None:
            self.add_error(None, "No user supplied.")
        elif not self.inviter.has_perm('groups.can_invite_member', self.get_group()):
            self.add_error(None, 'You can not invite members.')

    def validate_not_already_invited(self):
        # check if we find the user, and he is a member
        try:
            Invitation.objects.get(
                person=self.user, group=self.group)
            raise forms.ValidationError('This user is already invited.')
        except Invitation.DoesNotExist:
            return

    def validate_not_already_member(self):
        try:
            Membership.objects.get(
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
        email = self.cleaned_data.get('email').lower()

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
    description = forms.CharField(required=False, widget=forms.Textarea)
    thumbnail = forms.ImageField(required=False)
    cover_photo = forms.ImageField(required=False)

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

    def set_images(self):
        group = self.get_group()
        thumbnail = self.cleaned_data.get('thumbnail')
        cover_photo = self.cleaned_data.get('cover_photo')
        if thumbnail:
            group.thumbnail = thumbnail
        if cover_photo:
            group.cover_photo = cover_photo
        group.save()

    def set_description(self):
        group = self.get_group()
        description = self.cleaned_data.get('description')
        if description:
            group.description = description
        group.save()


class JoinOpenGroupForm(object):
    def __init__(self, slug, user):
        self.slug = slug
        self.user = user
        self.errors = []
        if self.validate_group():
            self.validate_group_is_public()

        self.validate_not_already_member()

    def is_valid(self):
        return len(self.errors) == 0

    def get_group(self):
        try:
            return SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            return None

    def validate_group(self):
        try:
            return SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            self.errors.append('Invalid group.')

    def validate_group_is_public(self):
        if not self.get_group().public:
            self.errors.append('Group is not public')
        else:
            return

    def validate_not_already_member(self):
        try:
            Membership.objects.get(person=self.user, group=self.get_group())
            self.errors.append("This user is already a member of this group.")
        except Membership.DoesNotExist:
            return

    def delete_invitation_if_exists(self):
        Invitation.objects.filter(group=self.get_group(), person=self.user).delete()

    def save(self):
        self.delete_invitation_if_exists()
        if self.is_valid():
            return Membership.objects.create(person=self.user, group=self.get_group())


class SaveGroupMemberSettingsForm(object):
    def __init__(self, slug, member_id, has_paid, comment):
        self.slug = slug
        self.member_id = member_id
        self.has_paid = has_paid
        self.comment = comment
        self.errors = []
        self.group = None
        self.member = None
        self.validate_paid()
        self.validate_group_is_valid()
        if self.validate_member_is_valid():
            self.validate_member_is_in_group()

    def get_group(self):
        if self.group:
            return self.group
        try:
            group = SportsGroup.objects.get(slug=self.slug)
            self.group = group
            return self.group
        except SportsGroup.DoesNotExist:
            return None

    def get_membership(self):
        if self.member:
            return self.member
        try:
            member = Membership.objects.get(pk=self.member_id)
            self.member = member
            return self.member
        except Membership.DoesNotExist:
            return None

    def save(self):
        if not self.is_valid():
            return
        self.member.comment = self.comment
        self.member.paid = self.has_paid == "paid"
        self.member.save()

    def is_valid(self):
        return len(self.errors) == 0

    def validate(self, condition, message):
        if condition:
            self.errors.append(message)
            return False
        return True

    def validate_paid(self):
        return self.validate(
            self.has_paid != "paid" and self.has_paid != "not-paid",
            'Payment status must be supplied.')

    def validate_comment(self):
        return self.validate(
            not isinstance(self.comment, str) or len(self.commment) > 140,
            'Comment must be 140 characters or less.')

    def validate_group_is_valid(self):
        return self.validate(self.get_group() is None, 'Group does not exist.')

    def validate_member_is_valid(self):
        return self.validate(self.get_membership() is None, 'Membership does not exist.')

    def validate_member_is_in_group(self):
        return self.validate(
            self.get_membership().person not in self.get_group(),
            'This is not a member of this group.'
        )


class KickUserForm(object):
    def __init__(self, slug, member_id):
        self.slug = slug
        self.member_id = member_id
        self.errors = []
        self.group = None
        self.member = None
        self.validate_group_is_valid()
        if self.validate_member_is_valid():
            if self.validate_member_is_in_group():
                self.validate_member_is_not_in_board()

    def save(self):
        if not self.is_valid():
            return
        self.get_membership().delete()

    def is_valid(self):
        return len(self.errors) == 0

    def get_group(self):
        if self.group:
            return self.group
        try:
            group = SportsGroup.objects.get(slug=self.slug)
            self.group = group
            return self.group
        except SportsGroup.DoesNotExist:
            return None

    def get_membership(self):
        if self.member:
            return self.member
        try:
            member = Membership.objects.get(pk=self.member_id)
            self.member = member
            return self.member
        except Membership.DoesNotExist:
            return None

    def validate(self, condition, message):
        if condition:
            self.errors.append(message)
            return False
        return True

    def validate_group_is_valid(self):
        return self.validate(self.get_group() is None, 'Group does not exist.')

    def validate_member_is_valid(self):
        return self.validate(self.get_membership() is None, 'Membership does not exist.')

    def validate_member_is_in_group(self):
        return self.validate(
            self.get_membership().person not in self.get_group(),
            'This is not a member of this group.'
        )

    def validate_member_is_not_in_board(self):
        return self.validate(
            self.get_membership().person in self.get_group().active_board,
            'Board members can not be kicked.'
        )


class WithdrawInvitationForm(object):
    def __init__(self, slug, inv_id):
        self.slug = slug
        self.inv_id = inv_id
        self.errors = []
        self.group = None
        self.invitation = None
        self.validate_group()
        if self.validate_invitation():
            self.validate_invitation_is_for_group()

    def save(self):
        if not self.is_valid():
            return
        self.get_invitation().delete()

    def is_valid(self):
        return len(self.errors) == 0

    def get_group(self):
        if self.group:
            return self.group
        try:
            group = SportsGroup.objects.get(slug=self.slug)
            self.group = group
            return self.group
        except SportsGroup.DoesNotExist:
            return None

    def get_invitation(self):
        if self.invitation:
            return self.invitation
        try:
            invitation = Invitation.objects.get(pk=self.inv_id)
            self.invitation = invitation
            return self.invitation
        except Invitation.DoesNotExist:
            return None

    def validate(self, condition, message):
        if condition:
            self.errors.append(message)
            return False
        return True

    def validate_group(self):
        return self.validate(self.get_group() is None, 'Group does not exist.')

    def validate_invitation(self):
        return self.validate(self.get_invitation() is None, 'Invitation does not exist.')

    def validate_invitation_is_for_group(self):
        return self.validate(
            self.get_invitation().group != self.get_group(),
            'This is not an invitation for this group.'
        )


class JoinPrivateGroupForm(object):
    def __init__(self, slug, user):
        self.slug = slug
        self.user = user
        self.errors = []
        if self.validate_group():
            self.validate_group_is_private()
        self.validate_not_already_member()

    def is_valid(self):
        return len(self.errors) == 0

    def get_group(self):
        try:
            return SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            return None

    def validate_group(self):
        try:
            return SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            self.errors.append('Invalid group.')

    def validate_group_is_private(self):
        if self.get_group().public:
            self.errors.append('Group is not private')
        else:
            return

    def validate_not_already_member(self):
        try:
            Membership.objects.get(person=self.user, group=self.get_group())
            self.errors.append("This user is already a member of this group.")
        except Membership.DoesNotExist:
            return

    def validate_not_already_request(self):
        try:
            Request.objects.get(person=self.user, group=self.get_group())
            self.errors.append("This user has already sent a group request.")
        except Request.DoesNotExist:
            return

    def save(self):
        if self.is_valid():
            return Request.objects.create(person=self.user, group=self.get_group())


class LeaveGroupForm():
    def __init__(self, slug, user):
        self.slug = slug
        self.user = user
        self.errors = []
        if self.validate_group():
            self.validate_user_is_member()

    def is_valid(self):
        return len(self.errors) == 0

    def get_group(self):
        try:
            return SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            return None

    def validate_group(self):
        try:
            return SportsGroup.objects.get(slug=self.slug)
        except SportsGroup.DoesNotExist:
            self.errors.append('Invalid group.')

    def validate_user_is_member(self):
        try:
            Membership.objects.get(person=self.user, group=self.get_group())
        except Membership.DoesNotExist:
            self.errors.append('This user is not a member of this group.')

    def save(self):
        if self.is_valid():
            return Membership.objects.filter(person=self.user, group=self.get_group()).delete()
