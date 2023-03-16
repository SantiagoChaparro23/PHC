import json
from operator import itemgetter
from collections import Counter
from datetime import datetime as dt, timedelta

import pandas as pd
from numpy import isnan
from django.db import connection
from imports.models import NetEffectiveCapacity, Resource, NationalBagPriceCustomDates

from django.conf import settings
from xlsx2csv import Xlsx2csv

def generation():
   
    cursor = connection.cursor()


    query = '''
        WITH sum_fuels as (
            select date_trunc('month', date) as date, sum(hour_0 + hour_1 + hour_2 + hour_3 + hour_4 + hour_5 + hour_6 + hour_7 + hour_8 + hour_9 + hour_10 + hour_11 + hour_12 + hour_13 + hour_14 + hour_15 + hour_16 + hour_17 + hour_18 + hour_19 + hour_20 + hour_21 + hour_22 + hour_23) as suma, fuel_id 
            from public.imports_generation
            group by date_trunc('month', date), fuel_id
        ), sum_agua as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 1
        ), sum_acpm as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 2
        ), sum_gas as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 3
        ), sum_gas_ni as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 4
        ), sum_bagazo as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 5
        ), sum_biogas as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 6
        ), sum_biomasa as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 7
        ), sum_carbon as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 8
        ), sum_combustoleo as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 9
        ), sum_rad_solar as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 10
        ), sum_viento as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 11
        ), sum_fueloil as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 12
        ), sum_jet_a1 as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 13
        ), sum_mezcla as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 14
        ), sum_querosene as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 15
        ), sum_null as(
            select date, suma from sum_fuels where sum_fuels.fuel_id = 16   
        ), table_fuels as(

            -- Group fuels in types of fuels
            select to_char(sum_agua.date, 'YYYY-MM-DD') as date, 
                   coalesce(sum_agua.suma, 0)/1000000.0 as hidraulica,
                   (coalesce(sum_gas.suma, 0) + coalesce(sum_gas_ni.suma, 0) + coalesce(sum_biogas.suma, 0))/1000000.0 as gas,
                   (coalesce(sum_biomasa.suma, 0) + coalesce(sum_bagazo.suma, 0))/1000000.0 as biomasa,
                   coalesce(sum_carbon.suma, 0)/1000000.0 as carbon,
                   (coalesce(sum_combustoleo.suma, 0) + coalesce(sum_acpm.suma, 0) + coalesce(sum_fueloil.suma, 0) + coalesce(sum_jet_a1.suma, 0) + coalesce(sum_mezcla.suma, 0) + coalesce(sum_querosene.suma, 0))/1000000.0 as liquidos,
                   coalesce(sum_rad_solar.suma, 0)/1000000.0 as solar,
                   coalesce(sum_viento.suma, 0)/1000000.0 as eolica
                   -- coalesce(sum_null.suma, 0)/100000000.0 as null
                   from sum_agua

            full outer join sum_acpm 
            on sum_agua.date = sum_acpm.date
            full outer join sum_gas 
            on sum_agua.date = sum_gas.date
            full outer join sum_gas_ni 
            on sum_agua.date = sum_gas_ni.date
            full outer join sum_bagazo 
            on sum_agua.date = sum_bagazo.date
            full outer join sum_biogas 
            on sum_agua.date = sum_biogas.date
            full outer join sum_biomasa 
            on sum_agua.date = sum_biomasa.date
            full outer join sum_carbon 
            on sum_agua.date = sum_carbon.date
            full outer join sum_combustoleo 
            on sum_agua.date = sum_combustoleo.date
            full outer join sum_rad_solar 
            on sum_agua.date = sum_rad_solar.date
            full outer join sum_viento 
            on sum_agua.date = sum_viento.date
            full outer join sum_fueloil 
            on sum_agua.date = sum_fueloil.date
            full outer join sum_jet_a1 
            on sum_agua.date = sum_jet_a1.date
            full outer join sum_mezcla 
            on sum_agua.date = sum_mezcla.date
            full outer join sum_querosene 
            on sum_agua.date = sum_querosene.date
            full outer join sum_null 
            on sum_agua.date = sum_null.date
        )

        -- We need know thermal participation too, so in this line we calculate this
        select *, ((gas + liquidos + biomasa + carbon)/(hidraulica + gas + biomasa + carbon + liquidos + solar + eolica + 0.000001))*100 as participacion_termica 
        from table_fuels
        where date  >= '2008-01-01 00:00:00'
        order by date desc;
       
    '''

    
    # Grafica de generacion ---------------
    cursor.execute(query) 

    # Sometimes query have nan's, change for none's, nan's generate errors in javascript
    generation_chart = [list(row) for row in list(zip(*cursor.fetchall()))]
    for i in range(len(generation_chart)):
        for j in range(len(generation_chart[0])):

            cell = generation_chart[i][j]

            if isinstance(cell, float) :
                if isnan(generation_chart[i][j]):
                    generation_chart[i][j] = None
    
    names_traces = ['Hidráulica', 'Gas', 'Biomasa', 'Carbon', 'Líquidos', 'Solar', 'Eólica']

    colors_generation = {
            'Hidráulica' : 'rgb(2, 97, 161)',
            'Gas'     : 'rgb(237, 125, 49)',
            'Biomasa' : 'rgb(255, 192, 0)',
            'Carbon'  : 'rgb(165, 165, 165)',
            'Solar'   : 'rgb(255, 255, 0)',
            'Eólica'  : 'rgb(0, 176, 80)',
            'Líquidos': 'rgb(255, 0, 0)'
    }

    return  generation_chart,  colors_generation,  names_traces


