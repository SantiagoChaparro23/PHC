from django import forms
from configuration_sddp.models import MetaMatrix


class MetaMatrixForm(forms.ModelForm):

    class Meta:
        model = MetaMatrix
        fields = '__all__'
