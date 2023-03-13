import requests

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm
from django.core.exceptions import ValidationError

from accounts.models import APIKey

User = get_user_model()


class UserSignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserSignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'autofocus': False})
        self.fields['email'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def save(self, commit=True):
        data = self.cleaned_data.copy()
        email = data.pop('email')
        password = data.pop('password1')
        data.pop('password2')
        user = User.objects.create_user(email, password, **data)
        return user

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2',)


class UserSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = ''


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = ''


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'autofocus': False})
        self.fields['email'].help_text = ''

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username',)


class APIKeyForm(forms.ModelForm):
    API_key = forms.CharField(help_text=f'Не маєте API ключа? Створіть акаунт на '
                                        f'<a href="https://support.blablacar.com/hc/en-gb/articles/360014200220--How-to-use-BlaBlaCar-search-API-" '
                                        f'target="_blank">BlaBlaCar API</a>', label='API ключ', required=False)

    class Meta:
        model = APIKey
        fields = ['API_key', ]

    def clean_API_key(self):
        API_key = self.cleaned_data['API_key']
        if API_key != '':
            response = requests.get(settings.BLABLACAR_API_URL, {'key': API_key})
            if not response.status_code == 400:
                raise ValidationError('Вказаний API-ключ не дійсний')
        return API_key
