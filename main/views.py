from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, FormView
from .models import Task, Trip, User
from . import forms, utils


class HomePage(LoginRequiredMixin, FormView):
    template_name = 'main/index.html'
    form_class = forms.SearchForm

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context['title'] = 'Пошук поїздок'
        context['heading'] = 'Куди їдемо?'
        if 'request_url' in kwargs:
            context['show_trips'] = True
            context['title'] = 'Доступні поїздки'
            context['heading'] = 'Пошук'
            context['trip_list'] = utils.get_trip_list_from_api(kwargs['request_url'])
        return context

    def form_valid(self, form):
        if self.request.POST.get('save', None):
            utils.save_task_to_db(self, form)
            return redirect('task_list')
        else:
            query_params = {
                'from_coordinate': form.from_coordinate,
                'to_coordinate': form.to_coordinate,
                'locale': 'uk-UA',
                'currency': 'UAH',
                'start_date_local': self.request.POST.get("start_date_local"),
                'end_date_local': self.request.POST.get("end_date_local"),
                'requested_seats': self.request.POST.get("requested_seats"),
                'radius_in_kilometers': self.request.POST.get("radius_in_kilometers"),
                'key': User.objects.get(username=self.request.user).API_key,
                'count': '100'}
            return self.render_to_response(
                self.get_context_data(form=form, request_url=utils.get_request_url(**query_params)))


class CreateTask(LoginRequiredMixin, CreateView):
    extra_context = {'title': 'Планування нової поїздки'}
    template_name = 'main/task_form.html'
    form_class = forms.TaskForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.from_coordinate = form.from_coordinate
        form.instance.to_coordinate = form.to_coordinate
        return super(CreateTask, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.object.pk})


class TaskList(LoginRequiredMixin, ListView):
    extra_context = {'title': 'Заплановані поїздки'}

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskDetail(LoginRequiredMixin, DetailView):
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(TaskDetail, self).get_context_data(**kwargs)
        context['title'] = 'Деталі поїздки'
        utils.Checker(self.object).update_data_at_db()
        context['trip_list'] = Trip.objects.filter(task=self.object)
        return context


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = forms.TaskForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.from_coordinate = form.from_coordinate
        form.instance.to_coordinate = form.to_coordinate
        Trip.objects.filter(task=self.object).delete()
        return super(TaskUpdate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TaskUpdate, self).get_context_data(**kwargs)
        context['title'] = 'Оновлення поїздки'
        context['url'] = utils.get_request_url(
            **utils.query_params_from_db_task(Task.objects.get(user=self.request.user, pk=self.kwargs['pk'])))
        return context

    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.kwargs['pk']})


class DeleteTask(LoginRequiredMixin, DeleteView):
    extra_context = {'title': 'Видалення поїздки'}
    model = Task
    success_url = reverse_lazy('task_list')