def calculateMarginalPlant(start, end, amount_plants, margin_error):

    cursor = connection.cursor()

    #   This function return a column with pland id's where each row means that one plant margined that time
    cursor.execute('''
        DROP FUNCTION IF EXISTS calculate_marginal_plant;

        CREATE OR REPLACE FUNCTION calculate_marginal_plant(ini_date date, end_date date, margin_error float8) 
        RETURNS TABLE(
                    plants text
                )
        AS $$
            DECLARE

                -- For iterate            
                d date;
                old_value integer;
                hour_col_name text;
                hours_cols text[][] := array['hour_0', 'hour_1', 'hour_2', 'hour_3', 'hour_4', 'hour_5', 'hour_6', 'hour_7', 'hour_8', 'hour_9', 'hour_10', 'hour_11', 'hour_12', 'hour_13', 'hour_14', 'hour_15', 'hour_16', 'hour_17', 'hour_18', 'hour_19', 'hour_20', 'hour_21', 'hour_22', 'hour_23'];
                
                -- For calculate
                mpo_day double precision;
                margin_plant text;
                value_margin float8;
                columna text;       
 
            BEGIN

                -- Create a temporal table to keep the number of times that one plants margin 
                DROP TABLE IF EXISTS times_margin;
                CREATE TEMP TABLE times_margin (
                    plant text
                );      
                
                -- iterates over days from imports_maximumnationalofferprice?
                FOR d IN SELECT DISTINCT imports_offerprice.date
                         FROM imports_offerprice 
                         WHERE imports_offerprice.date BETWEEN ini_date AND end_date
                LOOP                        
                    
                    -- Iterate over columns of hours from imports_offerprice
                    FOREACH hour_col_name IN ARRAY hours_cols
                    
                    LOOP
                    
                        -- Select maximum offer price from hour and day in currently iteration
                        EXECUTE format('SELECT %I 
                                        FROM imports_maximumnationalofferprice
                                        WHERE imports_maximumnationalofferprice.date = %L', 
                                        hour_col_name, d) 
                        INTO mpo_day;
                        
                        -- Select margin plant for this hour with value closest to offer price
                        SELECT resource_id, ideal_offer_price, ABS(mpo_day - margin_error) AS difference
                        INTO margin_plant, value_margin
                        FROM imports_offerprice
                        WHERE imports_offerprice.date = d
                        AND imports_offerprice.ideal_offer_price BETWEEN mpo_day - margin_error AND mpo_day + margin_error
                        ORDER BY difference ASC
                        LIMIT 1;
                        
                        -- Add one row with the plant name
                        INSERT INTO times_margin VALUES (margin_plant);
                    
                    END LOOP;
                 
                END LOOP;   

                RETURN QUERY SELECT plant FROM times_margin;
                
            END;
        $$ 
        LANGUAGE plpgsql;

        SELECT calculate_marginal_plant('{}', '{}', {});
    '''.format(start, end, float(margin_error))
    )

    #   Count times that margined every plant
    times_margin_plants_by_id = Counter([row[0] for row in cursor.fetchall()])

    #    Sometimes exist lost data, thus is imposible found the margin plant, delete this register before of continue
    try:
        del times_margin_plants_by_id[None]
    except:
        pass

    #   Change plant id's by names, sort and send in context only the require amount of plants
    resources_id2name = {dct['id']: dct['name'] for dct in Resource.objects.values('name', 'id')}

    times_margin_plants = [(resources_id2name[int(id_plant)], times_margin) for id_plant, times_margin in times_margin_plants_by_id.items()]
    times_margin_plants.sort(key=itemgetter(1), reverse=True)
    marginal_plant_chart = list(zip(*times_margin_plants[:amount_plants]))

    cursor.close()

    return marginal_plant_chart


