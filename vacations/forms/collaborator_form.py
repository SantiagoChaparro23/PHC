from django import forms
from vacations.models import Collaborator
# from django.core.exceptions import ValidationError


class CollaboratorForm(forms.ModelForm):

    class Meta:
        model = Collaborator
        fields = ('user', 'entry_at', 'id_card', 'salary', 'state')
        labels = {
            'user': 'Colaborador',
            'entry_at': 'Fecha ingreso',
            'id_card': 'Cédula',
            'salary': 'Salario',
            'state': 'Estado'
        }


    def __init__(self, *args, **kwargs):
        super(CollaboratorForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.attrs['class'] = 'select2'
