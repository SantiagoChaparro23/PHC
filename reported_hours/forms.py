
from reported_hours.models import ReportedHours
from django import forms
from django.core.exceptions import ValidationError
import datetime

class ReportedHoursForm(forms.ModelForm):


   
    def __init__(self, *args, **kwargs):

        super(ReportedHoursForm, self).__init__(*args, **kwargs)
        self.fields['time'].required = False
        self.fields['report_date_at'].required = True
        self.fields['report_date_at'].initial = datetime.datetime.now().strftime ("%Y-%m-%d")
        self.fields['description'].widget.attrs['rows'] = 3


    
    HOURS = [[x,x] for x in range(24)]
    hours = forms.ChoiceField(choices=HOURS, required=False, initial=1, label='Horas')

    MINUTES = [[(x),f'{x}'] for x in range(60)]
    minutes = forms.ChoiceField(choices=MINUTES, required=False, label='Minutos')

    #report_date_at = forms.TextInput(required=True, initial='2020-09-09', label='Minutos')
  


    class Meta:
        model = ReportedHours
        fields = ('description','report_date_at', 'time')
        labels = {
            'description': 'Descripción',
            'time': 'Tiempo',
            'report_date_at': 'Fecha de reporte'
        }


    #def clean_report_date_at(self):

    def clean_hours(self):
        #return self.cleaned_data['hours']
    
        hours = int(self.data.get('hours')) * 60
        
        minutes = int(self.data.get('minutes'))        
        
        total = int(hours) + int(minutes)

        if total < 1:
            raise ValidationError("El tiempo minímo para reportar es de 1 minuto")
     
        
        return total
       