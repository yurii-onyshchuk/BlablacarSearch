from django.shortcuts import redirect
from django.views.generic import CreateView, ListView, UpdateView, DetailView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from . import forms
from .models import Task, Trip
from .utils import Checker
from datetime import datetime


class HomePage(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        return redirect('task_list')


class CreateTask(LoginRequiredMixin, CreateView):
    extra_context = {'title': 'Пошук поїздок'}
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
    extra_context = {'title': 'Заплановані поїздки'}
    template_name = 'task_list.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskDetail(LoginRequiredMixin, DetailView):
    extra_context = {'title': 'Деталі поїздки'}
    template_name = 'task_detail.html'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(TaskDetail, self).get_context_data(**kwargs)
        Checker(self.object).single_check()
        context['trip_list'] = Trip.objects.filter(task=self.object, departure_time__gt=datetime.now())
        return context


class TaskUpdate(LoginRequiredMixin, UpdateView):
    extra_context = {'title': 'Оновлення поїздки'}
    model = Task
    form_class = forms.TaskForm
    template_name = 'task_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.from_coordinate = form.from_city_coord
        form.instance.to_coordinate = form.to_city_coord
        Trip.objects.filter(task=self.object).delete()
        return super(TaskUpdate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TaskUpdate, self).get_context_data(**kwargs)
        task = Task.objects.get(user=self.request.user, pk=self.kwargs['pk'])
        context['url'] = Task.get_url(task)
        return context

    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.kwargs['pk']})


class DeleteTask(LoginRequiredMixin, DeleteView):
    extra_context = {'title': 'Видалення поїздки'}
    model = Task
    success_url = reverse_lazy('task_list')
