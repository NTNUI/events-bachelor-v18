from django import template

register = template.Library()


@register.filter
def member(value, arg):
    groups = []
    for group in value.get(arg):
        groups.append(group)

    return ' '.join(groups)
