from django import template

register = template.Library()

@register.filter
def name(value):
    if value.endswith("_email"): return "Email:"
    if value.endswith("_name"): return "Name:"
    return ""

@register.filter
def title(value):
    # Email is the first part for each section, so make sure you add a title only before that
    if value.endswith("email"):
        return '<div class="form-fill-row-title">' + value.replace('_email', '').title().replace('_', ' ') + '</div>'
