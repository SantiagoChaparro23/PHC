from django import forms
from budgeted_hours.models import TemplatesBudgetedHours
# from django.core.exceptions import ValidationError


class TemplatesBudgetedHoursForm(forms.ModelForm):

    class Meta:
        model = TemplatesBudgetedHours
        fields = ('template_name', 'service_type', 'operator')
        labels = {
            'template_name': 'Nombre de la plantilla',
            'service_type': 'Tipo de servicio',
            'operator': 'Operador'
        }


    def __init__(self, *args, **kwargs):
        super(TemplatesBudgetedHoursForm, self).__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['service_type'].disabled = True


    # def __init__(self, *args, **kwargs):
    #     super(TemplatesPoliticalHoursForm, self).__init__(*args, **kwargs)
    #     self.fields['client'].widget.attrs['class'] = 'select2'

    #     instance = getattr(self, 'instance', None)
    #     if instance and instance.pk:
    #         self.fields['study_type'].disabled = True


    # code = forms.CharField(
    #     # label='Bloque',
    #     # max_digits=3,
    #     # decimal_places=0,
    #     widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'id': 'code'})
    # )

    # # choices = tuple(Client.objects.all().values_list())
    # client = forms.ModelChoiceField(
    #     queryset=Client.objects.all(),
    # # client = forms.ChoiceField(
    # #     choices = Client.CLIENT,
    # #     # label='Duración',
    # #     # max_digits=5,
    # #     # decimal_places=4,
    #     widget=forms.Select(attrs={'class': 'form-control', 'id': 'client'})
    # )

    # study_type = forms.ModelChoiceField(
    #     queryset = Activities.objects.all(),
    #     # label='Restup',
    #     # max_digits=5,
    #     # decimal_places=4,
    #     widget=forms.Select(attrs={'class': 'form-control', 'id': 'study_type'})
    # )

    # activity = forms.CharField(
    #     # label='Bloque',
    #     # max_digits=3,
    #     # decimal_places=0,
    #     widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'id': 'demcarac-bloque-input'})
    # )


    # # def __init__(self, *args, **kwargs):
    # #     super(BudgetedHours, self).__init__(*args, **kwargs)
    # #     self.fields['client'].choices = [(x.pk, x.client) for x in Client.objects.all()]


    # class Meta:
    #     model = BudgetedHours
    #     fields = ['code', 'client', 'study_type', 'activity']



    # def clean(self):
    #     cleaned_data = super().clean()

    #     code = cleaned_data.get('code')
    #     pk = self.instance.pk

    #     item = BudgetedHours.objects.filter(code=code).exclude(pk=pk).exists()

    #     if item:
    #         raise forms.ValidationError('Ya existe una actividad con este nombre')
