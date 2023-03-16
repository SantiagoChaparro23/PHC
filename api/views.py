import io
import os
import operator

from django.http import HttpResponse

from django.shortcuts import render
import datetime
import json
from dashboard.helpers.charts import (
                                    monthlyBagPrices,
                                    yearlyBagPrices,
                                    maximumNationalOfferPrice,
                                    generation, 
                                    netEffectiveCapacity,
                                    calculateMarginalPlant, 
                                    check_and_defaults_marginal_plant)

from django.core.serializers import serialize
                                 
from django.http import JsonResponse
from django.db import connection

import numpy as np
import pandas as pd
import xlsxwriter

from .files import generalize_query_code
from django.conf import settings


def index(request):
    """Summary

    Function to perform time series queries in the database, 
    in addition to calculating other elements such as histograms, 
    descriptive statistics and other elements, 
    in this function the conversion between different 
    prefixes of scientific notation is also applied if 
    there are any in the request.
    
    Args:
        request : Django request
    
    Returns:
        Json: Description
    """
    cursor = connection.cursor()

    # Take multiplier
    symbol_multiplier = request.GET.get('symbol_multiplier', None)


    # Take parameters to query
    id_component = request.GET['id_component']
    int_periodicity = request.GET.get('int_periodicity', 4)
    resample_method = request.GET.get('resample_method', 'sum')
    amount_bins = int(request.GET.get('amount_bins', 10))

    start_date = request.GET.get('start_date', '2000-01-01')
    end_date = request.GET.get('end_date', '2099-01-01')


    #   The order is important, DONT TOUCH, read first documentation from function in generalize_query_code
    lst_filters_names = ['agent_id', 'ciiu_id', 'fuel_id', 
                         'hydrological_region_id', 'market_id', 'river_id', 
                         'subactivity_id']
    id_direct_filters = [request.GET.get(json_var, -1) for json_var in lst_filters_names]

    lst_filters_names = ['agent_detail', 'agent_activity', 'resource_name', 
                         'generation_type', 'shipping_type']
    str_indirect_filters = [request.GET.get(json_var, 'NULL') for json_var in lst_filters_names]


    # Execute query and get data
    query = generalize_query_code.format(id_component, int_periodicity, resample_method,
                                             str(start_date), str(end_date),
                                             str(id_direct_filters), str(str_indirect_filters))

    # print(query)
    cursor.execute(query)

    query_data = cursor.fetchall()[0]

    # Convert units, values, prefixes of scientific notation
    values_array = np.array(query_data[1], dtype=np.float)
    unit         = query_data[2]

    # print()
    # print('values_array: ', values_array)
    # print()


    # This is 0 only if values_array have np.nan's
    sum_arr = np.nansum(values_array)

    # Calculate only if 
    if sum_arr > 0:

        if unit == '%':
            pass

        else:

            cmom = ConverterMultiplesOfMagnitudes()
            #   Detect and apply better multiplier
            if symbol_multiplier is None:
                unit, values_array, symbol_multiplier = cmom.improve_unit_multiplier(unit, values_array)

            #   Apply a wished multiplier
            else:
                unit, values_array = cmom.apply_wished_multiplier(symbol_multiplier, unit, values_array)


        # Calculate histogram
        #   Firts remove None's, without this calculate histogram raise errors
        arr = np.array(query_data[1])
        whithout_nan = arr[arr!=None]
        frecuency, bin_edges = np.histogram(whithout_nan, bins=amount_bins, density=False)

        # Assemble data to return
        values_array = np.where(np.isnan(values_array), None, values_array)

    else:

        bin_edges = np.array([])
        frecuency = np.array([])
        symbol_multiplier = 0  


    data = {
        'time_array'        : query_data[0],
        'values_array'      : values_array.tolist(),

        'unit'              : unit,
        'symbol_multiplier' : symbol_multiplier,
        'average'           : query_data[3],
        'median'            : query_data[4],
        'maximum'           : query_data[5],
        'minimum'           : query_data[6],
        'percentile_05'     : query_data[7],
        'percentile_95'     : query_data[8],
        'standard_deviation': query_data[9],

        'bin_edges'         : list(bin_edges.astype(float)),
        'frecuency'         : list(frecuency.astype(float)),
    }

    return JsonResponse(data)


