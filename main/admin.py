from django.contrib import admin
from .models import User, Task
from .forms import TaskForm


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'API_key']


class TaskAdmin(admin.ModelAdmin):
    form = TaskForm
    list_display = ('from_city', 'to_city', 'start_date_local')
    list_display_links = ('from_city', 'to_city',)

    def get_form(self, request, obj=None, **kwargs):
        print(self.exclude)
        self.exclude = (None,)
        print(self.exclude)
        return super(TaskAdmin, self).get_form(request, obj=None, **kwargs)


admin.site.register(User, UserAdmin)
admin.site.register(Task, TaskAdmin)
