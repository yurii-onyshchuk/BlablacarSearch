from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, FormView
from .models import Task, Trip, User
from . import forms, utils


class HomePage(LoginRequiredMixin, FormView):
    extra_context = {'title': 'Пошук поїздок', 'heading': 'Куди їдемо?'}
    template_name = 'main/index.html'
    form_class = forms.SearchForm

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        if 'query_params' in kwargs:
            context['show_trips'] = True
            context['title'] = 'Доступні поїздки'
            context['heading'] = 'Пошук'
            context['trip_list'] = utils.get_trip_list_from_api(kwargs['query_params'])
        return context

    def form_valid(self, form):
        if self.request.POST.get('search', None):
            form.cleaned_data['key'] = User.objects.get(username=self.request.user).API_key
            query_params = form.get_query_params()
            return self.render_to_response(self.get_context_data(form=form, query_params=query_params))
        elif self.request.POST.get('save', None):
            task = form.save(commit=False)
            task.user = self.request.user
            if self.request.POST.get('notification', False):
                task.notification = True
            if self.request.POST.get('only_from_city', False):
                task.only_from_city = True
            if self.request.POST.get('only_to_city', False):
                task.only_to_city = True
            task.save()
            utils.Checker(task).update_data_at_db()
            return redirect('task_list')


class CreateTask(LoginRequiredMixin, CreateView):
    extra_context = {'title': 'Планування нової поїздки'}
    template_name = 'main/task_form.html'
    form_class = forms.TaskForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateTask, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.object.pk})


class TaskList(LoginRequiredMixin, ListView):
    extra_context = {'title': 'Заплановані поїздки'}

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskDetail(LoginRequiredMixin, DetailView):
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TaskDetail, self).get_context_data(**kwargs)
        context['title'] = 'Деталі поїздки'
        utils.Checker(self.object).update_data_at_db()
        context['trip_list'] = Trip.objects.filter(task=self.object)
        return context


class TaskUpdate(LoginRequiredMixin, UpdateView):
    extra_context = {'title': 'Оновлення поїздки'}
    form_class = forms.TaskForm

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
