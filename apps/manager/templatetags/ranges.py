from django import template

register = template.Library()

@register.filter
def times(value):
    return range(int(value))
