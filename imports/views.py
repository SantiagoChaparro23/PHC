from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import redirect, reverse

from django.contrib import messages
from django.db import connection

from django.http import JsonResponse

from .files import (
    agents,
    energy_demand,
    maximun_national_offer_price,
    bag_price,
    offer_price,
    generation,
    net_effective_capacity,
    resources
)

from imports.formats import Format1, Format2, Format3, Format4, Format5
from .helpers import get_urls_metrics


# Common views
def agents_view(request):
    """
    Update agents in the data base
    
    Args:
        request (___): ___
    
    Returns:
        redirect to home
    """

    Format4('https://sinergox.xm.com.co/Histricos/Listado_Agentes.xlsx')
    messages.success(request, 'Importación con exito')
    return redirect('dashboard:home')


def resources_view(request, more_recent:str):
    '''
    Updates ONLY files that have data about resources in their content 
    
    Args:
        request: ___
        more_recent (str bool): Allows you to choose between updating 
                                only recent files or all files registered in the database.
    
                                True: Update only more recent
                                False: Update all
    
    Returns:
        redirect to home
    '''

    cursor = connection.cursor()

    # Ger urls from files with tables_with_column and where more_recent is true or false
    more_recent = more_recent == 'True'
    data_urls = get_urls_metrics(cursor=cursor, tables_with_column='resource_id', more_recent=more_recent)

    print()
    print('Urls to import:')
    print('more_recent: ', more_recent)
    for row in data_urls:
        print(row)
    print()

    # Import resources from all files with format 3
    for row in data_urls:
        print('Processing resources in file: ', row[0])
        Format3(row[0], cursor=cursor)

    messages.success(request, 'Importación con exito')

    return redirect('dashboard:home')


def column_relation_view(request, col_relation:str, more_recent:str):
    """Summary

    Updates elements of relationships whose table has only 2 columns, id and name.
    For example agent_id and resource_id do not fall into this category as they have 
    many other characteristics, but fueld_id, ciiu_id and subactivity_id do.
    
    Args:
        request (___): ___
        col_relation (str): Name of column relation, by example:
                            ciiu_id, subactivity_id

        more_recent (bool str): Allows you to choose between updating 
                                only recent files or all files registered in the database.
    
                                True: Update only more recent
                                False: Update all
    
    Returns:
        redirect to home
    """
    cursor = connection.cursor()


    # Ger urls from files with tables_with_column and where more_recent is true or false
    more_recent = more_recent == 'True'
    data_urls = get_urls_metrics(cursor=cursor, tables_with_column=col_relation, more_recent=more_recent)

    # Import values column with format5
    for row in data_urls:
        print(f'Processing {col_relation} relation in file: ', row[0])
        Format5(row[0], col_relation, cursor=cursor)

    messages.success(request, 'Importación con exito')

    return redirect('dashboard:home')


def import_all_files_view(request, col_relation:str, more_recent:str):
    """Summary
    
    It processes and imports the data of the files registered in the database, 
    choosing the processor according to its type of format.    
    
    Args:
        request (___): ___
        col_relation (str): Name of column relation, by example:
                            ciiu_id, subactivity_id        
        more_recent (str bool): Allows you to choose between updating 
                                only recent files or all files registered in the database.
    
                                True: Update only more recent
                                False: Update all

    
    Returns:
        redirect to home
    
    Raises:
        NotImplementedError: Currently here only process files with data in format 1 and format 2
                             Data with a file in other format gonna raise this exception
    """


    cursor = connection.cursor()


    # Ger urls from files with tables_with_column and where more_recent is true or false
    more_recent = more_recent == 'True'
    
    if col_relation is 'None':
        col_relation = None    

    data_urls = get_urls_metrics(cursor=cursor, more_recent=more_recent, tables_with_column=col_relation)

    print()
    print('Urls to import:')
    print('more_recent: ', more_recent)
    for row in data_urls:
        print(row)
    print()    

    # Import values column with format5
    for row in data_urls:

        try:
            
            url = row[0]
            frmat = row[4]
            name_table = row[5]

            print()
            print(f'Processing metric {name_table} with format {frmat} in file : ', row[0])

            if frmat == 1:
                Format1(row[0], name_table, cursor=cursor)

            elif frmat == 2:
                Format2(row[0], name_table, cursor=cursor)

            else:
                raise NotImplementedError(f'Format {frmat} for {url} not implemented or not in "if" list')

        except Exception as e:
            print(f'    ERROR GENERADO AL IMPORTAR ARCHIVO, tabla: {name_table}, format: {frmat} file: ', row[0])
            print(e)       

    messages.success(request, 'Importación con exito')

    return redirect('dashboard:home')


