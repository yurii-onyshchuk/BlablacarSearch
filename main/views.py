from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from . import forms


class UserRegister(CreateView):
    extra_context = {'title': 'Реєстрація'}
    template_name = 'register.html'
    form_class = forms.UserRegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('task_list')


class UserAuthentication(LoginView):
    extra_context = {'title': 'Вхід'}
    template_name = 'login.html'
    form_class = forms.UserAuthenticationForm
    success_url = reverse_lazy('task_list')


class TaskList(TemplateView):
    extra_context = {'title': 'Головна'}
    template_name = 'index.html'
