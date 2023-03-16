# import os

# from django import http
# from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
# from django.db.models.expressions import ValueRange
from helpers.email import sendEmail
from django.shortcuts import render, redirect
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
# from django.contrib.auth.models import User
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Q, Count
from django.db import connection

# from django.db.models import Count, Prefetch
from django.core.mail import EmailMessage
from datetime import datetime
# from django.utils import timezone
import pandas as pd
from re import sub
from decimal import Decimal
from io import BytesIO
# from django.db.models import Prefetch

from budgeted_hours.models import (
    Client,
    BudgetedHours,
    Activities,
    Hours,
    Categories,
    ServiceType,
    Softwares,
    TraceabilityBudgetedHours,
    TemplatesBudgetedHours,
    BudgetedHoursHistory,
    TraceabilityBudgetedHoursHistory,
    PriceRequestFormat,
    BudgetedHoursHistoryData,
    BudgetedHoursCategories,
    CategoriesVersions,
    BudgetedHoursFiles,
    STATES,
    STAGES
)

from budgeted_hours.forms.budgeted_hours_form import BudgetedHoursForm

# from mailjet_rest import Client
# from django.core.mail import EmailMultiAlternatives


# Create your views here.
def budgeted_hours_history(request):
    histories = BudgetedHoursHistoryData.objects.all()

    context = {
        'histories': histories
    }

    return render(request, 'budgeted_hours_history/list.html', context)


def budgeted_hours_history_data(request):

    histories_data = BudgetedHoursHistoryData.objects.filter(pk = request.GET['id']).all()

    context = {
        'histories_data': histories_data
    }

    return render(request, 'budgeted_hours_history/detail.html', context)


