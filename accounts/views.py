import requests
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, DeleteView
from . import forms
from .models import User


class UserRegister(CreateView):
    extra_context = {'title': 'Реєстрація'}
    template_name = 'accounts/register.html'
    form_class = forms.UserRegisterForm

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return redirect('index')


class UserAuthentication(LoginView):
    extra_context = {'title': 'Вхід'}
    template_name = 'accounts/login.html'
    form_class = forms.UserAuthenticationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('index')


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
    template_name = 'accounts/settings.html'
    form_class = forms.UserSettingForm
    success_url = reverse_lazy('index')

    def get_queryset(self):
        return User.objects.filter(username=self.request.user)


class DeleteAccount(LoginRequiredMixin, DeleteView):
    extra_context = {'title': 'Видалення облікового запису'}
    success_url = reverse_lazy('login')

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)