def check_and_defaults_marginal_plant(request):


    def get_older_date_from_used_metrics():

        cursor = connection.cursor()

        cursor.execute('''SELECT date FROM imports_maximumnationalofferprice 
                          ORDER BY date DESC LIMIT 1;''')

        last_date_mnop = cursor.fetchall()[0][0]

        cursor.execute('''SELECT date FROM imports_offerprice 
                          ORDER BY date DESC LIMIT 1;''')

        last_date_op = cursor.fetchall()[0][0]

        # start = more older record - 1 year
        if last_date_mnop > last_date_op:
            older_date = last_date_op
        else:
            older_date = last_date_mnop

        return older_date


    if 'start_plant_margin' in request.GET:
        start_str = request.GET['start_plant_margin']
        end_str = request.GET['end_plant_margin']
        amount_plt_str = request.GET['amount_plant_margin']
    else:
        start_str = ''
        end_str = ''
        amount_plt_str = ''    

    margin_error = 1.0 

    # Query the more recent dates from the two used metrics, use as end the older date
    # - Do this ONLY if start_str or end_str not are specified, this happen when the page is
    #   loaded for first time
    # - We use the more older date because we need data from two used metrics for do calculates
    #       For start date
    if start_str == '':

        older_date = get_older_date_from_used_metrics()
        start = (older_date - timedelta(days=365)).strftime("%Y-%m-%d") 

    else:
        start = start_str

    #       For end date
    if end_str == '':

        older_date = get_older_date_from_used_metrics()
        end = older_date.strftime("%Y-%m-%d") 

    else:
        end = end_str
 

    amount_plants = 10 if amount_plt_str == '' else int(amount_plt_str)

    return start, end, amount_plants, margin_error


def maximumNationalOfferPrice():
    cursor = connection.cursor()
    cursor.execute('''
        SELECT
             -- date_trunc('year', date) AS year,
             EXTRACT(YEAR FROM date)::INTEGER AS year,
             SUM(energy_demand_sin) AS yearly_sum
        FROM imports_energydemandsin
        GROUP BY year
        ORDER BY year        
    ''')
    query = cursor.fetchall()

    print(query)

    # Calculate grow rate
    maximum_national_offer_price_chart = list()

    #   Drop first 2 and last one, are calculate with incomplete data
    query = query[2:-1]

    for i in range(1, len(query)):
        date, current_val = query[i]
        prev_val = query[i-1][1]

        mnop = round(100*((current_val-prev_val)/prev_val), 4)

        maximum_national_offer_price_chart.append((date, mnop))

    

    maximum_national_offer_price_chart = list(zip(*maximum_national_offer_price_chart))

    return maximum_national_offer_price_chart


