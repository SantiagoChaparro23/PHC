from django import forms
from budgeted_hours.models import BudgetedHours
# from django.core.exceptions import ValidationError


class BudgetedHoursForm(forms.ModelForm):

    class Meta:
        model = BudgetedHours
        fields = (
            'code',
            'client',
            'service_type',
            'start_at',
            'compromise_delivery_at',
            'value',
            'additional_costs',
            'created_by',
            'state',
            'stages',
            'title',
            'description',
            'document_url',
            'duration_deliverables',
            'contract_signed',
            'project_type',
            'project_depends',
            'category_version'
        )
        labels = {
            'code': 'Código',
            'client': 'Cliente',
            'service_type': 'Tipo de servicio',
            'start_at': 'Fecha de inicio proyecto',
            'compromise_delivery_at': 'Fecha comprometida de envio de propuesta',
            'value': 'Valor',
            'additional_costs': 'Costos adicionales',
            'created_by': 'Por',
            'state': 'Estado',
            'stages': 'Etapa',
            'title': 'Título',
            'description': 'Descripción',
            'document_url': 'Link documentos de propuesta',
            'duration_deliverables': 'Duración / Entregables',
            'contract_signed': 'Contrato firmado',
            'project_type': 'Tipo de proyecto',
            'project_depends': 'Inicio del proyecto depende de',
            'category_version': 'Categoría y versión'
        }


    def __init__(self, *args, **kwargs):
        super(BudgetedHoursForm, self).__init__(*args, **kwargs)
        self.fields['client'].widget.attrs['class'] = 'select2'

        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['service_type'].disabled = True

#################################################################


    # # def __init__(self, *args, **kwargs):
    # #     super(BudgetedHours, self).__init__(*args, **kwargs)
    # #     self.fields['client'].choices = [(x.pk, x.client) for x in Client.objects.all()]


    # def clean(self):
    #     cleaned_data = super().clean()

    #     code = cleaned_data.get('code')
    #     pk = self.instance.pk

    #     item = BudgetedHours.objects.filter(code=code).exclude(pk=pk).exists()

    #     if item:
    #         raise forms.ValidationError('Ya existe una actividad con este nombre')
