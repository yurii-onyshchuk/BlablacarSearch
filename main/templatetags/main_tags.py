from django import template

register = template.Library()


@register.filter
def to_kilometers(value):
    """Converts a meters into kilometers"""
    return int(value / 1000)
