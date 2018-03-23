from django import template
from hs.models import MainBoardMembership

register = template.Library()

@register.assignment_tag
def user_in_hs(user):
    try:
        MainBoardMembership.objects.get(person=user)
        return True
    except MainBoardMembership.DoesNotExist:
        return False

@register.filter
def member(value, arg):
    """Returns html div with the given user's groups

    Keyword arguments
    value -- list of dictionaries, containing users, groups and roles
    arg -- a user
    """
    html = ''
    groups = []

    for group in value.get(arg):
        html += '<div>' + group + '</div>'
        groups.append(group)
    return html


@register.filter
def role(value, arg):
    """Returns html div with the given user's group's role

    Keyword arguments
    value -- list of dictionaries, containing users, groups and roles
    arg -- a user
    """
    html = ''

    for group in value.get(arg):
        role = value.get(arg).get(group)

        if role:
            html += '<div>' + role + '</div>'
        else:
            html += '<div>Member</div>'
    return html


