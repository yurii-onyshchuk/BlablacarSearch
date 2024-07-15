from django.conf import settings

from accounts.models import APIKey


def get_user_API_key(user):
    """Retrieve the API key associated with a user.

    This function checks if the user has set a personal API key in their account and returns it. If no personal API key
    is set, it returns None.
    """
    try:
        user_api_key = APIKey.objects.get(user=user).API_key
        if user_api_key:
            return user_api_key
    except APIKey.DoesNotExist:
        return None


def get_API_key(user):
    """Get the API key for a user.

    This function checks if the user has a personal API key set.
    If a personal API key is set, it is returned. If not, the default API key from settings is used.
    """
    user_api_key = get_user_API_key(user)
    if user_api_key:
        return user_api_key
    else:
        return settings.BLABLACAR_API_KEY
