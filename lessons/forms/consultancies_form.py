from django import forms
from lessons.models import Consultancies
import datetime


class ConsultanciesForm(forms.ModelForm):

    class Meta:
        model = Consultancies
        # fields = '__all__'
        fields = (
            'title',
            'created_at',
            'budgeted_hours',
            'client',
            'created_by',
            'lesson_type',
            'description',
            'action_plan',
            'file',
        )
        labels = {
            'title': 'Palabras clave',
            'created_at': 'Creado en',
            'budgeted_hours': 'Código',
            'client': 'Cliente',
            'created_by': 'Responsable',
            'lesson_type': 'Tipo de lección',
            'description': 'Descripción',
            'action_plan': 'Plan de acción propuesto',
            'file': 'Archivo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['created_by'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)
        self.fields['created_at'].widget.attrs['readonly'] = True
        now = datetime.datetime.now()
        self.fields['created_at'].widget.attrs['value'] = now.strftime('%d/%m/%Y')
