from django.urls import reverse_lazy

from accounts.services.user_service import get_user_API_key
from . import forms
from .services.request_service import get_Blablacar_response_data, get_query_params
from .services.task_service import TaskChecker


class TaskEditMixin:
    """Mixin for handling the editing of tasks."""

    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        """Handle the form submission for editing a task."""
        query_params = get_query_params(self.request.user, form.cleaned_data)
        response_data = get_Blablacar_response_data(query_params)
        form.instance.link = response_data['link']
        form.instance.user = self.request.user
        task = form.save(commit=True)
        TaskChecker(task, response_data).update_saved_trips()
        return super().form_valid(form)


class TaskFormMixin:
    """Mixin for determining the form class based on user's API key."""

    def get_form_class(self):
        """Get the appropriate form class based on user's API key."""
        user_api_key = get_user_API_key(self.request.user)
        if user_api_key:
            return forms.TaskProForm
        else:
            return forms.TaskForm


class SearchFormMixin(TaskFormMixin):
    """Mixin for selecting the form class for searching or creating tasks."""

    def get_form_class(self):
        """Get the form class based on the use case(search or create task)."""
        if self.request.POST.get('create_task', None):
            return super().get_form_class()
        else:
            return forms.SearchForm
