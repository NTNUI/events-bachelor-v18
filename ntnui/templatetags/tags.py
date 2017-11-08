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
