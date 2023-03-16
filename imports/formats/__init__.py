import re
import os
import csv
from time import sleep
import subprocess
from collections import OrderedDict
from django.conf import settings
from xlsx2csv import Xlsx2csv

import numpy as np
import urllib.request as urllib2
import ssl

from django.db import connection
import pandas as pd

from imports.formats.processing_format_anomalies import FormatAnomalyProcessor

ssl._create_default_https_context = ssl._create_unverified_context


class BaseParser:
    """
        Base parser with common methods and vars for all formats of files
    """

    # Times to try download a file
    TIMES_TRY_DOWNLOAD = 5

    # This dict help to find the relation between name of a ids column and the table where are the values
    # of this relation
    dct_col2table_relation = {
        'fuel_id'                : 'imports_fuel',
        'resource_id'            : 'imports_resource',
        'agent_id'               : 'imports_agent',
        'hydrological_region_id' : 'imports_hydrologicalregion',
        'river_id'               : 'imports_river',
        'ciiu_id'                : 'imports_ciiu',
        'subactivity_id'         : 'imports_subactivity',
        'market_id'              : 'imports_market',
        'reservoir_id'           : 'imports_reservoir'
    } 

    # Dicts with equivalences between names of columns in data and name of columns y bd
    # TAKE CARE ABOUT NOT CREATE A SAME KEY WITH DIFFERENT VALUE IN ONE O MORE DICTS FROM THIS GROUP, 
    # this can crash some function/process 
    #   Relations
    dct_relations_data2relations_db = {
        'Recurso'                : 'resource_id',
        'Agente'                 : 'agent_id',
        'Código Agente'          : 'agent_id',
        'Codigo Agente'          : 'agent_id',
        'Codigo Comercializador' : 'agent_id',
        'Código Distribuidor'    : 'agent_id',
        'Combustible'            : 'fuel_id',
        'Combustible por defecto': 'fuel_id',
        'Region Hidrologica'     : 'hydrological_region_id',
        'Nombre Río'             : 'river_id',
        'CIIU'                   : 'ciiu_id',
        'Sub Actividad'          : 'subactivity_id',
        'Mercado'                : 'market_id',
        'Nombre Embalse'         : 'reservoir_id'
    }

    #   Resources characteristics
    dct_res_cols_data2res_cols_db = {
        'Recurso'                : 'resource_id', # Replace this for name fo require process  
        'Tipo de Generación'     : 'generation_type',
        'Tipo Generación'        : 'generation_type',
        'Tipo Generacion'        : 'generation_type',
        'Tipo de Despacho'       : 'shipping_type',
        'Tipo Despacho'          : 'shipping_type',
        'Es Menor'               : 'is_minor',
        'Es Autogenerador'       : 'is_autogenerator',
        'Clasificación'          : 'clasification'

    }

    #   Mapping of components of metrics to columns, for metrics with format type 2
    #   where 1 column = 1 component
    dct_metric_data2metric_db = {

        # neteffectivecapacity
        'Capacidad Efectiva Neta kW': 'net_effective_capacity',

        # fuelconsumption
        'Consumo Combustible (MBTU)': 'fuel_consumption',

        # offerprice
        'Precio de Oferta Ideal $/kWh'      : 'ideal_offer_price',
        'Precio de Oferta de Despacho $/kWh': 'shipping_offer_price',
        'Precio de Oferta Declarado $/kWh'  : 'declared_offer_price',

        # dailycontributions
        'Aportes Caudal m3/s' : 'flow_inputs',
        'Aportes Energía kWh' : 'energy_contributions',
        'Aportes %'           : 'contributions',

        # internationaldeltaandnationaldelta
        'Delta Internacional': 'international_delta',
        'Delta Nacional'     : 'national_delta',

        # commercialdemandnotregulatedbyciiu
        'Demanda Comercial kWh': 'commercial_demand',

        # energydemandsin
        'Demanda Energia SIN kWh' : 'energy_demand_sin',
        'Generación kWh'          : 'generation',
        'Demanda No Atendida kWh' : 'demand_not_attended',
        'Exportaciones kWh'       : 'exports',
        'Importaciones kWh'       : 'imports',

        # maximumpowerdemand
        'Demanda Máxima de Potenca kW': 'maximum_power_demand',

        # monthly prices
        'Precio Escasez $/kWh'                   : 'price_shortage',
        'MC $/kWh'                               : 'mc',
        'CERE $/kWh'                             : 'cere',
        'CEE $/kWh'                              : 'cee',
        'FAZNI Precio $/kWh'                     : 'fazni_price',
        'Precio Promedio Contrato'               : 'average_contract_price',
        'Precio Promedio Contratos Regulados'    : 'average_price_regulated_contracts',
        'Precio Promedio Contratos No Regulados' : 'average_price_nonregulated_contracts',

        # monthly reserves
        'Capacidad Útil Volumen Mm3'        : 'useful_capacity_volume',
        'Volumen Máximo Técnico Energía kWh': 'maximum_technical_volume_energy',
        'Capacidad Útil Energía kWh'        : 'useful_capacity_energy',
        'Volumen Útil Diario Mm3'           : 'useful_daily_volume',
        'Volumen Útil Diario Energía kWh'   : 'daily_useful_volume_energy',
        'Volumen Útil Diario %'             : 'useful_dailyvolume'

    }

    #   Dict with all equivalences
    dct_name_col_data2name_col_db = dict()
    dct_name_col_data2name_col_db.update(dct_relations_data2relations_db)
    dct_name_col_data2name_col_db.update(dct_res_cols_data2res_cols_db)
    dct_name_col_data2name_col_db.update(dct_metric_data2metric_db)

    def __init__(self, cursor=None, date_title='Fecha'):

        # Basic variables and elements use for all parsers in the same way
        if cursor is None:
            self.cursor = connection.cursor()
        else:
            self.cursor = cursor
            
        self.date_title = date_title

        # For querys with resources
        self.cols_res = None
        self.dct_cols_i = None

        # Initialize some vars
        self.anomaly_processor = FormatAnomalyProcessor()
        self.file = None
        self.url = None

        self.PROJECT_PATH = settings.PROJECT_PATH
        
        self.tmp_file = self.PROJECT_PATH + '/cache'
        print('fileee', self.tmp_file)

    def download(self):
        """Summary

        Download a file with extension xlsx or xls, try download TIMES_TRY_DOWNLOAD times
        if fail raise exception.
        
        Raises:
            NotImplementedError: Raise for files that not are xlsx or xls
        """

        # Download sometimes fail..so we try more times
        success_download = False
        times_tried = 0
        while not success_download:
            try:
                urldata = urllib2.urlopen(self.url)
                datatowrite = urldata.read()
                success_download = True

            except Exception as e:
                times_tried += 1
                assert times_tried <= self.TIMES_TRY_DOWNLOAD, f'Times tried download {self.url} exceeded, error: {str(e)}'
                print('Failed download, trying again')
                sleep(1)

        # Verify extension from file
        print('ext')
        print(self.url)
        if self.url.endswith('xlsx'): 
            extension = 'xlsx'
        elif self.url.endswith('xls'): 
            extension = 'xls'
        else: 
            extension = 'xls'

        # Save in cache folder
        self.file = f'{self.tmp_file}/file.{extension}'

        with open(self.file , 'wb') as f:
            f.write(datatowrite)

    def read(self):
        """Summary

        Read and get data from download file, the process is different for xlsx and xls files,
        for xlsx files is faster that xls.

        The result of this is self.rows, self.headers, with data from folder and the index where
        start hour columns if apply.
        """

        # if file have xlsx extension convert first to csv and before get data
        if self.url.endswith('xlsx'):
            self.convert_xlsx2csv()
            self.get_data_csv()

        # if have xls extension read directly with pandas, more slower but easy to implement
        # this case apply only for approximately 1% from files            
        elif self.url.endswith('xls'): 
            self.get_data_xls()

        self.delete_last_empty_rows()

        # Remove specific anomalies in data rows and headers
        self.rows, self.headers = self.anomaly_processor.remove_anomaly(self.url, self.rows, self.headers)        

        self.found_hour_index()

    def select_date_title(self):
        """
            Date title is almost same for all variables except one, Precios mensuales
            date in Precios Mensuales come in 2 columns, Reservas mensuales too
        """

        # Old form, delete if the new way work fine
        # if self.table in ['imports_monthlyprices', 'imports_monthlyreserves']:
        #     self.date_title = 'Año'
        # else:
        #     self.date_title = 'Fecha'
        

        # We use the url because the format 5 dont have the self.table attribute
        if ('Reservas_Mensual' in self.url) or ('Precios_Mensuales' in self.url):
            self.date_title = 'Año'
        else:
            self.date_title = 'Fecha'            

    def convert_xlsx2csv(self):
        """
        Almost all files are get in xlsx format, convert to csv y before read is faster,
        apply this process for xls files require much more development time
        """

        # Raise assertion if not is a xlsx file
        assert self.file.endswith('xlsx'), 'This function only convert xlsx files'

        # Convert to csv and save again as csv file
        self.file = f'{self.tmp_file}/file.csv'

        read_file = pd.read_excel(f'{self.tmp_file}/file.xlsx', engine='openpyxl')

        # print('read_file')
        # print(read_file)
        # print()

        read_file.to_csv (self.file, index = True, header=True)

                
    def get_data_csv(self):
        """Summary

        Get data from csv file, rows and headers
        data format is same to results from get_data_xls method
        
        Raises:
            ValueError: Raise if the header row is not detected
        """
        self.rows = [] 
        self.headers = None

        header = None
        init_column = None

        # Take data from csv file
        with open(self.file, encoding='UTF-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if len(row) >= 2:
                    print(row)
                    #print(fdfd)
                    # sometimes we found a empty column
                    init_0 = row[0] == self.date_title
                    init_1 = row[1] == self.date_title
                    init_2 = row[2] == self.date_title

                    if init_0 or init_1 or init_2:

                        if init_0: init_column = 0 
                        if init_1: init_column = 1
                        if init_2: init_column = 2

                        header = line_count+1
                        self.headers = row[init_column:]

                    self.rows.append(row[init_column:])
                    
                    line_count += 1 
                    

                    # if(line_count == 10):
                    #     print(dfdfd)

            
        self.rows = np.array(self.rows[header:])

        if self.headers is None:
            raise ValueError('Headers row no detected from csv file')        

    def get_data_xls(self):
        """Summary

        Get data from xls file, rows and headers
        data format is same to results from get_data_csv method
        
        Raises:
            ValueError: Raise if the header row is not detected
        """
        self.headers = None

        df = pd.read_excel(self.file).fillna('')

        for i, row in enumerate(df.values):

            # sometimes we found a empty column
            init_0 = row[0] == self.date_title
            init_1 = row[1] == self.date_title

            if init_0 or init_1:

                if init_0: init_column = 0 
                if init_1: init_column = 1

                header = i
                break

        self.headers = df.iloc[header, init_column:].values.astype('<U100')
        self.rows = df.iloc[header+1:, init_column:].values.astype('<U100')

        if self.headers is None:
            raise ValueError('Headers row no detected from xls file')        

    def delete_last_empty_rows(self):
        """Summary

        Check if lasts rows not have values checking only the date column
        Have date format YYYY-MM-DD or YYYY?
            Yes: Do nothing, Not: Drop row
        """

        #   Only check if we have data to check
        if len(self.rows) > 0:

            # Iterate since end to start
            for i in range(len(self.rows), 0, -1):

                #  Yup....this can be more optimal...but not time
                format_date = re.search('20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]', self.rows[-1][0])
                format_year = re.search('20[0-9][0-9]', self.rows[-1][0])

                if (not format_date) and (not format_year):
                    self.rows = self.rows[:-1]

    def found_hour_index(self):
        """Summary

        Search the index from headers where start hour columns
        if not found, nothing happen

        The result is save in self.hour_index
        """
        self.hour_index = None
      
        for i, cell in enumerate(self.headers):
       
            if cell == '0' or cell == '0.0':
                self.hour_index = i
                break

    def get_columns_table(self, type_cols:str, table:str=None):
        """
        Return list of names from columns in the table, agents, resources, etc.
        
        args:
            type_cols: str: Types of columns names to get.
                            'relationals': Names of columns of relations as agent_id, fuel_id and etc.
                            'not_relationals': Names of columns DIFFERENTS of relations as id, date and names
                                               that belong to each metric as net_effective_capacity 
                                               in imports_neteffectivecapacity
                            'all': Names of ALL columns except 'id'
        
            table: str: Table to query columns, by default is the table associated to parser in __init__
        
        Returns:
            list: List with names of columns in table
        
        Raises:
            NotImplementedError: Raise if type_cols not in variable_str dict
        """

        # By default table is self.table
        if table is None: 
            table = self.table


        variable_str = {
            'relationals': "AND POSITION('id' in column_name) > 1",
            'not_relationals': "AND NOT POSITION('id' in column_name) > 1",
            'all': ''
        }

        try:        

            self.cursor.execute('''
                SELECT column_name
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{}'
                {}
                -- Every column of a relational element finish in id, 
                -- we need all this columns except by 'id', 
                -- which is proper to the current table
            '''.format(table, variable_str[type_cols])
            )

        except KeyError as e:
            raise NotImplementedError(f'''get_column_table for {type_cols} not implemented''')

        name_cols = [row[0] for row in self.cursor.fetchall()]

        return name_cols

    def get_elmnt_name2_elmnt_id(self, name_cols:list):
        """
        Return a dict with dicts for find the id 
        of a relational element, the key for 
        dicts are the name of col
            
        Args:
            name_cols (list): Name of database columns for get dict for convert str name to numeric id
        
        Returns:
            dct of dct's: This dicts have the next estructure:
                            {'fuel_id': {'AGUA': 1, ...},
                             'resource_id': {'JAGUAS': 460, ...}}
        
        Raises:
            NotImplementedError: Raise if a name of column not are in dct_col2table_relation, 
                                 add first and after try again
        """

        # resources requiere dict of agents por some process
        if 'resource_id' in name_cols:
            name_cols.append('agent_id')

        dct_name2id = dict()
        for col in name_cols:

            if col in self.dct_col2table_relation.keys():

                if col == 'resource_id':
                    """
                        Resources have a different behavior, conceptually 2 resources
                        with same name and at least a different feature are different resources
                        in the bd and therefore have 2 differents ids.
                    """
                    cols_res = self.get_columns_table('all', table='imports_resource')
                    cols_res.remove('id')
                    # is important use the same order ever, for dont add extra return, use
                    # alphabetically order
                    cols_res.sort() 
                    str_cols = ', '.join(cols_res)

                    self.cursor.execute('''
                        SELECT id, {}
                        FROM {}; 
                    '''.format(str_cols, self.dct_col2table_relation[col]))
                    dct_name2id[col] = {row[1:]: str(row[0]) for row in self.cursor.fetchall()}

                # for other columns do the same process
                else:
                    self.cursor.execute('''
                        SELECT name, id
                        FROM {}; 
                    '''.format( self.dct_col2table_relation[col]))                

                    dct_name2id[col] = {row[0]: str(row[1]) for row in self.cursor.fetchall()}

            else:
                raise NotImplementedError(f'''Unknown relation between cols of ids '{col}' and table of database
                                              add to "dct_col2table_relation" in "BaseParser" class''')

        return dct_name2id

    def get_index_columns(self, columns_db:list):
        """
        Get index from of columns from db using the header of data to import 
        
        Args:
            columns_db (list): List of columns to find id in self.headers
        
        Returns:
            OrderedDict: This dict have the next format:
                            key=columns_db : value=index of column_db in self.headers
        """

        lst_tuples = list()
        for i, head in enumerate(self.headers): # Iterate about headers from data to import

            # Are head in dict col_data2col_db? If true i can use for find equivalen name in db
            # in other case...do nothing
            # Some files dont have all normal columns of metric, do nothing prevent exceptions for this cases
            if head in self.dct_name_col_data2name_col_db.keys(): 
                if self.dct_name_col_data2name_col_db[head] in columns_db: 

                    tple = (self.dct_name_col_data2name_col_db[head], i)
                    lst_tuples.append(tple)

        #   Is very important ever have the same order for the moment of assemble str of cols and values
        dct_index = OrderedDict(lst_tuples)

        return dct_index

    def get_id_relational_element(self, col_name_relation:str, row, dct_name2id:dict, index):
        """
        Get numeric id of relational element using row of data,
        for all relations we use the same process except by resource_id where
        we need other characteristics to find the id of the resource since a 
        resource can have several versions.
        
        Args:
            col_name_relation (str): Name of col from relation, resource_id, agent_id, etc
            row (list or np.ndarray): Row from data extracted from file of metric
            dct_name2id (dict): Dict for find equivalences between a element and his id in the database
                                this dict can be generated for the method 'get_elmnt_name2_elmnt_id'
            index (int or str): Index from element in row of data
        
        Returns:
            tuple or str or int: id from element
        """

        if col_name_relation == 'resource_id':

            # Found resources features in the data to expord using header
            founded_features = [self.dct_res_cols_data2res_cols_db[h] 
                                for h in self.headers if h in self.dct_res_cols_data2res_cols_db.keys()]
            founded_features.sort() # Same order of resources keys in get_elmnt_name2_elmnt_id

            # Found indexes from this features
            #   If we do this for first time, do all process
            if self.cols_res is None:
                dct_cols_i = self.get_index_columns(founded_features)

                dct_cols_i['name'] = dct_cols_i['resource_id']
                del dct_cols_i['resource_id']

                # Build key 
                cols_res = self.get_columns_table('all', table='imports_resource')
                cols_res.sort()
                cols_res.remove('id')

                # Save vars
                self.dct_cols_i = dct_cols_i
                self.cols_res = cols_res                

            #   In other case, take the calculate variables
            else:
                dct_cols_i = self.dct_cols_i
                cols_res = self.cols_res

            key = []
            for col in cols_res:
                if col in dct_cols_i.keys():
                    if col == 'agent_id':
                        i_col = dct_cols_i[col]
                        id_agent = dct_name2id['agent_id'][row[i_col]]
                        key.append(int(id_agent))

                    else:
                        i_col = dct_cols_i[col]
                        key.append(row[i_col])
                else:
                    key.append('')

            key = tuple(key)


            # # Find id element in dct_name2id
            # print(dct_name2id['resource_id'])
            # print('------')
            # print(key)
            # print('------')
            # print(test)
            id_elm = dct_name2id['resource_id'][key]
            

        else:
            id_elm = dct_name2id[col_name_relation][row[index]]

        # except KeyError as e:
        #     raise NotImplementedError(f'''get_column_table for {type_cols} not implemented''')            

        return id_elm

    def parser(self):
        raise NotImplementedError('Base parser class cant parse files')


class Format1(BaseParser):
    """
        Parser for files with hours from 0 to 23 and every hour in a column,
        where the values of a component are in 24 columns, one column for each hour of a day.
    """

    def __init__(self, url, table, **kwargs):
        super().__init__(**kwargs)

        self.table = table
        self.url = url
        
        print('Downloading ...' , url)
        self.download()

        print('Reading ...')
        self.read()

        print('Parsering ...')
        self.parser()

    def parser(self):
        """Summary
        
        Parser the file download from the url
        
        Raises:
            ValueError: Raise if Hour index not found, canceling parser
        """
        if self.hour_index is None:
            raise ValueError('Hour index not found, parser cancelled')

        # Get names of relational columns from the metric table
        relat_cols = self.get_columns_table('relationals')

        # Check index for every relational column in the data to import
        dct_index = self.get_index_columns(relat_cols)

        # Get dicts for name of relational elements to id
        dct_name2id = self.get_elmnt_name2_elmnt_id(relat_cols)

        # Build str for cols to insert and conflict sentence
        str_cols, str_cols_conflict = self.asemble_columns_str(dct_index)

        # Inserts
        for row in self.rows:

            # Build str for values
            str_vals = self.assemble_values_str(row, dct_index, dct_name2id)

            # Build query and execute
            query = self.assemble_dinamic_sql_query(self.table, str_cols, str_vals, str_cols_conflict)
            
            self.cursor.execute(query)

    @staticmethod
    def asemble_columns_str(dct_index):
        str_cols_hours = ', hour_0, hour_1, hour_2, hour_3, hour_4, hour_5, hour_6, hour_7, hour_8, hour_9, hour_10, hour_11, hour_12, hour_13, hour_14, hour_15, hour_16, hour_17, hour_18, hour_19, hour_20, hour_21, hour_22, hour_23'

        if len(dct_index) > 0:            
            str_relations = ', '.join(dct_index.keys())
            str_cols = 'date, ' + str_relations + str_cols_hours
            str_cols_conflict = 'date, ' + str_relations

        else:
            str_cols = 'date' + str_cols_hours
            str_cols_conflict = 'date'

        return str_cols, str_cols_conflict  

    def assemble_values_str(self, row, dct_index, dct_name2id):

        # Take 24 hours and form a string in format SQL
        hours = row[self.hour_index: self.hour_index + 24]

        hours_str = str(hours)
        hours_str = re.sub(" ", ', ', hours_str)
        hours_str = re.sub('\n', '', hours_str[1:-1])
        hours_str = re.sub("''", 'NULL', hours_str)


        # Build total str for values
        if len(dct_index) > 0:
            str_rel_vals =  ', '.join(f"'{self.get_id_relational_element(col, row, dct_name2id, i)}'" for col, i in dct_index.items())
            #              date          relat elements     data of 24 hours
            str_vals = f"'{row[0]}', " + str_rel_vals + f', {hours_str}'

        else:
            str_vals = f"'{row[0]}', {hours_str}"

        return str_vals

    @staticmethod
    def assemble_dinamic_sql_query(table, cols, values, cols_conflict):

        return '''

        INSERT INTO {}({})
        VALUES({}) 
        ON CONFLICT ({}) 
        DO 
            UPDATE SET hour_0 = excluded.hour_0,
                        hour_1 = excluded.hour_1,
                        hour_2 = excluded.hour_2,
                        hour_3 = excluded.hour_3,
                        hour_4 = excluded.hour_4,
                        hour_5 = excluded.hour_5,
                        hour_6 = excluded.hour_6,
                        hour_7 = excluded.hour_7,
                        hour_8 = excluded.hour_8,
                        hour_9 = excluded.hour_9,
                        hour_10 = excluded.hour_10,
                        hour_11 = excluded.hour_11,
                        hour_12 = excluded.hour_12,
                        hour_13 = excluded.hour_13,
                        hour_14 = excluded.hour_14,
                        hour_15 = excluded.hour_15,
                        hour_16 = excluded.hour_16,
                        hour_17 = excluded.hour_17,
                        hour_18 = excluded.hour_18,
                        hour_19 = excluded.hour_19,
                        hour_20 = excluded.hour_20,
                        hour_21 = excluded.hour_21,
                        hour_22 = excluded.hour_22,
                        hour_23 = excluded.hour_23;

        '''.format(table, cols, values, cols_conflict)        


class Format2(BaseParser):
    """
        Parser for files where metric components have only one column
    """

    def __init__(self, url, table, **kwargs):
        super().__init__(**kwargs)

        self.cursor = connection.cursor()

        self.table = table
        self.url = url

        # Date title is diferent for imports_monthlyprices and imports_monthlyreserves
        self.select_date_title()


        print('Downloading ...', url)
        self.download()

        print('Reading ...')
        self.read()

        print('Parsering ...')
        self.parser()


    def parser(self):

        # Homogenize column date only for monthlyprices metric or similar
        if self.table in ['imports_monthlyprices', 'imports_monthlyreserves']: 
            self.year_month2fecha_column()

        # For data of relations
        #   Get names of relational columns from the metric table
        relat_cols = self.get_columns_table('relationals')

        #   Check index for every relational column in the data to import
        dct_index_relations = self.get_index_columns(relat_cols)

        #   Get dicts for name of relational elements to id
        dct_name2id = self.get_elmnt_name2_elmnt_id(relat_cols)


        # Same process for data of components from metrics
        comp_cols = self.get_columns_table('not_relationals')
        comp_cols.remove('id')
        comp_cols.remove('date')

        dct_index_components = self.get_index_columns(comp_cols)


        # Build str for cols to use in insert and conflict sentence
        str_cols, str_cols_confl = self.asemble_columns_str(dct_index_relations, dct_index_components)

        # Build str for columns to update in conflicts
        update_vals = self.assemble_update_str(comp_cols)

        print(self.rows)
        # Inserts
        for row in self.rows:

            # Build str for values
            str_vals = self.assemble_values_str(row, dct_index_relations, dct_index_components, dct_name2id)


            # Build query and execute
            query = self.assemble_dinamic_sql_query(self.table, str_cols, str_vals, str_cols_confl, update_vals)
            
            self.cursor.execute(query)

    def year_month2fecha_column(self):
        """
            Convert year and month columns in only one with Fecha, this applied only for 
            Precios Mensuales metric
        """
        # Used for convert names of months in spanish in standard format in numbers
        month2num = {
            'ENERO': '01',
            'FEBRERO': '02',
            'MARZO': '03',
            'ABRIL': '04',
            'MAYO': '05',
            'JUNIO': '06',
            'JULIO': '07',
            'AGOSTO': '08',
            'SEPTIEMBRE': '09',
            'OCTUBRE': '10',
            'NOVIEMBRE': '11',
            'DICIEMBRE': '12'
        }

        #   Change dates to standard format
        for row in self.rows:
            row[0] = '{}-{}-01'.format(row[0], month2num[row[1]])

        #   Delete not necessary columns and headers
        self.rows = np.delete(self.rows, 1, axis=1)
        self.headers[0] = 'Fecha'
        self.headers = np.delete(self.headers, [1])

    @staticmethod
    def asemble_columns_str(dct_idx_relat, dct_idx_comp):

        str_columns = 'date'
        str_cols_confl = 'date'

        if len(dct_idx_relat) > 0:            
            str_relations = ', '.join(dct_idx_relat.keys())
            str_columns += ', ' + str_relations
            str_cols_confl += ', ' + str_relations

        if len(dct_idx_comp) > 0:            
            str_components = ', '.join(dct_idx_comp.keys())
            str_columns += ', ' + str_components

        return str_columns, str_cols_confl  

    def assemble_values_str(self, row, dct_idx_rel, dct_idx_cmp, dct_name2id):

        str_vals = f"'{row[0]}'"

        # Build total str for values
        #   Relations 
        if len(dct_idx_rel) > 0:
            str_rel_vals =  ', '.join(f"'{self.get_id_relational_element(col, row, dct_name2id, i)}'" for col, i in dct_idx_rel.items())
            str_vals += ', ' + str_rel_vals

        #   Components
        if len(dct_idx_cmp) > 0:
            str_cmp_vals =  ', '.join(f"'{row[i]}'" if (row[i] != None and row[i]!= '') else 'NULL' for i in dct_idx_cmp.values())
            str_vals += ', ' + str_cmp_vals            

        return str_vals

    @staticmethod
    def assemble_update_str(comp_cols):
        return ', '.join([f'{col} = excluded.{col}' for col in comp_cols])

    @staticmethod
    def assemble_dinamic_sql_query(table, cols, values, cols_conflict, update_vals):

        return '''

        INSERT INTO {}({})
        VALUES({}) 
        ON CONFLICT ({}) 
        DO 
            UPDATE SET {};

        '''.format(table, cols, values, cols_conflict, update_vals)

# For resources
class Format3(BaseParser):
    """
        Currently for import ONLY Resources from metrics 
    """

    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)


        self.date_title = 'Fecha'
        self.table = 'imports_resource'
        self.url = url


        print('Downloading ...' , url)
        self.download()

        print('Reading ...')
        self.read()

        print('Parsering ...')
        self.parser()


    def parser(self):

        # Drop junk columns for this import process
        self.drop_junk_columns()

        # For data of relations
        #   Get names of relational columns from the metric table
        relat_cols = self.get_columns_table('relationals')

        #   Check index for every relational column in the data to import
        dct_index_relations = self.get_index_columns(relat_cols)

        #   Get dicts for name of relational elements to id
        dct_name2id = self.get_elmnt_name2_elmnt_id(relat_cols)


        # For data of components from metrics
        comp_cols = self.get_columns_table('not_relationals')
        comp_cols.remove('id')


        dct_index_components = self.get_index_columns(comp_cols)


        #   This step is the almost the same from get_columns_table, columun resource is call: id_resource
        #   this is true for all metrics, imports_resources not are a metric, is a index table with actors of energy market
        dct_index_components['name'] = self.headers.index('Recurso')        


        # Build str for cols to use in insert and conflict sentence, for resources
        # columns are the same for insert an conflict sentence
        str_cols, str_cols_confl = self.asemble_columns_str(dct_index_relations, dct_index_components)

        # Build str for columns to update in conflicts
        update_vals = self.assemble_update_str(comp_cols)



        # Inserts
        for row in self.rows:

            # Build str for values
            str_vals = self.assemble_values_str(row, dct_index_relations, dct_index_components, dct_name2id)

            # Build query and execute
            query = self.assemble_dinamic_sql_query(self.table, str_cols, str_vals, str_cols_confl, update_vals)
            
            self.cursor.execute(query)

    def drop_junk_columns(self):
        """ 
            Drop not necessary columns, then apply unique
            This help to do this process faster
        """

        # Get columns of resource table and add 'resource_id', equivalent of 'name' in resources table
        resources_cols = self.get_columns_table('all')
        resources_cols.remove('id')
        resources_cols.append('resource_id')


        # Check index for every relational column in the data to import
        dct_index_relations = self.get_index_columns(resources_cols)

        # Build list of indexes to index every array of self.rows
        indexes_take = list(dct_index_relations.values())
        indexes_take.sort()

        #  Get only unique rows with indexes_take, kept only require headers too
        self.rows = np.unique(np.array([row[indexes_take] for row in self.rows]), axis=0)
        self.headers = [self.headers[i] for i in indexes_take]

    def asemble_columns_str(self, dct_idx_relat, dct_idx_comp):
        """
            For resources str_cols_conflict must be build in a different way
            str_cols_confl includes all the columns of the resource table
        """

        # Buil str_columns use for insert values
        str_columns = ''

        add_str_relat = len(dct_idx_relat) > 0
        if add_str_relat:
            str_relations = ', '.join(dct_idx_relat.keys())
            str_columns += str_relations

        if len(dct_idx_comp) > 0:
            str_conector = ', ' if add_str_relat else ''

            str_components = ', '.join(dct_idx_comp.keys())
            str_columns += str_conector + str_components

        # Buil str_cols_confl use for conflict statement
        #   Query columns of resources
        cols_res = self.get_columns_table('all', 'imports_resource')
        cols_res.remove('id')

        #   Build con cols fo query
        str_cols_confl = ', '.join(cols_res)

        return str_columns, str_cols_confl

    @staticmethod
    def assemble_update_str(comp_cols):
        return ', '.join([f'{col} = excluded.{col}' for col in comp_cols])

    def assemble_values_str(self, row, dct_idx_rel, dct_idx_cmp, dct_name2id):

        # Not include data column as in the parsers 1 and 2
        str_vals = f""

        # Build total str for values
        #   Relations
        add_str_relat = len(dct_idx_rel) > 0
        if len(dct_idx_rel) > 0:
            str_rel_vals =  ', '.join(f"'{dct_name2id[col][row[i]]}'" for col, i in dct_idx_rel.items())
            str_vals += str_rel_vals

        #   Components
        if len(dct_idx_cmp) > 0:
            str_conector = ', ' if add_str_relat else ''

            str_cmp_vals =  ', '.join(f"'{row[i]}'" for i in dct_idx_cmp.values())
            str_vals += str_conector + str_cmp_vals

        return str_vals

    @staticmethod
    def assemble_dinamic_sql_query(table, cols, values, str_cols_confl, update_vals):

        return '''
        INSERT INTO {}({})
        VALUES({}) 
        ON CONFLICT ({}) 
        DO NOTHING;
        -- if a row with all the same values exist, 
        -- do not create a new resource
        '''.format(table, cols, values, str_cols_confl, update_vals)

