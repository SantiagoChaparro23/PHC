from django.shortcuts import render, redirect
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
# from django.contrib.auth.models import User

from django.db.models import Count, Prefetch
from django.core.mail import EmailMessage
# from datetime import datetime
import pandas as pd
# import numpy as np
# from django.db.models import Prefetch

from budgeted_hours.models import TemplatesBudgetedHours, Activities, HoursTemplates, Hours, Categories, Softwares, TraceabilityBudgetedHours, BudgetedHours

from budgeted_hours.forms.templates_budgeted_hours_form import TemplatesBudgetedHoursForm

# Create your views here.
# @method_decorator(login_required, name='dispatch')
class TemplatesBudgetedHoursListView(PermissionRequiredMixin, ListView):

    model = TemplatesBudgetedHours
    template_name = 'templates_budgeted_hours/list.html'
    context_object_name = 'templatesbudgetedhours'
    permission_required = 'budgeted_hours.view_templatesbudgetedhours'


def activities_by_service_template(request):
    service_type = request.GET['id_service_type']
    activities = Activities.objects.filter(service_type=service_type).values()
    activities = list(activities)

    context = {
        'activities': activities
    }

    return JsonResponse(context)


# @method_decorator(login_required, name='dispatch')
class TemplatesBudgetedHoursCreateView(PermissionRequiredMixin, CreateView):

    model = TemplatesBudgetedHours
    form_class = TemplatesBudgetedHoursForm
    template_name = 'templates_budgeted_hours/create.html'
    # success_url = reverse_lazy('budgeted_hours:budgeted_hours_list')
    permission_required = 'budgeted_hours.add_templatesbudgetedhours'


    def get_context_data(self, **kwargs):
        context = super(TemplatesBudgetedHoursCreateView, self).get_context_data(**kwargs)
        # activities = Activities.objects.values_list('study_type', flat=True)
        # study_type = STUDY_TYPE
        softwares = Softwares.objects.all()
        # print(activities)
        # context['study_type'] = study_type
        context['softwares'] = softwares
        # ctx['nombre'] = 'alex'
        return context


    def get_success_url(self):
        # print('get_success_url')
        print(self.request.POST)
        # print('________')
        # print(self.object)
        # print(self.object.id)
        # print(self.object.client)
        hours_engineer = self.request.POST.getlist('engineer[]')
        hours_leader = self.request.POST.getlist('leader[]')
        hours_management = self.request.POST.getlist('management[]')
        hours_software = self.request.POST.getlist('software[]')
        type_software = self.request.POST.getlist('type_software[]')
        hours_external = self.request.POST.getlist('external[]')

        activities = Activities.objects.filter(service_type = self.object.service_type.id).values_list('id', flat=True).all()
        print(activities)

        templates_budgeted_hours = TemplatesBudgetedHours.objects.get(pk=self.object.id)

        # categories = Categories.objects.filter(category='Caso base').values_list('id', flat=True)
        # # print(categories)
        # if categories:
        #     category = Categories.objects.get(pk=categories[0])
        #     # print('category if:', category)
        # else:
        #     instance = Categories(category='Caso base')
        #     instance.save()
        ############
        # category = Categories.objects.get(pk=1)
            # print('category else:', category)

        # print(self.request.POST.getlist('engineer[]'))
        # print(self.request.POST.getlist('leader[]'))
        # print(self.request.POST.getlist('management[]'))
        # print(self.request.POST.getlist('software[]'))
        # print('________')

        for i in range(len(activities)):

            activity = Activities.objects.get(pk=activities[i])

            if type_software[i] is not '':
                software = Softwares.objects.get(pk=type_software[i])
                # print('software:', software)
            else:
                software = None

            instance = HoursTemplates(
                templates_budgeted_hours=templates_budgeted_hours,
                activity=activity,
                # category=category,
                software=software,
                engineer=hours_engineer[i],
                leader=hours_leader[i],
                management=hours_management[i],
                software_hours=hours_software[i],
                external=hours_external[i]
            )

            instance.save()

        return reverse_lazy('budgeted_hours:templates_budgeted_hours_list')



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
        messages.success(self.request, 'Plantilla de horas presupuestadas creada con éxito')
        return super().form_valid(form)


    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.accepts('text/html'):
            return response
        else:
            return JsonResponse(form.errors, status=400)