def download_graphed_data(request):
    """Summary
    
    Stores the data of a time series plotted in the front 
    of the query section of the mec in an xlsx file to allow its later download 
    using a HttpResponse

    Args:
        request : Django request
    
    Returns:
        HttpResponse
    """
    base = settings.PROJECT_PATH
    path_file = f'{base}/cache/datos_consulta_mec.xlsx'

    # Get array of data with all data about series
    all_data = json.loads(request.body)

    save_data_xlsx(all_data, path_file)
    
    # sending response 
    response = HttpResponse(io.open(path_file, mode="rb").read(), content_type='application/xlsx')
    response['Content-Disposition'] = 'attachment; filename="datos_consulta_mec.xlsx"'

    # delete .xlsx file
    os.remove(path_file)
 
    return response


def save_data_xlsx(all_data:list, path_file:str):
    """Summary
    
    Stores the data of a time series plotted in the front of 
    the query section of the mec in an xlsx file.
    Each time series is on a different excel sheet with its 
    corresponding search parameters and filters used    
    
    Args:
        all_data (list): List with time series data
        path_file (str): Path where save the generate xlsx file
    """
    # Save all data in a excel file
    #   Initialize writer
    writer = pd.ExcelWriter(path_file, engine='xlsxwriter')
    workbook = writer.book

    # Iterate about array from graphed data
    for i, time_serie_data in enumerate(all_data):

        # Add a new sheet with, the max sheet name is 31 characters, 
        # so we use the first 31 characters
        sheet_name =  str(i) + ' ' + time_serie_data['component']['component']
        if len(sheet_name) > 31:
            sheet_name = sheet_name[:31]

        worksheet = workbook.add_worksheet(sheet_name)
        writer.sheets[sheet_name] = worksheet


        # Add meta data about the query
        worksheet.write_string(0, 0, sheet_name)

        worksheet.write_string(1, 0, 'Metrica:')
        worksheet.write_string(1, 1, time_serie_data['metric']['fields']['metric'])

        worksheet.write_string(2, 0, 'Componente:')
        worksheet.write_string(2, 1, time_serie_data['component']['component'])

        worksheet.write_string(3, 0, 'Unidades:')
        worksheet.write_string(3, 1, time_serie_data['unit'])

        worksheet.write_string(4, 0, 'Periodicidad:')
        worksheet.write_string(4, 1, time_serie_data['period'][1])

        worksheet.write_string(5, 0, 'Intervalo temporal:')
        worksheet.write_string(5, 1, time_serie_data['start_date'][:10])
        worksheet.write_string(5, 2, time_serie_data['limit_date'][:10])

        worksheet.write_string(6, 0, 'Metodo de resampleo:')
        worksheet.write_string(6, 1, time_serie_data['resample'][1])


        # Add inferential statistics
        worksheet.write_string(1, 4, 'Media:')
        worksheet.write_string(1, 5, str(time_serie_data['response']['average']))

        worksheet.write_string(2, 4, 'Mediana:')
        worksheet.write_string(2, 5, str(time_serie_data['response']['average']))

        worksheet.write_string(3, 4, 'Maxima:')
        worksheet.write_string(3, 5, str(time_serie_data['response']['maximum']))

        worksheet.write_string(4, 4, 'Minima:')
        worksheet.write_string(4, 5, str(time_serie_data['response']['minimum']))

        worksheet.write_string(5, 4, 'Percentil 05:')
        worksheet.write_string(5, 5, str(time_serie_data['response']['percentile_05']))

        worksheet.write_string(6, 4, 'Percentil 95:')
        worksheet.write_string(6, 5, str(time_serie_data['response']['percentile_95']))

        worksheet.write_string(7, 4, 'Desviación estandar:')
        worksheet.write_string(7, 5, str(time_serie_data['response']['standard_deviation']))


        # Add filters
        worksheet.write_string(1, 7, 'Filtros:')
        for i, (filter_key, value) in enumerate(time_serie_data['f'].items()):
            worksheet.write_string(1+i, 8, filter_key)
            worksheet.write_string(1+i, 9, value[1])


        # Add info from time series
        #   Values
        worksheet.write_string(9, 0, 'Serie de tiempo:')
        data = {
            'Fecha': time_serie_data['response']['time_array'],
            'Valor': time_serie_data['response']['values_array']
            }
        df = pd.DataFrame(data)
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%Y-%m-%dT%H:%M:%S')
        df.to_excel(writer, sheet_name=sheet_name, startrow=10, startcol=0, index=False)

        #   Histogram
        worksheet.write_string(9, 4, 'Histograma:')
        bin_edges = time_serie_data['response']['bin_edges']
        processed_bins = [f'{bin_edges[i-1]}-{bin_edges[i]}' for i in range(1, len(bin_edges))]
        data = {
            'Bins': processed_bins,
            'Frecuencia': time_serie_data['response']['frecuency']
            }
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet_name, startrow=10 , startcol=4, index=False)


        # Adjust width of columns
        for i in range(10):
            worksheet.set_column(i, i, 23)    

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()    


