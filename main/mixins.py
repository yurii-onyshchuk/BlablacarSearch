from . import forms
from accounts.utils import get_user_API_key


def get_task_form(user):
    user_api_key = get_user_API_key(user)
    if user_api_key:
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
