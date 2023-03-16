from helpers.email import sendEmail
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateView
from budgeted_hours.models import Activities, BudgetedHours, Client, Hours, ServiceType, CategoriesVersions
from users.models import RolesUsers
from reported_hours.forms import ReportedHoursForm
from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from reported_hours.models import ReportedHours, ReportedHoursDraft
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connection
from django.core.paginator import Paginator
# Create your views here.
from django.http import HttpResponse
from datetime import datetime, timedelta
import datetime
import calendar
from django.core.exceptions import PermissionDenied
from django.urls import reverse


import pandas as pd
import numpy as np


from django.http import HttpResponse
from io import BytesIO
from django.db.models import Sum, Count

from reported_hours.templatetags.format import can_delete_report

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


@login_required
def excel(request):
    xl = pd.read_excel("cache/horas2.xlsx")


    services = xl['Servicio'].unique().astype(str)
    activities = xl['Actividad'].astype(str)
    codes = xl['Código'].unique().astype(str)


    ##Importo los servicios que no existan
    for service in services:
        servicesType = ServiceType.objects.filter(service_type=service).first()
        if servicesType is None:
            s = ServiceType(service_type=service)
            s.save()



    CLIENT_DEFAULT = Client.objects.get(pk=8)
    SERVICETYPE_DEFAULT = ServiceType.objects.get(pk=25)
    USER_DEFAULT = User.objects.get(pk=3)
    
   
    for index, row in xl.iterrows():

        #servicesType = ServiceType.objects.filter(service_type=service).first()

        activtity = row['Actividad']
        service   = row['Servicio']
        code   = row['Código']
        employee   = row['Empleado']
        hours   = row['Horas']
        comments   = row['Comentarios']
        date   = row['Fecha']

        

        cursor = connection.cursor()
        query = f"SELECT * FROM auth_user WHERE name='{employee}' "
        cursor.execute(query)
        row = cursor.fetchone()
        if(row == None):
            print('no existe', employee)
            continue

        user  = row[0]
 

        servicesType = ServiceType.objects.filter(service_type=service).first()
        
        a = Activities.objects.filter(activity=activtity, service_type=servicesType).first()
        if a is None:
            a = Activities(activity=activtity, service_type=servicesType)
            a.save()
            a = Activities.objects.filter(activity=activtity, service_type=servicesType).first()
            

        
        b = BudgetedHours.objects.filter(code=code).first()
        if b is None:

            b = BudgetedHours(code=code, client=CLIENT_DEFAULT, service_type=SERVICETYPE_DEFAULT,  created_by=USER_DEFAULT)
            b = b.save() 
            b = BudgetedHours.objects.filter(code=code).first()


        
        #agrego la actividad al proyecto si no existe
        h = Hours.objects.filter(budgeted_hours=b, activity=a, category_id=1).first()
        if h is None:
            h = Hours(budgeted_hours=b, activity=a, category_id=1)
            h = h.save()

  
      
      
        minutes = hours*60
        print(b,date,a,minutes,comments,user)
        rh = ReportedHours(code=b, report_date_at=date, activity=a, time=minutes, description=comments, user_id=user)
        rh.save()

       
        
    

    return HttpResponse("return this string")



