from django.conf import settings
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView, TemplateView, DeleteView, FormView
from . import forms
from .models import Task, Trip, User
from .utils import Checker, Parser, TripDeserializer, get_response


class HomePage(LoginRequiredMixin, FormView):
    extra_context = {'title': 'Куди їдемо?'}
    form_class = forms.SearchForm
    template_name = 'index.html'

    def form_valid(self, form):
        url = f'{settings.BASE_BLABLACAR_API_URL}?' \
              f'key={User.objects.get(username=self.request.user).API_key}&' \
              f'from_coordinate={form.from_city_coord}&' \
              f'to_coordinate={form.to_city_coord}&' \
              f'locale=uk-UA&' \
              f'currency=UAH&' \
              f'start_date_local={self.request.POST.get("start_date_local")}&' \
              f'requested_seats={self.request.POST.get("requested_seats")}&' \
              f'count=100'
        if self.request.POST.get('end_date_local'):
            url += f'&end_date_local={self.request.POST.get("end_date_local")}'
        if self.request.POST.get('radius_in_meters'):
            url += f'&radius_in_meters={self.request.POST.get("radius_in_meters")}'
        self.request.session['search_url'] = url
        return super(HomePage, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.request.session['form'] = self.request.POST
        return super(HomePage, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('search')


class SearchList(HomePage):
    extra_context = {'title': 'Знайдені поїздки'}
    template_name = 'search_list.html'

    def get_context_data(self, **kwargs):
        context = super(SearchList, self).get_context_data(**kwargs)
        response = get_response(self.request.session['search_url'])
        parser = Parser(response.json())
        trip_list = parser.get_trips_list()
        trip_info_list = [parser.get_trip_info(trip) for trip in trip_list]
        trip_list = [TripDeserializer(trip_info) for trip_info in trip_info_list]
        context['trip_list'] = trip_list
        return context

    def get_initial(self):
        return self.request.session.get('form', self.initial.copy())

    def post(self, request, *args, **kwargs):
        self.request.session['form'] = self.request.POST
        return super(SearchList, self).post(request, *args, **kwargs)


class CreateTask(LoginRequiredMixin, CreateView):
    extra_context = {'title': 'Планування нової поїздки'}
    form_class = forms.TaskForm
    template_name = 'task_create.html'

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
        Checker(self.object).get_suitable_trips()
        context['trip_list'] = Trip.objects.filter(task=self.object, departure_time__gt=datetime.now())
        print(context['trip_list'])
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
