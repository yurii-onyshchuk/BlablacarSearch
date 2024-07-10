from django import forms


class CityAutocompleteWidget(forms.TextInput):
    """Custom widget for rendering an input field with autocomplete."""

    template_name = 'main/widgets/city_input_widget.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['data_prefix'] = attrs.get('id', '')
        return context


class InputGroupWidget(CityAutocompleteWidget):
    """Custom widget for rendering an input field with an input group."""

    template_name = 'main/widgets/input-group.html'
