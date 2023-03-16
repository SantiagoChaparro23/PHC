from django import forms
from configuration_sddp.models import Fuel


class FuelForm(forms.ModelForm):

    class Meta:
        model = Fuel
        fields = '__all__'
