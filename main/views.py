from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, FormView

from .mixins import SearchFormMixin, TaskFormMixin, TaskEditMixin
from .models import Task
from .services.request_service import get_Blablacar_response_data, get_query_params
from .services.task_service import TaskChecker, get_actual_user_tasks, get_archived_user_tasks


class SearchPage(LoginRequiredMixin, TaskEditMixin, SearchFormMixin, FormView):
    extra_context = {'title': 'Пошук поїздок', 'heading': 'Куди їдемо?'}
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(SearchPage, self).get_context_data(**kwargs)
        if 'query_params' in kwargs:
            response_data = get_Blablacar_response_data(query_params=kwargs['query_params'])
            context['title'] = 'Доступні поїздки'
            context['heading'] = 'Пошук'
            context['show_results'] = True
            context['response_data'] = response_data
        return context

    def form_valid(self, form):
        if self.request.POST.get('search', None):
            query_params = get_query_params(self.request.user, form.cleaned_data)
            return self.render_to_response(self.get_context_data(form=form, query_params=query_params))
        elif self.request.POST.get('create_task', None):
            return super().form_valid(form)


class TaskList(LoginRequiredMixin, ListView):
    extra_context = {'title': 'Заплановані поїздки'}

    def get_queryset(self):
        return get_actual_user_tasks(user=self.request.user)


class TaskListArchive(LoginRequiredMixin, ListView):
    extra_context = {'title': 'Архівовані поїздки', 'task_list_archive': True}
    template_name = 'main/task_list_archive.html'

    def get_queryset(self):
        return get_archived_user_tasks(user=self.request.user)


class TaskDetail(LoginRequiredMixin, DetailView):
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TaskDetail, self).get_context_data(**kwargs)
        response_data = get_Blablacar_response_data(self.object.user, self.object.__dict__)
        filtered_response_data = TaskChecker(self.object, response_data).response_filter_accord_to_task()
        TaskChecker(self.object, filtered_response_data).update_saved_trips()
        context['response_data'] = filtered_response_data
        context['title'] = 'Деталі поїздки'
        return context


class CreateTask(LoginRequiredMixin, TaskFormMixin, TaskEditMixin, CreateView):
    extra_context = {'title': 'Планування нової поїздки'}
    template_name = 'main/task_form.html'


class TaskUpdate(LoginRequiredMixin, TaskFormMixin, TaskEditMixin, UpdateView):
    extra_context = {'title': 'Оновлення поїздки'}

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class DeleteTask(LoginRequiredMixin, DeleteView):
    extra_context = {'title': 'Видалення поїздки'}
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
