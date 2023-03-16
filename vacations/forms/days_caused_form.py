from django import forms
from vacations.models import DaysCaused
# from django.core.exceptions import ValidationError


class DaysCausedForm(forms.ModelForm):

    class Meta:
        model = DaysCaused
        fields = ('collaborator', 'days_caused', 'description')
        labels = {
            'collaborator': 'Colaborador',
            'days_caused': 'Días causados',
            'description': 'Descripción'
        }


