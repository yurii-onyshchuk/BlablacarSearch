from django import template

from accounts.services.user_service import get_user_API_key

register = template.Library()


@register.simple_tag
def available_user_API_key(user):
    """Get the available API key for a user.

    This template tag retrieves the available API key for the specified user. If the user has set a personal API key
    in their account, it is returned. If no personal API key is set, None is returned.
    """
    return get_user_API_key(user)
