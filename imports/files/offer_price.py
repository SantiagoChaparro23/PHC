import csv

from xlsx2csv import Xlsx2csv
import numpy as np
import urllib.request as urllib2
import subprocess
from django.db import connection

import re
import os

from imports.models import Resource, Agent

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

        with open(self.file, encoding='UTF-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:

                if len(row) > 0:
                    self.rows.append(row)
            
        self.rows = np.array(self.rows[2:])

    
    def parser(self):
        
        cursor = connection.cursor()

        # Revisar y agregar nuevos recursos en caso de ser necesario
        self.add_resources()

        # Consulta de ids para sustitucion
        resource2id_resource = {row['name']: row['id'] for row in Resource.objects.values('id', 'name')}


        def empty_str2null(string):
            return 'NULL' if string == '' else string


        for row in self.rows:

            query = '''
                INSERT INTO "imports_offerprice" ("date", "resource_id", "ideal_offer_price", "shipping_offer_price", "declared_offer_price") VALUES
                ('{}', {}, {}, {}, {})
                ON CONFLICT (date, resource_id) DO 
                    UPDATE 
                    SET ideal_offer_price = excluded.ideal_offer_price,
                        shipping_offer_price  = excluded.shipping_offer_price,
                        declared_offer_price  = excluded.declared_offer_price;
                '''.format(row[0], resource2id_resource[row[1]], empty_str2null(row[3]),  empty_str2null(row[4]), empty_str2null(row[5]))

            cursor.execute(query)

    def add_resources(self):
        
        # recurso, generation_type, shipping_type, agent_code
        resources_info_file = set([(row[1], row[2]) for row in self.rows])

        # Consulta de recursos de la bd
        resources_bd = [dct['name'] for dct in Resource.objects.values('name')]

        # Dejar solo recursos nuevos
        new_resources_info = [row for row in resources_info_file if row[0] not in resources_bd]

        # Insertar recursos nuevos
        dct_agents = {row['agent_code']: row['id'] for row in Agent.objects.values('id', 'agent_code')}

        for row in new_resources_info:

            query = '''
                INSERT INTO "imports_resource" ( "name", "agent_id") VALUES
                ('{}', {});'''.format(row[0], 
                                      dct_agents[row[1]])

            self.cursor.execute(query)