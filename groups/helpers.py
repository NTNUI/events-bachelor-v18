from .rules import is_group_leader, is_group_vp, is_group_board_member, is_group_member

def get_group_role(user, group):
    if is_group_leader(user, group):
        return "President"
    if is_group_vp(user, group):
        return "Vice President"
    if is_group_board_member(user, group):
        return "Board Member"
    if is_group_member(user, group):
        return "Member"
    return "Not a member"