def hours_templates(request):
    # print(request.GET)
    template_id = request.GET['template_id']
    hours_templates = HoursTemplates.objects.filter(templates_budgeted_hours = template_id).values()

    for data in hours_templates:
        software = Softwares.objects.filter(pk = data['software_id']).values()
        if software:
            data['software'] = software[0]['software']
        else:
            data['software_id'] = ''
            data['software'] = ''

        activity = Activities.objects.filter(pk = data['activity_id']).values()
        if activity:
            data['activity'] = activity[0]['activity']

    hours_templates = list(hours_templates)
    # print(hours_templates)

    context = {
        'hours_templates': hours_templates
    }

    return JsonResponse(context)


def templates_budgeted_hours_update(request):
    # print(request.POST)
    # print(request.POST.get('budgeted_hours'))
    ids = request.POST.getlist('hours_templates_ids[]')
    hours_engineer = request.POST.getlist('engineer[]')
    hours_leader = request.POST.getlist('leader[]')
    hours_management = request.POST.getlist('management[]')
    hours_software = request.POST.getlist('software[]')
    type_software = request.POST.getlist('type_software[]')
    hours_external = request.POST.getlist('external[]')
    # print(type_software)

    for i in range(len(ids)):
        instance = HoursTemplates.objects.get(pk=ids[i])

        if type_software[i]:
            software = Softwares.objects.get(pk=type_software[i])
            instance.software=software
        else:
            instance.software=None

        # instance.budgeted_hours=instance.budgeted_hours
        # instance.activity=activity
        # instance.category=category
        instance.engineer = hours_engineer[i]
        instance.leader = hours_leader[i]
        instance.management = hours_management[i]
        instance.software_hours = hours_software[i]
        instance.external = hours_external[i]
        instance.save()
        # print(pks[i])
        # print(hours_engineer[i])
        # print(hours_leader[i])
        # print(hours_management[i])
        # print(hours_software[i])
        # print('--------------')

    messages.success(request, 'Plantilla de horas presupuestadas actualizadas con éxito')
    return redirect('budgeted_hours:templates_budgeted_hours_view', request.POST.get('templates_budgeted_hours'))


# def budgeted_hours_add(request):
#     print(request.POST)
#     activities_pks = request.POST.getlist('activities_pks[]')
#     hours_engineer = request.POST.getlist('engineer[]')
#     hours_leader = request.POST.getlist('leader[]')
#     hours_management = request.POST.getlist('management[]')
#     hours_software = request.POST.getlist('software[]')

#     # print(request.POST.get('budgeted_hours'))
#     budgeted_hours = BudgetedHours.objects.get(pk=request.POST.get('budgeted_hours'))
#     category = Categories.objects.get(pk=request.POST.get('category'))

#     for i in range(len(activities_pks)):
#         activity = Activities.objects.get(pk=activities_pks[i])

#         instance = Hours(
#             budgeted_hours=budgeted_hours,
#             activity=activity,
#             category=category,
#             engineer=hours_engineer[i],
#             leader=hours_leader[i],
#             management=hours_management[i],
#             software_hours=hours_software[i]
#         )
#         instance.save()

#     return redirect('budgeted_hours:budgeted_hours_view', request.POST.get('budgeted_hours'))


# def hours_import(request):
#     print(request.GET)
#     # print(request.FILES)
#     if request.method == 'POST':
#         try:
#             df = pd.read_excel(request.FILES['file'], engine = 'openpyxl')
#             hours = Hours.objects.filter(budgeted_hours=request.GET['budgeted_hours']).filter(category=request.GET['category']).all()

#             dict_names = {
#                 'actividad': 'activity',
#                 'ingeniero': 'engineer',
#                 'líder': 'leader',
#                 'gerencia': 'management',
#                 'horas de software': 'software_hours'
#             }

