from django import forms
from configuration_sddp.models import ExistingPlants


class ExistingPlantsForm(forms.ModelForm):

    class Meta:
        model = ExistingPlants
        fields = '__all__'
