from django import forms
from documents.models import Templates

class TemplatesForm(forms.ModelForm):
    
    class Meta:
        model = Templates 
        
        fields = (
            'created_at',
            'created_by',
            'area',
            'title',
            'description',            
            'file',            
        )
        
        labels = {
            'created_at': 'Fecha',
            'created_by': 'Responsable',
            'area': 'Área',
            'title': 'Título',
            'description': 'Descripción',
            'file': 'Archivo',
        }
        
