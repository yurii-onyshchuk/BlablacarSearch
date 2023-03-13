from django import template

from accounts.utils import get_user_API_key

register = template.Library()


@register.simple_tag
def available_user_API_key(user):
    return get_user_API_key(user)
