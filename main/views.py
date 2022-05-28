from django.views.generic import CreateView, ListView, UpdateView, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from . import forms
from .models import Task


class UserRegister(CreateView):
    extra_context = {'title': 'Реєстрація'}
    template_name = 'register.html'
    form_class = forms.UserRegisterForm
    success_url = reverse_lazy('task_list')


class UserAuthentication(LoginView):
    extra_context = {'title': 'Вхід'}
    template_name = 'login.html'
    form_class = forms.UserAuthenticationForm
    success_url = reverse_lazy('task_list')


class HomePage(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'


class CreateTask(LoginRequiredMixin, CreateView):
    extra_context = {'title': 'Додати нове завдання'}
    form_class = forms.TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.from_coordinate = form.from_city_coord
        form.instance.to_coordinate = form.to_city_coord
        return super(CreateTask, self).form_valid(form)


class TaskList(LoginRequiredMixin, ListView):
    extra_context = {'title': 'Головна'}
    template_name = 'task_list.html'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    extra_context = {'title': 'Деталі завдання'}
    model = Task
    form_class = forms.TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('task_list')

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
