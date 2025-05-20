from django import template
from datetime import datetime

register = template.Library()

@register.filter
def month_name(month_num):
    return datetime(2025, month_num, 1).strftime('%B')

@register.filter
def range_filter(value):
    return range(value)