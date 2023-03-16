from django import forms
from configuration_sddp.models import FuelPriceOption


class FuelPriceOptionForm(forms.ModelForm):

    class Meta:
        model = FuelPriceOption
        fields = '__all__'
        labels = {
            'name': 'Nombre'
        }
