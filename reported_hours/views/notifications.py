from helpers.email import sendEmail

from django.shortcuts import render
from django.template.loader import render_to_string
from django.db import connection
from django.core.paginator import Paginator
# Create your views here.
from django.http import HttpResponse

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.http import HttpResponse
from io import BytesIO


def daily(request):


    now = date_time_obj = datetime.strftime(datetime.now(), '%Y-%m-%d')
    today = datetime.strptime(now, '%Y-%m-%d')
    weekday = today.weekday()

    if(weekday == 5 or weekday == 6):
        return HttpResponse("Sabado o Domingo")

    delta = 1
    # si el dia es lunes el deta es 3 por seria la del viernes
    if weekday == 0:
        delta = 3


    yesterday = datetime.now() - timedelta(delta)
    yesterday = datetime.strftime(yesterday, '%Y-%m-%d')


    query = '''
        SELECT CONCAT(AU.first_name, ' ', AU.last_name), AU.email, RH.report_date_at FROM auth_user AU
        INNER JOIN reported_hours_usertoreport UR ON UR.user_id = AU.id AND UR.email = True
        LEFT JOIN reported_hours_reportedhours RH ON RH.user_id = AU.id AND RH.report_date_at = '{}'
        WHERE RH.report_date_at IS NULL
    '''.format(yesterday)


    cursor = connection.cursor()

    cursor.execute(query)

    users =  cursor.fetchall()
    
    print(users[0][0])
    
 


    context = {'user':users[0], 'date': yesterday}
    body = render_to_string('notifications/daily.html', context)
    #return render(request, 'notifications/daily.html', context)
    sendEmail(f'Reporte de horas del dia {yesterday}', body, 'daniel.londono@phc.com.co')

    return HttpResponse("ok")
    

    # for user in users:
    #     context = {'user':user}
    #     body = render_to_string('notifications/daily.html', context)
    #     #return render(request, 'notifications/daily.html', context)
    #     email = sendEmail('¡Reporte de horas!', body, [user[1]])
        

    return HttpResponse("ok")



