from django.contrib import admin
from django.contrib.auth import get_user_model

from accounts.models import APIKey

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin configuration for the User model.

    Defines the display fields and links for the User model in the admin panel.
    """

    list_display = ['email', 'username', 'first_name', 'last_name', 'slug', ]
    list_display_links = ['email', ]


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin configuration for the APIKey model.

    Defines the display fields for the APIKey model in the admin panel.
    """

    list_display = ('user', 'API_key',)
