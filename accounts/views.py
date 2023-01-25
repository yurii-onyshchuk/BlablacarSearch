import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, DeleteView
from . import forms
from .models import User


class UserSignUp(CreateView):
    extra_context = {'title': 'Реєстрація'}
    template_name = 'accounts/signup.html'
    form_class = forms.UserSignUpForm

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


class PersonalCabinet(LoginRequiredMixin, TemplateView):
    extra_context = {'title': 'Особистий кабінет',
                     'subtitle': 'Керуйте своїми особистими даними та безпекою акаунту'}
    template_name = 'accounts/personal_cabinet/personal_cabinet.html'


class PersonalInfoUpdateView(LoginRequiredMixin, UpdateView):
    extra_context = {'title': 'Особисті дані',
                     'subtitle': 'Керуйте своїми особистими та контактними даними'}
    template_name = 'accounts/personal_cabinet/personal_info.html'
    form_class = forms.UserSettingForm

    def get_queryset(self):
        return User.objects.filter(username=self.request.user)

    def get_success_url(self):
        messages.success(self.request, 'Особисті дані успішно змінено!')
        return reverse_lazy('personal_cabinet')


class PersonalSafetyView(LoginRequiredMixin, TemplateView):
    extra_context = {'title': 'Безпека облікового запису',
                     'subtitle': 'Змінити пароль або видалити обліковий запис'}
    template_name = 'accounts/personal_cabinet/personal_safety.html'


class DeleteAccount(LoginRequiredMixin, DeleteView):
    extra_context = {'title': 'Видалення облікового запису'}

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get_success_url(self):
        messages.success(self.request, 'Акаунт успішно видалено!')
        return reverse_lazy('login')


class APIQuotaView(TemplateView):
    extra_context = {'title': 'Ліміт API-запитів',
                     'subtitle': 'Перевірити ліміт та залишок доступних запитів до серверу BlaBlaCar'}
    template_name = 'accounts/personal_cabinet/personal_quota.html'

    def get_context_data(self, **kwargs):
        context = super(APIQuotaView, self).get_context_data()
        url = f'{settings.BASE_BLABLACAR_API_URL}?key={User.objects.get(username=self.request.user).API_key}'
        response = requests.get(url)
        context['quota'] = {'limit_day': response.headers['x-ratelimit-limit-day'],
                            'remaining_day': response.headers['x-ratelimit-remaining-day'],
                            'limit_minute': response.headers['x-ratelimit-limit-minute'],
                            'remaining_minute': response.headers['x-ratelimit-remaining-minute'], }
        return context
