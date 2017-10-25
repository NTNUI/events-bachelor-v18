from django import template

register = template.Library()


@register.filter
def member(value, arg):
    html = ''
    groups = []
    print("############")
    print(arg)
    print(value.get(arg))
    for group in value.get(arg):
        html += '<div class="group-member-name">' + group + '</div>'
        groups.append(group)
    return html


@register.filter
def role(value, arg):
    html = ''

    for group in value.get(arg):
        role = value.get(arg).get(group)

        if role:
            html += '<div class="group-member-role">' + role + '</div>'
        else:
            html += '<div class="group-member-role">Member</div>'
    return html