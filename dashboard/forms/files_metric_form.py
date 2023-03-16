from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from imports.models import UrlsFilesMetric

validate = URLValidator()

class UrlsFilesMetricForm(forms.ModelForm):
    url_file = forms.CharField(
        label='Url del archivo',
        validators=[validate]
    )


    class Meta:
        model = UrlsFilesMetric
        fields = ('metric', 'year_file', 'period', 'url_file')
        labels = {
            'url_file': 'Url del archivo',
            'year_file': 'Año correspondiente',
            'period': 'Periodo',
            'metric': 'Metrica'
        }

    def clean(self):
        cleaned_data = super().clean()

        name_file = cleaned_data.get('name_file')

        pk = self.instance.pk

        item = UrlsFilesMetric.objects.filter(name_file=name_file).exclude(pk=pk).exists()

        if item:
            raise forms.ValidationError('Ya existe una métrica con este nombre')

