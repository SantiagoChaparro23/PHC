from django.http import JsonResponse

import numpy as np
from pandas import DataFrame
from django.shortcuts import render, redirect
from django.core import serializers
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from imports.models import Agent, Fuel, HydrologicalRegion, Metric, Component, PERIODICITY, Resource, River
from decouple import config
import json

@login_required
def index(request):


    metrics = Metric.objects.all()
    metrics = serializers.serialize('json', metrics)

    periods = json.dumps(PERIODICITY)
    
    resamples = [
        ('min', 'Mínimo'),
        ('max', 'Máximo'),
        ('sum', 'Sumatoria'),
        ('avg', 'Promedio'),
    ]

    resamples = json.dumps(resamples)
    version = config('ASSETS_VERSION', default=1)
    context = {
        'metrics': metrics,
        'periods': periods,
        'resamples': resamples,
        'version':version
    }

   
    return render(request, 'search/index.html', context)


def get_components_by_metric(request):


    json_data = json.loads(request.body)
    
    metric_id = json_data['metric']
    custom_filters = []
    if 'custom_filters' in json_data:
        custom_filters = json_data['custom_filters']

   
    metric = Metric.objects.get(pk=metric_id)
   
    components = Component.objects.filter(metric_id=metric).values()

    filters =  get_filters(metric.name_table, custom_filters)    
    #  components = serializers.serialize('json', components)

    id_per = metric.records_periodicity

    avalaible_periodicitys = PERIODICITY[:id_per]

    data = {  
        'data': list( components),
        'filters': filters,
        'metric_name_table': metric.name_table,
        'avalaible_periodicitys': avalaible_periodicitys
    }


    return JsonResponse(data)


def get_filters(table_name, custom_filters):
    
    query = f"SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND column_name LIKE '%_id%' ORDER BY column_name"
    cursor = connection.cursor()
    cursor.execute(query)
    
    filters = cursor.fetchall()    
    filters = [f[0] for f in filters]

    
    data = get_filter_data(filters, table_name, custom_filters, [])
    # print(data)
    return data


def get_filter_data(filters, table_name, custom_filters, ids):
    
    data  = []
    cursor = connection.cursor()

    select = []
    group_by = []
    joins = []
    where = []
    # print(filters)
    if not len(filters):
        return []


    for f in filters:
        if f == 'ciiu_id':
            select.append("concat( imports_ciiu.name, '---', imports_ciiu.id ) as ciiu_id")

            joins.append(f"INNER JOIN imports_ciiu ON imports_ciiu.id = {table_name}.ciiu_id")

            group_by.append('imports_ciiu.id')

            if  'river_id' in custom_filters:
                id = custom_filters['ciiu_id']
                where.append(f'{table_name}.ciiu_id = {id}')



        if f == 'subactivity_id':
            select.append("concat( imports_subactivity.name, '---', imports_subactivity.id ) as subactivity_id")

            joins.append(f"INNER JOIN imports_subactivity ON imports_subactivity.id = {table_name}.subactivity_id")

            group_by.append('imports_subactivity.id')

            if  'river_id' in custom_filters:
                id = custom_filters['subactivity_id']
                where.append(f'{table_name}.subactivity_id = {id}')


        if f == 'river_id':
            select.append("concat( imports_river.name, '---', imports_river.id ) as river_id")

            joins.append(f"INNER JOIN imports_river ON imports_river.id = {table_name}.river_id")

            group_by.append('imports_river.id')

            if  'river_id' in custom_filters:
                id = custom_filters['river_id']
                where.append(f'{table_name}.river_id = {id}')


        if f == 'hydrological_region_id':
            select.append("concat( imports_hydrologicalregion.name, '---', imports_hydrologicalregion.id ) as hydrological_region_id")

            joins.append(f"INNER JOIN imports_hydrologicalregion ON imports_hydrologicalregion.id = {table_name}.hydrological_region_id")

            group_by.append('imports_hydrologicalregion.id')

            if  'hydrological_region_id' in custom_filters:
                id = custom_filters['hydrological_region_id']
                where.append(f'{table_name}.hydrological_region_id = {id}')


        if f == 'fuel_id':
            select.append("concat( imports_fuel.name, '---', imports_fuel.id ) as fuel_id")

            joins.append(f"INNER JOIN imports_fuel ON imports_fuel.id = {table_name}.fuel_id")

            group_by.append('imports_fuel.id')

            if  'fuel_id' in custom_filters:
                id = custom_filters['fuel_id']
                where.append(f'{table_name}.fuel_id = {id}')
            


        if f == 'agent_id':
            select.append("concat( imports_agent.detail, '---', imports_agent.detail ) as agent_detail")
            select.append("concat( imports_agent.activity, '---', imports_agent.activity ) as agent_activity")

            joins.append(f"INNER JOIN imports_agent ON imports_agent.id = {table_name}.agent_id")

            if 'agent_detail' in custom_filters:
                id = custom_filters['agent_detail']
                where.append(f"imports_agent.detail = '{id}'")

            if 'agent_activity' in custom_filters:
                id = custom_filters['agent_activity']
                where.append(f"imports_agent.activity = '{id}'")

            group_by.append('imports_agent.id')


        if f == 'resource_id':
            select.append("concat( imports_resource.name, '---', imports_resource.name ) as resource_name")
            select.append("concat( imports_resource.shipping_type, '---', imports_resource.shipping_type ) as shipping_type")

            select.append("concat( imports_resource.generation_type, '---', imports_resource.generation_type ) as generation_type")

            joins.append(f"INNER JOIN imports_resource ON imports_resource.id = {table_name}.resource_id")

            if 'resource_name' in custom_filters:
                id = custom_filters['resource_name']
                where.append(f"imports_resource.name = '{id}'")

            if 'shipping_type' in custom_filters:
                id = custom_filters['shipping_type']
                where.append(f"imports_resource.shipping_type = '{id}'")


            if 'generation_type' in custom_filters:
                id = custom_filters['generation_type']
                where.append(f"imports_resource.generation_type = '{id}'")

        
            group_by.append('imports_resource.name')
            group_by.append('imports_resource.shipping_type')
            group_by.append('imports_resource.generation_type')

    

    select = ', '.join(select)
    group_by = ', '.join(group_by)
    joins = ' '.join(joins)
    

    if len(where):
        where = ' and '.join(where)
        where = f'WHERE {where}'
    else:
        where = ''

    query = '''
            SELECT
            {}
            FROM {}
            {}
            {}
            GROUP BY {}
            '''.format( select, table_name, joins, where, group_by)

    # print(query)
    cursor.execute(query)
    results = cursor.fetchall()

    columns = [col[0] for col in cursor.description]
    
    df = DataFrame(results, columns=columns)
    

    filters = []
    for filter in columns:
        data = df[filter].drop_duplicates().sort_values()
        
        results = []
        for item in data:
            row = item.split('---')
            if len(row[0]):
                results.append([row[1], row[0]])
        
       
       
        data = {
            'key': filter,
            'name': filter,
            'data': results
        }
        filters.append(data)
    
    
    return filters
  

