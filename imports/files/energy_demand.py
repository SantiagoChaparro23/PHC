import re
import os

import csv

import numpy as np
import urllib.request as urllib2
import subprocess
from django.db import connection
from xlsx2csv import Xlsx2csv


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
        # self.hour_index = None
        # self.fuel_index = None


        with open(self.file, encoding='UTF-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:

                if len(row) > 0:

                    self.rows.append(row)
                    if(row[0] == self.date_title):
                        # j = 0
                        # for cell in row:
                        #     if cell == '0':
                        #         self.hour_index = j
                        #     j += 1
                        header = line_count+1

                    line_count += 1

        self.rows = np.array(self.rows[header:])


    def parser(self):

        cursor = connection.cursor()

        for row in self.rows:

            # limit_hour =  self.hour_index + 24
            # hours = row[self.hour_index:limit_hour]
            data = row

            data = np.where(data=='', 0, data)
            # hours = hours.astype(np.float)
            # total = np.sum(hours)

            # hours = hours.astype(str)
            data = str(data)
            data = re.sub(" ", ', ', data)
            data = re.sub('\n', '', data[1:-1])

            # date = row[0]

            query = '''
                INSERT INTO "imports_energydemand" ( "date", "energy_demand_sin_kwh", "generation_kwh", "demand_not_attended_kwh", "exports_kwh", "imports_kwh") VALUES
                ({});'''.format(data)

            cursor.execute(query)
