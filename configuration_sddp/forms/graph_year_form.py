from django import forms
from configuration_sddp.models import GraphYear


class GraphYearForm(forms.ModelForm):

    class Meta:
        model = GraphYear
        fields = '__all__'