class ConverterMultiplesOfMagnitudes(object):

    """Summary
    
    Attributes:
        MULTIPLES_OF_QUANTITIES (TYPE): Description
    """
    
    # Font: 
    # https://www.electronicafacil.net/tutoriales/Multiplos-submultiplos-unidades-magnitudes-fisicas-electronica.html
    MULTIPLES_OF_QUANTITIES = {
        # Symbol : Value
        #   Multiple
        'E': 10**18,
        'P': 10**15,
        'T': 10**12,
        'G': 10**9,
        'M': 10**6,
        'k': 10**3,
        'h': 10**2,
        'da': 10**1,

        #   Not multiple
        '': 1, 

        #   Submultiple
        'd': 10**(-1),
        'c': 10**(-2),
        'm': 10**(-3),
        'μ': 10**(-6),
        'n': 10**(-9),
        'p': 10**(-12),
        'f': 10**(-15),
        'a': 10**(-18)
    }

    def improve_unit_multiplier(self, original_unit:str, 
                                values_array:np.array) -> (str, np.array, str):
        """
        Process for get better multiplier:
            - Deduce the most appropriate multiplier to apply 
              looking for the array values to be in magnitudes between 0 and 1000,
              using deduct_proper_multiplier()
              Sometimes there is no exact symbol for the resulting multiplier, 
              so a new conversion is applied to the closest existing multiplier. 
              Example: 1da*1k = 1*10**4, in this case we will apply the closest multiplier
        
            - Get the original multiplier from the array values using get_multiple()
        
            - Apply the multiplier to the values of the array, 
              this will make the values remain with the desired magnitudes, 
              however the unit cannot be replaced by the old one, 
              the closest to the desired result must be sought.
              For example:
              If I have 1000.000k, the 1G multiplier will leave the value in the desired range, 
              but the result will not be 1G, 
              it will be 1T because the exponents of the multipliers are added.
        
        Args:
            original_unit (str): Original unit of time serie
            values_array (np.array): Values array of time serie
        
        Returns:
            str : New unit of time serie with applied multiplier, example: 'kWh', GWh
            np.array: Array with applied multiplier
            str : Notation of final multiplier, example: 'k', 'G'
        """
        
        symb_origin, mult_origin = self.get_multiple(original_unit)
        symb_better, mult_better = self.deduct_proper_multiplier(mult_origin, values_array)

        new_unit, new_array, symb_final = self.apply_multiplier_to_array(mult_better, mult_origin,
                                                             original_unit, values_array)


        return new_unit, new_array, symb_final

    def get_multiple(self, unit:str) -> (str, int):
        """Summary

        Deduce numeric multiplier and his symbol using the original unit from
        the time serie
        
        Args:
            unit (str): Original unit of a time serie, example: '<<k>>Wh', '<<G>>Wh'
                        in the same format used in the data base
        
        Returns:
            str : Symbol of multiplier in scientific notation, example: 'k', 'M', 'G'
            int : Numeric multiplier of symbol, by example for 'k' the numeric 
                  multiplier is 10**3, for 'M' is 10**6
        """
        ini = unit.find('<') + 1
        end = unit.find('>')

        # If symbol multiplier is not detected, then multiplier is 1
        if ini == -1 or end == -1:
            multiplier = 1
            symbol = ''

        # In other case, use the dict MULTIPLES_OF_QUANTITIES to get symbol and numeric
        # multiplier
        else:
            symbol = unit[ini:end]
            multiplier = self.MULTIPLES_OF_QUANTITIES[symbol]

        return symbol, multiplier

    def deduct_proper_multiplier(self, original_multiplier:int, values_array:np.array) -> (str, int):
        """Summary
        
        Args:
            original_multiplier (int): Description
            values_array (np.array): Description
        
        Returns:
            str, int: Description
        """
        mean = np.nanmean(values_array)

        get_exponent = lambda mean, mult: int(np.floor(np.log10(np.abs(mean)/mult)))

        proportions = [(sym, abs(get_exponent(mean, m) - 2)) 
                            for sym, m in self.MULTIPLES_OF_QUANTITIES.items()]

        proportions.sort(key=operator.itemgetter(1))

        # Is the result from multip_better and multip_origin a valid multip_final?
        #     Iterate until found a valid multiplier
        for proposed_symb, _ in proportions:            
            proposed_mult = self.MULTIPLES_OF_QUANTITIES[proposed_symb]

            final_multiplier = original_multiplier*proposed_mult
            try:
                final_symbol = self.multiplier2symbol(final_multiplier)

            except ValueError:
                pass

            else:
                better_symbol     = proposed_symb
                better_multiplier = proposed_mult

                break

        return better_symbol, better_multiplier

    def apply_multiplier_to_array(self, new_mult:int, old_mult:int, original_unit:str, 
                                        values_array:np.array) -> (str, np.array, str):

        # Apply wished multiplier to data array
        processed_array = values_array/new_mult

        # Combine the multipliers to get the final multiplier
        final_multiplier = new_mult*old_mult

        symb_final = self.multiplier2symbol(final_multiplier)

        # Create the new unit
        ini = original_unit.find('<')
        end = original_unit.find('>') + 1

        new_unit = original_unit[:ini] + symb_final + original_unit[end:]

        return new_unit, processed_array, symb_final

    def multiplier2symbol(self, multiplier):

        for k, v in self.MULTIPLES_OF_QUANTITIES.items():
            if multiplier == v:
                return k

        raise ValueError('Multiplier not found')

    def apply_wished_multiplier(self, symb_mult_to_apply:str, original_unit:str, 
                                      values_array:np.array) ->(str, np.array):

        multiplier_to_apply = self.MULTIPLES_OF_QUANTITIES[symb_mult_to_apply]
        origin_symbol, origin_mult = self.get_multiple(original_unit)

        # Apply wished multiplier to data array
        processed_array = values_array*(origin_mult/multiplier_to_apply)

        # Create the new unit
        ini = original_unit.find('<')
        end = original_unit.find('>') + 1

        new_unit = original_unit[:ini] + symb_mult_to_apply + original_unit[end:]

        return new_unit, processed_array        











