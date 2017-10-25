from django import template

register = template.Library()


@register.filter
def member(value, arg):
    html = ''
    groups = []

    for group in value.get(arg):
        html += '<div>' + group + '</div>'
        groups.append(group)
    return html


@register.filter
def role(value, arg):
    html = ''

    for group in value.get(arg):
        role = value.get(arg).get(group)

        if role:
            html += '<div>' + role + '</div>'
        else:
            html += '<div>Member</div>'
    return html