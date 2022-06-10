from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, FormView, UpdateView
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy
from . import forms
from .models import User
from main.models import Task
import requests


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


class APIQuotaView(TemplateView):
    extra_context = {'title': 'Ліміт API-запитів'}
    template_name = 'quota.html'

    def get_context_data(self, **kwargs):
        context = super(APIQuotaView, self).get_context_data()
        url = f'{Task.base_api_url}{Task.base_search_path}?key={User.objects.get(username=self.request.user).API_key}'
        response = requests.get(url)
        context['quota'] = {'limit_day': response.headers['x-ratelimit-limit-day'],
                            'remaining_day': response.headers['x-ratelimit-remaining-day'],
                            'limit_minute': response.headers['x-ratelimit-limit-minute'],
                            'remaining_minute': response.headers['x-ratelimit-remaining-minute'], }
        return context


class UserSettingsView(LoginRequiredMixin, UpdateView):
    extra_context = {'title': 'Налаштування акаунту'}
    model = User
    template_name = 'settings.html'
    form_class = forms.UserSettingForm
    success_url = reverse_lazy('index')


class ChangePassword(LoginRequiredMixin, PasswordChangeView):
    extra_context = {'title': 'Зміна паролю'}
    template_name = 'password_change.html'
    form_class = forms.UserPasswordChangeForm
