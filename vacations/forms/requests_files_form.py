from django import forms
from vacations.models import Requests
from django.core.exceptions import ValidationError


class RequestsFilesForm(forms.ModelForm):

    class Meta:
        model = Requests
        fields = ('path_liquidation',)
        labels = {
            'path_liquidation': 'Archivo'
        }


    def __init__(self, *args, **kwargs):
        super(RequestsFilesForm, self).__init__(*args, **kwargs)

        self.fields['path_liquidation'].required = False

        # instance = getattr(self, 'instance', None)
        # if instance and instance.pk:
        #     self.fields['service_type'].disabled = True


    # def clean(self):
    #     cleaned_data = super().clean()
    #     print(cleaned_data)

    #     activity = cleaned_data.get('activity')
    #     pk = self.instance.pk

    #     item = Activities.objects.filter(activity__iexact = activity).exclude(pk = pk).exists()

    #     if item:
    #         raise forms.ValidationError('Ya existe una actividad con este nombre')
