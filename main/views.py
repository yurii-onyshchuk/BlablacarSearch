from django.views.generic import CreateView
from django.urls import reverse_lazy
from . import forms


class UserRegister(CreateView):
    extra_context = {'title': 'Реєстрація'}
    template_name = 'register.html'
    form_class = forms.UserRegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('admin')