#             for name_col in dict_names.keys():
#                 if name_col not in df.columns:
#                     raise NameError(f'La columna "{name_col}" no se encuentra en el archivo')

#             if len(df.index) != len(hours):
#                 raise NameError(f'Las filas del archivo no coinciden con las actividades (filas: Archivo {len(df.index)}, Actividades {len(hours)})')

#             df.rename(columns=dict_names, inplace=True)
#             df = df.astype(str)
#             df.replace(to_replace=["nan", " - "], value=[0, 0], inplace=True)
#             # print(df)

#             for index, row in df.iterrows():
#                 for i in range(len(hours)):
#                     if row[0] == hours[i].activity.activity:
#                         instance = Hours.objects.get(pk=hours[i].id)
#                         instance.engineer = row[1]
#                         instance.leader = row[2]
#                         instance.management = row[3]
#                         instance.software_hours = row[4]
#                         instance.save()

#             messages.success(request, 'Importación realizada con éxito')
#             return redirect('budgeted_hours:budgeted_hours_view', request.GET.get('budgeted_hours'))

#         except Exception as e:
#             # print(e)
#             messages.error(request, 'Error de importación: ' + str(e))
#             return redirect('budgeted_hours:budgeted_hours_view', request.GET.get('budgeted_hours'))

#     else:
#         return render(request, 'import_file/import_file.html')


# def send_mail(request):
#     print('Get', request.GET)
#     print('Post', request.POST)
#     users = request.POST.getlist('users[]')
#     print(users)

#     if request.POST:
#         # budgeted_hours = BudgetedHours.objects.get(pk=request.GET['id'])
#         var = 21
#         budgeted_hours = BudgetedHours.objects.get(pk=var)
#         traceability = TraceabilityBudgetedHours.objects.filter(budgeted_hours=budgeted_hours).all()

#         if traceability:
#             messages.error(request, 'Mensaje enviado anteriormente')
#             return redirect('budgeted_hours:budgeted_hours_view', var)
#         else:
#             instance = TraceabilityBudgetedHours(
#                 budgeted_hours = budgeted_hours
#             )
#             instance.save()

#             body = """
#             Código: {}\n
#             Cliente: {}\n
#             Tipo de estudio: {}\n
#             """.format(budgeted_hours, budgeted_hours.client, budgeted_hours.get_study_type_display())

#             # users_emails = User.objects.filter(groups__name='financiero').all().values_list('email', flat=True)
#             # print("Usuarios", users_emails)

#             email = EmailMessage('Nuevas horas presupuestadas!', body, to=users)
#             email.send()

#             messages.success(request, 'Mensaje enviado con éxito')
#             return redirect('budgeted_hours:budgeted_hours_view', var)

#     else:
#         pending_budgeted_hours = TraceabilityBudgetedHours.objects.filter(reviewed_by=None).all()
#         # print(pending_budgeted_hours)

#         for pending in pending_budgeted_hours:
#             # print(pending.budgeted_hours)

#             body = """
#             Código: {}\n
#             Cliente: {}\n
#             Tipo de estudio: {}\n
#             """.format(pending, pending.budgeted_hours.client, pending.budgeted_hours.get_study_type_display())

#             # users_emails = User.objects.filter(groups__name='financiero').all().values_list('email', flat=True)
#             # print("Usuarios", users_emails)

#             email = EmailMessage('Horas presupuestadas pendientes!', body, to=['alex.igirio@phc.com.co'])
#             # email.send()

#         return HttpResponse('Mensajes enviados con éxito')


# def send_mail_reviewed(request):

#     budgeted_hours = BudgetedHours.objects.get(pk=request.GET['id'])

#     if budgeted_hours:
#         traceability = TraceabilityBudgetedHours.objects.filter(budgeted_hours=budgeted_hours).all()
#         instance = TraceabilityBudgetedHours.objects.get(pk=traceability[0].id)
#         instance.reviewed_by = request.user
#         instance.save()

