from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm

User = get_user_model()


class UserSignUpForm(UserCreationForm):
    API_key = forms.CharField(help_text=f'Не маєте API ключа? Створіть акаунт на '
                                        f'<a href="https://support.blablacar.com/hc/en-gb/articles/360014200220--How-to-use-BlaBlaCar-search-API-" '
                                        f'target="_blank">BlaBlaCar API</a>', label='API ключ', )

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
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'API_key',)


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
        fields = ('first_name', 'last_name', 'email', 'username', 'API_key')
