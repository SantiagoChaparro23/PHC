from django import forms
from imports.models import Metric
from django.core.exceptions import ValidationError


class MetricForm(forms.ModelForm):

    class Meta:
        model = Metric
        fields = ('metric', 'format', 'name_table')
        labels = {
            'metric': 'Métrica',
            'format': 'Formato',
            'name_table': 'Tabla',
        }


    def clean(self):
        cleaned_data = super().clean()

        metric = cleaned_data.get('metric')
        pk = self.instance.pk

        item = Metric.objects.filter(metric=metric).exclude(pk=pk).exists()

        if item:
            raise forms.ValidationError('Ya existe una métrica con este nombre')
