from lessons.models import ConnectionStudies
from django import forms
from .models import Generation, Project, Demand, Db, MarginalCostDemand, ReturnRate, WeightBlocks
from django.core.exceptions import ValidationError
from django.forms import ClearableFileInput
import pandas as pd
import datetime
from pandas.tseries.offsets import MonthEnd
import calendar
from django.db import connection
import datetime

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)




class DbsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(DbsForm, self).__init__(*args, **kwargs)

        self.fields['genpltproy_file'].required = False


    class Meta:
        model = Db
        fields = ('name', 'description', 'project', 'cmgdem_file', 'genpltproy_file')
        labels = {
            'name': 'Nombre de la base de datos',
            'description': 'Descripción',
            'project': 'Proyecto',
            'cmgdem_file': 'cmgdem.csv *',
            'genpltproy_file': 'genpltproy.csv'
        }

    def clean_cmgdem_file(self):
        #return self.cleaned_data['cmgdem_file']
        try: 
            _file = self.cleaned_data.get('cmgdem_file')
            
            df = pd.read_csv(_file)
            
            month_star = int(float(df.columns[5]))
            year_star = int(float(df.columns[6]))
            base_date = datetime.datetime(year_star, month_star, 1)

        except Exception as e:
            raise ValidationError("El archivo cmgdem no tiene un formato válido")

        return self.cleaned_data['cmgdem_file']


    def clean_genpltproy_file(self):
        if self.cleaned_data.get('genpltproy_file'):
            try: 
                _file = self.cleaned_data.get('genpltproy_file')
                
                df = pd.read_csv(_file)
                
                month_star = int(float(df.columns[5]))
                year_star = int(float(df.columns[6]))
                base_date = datetime.datetime(year_star, month_star, 1)
            except Exception as e:
                raise ValidationError("El archivo genpltproy no tiene un formato válido")

        return self.cleaned_data['genpltproy_file']
        
    def process_genpltproy(self, obj):
 
        if obj.genpltproy_file:
            df = pd.read_csv(obj.genpltproy_file)
            
        
            month_star = int(float(df.columns[5]))
            year_star = int(float(df.columns[6]))

            base_date = datetime.datetime(year_star, month_star, 1)
            
 
            # Daniel Ayuda
            for index, row in df.iloc[2:].iterrows():
                plant = row[3];
                obj.plant = plant
                obj.save()
                break
           
            cursor = connection.cursor()
            values = ''  
            table_name = Generation.objects.model._meta.db_table
            for row in df.iloc[3:].values.tolist():

            
                step = int(row[0]) - 1
                serie = row[1]
                block = row[2]
                value = row[3]
            
                #formato a la fecha
                date  = add_months(base_date,step)
                
                #calculo el ultimo dia del mes
                last_day = calendar.monthrange(date.year, date.month)
                

                #obtengo la fecha en el formatio que necesito inserat
                date = datetime.datetime(date.year, date.month, last_day[1])
                values += '''('{}', '{}', '{}', '{}', '{}'),'''.format(obj.pk, serie, block, value, date)
                

            result = f"{values[0: -1]};" 
            query = '''
            INSERT INTO "{}" ("db_id", "serie", "block", "value", "date") VALUES
            {}
            '''.format(table_name, result)

            cursor.execute(query)
            print(table_name)
            


    def process_cmgdem(self, obj):
       
        df = pd.read_csv(obj.cmgdem_file)
       
        month_star = int(float(df.columns[5]))
        year_star = int(float(df.columns[6]))

        base_date = datetime.datetime(year_star, month_star, 1)

       
        cursor = connection.cursor()
        values = ''
        table_name = MarginalCostDemand.objects.model._meta.db_table
        #for index, row in df.iloc[3:].iterrows():
        for row in df.iloc[3:].values.tolist():
        
            step = int(row[0]) - 1
            serie = row[1]
            block = row[2]
            value = row[3]
        
            #formato a la fecha
            date  = add_months(base_date,step)
            
            #calculo el ultimo dia del mes
            last_day = calendar.monthrange(date.year, date.month)
            

            #obtengo la fecha en el formatio que necesito inserat
            date = datetime.datetime(date.year, date.month, last_day[1])
     
            #MarginalCostDemand.objects.create(db_id=obj.pk, serie=serie, block=block, value=value, date=date)

            

            values += '''('{}', '{}', '{}', '{}', '{}'),'''.format(block, date, value, obj.pk, serie)

        
        result = f"{values[0: -1]};"
       
        query = '''
            INSERT INTO "{}" ("block", "date", "value", "db_id", "serie") VALUES
            {}
            '''.format(table_name, result)
        # print(query)
        cursor.execute(query)
        
        
        
     
        
        return
      


