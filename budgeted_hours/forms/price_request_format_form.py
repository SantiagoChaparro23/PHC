from django import forms
from budgeted_hours.models import PriceRequestFormat
from django.core.exceptions import ValidationError


class PriceRequestFormatForm(forms.ModelForm):

    class Meta:
        model = PriceRequestFormat
        fields = ('budgeted_hours', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj', 'ak', 'al', 'am', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'bg', 'bh', 'ca', 'cb', 'cc')
        labels = {
            'budgeted_hours': 'Código',
            'aa': 'Códigos de proyectos de Referencia',
            'ab': 'Valores cotizados al mismo cliente para proyectos similares',
            'ac': 'Tiempos presupuestados vs ejecutados en proyectos similares',
            'ad': '¿Cómo llegó el cliente a phc? (ejemplo: referido, ferias, internet, etc)',
            'ae': 'Descripción Breve del cliente',
            'af': 'Moneda en la que se debe entregar la cotización',
            'ag': 'Nombre de Operador de Red si aplica',
            'ah': '¿Se necesita póliza para este proyecto?',
            'ai': '¿Se requiere la participación de un especialista externo? Escribir el nombre y Valor',
            'aj': '¿Se requieren Gastos de viajes para el proyecto?',
            'ak': 'Tiempo de elaboración de la propuesta',
            'al': 'Personas que participarían en la ejecución del proyecto',
            'am': '¿Existe algún impuesto o Gasto adicional para la propuesta?',
            'ba': 'Cámara de Comercio  Actualizada',
            'bb': 'Registro Mercantil Renovado',
            'bc': 'Fecha de constitución de la Empresa mayor a 5 años',
            'bd': 'Duración de la Sociedad Indefinida',
            'be': 'Objeto y Actividad social acorde con el proyecto solicitado',
            'bf': 'Análisis positivos de los antecedentes del Representante Legal',
            'bg': 'Formulario del conocimiento del cliente completo',
            'bh': 'Cuenta con Estados Financieros o Impuesta de Renta Vigentes',
            'ca': 'La búsqueda del RL y relacionados se encuentran en la lista de la OFAC',
            'cb': 'La búsqueda del RL y relacionados se encuentran en la lista de la ONU',
            'cc': 'La búsqueda del RL y relacionados se encuentran involucrados en NOTICIAS PÚBLICAS que impliquen un riesgo alto para nuestra empresa'
        }


    # def clean(self):
    #     cleaned_data = super().clean()

    #     activity = cleaned_data.get('activity')
    #     pk = self.instance.pk

    #     item = EnergyAnalysis.objects.filter(activity=activity).exclude(pk=pk).exists()

    #     if item:
    #         raise forms.ValidationError('Ya existe una actividad con este nombre')
