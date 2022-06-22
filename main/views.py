from django.conf import settings
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView, TemplateView, DeleteView, FormView
from . import forms
from .models import Task, Trip, User
from .utils import Checker, Parser, TripDeserializer, get_response


class HomePage(LoginRequiredMixin, FormView):
    template_name = 'main/index.html'
    form_class = forms.SearchForm

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context['title'] = 'Пошук поїздок'
        context['heading'] = 'Куди їдемо?'
        if 'api_url' in kwargs:
            context['show_trips'] = True
            context['title'] = 'Доступні поїздки'
            context['heading'] = 'Пошук'
            response = get_response(kwargs['api_url'])
            parser = Parser(response.json())
            trip_list = parser.get_trips_list()
            trip_info_list = [parser.get_trip_info(trip) for trip in trip_list]
            trip_list = [TripDeserializer(trip_info) for trip_info in trip_info_list]
            context['trip_list'] = trip_list
        return context

    def form_valid(self, form):
        if 'search' in self.request.POST:
            api_url = f'{settings.BASE_BLABLACAR_API_URL}?' \
                      f'key={User.objects.get(username=self.request.user).API_key}&' \
                      f'from_coordinate={form.from_city_coord}&' \
                      f'to_coordinate={form.to_city_coord}&' \
                      f'locale=uk-UA&' \
                      f'currency=UAH&' \
                      f'start_date_local={self.request.POST.get("start_date_local")}&' \
                      f'requested_seats={self.request.POST.get("requested_seats")}&' \
                      f'count=100'
            if self.request.POST.get('end_date_local'):
                api_url += f'&end_date_local={self.request.POST.get("end_date_local")}'
            if self.request.POST.get('radius_in_meters'):
                api_url += f'&radius_in_meters={self.request.POST.get("radius_in_meters")}'
            return self.render_to_response(self.get_context_data(form=form, api_url=api_url))
        elif 'save' in self.request.POST:
            task = form.save(commit=False)
            task.user = self.request.user
            task.from_coordinate = form.from_city_coord
            task.to_coordinate = form.to_city_coord
            if 'notification' in self.request.POST:
                task.notification = True
            task.save()
            return redirect('task_list')


class CreateTask(LoginRequiredMixin, CreateView):
    extra_context = {'title': 'Планування нової поїздки'}
    template_name = 'main/task_form.html'
    form_class = forms.TaskForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.from_coordinate = form.from_city_coord
        form.instance.to_coordinate = form.to_city_coord
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
        Checker(self.object).get_suitable_trips()
        context['trip_list'] = Trip.objects.filter(task=self.object, departure_time__gt=datetime.now())
        return context


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = forms.TaskForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.from_coordinate = form.from_city_coord
        form.instance.to_coordinate = form.to_city_coord
        Trip.objects.filter(task=self.object).delete()
        return super(TaskUpdate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TaskUpdate, self).get_context_data(**kwargs)
        context['title'] = 'Оновлення поїздки'
        context['url'] = Task.objects.get(user=self.request.user, pk=self.kwargs['pk']).get_url()
        return context

    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.kwargs['pk']})


class DeleteTask(LoginRequiredMixin, DeleteView):
    extra_context = {'title': 'Видалення поїздки'}
    model = Task
    success_url = reverse_lazy('task_list')