def netEffectiveCapacity(date):

    cursor = connection.cursor()


    cursor.execute('''
        SELECT
            r.generation_type,
            r.shipping_type,
            f.name as fuel,
            r.clasification,
            SUM(c.net_effective_capacity)/1000
        FROM
            imports_neteffectivecapacity c
            
       INNER JOIN imports_resource r
           ON r.id = c.resource_id

        INNER JOIN imports_fuel f
            ON f.id = c.fuel_id
        WHERE
            c.date = '{}'
        GROUP BY r.generation_type, r.shipping_type, f.name, r.clasification
    '''.format(date))
    chart4 = cursor.fetchall()

    df = pd.DataFrame(chart4, columns=['gen_type', 'ship_type', 'fuel', 'clas', 'value'])

    data_neteffectivecapacity = {

        "Hidráulica"       : df.loc[(df.gen_type=='HIDRAULICA') &
                                    (df.ship_type=='DESPACHADO CENTRALMENTE'), 'value'].sum(),

        "Gas"              : df.loc[(df.fuel=='GAS') &
                                    (df.ship_type=='DESPACHADO CENTRALMENTE'), 'value'].sum(),

        "Carbon"           : df.loc[(df.fuel=='CARBON') &
                                    (df.ship_type=='DESPACHADO CENTRALMENTE'), 'value'].sum(),

        "Líquidos"         : df.loc[((df.fuel=='ACPM') | (df.fuel=='JET-A1') | (df.fuel=='COMBUSTOLEO')) &
                                    (df.ship_type=='DESPACHADO CENTRALMENTE'), 'value'].sum(),

        "NDC Hidráulica"   : df.loc[(df.gen_type=='HIDRAULICA') &
                                    (df.ship_type=='NO DESPACHADO CENTRALMENTE'), 'value'].sum(),

        "NDC Térmica"      : df.loc[(df.gen_type=='TERMICA') &
                                    (df.ship_type=='NO DESPACHADO CENTRALMENTE') &
                                    (df.clas!='AUTOGENERADOR') & (df.clas!='AUTOG PEQ. ESCALA'), 'value'].sum(),

        "Cogenerador"  : df.loc[(df.gen_type=='COGENERADOR') &
                                    (df.ship_type=='NO DESPACHADO CENTRALMENTE'), 'value'].sum(),

        "Autogenerador": df.loc[(df.gen_type=='TERMICA') &
                                    (df.ship_type=='NO DESPACHADO CENTRALMENTE') &
                                    ((df.clas=='AUTOGENERADOR') | (df.clas=='AUTOG PEQ. ESCALA')), 'value'].sum(),

        "Solar"            : df.loc[(df.gen_type=='SOLAR'), 'value'].sum(),

        "Eólica"           : df.loc[df.gen_type=='EOLICA', 'value'].sum(), 
    }

    colors_neteffectivecapacity = {
        "Hidráulica"       : 'rgb(2, 97, 161)',
        "Gas"              : 'rgb(255, 192, 0)',
        "Carbon"           : 'rgb(165, 165, 165)',
        "Líquidos"         : 'rgb(228, 120, 47)',
        "NDC Hidráulica"   : 'rgb(86, 156, 220)',
        "NDC Térmica"      : 'rgb(244, 177, 131)',
        "Cogenerador"  : 'rgb(200, 191, 231)',
        "Autogenerador": 'rgb(221, 139, 82)',
        "Solar"            : 'rgb(255, 255, 0)',
        "Eólica"           : 'rgb(0, 176, 80)'
    }


    # Calculate table
    total_capacity = sum(data_neteffectivecapacity.values())
    chart_neteffectivecapacity = [(key, round(val, 1), round(100*val/total_capacity, 1), colors_neteffectivecapacity[key]) for key, val in data_neteffectivecapacity.items()]
    chart_neteffectivecapacity.append(("Total", round(total_capacity, 1), 100, None))
    chart_neteffectivecapacity = list(zip(*chart_neteffectivecapacity))

    return chart_neteffectivecapacity


def check_and_defaults_net_effective_capacity(request):

    if 'date_neteffectivecapacity' in request.GET:
        date_str = request.GET['date_neteffectivecapacity']
    else:
        date_str = ''

    cursor = connection.cursor()
    date_str = NetEffectiveCapacity.objects.latest('date') if date_str == '' else date_str

    return date_str


