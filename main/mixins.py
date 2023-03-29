from django.urls import reverse_lazy

from . import forms
from accounts.utils import get_user_API_key
from .services.request_service import get_Blablacar_response_data, get_query_params
from .services.task_service import TaskChecker


class TaskEditMixin:
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        query_params = get_query_params(self.request.user, form.cleaned_data)
        response_data = get_Blablacar_response_data(query_params)
        form.instance.link = response_data['link']
        form.instance.user = self.request.user
        task = form.save(commit=True)
        filtered_response_data = TaskChecker(task, response_data).response_filter_accord_to_task()
        TaskChecker(task, filtered_response_data).update_saved_trips()
        return super().form_valid(form)


class TaskFormMixin:
    def get_form_class(self):
        user_api_key = get_user_API_key(self.request.user)
        if user_api_key:
            return forms.TaskProForm
        else:
            return forms.TaskForm


class SearchFormMixin(TaskFormMixin):
    def get_form_class(self):
        if self.request.POST.get('create_task', None):
            return super().get_form_class()
        else:
            return forms.SearchForm
