from django.urls import path
from .views import (
    search,
    fuel_price_option,
    growing_rate,
    project,
    graph_year,
    additional_capacity,
    meta_matrix,
    max_new_capacity,
    lcoe_energy_cost,
    demand,
    plant_type,
    fuel,
    existing_plants,
    future_plants
)


app_name = 'configuration_sddp'


urlpatterns = [
    # path('project_old', old_project.ProjectListView.as_view(), name='old_project_list'),
    # path('project_old/create', old_project.ProjectCreateView.as_view(), name='old_project_create'),
    # path('interaction_type/<int:pk>/change', interaction_type.InteractionTypeChangeView.as_view(), name='interaction_type_change'),
    # path('interaction_type/<int:pk>/delete', interaction_type.InteractionTypeDeleteView.as_view(), name='interaction_type_delete')

    path('search', search.SearchTemplateView.as_view(), name='search_view'),

    path('fuel_price_option', fuel_price_option.FuelPriceOptionListView.as_view(), name='fuel_price_option_list'),
    path('fuel_price_option/create', fuel_price_option.FuelPriceOptionCreateView.as_view(), name='fuel_price_option_create'),
    path('fuel_price_option/<int:pk>/change', fuel_price_option.FuelPriceOptionUpdateView.as_view(), name='fuel_price_option_change'),
    path('fuel_price_option/<int:pk>/delete', fuel_price_option.FuelPriceOptionDeleteView.as_view(), name='fuel_price_option_delete'),

    path('growing_rate', growing_rate.GrowingRateListView.as_view(), name='growing_rate_list'),
    path('growing_rate/create', growing_rate.GrowingRateCreateView.as_view(), name='growing_rate_create'),
    path('growing_rate/<int:pk>/change', growing_rate.GrowingRateUpdateView.as_view(), name='growing_rate_change'),
    path('growing_rate/<int:pk>/delete', growing_rate.GrowingRateDeleteView.as_view(), name='growing_rate_delete'),

    path('project', project.ProjectListView.as_view(), name='project_list'),
    path('project/create', project.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/change', project.ProjectUpdateView.as_view(), name='project_change'),
    path('project/<int:pk>/delete', project.ProjectDeleteView.as_view(), name='project_delete'),

    path('graph_year', graph_year.GraphYearListView.as_view(), name='graph_year_list'),
    path('graph_year/create', graph_year.GraphYearCreateView.as_view(), name='graph_year_create'),
    path('graph_year/<int:pk>/change', graph_year.GraphYearUpdateView.as_view(), name='graph_year_change'),
    path('graph_year/<int:pk>/delete', graph_year.GraphYearDeleteView.as_view(), name='graph_year_delete'),

    path('additional_capacity', additional_capacity.AdditionalCapacityListView.as_view(), name='additional_capacity_list'),
    path('additional_capacity/create', additional_capacity.AdditionalCapacityCreateView.as_view(), name='additional_capacity_create'),
    path('additional_capacity/<int:pk>/change', additional_capacity.AdditionalCapacityUpdateView.as_view(), name='additional_capacity_change'),
    path('additional_capacity/<int:pk>/delete', additional_capacity.AdditionalCapacityDeleteView.as_view(), name='additional_capacity_delete'),

    path('meta_matrix', meta_matrix.MetaMatrixListView.as_view(), name='meta_matrix_list'),
    path('meta_matrix/create', meta_matrix.MetaMatrixCreateView.as_view(), name='meta_matrix_create'),
    path('meta_matrix/<int:pk>/change', meta_matrix.MetaMatrixUpdateView.as_view(), name='meta_matrix_change'),
    path('meta_matrix/<int:pk>/delete', meta_matrix.MetaMatrixDeleteView.as_view(), name='meta_matrix_delete'),

    path('max_new_capacity', max_new_capacity.MaxNewCapacityListView.as_view(), name='max_new_capacity_list'),
    path('max_new_capacity/create', max_new_capacity.MaxNewCapacityCreateView.as_view(), name='max_new_capacity_create'),
    path('max_new_capacity/<int:pk>/change', max_new_capacity.MaxNewCapacityUpdateView.as_view(), name='max_new_capacity_change'),
    path('max_new_capacity/<int:pk>/delete', max_new_capacity.MaxNewCapacityDeleteView.as_view(), name='max_new_capacity_delete'),

    path('lcoe_energy_cost', lcoe_energy_cost.LcoeEnergyCostListView.as_view(), name='lcoe_energy_cost_list'),
    path('lcoe_energy_cost/create', lcoe_energy_cost.LcoeEnergyCostCreateView.as_view(), name='lcoe_energy_cost_create'),
    path('lcoe_energy_cost/<int:pk>/change', lcoe_energy_cost.LcoeEnergyCostUpdateView.as_view(), name='lcoe_energy_cost_change'),
    path('lcoe_energy_cost/<int:pk>/delete', lcoe_energy_cost.LcoeEnergyCostDeleteView.as_view(), name='lcoe_energy_cost_delete'),

    path('demand', demand.DemandListView.as_view(), name='demand_list'),
    path('demand/create', demand.DemandCreateView.as_view(), name='demand_create'),
    path('demand/<int:pk>/change', demand.DemandUpdateView.as_view(), name='demand_change'),
    path('demand/<int:pk>/delete', demand.DemandDeleteView.as_view(), name='demand_delete'),

    path('plant_type', plant_type.PlantTypeListView.as_view(), name='plant_type_list'),
    path('plant_type/create', plant_type.PlantTypeCreateView.as_view(), name='plant_type_create'),
    path('plant_type/<int:pk>/change', plant_type.PlantTypeUpdateView.as_view(), name='plant_type_change'),
    path('plant_type/<int:pk>/delete', plant_type.PlantTypeDeleteView.as_view(), name='plant_type_delete'),

    path('fuel', fuel.FuelListView.as_view(), name='fuel_list'),
    path('fuel/create', fuel.FuelCreateView.as_view(), name='fuel_create'),
    path('fuel/<int:pk>/change', fuel.FuelUpdateView.as_view(), name='fuel_change'),
    path('fuel/<int:pk>/delete', fuel.FuelDeleteView.as_view(), name='fuel_delete'),

    path('existing_plants', existing_plants.ExistingPlantsListView.as_view(), name='existing_plants_list'),
    path('existing_plants/create', existing_plants.ExistingPlantsCreateView.as_view(), name='existing_plants_create'),
    path('existing_plants/<int:pk>/change', existing_plants.ExistingPlantsUpdateView.as_view(), name='existing_plants_change'),
    path('existing_plants/<int:pk>/delete', existing_plants.ExistingPlantsDeleteView.as_view(), name='existing_plants_delete'),

    path('future_plants', future_plants.FuturePlantsListView.as_view(), name='future_plants_list'),
    path('future_plants/create', future_plants.FuturePlantsCreateView.as_view(), name='future_plants_create'),
    path('future_plants/<int:pk>/change', future_plants.FuturePlantsUpdateView.as_view(), name='future_plants_change'),
    path('future_plants/<int:pk>/delete', future_plants.FuturePlantsDeleteView.as_view(), name='future_plants_delete'),
]