from django import forms
from configuration_sddp.models import PlantType


class PlantTypeForm(forms.ModelForm):

    class Meta:
        model = PlantType
        fields = '__all__'
