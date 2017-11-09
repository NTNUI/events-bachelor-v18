from django.db import models
from django.conf import settings
import datetime
import os


def get_thumbnail_upload_to(instance, filename):
    return os.path.join(
        "thumbnail/{}".format(instance.slug), filename)


def get_cover_upload_to(instance, filename):
    return os.path.join(
        "cover_photo/{}".format(instance.slug), filename)


class SportsGroup(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=12)
    description = models.TextField(max_length=200)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='Membership', related_name='group_members')
    invitations = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='Invitation', related_name='group_invitations')
    requests = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='Request', related_name='group_requests')
    public = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to=get_thumbnail_upload_to, default='thumbnail/ntnui2.svg')
    cover_photo = models.ImageField(upload_to=get_cover_upload_to,
                                    default='cover_photo/ntnui-volleyball.png')

    # Store the currently active board
    active_board = models.ForeignKey('Board', related_name='active_board',
                                     null=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        super(SportsGroup, self).save(*args, **kwargs)
        self.update()  # Make sure you update the members AFTER the new board has been saved

    # Update all members of the
    def update(self):
        for mem in Membership.objects.filter(group=self):
            mem.save()

    def __str__(self):
        return self.name

    def __contains__(self, other):
        if other in self.members.all():
            return True
        return False


class Board(models.Model):
    president = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='board_president')
    vice_president = models.ForeignKey(
        settings.AUTH_USER_MODEL,  related_name='board_vp')
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='board_cashier')
    sports_group = models.ForeignKey(
        SportsGroup, related_name='sports_group', on_delete=models.CASCADE)

    def __str__(self):
        return "Board of {}: {} - {} - {}".format(
            self.sports_group.name, self.president, self.vice_president, self.cashier)

    def __contains__(self, other):
        if self.president == other:
            return True
        if self.vice_president == other:
            return True
        if self.cashier == other:
            return True
        return False

    @classmethod
    def create(cls, president, vice_president, cashier, sports_group):
        board = cls(
            president=president,
            vice_president=vice_president,
            cashier=cashier,
            sports_group=sports_group)

        return board


class Membership(models.Model):
    person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(SportsGroup, on_delete=models.CASCADE)
    date_joined = models.DateField(default=datetime.date.today)
    paid = models.BooleanField(default=False)
    role = models.CharField(max_length=50, default="member")
    comment = models.CharField(max_length=140, blank=True)

    # Update the membership fields based on the person's role in the group
    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        if self.group.active_board.president == self.person:
            self.role = "president"
        elif self.group.active_board.vice_president == self.person:
            self.role = "vice_president"
        elif self.group.active_board.cashier == self.person:
            self.role = "cashier"
        else:
            self.role = "member"

        # TODO Add model to allow other roles than the above (like Chief of Material)
        super(Membership, self).save(*args, **kwargs)


class Invitation(models.Model):
    person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(SportsGroup, on_delete=models.CASCADE)
    date_issued = models.DateField(auto_now_add=True)


class Request(models.Model):
    person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(SportsGroup, on_delete=models.CASCADE)
    date_issued = models.DateField(auto_now_add=True)
