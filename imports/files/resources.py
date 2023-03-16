import re
import os
import csv

import numpy as np
import urllib.request as urllib2
import subprocess
from django.db import connection
from xlsx2csv import Xlsx2csv

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
        tmp_file = PROJECT_PATH+'/cache'

        with open(f'{tmp_file}/file.xlsx' , 'wb') as f:
            f.write(datatowrite)

        Xlsx2csv(f'{tmp_file}/file.xlsx', outputencoding="utf-8").convert(f'{tmp_file}/file.csv')

        self.file = f'{tmp_file}/file.csv'


    def read(self):

        self.rows = []
        header = None
        self.resource = None
        self.generation_type = None
        self.shipping_type = None
        self.agent_code = None

        names = ['Recurso', 'Tipo de Generación', 'Tipo de Despacho', 'Código Agente', 'Codigo Comercializador']

        with open(self.file, encoding='UTF-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0

            for row in csv_reader:

                if len(row) > 0:

                    self.rows.append(row)
                    if(row[0] == self.date_title):
                        j = 0

                        for cell in row:
                            if cell == names[0]:
                                self.resource = j

                            if cell == names[1]:
                                self.generation_type = j

                            if cell == names[2]:
                                self.shipping_type = j

                            if cell == names[3] or cell == names[4]:
                                self.agent_code = j

                            j += 1

                        header = line_count+1
                        # print('Recurso', self.resource, 'Tipo de Generación', self.generation_type, 'Tipo de Despacho', self.shipping_type, 'Código Agente', self.agent_code)
                        # break

                    line_count += 1

        self.rows = np.array(self.rows[header:])


    def parser(self):

        self.cursor = connection.cursor()

        # self.add_resources()

        for row in self.rows:

            # hours = row[self.hour_index:limit_hour]
            data = row[self.resource], None, None
            # print('Data: ', data)
            # break

            if (self.generation_type is not None) and (self.shipping_type is not None):
                data = row[self.resource], row[self.generation_type], row[self.shipping_type]
            elif self.generation_type is not None:
                data = row[self.resource], row[self.generation_type], self.shipping_type
            elif self.shipping_type is not None:
                data = row[self.resource], self.generation_type, row[self.shipping_type]

            # print('Data: ', data)
            # break

            # name = row[1]
            id_agent = Agent.objects.filter(agent_code = row[self.agent_code]).values_list('id').first()

            if id_agent:
                id_agent = id_agent[0]
                #     print('****', resource[0])
                # data.append[resource[0]]
                # print(data)

                # break

                data = np.where(data=='', 0, data)
                # hours = hours.astype(np.float)
                # total = np.sum(hours)

                # hours = hours.astype(str)
                print('*', data)
                data = str(data)
                print('**', data)
                data = re.sub("\n", "", data[1:-1])
                data = re.sub("' ", "', ", data)
                data = re.sub("None ", "NULL, ", data)
                data = re.sub("None", "NULL", data)
                if re.search('20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]', row[0]):

                    print('--------------------------')
                    print(data)
                    print(id_agent)
                    print('--------------------------')

                    query = '''
                    INSERT INTO "imports_resource" ( "name", "generation_type", "shipping_type", "agent_id") VALUES
                    ({}, {})
                    ON CONFLICT DO NOTHING;
                    '''.format(data, id_agent)

                    print(query)
                    # break

                    # query = '''
                    #     INSERT INTO "imports_neteffectivecapacity" ( "date", "net_effective_capacity", "resource") VALUES
                    #     ({}, '{}');
                    # '''.format(data, resource[0])

                    # print(query)

                    self.cursor.execute(query)
                    # break


    def add_resources(self):

        # recurso, generation_type, shipping_type, agent_code
        resources_info_file = set([(row[1], row[3], row[5], row[2]) for row in self.rows])

        # Consulta de recursos de la bd
        resources_bd = Resource.objects.values('name')

        # Dejar solo recursos nuevos
        new_resources_info = [row for row in resources_info_file if row[1] not in resources_bd]

        # Insertar recursos nuevos
        dct_agents = {row['agent_code']: row['id'] for row in Agent.objects.values('id', 'agent_code')}

        for row in new_resources_info:

            if re.search('20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]', row[0]):

                print(row)
                print(dct_agents[row[3]])

                query = '''
                    INSERT INTO "imports_resource" ( "name", "generation_type", "shipping_type", "agent_id") VALUES
                    ('{}', '{}', '{}', {});'''.format(row[0],
                                                        row[1],
                                                        row[2],
                                                        dct_agents[row[3]])

                print(query)

                self.cursor.execute(query)