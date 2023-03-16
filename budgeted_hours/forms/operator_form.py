from django import forms
from budgeted_hours.models import Operator
from django.core.exceptions import ValidationError


class OperatorForm(forms.ModelForm):

    class Meta:
        model = Operator
        fields = ('operator',)
        labels = {
            'operator': 'Operador'
        }


    # def clean(self):
    #     cleaned_data = super().clean()

    #     activity = cleaned_data.get('activity')
    #     pk = self.instance.pk

    #     item = EnergyAnalysis.objects.filter(activity=activity).exclude(pk=pk).exists()

    #     if item:
    #         raise forms.ValidationError('Ya existe una actividad con este nombre')
