from django import forms
from configuration_sddp.models import AdditionalCapacity


class AdditionalCapacityForm(forms.ModelForm):

    class Meta:
        model = AdditionalCapacity
        fields = '__all__'
