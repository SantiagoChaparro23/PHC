from django import forms
from budgeted_hours.models import Softwares
from django.core.exceptions import ValidationError


class SoftwaresForm(forms.ModelForm):

    class Meta:
        model = Softwares
        fields = ('software',)
        labels = {
            'software': 'Software'
        }


    def clean(self):
        cleaned_data = super().clean()

        software = cleaned_data.get('software')
        pk = self.instance.pk

        item = Softwares.objects.filter(software=software).exclude(pk=pk).exists()

        if item:
            raise forms.ValidationError('Ya existe una actividad con este nombre')
