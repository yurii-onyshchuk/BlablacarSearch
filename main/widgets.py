from django import forms


class InputGroupWidget(forms.TextInput):
    template_name = 'main/widgets/input-group.html'
