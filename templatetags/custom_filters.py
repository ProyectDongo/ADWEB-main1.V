from django import template

register = template.Library()

@register.filter(name='mul')
def mul(value, arg):
    return value * arg

@register.filter(name='div')
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ZeroDivisionError, ValueError, TypeError):
        return 0.0