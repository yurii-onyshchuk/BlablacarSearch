from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, Task
from .utils import get_city_coordinate


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
    def clean_from_city(self):
        from_city = self.cleaned_data['from_city']
        coordinate = get_city_coordinate(from_city)
        if coordinate:
            return from_city
        else:
            raise ValidationError(f'Міста "{from_city}" не знайдено..')

    def clean_to_city(self):
        to_city = self.cleaned_data['to_city']
        coordinate = get_city_coordinate(to_city)
        if coordinate:
            return to_city
        else:
            raise ValidationError(f'Міста "{to_city}" не знайдено..')

    class Meta:
        model = Task
        fields = '__all__'
        exclude = ['user', 'from_coordinate', 'to_coordinate']
