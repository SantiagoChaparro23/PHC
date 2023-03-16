from django import forms
from vacations.models import Bonus
# from django.core.exceptions import ValidationError


class BonusForm(forms.ModelForm):

    class Meta:
        model = Bonus
        fields = ('collaborator', 'extra_days', 'expiration_at', 'description')
        labels = {
            'collaborator': 'Colaborador',
            'extra_days': 'Días extras',
            'expiration_at': 'Fecha de vencimiento',
            'description': 'Descripción'
        }


    def __init__(self, *args, **kwargs):
        super(BonusForm, self).__init__(*args, **kwargs)
        self.fields['collaborator'].widget.attrs['class'] = 'select2'


    # def __init__(self, *args, **kwargs):
    #     super(ActivitiesForm, self).__init__(*args, **kwargs)

    #     instance = getattr(self, 'instance', None)
    #     if instance and instance.pk:
    #         self.fields['service_type'].disabled = True


    # def clean(self):
    #     cleaned_data = super().clean()
    #     print(cleaned_data)

    #     activity = cleaned_data.get('activity')
    #     pk = self.instance.pk

    #     item = Activities.objects.filter(activity__iexact = activity).exclude(pk = pk).exists()

    #     if item:
    #         raise forms.ValidationError('Ya existe una actividad con este nombre')