#         body = """
#         Código: {}\n
#         Cliente: {}\n
#         Tipo de estudio: {}\n
#         Valor: {}
#         """.format(budgeted_hours.code, budgeted_hours.client, budgeted_hours.get_study_type_display(), budgeted_hours.value)

#         email = EmailMessage('Horas presupuestadas revisadas!', body, to=['alex.igirio@phc.com.co'])
#         email.send()

#         messages.success(request, 'Mensaje enviado con éxito')
#         return redirect('budgeted_hours:budgeted_hours_view', request.GET['id'])


# @method_decorator(login_required, name='dispatch')
class TemplatesBudgetedHoursUpdateView(PermissionRequiredMixin, UpdateView):

    model = TemplatesBudgetedHours
    form_class = TemplatesBudgetedHoursForm
    template_name = 'templates_budgeted_hours/detail.html'
    success_url = reverse_lazy('budgeted_hours:templates_budgeted_hours_list')
    permission_required = 'budgeted_hours.change_templatesbudgetedhours'


    def get_context_data(self, **kwargs):
        context = super(TemplatesBudgetedHoursUpdateView, self).get_context_data(**kwargs)

        # print(self.object)
        # print(self.object.code)
        # print(self.object.client)
        # print(self.object.study_type)
        # activities = Activities.objects.filter(study_type=self.object.service_type.id).all()
        # print('activities **', activities)

        # activities = Activities.objects.filter(study_type=self.object.study_type).values_list('activity')
        # print('activities', activities)
        # categories = Categories.objects.prefetch_related(Prefetch('hours', queryset=Hours.objects.filter(budgeted_hours=self.object.id))).annotate(dcount=Count('category')).order_by().all()

        # .annotate(dcount=Count('category')).order_by()
        # print('categories **', categories)
        # print('------------')
        # for category in categories:
        #     print(category)
        #     print(category.hours.filter(budgeted_hours=self.object.id).all())
        #     fil = category.hours.filter(budgeted_hours=self.object.id).all()
        #     for hour in category.hours.all():
        #         print(hour)
        #     print('------------')
        # print(categories[0]['hours'])
        # print(categories[0]['hours'])
        hours_templates = HoursTemplates.objects.filter(templates_budgeted_hours=self.object.id).all()
        # for hour in hours:
        #     print(hour.activity.activity)
        # print('hours', hours)
        # hours = list(hours)

        softwares = Softwares.objects.all()


        # for hour_template in hours_templates:
        #     print(hour_template.id, hour_template.activity.activity, hour_template.engineer)

        # lis = []
        # for i in range(0, len(activities)):
        #     lis.append(i)
        # print(lis)

        # context['categories'] = categories
        context['hours_templates'] = hours_templates
        context['templates_budgeted_hours'] = self.object
        # context['activities'] = activities
        context['softwares'] = softwares

        return context


    # def get_success_url(self):
    #     print('get')
    #     print(self.request.POST)
    #     print(self.object)
    #     hours_engineer = self.request.POST.getlist('engineer[]')
    #     hours_leader = self.request.POST.getlist('leader[]')
    #     hours_management = self.request.POST.getlist('management[]')
    #     hours_software = self.request.POST.getlist('software[]')

    #     budgeted_hours = BudgetedHours.objects.get(pk=self.object.id)
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

    #     return reverse_lazy('budgeted_hours:budgeted_hours_list')


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Plantilla de horas presupuestadas actualizadas con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


# @method_decorator(login_required, name='dispatch')
class TemplatesBudgetedHoursDeleteView(PermissionRequiredMixin, DeleteView):

    model = BudgetedHours
    template_name = 'templates_budgeted_hours/delete.html'
    success_url = reverse_lazy('budgeted_hours:templates_budgeted_hours_list')
    context_object_name = 'templatesbudgetedhours'
    permission_required = 'budgeted_hours.delete_templatesbudgetedhours'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Plantilla de horas presupuestadas eliminadas con éxito')
        return super(TemplatesBudgetedHoursDeleteView, self).delete(*args, **kwargs)
