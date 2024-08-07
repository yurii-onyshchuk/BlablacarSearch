from django.urls import reverse_lazy

from accounts.services.user_service import get_user_API_key
from . import forms
from .services.external_api_services import BlaBlaCarService
from .services.task_service import TaskChecker


class TaskSaveMixin:
    """Mixin for saving tasks."""

    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        """Handle the form submission for creating or updating a task."""

        blablacar = BlaBlaCarService(form.cleaned_data)
        query_params = blablacar.get_query_params_for_searching()
        response_data = blablacar.send_api_request(query_data=query_params, method='GET').json()
        form.instance.link = response_data['link']
        form.instance.user = self.request.user
        task = form.save(commit=True)
        TaskChecker(task, response_data).update_saved_trips()
        return super().form_valid(form)


class TaskFormRetrieveMixin:
    """Mixin for determining the form class based on user's API key."""

    def get_form_class(self):
        """Get the appropriate form class based on user's API key."""

        user_api_key = get_user_API_key(self.request.user)
        if user_api_key:
            return forms.TaskProForm
        else:
            return forms.TaskForm

    def get_form_kwargs(self):
        """Pass user to the form."""

        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class FormRetrieveMixin(TaskFormRetrieveMixin):
    """Mixin for selecting the form class for searching or creating tasks."""

    def get_form_class(self):
        """Get the form class based on the use case(search or create task)."""

        if self.request.POST.get('create_task', None):
            return super().get_form_class()
        else:
            return forms.SearchForm
