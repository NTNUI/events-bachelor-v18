from django import template

register = template.Library()


@register.filter
def member(value, arg):
    html = ''
    groups = []
    for group in value.get(arg):
        html += '<div class="group-member-name">' + group + '</div>'
        groups.append(group)

    return html
