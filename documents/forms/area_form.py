from django import forms
from documents.models import Area


class AreaForm(forms.ModelForm):
    
    class Meta:
        model = Area
        
        fields = (
            'area',
        )
        
        labels = {
            'area': 'Área',
        }