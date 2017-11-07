from rules import predicate, add_perm
from .models import Membership


@predicate
def is_group_member(user, group):
    return user in group.members.all()


@predicate
def is_group_board_member(user, group):
    try:
        membership = group.membership_set.get(person=user)
        return membership.in_board
    except Membership.DoesNotExist:
        return False


@predicate
def is_group_leader(user, group):
    try:
        return group.board.president == user
    except AttributeError:
        return False


@predicate
def is_group_vp(user, group):
    try:
        return group.board.vice_president == user
    except AttributeError:
        return False


@predicate
def is_group_cashier(user, group):
    try:
        return group.board.cashier == user
    except AttributeError:
        return False


add_perm('groups.can_see_board', is_group_member)
add_perm('groups.can_see_forms', is_group_member)
add_perm('groups.can_see_members', is_group_board_member)
add_perm('groups.can_see_settings', is_group_member)
add_perm('groups.can_see_group_settings', is_group_leader | is_group_vp)
add_perm('groups.can_see_invitations', is_group_board_member)
add_perm('groups.can_invite_member', is_group_leader | is_group_vp)
add_perm('groups.can_leave_group', (~is_group_leader  # pylint:disable=invalid-unary-operand-type # noqa
                                    & ~is_group_vp  # pylint:disable=invalid-unary-operand-type # noqa
                                    & ~is_group_cashier)  # pylint:disable=invalid-unary-operand-type # noqa
         & is_group_member)
