from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from lessons.models import ConnectionStudies, Zones, Areas, Operators
from lessons.forms.connection_studies_form import ConnectionStudiesForm

# from django.http import HttpResponse

from django.contrib.auth.models import User
# import json

# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.utils.translation import gettext as _
# from django.utils.decorators import method_decorator
from django.http import JsonResponse

import unidecode


class ConnectionStudiesListView(PermissionRequiredMixin, ListView):

    model = ConnectionStudies
    template_name = 'connection_studies/list.html'
    context_object_name = 'connection_studies'
    permission_required = ''

    queryset = ConnectionStudies.objects.select_related('budgeted_hours', 'client', 'created_by', 'zone', 'operator', 'area').all()


# class ConnectionStudiesDetailView(PermissionRequiredMixin, DetailView):
#     model = ConnectionStudies
#     template_name = 'connection_studies/detail.html'
#     context_object_name = 'connectionStudy'
#     permission_required = 'lessons.view_connectionstudies'


class ConnectionStudiesCreateView(PermissionRequiredMixin, CreateView):

    model = ConnectionStudies
    form_class = ConnectionStudiesForm
    template_name =  'connection_studies/create.html'
    success_url = reverse_lazy('lessons:connection_studies_list')
    permission_required = ''

    # def get_context_data(self, **kwargs):
    #     ctx = super(ConnectionStudiesCreateView, self).get_context_data(**kwargs)
    #     #ctx['form'].fields["responsable"].queryset = User.objects.filter(is_superuser=False)
    #     ctx['form'].fields['created_by'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)

    #     return ctx


    def form_valid(self, form):
        # obj = form.save(commit=False)
        # obj.created_by = self.request.user

        # if obj.file:
        #     obj.file.name = unidecode.unidecode(obj.file.name)

        messages.success(self.request, 'Registro creado con éxito')
        # obj.save()
        return super().form_valid(form)


class ConnectionStudiesDetailView(PermissionRequiredMixin, DetailView):

    model = ConnectionStudies
    template_name = 'connection_studies/detail.html'
    context_object_name = 'connection_studies'
    permission_required = ''

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['site'] = settings.URL_SITE
    #     return context


class ConnectionStudiesChangeView(PermissionRequiredMixin, UpdateView):

    model = ConnectionStudies
    form_class = ConnectionStudiesForm
    template_name = 'connection_studies/change.html'
    success_url = reverse_lazy('lessons:connection_studies_list')
    permission_required = ''


    # def get_context_data(self, **kwargs):
    #     ctx = super().get_context_data(**kwargs)

    #     print(self.object)
    #     self.object = self.get_object()
    #     print(self.object)
    #     zone_id = self.object.zone.id
    #     operator_id = self.object.operator.id

    #     #ctx['form'].fields["responsable"].queryset = User.objects.filter(is_superuser=False)
    #     # ctx['form'].fields['responsable'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)

    #     ctx['form'].fields['operator'].queryset = Operators.objects.filter(zone=zone_id)
    #     ctx['form'].fields['area'].queryset = Areas.objects.filter(operator=operator_id)

    #     return ctx

    def form_valid(self, form):
        # self.object = form.save()
        messages.success(self.request, 'Registro actualizado con exito')
        return super().form_valid(form)


class ConnectionStudiesDeleteView(PermissionRequiredMixin, DeleteView):

    model = ConnectionStudies
    template_name = 'connection_studies/delete.html'
    success_url = reverse_lazy('lessons:connection_studies_list')
    context_object_name = 'connection_studies'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super(ConnectionStudiesDeleteView, self).delete(*args, **kwargs)


def getOperators(request):

    zone_id = request.GET['zone_id']

    operators = Operators.objects.filter(zone=zone_id).values('id', 'name')

    operator = operators.first()
    if operator:
        operator_id = operator['id']
        areas = Areas.objects.filter(operator=operator_id).values('id', 'name')

    data = {
        'operators': list(operators),
        'areas': list(areas)
    }

    return JsonResponse(data)


def getAreas(request):

    operator_id = request.GET['operator_id']

    areas = Areas.objects.filter(operator=operator_id).values('id', 'name')

    data = {
        'areas': list(areas),
    }

    return JsonResponse(data)
