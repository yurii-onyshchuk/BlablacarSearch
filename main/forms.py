from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError

from .models import Task
from .widgets import InputGroupWidget, CityAutocompleteWidget


class SearchForm(forms.Form):
    """Form for collecting search criteria for BlaBlaCar trips."""

    from_city = forms.CharField(label='Звідки?', widget=InputGroupWidget(attrs={'autocomplete': 'off'}))
    from_coordinate = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}), required=False)
    to_city = forms.CharField(label='Куди?', widget=CityAutocompleteWidget(attrs={'autocomplete': 'off'}))
    to_coordinate = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}), required=False)
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
        """Clean and validate the 'from_city' field."""
        from_city = self.cleaned_data['from_city']
        coordinate = self.data['from_coordinate']
        if coordinate:
            return from_city
        else:
            raise ValidationError(f'Міста "{from_city}" не знайдено..')

    def clean_to_city(self):
        """Clean and validate the 'to_city' field."""
        to_city = self.cleaned_data['to_city']
        coordinate = self.data['to_coordinate']
        if coordinate:
            return to_city
        else:
            raise ValidationError(f'Міста "{to_city}" не знайдено..')

    def clean(self):
        """Custom cleaning and validation logic for the entire form."""
        clean_data = super(SearchForm, self).clean()
        if clean_data['end_date_local'] and clean_data['start_date_local'] > clean_data['end_date_local']:
            raise ValidationError('"Час початку пошуку" має бути раніше "Часу закінчення пошуку": ')


class TaskForm(SearchForm, forms.ModelForm):
    """Form for creating or updating a Task."""

    only_from_city = forms.BooleanField(label='Ігнорувати міста поблизу', required=False, label_suffix='')
    only_to_city = forms.BooleanField(label='Ігнорувати міста поблизу', required=False, label_suffix='')

    class Meta:
        model = Task
        fields = ['from_coordinate', 'to_coordinate', 'from_city', 'only_from_city', 'to_city', 'only_to_city',
                  'start_date_local', 'end_date_local', 'requested_seats', 'radius_in_kilometers', ]


class TaskProForm(TaskForm):
    """Form for creating or updating a Task with additional option: notification."""

    notification = forms.BooleanField(label='Отримувати сповіщення про нові поїздки', required=False, label_suffix='')

    class Meta:
        model = Task
        fields = ['from_coordinate', 'to_coordinate', 'from_city', 'only_from_city', 'to_city', 'only_to_city',
                  'start_date_local', 'end_date_local', 'requested_seats', 'radius_in_kilometers', 'notification', ]
