from django import forms
from markers.models import Team

class TeamForm(forms.ModelForm):
    
    class Meta:
        model = Team
        
        fields = (
            'name',
        )
        
        labels = {
            'name': 'Nombre',
        }