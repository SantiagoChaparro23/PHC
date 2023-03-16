from datetime import datetime
from django import forms
from numpy import NaN
import pandas as pd

# from configuration_sddp.models import Project, Demand, ExistingPlants, CurrentMatrix, CxC, CLP


class ProjectsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProjectsForm, self).__init__(*args, **kwargs)

        self.fields['file'].required = True
        # self.fields['area'].required = False
        # self.fields['type'].required = False
        #self.fields['date'].label = 'Fecha'


    class Meta:
        # model = Project
        fields = ('name', 'description', 'file')
        labels = {
            'name': 'Nombre del proyecto',
            'description': 'Descripción',
            'file': 'config_sddp_input.csv'
        }


    def process(self, obj):

        _file = self.cleaned_data.get('file')

        # Read data
        df_existing_plants = pd.read_excel(obj.file, engine="openpyxl", sheet_name="Plantas existentes")
        df_current_matrix  = pd.read_excel(obj.file, engine="openpyxl", sheet_name="Matriz actual")
        df_cxc             = pd.read_excel(obj.file, engine="openpyxl", sheet_name="CxC")
        df_clp             = pd.read_excel(obj.file, engine="openpyxl", sheet_name="CLP")
        df_demand          = pd.read_excel(obj.file, engine="openpyxl", sheet_name="Demanda")

        df_existing_plants['Fecha inicio Vigencia de la ENFICC*'] = pd.to_datetime(df_existing_plants['Fecha inicio Vigencia de la ENFICC*'], format="%Y/%m/%d", infer_datetime_format=True)
        df_existing_plants['Fecha Fin Vigencia de la ENFICC*'] = pd.to_datetime(df_existing_plants['Fecha Fin Vigencia de la ENFICC*'], format="%Y/%m/%d", infer_datetime_format=True)

        df_current_matrix['Fecha de entrada'] = pd.to_datetime(df_current_matrix['Fecha de entrada'], format="%Y/%m/%d", infer_datetime_format=True)

        df_cxc['Inicio Período de Vigencia  (dd/mm/aaaa)'] = pd.to_datetime(df_cxc['Inicio Período de Vigencia  (dd/mm/aaaa)'], format="%Y/%m/%d", infer_datetime_format=True)
        df_cxc['Fin \nPeríodo de Vigencia  (dd/mm/aaaa)'] = pd.to_datetime(df_cxc['Fin \nPeríodo de Vigencia  (dd/mm/aaaa)'], format="%Y/%m/%d", infer_datetime_format=True)
        df_cxc['Fecha de entrada'] = pd.to_datetime(df_cxc['Fecha de entrada'], format="%Y/%m/%d", infer_datetime_format=True)

        df_clp['Inicio Período de Vigencia  (dd/mm/aaaa)'] = pd.to_datetime(df_clp['Inicio Período de Vigencia  (dd/mm/aaaa)'], format="%Y/%m/%d", infer_datetime_format=True)
        df_clp['Fin \nPeríodo de Vigencia  (dd/mm/aaaa)'] = pd.to_datetime(df_clp['Fin \nPeríodo de Vigencia  (dd/mm/aaaa)'], format="%Y/%m/%d", infer_datetime_format=True)
        df_clp['Fecha de entrada'] = pd.to_datetime(df_clp['Fecha de entrada'], format="%Y/%m/%d", infer_datetime_format=True)

        df_demand['Fecha'] = pd.to_datetime(df_demand['Fecha'], format="%Y/%m/%d", infer_datetime_format=True)

        # Apply some
        df_existing_plants['Fecha inicio Vigencia de la ENFICC*'] = df_existing_plants['Fecha inicio Vigencia de la ENFICC*'].astype(str)
        df_existing_plants['Fecha Fin Vigencia de la ENFICC*'] = df_existing_plants['Fecha Fin Vigencia de la ENFICC*'].astype(str)
        df_existing_plants = df_existing_plants.where(pd.notnull(df_existing_plants), None)

        df_current_matrix['Fecha de entrada'] = df_current_matrix['Fecha de entrada'].astype(str)
        df_current_matrix = df_current_matrix.where(pd.notnull(df_current_matrix), None)

        df_cxc['Inicio Período de Vigencia  (dd/mm/aaaa)'] = df_cxc['Inicio Período de Vigencia  (dd/mm/aaaa)'].astype(str)
        df_cxc['Fin \nPeríodo de Vigencia  (dd/mm/aaaa)'] = df_cxc['Fin \nPeríodo de Vigencia  (dd/mm/aaaa)'].astype(str)
        df_cxc['Fecha de entrada'] = df_cxc['Fecha de entrada'].astype(str)
        df_cxc = df_cxc.where(pd.notnull(df_cxc), None)

        df_clp['Inicio Período de Vigencia  (dd/mm/aaaa)'] = df_clp['Inicio Período de Vigencia  (dd/mm/aaaa)'].astype(str)
        df_clp['Fin \nPeríodo de Vigencia  (dd/mm/aaaa)'] = df_clp['Fin \nPeríodo de Vigencia  (dd/mm/aaaa)'].astype(str)
        df_clp['Fecha de entrada'] = df_clp['Fecha de entrada'].astype(str)
        df_clp = df_clp.where(pd.notnull(df_clp), None)

        df_demand['Días mes'] = df_demand['Fecha'].dt.daysinmonth

        df_demand['Fecha'] = df_demand['Fecha'].astype(str)
        df_demand = df_demand.where(pd.notnull(df_demand), None)

        # df['fecha'] = pd.to_datetime(df['fecha'], format="%Y/%m/%d")

        df_existing_plants.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)
        df_current_matrix.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)
        df_cxc.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)
        df_clp.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)
        df_demand.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)


        # Save data in models
        # for row in df_existing_plants.values:

        #     exist_plant = ExistingPlants(
        #         project=obj,
        #         agent=row[0],
        #         plant=row[1],
        #         type_plant=row[2],
        #         dc_ndc=row[3],
        #         clasification=row[4],
        #         contract=row[5],
        #         verified_enficc=row[6],
        #         uncommitted_enficc=row[7],
        #         start_date_validity_enficc=row[8],
        #         end_date_validity_enficc=row[9],
        #         declared_fuel=row[10]
        #     )

        #     exist_plant.save()


        # for row in df_current_matrix.values:

        #     curr_mat = CurrentMatrix(
        #         project=obj,
        #         power_source=row[0],
        #         capacity=row[1],
        #         convertion=row[2],
        #         date=row[3],
        #         type_source=row[4],
        #     )

        #     curr_mat.save()


        # for row in df_cxc.values:

        #     cxc = CxC(
        #         project=obj,
        #         power_source=row[0],
        #         plant=row[1],
        #         classification_plant=row[2],
        #         oef_assigned=row[3],
        #         start_validity=row[4],
        #         end_validity=row[5],
        #         technology=row[6],
        #         capacity=row[7],
        #         entry_date=row[8]
        #     )

        #     cxc.save()


        # for row in df_clp.values:

        #     clp = CLP(
        #         project=obj,
        #         power_source=row[0],
        #         plant=row[1],
        #         classification_plant=row[2],
        #         oef_assigned=row[3],
        #         start_validity=row[4],
        #         end_validity=row[5],
        #         technology=row[6],
        #         capacity=row[7],
        #         entry_date=row[8]
        #     )

        #     clp.save()


        # for row in df_demand.values:

        #     dem = Demand(
        #         project=obj,
        #         date=row[0],
        #         month_days=row[1],
        #         energy_demand=row[2]
        #     )

        #     dem.save()


        return None