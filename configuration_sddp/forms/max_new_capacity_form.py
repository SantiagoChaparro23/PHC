from django import forms
from configuration_sddp.models import MaxNewCapacity


class MaxNewCapacityForm(forms.ModelForm):

    class Meta:
        model = MaxNewCapacity
        fields = '__all__'