def monthlyBagPrices():
    

    cursor = connection.cursor()
    cursor.execute('''
        SELECT
            to_char(date_trunc('year', imports_nationalbagprice.date), 'YYYY') || '-' || to_char(date_trunc('month', imports_nationalbagprice.date), 'MM') AS year,
            ROUND(AVG((hour_0+hour_1+hour_2+hour_3+hour_4+hour_5+
                       hour_6+hour_7+hour_8+hour_9+hour_10+hour_11+
                       hour_12+hour_13+hour_14+hour_15+hour_16+hour_17+
                       hour_18+hour_19+hour_20+hour_21+hour_22+hour_23)/24)) AS monthly_avg,
            phenomenon
        FROM imports_nationalbagprice
        LEFT JOIN imports_nationalbagpricecustomdates
        ON date_trunc('month', imports_nationalbagpricecustomdates.date) = date_trunc('month', imports_nationalbagprice.date)
        GROUP BY year, phenomenon
        ORDER BY year
    ''')
    data_chart = cursor.fetchall()


    bag_prices_chart = list() 
    girl_phenomenons = list()
    boy_phenomenons = list()
    for y, m_avg, phe in data_chart:

        row = (y, m_avg)
        bag_prices_chart.append(row)

        if phe == 1: girl_phenomenons.append(row)
        elif phe == 2: boy_phenomenons.append(row)

    # Transpose array from datapoints
    bag_prices_chart = list(zip(*bag_prices_chart))
    girl_phenomenons = list(zip(*girl_phenomenons))
    boy_phenomenons = list(zip(*boy_phenomenons))


    return bag_prices_chart, girl_phenomenons, boy_phenomenons


def yearlyBagPrices():
    

    cursor = connection.cursor()
    cursor.execute('''
        SELECT FORMAT('%s', EXTRACT(YEAR FROM imports_nationalbagprice.date)) AS date_result,
               ROUND(AVG((hour_0 + hour_1 + hour_2 + hour_3 + hour_4 + hour_5 + hour_6 + hour_7 + hour_8 + 
                                        hour_9 + hour_10 + hour_11 + hour_12 + hour_13 + hour_14 + hour_15 + hour_16 + 
                                        hour_17 + hour_18 + hour_19 + hour_20 + hour_21 + hour_22 + hour_23)/24)) 
                        AS yearly_avg        
        FROM imports_nationalbagprice
        GROUP BY date_result
        ORDER BY date_result
    ''')

    bag_prices_chart = cursor.fetchall()

    bag_prices_chart = list(zip(*bag_prices_chart))    
    
    return bag_prices_chart


def usefulDailyVolumePercentage():
    

    cursor = connection.cursor()
    cursor.execute('''
        WITH sum_dudv AS(
                SELECT
                    to_char(date_trunc('year', imports_monthlyreserves.date), 'YYYY') || '-' || to_char(date_trunc('month', imports_monthlyreserves.date), 'MM') AS dates,
                    SUM(daily_useful_volume_energy)
                    
                FROM imports_monthlyreserves
                GROUP BY dates
                ORDER BY dates
                
        ), sum_uce AS(

                SELECT
                    to_char(date_trunc('year', imports_monthlyreserves.date), 'YYYY') || '-' || to_char(date_trunc('month', imports_monthlyreserves.date), 'MM') AS dates,
                    SUM(useful_capacity_energy)
                    
                FROM imports_monthlyreserves
                GROUP BY dates
                ORDER BY dates
        )

        SELECT sum_dudv.dates as date, (sum_dudv.sum/sum_uce.sum)*100 as mean from sum_dudv

        full outer join sum_uce 
        on sum_dudv.dates = sum_uce.dates
    ''')

    useful_percentage_chart = cursor.fetchall()

    useful_percentage_chart = list(zip(*useful_percentage_chart))    
    
    return useful_percentage_chart


def dailyContributionsByMonth():


    # print(format(10, '15f'))

    # PROJECT_PATH = settings.PROJECT_PATH
        
    # tmp_file = PROJECT_PATH + '/cache'


    # Xlsx2csv(f'{tmp_file}/aportes.xlsx', outputencoding="utf-8",).convert(f'{tmp_file}/raro.csv')   
    # print('se genero')

    # read_file = pd.read_excel (f'{tmp_file}/aportes.xlsx')
    # read_file.to_csv (f'{tmp_file}/pandas.csv', index = None, header=False)

    cursor = connection.cursor()

    cursor.execute('''
        SELECT 
        CONCAT(to_char(date_trunc('year', date_trunc('month', date)), 'YYYY'), '-', to_char(date_trunc('month', date_trunc('month', date)), 'MM')) AS date,
        ROUND((SUM(energy_contributions)/SUM(energy_contributions/contributions))*100)   FROM imports_dailycontributions
        GROUP BY DATE_TRUNC('month',date)
        ORDER BY DATE_TRUNC('month',date) ASC
    ''')

    result = cursor.fetchall()

    result = list(zip(*result))    

    return result

