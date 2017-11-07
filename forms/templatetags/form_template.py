from django import template

register = template.Library()


@register.filter
def filterTitle(value):
    # Email is the first part for each section, so make sure you add a title only before that
    if value.endswith("email"):
        return '<div class="form-fill-row-title">' + value.replace('_email', '').title().replace('_', ' ') + '</div>'


@register.filter
def filterType(fieldname):
    if fieldname.endswith("_email"):
        return "email"
    if fieldname.endswith("_name"):
        return "text"
    return ""


@register.filter
def filterLabel(fieldname):
    if fieldname.endswith("_name"):
        return "Name:"

    return {
        "president_email": "President email:",
        "vice_president_email": "Vice President email:",
        "cashier_email": "Cashier email:",
    }.get(fieldname, '')


@register.filter
def filterPlaceholder(fieldname):
    if fieldname.endswith("_email"):
        return "Email"
    return ""


@register.filter
def isDisabled(field):
    if 'disabled' in str(field):
        return 'disabled'

    return ''


@register.filter(name='addAttributes')
def addAttributes(field, css):
    attrs = {}
    definition = css.split(',')

    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            t, v = d.split(':')
            attrs[t] = v
    return field.as_widget(attrs=attrs)


@register.filter
def add(fieldname, string):
    return fieldname + string


@register.filter
def printForm(form):
    print(form.name)
    return ''


@register.filter
def getBoardFields(fieldname):
    return {
        "president_name": True,
        "vice_president_name": True,
        "cashier_name": True,
    }.get(fieldname, False)


@register.filter
def getApprovals(form):
    return form.needs_approval_from()
