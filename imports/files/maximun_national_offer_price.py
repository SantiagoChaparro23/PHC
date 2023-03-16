import csv

from xlsx2csv import Xlsx2csv
import numpy as np
import urllib.request as urllib2
import subprocess
from django.db import connection

import re
import os

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
        
        cursor = connection.cursor()
        
        for row in self.rows:
          
            limit_hour =  self.hour_index + 24
            hours = row[self.hour_index:limit_hour]

            hours = np.where(hours=='', 0, hours)
            # hours = hours.astype(np.float)
            # total = np.sum(hours)


            # hours = hours.astype(str)
            hours = str(hours)
            hours = re.sub(" ", ', ', hours)
            hours = re.sub('\n', '', hours[1:-1])

        

            date = row[0]
          
          
            query = '''
                INSERT INTO "imports_maximumnationalofferprice" ( "date", "hour_0", "hour_1", "hour_2", "hour_3", "hour_4", "hour_5", "hour_6", "hour_7", "hour_8", "hour_9", "hour_10", "hour_11", "hour_12", "hour_13", "hour_14", "hour_15", "hour_16", "hour_17", "hour_18", "hour_19", "hour_20", "hour_21", "hour_22", "hour_23") VALUES
                ('{}', {});'''.format(date, hours)

           
            cursor.execute(query)

        
        