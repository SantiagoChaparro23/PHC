# from django.http import request
# from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.conf import settings
import os

from vacations.models import Requests
from vacations.forms.requests_files_form import RequestsFilesForm

from datetime import datetime

# Create your views here.
# @method_decorator(login_required, name='dispatch')
# class ActivitiesListView(PermissionRequiredMixin, ListView):

#     model = Activities
#     template_name = 'activities/list.html'
#     context_object_name = 'activities'
#     permission_required = 'budgeted_hours.view_activities'


# @method_decorator(login_required, name='dispatch')
# class ActivitiesCreateView(PermissionRequiredMixin, CreateView):

#     model = Activities
#     form_class = ActivitiesForm
#     template_name = 'activities/create.html'
#     permission_required = 'budgeted_hours.add_activities'


#     def get_success_url(self):
#         cursor = connection.cursor()
#         cursor.execute('''
#             SELECT
#                 budgeted_hours_id,
#                 category_id,
#                 version
#             FROM
#                 budgeted_hours_hours AS bh
#                 INNER JOIN budgeted_hours_activities AS ba ON ba.id = bh.activity_id
#             WHERE
#                 ba.service_type_id = {}
#             GROUP BY
#                 budgeted_hours_id,
#                 category_id,
#                 version;
#         '''.format(self.object.service_type.id))

#         query_budgeted_hours = cursor.fetchall()
#         print(query_budgeted_hours)
#         print(type(query_budgeted_hours))

#         if query_budgeted_hours:
#             for i in query_budgeted_hours:
#                 # print('budgeted_hours_id', i[0], 'category_id', i[1])
#                 budgeted_hours = BudgetedHours.objects.get(pk=i[0])
#                 activity = Activities.objects.get(pk=self.object.id)
#                 category = Categories.objects.get(pk=i[1])

#                 instance = Hours(
#                     budgeted_hours = budgeted_hours,
#                     activity = activity,
#                     category = category,
#                     version = i[2]
#                 )
#                 instance.save()

#         cursor.execute('''
#             SELECT
#                 templates_budgeted_hours_id
#             FROM
#                 budgeted_hours_hourstemplates AS bh
#                 INNER JOIN budgeted_hours_activities AS ba ON ba.id = bh.activity_id
#             WHERE
#                 ba.service_type_id = {}
#             GROUP BY
#                 templates_budgeted_hours_id;
#         '''.format(self.object.service_type.id))

#         query_templates_budgeted_hours = cursor.fetchall()

#         if query_templates_budgeted_hours:
#             for i in query_templates_budgeted_hours:
#                 # print('templates_budgeted_hours_id', i[0])
#                 templates_budgeted_hours = TemplatesBudgetedHours.objects.get(pk=i[0])
#                 activity = Activities.objects.get(pk=self.object.id)

#                 instance = HoursTemplates(
#                     templates_budgeted_hours = templates_budgeted_hours,
#                     activity = activity
#                 )
#                 instance.save()

#         cursor.close()

#         return reverse_lazy('budgeted_hours:activity_list')


#     def form_valid(self, form):
#         messages.success(self.request, 'Actividad creada con éxito')
#         return super().form_valid(form)


@method_decorator(csrf_exempt, name='dispatch')
class RequestsFilesUpdateView(PermissionRequiredMixin, UpdateView):

    model = Requests
    form_class = RequestsFilesForm
    context_object_name = 'file'
    template_name = 'requests_files/change.html'
    # success_url = reverse_lazy('vacations:requests_detail')
    permission_required = 'budgeted_hours.change_budgetedhours'

    def get_success_url(self):
        return reverse_lazy('vacations:requests_detail', args=[self.object.id])


    # def get_context_data(self, **kwargs):
    #     context = super(BudgetedHoursFilesUpdateView, self).get_context_data(**kwargs)

    #     return context


    # def get_object(self):
    #     # print('get_object')
    #     # print(self.kwargs)

    #     return BudgetedHoursFiles.objects.get(budgeted_hours = self.kwargs['pk'])


    # def get(self, request, *args, **kwargs):
    #     print('GET')

    #     obj = BudgetedHoursFiles.objects.filter(budgeted_hours = self.get_object().id)
    #     if obj:
    #         obj = BudgetedHoursFiles.objects.get(budgeted_hours = self.get_object().id)
    #     print(obj)

    #     self.object = self.get_object()
    #     return super(BudgetedHoursFilesUpdateView, self).get(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     print('POST')
    #     self.object = self.get_object()
    #     return super(BudgetedHoursFilesUpdateView, self).post(request, *args, **kwargs)


    def handle_uploaded_file(self, f, tmp_folder):
        with open(f'{tmp_folder}/{f.name}', 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)


    def form_valid(self, form):
        request = self.request
        print('request', request)

        unix = int(datetime.now().timestamp())
        print('unix', unix)

        base = settings.PROJECT_PATH
        print('base', base)

        tmp_folder = f'{base}/storage/vacations/{unix}'
        print('tmp_folder', tmp_folder)

        os.makedirs(tmp_folder)

        files = []
        print('request.FILES', request.FILES)

        for filename, file in request.FILES.items():
            print('filename', filename)
            print('file', file)
            files.append(str(file))
            self.handle_uploaded_file(file, tmp_folder)

        object = self.object
        filename = f'{base}/static/vacations/vacation-{unix}.zip'

        command = f'zip -r -j {filename} {tmp_folder}'
        print(command)
        os.system(command)

        obj = form.save(commit=False)

        # files = '<br>'.join(files)
        # print(files)
        obj.path_liquidation = f'static/vacations/vacation-{unix}.zip'
        # obj.file_name = object.budgeted_hours.code
        # obj.files = files
        obj.save()

        messages.success(self.request, 'Éxito')
        return HttpResponseRedirect(self.get_success_url())


# @method_decorator(login_required, name='dispatch')
# class ActivitiesDeleteView(PermissionRequiredMixin, DeleteView):

#     model = Activities
#     template_name = 'activities/delete.html'
#     success_url = reverse_lazy('budgeted_hours:activity_list')
#     context_object_name = 'activities'
#     permission_required = 'budgeted_hours.delete_activities'


#     def delete(self, *args, **kwargs):
#         messages.success(self.request, 'Actividad eliminada con éxito')
#         return super(ActivitiesDeleteView, self).delete(*args, **kwargs)
