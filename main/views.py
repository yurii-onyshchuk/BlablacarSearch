from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, FormView

from . import utils
from .mixins import SearchFormMixin, TaskFormMixin
from .models import Task, Trip


class SearchPage(LoginRequiredMixin, SearchFormMixin, FormView):
    extra_context = {'title': 'Пошук поїздок', 'heading': 'Куди їдемо?'}
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(SearchPage, self).get_context_data(**kwargs)
        if 'query_params' in kwargs:
            context['title'] = 'Доступні поїздки'
            context['heading'] = 'Пошук'
            context['show_trips'] = True
            context['trip_list'] = utils.get_trip_list_from_api(kwargs['query_params'])
        return context

    def form_valid(self, form):
        if self.request.POST.get('search', None):
            query_params = utils.get_query_params(self.request.user, form.cleaned_data)
            return self.render_to_response(self.get_context_data(form=form, query_params=query_params))
        elif self.request.POST.get('add_to_task', None):
            task = form.save(commit=False)
            task.user = self.request.user
            task.save()
            return redirect('task_detail', pk=task.pk)


class CreateTask(LoginRequiredMixin, TaskFormMixin, CreateView):
    extra_context = {'title': 'Планування нової поїздки'}
    template_name = 'main/task_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateTask, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.object.pk})


class TaskList(LoginRequiredMixin, ListView):
    extra_context = {'title': 'Заплановані поїздки'}

    def get_queryset(self):
        return utils.get_actual_user_task(user=self.request.user)


class TaskListArchive(LoginRequiredMixin, ListView):
    extra_context = {'title': 'Архівовані поїздки', 'task_list_archive': True}
    template_name = 'main/task_list_archive.html'

    def get_queryset(self):
        return utils.get_archived_user_task(user=self.request.user)


class TaskDetail(LoginRequiredMixin, DetailView):
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TaskDetail, self).get_context_data(**kwargs)
        context['title'] = 'Деталі поїздки'
        utils.Checker(self.object).update_data_at_db()
        context['trip_list'] = Trip.objects.filter(task=self.object)
        return context


class TaskUpdate(LoginRequiredMixin, TaskFormMixin, UpdateView):
    extra_context = {'title': 'Оновлення поїздки'}

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        Trip.objects.filter(task=self.object).delete()
        return super(TaskUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.kwargs['pk']})


class DeleteTask(LoginRequiredMixin, DeleteView):
    extra_context = {'title': 'Видалення поїздки'}
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', self.success_url)
