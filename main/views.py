import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, FormView

from .mixins import FormRetrieveMixin, TaskFormRetrieveMixin, TaskSaveMixin
from .models import Task
from .services.external_api_services import BlaBlaCarService, NovaPoshtaGeoService
from .services.task_service import TaskChecker, get_actual_user_tasks, get_archived_user_tasks


class SearchPage(LoginRequiredMixin, TaskSaveMixin, FormRetrieveMixin, FormView):
    """View for the BlaBlaCar trip search page.

    This view allows authenticated users to search for BlaBlaCar trips based on various criteria.
    Users can search for trips and view the results.
    """

    extra_context = {'title': 'Пошук поїздок', 'heading': 'Куди їдемо?'}
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        """Get the context data for rendering the page.

        This method retrieves the context data required for rendering the search page.
        If there are query parameters in the kwargs, it initiates a request to check for the availability
        of corresponding trips, which are then included in the context with the trip search form.
        When no query parameters are provided, only the trip search form is displayed.
        """
        context = super(SearchPage, self).get_context_data(**kwargs)
        if 'query_params' in kwargs:
            context['title'] = 'Доступні поїздки'
            context['heading'] = 'Пошук'
            context['show_results'] = True
            context['response_data'] = BlaBlaCarService().send_api_request(query_data=kwargs['query_params'],
                                                                           method='GET').json()
        return context

    def form_valid(self, form):
        """Handle the form submission and rendering results or creating a new task."""

        if self.request.POST.get('search', None):
            query_params = BlaBlaCarService(form.cleaned_data).get_query_params_for_searching()
            return self.render_to_response(self.get_context_data(form=form, query_params=query_params))
        elif self.request.POST.get('create_task', None):
            return super().form_valid(form)


class TaskList(LoginRequiredMixin, ListView):
    """List view for planned trips"""

    extra_context = {'title': 'Заплановані поїздки'}

    def get_queryset(self):
        return get_actual_user_tasks(user=self.request.user)


class TaskListArchive(LoginRequiredMixin, ListView):
    """List view for archived trips"""

    extra_context = {'title': 'Архівовані поїздки', 'task_list_archive': True}
    template_name = 'main/task_list_archive.html'

    def get_queryset(self):
        return get_archived_user_tasks(user=self.request.user)


class TaskDetail(LoginRequiredMixin, DetailView):
    """Detail view for a single task."""

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """Get the context data for rendering the task detail page.

        This method retrieves the context data required for rendering the task detail page.
        It includes detailed information about the selected task and updates information
        about the available trips based on the task's criteria.

        Returns:
            dict: A dictionary containing the context data for rendering the page.
        """
        context = super(TaskDetail, self).get_context_data(**kwargs)
        blablacar = BlaBlaCarService(self.object.__dict__)
        query_params = blablacar.get_query_params_for_searching()
        response_data = blablacar.send_api_request(query_data=query_params, method='GET').json()
        task_checker = TaskChecker(self.object, response_data)
        task_checker.update_saved_trips()
        context['response_data'] = task_checker.filter_response_accord_to_task()
        context['title'] = 'Деталі поїздки'
        return context


class CreateTask(LoginRequiredMixin, TaskFormRetrieveMixin, TaskSaveMixin, CreateView):
    """View for creating a new task."""

    extra_context = {'title': 'Планування нової поїздки'}
    template_name = 'main/task_form.html'


class TaskUpdate(LoginRequiredMixin, TaskFormRetrieveMixin, TaskSaveMixin, UpdateView):
    """View for updating an existing task."""

    extra_context = {'title': 'Оновлення поїздки'}

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class DeleteTask(LoginRequiredMixin, DeleteView):
    """View for deleting an existing task."""

    extra_context = {'title': 'Видалення поїздки'}
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


def city_autocomplete(request):
    """ Handle city autocomplete requests.

    This view function processes POST requests for city autocomplete queries.
    It uses the NovaPoshtaGeoService to search for cities based on the provided query
    and returns a sorted and limited list of results.
    """

    if request.method == 'POST':
        data = json.loads(request.body)
        searcher = NovaPoshtaGeoService({'query': data.get('query')})
        query_data = searcher.get_query_params()
        autocomplete_data = searcher.send_api_request(query_data=query_data, method='POST').json()
        sorted_data = sorted(autocomplete_data['data'],
                             key=lambda x: (x.get('SettlementTypeDescription') != 'місто', x.get('Description')))
        limited_data = sorted_data[:10]
        return JsonResponse({'success': True, 'data': limited_data}, safe=False)
    else:
        raise Http404()
