from django import forms
from vacations.models import Requests
# from django.core.exceptions import ValidationError


class RequestsForm(forms.ModelForm):

    class Meta:
        model = Requests
        fields = (
            'leader',
            'final_acceptor',
            'accepted_leader',
            'date_leader',
            'accepted_final_acceptor',
            'date_final_acceptor',
            'request_completed',
            'start_date_vacations',
            'end_date_vacations',
            'accepted_liquidation',
            'comments'
        )
        labels = {
            'leader': 'Lider',
            'final_acceptor': 'Aceptador final',
            'accepted_leader': 'Aceptada por el lider',
            'date_leader': 'Fecha en que acepto/rechazo el lider',
            'accepted_final_acceptor': 'Aceptada por el aceptante final',
            'date_final_acceptor': 'Fecha en que acepto/rechazo el aceptante final',
            'request_completed':'Solicitud completada',
            'start_date_vacations': 'Fecha de inicio de las vacaciones',
            'end_date_vacations': 'Fecha de fin de las vacaciones',
            'accepted_liquidation': 'Liquidacion aceptada',
            'comments': 'Comentarios'
        }


    def __init__(self, *args, **kwargs):
        super(RequestsForm, self).__init__(*args, **kwargs)
        self.fields['leader'].widget.attrs['class'] = 'select2'
        self.fields['comments'].widget.attrs = {'rows': 4}
