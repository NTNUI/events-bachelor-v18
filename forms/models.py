from django.db import models
from accounts.models import User
from groups.models import SportsGroup, Board


class FormDoc(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=150)

    def __str__(self):
        return self.name


class BoardChange(models.Model):
    name = models.CharField(default="Board Change Form", max_length=100)

    group = models.ForeignKey(SportsGroup, related_name="group")
    old_president = models.ForeignKey(User, related_name="old_president")
    old_president_approved = models.BooleanField(default=False)

    president = models.ForeignKey(User, related_name='president')
    president_approved = models.BooleanField(default=False)

    vice_president = models.ForeignKey(User, related_name='vice_president')
    vice_president_approved = models.BooleanField(default=True)

    cashier = models.ForeignKey(User, related_name='cashier')

    @classmethod
    def create(cls, g, op, p, vp, c):  # pylint: disable=too-many-arguments
        board_change = cls(group=g, old_president=op, president=p, vice_president=vp, cashier=c)

        return board_change

    def __str__(self):
        return "----------------------------------------\n\
Board change form for: {}\n\
- Old President: {}\n\
- President: {}\n\
- Vice President: {}\n\
- Cashier: {}\n\
----------------------------------------".format(
            self.group, self.old_president, self.president, self.vice_president, self.cashier)

    def __eq__(self, other):
        if self.old_president != other.old_president:
            return False
        if self.group != other.group:
            return False
        if self.president != other.president:
            return False
        if self.vice_president != other.vice_president:
            return False
        if self.cashier != other.cashier:
            return False
        return True

    def __contains__(self, other):
        if self.old_president == other:
            return True
        if self.president == other:
            return True
        if self.vice_president == other:
            return True
        if self.cashier == other:
            return True
        return False

    def needs_approval_from(self):
        """ Returns a list of users needed to approve the form """
        approval = []
        if not self.old_president_approved:
            approval.append(self.old_president)
        if not self.president_approved:
            approval.append(self.president)
        if not self.vice_president_approved:
            approval.append(self.vice_president)

        return list(set(approval))

    def approve(self, user):
        """ Saves approvals """
        if user == self.old_president:
            self.old_president_approved = True
        # If the old president and the new are the same, this ensures both are validated
        if user == self.president:
            self.president_approved = True
        if user == self.vice_president:
            self.vice_president_approved = True

        # Save the above changes to form
        self.save()

        if (self.old_president_approved
            and self.president_approved
                and self.vice_president_approved):
            self.change_board()

    def change_board(self):
        new_board = Board.create(self.president,
                                 self.vice_president,
                                 self.cashier,
                                 self.group)

        new_board.save()
        self.group.active_board = new_board
        self.group.save()
