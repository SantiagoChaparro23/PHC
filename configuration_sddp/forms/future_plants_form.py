from django import forms
from configuration_sddp.models import FuturePlants


class FuturePlantsForm(forms.ModelForm):

    class Meta:
        model = FuturePlants
        fields = '__all__'
