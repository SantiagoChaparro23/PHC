from django import forms
from lessons.models import ProtectionCoordinationStudies
import datetime


class ProtectionCoordinationStudiesForm(forms.ModelForm):

    class Meta:
        model = ProtectionCoordinationStudies
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
            'subcategory',
            'subcategory_description',
            'element_type',
            'element_type_description',
            'protection',
            'relay_brand',
            'relay_brand_description',
            'relay_model',
            'file'
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
            'subcategory': 'Subcategoría',
            'subcategory_description': 'Descripción de subcategoría',
            'element_type': 'Tipo de elemento',
            'element_type_description': 'Descripción de elemento',
            'protection': 'Protección',
            'relay_brand': 'Marca de relé',
            'relay_brand_description': 'Descripción relé',
            'relay_model': 'Modelo de relé',
            'file': 'Archivo'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['created_by'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)
        self.fields['created_at'].widget.attrs['readonly'] = True
        now = datetime.datetime.now()
        self.fields['created_at'].widget.attrs['value'] = now.strftime('%d/%m/%Y')
