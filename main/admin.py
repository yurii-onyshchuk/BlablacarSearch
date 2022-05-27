from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import User, Task
from .forms import TaskForm


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'API_key']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'start_date_local', 'end_date_local', 'requested_seats', 'radius_in_meters',
                    'user', 'id', 'URL')
    list_display_links = ('from_city', 'to_city',)
    readonly_fields = ('URL',)

    def URL(self, obj):
        return mark_safe(f'<a href="{obj.get_url()}">{obj.get_url()}</a>')
