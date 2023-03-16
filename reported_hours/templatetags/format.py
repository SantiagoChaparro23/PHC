from django import template
from datetime import datetime
register = template.Library()


@register.filter(name='get_hour')
def get_hour(value, arg):
    
    time = value[arg+2]
    if time:
        time = time/60
        return "{:.2f}".format(time)
    
    return 0

    

@register.filter(name='get_day_of_week')
def get_day_of_week(date):
    
    date_time_obj = datetime.strptime(date, '%Y-%m-%d')
    weekday = date_time_obj.weekday()
    
    days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    
    
    return days[weekday]



@register.filter(name='get_day_of_week_index')
def get_day_of_week_index(date):
    
    date_time_obj = datetime.strptime(date, '%Y-%m-%d')
    weekday = date_time_obj.weekday()
    

    if weekday == 6 or weekday == 5:
        return 'table-success'
    
    return ''


@register.filter(name='can_delete_report')
def can_delete_report(item):

    current_time = datetime.now()
    current_time = current_time.strftime('%Y-%m-%d')
    current_time =   datetime.strptime(current_time, '%Y-%m-%d')

    date = item.report_date_at.strftime('%Y-%m-%d')
    date_time_obj =   datetime.strptime(date, '%Y-%m-%d')
    
    weekday = current_time.weekday()
    
    diff = current_time - date_time_obj
    print(weekday)
    if weekday == 0:
        if diff.days  <= 3:
            return True  
    
    if weekday == 6:
         if diff.days  <= 2:
            return True  
    
    if weekday >= 1 or weekday <= 5:
         if diff.days  <= 1:
            return True 

    
    return False

