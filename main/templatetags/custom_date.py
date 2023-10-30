from django import template
from datetime import datetime
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def fromisoformat(value):
    """Convert an ISO 8601 formatted string (e.g., "2023-10-30T15:45:00Z") to a Python datetime object."""
    return datetime.fromisoformat(value)
