from django import forms
from configuration_sddp.models import GrowingRate


class GrowingRateForm(forms.ModelForm):

    class Meta:
        model = GrowingRate
        fields = '__all__'
        labels = {
            'name': 'Nombre'
        }