def get_files_download_view(request):
    """Summary

    Delivers the list of files to import on a regular basis, 
    which by default are those of the last 2 years    
    
    Args:
        request (___): ___
    
    Returns:
        json with list of info about files to download 
    """
    current_year = datetime.now().year

    print('current_year: ', current_year)

    list_files_current_year = get_urls_metrics(year=current_year)
    list_files_previous_year = get_urls_metrics(year=current_year-1)

    list_files_current_year.extend(list_files_previous_year)
    print(list_files_current_year[3])
    list_files = [{'url_file':row[0], 
    'format':row[4], 
    'name_table':row[5], 
    'records_periodicity':row[6], 
    'id_metric':row[7],
    'url': reverse('dashboard:files_metrics_process', args=[row[7]])
    }
                        for row in list_files_current_year]

    return JsonResponse({'files': list_files})


# Develop views
def test_view(request):

    print('TESTEO')
    # Format1('http://portalbissrs.xm.com.co/oferta/Histricos/Generaci%C3%B3n/Generacion_de_Seguridad_(kWh)_2003.xlsx', 'imports_securitygeneration')
    # Format3('http://portalbissrs.xm.com.co/oferta/Histricos/Generaci%C3%B3n/Generacion_de_Seguridad_(kWh)_2003.xlsx')
    # Format3('http://portalbissrs.xm.com.co/oferta/Histricos/Capacidad/Capacidad_Efectiva_Neta_(kW)_2019.xlsx')
    # Format1('http://portalbissrs.xm.com.co/oferta/Histricos/Generaci%C3%B3n/Generacion_(kWh)_2016SEM1.xlsx', 'imports_generation')
    # Format1('http://portalbissrs.xm.com.co/oferta/Histricos/Generaci%C3%B3n/Generacion_(kWh)_2015.xls', 'imports_generation')
    # Format2('http://portalbissrs.xm.com.co/oferta/Histricos/Capacidad/Capacidad_Efectiva_Neta_(kW)_2019.xlsx', 'imports_neteffectivecapacity')

    return redirect('dashboard:home')


def import_custom_dates(request):
    import pandas as pd
    import numpy as np
    df_niños = pd.read_csv('cache/datos_niño_niña_precio_bolsa.csv', sep=';')
    df_niños['AÑO'] = df_niños['AÑO'].astype(str)
    df_niños['MES'] = df_niños['MES'].astype(str)
    df_niños['MES'] = [s if len(s)==2 else '0'+s for s in df_niños['MES'].values]
    df_niños['date'] = df_niños['AÑO'] + '-' + df_niños['MES'] + '-01'

    phe = list()
    for i in df_niños.index:
        date = df_niños.loc[i, 'date']
        if isinstance(df_niños.loc[i, 'Fenómeno del Niño'], str):
            phe.append((date, 2))
        elif isinstance(df_niños.loc[i, 'Fenómeno de la Niña'], str):
            phe.append((date, 1))

    cursor = connection.cursor()

    for date, id_phe in phe:
        query = '''
            INSERT INTO "imports_nationalbagpricecustomdates"("date", "phenomenon") VALUES
            ('{}', '{}');
            '''.format(date, id_phe)

        cursor.execute(query)
