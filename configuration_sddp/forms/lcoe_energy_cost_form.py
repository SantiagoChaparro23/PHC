from django import forms
from configuration_sddp.models import LcoeEnergyCost


class LcoeEnergyCostForm(forms.ModelForm):

    class Meta:
        model = LcoeEnergyCost
        fields = '__all__'
