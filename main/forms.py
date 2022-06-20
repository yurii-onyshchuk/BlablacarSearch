from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import Task
from .utils import get_city_coordinate


class SearchForm(forms.Form):
    from_city = forms.CharField(label='Звідки?', widget=forms.TextInput(attrs={'class': 'form-control'}))
    to_city = forms.CharField(label='Куди?', widget=forms.TextInput(attrs={'class': 'form-control'}))
    start_date_local = forms.DateTimeField(label='Починаючи з часу', initial=datetime.now(),
                                           widget=forms.DateTimeInput(
                                               attrs={'class': 'form-control', 'type': "datetime-local"},
                                               format="%Y-%m-%dT%H:%M"))
    end_date_local = forms.DateTimeField(label='Закінчуючи часом', required=False,
                                         widget=forms.DateTimeInput(
                                             attrs={'class': 'form-control', 'type': "datetime-local"},
                                             format="%Y-%m-%dT%H:%M"))

    requested_seats = forms.IntegerField(label='Кількість місць', initial=1, min_value=1, max_value=8,
                                         widget=forms.NumberInput(attrs={'class': 'form-control'}))
    radius_in_meters = forms.IntegerField(label='Радіус пошуку, м', required=False, min_value=1, max_value=50000,
                                          widget=forms.NumberInput(attrs={'class': 'form-control'}))

    from_city_coord = None
    to_city_coord = None

    def clean_from_city(self):
        from_city = self.cleaned_data['from_city']
        coordinate = get_city_coordinate(from_city)
        if coordinate:
            self.from_city_coord = coordinate
            return from_city
        else:
            raise ValidationError(f'Міста "{from_city}" не знайдено..')

    def clean_to_city(self):
        to_city = self.cleaned_data['to_city']
        coordinate = get_city_coordinate(to_city)
        if coordinate:
            self.to_city_coord = coordinate
            return to_city
        else:
            raise ValidationError(f'Міста "{to_city}" не знайдено..')

    def clean(self):
        if self.cleaned_data['end_date_local'] and \
                self.cleaned_data['start_date_local'] > self.cleaned_data['end_date_local']:
            raise ValidationError('"Час початку пошуку" має бути раніше "Часу закінчення пошуку": ')

    class Meta:
        fields = ['from_city', 'to_city', 'start_date_local', 'end_date_local', 'requested_seats', 'radius_in_meters']


class TaskForm(SearchForm, forms.ModelForm):
    notification = forms.BooleanField(label='Отримувати сповіщення про нові поїздки', required=False, label_suffix='',
                                      widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = Task
        fields = ['from_city', 'to_city', 'start_date_local', 'end_date_local', 'requested_seats', 'radius_in_meters',
                  'notification']
