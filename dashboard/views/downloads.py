import io

import pandas as pd
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dashboard.helpers.charts import (calculateMarginalPlant, 
                                      check_and_defaults_marginal_plant, dailyContributionsByMonth, 
                                      generation, 
                                      netEffectiveCapacity,
                                      check_and_defaults_net_effective_capacity,
                                      maximumNationalOfferPrice,
                                      yearlyBagPrices,
                                      monthlyBagPrices,
                                      usefulDailyVolumePercentage
                                      )

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def standard_downloads(request):
    """

        Process downloads of submits buttons for download data from standard graphics 

        References:
            https://stackoverflow.com/questions/20448911/get-id-of-one-of-multiple-buttons-in-html-form-in-django
    """

    if 'net_effective_capacity' in request.GET.keys():

        date = check_and_defaults_net_effective_capacity(request)
        data = list(zip(*netEffectiveCapacity(date)[:3]))

        df = pd.DataFrame(data, columns=['Tecnología', 'Capacidad[MW]', 'Participacion[%]'])

        return df2xlsx_response(df, 'Capacidad efectiva neta.xlsx')        

    elif 'generation' in request.GET.keys():
        
        data, _, names_traces = generation()
        data = list(zip(*data))

        name_columns = ['Fecha'] + names_traces + ['Participacion termica']        
        df = pd.DataFrame(data, columns=name_columns)

        return df2xlsx_response(df, 'Generacion.xlsx')

    elif 'monthly_bag_price' in request.GET.keys():

        monthly_bag_prices_chart, girl_phenomenons, boy_phenomenons = monthlyBagPrices()

        df = pd.DataFrame({'Fecha':monthly_bag_prices_chart[0], 'Precio de bolsa':monthly_bag_prices_chart[1]}).set_index('Fecha')
        df['Niño'] = ''
        df['Niña'] = '' 
        for d, v  in zip(*girl_phenomenons):
            print(d, v)
            df.loc[d, 'Niña'] = v

        for d, v  in zip(*boy_phenomenons):
            print(d, v)
            df.loc[d, 'Niño'] = v  

        df.reset_index(inplace=True)
        
        return df2xlsx_response(df, 'Precio de bolsa mensual.xlsx')

    elif 'yearly_bag_price' in request.GET.keys():

        data = yearlyBagPrices()
        df = pd.DataFrame(data)
        df = df.T
        df.columns  = ['Fecha', 'Valor']
        #df = pd.DataFrame(data, columns=['Fecha', 'Valor'])
        return df2xlsx_response(df, 'Precio de bolsa anual.xlsx')

    elif 'energy_demand' in request.GET.keys():
       
        data = maximumNationalOfferPrice()
        df = pd.DataFrame(data)
        df = df.T
        df.columns  = ['Fecha', 'Valor']
        return df2xlsx_response(df, 'Demanda de energia.xlsx')

    elif 'marginal_plant' in request.GET.keys():

        start, end, amount_plants, margin_error = check_and_defaults_marginal_plant(request)
        data = list(zip(*calculateMarginalPlant(start, end, amount_plants, margin_error)))

        df = pd.DataFrame(data, columns=['Planta', 'Veces que margina'])

        return df2xlsx_response(df, 'Planta que margina.xlsx')        

    elif 'useful_percentage_chart' in request.GET.keys():
        data = usefulDailyVolumePercentage()
        
        df = pd.DataFrame(data).T
        df.columns = ['Fecha', 'Valor']

        return df2xlsx_response(df, 'Embalse Agregado del Sistema.xlsx')        

    elif 'daily_contributions_by_month' in request.GET.keys():
        data = dailyContributionsByMonth()
        
        df = pd.DataFrame(data)

        return df2xlsx_response(df[::-1], 'Historico Aportes Diario.xlsx')

    else:
        raise NotImplementedError('Standard download for this file not implemented')


def df2xlsx_response(df, name_file):
    """
        References:
            https://stackoverflow.com/questions/28058563/write-to-stringio-object-using-pandas-excelwriter
            https://stackoverflow.com/questions/48488697/python-django-offering-a-zip-file-for-download-from-io-bytesio-buffer  
    """


    base = settings.PROJECT_PATH

    path_file = f'{base}/cache/{name_file}'
   
    # Write dataframe in a buffer
    writer = pd.ExcelWriter(path_file, engine='xlsxwriter')

    df.to_excel(writer, index=False)
    writer.save() 

    # Define response object with xlsx file
    response = HttpResponse(io.open(path_file, mode="rb").read(), content_type='application/xlsx')
    response['Content-Disposition'] = f'attachment; filename={name_file}'

    return response