from . import forms
from .models import APIKey


def get_task_form(user):
    if APIKey.objects.get(user=user).API_key:
        return forms.TaskProForm
    else:
        return forms.TaskForm


class TaskFormMixin:
    def get_form_class(self):
        return get_task_form(self.request.user)


class SearchFormMixin:
    def get_form_class(self):
        if self.request.POST.get('add_to_task', None):
            return get_task_form(self.request.user)
        else:
            return forms.SearchForm
