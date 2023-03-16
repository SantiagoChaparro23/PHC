from django import forms
from configuration_sddp.models import (
    Project,
    GraphYear,
    AdditionalCapacity,
    MetaMatrix,
    MaxNewCapacity,
    LcoeEnergyCost,
    Demand,
    PlantType,
    Fuel,
    ExistingPlants,
    FuturePlants
)

import pandas as pd


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = '__all__'


    def processExcel(self, obj):

        try:
            GraphYear.objects.filter(project = obj.id).delete()
            # AdditionalCapacity.objects.filter(project = obj.id).delete()
            MetaMatrix.objects.filter(project = obj.id).delete()
            MaxNewCapacity.objects.filter(project = obj.id).delete()
            LcoeEnergyCost.objects.filter(project = obj.id).delete()
            Demand.objects.filter(project = obj.id).delete()
            ExistingPlants.objects.filter(project = obj.id).delete()
            FuturePlants.objects.filter(project = obj.id).delete()

            df_graph_year = pd.read_excel(obj.file, engine='openpyxl', sheet_name='GraphYear')
            # df_additional_capacity = pd.read_excel(obj.file, engine='openpyxl', sheet_name='AdditionalCapacity')
            df_meta_matrix = pd.read_excel(obj.file, engine='openpyxl', sheet_name='MetaMatrix')
            df_max_new_capacity = pd.read_excel(obj.file, engine='openpyxl', sheet_name='MaxNewCapacity')
            df_lcoe_energy_cost = pd.read_excel(obj.file, engine='openpyxl', sheet_name='LcoeEnergyCost')
            df_demand = pd.read_excel(obj.file, engine='openpyxl', sheet_name='Demand')
            df_existing_plants = pd.read_excel(obj.file, engine='openpyxl', sheet_name='ExistingPlants')
            df_future_plants = pd.read_excel(obj.file, engine='openpyxl', sheet_name='FuturePlants')

            df_demand['demand_at'] = pd.to_datetime(df_demand['demand_at'], format='%Y/%m/%d', infer_datetime_format=True)

            df_future_plants['start_at'] = pd.to_datetime(df_future_plants['start_at'], format='%Y%m%d', infer_datetime_format=True)

            df_demand = df_demand.astype(str)
            df_existing_plants = df_existing_plants.astype(str)
            df_future_plants = df_future_plants.astype(str)

            # df_additional_capacity.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)
            df_meta_matrix.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)
            df_max_new_capacity.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)
            df_lcoe_energy_cost.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)
            df_demand.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)
            df_existing_plants.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)
            df_future_plants.replace(to_replace=["nan", "NaN", " - ", "NaT"], value=[None, None, None, None], inplace=True)

            for row in df_graph_year.values:
                graph_year = GraphYear(
                    project = obj,
                    year = row[0]
                )
                graph_year.save()

            # for row in df_additional_capacity.values:
            #     additional_capacity = AdditionalCapacity(
            #         project = obj,
            #         year = row[0],
            #         wind = row[1],
            #         solar = row[2],
            #         pch = row[3],
            #         thermal_not_centralized = row[4],
            #         renewable_not_conventional = row[5],
            #         liquid = row[6],
            #         coal = row[7],
            #         gas = row[8],
            #         glp = row[9],
            #         hidro = row[10]
            #     )
            #     additional_capacity.save()

            for row in df_meta_matrix.values:
                meta_matrix = MetaMatrix(
                    project = obj,
                    year = row[0],
                    wind = row[1],
                    solar = row[2],
                    pch = row[3],
                    thermal_not_centralized = row[4],
                    # renewable_not_conventional = row[5],
                    liquid = row[5],
                    coal = row[6],
                    gas = row[7],
                    glp = row[8],
                    hidro = row[9]
                )
                meta_matrix.save()

            for row in df_max_new_capacity.values:
                max_new_capacity = MaxNewCapacity(
                    project = obj,
                    year = row[0],
                    wind = row[1],
                    solar = row[2],
                    pch = row[3],
                    thermal_not_centralized = row[4],
                    # renewable_not_conventional = row[5],
                    liquid = row[5],
                    coal = row[6],
                    gas = row[7],
                    glp = row[8],
                    hidro = row[9]
                )
                max_new_capacity.save()

            for row in df_lcoe_energy_cost.values:
                lcoe_energy_cost = LcoeEnergyCost(
                    project = obj,
                    year = row[0],
                    wind = row[1],
                    solar = row[2],
                    pch = row[3],
                    thermal_not_centralized = row[4],
                    # renewable_not_conventional = row[5],
                    liquid = row[5],
                    coal = row[6],
                    gas = row[7],
                    glp = row[8],
                    hidro = row[9]
                )
                lcoe_energy_cost.save()

            for row in df_demand.values:
                demand = Demand(
                    project = obj,
                    demand_at = row[0],
                    month_days = row[1],
                    value = row[2]
                )
                demand.save()

            for row in df_existing_plants.values:
                existing_plants = ExistingPlants(
                    project = obj,
                    plant_type = PlantType.objects.get(pk = row[0]) if row[0] else None,
                    fuel = Fuel.objects.get(pk = row[1]) if row[1] else None,
                    name = row[2],
                    reliability_obligation = row[3],
                    long_term_contract = row[4],
                    central_dispatch = row[5],
                    nominal_power = row[6]
                )
                existing_plants.save()

            for row in df_future_plants.values:
                future_plants = FuturePlants(
                    project = obj,
                    plant_type = PlantType.objects.get(pk = row[0]) if row[0] else None,
                    fuel = Fuel.objects.get(pk = row[1]) if row[1] else None,
                    name = row[2],
                    reliability_obligation = row[3],
                    long_term_contract = row[4],
                    central_dispatch = row[5],
                    nominal_power = row[6],
                    start_at = row[7]
                )
                future_plants.save()

            return None

        except Exception as e:
            print(e)
            return f'Inconvenientes con la importación: {e}'
