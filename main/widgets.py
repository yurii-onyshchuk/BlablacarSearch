from django import forms


class InputGroupWidget(forms.TextInput):
    """Custom widget for rendering an input field with an input group."""

    template_name = 'main/widgets/input-group.html'
