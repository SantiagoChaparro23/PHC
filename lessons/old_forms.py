from django import forms
# from .models import (ConnectionStudies, MarketStudies, MarketStudiesFiles, 
#                      Commercial, PreventiveActions, CommercialLesson, RelatedArea)
from django.core.exceptions import ValidationError


class RelatedAreaForm(forms.ModelForm):

    class Meta:
        # model = RelatedArea
        fields = ('name',)
        labels = {
            'name': 'Area relacionada'
        }

    def clean(self):
        cleaned_data = super().clean()

        related_area = cleaned_data.get('name')
        pk = self.instance.pk

        # item = RelatedArea.objects.filter(name__iexact=related_area).exclude(pk=pk).exists()

        # if item:
        #     raise forms.ValidationError('Ya existe un area relacionada con este nombre')



class CommercialForm(forms.ModelForm):

    date = forms.DateField(widget=forms.DateInput(format = '%Y-%m-%d'))

    def __init__(self, *args, **kwargs):

        super(CommercialForm, self).__init__(*args, **kwargs)

        self.fields['date'].label = 'Fecha'

    class Meta:
        # model = Commercial
        fields = ('date', 'phc_code', 'rfp_issued_by_client', 'name', 'business_manager', 'client', 'service_type')
        labels = {

            'date': 'Fecha',           
            'phc_code': 'Codigo PHC',
            'rfp_issued_by_client': 'RFP emitido por el cliente',
            'name': 'Nombre del Proyecto a Evaluar',
            'business_manager': 'Gestor Comercial',
            'client': 'Cliente',
            'service_type': 'Línea de Producto'
        }


class ConnectionStudiesForm(forms.ModelForm):


    date = forms.DateField(widget=forms.DateInput(format = '%Y-%m-%d'))

    def __init__(self, *args, **kwargs):

        super(ConnectionStudiesForm, self).__init__(*args, **kwargs)

        self.fields['area'].required = False
        self.fields['description'].required = False
        self.fields['type'].required = False

        self.fields['date'].label = 'Fecha'

    class Meta:
        # model = ConnectionStudies
        fields = ('date', 'zone', 'operator', 'area', 'description', 'file')
        labels = {
           
            # 'code': 'Código',
            # 'title': 'Título',
            'zone': 'Zona',
            'operator': 'Operador',

            'description': 'Descripción',
            'responsable': 'Responsable',
            # 'type': 'Tipo de lección',
            # 'file': 'Archivo'
          
        }


    # def clean(self):
    #     cleaned_data = super().clean()
    #     if True:
    #         raise forms.ValidationError('Ya existe una métrica con este nombre')


class MarketStudiesFilesForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):

        super(MarketStudiesFilesForm, self).__init__(*args, **kwargs)

        # self.fields['area'].required = False
        # self.fields['description'].required = False
        self.fields['file'].required = False

    

    class Meta:
        # model = MarketStudiesFiles
        fields = ('file',)
        labels = {
            'file': 'Archivo'          
        }


class MarketStudiesForm(forms.ModelForm):


    date = forms.DateField(widget=forms.DateInput(format = '%Y-%m-%d'))

    def __init__(self, *args, **kwargs):

        super(MarketStudiesForm, self).__init__(*args, **kwargs)

        # self.fields['area'].required = False
        # self.fields['description'].required = False
        self.fields['characteristic'].required = False
     
      
        self.fields['date'].label = 'Fecha'


    class Meta:
        # model = MarketStudies
        fields = ('date', 
        'code',
        'title', 
        'study_type', 
        'information_type', 
        'characteristic', 
        'other', 
        'description', 
        'file_market_studies'
        )
        labels = {
           
            'code': 'Código',
            'title': 'Título',
            'study_type': 'Tipo de estudio',
            'information_type': 'Tipo de información',
            'characteristic': 'Característica',
            'other': 'Otro',
            'description': 'Descripción',
            'file_market_studies': 'Archivo',
       
           
        }



    def clean_other(self):
        characteristic = self.cleaned_data['characteristic']
        if characteristic is not None:
            if characteristic.name == 'Otro':
                other = self.cleaned_data['other']        
                if other is None:
                    raise ValidationError("Este es campo es requerido")

        return self.cleaned_data['other']
