from django.conf import settings

from accounts.models import APIKey


def get_user_API_key(user):
    try:
        user_api_key = APIKey.objects.get(user=user).API_key
        if user_api_key:
            return user_api_key
    except APIKey.DoesNotExist:
        return None


def get_API_key(user):
    user_api_key = get_user_API_key(user)
    if user_api_key:
        return user_api_key
    else:
        return settings.BLABLACAR_API_KEY
