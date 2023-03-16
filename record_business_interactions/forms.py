from datetime import datetime, timezone, timedelta

from django import forms
from .models import VisitRecord, InteractionType, Settings
from django.core.exceptions import ValidationError


class InteractionTypeForm(forms.ModelForm):

    class Meta:
        model = InteractionType
        fields = ('name',)
        labels = {
            'name': 'Tipo de interaccion'
        }

    def clean(self):
        cleaned_data = super().clean()

        interaction_type = cleaned_data.get('name')
        pk = self.instance.pk

        item = InteractionType.objects.filter(name__iexact=interaction_type).exclude(pk=pk).exists()

        if item:
            raise forms.ValidationError('Ya existe un tipo de interaccion con este nombre')


class VisitRecordForm(forms.ModelForm):

    class Meta:
        model = VisitRecord
        fields = ('date_visit', 'client', 'user', 'phc_code', 'interaction_type', 'customer_commitments', 'is_in_crm', 'validated_in_crm',)
        labels = {
            'date_visit'          : 'Fecha visita',
            'client'              : 'Cliente',
            'user'                : 'Gestor comercial',
            'phc_code'            : 'Codigo PHC',
            'interaction_type'    : 'Tipo de interaccion',
            'customer_commitments': 'Compromisos con el cliente',
            'is_in_crm'           : 'En el CRM',
            'validated_in_crm'    : 'Validado en el CRM'
        }

    def clean(self):

        # Take parameters and variables - - - - - - - - - - - - - - - - - - - - - - - - - -
        max_visits_by_client = int(Settings.objects.filter(key='max_visits_by_client')[0].value)

        #   Take input parameters from the form
        cleaned_data = super().clean()
        client_obj = cleaned_data['client']
        user_obj = cleaned_data["user"]
        date_visit = cleaned_data['date_visit']

        # Check 1 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check if date_visit is in the range given by the current month

        #   Take date from the input date
        visit_year, visit_month = date_visit.year, date_visit.month

        #   Take date from the current date, apply Colombia offset
        current_date = datetime.now().replace(tzinfo=timezone(timedelta(hours=-5))) - timedelta(hours=5)
        curr_year, curr_month  = current_date.year, current_date.month

        #   Compare if the month and date are the same
        if (visit_year != curr_year) or (visit_month != curr_month):
            raise forms.ValidationError("Solo esta permitido ingresar fechas de visitas del mes actual")

        print('date_visit: ', date_visit, current_date)


        # Check 2 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check if amount of visits to client from business manager if under max_visits_by_client limit

        #   Calculate amount of previous visits to client did by business manager in the CURRENT MONTH
        visit_year, visit_month  = str(date_visit.year), str(date_visit.month)

        amount_visits = VisitRecord.objects.filter(client=client_obj, user=user_obj,
                                                   date_visit__year=visit_year, date_visit__month=visit_month)

        if client_obj and user_obj:
            # Only do something if both fields are valid so far.
            if len(amount_visits) >= max_visits_by_client:
                raise forms.ValidationError(
                    f"Cantidad maxima de visitas mensuales ({max_visits_by_client}) realizadas por el gestor comercial al cliente, excedidas. "
                    "No se puede realizar el registro"
                )

class VisitRecordValidateForm(forms.ModelForm):
    class Meta:
        model = VisitRecord
        fields = ('date_visit', 'client', 'user', 'phc_code', 'interaction_type', 'customer_commitments', 'is_in_crm', 'validated_in_crm',)
        labels = {
            'date_visit'          : 'Fecha visita',
            'client'              : 'Cliente',
            'user'                : 'Gestor comercial',
            'phc_code'            : 'Codigo PHC',
            'interaction_type'    : 'Tipo de interaccion',
            'customer_commitments': 'Compromisos con el cliente',
            'is_in_crm'           : 'En el CRM',
            'validated_in_crm'    : 'Validado en el CRM'
        }       

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_visit'].disabled = True
        self.fields['client'].disabled = True
        self.fields['user'].disabled = True
        self.fields['phc_code'].disabled = True
        self.fields['interaction_type'].disabled = True
        self.fields['customer_commitments'].disabled = True
        self.fields['is_in_crm'].disabled = True



