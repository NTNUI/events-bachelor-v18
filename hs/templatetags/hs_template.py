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


@register.filter
def role(value, arg):
    html = ''
    print("#################")
    print("#################")
    print(arg)
    print("#################")
    print(value)

    #for group in value.get(arg):
     #   for role in group:
      #      html += '<div class="group-member-role">' + role + '</div>'

    return html