class ReportedHoursListView(LoginRequiredMixin, ListView):


    model = ReportedHours
    template_name = 'reported_hours/list.html'


    def post(self, request, *args, **kwargs):
        
        back_url = request.META.get('HTTP_REFERER')
        
        code_id = self.request.POST.get('project_id','')
        report_date_at = self.request.POST.get('report_date_at','')
        description = self.request.POST.get('description','')
        activity_id = self.request.POST.get('activity_id','')
        hours = self.request.POST.get('hours','')
        minutes = self.request.POST.get('minutes','')

        print(activity_id)
        if activity_id is None or activity_id is '':
            messages.error(request, 'Seleccione la actividad')
            return HttpResponseRedirect(back_url)

        hours = int(hours) * 60
        minutes = int(minutes)        
        total = int(hours) + int(minutes)

        if total < 1:
            messages.error(request, 'El tiempo minímo para reportar es de 1 minuto')
            return HttpResponseRedirect(back_url)

        user = self.request.user
        report = ReportedHoursDraft(user=user, time=total, description=description, activity_id=activity_id, code_id=code_id, report_date_at=report_date_at)
        
        if user.has_perm('reported_hours.multiple_users'):
            reported_by = user
            
            user_id = self.request.POST.get('user_id','')
            user = User.objects.get(pk=user_id)
            
            if reported_by != user:
                report.description = f'{description} - Tiempo reportado por {reported_by.first_name} {reported_by.last_name}'
            report.reported_by = reported_by
            report.user = user

        
        report.save()

        messages.success(request, 'Tiempo guardado')
        return HttpResponseRedirect(back_url)

       
    

    def get_context_data(self, **kwargs):
     
        ctx = super(ReportedHoursListView, self).get_context_data(**kwargs)


        query = self.request.GET.get('q','')
        ctx['query'] = query
        #ctx['form'].fields["responsable"].queryset = User.objects.filter(is_superuser=False)
       
        user = self.request.user
        
        #si el usuario tiene este permiso puede reportar tiempo a otro
        if user.has_perm('reported_hours.multiple_users'):
            ctx['users'] =  User.objects.order_by('first_name').all()
        


       # grouped = ReportedHours.objects.filter(user=user).all().group_by('report_date_at')
        
        
        grouped = (ReportedHours.objects
            .filter(user=user)
            .values('report_date_at')
            .annotate(dcount=Sum('time'))
            .order_by('-report_date_at')
        )

    

        for day in grouped:
            hour = round(day['dcount']//60)
            minute = round(day['dcount']%60)

            hour = "{0:0=2d}".format(hour)
            minute = "{0:0=2d}".format(minute)

            day['hour'] = hour
            day['minute'] = minute
            
            



        last_report  = ReportedHours.objects.filter(user=user).order_by('-report_date_at').first()
        
        if last_report:
            last_report = last_report.created_at - timedelta(hours=5, minutes=0)
            
        
        ctx['last_report'] = last_report


        date = self.request.GET.get('date')

        
        if date:
            reportedhours = ReportedHours.objects.filter(user=user, report_date_at=date).all().order_by('-report_date_at')
        else:
            reportedhours = ReportedHours.objects.filter(user=user).all().order_by('-report_date_at')
        
        reportedhours_paginator = Paginator(reportedhours, 20)

        page_num = self.request.GET.get('page')
        page = reportedhours_paginator.get_page(page_num)

        ctx['page'] = page
        ctx['grouped'] = grouped


        ##reporte rapido de proyectos
        project_id = int(self.request.GET.get('project_id',0))
        projects  = BudgetedHours.objects.filter(state=2, stages=4).prefetch_related('client').all()
        
        projects_search = projects
        if query != '':
            projects = BudgetedHours.objects.filter(state=2, stages=4).filter( Q(code__icontains=query) | Q(client__client__icontains=query)).prefetch_related('client').all()

        
        projects_paginator = Paginator(projects, 10)
        page_num = self.request.GET.get('page_project')
        projects_paginator = projects_paginator.get_page(page_num)
     
        

        drafts = ReportedHoursDraft.objects.order_by('-report_date_at').prefetch_related('activity').filter(Q(user=user) | Q(reported_by=user)).all()
        activities = []
        if project_id:
            activities = Hours.objects.filter(budgeted_hours=project_id).prefetch_related('activity').all()

        
        
        ctx['projects_search'] = projects_search
        ctx['project_id'] = project_id
        ctx['projects'] = projects_paginator
        ctx['activities'] = activities
        ctx['drafts'] = drafts
        ctx['hours'] = [[x,x] for x in range(24)]
        ctx['minutes'] = [[(x),f'{x}'] for x in range(60)]
        ctx['today'] = datetime.datetime.now().strftime ("%Y-%m-%d")



        activitiesjson = []
        for activity in activities:
            a = {"id": activity.activity.id, "activity": activity.activity.activity}        
            activitiesjson.append(a)

        ctx['activitiesjson'] = activitiesjson



        ctx['reportedhours'] = reportedhours 
        return ctx

class ReportedHoursConfirmationView(LoginRequiredMixin, CreateView):
    form_class = ReportedHoursForm
    template_name =  'reported_hours/confirmation.html'
    success_url = reverse_lazy('reported_hours:reported_hours_list')
    
    
    def get_context_data(self, **kwargs):
        ctx = super(ReportedHoursConfirmationView, self).get_context_data(**kwargs)

        code_id = self.request.GET.get('code_id','')
        report_date_at = self.request.GET.get('report_date_at','')
        description = self.request.GET.get('description','')
        activity_id = self.request.GET.get('activity_id','')
        hours = self.request.GET.get('hours','')
        minutes = self.request.GET.get('minutes','')
      
        project = BudgetedHours.objects.prefetch_related('client').get(pk=code_id)
        activity = Activities.objects.get(pk=activity_id)
        user =  self.request.user




        reported = ReportedHours.objects.filter(user=user, code=project, report_date_at=report_date_at).all()

        
        ctx['project'] = project
        ctx['activity'] = activity
        ctx['report_date_at'] = report_date_at
        ctx['description'] = description
        ctx['hours'] = hours
        ctx['minutes'] = minutes
        ctx['reported'] = reported

        return ctx



    def form_valid(self, form):
        print('valid')
        
        hours = form.cleaned_data['hours']

        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.time = hours
        obj.activity_id = self.request.POST['activity_id']
        obj.code_id = self.request.GET['code_id']

    
        return super().form_valid(form)




class ReportedHoursCreateView(LoginRequiredMixin, CreateView):
    
    form_class = ReportedHoursForm
    template_name =  'reported_hours/create.html'


    def get_context_data(self, **kwargs):
        ctx = super(ReportedHoursCreateView, self).get_context_data(**kwargs)

        project = self.request.GET.get('project','')
        project = BudgetedHours.objects.prefetch_related('client').get(pk=project)
        activities = Hours.objects.filter(budgeted_hours=project).prefetch_related('activity').all()


        hours = ReportedHours.objects.filter(code=project)
        
    
        ctx['hours'] = hours
        ctx['activities'] = activities
        ctx['project'] = project

        # Cuento horas presupuestadas del proyecto
        cursor = connection.cursor()
        query = f'SELECT SUM(management) + SUM(software_hours) + SUM(external) + SUM(leader) + SUM(engineer)  FROM budgeted_hours_hours WHERE budgeted_hours_id = {project.pk} GROUP BY  budgeted_hours_id'
        cursor.execute(query)
        row = cursor.fetchone()
        
        total_budgeted_hours = 1
        if row:   
            total_budgeted_hours = int(row[0])

        if total_budgeted_hours == 0:
            total_budgeted_hours = 1

        #obtengo las horas reportas
        query = f'SELECT SUM(time)/60 FROM reported_hours_reportedhours  WHERE code_id = {project.pk} GROUP BY  code_id'
        cursor.execute(query)
        row = cursor.fetchone()

        total_reported_hours = 0
        if row:   
            total_reported_hours = row[0]

        
        #porcentaje
        
        execution = (total_reported_hours*100) / total_budgeted_hours
        ctx['execution'] = execution

        ctx['total_budgeted_hours'] = total_budgeted_hours
        ctx['total_reported_hours'] = total_reported_hours 
        reportedhours  = ReportedHours.objects.filter(code=project).all()

        reportedhours_paginator = Paginator(reportedhours, 20)

        page_num = self.request.GET.get('page')
        page = reportedhours_paginator.get_page(page_num)

        ctx['page'] = page


      

        return ctx



    # def form_valid(self, form):
    #     print('valid')
        
    #     hours = form.cleaned_data['hours']

    #     obj = form.save(commit=False)
    #     obj.user = self.request.user
    #     obj.time = hours
    #     obj.activity_id = self.request.POST['activity_id']
    #     obj.code_id = self.request.GET['project']

    
    #     return super().form_valid(form)



class ReportedHoursDeleteView(LoginRequiredMixin, DeleteView):
    model = ReportedHours
    template_name =  'reported_hours/delete.html'
    success_url = reverse_lazy('reported_hours:reported_hours_list')
    context_object_name = 'hour'
  #  permission_required = 'reported_hours.delete_reportedhours'

 
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        
        if request.user.has_perm('reported_hours.delete_reportedhours'):
            return super(ReportedHoursDeleteView, self).get(request, *args, **kwargs)


        if request.user.pk == obj.user_id and can_delete_report(obj):
            return super(ReportedHoursDeleteView, self).get(request, *args, **kwargs)

        raise PermissionDenied()
        
        

    def get_queryset(self) :
        queryset = ReportedHours.objects.prefetch_related('user').prefetch_related('code')
        return queryset
    
    def delete(self, *args, **kwargs):
        messages.success(self.request, 'reporte eliminada con exito') 
        return super(ReportedHoursDeleteView, self).delete(*args, **kwargs)



class ReportsView(PermissionRequiredMixin, TemplateView):
    template_name =  'reported_hours/reports.html'
    permission_required = 'reported_hours.view_usertoreport'


    def get_context_data(self, **kwargs):
        ctx = super(ReportsView, self).get_context_data(**kwargs)

        # categories = Hours.objects.filter(budgeted_hours = 1).values('category').annotate(dcount=Count('category'))
        # categories_list = [category['category'] for category in categories]

        # categories_version = Hours.objects.filter(budgeted_hours = 1).values('category_version').annotate(dcount=Count('category_version'))
        # categories_version_ids = [category_version['category_version'] for category_version in categories_version]

        cursor = connection.cursor()
        query ='''
            SELECT bhv.id, bhc.category, bhv.version FROM budgeted_hours_hours AS bhh
            INNER JOIN budgeted_hours_categories AS bhc ON bhh.category_id = bhc.id
            INNER JOIN budgeted_hours_categoriesversions AS bhv ON bhh.category_version_id = bhv.id
            WHERE budgeted_hours_id = {} GROUP BY bhv.id, bhc.category, bhv.version ORDER BY bhc.category;
        '''.format(1)
        cursor.execute(query)
        categories_versions = cursor.fetchall()
        # versions = [version[0] for version in cursor.fetchall()]

        # print(categories_list)
        print(categories_versions)

        # print('-----------------------------------')
        # report_hour = ReportedHours.objects.filter(code=1)
        # print(report_hour[0].code)
        # print(report_hour[0].user)
        # print(report_hour[0].time/60)
        # role = RolesUsers.objects.filter(user = report_hour[0].user.id).first()
        # print(role)
        
        users = User.objects.order_by('first_name').all()
        projects  = BudgetedHours.objects.prefetch_related('client').all()
        clients  = Client.objects.all()

        ctx['users'] = users
        ctx['projects'] = projects
        ctx['clients'] = clients

        return ctx


    def getQuery(self, where, dates):
        cursor = connection.cursor()
        
        query ='''
            SELECT 
            to_char( RH.report_date_at, 'DD/MM/YYYY') as "Fecha",
            CONCAT(AU.first_name, ' ', AU.last_name ) as Empleado,
            HH.code as "Codigo",
            HA.activity as "Actividad",
            to_char(RH.time/60::float,'FM999999990.00')  as "Tiempo",
            HC.client as "Cliente",
            ST.service_type as "Servicio",
            RH.description as "Comentarios"
            FROM reported_hours_reportedhours RH
            INNER JOIN budgeted_hours_activities HA ON HA.id = RH.activity_id
            INNER JOIN auth_user AU ON AU.id = RH.user_id
            INNER JOIN budgeted_hours_budgetedhours HH ON HH.id = RH.code_id
            INNER JOIN budgeted_hours_client HC ON HC.id = HH.client_id
            INNER JOIN budgeted_hours_servicetype ST ON ST.id = HA.service_type_id
            WHERE {}    
            {}
            ORDER BY  RH.report_date_at
        '''.format(where, dates)
       # print(query)
        cursor.execute(query)


        
        return cursor.fetchall()

    
    def post(self, request):

        type = self.request.POST['type']
       # value = self.request.POST['value']

        value = self.request.POST.getlist('value[]')
        value = ','.join(map(str, value))
        print(value)
        dates = self.request.POST['dates']
        
        dates = dates.split(' - ')

        
        whereDate = ''
        if len(dates) == 2:
            whereDate = f" AND report_date_at BETWEEN '{dates[0]}' AND  '{dates[1]}'"
        

        if(type == 'user'):
            where = f'user_id IN ({value})'
            query = self.getQuery(where, whereDate)

        if(type == 'code'):
            where = f'HH.id IN ({value})'
            query = self.getQuery(where, whereDate)

        if(type == 'client'):
            where = f'HC.id IN ({value})'
            query = self.getQuery(where, whereDate)

        if(type == 'general'):
            where = '1=1'
            query = self.getQuery(where, whereDate)
        
        count = (len(query))


        #pongo numeros enteros sin los dos puntos
        data = []
        for r in query:
            t = r[4].replace(".00", "")
            data.append([r[0],r[1],r[2],r[3],t,r[5],r[6],r[7]])

        
        if count:
            df = pd.DataFrame(data)
            
            with BytesIO() as b:
                # Use the StringIO object as the filehandle.
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                df.to_excel(writer, sheet_name='Reporte Consolidado', header=('Fecha', 'Nombres', 'Codigo','Actividad','Tiempo (Horas)','Cliente','Servicio','Comentarios'), index=False)
                writer.save()
                filename = 'Reporte'
                content_type = 'application/vnd.ms-excel'
                response = HttpResponse(b.getvalue(), content_type=content_type)
                response['Content-Disposition'] = 'attachment; filename="' + filename + '.xlsx"'
                return response

        messages.error(request, 'No se encontraron registros!')
        return HttpResponseRedirect(reverse_lazy('reported_hours:reported_hours_reports'))




@login_required
def remove_draft(request, pk):
    
    draft =  ReportedHoursDraft.objects.get(pk=pk).delete()
    messages.success(request, 'Elemento eliminado')
    back_url = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(back_url)

@login_required
def apply_drafts(request):

    user =  request.user
    drafs = ReportedHoursDraft.objects.filter(Q(user=user) | Q(reported_by=user)).all()

    for draft in drafs:
        
        report = ReportedHours(user_id=draft.user_id, time=draft.time, description=draft.description, activity_id=draft.activity_id, code_id=draft.code_id, report_date_at=draft.report_date_at)
        report.save()
        draft.delete()
        

    messages.success(request, 'Tiempo aplicado')
    back_url = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(back_url)




def sabana(request):

    today = datetime.date.today()

    date = request.GET.get('date', None)

    if date:
        year,month = date.split('-')
    
    else:
        month = today.month
        year = today.year


    month = int(month)
    year = int(year)

    lastday = calendar.monthrange(year, month)[1]

    subquery = ''
    days = []
    dates = []

    for i in range(lastday):
        day = i+1    
        day = "{:02d}".format(day)
        
        date = f'{year}-{month}-{day}'
        q = f" (SELECT sum(\"time\") FROM reported_hours_reportedhours WHERE report_date_at='{date}' AND user_id=AU.id) as \"{date}\" "
        days.append(q)
        dates.append(date)

    subquery = ','.join(days)
 
    
    query ='''
            SELECT 
                AU.id,
                CONCAT(AU.first_name, ' ', AU.last_name),
                {}
         
                FROM reported_hours_usertoreport UR
            INNER JOIN auth_user AU ON AU.id = UR.user_id
            LEFT JOIN reported_hours_reportedhours RH ON RH.user_id = AU.id
            GROUP BY AU.id
            ORDER BY AU.first_name
        '''.format(subquery)
   
    cursor = connection.cursor()
    cursor.execute(query)

    result = cursor.fetchall()
    

    arr = np.array(result)
    
    
   

    context = {
        'users': arr,
        'dates': dates,
        'year': year,
        'month': month,
    }




    return render(request,'reported_hours/sabana.html', context)
    




class SabanaView(PermissionRequiredMixin, TemplateView):
    template_name =  'reported_hours/sabana.html'
    permission_required = 'reported_hours.view_usertoreport'


    def get_context_data(self, **kwargs):
        ctx = super(SabanaView, self).get_context_data(**kwargs)
        

        today = datetime.date.today()

        date = self.request.GET.get('date', None)

        if date:
            year,month = date.split('-')
        
        else:
            month = today.month
            year = today.year


        month = int(month)
        year = int(year)

        lastday = calendar.monthrange(year, month)[1]

        subquery = ''
        days = []
        dates = []

        for i in range(lastday):
            day = i+1    
            day = "{:02d}".format(day)
            
            date = f'{year}-{month}-{day}'
            q = f" (SELECT sum(\"time\") FROM reported_hours_reportedhours WHERE report_date_at='{date}' AND user_id=AU.id) as \"{date}\" "
            days.append(q)
            dates.append(date)

        subquery = ','.join(days)
 
    
        query ='''
                SELECT 
                    AU.id,
                    CONCAT(AU.first_name, ' ', AU.last_name),
                    {}
            
                    FROM reported_hours_usertoreport UR
                INNER JOIN auth_user AU ON AU.id = UR.user_id
                LEFT JOIN reported_hours_reportedhours RH ON RH.user_id = AU.id
                GROUP BY AU.id
                ORDER BY AU.first_name
            '''.format(subquery)
    
        cursor = connection.cursor()
        cursor.execute(query)

        result = cursor.fetchall()
        

        arr = np.array(result)
        
        
    

        # context = {
        #     'users': arr,
        #     'dates': dates,
        #     'year': year,
        #     'month': month,
        # }

        ctx['users'] = arr
        ctx['dates'] = dates
        ctx['year'] = year
        ctx['month'] = month

        return ctx




class UserReportView(PermissionRequiredMixin, TemplateView):
    template_name =  'reported_hours/user_reported.html'
    permission_required = 'reported_hours.view_usertoreport'


    def get_context_data(self, **kwargs):
        ctx = super(UserReportView, self).get_context_data(**kwargs)
        
        pk  =  self.kwargs.get('pk')
        user = User.objects.get(pk=pk)
        reports  = ReportedHours.objects.filter(user=user).prefetch_related('activity').order_by('-report_date_at')
    
        ctx['user'] = user
        ctx['reports'] = reports

        reportedhours_paginator = Paginator(reports, 20)
        page_num = self.request.GET.get('page')
        page = reportedhours_paginator.get_page(page_num)
        
        ctx['page'] = page
     
        return ctx