# For agents
class Format4(BaseParser):

    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)

        self.url = url

        self.download()
        self.read()
        self.parser()
        
    def read(self):
        """
            csv.read give utf-8 errors, so we use pandas here
        """

        # Default excel engine does not support xlsx files
        # so we use openpyxl
        df = pd.read_excel(self.file, skiprows=3, engine='openpyxl')            
        self.rows = df.values

    def parser(self):
             
        for row in self.rows:

            # Old format used in agent files: '19/02/2019'
            # fixed_date = f'{row[4][6:]}-{row[4][3:5]}-{row[4][:2]}'

            # New format used in agent files: '2021-10-25'
            fixed_date = f'{row[4][:4]}-{row[4][5:7]}-{row[4][8:]}'


            query = '''
                INSERT INTO "imports_agent" ( "name", "detail", "activity", "state", "input_date") VALUES
                ('{}', '{}', '{}', '{}', '{}')
                ON CONFLICT (name) DO 
                    UPDATE 
                    SET name = excluded.name,
                        state  = excluded.state,
                        activity  = excluded.activity;                    

                ;'''.format(row[0], row[1], row[2], row[3], fixed_date)

            self.cursor.execute(query)

# For relational elements from a column of metric file
class Format5(BaseParser):

    def __init__(self, url, col_relation, **kwargs):
        super().__init__(**kwargs)

        self.col_relation = col_relation
        self.url = url

        print(url)

        # Date title is diferent for imports_monthlyprices and imports_monthlyreserves
        self.select_date_title()        

        self.download()
        self.read()
        self.parser()        
        
    def parser(self):

        # Check index for every relational column in the data to import
        dct_index_relations = self.get_index_columns([self.col_relation])

        # Take only wish column and get unique elements 
        i_col = dct_index_relations[self.col_relation]
        unique_elements = set([rw[i_col] for rw in self.rows])

        print()
        print('Some unique_elements to insert:')
        print(list(unique_elements)[-5:])
        print()
        
        for elm in unique_elements:

            query = '''
                INSERT INTO "{}" ("name") VALUES
                ('{}')
                ON CONFLICT (name) DO 
                    NOTHING
                ;'''.format(self.dct_col2table_relation[self.col_relation], elm)

            self.cursor.execute(query)






