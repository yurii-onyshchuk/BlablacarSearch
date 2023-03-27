from django import template
from datetime import datetime
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def fromisoformat(value):
    return datetime.fromisoformat(value)
