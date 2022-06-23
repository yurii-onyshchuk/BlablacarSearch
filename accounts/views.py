import requests
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from . import forms
from .models import User


class UserRegister(CreateView):
    extra_context = {'title': 'Реєстрація'}
    template_name = 'accounts/register.html'
    form_class = forms.UserRegisterForm
    success_url = reverse_lazy('task_list')


class UserAuthentication(LoginView):
    extra_context = {'title': 'Вхід'}
    template_name = 'accounts/login.html'
    form_class = forms.UserAuthenticationForm
    success_url = reverse_lazy('task_list')


class APIQuotaView(TemplateView):
    extra_context = {'title': 'Ліміт API-запитів'}
    template_name = 'accounts/quota.html'

    def get_context_data(self, **kwargs):
        context = super(APIQuotaView, self).get_context_data()
        url = f'{settings.BASE_BLABLACAR_API_URL}?key={User.objects.get(username=self.request.user).API_key}'
        response = requests.get(url)
        context['quota'] = {'limit_day': response.headers['x-ratelimit-limit-day'],
                            'remaining_day': response.headers['x-ratelimit-remaining-day'],
                            'limit_minute': response.headers['x-ratelimit-limit-minute'],
                            'remaining_minute': response.headers['x-ratelimit-remaining-minute'], }
        return context


class UserSettingsView(LoginRequiredMixin, UpdateView):
    extra_context = {'title': 'Налаштування акаунту'}
    model = User
    template_name = 'accounts/settings.html'
    form_class = forms.UserSettingForm
    success_url = reverse_lazy('index')
