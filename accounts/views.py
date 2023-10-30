from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, DeleteView, FormView

from . import forms
from .mixins import RedirectAuthenticatedUserMixin
from .models import APIKey
from .services.user_service import get_user_API_key
from main.models import Task
from main.services.request_service import request_to_Blablacar

User = get_user_model()


class SignUpView(RedirectAuthenticatedUserMixin, CreateView):
    """View for handling the user registration."""

    extra_context = {'title': 'Реєстрація'}
    template_name = 'accounts/signup.html'
    form_class = forms.SignUpForm
    redirect_authenticated_user_url = reverse_lazy('index')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user, backend='accounts.backends.EmailBackend')
            messages.success(self.request, 'Успішна реєстрація!')
        return redirect('index')

    def form_invalid(self, form):
        messages.error(self.request, 'Помилка реєстрації!')
        return super(SignUpView, self).form_invalid(form)


class CustomLoginView(LoginView):
    """View for handling the user login process."""

    extra_context = {'title': 'Вхід'}
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('index')


class PersonalCabinetView(LoginRequiredMixin, TemplateView):
    """View for the user's personal cabinet.

    This view displays the user's personal cabinet with information
    about orders and personal data.
    """

    extra_context = {'title': 'Особистий кабінет',
                     'subtitle': 'Керуйте своїми особистими даними та безпекою акаунту'}
    template_name = 'accounts/personal_cabinet/personal_cabinet.html'


class PersonalInfoUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating the user's personal information."""

    extra_context = {'title': 'Особисті дані',
                     'subtitle': 'Керуйте своїми особистими та контактними даними'}
    template_name = 'accounts/personal_cabinet/personal_info.html'
    form_class = forms.UserForm

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get_success_url(self):
        messages.success(self.request, 'Особисті дані успішно змінено!')
        return reverse_lazy('personal_cabinet')


class PersonalSafetyView(LoginRequiredMixin, TemplateView):
    """View for account safety settings."""

    extra_context = {'title': 'Безпека облікового запису',
                     'subtitle': 'Змінити пароль або видалити обліковий запис'}
    template_name = 'accounts/personal_cabinet/personal_safety.html'


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a user's account."""

    extra_context = {'title': 'Видалення облікового запису'}

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get_success_url(self):
        messages.success(self.request, 'Акаунт успішно видалено!')
        return reverse_lazy('login')


class APIKeyView(FormView):
    """View for managing and setting personal API keys.

    This view allows users to manage their personal API keys associated with their accounts. Users can set or remove
    their API keys and view API usage information such as limits and remaining requests.
    """

    extra_context = {'title': 'Особистий API-ключ',
                     'subtitle': 'Встановити особистий API-ключ, перевірити ліміт та залишок доступних запитів до '
                                 'серверу BlaBlaCar'}
    template_name = 'accounts/personal_cabinet/personal_api_key.html'
    form_class = forms.APIKeyForm
    success_url = reverse_lazy('personal_cabinet')

    def get_context_data(self, **kwargs):
        """Get additional context data to pass to the template.

        This method retrieves the user's API key, sets initial form data,
        and fetches API usage information if an API key is available.
        """
        context = super(APIKeyView, self).get_context_data()
        user_API_key = get_user_API_key(self.request.user)
        if user_API_key:
            context['form'].initial['API_key'] = user_API_key
            response = request_to_Blablacar({'key': user_API_key})
            context['quota'] = {'limit_day': response.headers['x-ratelimit-limit-day'],
                                'remaining_day': response.headers['x-ratelimit-remaining-day'],
                                'limit_minute': response.headers['x-ratelimit-limit-minute'],
                                'remaining_minute': response.headers['x-ratelimit-remaining-minute'], }
        return context

    def form_valid(self, form):
        """Handle the form submission when the API key is set or removed.

        This method is called when the form is submitted. It handles setting or removing the API key based on the form
        data.
        """
        API_key = form.cleaned_data['API_key']
        if API_key:
            APIKey.objects.update_or_create(user=self.request.user, defaults={'API_key': API_key})
            messages.success(self.request, 'API-ключ успішно оновлено!')
        else:
            APIKey.objects.get(user=self.request.user).delete()
            Task.objects.filter(user=self.request.user).update(notification=False)
            messages.warning(self.request,
                             'API-ключ не встановлено! Ви не зможете отримувати сповіщення про нові поїздки.')
        return super(APIKeyView, self).form_valid(form)
