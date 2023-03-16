from django import forms
from budgeted_hours.models import Categories
from django.core.exceptions import ValidationError


class CategoriesForm(forms.ModelForm):

    class Meta:
        model = Categories
        fields = ('category',)
        labels = {
            'category': 'Nombre'
        }


    # def clean(self):
    #     cleaned_data = super().clean()

    #     activity = cleaned_data.get('activity')
    #     pk = self.instance.pk

    #     item = EnergyAnalysis.objects.filter(activity=activity).exclude(pk=pk).exists()

    #     if item:
    #         raise forms.ValidationError('Ya existe una actividad con este nombre')
