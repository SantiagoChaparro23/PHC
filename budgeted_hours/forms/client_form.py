from django import forms
from budgeted_hours.models import Client
from django.core.exceptions import ValidationError


class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ('client',)
        labels = {
            'client': 'Cliente'
        }


    def clean(self):
        cleaned_data = super().clean()

        client = cleaned_data.get('client')
        pk = self.instance.pk

        item = Client.objects.filter(client__iexact = client).exclude(pk=pk).exists()

        if item:
            raise forms.ValidationError('Ya existe un cliente con este nombre')
