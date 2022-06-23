from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, SetPasswordForm
from .models import User


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Ім'я")
    last_name = forms.CharField(label='Прізвище')
    username = forms.CharField(label="Ім'я користувача")
    API_key = forms.CharField(label='API ключ',
                              help_text=f'Не маєте API ключа? Створіть акаунт на '
                                        f'<a href="https://support.blablacar.com/hc/en-gb/articles/360014200220--How-to-use-BlaBlaCar-search-API-" '
                                        f'target="_blank">BlaBlaCar API</a>')
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Підтвердження паролю', widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus': False})

        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'API_key', 'email', 'password1', 'password2']


class UserAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Ім'я користувача")
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(UserAuthenticationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'


class UserSettingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus': False})

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'API_key')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'API_key': forms.TextInput(attrs={'class': 'form-control'})
        }
        help_texts = {'username': ''}


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старий пароль:", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label="Новий пароль:", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label="Новий пароль (підтвердження):",
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='Новий пароль:',
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": 'form-control'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label='Підтвердіть пароль:',
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": 'form-control'}),
    )
