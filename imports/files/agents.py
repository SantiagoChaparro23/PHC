import csv

from xlsx2csv import Xlsx2csv
import numpy as np
import urllib.request as urllib2
import subprocess
from django.db import connection

import re
import os

class Parser:

    def __init__(self, file):

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

        
        for row in self.rows:

            fixed_date = f'{row[4][6:]}-{row[4][3:5]}-{row[4][:2]}'

            query = '''
                INSERT INTO "imports_agent" ( "name", "detail", "activity", "state", "input_date") VALUES
                ('{}', '{}', '{}', '{}', '{}')
                ON CONFLICT (name) DO 
                    UPDATE 
                    SET name = excluded.name,
                        state  = excluded.state,
                        activity  = excluded.activity;                    

                ;'''.format(row[0], row[1], row[2], row[3], fixed_date)

            cursor.execute(query)
