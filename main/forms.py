from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime
from .widgets import InputGroupWidget
from .models import Task
from main.utils import get_city_coordinate


class SearchForm(forms.ModelForm):
    key = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}), required=False)
    from_city = forms.CharField(label='Звідки?', widget=InputGroupWidget())
    to_city = forms.CharField(label='Куди?', widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'to_city'}))
    from_coordinate = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}), required=False)
    to_coordinate = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}), required=False)
    start_date_local = forms.DateTimeField(label='Починаючи з часу', initial=datetime.now(),
                                           widget=forms.DateTimeInput(
                                               attrs={'class': 'form-control', 'type': "datetime-local"},
                                               format="%Y-%m-%dT%H:%M"))
    end_date_local = forms.DateTimeField(label="Закінчуючи часом (не обов'язково)", required=False,
                                         widget=forms.DateTimeInput(
                                             attrs={'class': 'form-control', 'type': "datetime-local"},
                                             format="%Y-%m-%dT%H:%M"))
    requested_seats = forms.IntegerField(label='Кількість місць', initial=1, min_value=1, max_value=8,
                                         widget=forms.NumberInput(attrs={'class': 'form-control'}))
    radius_in_kilometers = forms.IntegerField(label="Радіус пошуку навколо вказаних міст, км (не обов'язково)",
                                              required=False, min_value=1, max_value=50,
                                              widget=forms.NumberInput(attrs={'class': 'form-control'}))
    radius_in_meters = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}), required=False,
                                       empty_value=None)
    locale = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}), initial='uk-UA', required=False)
    currency = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}), initial='UAH', required=False)

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

    def clean_radius_in_kilometers(self):
        radius_in_kilometers = self.cleaned_data['radius_in_kilometers']
        if radius_in_kilometers:
            self.cleaned_data['radius_in_meters'] = radius_in_kilometers * 1000
        return radius_in_kilometers

    def clean(self):
        clean_data = super(SearchForm, self).clean()
        if clean_data['end_date_local'] and clean_data['start_date_local'] > clean_data['end_date_local']:
            raise ValidationError('"Час початку пошуку" має бути раніше "Часу закінчення пошуку": ')

    def get_query_params(self):
        query_params = {}
        query_params_key = ['key', 'from_coordinate', 'to_coordinate', 'start_date_local', 'end_date_local',
                            'requested_seats', 'radius_in_meters', 'locale', 'currency']
        for key in query_params_key:
            value = self.cleaned_data[key]
            if key == 'start_date_local':
                value = value.isoformat()
            if key == 'end_date_local' and value:
                value = value.isoformat()
            query_params[key] = value
        query_params['count'] = 100
        return query_params

    class Meta:
        model = Task
        fields = ['from_coordinate', 'to_coordinate', 'from_city', 'to_city', 'start_date_local', 'end_date_local',
                  'requested_seats', 'radius_in_meters', 'radius_in_kilometers']


class TaskForm(SearchForm):
    notification = forms.BooleanField(label='Отримувати сповіщення про нові поїздки', required=False, label_suffix='',
                                      widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    only_from_city = forms.BooleanField(label='Не шукати міста поблизу', required=False,
                                        label_suffix='',
                                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    only_to_city = forms.BooleanField(label='Не шукати міста поблизу', required=False,
                                      label_suffix='',
                                      widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta(SearchForm.Meta):
        fields = ['from_coordinate', 'to_coordinate', 'from_city', 'only_from_city', 'to_city', 'only_to_city',
                  'start_date_local', 'end_date_local', 'requested_seats', 'radius_in_meters', 'radius_in_kilometers',
                  'notification']