def download_budgeted_hours(request):

    budgetedhours_pks = request.GET.getlist('budgetedhours_pks[]')
    budgeted_hours = tuple(budgetedhours_pks)

    if len(budgeted_hours) <= 1: budgeted_hours = f"('{budgetedhours_pks[0]}')"

    cursor = connection.cursor()

    query = '''
    SELECT
        bh.code,
        budgeted_hours_client.client,
        budgeted_hours_servicetype.service_type,
        bh.value,
        bh.additional_costs,
        auth_user.username,
        bh.created_at,
        bh.state,
        bh.stages,
        bh.title,
        bh.description,
        bh.document_url,
        bh.start_at,
        bh.duration_deliverables
    FROM budgeted_hours_budgetedhours AS bh
    INNER JOIN budgeted_hours_client ON budgeted_hours_client.id = bh.client_id
    INNER JOIN budgeted_hours_servicetype ON budgeted_hours_servicetype.id = bh.service_type_id
    INNER JOIN auth_user ON auth_user.id = bh.created_by_id
    WHERE bh.id IN {};
    '''.format(budgeted_hours)

    cursor.execute(query)

    result_query = cursor.fetchall()

    df = pd.DataFrame(result_query)
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Horas presupuestadas', header=('Código', 'Cliente', 'Tipo de servicio', 'Valor', 'Costos adicionales', 'Creado por', 'Creado en', 'Estado', 'Etapa', 'Titulo', 'Descripción', 'URL', 'Fecha inicio', 'Duración'), index=False)
        writer.save()
        filename = 'Horas presupuestadas'
        content_type = 'application/vnd.ms-excel'
        response = HttpResponse(b.getvalue(), content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="' + filename + '.xlsx"'
        return response


# @method_decorator(login_required, name='dispatch')
class BudgetedHoursListView(PermissionRequiredMixin, ListView):

    model = BudgetedHours
    template_name = 'budgeted_hours/list.html'
    # context_object_name = 'budgetedhours'
    permission_required = 'budgeted_hours.view_budgetedhours'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        traceability_history = TraceabilityBudgetedHoursHistory.objects.all()
        context['traceability_history'] = traceability_history

        codes = BudgetedHours.objects.values_list('code', flat=True)
        context['codes'] = codes

        clients = Client.objects.filter(pk__in = BudgetedHours.objects.values_list('client', flat=True))
        context['clients'] = clients

        service_types = ServiceType.objects.filter(pk__in = BudgetedHours.objects.values_list('service_type', flat=True))
        context['service_types'] = service_types

        context['states'] = STATES

        context['stages'] = STAGES

        users = User.objects.filter(pk__in = BudgetedHours.objects.values_list('created_by', flat=True))
        context['users'] = users

        query = self.request.GET.get('q','')
        query2 = self.request.GET.get('q2','')
        query3 = self.request.GET.get('q3','')
        query4 = self.request.GET.get('q4','')
        query5 = self.request.GET.get('q5','')
        query6 = self.request.GET.get('q6','')
        query7 = self.request.GET.get('q7','')

        # print(query)
        # print(query2)
        # print(query3)
        # print(query4)
        # print(query5)
        # print(query6)
        # print(query7)
        context['query'] = query
        context['query2'] = query2
        context['query3'] = query3
        context['query4'] = int(query4) if query4 != '' else query4
        context['query5'] = int(query5) if query5 != '' else query5
        context['query6'] = query6
        context['query7'] = query7

        if query != '' or query2 != '' or query3 != '' or query4 != '' or query5 != '' or query6 != '' or query7 != '':
            projects = BudgetedHours.objects.filter(
                Q(code__icontains=query) &
                Q(client__client__icontains=query2) &
                Q(service_type__service_type__icontains=query3) &
                Q(state__icontains=query4) &
                Q(stages__icontains=query5) &
                Q(created_by__username__icontains=query6) &
                Q(start_at__icontains=query7)
            ).prefetch_related('client', 'service_type', 'created_by').all()[:20]
            # print(projects)
            context['budgetedhours'] = projects

        else:
            budgetedhours = BudgetedHours.objects.all()[:20]
            context['budgetedhours'] = budgetedhours

        return context


def activities_by_service(request):
    service_type = request.GET['service_type_id']
    activities = Activities.objects.filter(service_type=service_type).values()
    activities = list(activities)

    context = {
        'activities': activities
    }

    return JsonResponse(context)


# @method_decorator(login_required, name='dispatch')
class BudgetedHoursCreateView(PermissionRequiredMixin, CreateView):

    model = BudgetedHours
    form_class = BudgetedHoursForm
    template_name = 'budgeted_hours/create.html'
    # success_url = reverse_lazy('budgeted_hours:budgeted_hours_list')
    permission_required = 'budgeted_hours.add_budgetedhours'


    def get_context_data(self, **kwargs):
        context = super(BudgetedHoursCreateView, self).get_context_data(**kwargs)
        # activities = Activities.objects.values_list('study_type', flat=True)
        service_type = ServiceType.objects.all()
        # study_type = STUDY_TYPE
        softwares = Softwares.objects.all()
        # print(activities)
        context['service_type'] = service_type
        context['softwares'] = softwares

        return context


    def get_success_url(self):
        # print(self.request.POST)

        hours_engineer = self.request.POST.getlist('engineer[]')
        hours_leader = self.request.POST.getlist('leader[]')
        hours_senior_leader = self.request.POST.getlist('senior_leader[]')
        hours_management = self.request.POST.getlist('management[]')
        hours_software = self.request.POST.getlist('software[]')
        type_software = self.request.POST.getlist('type_software[]')
        hours_external = self.request.POST.getlist('external[]')

        activities = Activities.objects.filter(service_type = self.object.service_type).values_list('id', flat=True)
        # budgeted_hours = BudgetedHours.objects.get(pk=self.object.id)
        categories = Categories.objects.all()

        if categories:
            category = Categories.objects.first()
        else:
            instance = Categories(
                category = 'Alcance 1'
            )
            instance.save()
            category = Categories.objects.first()

        instance =  BudgetedHoursCategories(
            budgeted_hours = self.object,
            category = category
        )
        instance.save()

        instance_2 = CategoriesVersions(
            budgeted_hours_categories = instance
        )
        instance_2.save()

        for i in range(len(activities)):

            activity = Activities.objects.get(pk=activities[i])

            if type_software[i]:
                software = Softwares.objects.get(pk=type_software[i])
            else:
                software = None

            instance = Hours(
                budgeted_hours=self.object,
                activity=activity,
                category=category,
                software=software,
                engineer = 0 if hours_engineer[i] == '' or hours_engineer[i] == None else hours_engineer[i],
                leader = 0 if hours_leader[i] == '' or hours_leader[i] == None else hours_leader[i],
                senior_leader = 0 if hours_senior_leader[i] == '' or hours_senior_leader[i] == None else hours_senior_leader[i],
                management = 0 if hours_management[i] == '' or hours_management[i] == None else hours_management[i],
                software_hours = 0 if hours_software[i] == '' or hours_software[i] == None else hours_software[i],
                external = 0 if hours_external[i] == '' or hours_external[i] == None else hours_external[i],
                category_version = instance_2
            )
            instance.save()

        instance_3 = PriceRequestFormat(
            budgeted_hours = self.object
        )
        instance_3.save()

        instance_4 = TraceabilityBudgetedHours(
            budgeted_hours = self.object
        )
        instance_4.save()

        instance_5 = BudgetedHoursFiles(
            budgeted_hours = self.object
        )
        instance_5.save()

        return reverse_lazy('budgeted_hours:budgeted_hours_view', args=[self.object.id])



    # def post(self, *args, **kwargs):
    #     print('________')
    #     print(self.request.POST)
    #     print('________')
    #     print(self.request.POST.getlist('engineer[]'))
    #     print(self.request.POST.getlist('leader[]'))
    #     print(self.request.POST.getlist('management[]'))
    #     print(self.request.POST.getlist('software[]'))
    #     print('________')


    def form_valid(self, form):
        # print(self.request)
        messages.success(self.request, 'Horas presupuestadas creadas con éxito')
        return super().form_valid(form)


    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.accepts('text/html'):
            return response
        else:
            return JsonResponse(form.errors, status=400)


def budgeted_hours_update(request):
    # print(request.POST)

    new_version = request.POST.get('new_version')

    hours_pks = request.POST.getlist('hours_pks[]')
    hours_engineer = request.POST.getlist('engineer[]')
    hours_leader = request.POST.getlist('leader[]')
    hours_senior_leader = request.POST.getlist('senior_leader[]')
    hours_management = request.POST.getlist('management[]')
    hours_software = request.POST.getlist('software[]')
    type_software = request.POST.getlist('type_software[]')
    hours_external = request.POST.getlist('external[]')

    budgeted_hours_categories = BudgetedHoursCategories.objects.filter(budgeted_hours = request.POST.get('budgeted_hours'), category = request.POST.get('category')).all()

    value = request.POST.get('value')
    if value:
        value = Decimal(sub(r'[^\d.]', '', value))
    else:
        value = 0

    if budgeted_hours_categories:
        instance = BudgetedHoursCategories.objects.get(pk = budgeted_hours_categories[0].id)
        instance.value = value
        instance.save()

    if new_version:
        first_hour = Hours.objects.get(pk = hours_pks[0])
        category_version = CategoriesVersions.objects.get(pk = first_hour.category_version.id)
        last_version = CategoriesVersions.objects.filter(budgeted_hours_categories = category_version.budgeted_hours_categories).latest('version')

        instance = CategoriesVersions(
            budgeted_hours_categories = last_version.budgeted_hours_categories,
            version = last_version.version + 1
        )
        instance.save()

        for i in range(len(hours_pks)):
            hours = Hours.objects.get(pk = hours_pks[i])
            # print(hours)

            if type_software[i]:
                software = Softwares.objects.get(pk = type_software[i])
            else:
                software = None

            instance_2 = Hours(
                budgeted_hours = hours.budgeted_hours,
                activity = hours.activity,
                category = hours.category,
                software = software,
                engineer = 0 if hours_engineer[i] == '' or hours_engineer[i] == None else hours_engineer[i],
                leader = 0 if hours_leader[i] == '' or hours_leader[i] == None else hours_leader[i],
                senior_leader = 0 if hours_senior_leader[i] == '' or hours_senior_leader[i] == None else hours_senior_leader[i],
                management = 0 if hours_management[i] == '' or hours_management[i] == None else hours_management[i],
                software_hours = 0 if hours_software[i] == '' or hours_software[i] == None else hours_software[i],
                external = 0 if hours_external[i] == '' or hours_external[i] == None else hours_external[i],
                category_version = instance
            )
            instance_2.save()

    else:

        for i in range(len(hours_pks)):
            instance = Hours.objects.get(pk = hours_pks[i])

            if type_software[i]:
                software = Softwares.objects.get(pk = type_software[i])
                instance.software = software
            else:
                instance.software = None

            instance.engineer = 0 if hours_engineer[i] == '' or hours_engineer[i] == None else hours_engineer[i]
            instance.leader = 0 if hours_leader[i] == '' or hours_leader[i] == None else hours_leader[i]
            instance.senior_leader = 0 if hours_senior_leader[i] == '' or hours_senior_leader[i] == None else hours_senior_leader[i]
            instance.management = 0 if hours_management[i] == '' or hours_management[i] == None else hours_management[i]
            instance.software_hours = 0 if hours_software[i] == '' or hours_software[i] == None else hours_software[i]
            instance.external = 0 if hours_external[i] == '' or hours_external[i] == None else hours_external[i]
            instance.save()

        # budgeted_hours = BudgetedHours.objects.get(pk = request.POST.get('budgeted_hours'))
        # user = User.objects.get(pk = request.user.id)
        # if budgeted_hours and user:
        #     instance = BudgetedHoursHistory(
        #         budgeted_hours = budgeted_hours,
        #         updated_by = user
        #     )
        #     instance.save()

    messages.success(request, 'Horas presupuestadas actualizadas con éxito')
    return redirect('budgeted_hours:budgeted_hours_view', request.POST.get('budgeted_hours'))


def budgeted_hours_add(request):
    # print(request.POST)
    if request.POST:
        activities_pks = request.POST.getlist('activities_pks[]')
        hours_engineer = request.POST.getlist('engineer[]')
        hours_leader = request.POST.getlist('leader[]')
        hours_senior_leader = request.POST.getlist('senior_leader[]')
        hours_management = request.POST.getlist('management[]')
        hours_software = request.POST.getlist('software[]')
        type_software = request.POST.getlist('type_software[]')
        hours_external = request.POST.getlist('external[]')

        # print(request.POST.get('budgeted_hours'))
        budgeted_hours = BudgetedHours.objects.get(pk = request.POST.get('budgeted_hours'))
        category = Categories.objects.get(pk = request.POST.get('category'))

        instance =  BudgetedHoursCategories(
            budgeted_hours = budgeted_hours,
            category = category
        )
        instance.save()

        instance_2 = CategoriesVersions(
            budgeted_hours_categories = instance
        )
        instance_2.save()

        for i in range(len(activities_pks)):
            activity = Activities.objects.get(pk = activities_pks[i])

            if type_software[i]:
                software = Softwares.objects.get(pk=type_software[i])
            else:
                software = None

            instance = Hours(
                budgeted_hours=budgeted_hours,
                activity=activity,
                category=category,
                software=software,
                engineer = 0 if hours_engineer[i] == '' or hours_engineer[i] == None else hours_engineer[i],
                leader = 0 if hours_leader[i] == '' or hours_leader[i] == None else hours_leader[i],
                senior_leader = 0 if hours_senior_leader[i] == '' or hours_senior_leader[i] == None else hours_senior_leader[i],
                management = 0 if hours_management[i] == '' or hours_management[i] == None else hours_management[i],
                software_hours = 0 if hours_software[i] == '' or hours_software[i] == None else hours_software[i],
                external =  0 if hours_external[i] == '' or hours_external[i] == None else hours_external[i],
                category_version = instance_2
            )
            instance.save()

        messages.success(request, 'Horas presupuestadas creadas con éxito')
        return redirect('budgeted_hours:budgeted_hours_view', request.POST.get('budgeted_hours'))


def hours_import(request):
    # print(request.GET)
    # print(request.FILES)
    if request.method == 'POST':
        try:
            df = pd.read_excel(request.FILES['file'], engine = 'openpyxl')
            hours = Hours.objects.filter(budgeted_hours=request.GET['budgeted_hours']).filter(category=request.GET['category']).all()

            dict_names = {
                'actividad': 'activity',
                'ingeniero': 'engineer',
                'líder': 'leader',
                'líder senior': 'senior_leader',
                'gerencia': 'management',
                'horas de software': 'software_hours',
                'externo': 'external'
            }

            for name_col in dict_names.keys():
                if name_col not in df.columns:
                    raise NameError(f'La columna "{name_col}" no se encuentra en el archivo')

            if len(df.index) != len(hours):
                raise NameError(f'Las filas del archivo no coinciden con las actividades (filas: Archivo {len(df.index)}, Actividades {len(hours)})')

            df.rename(columns=dict_names, inplace=True)
            df = df.astype(str)
            df.replace(to_replace=["nan", " - "], value=[0, 0], inplace=True)
            # print(df)

            for index, row in df.iterrows():
                for i in range(len(hours)):
                    if row[0] == hours[i].activity.activity:
                        instance = Hours.objects.get(pk=hours[i].id)
                        instance.engineer = row[1]
                        instance.leader = row[2]
                        instance.senior_leader = row[3]
                        instance.management = row[4]
                        instance.software_hours = row[5]
                        instance.external = row[6]
                        instance.save()

            messages.success(request, 'Importación realizada con éxito')
            return redirect('budgeted_hours:budgeted_hours_view', request.GET.get('budgeted_hours'))

        except Exception as e:
            # print(e)
            messages.error(request, 'Error de importación: ' + str(e))
            return redirect('budgeted_hours:budgeted_hours_view', request.GET.get('budgeted_hours'))

    else:
        return render(request, 'import_file/import_file.html')


def send_mail(request):
    # print('Get', request.GET)
    # print('Post', request.POST)

    if request.POST:
        users = request.POST.getlist('users[]')
        # print(users)

        if users:
            budgeted_hours = BudgetedHours.objects.get(pk = request.POST['budgeted_hours_id'])
            traceability = TraceabilityBudgetedHours.objects.filter(budgeted_hours = budgeted_hours).all()

            if budgeted_hours and traceability:
                # print(settings.URL_SITE)

                context = {
                    'budgeted_hours': budgeted_hours,
                    'URL_SITE': settings.URL_SITE
                }

                body = render_to_string('emails/template.html', context)

                for user in users:
                    # print('Usuario', user)
                    email = sendEmail('¡Nueva propuesta a desarrollar!', body, user)

                messages.success(request, 'Mensaje enviado con éxito')
                return redirect('budgeted_hours:budgeted_hours_view', request.POST['budgeted_hours_id'])
            else:
                # print(settings.URL_SITE)

                instance = TraceabilityBudgetedHours(
                    budgeted_hours = budgeted_hours
                )
                instance.save()

                context = {
                    'budgeted_hours': budgeted_hours,
                    'URL_SITE': settings.URL_SITE
                }

                body = render_to_string('emails/template.html', context)

                for user in users:
                    # print('Usuario', user)
                    email = sendEmail('¡Nueva propuesta a desarrollar!', body, user)

                # users_emails = User.objects.filter(groups__name='financiero').all().values_list('email', flat=True)
                # print("Usuarios", users_emails)

                # email = EmailMessage('¡Nuevas horas presupuestadas!', body, settings.EMAIL_SENDER, to=users)
                # email.attach_file('C:/Users/alexi/Downloads/___ Comunica ___.pdf')
                # email.send()

                messages.success(request, 'Mensaje enviado con éxito')
                return redirect('budgeted_hours:budgeted_hours_view', request.POST['budgeted_hours_id'])

        else:
            messages.error(request, 'Es necesario seleccionar mínimo un responsable')
            return redirect('budgeted_hours:budgeted_hours_view', request.POST['budgeted_hours_id'])

    else:
        return HttpResponse('Mensaje (NO POST)')

        pending_budgeted_hours = TraceabilityBudgetedHours.objects.filter(reviewed_by_financial=None).all()
        if pending_budgeted_hours:
            for pending in pending_budgeted_hours:
                # print(pending.budgeted_hours)

                body = """
                Código: {}\n
                Cliente: {}\n
                Tipo de estudio: {}\n
                """.format(pending, pending.budgeted_hours.client, pending.budgeted_hours.get_study_type_display())

                # users_emails = User.objects.filter(groups__name='financiero').all().values_list('email', flat=True)
                # print("Usuarios", users_emails)

                email = EmailMessage('Horas presupuestadas pendientes!', body, settings.EMAIL_SENDER, to=['alex.igirio@phc.com.co'])
                email.send()

            return HttpResponse('Mensajes enviados con éxito')


def reviewed(request):

    budgeted_hours = BudgetedHours.objects.get(pk = request.GET['id'])

    if budgeted_hours:
        traceability = TraceabilityBudgetedHours.objects.filter(budgeted_hours = budgeted_hours.id).all()
        user = User.objects.get(pk = request.user.id)

        if traceability and user:

            instance = TraceabilityBudgetedHoursHistory(
                budgeted_hours = traceability[0],
                reviewed_by = user
            )
            instance.save()

            messages.success(request, 'Revisado con éxito')
            return redirect('budgeted_hours:budgeted_hours_view', request.GET['id'])

        else:
            messages.error(request, 'Es necesario que se envié el mensaje primero')
            return redirect('budgeted_hours:budgeted_hours_view', request.GET['id'])


# @method_decorator(login_required, name='dispatch')
class BudgetedHoursDetailView(PermissionRequiredMixin, UpdateView):

    model = BudgetedHours
    form_class = BudgetedHoursForm
    template_name = 'budgeted_hours/detail.html'
    # success_url = reverse_lazy('budgeted_hours:budgeted_hours_list')
    permission_required = 'budgeted_hours.change_budgetedhours'


    def get_context_data(self, **kwargs):
        context = super(BudgetedHoursDetailView, self).get_context_data(**kwargs)

        # Se filtran los (ids de las horasPres... por categoria) en la tabla de BudgetedHoursCategories donde (budgeted_hours = id) y se hace una [] con los ids
        budgeted_hours_categories_id = BudgetedHoursCategories.objects.filter(budgeted_hours = self.object.id).values_list('id', flat = True)
        # print(budgeted_hours_categories_id)

        # Se filtran los (ids de las categorias) y se hace una [] con los ids
        budgeted_hours_categories = BudgetedHoursCategories.objects.filter(budgeted_hours = self.object.id).values_list('category', flat=True)

        # Se filtra las (versiones) en la tabla CategoriesVersions donde (budgeted_hours_categories = a la [] de (budgeted_hours_categories_id)) el resultado es una [] filtrada por las categorias de las horasPres...
        categories_versions = CategoriesVersions.objects.filter(budgeted_hours_categories__in = budgeted_hours_categories_id).order_by('budgeted_hours_categories').all()

        categories_versions_hours_list = []

        # Se itera en las categories_versions
        for category_version in categories_versions:

            # Se filtra las (horas) de la tabla Hours donde (category_version = a la iteracion de categories_versions por el id) el resultado es una [] por cada iteración
            hours = Hours.objects.filter(category_version = category_version.id).all()

            # Se crea un (diccionario/objecto) donde el valor de category_version es el objecto de la iteración, la versión es la versión de la iteración y las horas de la iteración
            category_version_hours = {
                'category_version': category_version,
                'version': category_version.version,
                'hours': hours
            }

            # Se agrega el (diccionario/objecto) a la [] categories_versions_hours_list
            categories_versions_hours_list.append(category_version_hours)

        groups = {}

        # Se itera en la [] de categories_versions_hours_list
        for i in categories_versions_hours_list:

            # Se agrupa por (category_version) el resultado es un {} con las categorias y el valor es las versiones con las horas
            # Función setdefault() link https://www.w3schools.com/python/ref_dictionary_setdefault.asp
            groups.setdefault(i['category_version'].budgeted_hours_categories, []).append({k: v for k, v in i.items() if k != 'category_version'})

        categories_all = Categories.objects.all()

        categories = []
        for category in categories_all:
            if category.id not in budgeted_hours_categories:
                categories.append(category)

        activities = Activities.objects.filter(service_type = self.object.service_type).all()
        softwares = Softwares.objects.all()
        templates_budgeted_hours = TemplatesBudgetedHours.objects.all()
        price_request_format = PriceRequestFormat.objects.filter(budgeted_hours = self.object.id).values().first()

        ##################################################

        total_softwares = []
        alcances = {}

        for k, v in groups.items():
            # print(k.category)
            alcances = {'scope' + str(k): ''}
            versiones = {}
            for version in v:
                # print('Versión', version['version'])
                valores = {}
                for software in softwares:
                    software_hours = 0
                    for i in version['hours']:
                        if software == i.software:
                            # print(i.software, i.software_hours)

                            software_hours += i.software_hours
                            # print(software_hours)
                            valores[i.software] = software_hours
                            # alcance.update({k: valores})

                versiones['version' + str(version['version'])] = valores
            alcances['scope' + str(k)] = versiones
            # if 'scope'+str(k) not in alcances.keys():
            total_softwares.append(alcances)
            # print(total_softwares)
            # print(alcances)
        # print(total_softwares)



        ##################################################
        ##################################################
        ##################################################

        # categories = Categories.objects.prefetch_related(Prefetch('hours', queryset=Hours.objects.filter(budgeted_hours=self.object.id))).annotate(dcount=Count('category')).order_by().all()

        # alcances = []


        # versions = Hours.objects.filter(budgeted_hours = self.object).latest('version')
        # # print('versiones', versions.version)
        # versions_list = []

        # for version in range(1, versions.version + 1):
        #     versions_list.append(version)

        # # print(versions_list)
        # context['versions_list'] = versions_list

        # for v in versions_list:
        #     for category in categories:
        #         # print(category)
        #         if category.hours.all():
        #             alcance = {}
        #             alcance['alcance'] = category

        #             for hour in category.hours.all():
        #                 if hour.version == v:
        #                     pass
        #                     # print('tiene versión', v)
        #                     # print(hour.engineer)

        # hours = Hours.objects.filter(budgeted_hours=self.object.id).all()

        ###########################################################

        cursor = connection.cursor()
        query ='''
            SELECT bhv.id, bhc.category, bhv.version FROM budgeted_hours_hours AS bhh
            INNER JOIN budgeted_hours_categories AS bhc ON bhh.category_id = bhc.id
            INNER JOIN budgeted_hours_categoriesversions AS bhv ON bhh.category_version_id = bhv.id
            WHERE budgeted_hours_id = {} GROUP BY bhv.id, bhc.category, bhv.version ORDER BY bhc.category;
        '''.format(self.object.id)
        cursor.execute(query)
        categories_versions = cursor.fetchall()

        traceability = TraceabilityBudgetedHours.objects.filter(budgeted_hours = self.object.id).values().first()
        if traceability:
            reviewed_by = TraceabilityBudgetedHoursHistory.objects.filter(budgeted_hours = traceability['id'])

            if reviewed_by:
                reviewed_by = TraceabilityBudgetedHoursHistory.objects.filter(budgeted_hours = traceability['id']).latest('reviewed_at')
                context['reviewed_by'] = reviewed_by

        context['price_request_format'] = price_request_format
        context['traceability'] = traceability

        # context['categories'] = categories
        context['categories_versions'] = categories_versions
        context['budgeted_hours'] = self.object
        context['activities'] = activities
        context['softwares'] = softwares
        context['templates_budgeted_hours'] = templates_budgeted_hours

        context['categories'] = categories
        context['groups'] = groups
        context['categories_all'] = categories_all

        return context


    def get_success_url(self):
        # print(self.request.POST)

        #     print('get')
        # print(self.request.POST)
        # print(self.request.user.id)
        # print(self.object)
    #     hours_engineer = self.request.POST.getlist('engineer[]')
    #     hours_leader = self.request.POST.getlist('leader[]')
    #     hours_management = self.request.POST.getlist('management[]')
    #     hours_software = self.request.POST.getlist('software[]')

        # budgeted_hours = BudgetedHours.objects.get(pk=self.object.id)
        # user = User.objects.get(pk = self.request.user.id)
        # if budgeted_hours and user:
        #     instance = BudgetedHoursHistory(
        #         budgeted_hours = budgeted_hours,
        #         updated_by = user
        #     )
        #     instance.save()
        #     print(instance)
        #     print(instance.id)

    #     activities = Activities.objects.filter(study_type=self.object.study_type).values_list('id', flat=True)
    #     print(activities)

    #     categories = Categories.objects.filter(category='Caso base').values_list('id', flat=True)
    #     category = Categories.objects.get(pk=categories[0])


    #     for i in range(len(activities)):
    #         activity = Activities.objects.get(pk=activities[i])

    #         hours = Hours.objects.filter(activity=activity).values_list('id', flat=True)
    #         print(hours)
    #         instance = Hours.objects.get(pk=hours[0])
    #         print('instance', instance)


    #         instance.budgeted_hours=budgeted_hours
    #         instance.activity=activity
    #         instance.category=category
    #         instance.engineer=hours_engineer[i]
    #         instance.leader=hours_leader[i]
    #         instance.management=hours_management[i]
    #         instance.software=hours_software[i]

    #         instance.save()

        return reverse_lazy('budgeted_hours:budgeted_hours_view', args=[self.object.id])


    def form_valid(self, form):
        obj = form.save(commit=False)

        if self.request.POST:
            users = self.request.POST.getlist('users[]')
            traceability = TraceabilityBudgetedHours.objects.filter(budgeted_hours = self.object.id).all()
            # print(traceability[0])
            # print(len(TraceabilityBudgetedHoursHistory.objects.filter(budgeted_hours = traceability[0])))

            if traceability:

                instance = TraceabilityBudgetedHoursHistory(
                    budgeted_hours = traceability[0],
                    reviewed_by = self.request.user,
                    stages = self.object.stages
                )
                instance.save()

                messages.success(self.request, 'Revisado con éxito')

            if users:

                # Verificar si hay trazabilidad para enviar un asunto diferente
                # Importante mirar si es el primer registro de (TraceabilityBudgetedHoursHistory)
                ############################
                ############################
                ############################
                ############################
                ############################

                context = {
                    'budgeted_hours': self.object,
                    'URL_SITE': settings.URL_SITE
                }

                body = render_to_string('emails/template.html', context)

                # if len(TraceabilityBudgetedHoursHistory.objects.filter(budgeted_hours = traceability[0])) > 1:
                msj = f'{self.object.code}, Estado: {self.object.get_state_display()}, Etapa: {self.object.get_stages_display()}'
                    # print(msj)
                # else:
                #     msj = f'¡Nueva propuesta a desarrollar!'
                    # print(msj)

                for user in users:
                    email = sendEmail(msj, body, user)

                messages.success(self.request, 'Mensaje enviado con éxito')

            else:
                messages.error(self.request, 'Es necesario seleccionar mínimo un responsable')
                return HttpResponseRedirect(self.get_success_url())

        instance = BudgetedHoursHistory(
            budgeted_hours = self.object,
            updated_by = self.request.user
        )
        instance.save()

        budgeted_hours = BudgetedHours.objects.get(pk = self.object.id)
        if budgeted_hours:
            instance_2 = BudgetedHoursHistoryData(
                budgeted_hours_history = instance,
                code = budgeted_hours.code,
                client = budgeted_hours.client,
                additional_costs = budgeted_hours.additional_costs
            )
            instance_2.save()

        messages.success(self.request, 'Horas presupuestadas actualizadas con éxito')
        obj.save()
        # print('Save')

        return HttpResponseRedirect(self.get_success_url())


    def post(self, request, **kwargs):
        request.POST = request.POST.copy()

        additional_costs = request.POST.get('additional_costs')
        if additional_costs:
            additional_costs = Decimal(sub(r'[^\d.]', '', additional_costs))
        else:
            additional_costs = 0

        request.POST['additional_costs'] = additional_costs

        return super(BudgetedHoursDetailView, self).post(request, **kwargs)


# @method_decorator(login_required, name='dispatch')
class BudgetedHoursDeleteView(PermissionRequiredMixin, DeleteView):

    model = BudgetedHours
    template_name = 'budgeted_hours/delete.html'
    success_url = reverse_lazy('budgeted_hours:budgeted_hours_list')
    context_object_name = 'budgetedhours'
    permission_required = 'budgeted_hours.delete_budgetedhours'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'horas presupuestadas eliminadas con exito')
        return super(BudgetedHoursDeleteView, self).delete(*args, **kwargs)




