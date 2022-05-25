from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Task


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Ім'я")
    last_name = forms.CharField(label='Прізвище')
    username = forms.CharField(label="Ім'я користувача")
    API_key = forms.CharField(label='API ключ',
                              help_text='Не маєте API ключа? Створи акаунт на Develompent BlaBlaCar API')
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Підтвердження паролю', widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus': False})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'API_key', 'email', 'password1', 'password2']


class UserAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Ім'я користувача")
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        exclude = ['user', ]
