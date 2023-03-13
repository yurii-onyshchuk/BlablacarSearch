from django.contrib import admin
from django.contrib.auth import get_user_model

from accounts.models import APIKey

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'slug', ]
    list_display_links = ['email', ]


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'API_key',)