def test(request):


    context = {
        'content': '--Te acompañamos en tu propósito de tener vivienda propia. Conversemos el próximo sábado 17 de julio a las 11:00 a. m. sobre los pasos que debes recorrer para tener casa propia. Además, hablaremos sobre educación financiera, ahorro, subsidios y el programa Camino a mi casa.'
    }

    body = render_to_string('emails/template.html', context)

    users = ['alex.igirio@phc.com.co']

    email = sendEmail('¡Horas presupuestadas!', body, users, 'C:/Users/alexi/Downloads/horarioMatricula 2021-2.pdf')

    return render(request, 'emails/template.html', context)


    # body = """
    # Código: {}\n
    # Cliente: {}\n
    # Tipo de estudio: {}\n
    # """.format(11, 22, 32)

    # email = EmailMessage('¡Horas presupuestadas!', body, settings.EMAIL_SENDER, to=['alex.igirio@phc.com.co'])
    # email.send()


    # body = render_to_string('emails/template.html', { 'foo': 'bar' })

    # mailjet = Client(auth=('047dd0fb4c9d4790cb8113ed38c384f1', 'c201f5da67867f3d7c7fa4ae5665ad93'), version='v3.1')
    # data = {
    #     'Messages': [
    #         {
    #         "From": {
    #             "Email": 'no-responder@datcore.site',
    #             "Name": "Datcore"
    #         },
        
    #         "To": [
    #             {
    #             "Email": "susana.marin@phc.com.co",
    #             "Name": "Susana Marin"
    #             }
    #         ],
    #         "Subject": "Horas presupuestadas",
    #         "TextPart": "Charla de Horas presupuestadas",
    #         "HTMLPart": body
    #         }
    #     ]
    #     }
    # result = mailjet.send.create(data=data)
    # print (result.status_code)
    # print (result.json())
    



    # return render(request, 'emails/template.html')