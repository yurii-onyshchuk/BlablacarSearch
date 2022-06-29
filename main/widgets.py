from django import forms
from django.utils.safestring import mark_safe


class InputGroupWidget(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        """Render base widget and add bootstrap spans"""
        super().render(name, value, attrs, renderer)
        if value:
            value = f'value={value}'
        html = f'''
<span class="input-group">
    <input type="text" name="from_city" {value} class="form-control" id="from_city" required="">
    <button class="btn btn-exchange" type="button"><i class="bi bi-arrow-down-up btn-exchange"></i></button>
</span>
        '''
        return mark_safe(html)
