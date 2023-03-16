from django import forms
from lessons.models import ConnectionStudies
import datetime


class ConnectionStudiesForm(forms.ModelForm):

    class Meta:
        model = ConnectionStudies
        # fields = '__all__'
        fields = (
            'title',
            'created_at',
            'budgeted_hours',
            'client',
            'created_by',
            'zone',
            'operator',
            'area',
            'lesson_type',
            'subcategory',
            'description',
            'action_plan',
            'file'
        )
        labels = {
            'title': 'Palabras clave',
            'created_at': 'Creado en',
            'budgeted_hours': 'Código',
            'client': 'Cliente',
            'created_by': 'Responsable',
            'zone': 'Zona',
            'operator': 'Operador',
            'area': 'Área',
            'lesson_type': 'Tipo de lección',
            'subcategory': 'Subcategoría',
            'description': 'Descripción',
            'action_plan': 'Plan de acción propuesto',
            'file': 'Archivo'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['created_by'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)
        self.fields['created_at'].widget.attrs['readonly'] = True
        now = datetime.datetime.now()
        self.fields['created_at'].widget.attrs['value'] = now.strftime('%d/%m/%Y')
