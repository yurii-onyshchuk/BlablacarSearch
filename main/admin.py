from django.contrib import admin
from .models import User, Task


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'API_key']


class TaskAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'start_date_local')
    list_display_links = ('from_city', 'to_city',)


admin.site.register(User, UserAdmin)
admin.site.register(Task, TaskAdmin)
