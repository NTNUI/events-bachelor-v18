from django import template
from hs.models import HSMembership

register = template.Library()


@register.assignment_tag
def user_in_hs(user):
    try:
        HSMembership.objects.get(person=user)
        return True
    except HSMembership.DoesNotExist:
        return False
