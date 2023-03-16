from django import forms
from imports.models import PHENOMENONS, NationalBagPriceCustomDates
from django.core.exceptions import ValidationError


from django.core.validators import URLValidator


validate = URLValidator()




class PhenomenonForm(forms.ModelForm):
    # phenomenon = forms.ChoiceField(choices=NationalBagPriceCustomDates)
    # date = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Fecha'}))
    
    is_active = forms.CharField(
        label='is_active',
        validators=[validate],
    )

    class Meta:
        model = NationalBagPriceCustomDates
        fields = ('date', 'phenomenon', 'is_active')
        labels = {
            "date": "Fecha",
            "phenomenon": "Fenómeno",
        }

    def clean(self):
        cleaned_data = super().clean()
        
        date = cleaned_data.get('date')
        phenomenon = cleaned_data.get('phenomenon')
        pk = self.instance.pk
        
        item = NationalBagPriceCustomDates.objects.filter(phenomenon=phenomenon, date=date).exclude(pk=pk).exists()
        if item:
            raise forms.ValidationError('Ya existe una fecha con estos datos')

  

