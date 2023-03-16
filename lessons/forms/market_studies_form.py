from django import forms
from lessons.models import MarketStudies
import datetime


class MarketStudiesForm(forms.ModelForm):

    class Meta:
        model = MarketStudies
        fields = '__all__'
        # fields = ('operator',)
        labels = {
            'title': 'Palabras clave',
            'created_at': 'Creado en',
            'budgeted_hours': 'Código',
            'client': 'Cliente',
            'created_by': 'Responsable',
            'study_type': 'Tipo de estudio',
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
