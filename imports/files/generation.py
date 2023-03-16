import re
import os
import csv

from xlsx2csv import Xlsx2csv
import numpy as np
import urllib.request as urllib2
import subprocess
from django.db import connection

from imports.models import Resource, Agent, Fuel

# def add_fuels

# # Agregar combustibles, se coloca para que no genere errores en los otros sistemas
# cursor = connection.cursor()

# lst_fuels = ['AGUA', 'ACPM', 'GAS', 'GAS NI', 'BAGAZO', 'BIOGAS', 'BIOMASA', 'CARBON', 'COMBUSTOLEO',
#              'RAD SOLAR', 'VIENTO', 'FUELOIL', 'JET-A1', 'MEZCLA GAS - JET-A1', 'QUEROSENE', None]

# for fuel in lst_fuels:
#     query = '''
#         INSERT INTO "imports_fuel" ("name") VALUES
#         ('{}');'''.format(fuel)

   
#     cursor.execute(query)    


class Parser:


    def __init__(self, file, date_title):
        
        self.date_title = date_title
        self.file = file
 
        self.download()
        self.read()
        self.parser()

    def download(self):
        file = self.file
        filedata = urllib2.urlopen(file)
        datatowrite = filedata.read()


        PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))
        tmp_file = PROJECT_PATH +'/cache'


        with open(f'{tmp_file}/file.xlsx' , 'wb') as f:
            f.write(datatowrite)


        Xlsx2csv(f'{tmp_file}/file.xlsx', outputencoding="utf-8").convert(f'{tmp_file}/file.csv')       

        self.file = f'{tmp_file}/file.csv'
        
        
    def read(self):

        self.rows = [] 
        header = None
        self.hour_index = None
        self.fuel_index = None



        with open(self.file, encoding='UTF-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:

                if len(row) > 0:
                
                    self.rows.append(row)
                    if(row[0] == self.date_title):
                        j = 0
                        for cell in row:
                            if cell == '0':
                                self.hour_index = j
                            j += 1  
                        header = line_count+1
                    
                    line_count += 1 
            
        self.rows = np.array(self.rows[header:])

    
    def parser(self):
        
        self.cursor = connection.cursor()

        # Revisar y agregar nuevos recursos en caso de ser necesario
        self.add_resources()


        # Procesar datos        
        for row in self.rows:
          
            limit_hour =  self.hour_index + 24
            hours = row[self.hour_index:limit_hour]

            hours = np.where(hours=='', 0, hours)

            hours = str(hours)
            hours = re.sub(" ", ', ', hours)
            hours = re.sub('\n', '', hours[1:-1])

            date = row[0]


            # Consulta de ids para sustitucion
            fuel2id_fuel = {row['name']: row['id'] for row in Fuel.objects.values('id', 'name')}
            resource2id_resource = {row['name']: row['id'] for row in Resource.objects.values('id', 'name')}
          
            str_cols_hours = '"hour_0", "hour_1", "hour_2", "hour_3", "hour_4", "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23"'

            query = '''
                INSERT INTO "imports_generation" ( "date", "resource_id", "fuel_id", {}) VALUES
                ('{}', {}, {}, {})
                ON CONFLICT (date, resource_id, fuel_id) DO 
                    UPDATE 
                    SET hour_0 = excluded.hour_0,
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
                        '''.format(str_cols_hours, date, resource2id_resource[row[1]], fuel2id_fuel[row[3]], hours)

           
            self.cursor.execute(query)


    def add_resources(self):
        
        # recurso, generation_type, shipping_type, agent_code
        resources_info_file = set([(row[1], row[2], row[5], row[4]) for row in self.rows])

        # Consulta de recursos de la bd
        resources_bd = [dct['name'] for dct in Resource.objects.values('name')]

        # Dejar solo recursos nuevos
        new_resources_info = [row for row in resources_info_file if row[0] not in resources_bd]

        # Insertar recursos nuevos
        dct_agents = {row['agent_code']: row['id'] for row in Agent.objects.values('id', 'agent_code')}

        for row in new_resources_info:

            query = '''
                INSERT INTO "imports_resource" ( "name", "generation_type", "shipping_type", "agent_id") VALUES
                ('{}', '{}', '{}', {});'''.format(row[0], 
                                                  row[1],
                                                  row[2],
                                                  dct_agents[row[3]])

            self.cursor.execute(query)


