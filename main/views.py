from django.views.generic import CreateView, ListView, UpdateView, DetailView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from . import forms
from .models import Task
from .utils import Checker


class HomePage(LoginRequiredMixin, TemplateView):
    extra_context = {'title': 'Головна'}
    template_name = 'index.html'


class CreateTask(LoginRequiredMixin, CreateView):
    extra_context = {'title': 'Створити новий пошук'}
    form_class = forms.TaskForm
    template_name = 'task_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.from_coordinate = form.from_city_coord
        form.instance.to_coordinate = form.to_city_coord
        return super(CreateTask, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.object.pk})


class TaskList(LoginRequiredMixin, ListView):
    extra_context = {'title': 'Підписки на поїздки'}
    template_name = 'task_list.html'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskDetail(LoginRequiredMixin, DetailView):
    extra_context = {'title': 'Деталі завдання'}
    model = Task
    template_name = 'task_detail.html'

    def get(self, request, *args, **kwargs):
        Checker().check_task(Task.objects.get(pk=self.kwargs['pk']))
        return super(TaskDetail, self).get(request, *args, **kwargs)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    extra_context = {'title': 'Оновлення завдання'}
    model = Task
    form_class = forms.TaskForm
    template_name = 'task_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.from_coordinate = form.from_city_coord
        form.instance.to_coordinate = form.to_city_coord
        return super(TaskUpdate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TaskUpdate, self).get_context_data(**kwargs)
        task = Task.objects.get(user=self.request.user, pk=self.kwargs['pk'])
        context['url'] = Task.get_url(task)
        return context

    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.kwargs['pk']})


class DeleteTask(LoginRequiredMixin, DeleteView):
    extra_context = {'title': 'Видалити задання'}
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = reverse_lazy('task_list')
