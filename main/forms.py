from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError

from .models import Task, APIKey
from .widgets import InputGroupWidget
from .utils import get_city_coordinate


class SearchForm(forms.Form):
    from_city = forms.CharField(label='Звідки?', widget=InputGroupWidget())
    to_city = forms.CharField(label='Куди?')
    start_date_local = forms.DateTimeField(label='Починаючи з часу', initial=datetime.now(),
                                           widget=forms.DateTimeInput(attrs={'type': "datetime-local"},
                                                                      format="%Y-%m-%dT%H:%M"))
    end_date_local = forms.DateTimeField(label="Закінчуючи часом (не обов'язково)", required=False,
                                         widget=forms.DateTimeInput(attrs={'type': "datetime-local"},
                                                                    format="%Y-%m-%dT%H:%M"))
    requested_seats = forms.IntegerField(label='Кількість місць', initial=1, min_value=1, max_value=8)
    radius_in_kilometers = forms.IntegerField(label="Радіус пошуку навколо вказаних міст, км (не обов'язково)",
                                              required=False, min_value=1, max_value=50)

    def clean_from_city(self):
        from_city = self.cleaned_data['from_city']
        coordinate = get_city_coordinate(from_city)
        if coordinate:
            self.cleaned_data['from_coordinate'] = coordinate
            return from_city
        else:
            raise ValidationError(f'Міста "{from_city}" не знайдено..')

    def clean_to_city(self):
        to_city = self.cleaned_data['to_city']
        coordinate = get_city_coordinate(to_city)
        if coordinate:
            self.cleaned_data['to_coordinate'] = coordinate
            return to_city
        else:
            raise ValidationError(f'Міста "{to_city}" не знайдено..')

    def clean(self):
        clean_data = super(SearchForm, self).clean()
        if clean_data['end_date_local'] and clean_data['start_date_local'] > clean_data['end_date_local']:
            raise ValidationError('"Час початку пошуку" має бути раніше "Часу закінчення пошуку": ')


class TaskForm(SearchForm, forms.ModelForm):
    from_coordinate = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}), required=False)
    to_coordinate = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}), required=False)
    radius_in_meters = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}), required=False,
                                       empty_value=None)
    only_from_city = forms.BooleanField(label='Ігнорувати міста поблизу', required=False, label_suffix='')
    only_to_city = forms.BooleanField(label='Ігнорувати міста поблизу', required=False, label_suffix='')
    notification = forms.BooleanField(label='Отримувати сповіщення про нові поїздки', required=False, label_suffix='')

    def clean_radius_in_kilometers(self):
        radius_in_kilometers = self.cleaned_data['radius_in_kilometers']
        if radius_in_kilometers:
            self.cleaned_data['radius_in_meters'] = radius_in_kilometers * 1000
        return radius_in_kilometers

    class Meta:
        model = Task
        fields = ['from_coordinate', 'to_coordinate', 'radius_in_meters',
                  'from_city', 'only_from_city', 'to_city', 'only_to_city', 'start_date_local', 'end_date_local',
                  'requested_seats', 'radius_in_kilometers', 'notification', ]


class APIKeyForm(forms.ModelForm):
    API_key = forms.CharField(help_text=f'Не маєте API ключа? Створіть акаунт на '
                                        f'<a href="https://support.blablacar.com/hc/en-gb/articles/360014200220--How-to-use-BlaBlaCar-search-API-" '
                                        f'target="_blank">BlaBlaCar API</a>', label='API ключ', )

    class Meta:
        model = APIKey
        fields = ['API_key', ]
