from django import forms
from budgeted_hours.models import Activities
from django.core.exceptions import ValidationError


class ActivitiesForm(forms.ModelForm):

    class Meta:
        model = Activities
        fields = ('service_type', 'activity', 'description')
        labels = {
            'service_type': 'Tipo de servicio',
            'activity': 'Actividad',
            'description': 'Descripción'
        }


    def __init__(self, *args, **kwargs):
        super(ActivitiesForm, self).__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['service_type'].disabled = True


    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)

        activity = cleaned_data.get('activity')
        pk = self.instance.pk

        item = Activities.objects.filter(activity__iexact = activity).exclude(pk = pk).exists()

        if item:
            raise forms.ValidationError('Ya existe una actividad con este nombre')
