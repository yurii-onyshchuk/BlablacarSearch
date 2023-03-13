import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, FormView

from . import forms, utils
from .mixins import SearchFormMixin, TaskFormMixin
from .models import Task, Trip, APIKey


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


class APIKeyView(FormView):
    extra_context = {'title': 'Особистий API-ключ',
                     'subtitle': 'Встановити особистий API-ключ, перевірити ліміт та залишок доступних запитів до '
                                 'серверу BlaBlaCar'}
    template_name = 'accounts/personal_cabinet/personal_api_key.html'
    form_class = forms.APIKeyForm
    success_url = reverse_lazy('personal_cabinet')

    def get_context_data(self, **kwargs):
        context = super(APIKeyView, self).get_context_data()
        user_API_key = utils.get_user_API_key(self.request.user)
        if user_API_key:
            context['form'].initial['API_key'] = user_API_key
            url = f'{settings.BLABLACAR_API_URL}?key={APIKey.objects.get(user=self.request.user).API_key}'
            response = requests.get(url)
            context['quota'] = {'limit_day': response.headers['x-ratelimit-limit-day'],
                                'remaining_day': response.headers['x-ratelimit-remaining-day'],
                                'limit_minute': response.headers['x-ratelimit-limit-minute'],
                                'remaining_minute': response.headers['x-ratelimit-remaining-minute'], }
        return context

    def form_valid(self, form):
        API_key = form.cleaned_data['API_key']
        APIKey.objects.update_or_create(user=self.request.user, defaults={'API_key': API_key})
        if API_key:
            messages.success(self.request, 'API-ключ успішно оновлено!')
        else:
            Task.objects.filter(user=self.request.user).update(notification=False)
            messages.warning(self.request,
                             'API-ключ не встановлено! Ви не зможете отримувати сповіщення про нові поїздки.')
        return super(APIKeyView, self).form_valid(form)
