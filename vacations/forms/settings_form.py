from django import forms
from vacations.models import Settings
# from django.core.exceptions import ValidationError


class SettingsForm(forms.ModelForm):

    class Meta:
        model = Settings
        fields = (
            'days_max',
            'notify_days_max',
            'group_notify_days_max',
            'group_notify_request',
            'notify_request_pending',
            'group_notify_request_pending',
            'group_notify_request_accepted',
            'group_notify_request_deny_final_acceptor',
            'group_notify_liquidation_deny',
            'final_acceptor'
        )
        labels = {
            'days_max': 'Días máximos',
            'notify_days_max': 'Notificar cada',
            'group_notify_days_max': 'Notificar por dias maximos a',
            'group_notify_request': 'Notificar solicitudes a',
            'notify_request_pending': 'Notificar solicitudes pendientes cada',
            'group_notify_request_pending': 'Notificar solicitudes pendientes a',
            'group_notify_request_accepted': 'Notificar solicitudes aceptadas a',
            'group_notify_request_deny_final_acceptor': 'Notificar solicitudes rechazadas por el aceptador final',
            'group_notify_liquidation_deny': 'Notificar liquidaciones rechazadas a',
            'final_acceptor': 'Aceptador final'
        }


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
