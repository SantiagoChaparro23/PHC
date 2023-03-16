from django import forms
from imports.models import PHENOMENONS, BagPriceCustomDates
from django.core.exceptions import ValidationError


class PhenomenonForm(forms.ModelForm):
    # phenomenon = forms.ChoiceField(choices=BagPriceCustomDates)
    # date = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Fecha'}))
    # is_active = forms.DateField(
    #     label='Fecha',
    #     validators=[validate_domain],
    # )

    class Meta:
        model = BagPriceCustomDates
        fields = ('date', 'phenomenon')
        labels = {
            "date": "Fecha",
            "phenomenon": "Fenómeno"
        }

    def clean(self):
        cleaned_data = super().clean()
        
        date = cleaned_data.get('date')
        phenomenon = cleaned_data.get('phenomenon')
        pk = self.instance.pk
        
        item = BagPriceCustomDates.objects.filter(phenomenon=phenomenon, date=date).exclude(pk=pk).exists()
        if item:
            raise forms.ValidationError('Ya existe una fecha con estos datos')

  