class ProjectsForm(forms.ModelForm):


   # date = forms.DateField(widget=forms.DateInput(format = '%Y-%m-%d'))

    def __init__(self, *args, **kwargs):

        super(ProjectsForm, self).__init__(*args, **kwargs)

        # self.fields['area'].required = False
        self.fields['file'].required = True
        # self.fields['type'].required = False

        #self.fields['date'].label = 'Fecha'

    class Meta:
        model = Project
        fields = ('file', 'name', 'description', 'demand_factor', 'trm', 'trm_date', 'start_date', 'limit_date' )
        labels = {
            'name': 'Nombre del proyecto',
            'description': 'Descripción',
            'demand_factor': 'Factor de demanda',
            'trm': 'TRM',
            'trm_date': 'Fecha TRM',
            'start_date': 'Fecha de entrada en operación',
            'limit_date': 'Fecha limite de operación',
            'file': 'demand.csv',
        }
        # widgets = {
        #     'file': ClearableFileInput(attrs={'multiple': True}),
        # }

    #valido si puedo parsear el archivo
    def clean_file(self):
        try: 
            _file = self.cleaned_data.get('file')

            df = pd.read_csv(_file)
            
            month_star = int(float(df.columns[5]))
            year_star = int(float(df.columns[6]))

            base_date = datetime.datetime(year_star, month_star, 1)

        except Exception as e:
            raise ValidationError("El archivo no tiene un formato válido")

        return self.cleaned_data['file']


    def process(self, obj):

        _file = self.cleaned_data.get('file')
       
        df = pd.read_csv(obj.file)
       
        month_star = int(float(df.columns[5]))
        year_star = int(float(df.columns[6]))

        base_date = datetime.datetime(year_star, month_star, 1)

        for index, row in df.iloc[3:].iterrows():
        
            step = int(row[0])
            serie = row[1]
            block = row[2]
            value = row[3]
        
            #formato a la fecha
            date  = add_months(base_date,step)
            
            #calculo el ultimo dia del mes
            last_day = calendar.monthrange(date.year, date.month)
            

            #obtengo la fecha en el formatio que necesito inserat
            date = datetime.datetime(date.year, date.month, last_day[1])
     
            Demand.objects.create(project_id=obj.pk, block=block, value=value, date=date)
        try:
            pass

               

        except Exception as e:

            return False

     
        
        return
    #     # df = pd.read_csv(_file,  delimiter = ',')
    #     # print(df)
     
    #     print(self.FILES)
        #raise ValidationError("Este es campo es requerido")

    #     characteristic = self.cleaned_data['characteristic']
      
    #     if characteristic.name == 'Otro':
    #         other = self.cleaned_data['other']
                        
    #         if other is None:
    #             raise ValidationError("Este es campo es requerido")

    #     return self.cleaned_data['other']





class WeightBlocksForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(WeightBlocksForm, self).__init__(*args, **kwargs)

    class Meta:
        model = WeightBlocks 
        fields = ('block', 'weight')
        labels = {
            'block': 'Bloque',
            'weight': 'Peso',
        } 


class ReturnRateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(ReturnRateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ReturnRate
        fields = ('year', 'value', 'resolution', 'tension_level')
        labels = {
            'year': 'Año',
            'value': 'Tasa de retorno',
            'resolution': 'Resolución',
            'tension_level': 'Nivel de tensión',
        } 